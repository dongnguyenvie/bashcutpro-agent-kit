#!/usr/bin/env python3
"""Quality bench: Pro vs BashCut on the raw test set (BashCutPro#58). Rubric: bench/rubric.md.

    score.py plan --raw /abs/resources/raw                  # the jobs and the input files each one gets
    score.py score --runs /abs/bench-runs [--date 2026-10-20] [--out scorecard.md]
    score.py blind --runs /abs/bench-runs --out /abs/blind  # random A/B labels for the owner's side-by-side

Runs folder: `<runs>/<side>/<job id>/` for side `pro` and `bashcut`, each with `metrics.json` (one object, or a
list for a job with several outputs) gathered after the run:

    {"output": "short.mp4", "seconds": 52.4,
     "loudness": <loudness.py JSON of a WAV export: integratedLufs, truePeakDbtp>,
     "review": {"findings": [{"severity": "blocker|major|minor|polish", "category": "..."}]},
     "captions": "short.srt" (relative to the job folder) | null,
     "safeArea": {"outside": 0, "checked": 12},
     "cuts": [seconds], "words": "words.json" | [[start, end], ...],
     "picture": {"blackFrames": 0, "frozenSeconds": 0.0},
     "renderSeconds": 41.0}

Missing measurements are reported as "not measured" and leave their category out of the total, never scored as 0.
Prints the scorecard (Markdown, from bench/scorecard-template.md) or writes it with --out. Standard library only.
"""

import argparse
import datetime
import glob
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIDES = ("pro", "bashcut")
WEIGHTS = {"sound": 20, "captions": 20, "edit": 20, "picture": 15, "review": 15, "length": 10}
SEVERITY = {"blocker": 25, "major": 10, "minor": 3, "polish": 0}
# bashcut.review.run (#57) names its own levels; a measured warning is not automatically a blocker (skills/review)
ENGINE_SEVERITY = {"blocking": "blocker", "warning": "minor", "info": "polish"}
MARGIN = 3.0  # a job is won by at least this many points of the total; closer is a tie


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Measurements --------------------------------------------------------------------------------------------------
def srt_cues(path):
    """[(start, end, text)] from an SRT or VTT file."""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    stamp = r"(\d+):(\d\d):(\d\d)[,.](\d{3})"
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        m = re.search(stamp + r"\s*-->\s*" + stamp, block)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
        body = " ".join(line.strip() for line in block[m.end():].strip().splitlines())
        body = re.sub(r"<[^>]+>", "", body)
        cues.append((start, end, body))
    return cues


def reading_speeds(cues):
    """Characters per second of each cue (spaces counted, as subtitle guides do)."""
    return [len(text) / max(end - start, 0.001) for start, end, text in cues if text]


def cut_on_word_rate(cuts, words, edge=0.02):
    """Share of cuts that do not fall inside a spoken word (an edge within 20 ms of a word boundary is fine)."""
    if not cuts:
        return None
    spans = [(w["start"], w["end"]) if isinstance(w, dict) else (w[0], w[1]) for w in words]
    inside = sum(1 for c in cuts if any(s + edge < c < e - edge for s, e in spans))
    return 1.0 - inside / float(len(cuts))


# Scores (0-100 per category) -----------------------------------------------------------------------------------
def score_sound(m, target):
    loud = m.get("loudness") or {}
    lufs, peak = loud.get("integratedLufs"), loud.get("truePeakDbtp")
    if lufs is None:
        return None, "not measured"
    off = abs(lufs - target.get("lufs", -14))
    score = 100.0 if off <= 1.0 else max(0.0, 100.0 - 20.0 * (off - 1.0))
    note = "%.1f LUFS" % lufs
    if peak is not None:
        note += ", %.1f dBTP" % peak
        if peak > target.get("truePeak", -1.0):
            score = max(0.0, score - 30.0)
    return score, note


