#!/usr/bin/env python3
"""Estimate the beat grid of a music WAV, out of process: BashCutPro has no beat analysis command yet (clip.remix
analyses beats internally only). Standard library only (Python 3.9+), an estimate, not a reference tracker.

  beats.py music.wav                                   # tempo, alternates, beats, downbeats, energy per second
  beats.py music.wav --markers --at 12.5 [--source-in 3.0] [--downbeats]   # markers.add steps for command_batch
  beats.py music.wav --at 12.5 --cuts 14.0,16.1,18.2 [--fps 30]      # each cut's offset from the nearest beat

How: a mono onset envelope (rise in log energy, full band plus a low band for kicks) every ~11.6 ms; tempo from
its autocorrelation between --min-bpm and --max-bpm, weighted toward 120 BPM; beats placed by dynamic programming
on the envelope (Ellis 2007), the tempo then refined from the beats' straight-grid slope; downbeats = the bar phase (of --meter beats) with the strongest low band. Prints one
JSON object: `tempo`, `alternates` (other tempi and scores), `confidence` (best score over the runner-up),
`beats` and `downbeats` (seconds in the file), `fit.rmsErrorMs` (beats against a straight grid), `phaseScores`,
`strengths` (onset strength per beat, 0-1), `energy` ([second, dB] of the level). --markers prints `markers.add`
steps instead, at timeline time = --at + (beat - --source-in), for beats inside the placed clip (--duration).
--cuts (timeline seconds, comma-separated or a JSON file) adds `sync`: each cut's offset from the nearest beat in ms
(+ = late), the median, p10-p90, and the share within 1 and 2 frames at --fps."""
import argparse, array, json, math, struct, sys

TICKS = 254016000000  # per second
HOP = 512


