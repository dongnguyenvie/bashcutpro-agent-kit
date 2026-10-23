#!/usr/bin/env python3
"""Captions grouped from the words at a readable speed, and the fix for fast cues, without paraphrasing.
BashCutPro's `transcript.createCaptions` breaks a cue on the character limit and pauses of 1 s or more, and ends each
cue on its last word, so cues end mid-phrase and fast ones have no silence to hold into. This does it from the words:

  captions_fit.py group words.json --out cues.srt [--max-chars 42] [--lines 2] [--max-cps 20]   # then captions.import
  captions_fit.py plan caps.json [--max-cps 20] [--jsonl]       # fix an existing track (translated, imported, edited)
  captions_fit.py report caps.json|cues.srt [--max-cps 20]      # cues, % at or under the limit, % over 25, worst
  captions_fit.py apply --cli bashcutpro-cli --project p.fcproj [group options]   # group the active sequence and import

`group` reads `transcript.inspect` output (the edited sequence's words, ticks) or any JSON of {text|word, start, end}
words (seconds) and breaks a cue at a sentence end, at a comma once the cue is half full (--fill), at a pause of
--break-gap seconds, at a speaker change, or when the text no longer fits --max-chars × --lines or --max-seconds;
never after "a", "the", "and"… when it breaks on the limit. Both modes then drop hesitation fillers ("um", "uh", …)
and stuttered repeats ("the the") from the text (never other words; --keep-fillers keeps them), hold each cue into
the silence after it until it reads at 95 % of --max-cps (up to the next cue less --gap-frames, at least
--min-seconds), start it up to --lead seconds before its first word when that is not enough, and merge a still-fast
cue with a neighbour when the pair reads under the limit and fits the lines; --trim-hedges then drops "just",
"actually", "you know"… from the cues still over. `plan` prints `commands` for
`bashcut.batch {commands, label}` (`--jsonl`: one per line for `bashcutpro-cli run`). Every mode prints `before` /
`after` stats and `left`: cues still over the limit (shorten them yourself, or keep them when the speech is that
fast). `apply` does `group` through the engine's CLI on a saved project (a `bashcut-batch` plugin step, or any shell):
reads the active sequence's words, length and frame rate, writes the SRT (--out, default `<project folder>/captions/
<project>.srt`), replaces the first caption track with it (`captions.import`) and saves. Standard library only
(Python 3.9+)."""
import argparse, json, os, re, subprocess, sys, tempfile

TICKS = 254016000000  # per second
FILLERS = {"um", "umm", "uh", "uhh", "uhm", "erm", "er", "ah", "eh", "hmm", "mm", "mhm"}
HEDGES = ["you know", "i mean", "kind of", "sort of", "just", "actually", "really", "basically", "literally",
          "honestly", "like"]
WEAK = {"a", "an", "the", "and", "or", "but", "to", "of", "in", "on", "at", "for", "with", "my", "your", "our",
        "their", "his", "her", "its", "is", "are", "was", "i", "you", "we", "they", "that", "if", "so"}


def collect(node, out):
    if isinstance(node, dict):
        text = node.get("text", node.get("word"))
        if isinstance(text, str) and isinstance(node.get("start"), (int, float)) and isinstance(node.get("end"), (int, float)):
            out.append(node)
            return
        for key, value in node.items():
            if key != "paragraphs":  # transcript.inspect repeats the words as paragraphs
                collect(value, out)
    elif isinstance(node, list):
        for value in node:
            collect(value, out)


def load_words(path):
    raw = []
    with open(path, encoding="utf-8") as f:
        collect(json.load(f), raw)
    scale = TICKS if raw and max(w["end"] for w in raw) > 1e6 else 1  # ticks are huge, seconds small
    words = [{"text": w.get("text", w.get("word")).strip(), "start": w["start"] / scale, "end": w["end"] / scale,
              "speaker": w.get("speaker")} for w in raw]
    return sorted((w for w in words if w["text"]), key=lambda w: w["start"])


