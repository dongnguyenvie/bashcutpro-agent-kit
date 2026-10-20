#!/usr/bin/env python3
"""Tighten selects into a cut on word edges: one `bashcut.batch` of `timeline.place` steps.

    tighten.py --words words.json --item 3 --keep 12-58,140-171 [--wav source.wav] [--fps 30]
               [--min-pause 0.35] [--keep-pause 0.12] [--lang en|vi] [--fillers um,uh] [--protect 40,41]

`words.json` is a `transcript.inspect` result (or the CLI's `run` line holding it) of a scratch sequence holding the whole item at 0 from its start (so
word times are the item's own clock, in ticks). `--keep` lists the selects as word-index ranges (`from`-`to`, the
`transcript.search` hit), in story order: a hook moved first is just the first range. Inside each select it drops
filler words and false starts (a word or phrase said twice in a row keeps the later), and cuts every pause of at
least `--min-pause` down to `--keep-pause` of quiet on each side. Each edge stays in the gap between words, never
past the neighbouring word: clips are whole frames long, but their source in point is exact (ticks), so a
cut between two touching words still lands on the word edge.

`--wav` (the same scratch sequence exported as WAV, `file.exportMedia {format: "wav"}`; `--wav-start` when it
starts later) checks each edge against the sound: transcriber word ends run late and starts early, so an edge the
energy says is still in speech moves into the nearest quiet within the gap.

Prints {"command": <bashcut.batch for command_run>, "report": {...}}: spans, cuts, cuts a minute, what was removed
and why, edges moved by the sound check and edges in connected speech to look at. Standard library only.
"""
import argparse, array, json, math, re, struct, sys
from fractions import Fraction

TPS = 254016000000  # ticks a second
FILLERS = {
    "en": ["um", "uh", "umm", "uhm", "erm", "er", "ah", "ahm", "hmm", "mm", "mhm"],
    # "à", "ừ" can be answers in Vietnamese: pass them with --fillers after reading the hits
    "vi": ["ờ", "ừm", "ơ", "ờm", "hừm"],
}


def norm(text):
    return re.sub(r"[^\w']+", "", text.lower())


