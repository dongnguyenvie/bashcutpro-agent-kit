#!/usr/bin/env python3
"""Map a published video's audience retention onto its edit: where viewers left or rewatched, and what was on screen.

    outcomes.py RETENTION.csv --sequence SEQ.json [--duration S] [--project P.fcproj --video NAME]
                [--markers-out batch.json] [--learn] [--text]

RETENTION.csv: an analytics export the user downloaded (YouTube Studio audience retention, TikTok or Facebook
retention): one row per point, a position column (seconds, or percent of the video: "Video position (%)") and a
retention column ("Absolute audience retention (%)", "Viewers (%)", "Retention", "Audience"). Columns are found by
name; percent positions need the video's length (from SEQ.json, or --duration). Nothing is fetched from any account.

SEQ.json: `sequence_inspect` (ticks) or `bashcut.timeline.summary` (seconds) of the sequence that was exported.
Its clips give the cuts and what was on screen, its markers the sections.

Finds:
- `hook`: retention at 3 s and 30 s (or the end);
- `drops`: where retention falls clearly faster than the video's usual decline (default at least 3 points within
  2 s and three times the median fall), each with the nearest cut (within 1 s), the section marker and the clips on
  screen;
- `rewatches`: where retention rises (viewers going back), with the same context.

--project writes the findings to `<name>.fcproj.bashcut/outcomes/<video>.json`. --markers-out writes a
`command_batch` of `markers.add` (red for drops, green for rewatches) to run on a copy of the sequence.
--learn records each drop at a cut as a lesson through self-learn's knowledge.py (tags outcomes, pacing) and an
existing one as seen again. Standard library only.
"""

import argparse
import csv
import importlib.util
import json
import os
import re
import statistics
import sys

TPS = 254016000000  # FilmCraft ticks per second
POSITION = re.compile(r"position|second|time|moment|thời", re.I)
RETENTION = re.compile(r"retention|viewers|audience|watch|giữ chân|người xem", re.I)


def number(text):
    text = str(text).strip().replace("%", "").replace(",", ".") if text is not None else ""
    try:
        return float(text)
    except ValueError:
        m = re.match(r"^(\d+):(\d+(?:\.\d+)?)$", text)  # 0:12
        return int(m.group(1)) * 60 + float(m.group(2)) if m else None