def load(path, track=None):
    """Cues [{id, start, end, text, speaker}] in seconds from captions.list JSON (ticks) or an SRT / VTT."""
    if path.lower().endswith((".srt", ".vtt")):
        return srt(path)
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    doc = doc.get("result", doc) if isinstance(doc, dict) else doc
    tracks = doc.get("tracks", []) if isinstance(doc, dict) else []
    if track is not None:
        tracks = [t for t in tracks if str(t.get("id", t.get("track"))) == str(track)] or tracks
    caps = tracks[0].get("captions", []) if tracks else (doc.get("captions", []) if isinstance(doc, dict) else [])
    cues = [{"id": c["id"], "start": c["start"] / TICKS, "end": c["end"] / TICKS, "text": c.get("text", ""),
             "speaker": c.get("speaker")} for c in caps]
    return sorted(cues, key=lambda c: c["start"])


def srt(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read().replace("\r\n", "\n")
    stamp = r"(\d+):(\d\d):(\d\d)[,.](\d{3})"
    cues = []
    for block in re.split(r"\n\s*\n", text):
        m = re.search(stamp + r"\s*-->\s*" + stamp, block)
        if m:
            g = [int(x) for x in m.groups()]
            body = "\n".join(line.strip() for line in block[m.end():].strip().splitlines())
            cues.append({"id": len(cues) + 1, "start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0,
                         "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0, "text": body, "speaker": None})
    return cues


def to_srt(cues):
    def stamp(t):
        ms = int(round(t * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    return "".join("%d\n%s --> %s\n%s\n\n" % (k + 1, stamp(c["start"]), stamp(c["end"]), c["text"]) for k, c in enumerate(cues))


def chars(text):
    """Characters as a reader (and the bench) counts them: lines joined by one space, tags removed."""
    return len(" ".join(line.strip() for line in re.sub(r"<[^>]+>", "", text).splitlines()))


def cps(c):
    return chars(c["text"]) / max(c["end"] - c["start"], 0.001)


def stats(cues, limit):
    speeds = [cps(c) for c in cues if c["text"].strip()]
    n = len(speeds) or 1
    return {"cues": len(speeds), "atOrUnder": round(100.0 * sum(s <= limit for s in speeds) / n, 1),
            "over25": round(100.0 * sum(s > 25 for s in speeds) / n, 1),
            "medianCps": round(sorted(speeds)[len(speeds) // 2], 1) if speeds else None}


def bare(word):
    return re.sub(r"[^\w']", "", word).lower()


def clean(text):
    """Text without hesitation fillers and stuttered repeats; capitalised again if it was."""
    words = text.split()
    out = []
    for w in words:
        if bare(w) in FILLERS:
            if out and re.search(r"[.?!]$", w) and not re.search(r"[.?!]$", out[-1]):
                out[-1] = out[-1].rstrip(",;:") + w[-1]
            continue
        if out and bare(w) and bare(w) == bare(out[-1]) and not re.search(r"[.?!,;:]$", out[-1]):
            out[-1] = w  # "the the" → "the"
            continue
        out.append(w)
    if not out:
        return text
    if words[0][:1].isupper() and out[0][:1].islower():
        out[0] = out[0][:1].upper() + out[0][1:]
    return " ".join(out)


def trim(text):
    """Text without hedges and discourse markers ("just", "you know", …); content words stay."""
    out = " ".join(text.split())
    for h in HEDGES:
        out = re.sub(r"(?i)(^|\s)" + re.escape(h) + r",?(?=\s|$)", "", out)
    out = " ".join(out.split()).rstrip(",;:")
    if not out:
        return text
    return out[:1].upper() + out[1:] if text[:1].isupper() else out


def wrap(text, max_chars, lines):
    """One line when it fits, else the best two-line split; None when it does not fit."""
    words = text.split()
    one = " ".join(words)
    if len(one) <= max_chars or not words:
        return one
    if lines < 2:
        return None
    best = None
    for k in range(1, len(words)):  # even lines, a break after punctuation, never a line ending on "the"
        a, b = " ".join(words[:k]), " ".join(words[k:])
        score = abs(len(a) - len(b)) - (12 if re.search(r"[,;:.?!]$", a) else 0) + (12 if bare(words[k - 1]) in WEAK else 0)
        if len(a) <= max_chars and len(b) <= max_chars and (best is None or score < best[0]):
            best = (score, a + "\n" + b)
    return best[1] if best else None


def snap(t, fps):
    return round(t * fps) / fps


class Rules:
    def __init__(self, a):
        self.limit, self.fps, self.gap = a.max_cps, a.fps, a.gap_frames / a.fps
        self.lead, self.max_chars, self.lines = a.lead, a.max_chars, a.lines
        self.max_seconds, self.min_seconds, self.end = a.max_seconds, a.min_seconds, a.end
        self.break_gap, self.fill, self.keep_fillers = a.break_gap, a.fill, a.keep_fillers
        self.trim_hedges = a.trim_hedges


def group(words, r):
    """Cues from words, broken at meaning first and at the limits second; no one-word cue inside a sentence."""
    groups, cur = [], []
    capacity = r.max_chars * r.lines

    def text_of(ws):
        return " ".join(w["text"] for w in ws)

    def fits(ws):
        return wrap(text_of(ws), r.max_chars, r.lines) is not None and ws[-1]["end"] - ws[0]["start"] <= r.max_seconds

    for w in words:
        if cur:
            prev = cur[-1]
            sentence = re.search(r"[.?!]$", prev["text"]) and len(cur) >= 2
            phrase = re.search(r"[,;:]$", prev["text"]) and len(text_of(cur)) >= r.fill * capacity
            full = not fits(cur + [w])
            if full or sentence or phrase or w["start"] - prev["end"] >= r.break_gap or w.get("speaker") != prev.get("speaker"):
                if full and not (sentence or phrase) and len(cur) > 2 and bare(prev["text"]) in WEAK:
                    groups.append(cur[:-1])  # never end a cue on "the": it opens the next one
                    cur = [prev] + ([w] if fits([prev, w]) else [])
                    if len(cur) == 1:
                        groups.append(cur)
                        cur = [w]
                    continue
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    k = 1
    while k < len(groups):  # a lone word ending a sentence goes back to its cue, or takes a word from it
        g, p = groups[k], groups[k - 1]
        joined = g[0]["start"] - p[-1]["end"] < r.break_gap and not re.search(r"[.?!]$", p[-1]["text"]) \
            and g[0].get("speaker") == p[-1].get("speaker")
        if len(g) == 1 and joined:
            if fits(p + g):
                groups[k - 1] = p + g
                del groups[k]
                continue
            if len(p) > 2:
                groups[k - 1], groups[k] = p[:-1], p[-1:] + g
        k += 1
    return [{"id": i + 1, "start": g[0]["start"], "end": g[-1]["end"], "text": text_of(g), "speaker": g[0].get("speaker")}
            for i, g in enumerate(groups)]


def fit(cues, r):
    """Clean and wrap the text, hold fast cues into the silence after them, then merge what is still fast."""
    work = [dict(c, ids=[c["id"]], orig=dict(c)) for c in cues]
    for c in work:
        t = wrap(c["text"] if r.keep_fillers else clean(c["text"]), r.max_chars, r.lines)
        if t is not None:
            c["text"] = t

    def hold(i):
        c = work[i]
        need = max(chars(c["text"]) / (0.95 * r.limit), r.min_seconds)
        if c["end"] - c["start"] >= need:
            return
        last = r.end if r.end is not None else c["end"] + 1.0
        nxt = work[i + 1]["start"] - r.gap if i + 1 < len(work) else last
        c["end"] = max(c["end"], snap(min(nxt, c["start"] + need, c["start"] + r.max_seconds), r.fps))
        if c["end"] - c["start"] < need:
            floor = 0.0
            if i > 0:  # the cue before may give back up to --lead of its tail when it still reads in time
                p = work[i - 1]
                p_need = max(chars(p["text"]) / (0.95 * r.limit), r.min_seconds)
                floor = max(p["start"] + p_need, p["orig"]["end"] - r.lead, p["start"] + r.min_seconds)
                floor = min(floor, p["end"]) + r.gap
            start = min(c["start"], snap(max(floor, c["start"] - r.lead, c["end"] - need), r.fps))
            if i > 0 and start < work[i - 1]["end"] + r.gap:
                work[i - 1]["end"] = snap(start - r.gap, r.fps)
            c["start"] = start

    for i in range(len(work)):
        hold(i)
    i = 0
    while i < len(work):
        c, best = work[i], None
        if cps(c) > r.limit:
            for j in (i - 1, i + 1):
                if not 0 <= j < len(work) or work[j].get("speaker") != c.get("speaker"):
                    continue
                a, b = (work[j], c) if j < i else (c, work[j])
                text = wrap(a["text"] + " " + b["text"], r.max_chars, r.lines)
                if text is None or b["end"] - a["start"] > r.max_seconds:
                    continue
                speed = chars(text) / max(b["end"] - a["start"], 0.001)
                if speed <= r.limit and (best is None or speed < best[0]):
                    best = (speed, min(i, j), text)
        if best is None:
            i += 1
            continue
        _, k, text = best
        a, b = work[k], work[k + 1]
        a.update(text=text, end=b["end"], ids=a["ids"] + b["ids"])
        del work[k + 1]
        hold(k)
        i = k
    if r.trim_hedges:
        for k, c in enumerate(work):
            if cps(c) > r.limit:
                t = wrap(trim(c["text"]), r.max_chars, r.lines)
                if t is not None and t != c["text"]:
                    c["text"] = t
                    hold(k)
    return work


def left(work, limit):
    return [{"caption": c["id"], "at": round(c["start"], 2), "cps": round(cps(c), 1), "text": c["text"],
             "needsSeconds": round(chars(c["text"]) / limit, 2), "hasSeconds": round(c["end"] - c["start"], 2)}
            for c in work if cps(c) > limit]


def commands(work):
    out = []
    for c in work:
        o = c["orig"]
        if len(c["ids"]) > 1:
            out.append({"id": "captions.merge", "params": {"captions": c["ids"]}})
        if len(c["ids"]) > 1 or c["text"] != o["text"]:
            out.append({"id": "captions.setText", "params": {"caption": c["id"], "text": c["text"]}})
        if abs(c["start"] - o["start"]) > 1e-6 or abs(c["end"] - o["end"]) > 1e-6:
            out.append({"id": "captions.setTimes", "params": {"caption": c["id"], "startSeconds": round(c["start"], 6),
                                                             "endSeconds": round(c["end"], 6)}})
    return out


def cli_json(cli, project, cid):
    out = subprocess.run([cli, "--project", project, "exec", cid], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def apply(a, r):
    """Group the active sequence of a saved project and replace its first caption track, through the CLI."""
    summary = cli_json(a.cli, a.project, "bashcut.timeline.summary")
    r.fps = float(summary.get("fps") or r.fps)
    if r.end is None:
        r.end = float(summary.get("duration") or 0) or None
    doc = cli_json(a.cli, a.project, "transcript.inspect")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(doc, f)
    words = load_words(f.name)
    os.unlink(f.name)
    if not words:
        return {"error": "no words in the active sequence: transcribe it first"}
    cues = group(words, r)
    work = fit(cues, r)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.project)), "captions",
                                os.path.splitext(os.path.basename(a.project))[0] + ".srt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(to_srt(work))
    steps = []
    if cli_json(a.cli, a.project, "captions.list").get("tracks"):
        steps.append({"id": "captions.deleteTrack", "params": {}})
    steps += [{"id": "captions.import", "params": {"path": os.path.abspath(out), "name": a.name}},
              {"id": "file.save", "params": {}}]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        fh.write("".join(json.dumps(x) + "\n" for x in steps))
    run = subprocess.run([a.cli, "--project", a.project, "run", fh.name], capture_output=True, text=True)
    os.unlink(fh.name)
    failed = [json.loads(l) for l in run.stdout.splitlines() if l.strip() and not json.loads(l).get("ok")]
    result = {"out": out, "before": stats(cues, r.limit), "after": stats(work, r.limit), "left": left(work, r.limit)}
    if run.returncode or failed:
        result["error"] = failed or run.stderr.strip()
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mode", choices=["group", "plan", "report", "apply"])
    ap.add_argument("path", nargs="?", help="group: words JSON; plan, report: captions.list JSON (ticks) or an SRT / VTT")
    ap.add_argument("--cli", default=os.environ.get("BASHCUTPRO_CLI") or "bashcutpro-cli", help="apply: the engine (bashcutpro-cli, bcpro or filmcraft-cli)")
    ap.add_argument("--project", default=os.environ.get("BASHCUT_PROJECT"), help="apply: the saved project")
    ap.add_argument("--name", default="Captions", help="apply: the caption track's name")
    ap.add_argument("--out", help="group, apply: the SRT to write")
    ap.add_argument("--track", help="caption track id (default the first)")
    ap.add_argument("--max-cps", type=float, default=20.0)
    ap.add_argument("--max-chars", type=int, default=42, help="characters a line")
    ap.add_argument("--lines", type=int, default=2)
    ap.add_argument("--max-seconds", type=float, default=7.0, help="longest cue")
    ap.add_argument("--min-seconds", type=float, default=0.7, help="shortest cue, when the silence allows")
    ap.add_argument("--break-gap", type=float, default=0.5, help="group: a pause this long starts a cue")
    ap.add_argument("--fill", type=float, default=0.5, help="group: break at a comma once the cue is this full")
    ap.add_argument("--fps", type=float, default=30.0, help="sequence frame rate (times are snapped to frames)")
    ap.add_argument("--gap-frames", type=int, default=2, help="frames left between cues")
    ap.add_argument("--lead", type=float, default=0.15, help="seconds a cue may start before its first word")
    ap.add_argument("--end", type=float, help="sequence length in seconds (the last cue holds at most to it)")
    ap.add_argument("--keep-fillers", action="store_true", help="keep um, uh, … and repeats in the text")
    ap.add_argument("--trim-hedges", action="store_true",
                    help="drop hedges (just, actually, you know, …) from cues still over the limit")
    ap.add_argument("--jsonl", action="store_true", help="plan: print only the commands, one per line")
    a = ap.parse_args(argv)
    r = Rules(a)
    if a.mode == "apply":
        if not a.project:
            ap.error("apply needs --project (or BASHCUT_PROJECT)")
        result = apply(a, r)
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 1 if "error" in result else 0
    if not a.path:
        ap.error("%s needs a path" % a.mode)
    if a.mode == "report":
        cues = load(a.path, a.track)
        out = stats(cues, a.max_cps)
        out["worst"] = [{"caption": c["id"], "at": round(c["start"], 2), "cps": round(cps(c), 1), "text": c["text"]}
                        for c in sorted(cues, key=cps, reverse=True)[:5] if cps(c) > a.max_cps]
        out["longLines"] = [c["id"] for c in cues if any(len(l) > a.max_chars for l in c["text"].splitlines())]
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0
    if a.mode == "group":
        if not a.out:
            ap.error("group needs --out cues.srt")
        cues = group(load_words(a.path), r)
        work = fit(cues, r)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(to_srt(work))
        print(json.dumps({"out": a.out, "before": stats(cues, a.max_cps), "after": stats(work, a.max_cps),
                          "left": left(work, a.max_cps)}, ensure_ascii=False, indent=1))
        return 0
    cues = load(a.path, a.track)
    work = fit(cues, r)
    cmds = commands(work)
    if a.jsonl:
        for c in cmds:
            print(json.dumps(c, ensure_ascii=False))
    else:
        print(json.dumps({"commands": cmds, "before": stats(cues, a.max_cps), "after": stats(work, a.max_cps),
                          "left": left(work, a.max_cps)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