def score_captions(m, target, folder):
    if not target.get("captions"):
        return None, "no captions in this job"
    if not m.get("captions"):
        return 0.0, "captions missing"
    path = m["captions"] if os.path.isabs(m["captions"]) else os.path.join(folder, m["captions"])
    try:
        speeds = reading_speeds(srt_cues(path))
    except OSError:
        return None, "captions file not found"
    if not speeds:
        return 0.0, "no cues"
    comfortable = sum(1 for s in speeds if s <= 20) / float(len(speeds))
    hard = sum(1 for s in speeds if s > 25) / float(len(speeds))
    score = 100.0 * comfortable - 100.0 * hard
    safe = m.get("safeArea") or {}
    if safe.get("checked"):
        score -= 50.0 * safe.get("outside", 0) / float(safe["checked"])
    return max(0.0, score), "%d cues, %.0f%% at or under 20 cps, %.0f%% over 25" % (len(speeds), 100 * comfortable, 100 * hard)


def score_edit(m, folder):
    words = m.get("words")
    if isinstance(words, str):
        try:
            words = load_json(os.path.join(folder, words))
        except (OSError, ValueError):
            words = None
    if words is None or m.get("cuts") is None:
        return None, "not measured"
    rate = cut_on_word_rate(m["cuts"], words)
    if rate is None:
        return 100.0, "no cuts"
    return 100.0 * rate, "%.0f%% of %d cuts on a word edge" % (100 * rate, len(m["cuts"]))


def score_picture(m):
    pic = m.get("picture")
    if pic is None:
        return None, "not measured"
    black, frozen = pic.get("blackFrames", 0), pic.get("frozenSeconds", 0.0)
    return max(0.0, 100.0 - 10.0 * black - 20.0 * frozen), "%d black frames, %.1f s frozen" % (black, frozen)


def score_review(m):
    review = m.get("review")
    if review is None:
        return None, "not measured"
    counts = {}
    for f in review.get("findings") or []:
        sev = str(f.get("severity", "minor")).lower()
        sev = ENGINE_SEVERITY.get(sev, sev)
        counts[sev] = counts.get(sev, 0) + 1
    score = 100.0 - sum(SEVERITY.get(k, 3) * n for k, n in counts.items())
    return max(0.0, score), ", ".join("%d %s" % (n, k) for k, n in sorted(counts.items())) or "no findings"


def score_length(m, target):
    seconds, band = m.get("seconds"), target.get("seconds")
    if seconds is None:
        return None, "not measured"
    if not band:
        return None, "%.1f s (no target)" % seconds
    low, high = band
    if low <= seconds <= high:
        return 100.0, "%.1f s" % seconds
    off = (low - seconds) / low if seconds < low else (seconds - high) / high
    return max(0.0, 100.0 - 100.0 * off), "%.1f s (target %g-%g)" % (seconds, low, high)


def score_output(m, target, folder):
    parts = {"sound": score_sound(m, target), "captions": score_captions(m, target, folder),
             "edit": score_edit(m, folder), "picture": score_picture(m), "review": score_review(m),
             "length": score_length(m, target)}
    scored = {k: v[0] for k, v in parts.items() if v[0] is not None}
    weight = sum(WEIGHTS[k] for k in scored)
    total = sum(WEIGHTS[k] * v for k, v in scored.items()) / weight if weight else None
    return {"total": total, "parts": {k: {"score": v[0], "note": v[1]} for k, v in parts.items()},
            "renderSeconds": m.get("renderSeconds")}


def score_side(runs, side, job):
    folder = os.path.join(runs, side, job["id"])
    path = os.path.join(folder, "metrics.json")
    if not os.path.isfile(path):
        return None
    metrics = load_json(path)
    outputs = [score_output(m, job.get("target") or {}, folder) for m in (metrics if isinstance(metrics, list) else [metrics])]
    totals = [o["total"] for o in outputs if o["total"] is not None]
    return {"outputs": outputs, "total": sum(totals) / len(totals) if totals else None}


def verdict(pro, bashcut):
    if not pro or pro["total"] is None:
        return "pending"
    if not bashcut or bashcut["total"] is None:
        return "pro only"
    gap = pro["total"] - bashcut["total"]
    return "pro" if gap >= MARGIN else "bashcut" if gap <= -MARGIN else "tie"


def score(runs, jobs):
    rows = []
    for job in jobs["jobs"]:
        pro, bashcut = score_side(runs, "pro", job), score_side(runs, "bashcut", job)
        rows.append({"job": job, "pro": pro, "bashcut": bashcut, "winner": verdict(pro, bashcut)})
    return rows