def read_curve(path, duration=None):
    """[(seconds, retention percent)], sorted. Raises ValueError when the columns cannot be found."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError("%s is empty" % path)
    header = rows[0]
    pos = next((i for i, h in enumerate(header) if POSITION.search(h)), None)
    ret = [i for i, h in enumerate(header) if RETENTION.search(h) and i != pos]
    # prefer absolute retention over relative (YouTube exports both)
    ret = sorted(ret, key=lambda i: ("relative" in header[i].lower(), "absolute" not in header[i].lower()))
    if pos is None or not ret:
        raise ValueError("no position and retention columns in %s (header: %s)" % (path, ", ".join(header)))
    ret = ret[0]
    points = []
    for row in rows[1:]:
        if len(row) <= max(pos, ret):
            continue
        x, y = number(row[pos]), number(row[ret])
        if x is not None and y is not None:
            points.append((x, y))
    if len(points) < 3:
        raise ValueError("%s has fewer than 3 points" % path)
    percent_position = "%" in header[pos] or "position" in header[pos].lower()
    if percent_position:
        if not duration:
            raise ValueError("the export gives positions in percent: the video's length is needed (--duration)")
        scale = duration / (100.0 if max(x for x, _ in points) > 1.0 else 1.0)
        points = [(x * scale, y) for x, y in points]
    if max(y for _, y in points) <= 1.0:  # fractions, not percent
        points = [(x, y * 100.0) for x, y in points]
    return sorted(points)


def load(path):
    with open(path, encoding="utf-8") as f:
        value = json.load(f)
    if isinstance(value, dict) and isinstance(value.get("content"), list) and value["content"]:
        try:
            value = json.loads(value["content"][0].get("text", ""))
        except (ValueError, AttributeError):
            pass
    return value


def edit_of(seq):
    """{duration, clips: [{name, start, end, track}], markers: [{name, start, end}], cuts: [seconds]} in seconds."""
    clips, markers = [], []
    if "tracks" in seq:  # timeline summary, seconds
        for t in seq["tracks"]:
            for c in t.get("clips") or t.get("items") or []:
                clips.append({"name": c.get("name") or str(c.get("item")), "start": float(c.get("start", 0)),
                              "end": float(c.get("end", 0)), "track": t.get("name") or t.get("kind") or ""})
        for m in seq.get("markers") or []:
            start = float(m.get("start", 0))
            markers.append({"name": m.get("name") or "", "start": start, "end": start + float(m.get("duration", 0))})
        duration = float(seq.get("duration") or max([c["end"] for c in clips] or [0]))
    else:  # sequence_inspect, ticks
        for kind in ("video", "audio"):
            for i, t in enumerate(seq.get(kind) or []):
                for c in t.get("items") or []:
                    clips.append({"name": c.get("name") or str(c.get("item")), "start": c.get("start", 0) / TPS,
                                  "end": c.get("end", c.get("start", 0) + c.get("duration", 0)) / TPS,
                                  "track": t.get("name") or "%s%d" % (kind[0].upper(), i + 1)})
        for m in seq.get("markers") or []:
            start = m.get("start", 0) / TPS
            markers.append({"name": m.get("name") or "", "start": start, "end": start + m.get("duration", 0) / TPS})
        duration = seq["duration"] / TPS if seq.get("duration") is not None else max([c["end"] for c in clips] or [0])
    video = [c for c in clips if str(c["track"]).upper().startswith("V")]
    cuts = sorted({round(e, 3) for c in video for e in (c["start"], c["end"]) if 0 < e < duration - 1e-6})
    return {"duration": duration, "clips": clips, "markers": markers, "cuts": cuts}


def at(curve, seconds):
    """Retention at a time, linearly interpolated."""
    if seconds <= curve[0][0]:
        return curve[0][1]
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if x0 <= seconds <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (seconds - x0) / (x1 - x0)
    return curve[-1][1]


def context(edit, seconds, near=1.0):
    cut = min(edit["cuts"], key=lambda c: abs(c - seconds), default=None)
    section = next((m["name"] for m in edit["markers"] if m["start"] <= seconds < max(m["end"], m["start"] + 1e-6)), None)
    if section is None:  # point markers: the last one before
        before = [m for m in edit["markers"] if m["start"] <= seconds]
        section = before[-1]["name"] if before else None
    on_screen = sorted({c["name"] for c in edit["clips"] if c["start"] <= seconds < c["end"]})
    out = {"onScreen": on_screen}
    if cut is not None and abs(cut - seconds) <= near:
        out["cut"] = cut
        out["cutTo"] = sorted({c["name"] for c in edit["clips"] if abs(c["start"] - cut) < 1e-3
                               and str(c["track"]).upper().startswith("V")})
    if section:
        out["section"] = section
    return out


def events(curve, window=2.0, min_points=3.0, factor=3.0):
    """Falls and rises over `window` seconds that stand out from the curve's usual decline."""
    end = curve[-1][0]
    start = 3.0 if end > 6.0 else 0.0  # the first seconds always fall fast: that is the hook figure, not a drop
    step = max(0.5, window / 4)
    slopes = []
    t = curve[0][0]
    while t + window <= end:
        slopes.append((t, at(curve, t + window) - at(curve, t)))
        t += step
    if not slopes:
        return [], []
    usual = abs(statistics.median([s for _, s in slopes])) or 0.1
    drops, rises = [], []
    for t, change in slopes:
        if t < start:
            continue
        if change <= -min_points and -change >= factor * usual:
            drops.append((t, change))
        elif change >= 1.0:
            rises.append((t, change))

    def merge(found, pick):
        merged = []
        for t, change in found:
            if merged and t - merged[-1][0] <= window:
                if pick(change, merged[-1][1]):
                    merged[-1] = (t, change)
                continue
            merged.append((t, change))
        return merged

    return merge(drops, lambda a, b: a < b), merge(rises, lambda a, b: a > b)


def steepest(curve, t, window):
    """The time inside [t, t + window] where the curve falls (or rises) the most between points."""
    inside = [(x0, x1, y1 - y0) for (x0, y0), (x1, y1) in zip(curve, curve[1:]) if x1 > t and x0 < t + window]
    if not inside:
        return t + window / 2
    x0, x1, _ = max(inside, key=lambda s: abs(s[2]))
    return (max(x0, t) + min(x1, t + window)) / 2


def analyse(curve, edit, window=2.0, min_points=3.0, factor=3.0):
    drops, rises = events(curve, window, min_points, factor)
    end = edit["duration"] or curve[-1][0]
    out = {"duration": round(end, 3), "points": len(curve),
           "hook": {"at3s": round(at(curve, 3.0), 1), "at30s": round(at(curve, min(30.0, end)), 1),
                    "end": round(curve[-1][1], 1)},
           "drops": [], "rewatches": []}
    for t, change in drops:
        when = steepest(curve, t, window)
        out["drops"].append(dict({"time": round(when, 2), "points": round(change, 1)}, **context(edit, when)))
    for t, change in rises:
        when = steepest(curve, t, window)
        out["rewatches"].append(dict({"time": round(when, 2), "points": round(change, 1)}, **context(edit, when)))
    return out


