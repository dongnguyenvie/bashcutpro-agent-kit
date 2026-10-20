#!/usr/bin/env python3
"""Measure the loudness of a WAV file (ITU-R BS.1770 / EBU R128), read-only. BashCutPro has no loudness meter yet:
export the mix, a stem or a range as WAV (`file.exportMedia {format: "wav"}`) and read it here.

  loudness.py mix.wav                              # integrated LUFS, LRA, sample and true peak, silences
  loudness.py music.wav --speech voice.wav         # music under the voice vs in its gaps (stems, same range)
  loudness.py music.wav --windows speech.json      # the same against explicit speech windows
  loudness.py mix.wav --from 30 --to 60 --curve    # one range, short-term loudness per second
  loudness.py mix.wav --min-silence 0.8 --tighten 0.4   # + a bashcut.batch that cuts each silence down to 0.4 s

--speech: speech windows are where that file (the voice stem exported over the same range) is above
--silence-lufs. --windows: a JSON list of [start, end] or {"start", "end"} in seconds (word spans from `transcript.inspect`,
joined), on the file's own clock. --tighten KEEP: for a WAV of the whole sequence mix (`--sequence-start` when it
starts later), `tighten.commands` mark in and out inside every silence of --min-silence or more, KEEP seconds left
(half each side), and `sequence.extract` it, last silence first, for one `bashcut.batch`. Prints one JSON object. True peak is estimated by 4x oversampling around the
loudest samples. PCM 16 / 24 / 32-bit and float WAV. Standard library only (Python 3.9+); about 3 s per minute
of stereo 48 kHz audio."""
import argparse, array, json, math, struct, sys


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


def biquad(x, b, a):
    b0, b1, b2 = b
    a1, a2 = a
    y = array.array("d", bytes(8 * len(x)))
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        out = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, out
        y[i] = out
    return y


def k_weight(x, rate):
    """BS.1770 K-weighting (high shelf + high pass) for any sample rate, designed as libebur128 does; at 48 kHz it
    gives the standard's coefficients."""
    k, q = math.tan(math.pi * 1681.974450955533 / rate), 0.7071752369554196
    vh = 10 ** (3.999843853973347 / 20)
    vb = vh ** 0.4996667741545416
    a0 = 1 + k / q + k * k
    shelf = ([(vh + vb * k / q + k * k) / a0, 2 * (k * k - vh) / a0, (vh - vb * k / q + k * k) / a0],
             [2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0])
    k, q = math.tan(math.pi * 38.13547087602444 / rate), 0.5003270373238773
    a0 = 1 + k / q + k * k
    high = ([1, -2, 1], [2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0])
    return biquad(biquad(x, *shelf), *high)


def block_power(chans, rate, size_s, hop_s):
    """Mean square of each block, summed over channels (weights 1: mono / stereo)."""
    size, hop = int(size_s * rate), int(hop_s * rate)
    n = len(chans[0])
    sq = []
    for c in chans:  # running sum of squares makes every block O(1)
        acc, s = array.array("d", [0.0]), 0.0
        for v in c:
            s += v * v
            acc.append(s)
        sq.append(acc)
    out = []
    for start in range(0, max(n - size, 0) + 1, hop):
        out.append(sum((acc[start + size] - acc[start]) for acc in sq) / size if n >= size else 0.0)
    return out


def lufs(p):
    return -0.691 + 10 * math.log10(p) if p > 0 else -math.inf


def integrated(powers):
    gated = [p for p in powers if lufs(p) > -70]
    if not gated:
        return -math.inf
    rel = lufs(sum(gated) / len(gated)) - 10
    kept = [p for p in gated if lufs(p) > rel]
    return lufs(sum(kept) / len(kept)) if kept else -math.inf


def loudness_range(short):
    vals = sorted(l for l in (lufs(p) for p in short) if l > -70)
    if not vals:
        return 0.0
    mean = lufs(sum(10 ** ((l + 0.691) / 10) for l in vals) / len(vals))
    vals = [l for l in vals if l > mean - 20]
    pct = lambda q: vals[min(len(vals) - 1, int(round(q * (len(vals) - 1))))]
    return pct(0.95) - pct(0.10)


def true_peak(chans, around=64, taps=8):
    """4x oversampled peak (Hann-windowed sinc) around each channel's loudest samples."""
    best = 0.0
    for c in chans:
        top = sorted(range(len(c)), key=lambda i: -abs(c[i]))[:around]
        for i in top:
            best = max(best, abs(c[i]))
            for k in (1, 2, 3):
                t, s = k / 4, 0.0
                for j in range(-taps + 1, taps + 1):
                    if 0 <= i + j < len(c):
                        x = t - j
                        s += c[i + j] * (math.sin(math.pi * x) / (math.pi * x)) * (0.5 + 0.5 * math.cos(math.pi * x / taps))
                best = max(best, abs(s))
    return best


