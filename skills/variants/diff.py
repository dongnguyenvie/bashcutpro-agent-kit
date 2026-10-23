#!/usr/bin/env python3
"""Compare two versions of an edit (two sequences of one project): what a viewer would notice.

    diff.py A.json B.json [--review-a RA.json --review-b RB.json] [--one-change] [--hook 3] [--text]

A.json / B.json: the output of MCP `sequence_inspect` (times in ticks) or of `bashcut.timeline.summary` (times in
seconds) for each sequence, saved as files. Optional review results (`bashcut.review.run`: `scores` per category and
`findings` with `severity`) add the score change. Prints JSON (or lines with --text):

- `duration`: seconds of A and B and the change;
- `cuts`: cut times (clip edges on video tracks) only in A (`removed`) or only in B (`added`), 1 frame tolerance;
- `clips`: shots (media item + source in) only in A or only in B;
- `hook`: what plays in the first --hook seconds (default 3) of each, when it differs;
- `music`: audio clips not linked to a video clip (beds, music, effects) only in A or only in B;
- `looks`: video effects used, with counts, where they differ;
- `captions`: caption count, when the input has one;
- `review`: score per category and blocking findings, when given;
- `changed`: the kinds of change found; with --one-change, exit 1 when more than one kind changed (ad tests change
  one thing at a time).

Standard library only.
"""

import argparse
import json
import sys

TPS = 254016000000  # engine ticks per second
BLOCKING = {"blocker", "blocking", "high", "error"}


def load(path):
    with open(path, encoding="utf-8") as f:
        value = json.load(f)
    # a saved MCP tool result: {"content": [{"type": "text", "text": "<json>"}]}
    if isinstance(value, dict) and isinstance(value.get("content"), list) and value["content"]:
        try:
            value = json.loads(value["content"][0].get("text", ""))
        except (ValueError, AttributeError):
            pass
    return value


def fps_of(seq):
    settings = seq.get("settings") or {}
    rate = settings.get("frame_rate") or settings.get("frameRate") or settings.get("fps") or seq.get("fps")
    if isinstance(rate, dict):  # {"num", "den"}
        num, den = rate.get("num") or rate.get("numerator"), rate.get("den") or rate.get("denominator") or 1
        return float(num) / float(den) if num else 30.0
    try:
        return float(rate) if rate else 30.0
    except (TypeError, ValueError):
        return 30.0


def normalise(seq):
    """{duration, fps, video: [[clip]], audio: [[clip]], captions?}; clip = {key, name, start, end, link, effects}."""
    if "tracks" in seq:  # bashcut.timeline.summary: seconds, tracks with a kind
        video, audio = [], []
        for t in seq["tracks"]:
            kind = str(t.get("kind") or t.get("type") or t.get("name") or "")[:1].upper()
            clips = [{"key": (c.get("item"), round(float(c.get("sourceIn", 0)), 3)), "name": c.get("name") or str(c.get("item")),
                      "start": float(c.get("start", 0)), "end": float(c.get("end", 0)), "link": c.get("link"),
                      "effects": [e if isinstance(e, str) else e.get("effect") for e in c.get("effects") or []]}
                     for c in t.get("clips") or t.get("items") or []]
            (audio if kind == "A" else video).append(clips)
        duration = float(seq.get("duration") or max([c["end"] for t in video + audio for c in t] or [0]))
        captions = seq.get("captions")
        return {"duration": duration, "fps": fps_of(seq), "video": video, "audio": audio,
                "captions": len(captions) if isinstance(captions, list) else captions}

    def track(t):
        return [{"key": (c.get("item"), round(c.get("sourceIn", 0) / TPS, 3)), "name": c.get("name") or str(c.get("item")),
                 "start": c.get("start", 0) / TPS, "end": c.get("end", c.get("start", 0) + c.get("duration", 0)) / TPS,
                 "link": c.get("link"), "effects": [e.get("effect") for e in c.get("effects") or [] if e.get("enabled", True)]}
                for c in t.get("items") or []]

    video = [track(t) for t in seq.get("video") or []]
    audio = [track(t) for t in seq.get("audio") or []]
    duration = seq.get("duration")
    duration = duration / TPS if duration is not None else max([c["end"] for t in video + audio for c in t] or [0])
    captions = seq.get("captions")
    return {"duration": duration, "fps": fps_of(seq), "video": video, "audio": audio,
            "captions": len(captions) if isinstance(captions, list) else captions}


def cut_times(n):
    edges = set()
    for t in n["video"]:
        for c in t:
            edges.add(round(c["start"], 3))
            edges.add(round(c["end"], 3))
    edges.discard(0.0)
    edges.discard(round(n["duration"], 3))
    return sorted(edges)


def only_in(xs, ys, tolerance):
    return [x for x in xs if not any(abs(x - y) <= tolerance for y in ys)]


def shots(n):
    return {c["key"]: c["name"] for t in n["video"] for c in t}


def beds(n):
    """Audio clips not linked to a picture clip: music, beds, effects."""
    return {c["key"]: c["name"] for t in n["audio"] for c in t if not c.get("link")}


def looks(n):
    counts = {}
    for t in n["video"]:
        for c in t:
            for e in c["effects"]:
                if e:
                    counts[e] = counts.get(e, 0) + 1
    return counts