def clock(seconds):
    return "%d:%04.1f" % (seconds // 60, seconds % 60)


def marker_batch(found):
    commands = []
    for kind, color in (("drops", "Red"), ("rewatches", "Green")):
        for e in found[kind]:
            what = "cut to %s" % ", ".join(e["cutTo"]) if e.get("cutTo") else "on screen: %s" % ", ".join(e["onScreen"])
            commands.append({"id": "markers.add", "params": {
                "target": "program", "time": int(round(e["time"] * TPS)), "color": color,
                "name": "%s %+.1f pts" % ("drop" if kind == "drops" else "rewatch", e["points"]),
                "comment": "%s%s" % (what, " (section %s)" % e["section"] if e.get("section") else "")}})
    return {"commands": commands}


def knowledge_store():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "self-learn", "knowledge.py")
    spec = importlib.util.spec_from_file_location("knowledge", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Store()


def learn(found, video, project=None, store=None):
    """One lesson per drop at a cut (or `--seen` on the lesson already about that cut)."""
    store = store or knowledge_store()
    recorded = []
    for e in found["drops"]:
        if "cut" not in e:
            continue
        target = ", ".join(e.get("cutTo") or e["onScreen"]) or "the next shot"
        title = "Viewers left at the cut to %s" % target
        evidence = "%s: %+.1f points at %s (cut at %s)%s" % (video, e["points"], clock(e["time"]), clock(e["cut"]),
                                                             ", section %s" % e["section"] if e.get("section") else "")
        existing = [r for r in store.lessons() if r.get("title") == title and r.get("status") != "disabled"]
        if existing:
            recorded.append(store.update_lesson(existing[0]["id"], seen=True, project=project, evidence=evidence))
            continue
        recorded.append(store.add_lesson(
            title, symptom="retention fell %.1f points within 2 s of the cut to %s" % (-e["points"], target),
            cause="to confirm on the frame: what changed at the cut (shot, line, music, text)",
            fix="look at the cut before repeating it: keep the promise on screen, cut on the line, or move the shot later",
            tags=["outcomes", "pacing"], evidence=evidence,
            check="Does the cut to %s keep the viewer's question open?" % target,
            status="proposed", project=project))
    return recorded


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("csv")
    p.add_argument("--sequence", required=True, help="sequence_inspect or bashcut.timeline.summary of the exported sequence")
    p.add_argument("--duration", type=float, help="the video's length in seconds (default: the sequence's)")
    p.add_argument("--project", help="the .fcproj: findings go to its sidecar")
    p.add_argument("--video", default="video", help="a name for this published video (file name in the sidecar)")
    p.add_argument("--markers-out", help="write a command_batch of markers.add here")
    p.add_argument("--learn", action="store_true", help="record drops at cuts as lessons (self-learn)")
    p.add_argument("--window", type=float, default=2.0)
    p.add_argument("--min-points", type=float, default=3.0)
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)
    try:
        edit = edit_of(load(args.sequence))
        curve = read_curve(args.csv, args.duration or edit["duration"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        return 2
    found = analyse(curve, edit, args.window, args.min_points)
    found["video"] = args.video
    if args.project:
        folder = os.path.join(os.path.abspath(args.project) + ".bashcut", "outcomes")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, re.sub(r"[^\w.-]+", "-", args.video) + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(found, f, ensure_ascii=False, indent=2)
        found["sidecar"] = path
    if args.markers_out:
        with open(args.markers_out, "w", encoding="utf-8") as f:
            json.dump(marker_batch(found), f, ensure_ascii=False, indent=2)
    if args.learn:
        found["lessons"] = [r["id"] for r in learn(found, args.video, args.project)]
    if args.text:
        lines = ["retention: %.0f%% at 3 s, %.0f%% at 30 s, %.0f%% at the end" % (
            found["hook"]["at3s"], found["hook"]["at30s"], found["hook"]["end"])]
        for e in found["drops"]:
            lines.append("drop %+.1f at %s%s; on screen %s%s" % (
                e["points"], clock(e["time"]), " (cut at %s to %s)" % (clock(e["cut"]), ", ".join(e["cutTo"])) if "cut" in e else "",
                ", ".join(e["onScreen"]) or "-", ", section %s" % e["section"] if e.get("section") else ""))
        for e in found["rewatches"]:
            lines.append("rewatch %+.1f at %s; on screen %s" % (e["points"], clock(e["time"]), ", ".join(e["onScreen"]) or "-"))
        print("\n".join(lines))
    else:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