def fmt(value):
    return "–" if value is None else "%.0f" % value


def render(rows, date, template):
    summary, detail, losses = [], [], []
    for r in rows:
        job, pro, bc = r["job"], r["pro"], r["bashcut"]
        summary.append("| %s | %s | %s | %s |" % (job["title"], fmt(pro and pro["total"]), fmt(bc and bc["total"]), r["winner"]))
        if r["winner"] == "bashcut":
            losses.append("- [ ] %s: Pro %s vs BashCut %s, open a follow-up issue" % (job["title"], fmt(pro["total"]), fmt(bc["total"])))
        detail.append("### %s\n\n| Category | Pro | BashCut |\n|---|---|---|" % job["title"])
        for cat in WEIGHTS:
            cells = []
            for side in (pro, bc):
                if not side:
                    cells.append("not run")
                    continue
                parts = [o["parts"][cat] for o in side["outputs"]]
                scored = [p["score"] for p in parts if p["score"] is not None]
                cells.append("%s (%s)" % (fmt(sum(scored) / len(scored)) if scored else "–", "; ".join(p["note"] for p in parts)))
            detail.append("| %s | %s | %s |" % (cat, cells[0], cells[1]))
        renders = [", ".join("%.0f s" % o["renderSeconds"] for o in s["outputs"] if o.get("renderSeconds") is not None) if s else ""
                   for s in (pro, bc)]
        detail.append("| render time (not scored) | %s | %s |\n" % (renders[0] or "–", renders[1] or "–"))
    pending = sum(1 for r in rows if r["winner"] == "pending")
    out = template
    for key, value in {"{{date}}": date, "{{summary}}": "\n".join(summary), "{{detail}}": "\n".join(detail),
                       "{{losses}}": "\n".join(losses) or "None.",
                       "{{status}}": ("%d of %d jobs not run yet." % (pending, len(rows))) if pending else "All jobs run."}.items():
        out = out.replace(key, value)
    return out


def plan(raw, jobs):
    out = []
    for job in jobs["jobs"]:
        files = sorted({f for pattern in job["inputs"] for f in glob.glob(os.path.join(raw, pattern))})
        out.append({"job": job["id"], "files": [os.path.relpath(f, raw).replace(os.sep, "/") for f in files], "missing": not files})
    return out


def blind(runs, jobs, folder, rng=None):
    """Per job, which side is A and which is B; the key goes to a separate file the owner opens after judging."""
    rng = rng or random.Random()
    os.makedirs(folder, exist_ok=True)
    sheet, key = [], {}
    for job in jobs["jobs"]:
        sides = list(SIDES)
        rng.shuffle(sides)
        key[job["id"]] = {"A": sides[0], "B": sides[1]}
        sheet.append({"job": job["id"], "title": job["title"],
                      "A": os.path.join(runs, sides[0], job["id"]), "B": os.path.join(runs, sides[1], job["id"]),
                      "pick": "A | B | tie"})
    with open(os.path.join(folder, "sheet.json"), "w", encoding="utf-8") as f:
        json.dump(sheet, f, indent=2)
    with open(os.path.join(folder, "key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=2)
    return sheet, key


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("command", choices=("plan", "score", "blind"))
    p.add_argument("--jobs", default=os.path.join(HERE, "jobs.json"))
    p.add_argument("--raw")
    p.add_argument("--runs")
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--out")
    args = p.parse_args(argv)
    jobs = load_json(args.jobs)
    if args.command == "plan":
        if not args.raw:
            p.error("plan needs --raw")
        print(json.dumps(plan(args.raw, jobs), indent=2))
        return 0
    if not args.runs:
        p.error("%s needs --runs" % args.command)
    if args.command == "blind":
        if not args.out:
            p.error("blind needs --out")
        sheet, _ = blind(args.runs, jobs, args.out)
        print(json.dumps(sheet, indent=2))
        return 0
    with open(os.path.join(HERE, "scorecard-template.md"), encoding="utf-8") as f:
        text = render(score(args.runs, jobs), args.date, f.read())
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
