#!/usr/bin/env python3
"""Speaking rate, narration windows and take checks from word timings, read-only. BashCutPro has no `speech rate`,
`narration windows` or `voice check`: read the words with `transcript.inspect` (or an outside transcriber's
Whisper JSON) and measure them here.

  narration.py rate words.json [--lang vi] [--speaker 0]          # units/s: overall, articulation, p10/p50/p90
  narration.py windows words.json --rate 4.2 --min-seconds 1.5     # speech-free windows with a unit budget each
  narration.py check take.json --text "Line as written"            # a take's words against its line

Words are any JSON holding {"text" or "word", "start", "end"} objects: `transcript.inspect` output (times in ticks,
254 016 000 000 a second, detected), `transcript.set` params, or Whisper JSON (seconds). --offset S adds S seconds
to every time (words on a media item's clock → the sequence's). Units: syllables for Vietnamese (one written word
each), characters for Chinese, Japanese and Korean, else words. Prints one JSON object. Standard library only
(Python 3.9+)."""
import argparse, difflib, json, re, sys, unicodedata

TICKS = 254016000000  # per second
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")


def collect(node, out):
    if isinstance(node, dict):
        text = node.get("text", node.get("word"))
        if isinstance(text, str) and isinstance(node.get("start"), (int, float)) and isinstance(node.get("end"), (int, float)):
            out.append(node)
            return
        for value in node.values():
            collect(value, out)
    elif isinstance(node, list):
        for value in node:
            collect(value, out)


def language_of(doc):
    if isinstance(doc, dict):
        for key in ("language", "lang"):
            if isinstance(doc.get(key), str):
                return doc[key]
        for value in doc.values():
            found = language_of(value)
            if found:
                return found
    elif isinstance(doc, list):
        for value in doc:
            found = language_of(value)
            if found:
                return found
    return None


def load(path, offset, speaker=None):
    doc = json.load(open(path, encoding="utf-8"))
    raw = []
    collect(doc, raw)
    # Ticks are huge: a word ending after one second is 2.5e11 ticks; Whisper seconds stay small.
    scale = TICKS if raw and max(w["end"] for w in raw) > 1e6 else 1
    words = []
    for w in raw:
        if speaker is not None and w.get("speaker") != speaker:
            continue
        text = (w.get("text") if isinstance(w.get("text"), str) else w.get("word")).strip()
        if text:
            words.append({"text": text, "start": w["start"] / scale + offset, "end": w["end"] / scale + offset})
    words.sort(key=lambda w: w["start"])
    return words, language_of(doc)


def units(text, lang):
    if lang[:2] in ("zh", "ja", "ko") or CJK.search(text):
        return len(CJK.findall(text)) or len(tokens(text))
    return len(tokens(text))


def tokens(text):
    text = unicodedata.normalize("NFC", text).lower()
    return [t for t in re.split(r"[^\w']+", text) if t]


def phrases(words, gap):
    runs, run = [], []
    for w in words:
        if run and w["start"] - run[-1]["end"] >= gap:
            runs.append(run)
            run = []
        run.append(w)
    if run:
        runs.append(run)
    return runs


def pct(values, p):
    if not values:
        return None
    values = sorted(values)
    i = (len(values) - 1) * p
    lo, hi = int(i), min(int(i) + 1, len(values) - 1)
    return round(values[lo] + (values[hi] - values[lo]) * (i - lo), 2)


def cmd_rate(a):
    words, lang = load(a.words, a.offset, a.speaker)
    lang = a.lang or lang or "en"
    if not words:
        return {"error": "no words"}
    runs = phrases(words, a.phrase_gap)
    total = sum(units(w["text"], lang) for w in words)
    spoken = sum(r[-1]["end"] - r[0]["start"] for r in runs)
    voiced = sum(w["end"] - w["start"] for w in words)
    per = [units(" ".join(w["text"] for w in r), lang) / (r[-1]["end"] - r[0]["start"])
           for r in runs if units(" ".join(w["text"] for w in r), lang) >= 4 and r[-1]["end"] > r[0]["start"]]
    return {"lang": lang, "unit": unit_name(lang), "units": total, "words": len(words), "phrases": len(runs),
            "overall": round(total / spoken, 2) if spoken else None,
            "articulation": round(total / voiced, 2) if voiced else None,
            "p10": pct(per, 0.1), "p50": pct(per, 0.5), "p90": pct(per, 0.9),
            "speechSeconds": round(spoken, 2), "span": [round(words[0]["start"], 2), round(words[-1]["end"], 2)]}


