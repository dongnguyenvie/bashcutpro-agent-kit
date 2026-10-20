"""rough-cut/tighten.py: fillers, false starts, pause cuts and edges that never land inside a kept word."""

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("tighten", os.path.join(ROOT, "skills", "rough-cut", "tighten.py"))
tighten = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tighten)
TPS = tighten.TPS


def words(*spec):
    """(text, start, end) in seconds to transcript.inspect words in ticks."""
    return {"words": [{"i": n, "text": t, "start": round(a * TPS), "end": round(b * TPS)} for n, (t, a, b) in enumerate(spec)]}


def run(data, keep, *extra):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(data, f)
    try:
        out = io.StringIO()
        with redirect_stdout(out):
            tighten.main(["--words", f.name, "--item", "7", "--keep", keep, "--fps", "30", *extra])
        return json.loads(out.getvalue())
    finally:
        os.unlink(f.name)


def clips(result):
    """(source in, source out) seconds of each placed clip and the timeline frames."""
    out, frames = [], []
    for step in result["command"]["params"]["commands"]:
        p = step["params"]
        out.append((p["sourceIn"] / TPS, (p["sourceIn"] + p["duration"]) / TPS))
        frames.append(p["frame"])
    return out, frames


SPEECH = words(("So", 0.5, 0.7), ("um,", 0.7, 1.1), ("I", 1.1, 1.2), ("went", 1.2, 1.5), ("home.", 1.5, 1.9),
               ("Then", 3.0, 3.2), ("the", 3.2, 3.3), ("the", 3.3, 3.4), ("dog", 3.4, 3.8), ("barked.", 3.8, 4.3))


class TightenTests(unittest.TestCase):
    def test_drops_fillers_repeats_and_long_pauses(self):
        r = run(SPEECH, "0-9")
        rep = r["report"]
        self.assertEqual([x["text"] for x in rep["removed"]["fillers"]], ["um,"])
        self.assertEqual([x["i"] for x in rep["removed"]["repeats"]], [6])
        self.assertEqual(rep["removed"]["pauses"], 1)
        self.assertEqual(rep["cuts"], 3)
        self.assertEqual(r["command"]["id"], "bashcut.batch")
        self.assertTrue(all(s["id"] == "timeline.place" and s["params"]["item"] == 7 for s in r["command"]["params"]["commands"]))

    def test_edges_stay_out_of_kept_and_neighbouring_words(self):
        data = SPEECH["words"]
        r = run(SPEECH, "0-9")
        kept = [w for w in data if w["i"] not in (1, 6)]
        for a, b in clips(r)[0]:
            for w in data:
                s, e = w["start"] / TPS, w["end"] / TPS
                self.assertFalse(s + 1e-3 < a < e - 1e-3, f"in point {a:.3f} inside {w['text']}")
                self.assertFalse(s + 1e-3 < b < e - 1e-3, f"out point {b:.3f} inside {w['text']}")
        covered = clips(r)[0]
        for w in kept:
            s, e = w["start"] / TPS, w["end"] / TPS
            self.assertTrue(any(a <= s + 1e-3 and e - 1e-3 <= b for a, b in covered), f"{w['text']} not kept whole")

    def test_clips_are_whole_frames_and_butt_on_the_timeline(self):
        r = run(SPEECH, "0-9")
        steps = r["command"]["params"]["commands"]
        pos = 0
        for s in steps:
            self.assertEqual(s["params"]["frame"], pos)
            n = s["params"]["duration"] * 30 / TPS
            self.assertAlmostEqual(n, round(n), places=6)
            pos += round(n)
        self.assertAlmostEqual(r["report"]["seconds"], pos / 30, places=2)

    def test_story_order_puts_the_hook_first(self):
        r = run(SPEECH, "5-9,0-4")
        (first, _), *_ = clips(r)[0]
        self.assertGreater(first, 2.5)

    def test_sentence_end_repeat_is_kept(self):
        data = words(("One", 0.0, 0.2), ("line.", 0.2, 0.5), ("One", 0.6, 0.8), ("line.", 0.8, 1.1))
        self.assertEqual(run(data, "0-3")["report"]["removed"]["repeats"], [])

    def test_protect_keeps_a_filler(self):
        r = run(SPEECH, "0-9", "--protect", "1")
        self.assertEqual(r["report"]["removed"]["fillers"], [])

    def test_bad_range_exits(self):
        with self.assertRaises(SystemExit):
            run(SPEECH, "0-40")


if __name__ == "__main__":
    unittest.main()