def opening(n, seconds):
    names = []
    for t in n["video"]:
        for c in sorted(t, key=lambda c: c["start"]):
            if c["start"] < seconds and c["name"] not in names:
                names.append(c["name"])
    return names


def review_of(r):
    if not r:
        return None
    findings = r.get("findings") or []
    return {"scores": r.get("scores") or {},
            "blocking": sum(1 for f in findings if str(f.get("severity", "")).lower() in BLOCKING),
            "findings": len(findings)}


def diff(a, b, review_a=None, review_b=None, hook=3.0):
    na, nb = normalise(a), normalise(b)
    frame = 1.0 / max(na["fps"], nb["fps"], 1.0)
    ca, cb = cut_times(na), cut_times(nb)
    sa, sb = shots(na), shots(nb)
    ba, bb = beds(na), beds(nb)
    la, lb = looks(na), looks(nb)
    out = {"duration": {"a": round(na["duration"], 3), "b": round(nb["duration"], 3),
                        "change": round(nb["duration"] - na["duration"], 3)},
           "cuts": {"a": len(ca), "b": len(cb), "removed": only_in(ca, cb, frame), "added": only_in(cb, ca, frame)},
           "clips": {"removed": sorted(sa[k] for k in sa.keys() - sb.keys()), "added": sorted(sb[k] for k in sb.keys() - sa.keys())},
           "music": {"removed": sorted(ba[k] for k in ba.keys() - bb.keys()), "added": sorted(bb[k] for k in bb.keys() - ba.keys())},
           "looks": {k: {"a": la.get(k, 0), "b": lb.get(k, 0)} for k in sorted(set(la) | set(lb)) if la.get(k, 0) != lb.get(k, 0)}}
    ha, hb = opening(na, hook), opening(nb, hook)
    if ha != hb:
        out["hook"] = {"seconds": hook, "a": ha, "b": hb}
    if na["captions"] is not None or nb["captions"] is not None:
        out["captions"] = {"a": na["captions"], "b": nb["captions"]}
    ra, rb = review_of(review_a), review_of(review_b)
    if ra or rb:
        ra, rb = ra or {"scores": {}, "blocking": 0, "findings": 0}, rb or {"scores": {}, "blocking": 0, "findings": 0}
        out["review"] = {"scores": {k: {"a": ra["scores"].get(k), "b": rb["scores"].get(k)}
                                    for k in sorted(set(ra["scores"]) | set(rb["scores"]))},
                         "blocking": {"a": ra["blocking"], "b": rb["blocking"]}}
    changed = []
    if out["cuts"]["added"] or out["cuts"]["removed"] or out["clips"]["added"] or out["clips"]["removed"]:
        changed.append("cut")
    elif abs(out["duration"]["change"]) >= frame:
        changed.append("length")
    if "hook" in out:
        changed.append("hook")
    if out["music"]["added"] or out["music"]["removed"]:
        changed.append("music")
    if out["looks"]:
        changed.append("look")
    if "captions" in out and None not in out["captions"].values() and out["captions"]["a"] != out["captions"]["b"]:
        changed.append("captions")
    out["changed"] = changed
    return out


def text(d):
    lines = ["length %.1f s -> %.1f s (%+.1f s)" % (d["duration"]["a"], d["duration"]["b"], d["duration"]["change"]),
             "cuts %d -> %d: %d added, %d removed" % (d["cuts"]["a"], d["cuts"]["b"], len(d["cuts"]["added"]), len(d["cuts"]["removed"]))]
    if d["clips"]["added"] or d["clips"]["removed"]:
        lines.append("shots added: %s; removed: %s" % (", ".join(d["clips"]["added"]) or "-", ", ".join(d["clips"]["removed"]) or "-"))
    if "hook" in d:
        lines.append("first %gs: A %s | B %s" % (d["hook"]["seconds"], ", ".join(d["hook"]["a"]), ", ".join(d["hook"]["b"])))
    if d["music"]["added"] or d["music"]["removed"]:
        lines.append("music added: %s; removed: %s" % (", ".join(d["music"]["added"]) or "-", ", ".join(d["music"]["removed"]) or "-"))
    for name, n in d["looks"].items():
        lines.append("look %s: %d -> %d clips" % (name, n["a"], n["b"]))
    if "captions" in d:
        lines.append("captions %s -> %s" % (d["captions"]["a"], d["captions"]["b"]))
    if "review" in d:
        for k, s in d["review"]["scores"].items():
            lines.append("review %s: %s -> %s" % (k, s["a"], s["b"]))
        lines.append("blocking findings %d -> %d" % (d["review"]["blocking"]["a"], d["review"]["blocking"]["b"]))
    lines.append("changed: %s" % (", ".join(d["changed"]) or "nothing"))
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--review-a")
    p.add_argument("--review-b")
    p.add_argument("--hook", type=float, default=3.0, help="seconds counted as the opening (default 3)")
    p.add_argument("--one-change", action="store_true", help="exit 1 when more than one kind of change was found")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)
    try:
        d = diff(load(args.a), load(args.b), load(args.review_a) if args.review_a else None,
                 load(args.review_b) if args.review_b else None, args.hook)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(text(d) if args.text else json.dumps(d, ensure_ascii=False, indent=2))
    return 1 if args.one_change and len(d["changed"]) > 1 else 0


if __name__ == "__main__":
    sys.exit(main())