def unit_name(lang):
    return "syllables" if lang[:2] == "vi" else "characters" if lang[:2] in ("zh", "ja", "ko") else "words"


def context(words, start, end):
    return " ".join(w["text"] for w in words if start <= w["start"] < end)


def cmd_windows(a):
    words, _ = load(a.words, a.offset)
    lo = a.start if a.start is not None else 0.0
    hi = a.end if a.end is not None else (words[-1]["end"] if words else 0.0)
    inside = [w for w in words if w["end"] > lo and w["start"] < hi]
    edges = [lo] + [x for w in inside for x in (w["start"], w["end"])] + [hi]
    out = []
    for i in range(0, len(edges) - 1, 2):
        gap_start, gap_end = edges[i], edges[i + 1]
        start, end = gap_start + (a.margin if i else 0), gap_end - (a.margin if i + 2 < len(edges) else 0)
        seconds = end - start
        if seconds >= a.min_seconds:
            out.append({"start": round(start, 2), "end": round(end, 2), "seconds": round(seconds, 2),
                        "budget": int(seconds * a.rate),
                        "before": context(words, gap_start - a.context, gap_start),
                        "after": context(words, gap_end, gap_end + a.context)})
    return {"rate": a.rate, "margin": a.margin, "range": [round(lo, 2), round(hi, 2)], "windows": out}


def cmd_check(a):
    words, lang = load(a.take, a.offset)
    lang = a.lang or lang or "en"
    want, heard = tokens(a.text), tokens(" ".join(w["text"] for w in words))
    match = difflib.SequenceMatcher(None, want, heard, autojunk=False)
    unmatched, extra = [], []
    for op, i1, i2, j1, j2 in match.get_opcodes():
        if op in ("replace", "delete"):
            unmatched += [{"word": t, "index": i} for i, t in enumerate(want[i1:i2], i1)]
        if op in ("replace", "insert"):
            extra += [{"word": t, "index": j} for j, t in enumerate(heard[j1:j2], j1)]
    seconds = words[-1]["end"] - words[0]["start"] if words else 0.0
    result = {"similarity": round(match.ratio(), 3), "unmatched": unmatched, "extra": extra,
              "atStart": any(u["index"] < 3 for u in unmatched) or any(e["index"] < 3 for e in extra),
              "heard": " ".join(heard), "seconds": round(seconds, 2),
              "unitsPerSecond": round(units(a.text, lang) / seconds, 2) if seconds else None}
    if a.min_similarity is not None:
        result["pass"] = result["similarity"] >= a.min_similarity and not unmatched
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rate", help="speaking rate of the words")
    r.add_argument("words")
    r.add_argument("--speaker", type=int, help="only this speaker index")
    r.add_argument("--phrase-gap", type=float, default=0.5, help="a gap this long (s) ends a phrase (0.5)")
    w = sub.add_parser("windows", help="speech-free windows with a unit budget")
    w.add_argument("words")
    w.add_argument("--rate", type=float, required=True, help="units a second the voice speaks (measured)")
    w.add_argument("--min-seconds", type=float, default=1.5)
    w.add_argument("--margin", type=float, default=0.3, help="gap kept from real speech on each side (0.3 s)")
    w.add_argument("--from", dest="start", type=float)
    w.add_argument("--to", dest="end", type=float)
    w.add_argument("--context", type=float, default=5.0, help="seconds of speech quoted each side (5)")
    c = sub.add_parser("check", help="a take's words against its line")
    c.add_argument("take", help="the take's words (transcript.inspect after transcript.generate, or Whisper JSON)")
    c.add_argument("--text", required=True, help="the line as written for the voice")
    c.add_argument("--min-similarity", type=float)
    for s in (r, w, c):
        s.add_argument("--offset", type=float, default=0.0, help="seconds added to every time")
    for s in (r, c):
        s.add_argument("--lang", help="language code; default: the file's, else en")
    a = p.parse_args()
    result = {"rate": cmd_rate, "windows": cmd_windows, "check": cmd_check}[a.cmd](a)
    json.dump(result, sys.stdout, ensure_ascii=False)
    print()
    return 1 if "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())