def db(v):
    return round(20 * math.log10(v), 2) if v > 0 else None


def num(v):
    return None if v is None or math.isinf(v) else round(v, 1)


def spans(flags, hop, min_s):
    out, start = [], None
    for i, f in enumerate(flags + [False]):
        if f and start is None:
            start = i
        elif not f and start is not None:
            if (i - start) * hop >= min_s:
                out.append([round(start * hop, 1), round((i - 1) * hop + 0.4, 1)])
            start = None
    return out


def tighten(silences, keep, offset=0.0):
    """Commands that cut each silence down to `keep` seconds (mark in, mark out, extract), last one first so the
    earlier times stay right."""
    cmds, removed = [], 0.0
    for s, e in sorted(silences, reverse=True):
        a, b = s + offset + keep / 2.0, e + offset - keep / 2.0
        if b - a < 0.1:
            continue
        cmds += [{"id": "markers.markIn", "params": {"seconds": round(a, 3)}},
                 {"id": "markers.markOut", "params": {"seconds": round(b, 3)}},
                 {"id": "sequence.extract", "params": {}}]
        removed += b - a
    return {"commands": cmds, "cuts": len(cmds) // 3, "removedSeconds": round(removed, 2)}


def median(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wav")
    ap.add_argument("--from", dest="start", type=float, default=0, help="seconds into the file")
    ap.add_argument("--to", type=float, help="seconds into the file")
    ap.add_argument("--windows", help="JSON file of [start, end] seconds (speech) to compare inside vs outside")
    ap.add_argument("--speech", help="voice stem WAV of the same range: its sound marks the speech windows")
    ap.add_argument("--curve", action="store_true", help="add short-term loudness (3 s) once a second")
    ap.add_argument("--silence-lufs", type=float, default=-50, help="momentary loudness below this is silence")
    ap.add_argument("--min-silence", type=float, default=1.0, help="shortest silence listed, seconds")
    ap.add_argument("--tighten", type=float, help="seconds of each silence to keep: print commands that cut the rest")
    ap.add_argument("--sequence-start", type=float, default=0.0, help="sequence time of the file's first sample")
    o = ap.parse_args(argv)
    rate, chans = read_wav(o.wav)
    a, b = int(o.start * rate), int(o.to * rate) if o.to else None
    chans = [c[a:b] for c in chans]
    raw = chans
    weighted = [k_weight(c, rate) for c in chans]
    momentary = block_power(weighted, rate, 0.4, 0.1)
    short = block_power(weighted, rate, 3.0, 1.0)
    out = {"file": o.wav, "from": o.start, "seconds": round(len(raw[0]) / rate, 2), "sampleRate": rate,
           "channels": len(raw), "integratedLufs": num(integrated(momentary)), "lraLu": round(loudness_range(short), 1),
           "samplePeakDbfs": db(max((max(map(abs, c)) for c in raw if len(c)), default=0)),
           "truePeakDbtp": db(true_peak(raw)),
           "maxMomentaryLufs": num(max(map(lufs, momentary), default=-math.inf)),
           "maxShortTermLufs": num(max(map(lufs, short), default=-math.inf)),
           "silences": spans([lufs(p) < o.silence_lufs for p in momentary], 0.1, o.min_silence)}
    wins = None
    if o.speech:
        srate, voice = read_wav(o.speech)
        vm = block_power([k_weight(c[int(o.start * srate):int(o.to * srate) if o.to else None], srate) for c in voice],
                         srate, 0.4, 0.1)
        wins = [(o.start + s, o.start + e) for s, e in spans([lufs(p) >= o.silence_lufs for p in vm], 0.1, 0.1)]
    elif o.windows:
        with open(o.windows, encoding="utf-8") as fh:
            wins = [(w["start"], w["end"]) if isinstance(w, dict) else tuple(w) for w in json.load(fh)]
    if wins is not None:
        inside, outside = [], []
        for i, p in enumerate(momentary):
            t = o.start + i * 0.1 + 0.2  # block centre on the file's clock
            (inside if any(s <= t < e for s, e in wins) else outside).append(lufs(p))
        audible = lambda v: [x for x in v if x > -70]
        out["windows"] = {"insideMedianLufs": num(median(audible(inside))), "outsideMedianLufs": num(median(audible(outside))),
                          "insideSeconds": round(len(inside) * 0.1, 1), "outsideSeconds": round(len(outside) * 0.1, 1)}
    if o.tighten is not None:
        out["tighten"] = tighten(out["silences"], o.tighten, o.start + o.sequence_start)
    if o.curve:
        out["shortTerm"] = [[round(o.start + i + 3, 1), num(lufs(p))] for i, p in enumerate(short)]
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
