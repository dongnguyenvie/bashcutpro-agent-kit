#!/usr/bin/env python3
"""Turn an outside transcriber's word timings into `transcript.set` params, for builds without Whisper.

  words_to_transcript.py whisper.json --item ITEM [--language vi] [--offset S] > params.json

Reads Whisper-style JSON with word timestamps (openai-whisper, mlx_whisper, faster-whisper:
{"language", "segments": [{"words": [{"word", "start", "end", "probability"}]}]}) or a plain {"words": [...]}
list; `speaker` on a word or segment is kept. Seconds become ticks from the media item's start (--offset: where
the transcribed audio began in the file). Prints {"item", "transcript"} for command_run transcript.set; suspect
words (longer than --long seconds or under --low probability: often a merged restart) go to stderr as JSON lines,
because transcript.set keeps no confidence. Standard library only."""
import argparse, json, sys

TICKS = 254016000000  # per second


def words_of(doc):
    if isinstance(doc, list):
        return doc
    if doc.get("words"):
        return doc["words"]
    out = []
    for seg in doc.get("segments", []):
        for w in seg.get("words", []):
            out.append(dict(w, speaker=w.get("speaker", seg.get("speaker"))))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json")
    ap.add_argument("--item", required=True, help="the media item id the words belong to")
    ap.add_argument("--language", help="default: the file's language, else 'auto'")
    ap.add_argument("--offset", type=float, default=0.0, help="seconds into the media where the audio began")
    ap.add_argument("--long", type=float, default=1.0, help="suspect: a word longer than this, seconds")
    ap.add_argument("--low", type=float, default=0.4, help="suspect: probability under this")
    o = ap.parse_args(argv)
    with open(o.json, encoding="utf-8") as fh:
        doc = json.load(fh)
    speakers, words = [], []
    for w in words_of(doc):
        text = (w.get("word") or w.get("text") or "").strip()
        if not text or w.get("start") is None or w.get("end") is None:
            continue
        start, end = float(w["start"]) + o.offset, float(w["end"]) + o.offset
        word = {"text": text, "start": round(start * TICKS), "end": round(max(end, start) * TICKS)}
        spk = w.get("speaker")
        if spk is not None:
            name = str(spk)
            if name not in speakers:
                speakers.append(name)
            word["speaker"] = speakers.index(name)
        words.append(word)
        prob = w.get("probability", w.get("confidence"))
        if end - start > o.long or (prob is not None and prob < o.low):
            print(json.dumps({"suspect": text, "start": round(start, 2), "end": round(end, 2), "probability": prob},
                             ensure_ascii=False), file=sys.stderr)
    language = o.language or (doc.get("language") if isinstance(doc, dict) else None) or "auto"
    transcript = {"language": language, "speakers": [{"name": s} for s in speakers] or [{"name": "Speaker 1"}],
                  "words": words}
    print(json.dumps({"item": o.item, "transcript": transcript}, ensure_ascii=False))


if __name__ == "__main__":
    main()