def load_words(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "result" in data:
        data = data["result"]
    words = data["words"] if isinstance(data, dict) else data
    out = []
    for n, w in enumerate(words):
        out.append({"i": w.get("i", n), "text": w["text"], "start": w["start"] / TPS, "end": w["end"] / TPS})
    return out


def parse_ranges(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        out.append((int(a), int(b or a)))
    return out


def read_wav(path):
    """(rate, mono floats) from a PCM 16/24/32-bit or float WAV."""
    with open(path, "rb") as f:
        data = f.read()
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
    kind = sub if kind == 0xFFFE else kind
    width = bits // 8
    body = body[:len(body) - len(body) % (width * channels)]
    if kind == 3 and bits == 32:
        samples = array.array("f", body)
    elif kind == 1 and bits == 16:
        samples = array.array("h", body)
        samples = array.array("f", (v / 32768.0 for v in samples))
    elif kind == 1 and bits in (24, 32):
        if bits == 24:
            wide = bytearray(len(body) // 3 * 4)
            wide[1::4], wide[2::4], wide[3::4] = body[0::3], body[1::3], body[2::3]
            body = bytes(wide)
        ints = array.array("i", body)
        samples = array.array("f", (v / 2147483648.0 for v in ints))
    else:
        sys.exit(f"{path}: unsupported WAV format {kind}, {bits} bits")
    if channels == 1:
        return rate, samples
    return rate, array.array("f", (sum(samples[i:i + channels]) / channels for i in range(0, len(samples), channels)))


def speech_mask(path, start, hop=0.01):
    """Per 10 ms window from `start`: True where the level is over the noise floor + 12 dB."""
    rate, x = read_wav(path)
    n = max(1, int(rate * hop))
    levels = []
    for i in range(0, len(x) - n + 1, n):
        s = sum(v * v for v in x[i:i + n]) / n
        levels.append(10 * math.log10(s + 1e-12))
    if not levels:
        return None
    floor = sorted(levels)[len(levels) // 10]
    gate = max(floor + 12, -60)
    mask = [lv > gate for lv in levels]
    for i in range(1, len(mask) - 3):  # fill holes under 40 ms inside speech
        if not mask[i] and mask[i - 1]:
            j = i
            while j < len(mask) and not mask[j] and j - i < 4:
                j += 1
            if j < len(mask) and mask[j] and j - i < 4:
                for k in range(i, j):
                    mask[k] = True
    return {"start": start, "hop": hop, "mask": mask}


def in_speech(vad, t):
    if not vad:
        return False
    i = int((t - vad["start"]) / vad["hop"])
    return 0 <= i < len(vad["mask"]) and vad["mask"][i]


def quiet_after(vad, t, limit):
    """First quiet time after t, before limit (or None)."""
    while t < limit:
        if not in_speech(vad, t):
            return t
        t += vad["hop"]
    return None


def quiet_before(vad, t, limit):
    """Last quiet time before t, after limit (or None)."""
    while t > limit:
        if not in_speech(vad, t):
            return t
        t -= vad["hop"]
    return None


def drop_words(words, lo, hi, fillers, protect):
    """Indices kept in words[lo..hi] and the removals {kind, i, text}."""
    removed = []
    keep = []
    phrases = sorted((f.split() for f in fillers), key=len, reverse=True)
    i = lo
    while i <= hi:
        hit = next((p for p in phrases if i + len(p) - 1 <= hi and all(norm(words[i + k]["text"]) == norm(w) for k, w in enumerate(p))), None)
        if hit and i not in protect:
            for k in range(len(hit)):
                removed.append({"kind": "filler", "i": i + k, "text": words[i + k]["text"], "at": round(words[i + k]["start"], 2)})
            i += len(hit)
            continue
        keep.append(i)
        i += 1
    changed = True
    while changed:  # false starts: a word or phrase (up to 3 words) said twice in a row keeps the later;
        # a first copy that ends a sentence ("one line. One line that…") is emphasis, not a false start
        changed = False
        for k in (3, 2, 1):
            for j in range(len(keep) - 2 * k + 1):
                a, b = keep[j:j + k], keep[j + k:j + 2 * k]
                if ([norm(words[x]["text"]) for x in a] == [norm(words[x]["text"]) for x in b] and not set(a) & protect
                        and not re.search(r"[.!?…。]$", words[a[-1]]["text"])):
                    for x in a:
                        removed.append({"kind": "repeat", "i": x, "text": words[x]["text"], "at": round(words[x]["start"], 2)})
                    keep = keep[:j] + keep[j + k:]
                    changed = True
                    break
            if changed:
                break
    return keep, sorted(removed, key=lambda r: r["i"])


def tighten(words, ranges, fps, min_pause, keep_pause, fillers, protect=frozenset(), vad=None):
    spans, removed, moved, connected = [], [], 0, []
    pauses, pause_seconds = 0, 0.0
    for lo, hi in ranges:
        if not (0 <= lo <= hi < len(words)):
            sys.exit(f"range {lo}-{hi} is outside the transcript (0-{len(words) - 1})")
        keep, rem = drop_words(words, lo, hi, fillers, protect)
        removed += rem
        groups = []
        for x in keep:
            if groups and x == groups[-1][-1] + 1 and words[x]["start"] - words[x - 1]["end"] < min_pause:
                groups[-1].append(x)
            else:
                if groups and x == groups[-1][-1] + 1:
                    pauses += 1
                    pause_seconds += words[x]["start"] - words[x - 1]["end"] - 2 * keep_pause
                groups.append([x])
        for g in groups:
            a, b = g[0], g[-1]
            lo_lim = words[a - 1]["end"] if a > 0 else 0.0
            hi_lim = words[b + 1]["start"] if b + 1 < len(words) else words[b]["end"] + keep_pause
            t_in = words[a]["start"] - min(keep_pause, max(0.0, words[a]["start"] - lo_lim) / 2)
            t_out = words[b]["end"] + min(keep_pause, max(0.0, hi_lim - words[b]["end"]) / 2)
            if in_speech(vad, t_in):
                q = quiet_before(vad, t_in, lo_lim + 0.02)
                if q is not None:
                    t_in, moved = q - min(0.04, (q - lo_lim) / 2), moved + 1
            if in_speech(vad, t_out):
                q = quiet_after(vad, t_out, hi_lim - 0.02)
                if q is not None:
                    t_out, moved = q + min(0.04, (hi_lim - q) / 2), moved + 1
            for side, gap in (("in", words[a]["start"] - lo_lim), ("out", hi_lim - words[b]["end"])):
                if 0 <= gap < 0.15 and not (side == "in" and a == 0):
                    connected.append({"edge": side, "word": words[a if side == "in" else b]["text"],
                                      "at": round(words[a]["start"] if side == "in" else words[b]["end"], 2), "gapSeconds": round(gap, 3)})
            spans.append({"from": a, "to": b, "in": t_in, "out": t_out, "lo": lo_lim, "hi": hi_lim,
                          "first": words[a]["start"], "last": words[b]["end"], "text": " ".join(words[x]["text"] for x in g)})
    # neighbouring spans that touch on the source (nothing removed between) are one clip
    merged = []
    for s in spans:
        m = merged[-1] if merged else None
        if m and s["from"] == m["to"] + 1 and s["in"] <= m["out"] + 1e-6:
            m.update(to=s["to"], out=s["out"], hi=s["hi"], last=s["last"], text=m["text"] + " " + s["text"])
        else:
            merged.append(dict(s))
    for s in merged:
        snap(s, fps)
    return merged, removed, moved, connected, pauses, pause_seconds


def snap(s, fps):
    """Whole frames on the timeline; the source in point is free (ticks), so no edge has to land inside a word.
    The span is trimmed or grown by under a frame on the side with the most padding (or room in the gap)."""
    n = max(1, math.floor((s["out"] - s["in"]) * fps + 1e-6))
    short = (s["out"] - s["in"]) - n / fps  # >= 0: trim this from the padding
    pad_in, pad_out = s["first"] - s["in"], s["out"] - s["last"]
    if short <= pad_in + pad_out + 1e-9:
        take_out = short * pad_out / (pad_in + pad_out) if pad_in + pad_out else 0.0
        s["in"] += short - take_out
        s["out"] -= take_out
    else:  # words touch both edges: one more frame, into whichever gap has room
        grow = (n + 1) / fps - (s["out"] - s["in"])
        n += 1
        room_out = s["hi"] - s["out"]
        add_out = min(grow, room_out)
        s["out"] += add_out
        s["in"] -= grow - add_out
    s["frames"] = n


def to_batch(spans, item, fps, track, label):
    ft = Fraction(TPS) / fps
    steps, pos = [], 0
    for s in spans:
        n = s["frames"]
        steps.append({"id": "timeline.place", "params": {"item": item, "track": track, "frame": pos,
                                                         "sourceIn": int(round(s["in"] * TPS)), "duration": int(round(n * ft))}})
        pos += n
    return {"id": "bashcut.batch", "params": {"label": label, "commands": steps}}, pos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--words", required=True)
    ap.add_argument("--item", required=True, type=int)
    ap.add_argument("--keep", required=True, help="word ranges in story order: 12-58,140-171")
    ap.add_argument("--fps", default="30", help="sequence frame rate: 30, 25, 30000/1001")
    ap.add_argument("--min-pause", type=float, default=0.35)
    ap.add_argument("--keep-pause", type=float, default=0.12)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--fillers", help="comma-separated words or phrases (replaces the language's list)")
    ap.add_argument("--protect", default="", help="word indices never dropped: 40,41")
    ap.add_argument("--wav")
    ap.add_argument("--wav-start", type=float, default=0.0)
    ap.add_argument("--track", default="V1")
    ap.add_argument("--label", default="tighten")
    a = ap.parse_args(argv)
    fps = Fraction(a.fps)
    words = load_words(a.words)
    fillers = a.fillers.split(",") if a.fillers else FILLERS.get(a.lang, FILLERS["en"])
    protect = {int(x) for x in a.protect.split(",") if x.strip()}
    vad = speech_mask(a.wav, a.wav_start) if a.wav else None
    ranges = parse_ranges(a.keep)
    spans, removed, moved, connected, pauses, pause_s = tighten(words, ranges, float(fps), a.min_pause, a.keep_pause,
                                                               [f.strip() for f in fillers if f.strip()], protect, vad)
    cmd, frames = to_batch(spans, a.item, fps, a.track, a.label)
    seconds = float(frames / fps)
    source = sum(words[hi]["end"] - words[lo]["start"] for lo, hi in ranges)
    report = {"spans": len(spans), "cuts": len(spans) - 1, "seconds": round(seconds, 2), "selectedSeconds": round(source, 2),
              "cutsPerMinute": round(60 * (len(spans) - 1) / seconds, 1) if seconds else 0,
              "removed": {"fillers": [r for r in removed if r["kind"] == "filler"],
                          "repeats": [r for r in removed if r["kind"] == "repeat"],
                          "pauses": pauses, "pauseSeconds": round(pause_s, 2)},
              "edgesMovedBySound": moved if vad else None, "connectedSpeech": connected,
              "shortSpans": [s["text"] for s in spans if s["frames"] / float(fps) < 0.4]}
    json.dump({"command": cmd, "report": report}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