def read_wav(path):
    """(rate, [channel arrays of floats in -1..1]) from a RIFF WAVE file: PCM 8/16/24/32-bit or 32/64-bit float."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        sys.exit(f"{path}: not a WAV file")
    pos, fmt, body = 12, None, None
    while pos + 8 <= len(data):
        tag, size = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])[0]
        chunk = data[pos + 8:pos + 8 + size]
        if tag == b"fmt ":
            fmt = struct.unpack("<HHIIHH", chunk[:16]) + ((struct.unpack("<H", chunk[24:26])[0],) if len(chunk) >= 26 else (None,))
        elif tag == b"data":
            body = chunk
        pos += 8 + size + (size & 1)
    if not fmt or body is None:
        sys.exit(f"{path}: no fmt or data chunk")
    kind, channels, rate, _, _, bits, sub = fmt
    if kind == 0xFFFE:  # WAVE_FORMAT_EXTENSIBLE: the subformat's first two bytes are the real format
        kind = sub
    width = bits // 8
    body = body[:len(body) - len(body) % (width * channels)]
    if kind == 3 and bits in (32, 64):
        samples = array.array("f" if bits == 32 else "d", body)
    elif kind == 1 and bits == 8:
        samples = array.array("f", ((b - 128) / 128 for b in body))
    elif kind == 1 and bits in (16, 24, 32):
        if bits == 24:  # widen to 32-bit: each sample becomes the top three bytes of an int32
            wide = bytearray(len(body) // 3 * 4)
            wide[1::4], wide[2::4], wide[3::4] = body[0::3], body[1::3], body[2::3]
            body, bits = bytes(wide), 32
        ints = array.array("h" if bits == 16 else "i", body)
        if sys.byteorder == "big":
            ints.byteswap()
        scale = 1 / float(1 << (bits - 1))
        samples = array.array("f", (v * scale for v in ints))
    else:
        sys.exit(f"{path}: unsupported WAV format {kind}, {bits} bits")
    return rate, [samples[c::channels] for c in range(channels)]


def envelopes(chans, rate):
    """Per hop: full-band and low-band (< ~150 Hz) energy of the mono mix."""
    n = len(chans[0])
    k = 2 * math.pi * 150 / rate
    a = k / (k + 1)  # one-pole low pass
    full, low, lp = [], [], 0.0
    ef = el = 0.0
    inv = 1 / len(chans)
    for i in range(n):
        v = sum(c[i] for c in chans) * inv if len(chans) > 1 else chans[0][i]
        lp += a * (v - lp)
        ef += v * v
        el += lp * lp
        if (i + 1) % HOP == 0:
            full.append(ef)
            low.append(el)
            ef = el = 0.0
    return full, low


def onset(energy):
    """Half-wave rectified rise of log energy, mean removed, scaled to 0-1."""
    log = [math.log10(e + 1e-10) for e in energy]
    d = [0.0] + [max(0.0, log[i] - log[i - 1]) for i in range(1, len(log))]
    m = sum(d) / len(d) if d else 0
    d = [max(0.0, x - m) for x in d]
    top = max(d) if d else 0
    return [x / top for x in d] if top else d


def tempo_scores(env, fps, lo, hi):
    """Autocorrelation per lag, weighted toward 120 BPM (log-Gaussian, one octave wide)."""
    n = len(env)
    out = []
    for lag in range(max(1, int(fps * 60 / hi)), int(fps * 60 / lo) + 1):
        if lag >= n:
            break
        ac = sum(env[i] * env[i + lag] for i in range(n - lag)) / (n - lag)
        bpm = 60 * fps / lag
        out.append((ac * math.exp(-0.5 * (math.log2(bpm / 120)) ** 2), bpm, lag))
    return out


def track(env, period, tightness=100.0):
    """Ellis dynamic programming: beats that sit on onsets and keep close to the period."""
    n = len(env)
    score, back = list(env), [-1] * n
    for t in range(n):
        lo, hi = t - int(2 * period), t - int(period / 2)
        best, arg = -1e9, -1
        for p in range(max(0, lo), max(0, hi + 1)):
            s = score[p] - tightness * math.log((t - p) / period) ** 2
            if s > best:
                best, arg = s, p
        if arg >= 0 and best > 0:  # else the chain starts here
            score[t] = env[t] + best
            back[t] = arg
    tail = max(range(max(0, n - int(period)), n), key=lambda i: score[i]) if n else 0
    beats = []
    while tail >= 0:
        beats.append(tail)
        tail = back[tail]
    return beats[::-1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wav")
    ap.add_argument("--min-bpm", type=float, default=60)
    ap.add_argument("--max-bpm", type=float, default=200)
    ap.add_argument("--bpm", type=float, help="use this tempo instead of estimating it (a known song, an octave fix)")
    ap.add_argument("--meter", type=int, default=4, help="beats per bar for downbeats")
    ap.add_argument("--markers", action="store_true", help="print markers.add steps instead of the analysis")
    ap.add_argument("--at", type=float, default=0, help="--markers: timeline second where the music clip starts")
    ap.add_argument("--source-in", type=float, default=0, help="--markers: the clip's source in-point, seconds")
    ap.add_argument("--duration", type=float, help="--markers: the clip's length on the timeline, seconds")
    ap.add_argument("--downbeats", action="store_true", help="--markers: downbeats only")
    ap.add_argument("--cuts", help="timeline seconds of cuts (comma-separated, or a JSON list file) to check")
    ap.add_argument("--fps", type=float, default=30, help="--cuts: the sequence frame rate")
    o = ap.parse_args(argv)
    rate, chans = read_wav(o.wav)
    fps = rate / HOP
    full, low = envelopes(chans, rate)
    env, kick = onset(full), onset(low)
    both = [0.5 * f + 0.5 * k for f, k in zip(env, kick)]
    scores = sorted(tempo_scores(both, fps, o.min_bpm, o.max_bpm), reverse=True)
    if not scores and not o.bpm:
        sys.exit("too short to estimate a tempo")
    peaks = []  # distinct tempi: skip lags next to a better one
    for s, bpm, lag in scores:
        if all(abs(lag - q[2]) > 2 for q in peaks):
            peaks.append((s, bpm, lag))
        if len(peaks) == 4:
            break
    bpm = o.bpm or peaks[0][1]
    period = fps * 60 / bpm
    beats = track(both, period)
    strong = sorted(both[b] for b in beats)[len(beats) // 2] * 0.1 if beats else 0
    while len(beats) > 2 and both[beats[0]] < strong:  # no onset under the ends: intro or tail padding
        beats.pop(0)
    while len(beats) > 2 and both[beats[-1]] < strong:
        beats.pop()
    times = [b * HOP / rate for b in beats]
    # Downbeats: the bar phase whose beats carry the most low-band onset.
    phase = [sum(kick[b] for b in beats[p::o.meter]) / max(1, len(beats[p::o.meter])) for p in range(o.meter)]
    best = max(range(o.meter), key=lambda p: phase[p])
    downs = times[best::o.meter]
    # Fit: beats against the least-squares straight grid.
    n = len(times)
    if n > 2:
        mx, my = (n - 1) / 2, sum(times) / n
        slope = sum((i - mx) * (t - my) for i, t in enumerate(times)) / sum((i - mx) ** 2 for i in range(n))
        rms = math.sqrt(sum((t - (my + slope * (i - mx))) ** 2 for i, t in enumerate(times)) / n) * 1000
        if not o.bpm:
            bpm = 60 / slope  # finer than the autocorrelation's whole-frame lags
    else:
        rms = None
    if o.markers:
        end = o.source_in + o.duration if o.duration else math.inf
        steps = [{"id": "markers.add", "params": {"target": "program", "time": round((o.at + t - o.source_in) * TICKS),
                  "name": ("downbeat" if t in downs else "beat")}}
                 for t in (downs if o.downbeats else times) if o.source_in <= t < end]
        print(json.dumps(steps, indent=1))
        return
    sec = int(rate)
    energy = []
    for s in range(0, len(chans[0]) - sec + 1, sec):
        p = sum(c[i] * c[i] for c in chans for i in range(s, s + sec, 4)) / (len(chans) * len(range(s, s + sec, 4)))
        energy.append([s // sec, round(10 * math.log10(p), 1) if p > 0 else None])
    sync = None
    if o.cuts:
        if o.cuts.endswith(".json"):
            with open(o.cuts, encoding="utf-8") as fh:
                cuts = [float(c) for c in json.load(fh)]
        else:
            cuts = [float(c) for c in o.cuts.split(",") if c.strip()]
        grid = [o.at + t - o.source_in for t in times]
        offs = sorted(min((c - g for g in grid), key=abs) * 1000 for c in cuts) if grid else []
        frame = 1000 / o.fps
        pick = lambda q: round(offs[min(len(offs) - 1, round(q * (len(offs) - 1)))], 1)
        sync = {"cuts": len(offs), "offsetsMs": [round(x, 1) for x in offs], "medianMs": pick(0.5) if offs else None,
                "p10Ms": pick(0.1) if offs else None, "p90Ms": pick(0.9) if offs else None,
                "within1Frame": round(sum(abs(x) <= frame for x in offs) / len(offs), 2) if offs else None,
                "within2Frames": round(sum(abs(x) <= 2 * frame for x in offs) / len(offs), 2) if offs else None}
    out = {"file": o.wav, "seconds": round(len(chans[0]) / rate, 2), "tempo": round(bpm, 2),
           "alternates": [{"bpm": round(b, 2), "score": round(s / peaks[0][0], 2)} for s, b, _ in peaks[1:]] if peaks else [],
           "confidence": round(peaks[0][0] / peaks[1][0], 2) if len(peaks) > 1 and peaks[1][0] else None,
           "fit": {"rmsErrorMs": round(rms, 1) if rms is not None else None, "frameMs": round(1000 / fps, 1)},
           "meter": o.meter, "phaseScores": [round(p, 3) for p in phase],
           "beats": [round(t, 3) for t in times], "downbeats": [round(t, 3) for t in downs],
           "strengths": [round(both[b], 2) for b in beats], "energy": energy}
    if sync:
        out["sync"] = sync
    print(json.dumps(out))


if __name__ == "__main__":
    main()
