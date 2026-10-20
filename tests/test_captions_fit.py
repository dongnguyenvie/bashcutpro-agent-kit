"""skills/captions-text/captions_fit.py: grouping words into readable cues, fixing a fast track, the report."""

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("captions_fit", os.path.join(ROOT, "skills", "captions-text", "captions_fit.py"))
fit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)
T = fit.TICKS


def words(spec):
    """'text start end' per word, seconds."""
    out = []
    for line in spec.strip().splitlines():
        text, start, end = line.split()
        out.append({"text": text, "start": float(start), "end": float(end)})
    return out


SPEECH = words("""
So, 0.00 0.37
here 0.54 0.66
is 0.66 0.80
the 0.80 0.90
thing 0.90 1.04
about 1.04 1.24
editing 1.24 1.50
podcasts. 1.50 2.35
Um, 2.52 2.78
most 2.93 3.12
people 3.12 3.38
cut 3.38 3.58
the 3.58 3.70
the 3.70 3.76
clip 3.76 3.96
short. 3.96 4.30
""")


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fit.main(argv)
    return buf.getvalue()


class TextTests(unittest.TestCase):
    def test_fillers_and_stutters_go_meaning_stays(self):
        self.assertEqual(fit.clean("Um, most people cut the the clip short."), "Most people cut the clip short.")
        self.assertEqual(fit.clean("I mean it, uh."), "I mean it.")
        self.assertEqual(fit.clean("um"), "um")  # a cue of only a filler is left for the editor to delete

    def test_wrap_prefers_punctuation_and_never_ends_on_the(self):
        self.assertEqual(fit.wrap("then you trim the fillers, keep the breaths,", 32, 2),
                         "then you trim the fillers,\nkeep the breaths,")
        self.assertIsNone(fit.wrap("a line far too long to fit on one line of twenty", 20, 1))

    def test_trim_drops_hedges_only(self):
        self.assertEqual(fit.trim("You just need to be ruthless, you know"), "You need to be ruthless")


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.r = fit.Rules(fit.main.__globals__["argparse"].Namespace(
            max_cps=20.0, fps=30.0, gap_frames=2, lead=0.15, max_chars=32, lines=2, max_seconds=7.0,
            min_seconds=0.7, end=5.0, break_gap=0.5, fill=0.5, keep_fillers=False, trim_hedges=False))

    def test_breaks_at_sentence_ends_and_reads_under_the_limit(self):
        cues = fit.group(SPEECH, self.r)
        self.assertEqual([c["text"] for c in cues],
                         ["So, here is the thing about editing podcasts.", "Um, most people cut the the clip short."])
        work = fit.fit(cues, self.r)
        self.assertEqual(work[1]["text"], "Most people cut the clip short.")
        for c in work:
            self.assertLessEqual(fit.cps(c), 20.0)
        self.assertLessEqual(work[0]["end"] + 2 / 30.0, work[1]["start"] + 1e-6)  # no overlap, a 2-frame gap
        self.assertLessEqual(work[1]["end"], 5.0)

    def test_no_lone_word_inside_a_sentence(self):
        ws = words("""
alpha 0.0 0.3
beta 0.3 0.6
gamma 0.6 0.9
delta 0.9 1.2
eps. 1.2 1.5
""")
        self.r.max_chars, self.r.lines = 17, 1
        cues = fit.group(ws, self.r)
        self.assertTrue(all(len(c["text"].split()) > 1 for c in cues), cues)


class CommandLineTests(unittest.TestCase):
    def test_group_writes_srt_and_report_reads_it(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "words.json")
            with open(src, "w") as f:
                json.dump({"words": [dict(w, start=int(w["start"] * T), end=int(w["end"] * T)) for w in SPEECH],
                           "paragraphs": [{"text": "ignored", "start": 0, "end": T}]}, f)
            out = json.loads(run(["group", src, "--out", os.path.join(d, "c.srt"), "--end", "5"]))
            self.assertEqual(out["after"]["atOrUnder"], 100.0)
            self.assertEqual(out["left"], [])
            rep = json.loads(run(["report", os.path.join(d, "c.srt")]))
            self.assertEqual(rep["cues"], 2)
            self.assertEqual(rep["over25"], 0.0)

    def test_plan_on_a_fast_track_gives_batch_commands(self):
        caps = {"tracks": [{"id": 12, "captions": [
            {"id": 13, "start": 0, "end": int(0.6 * T), "text": "So here is the thing about", "speaker": None},
            {"id": 14, "start": int(1.6 * T), "end": int(2.4 * T), "text": "editing", "speaker": None},
            {"id": 15, "start": int(2.4 * T), "end": int(4.0 * T), "text": "podcasts.", "speaker": None},
        ]}]}
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "caps.json")
            with open(src, "w") as f:
                json.dump(caps, f)
            out = json.loads(run(["plan", src, "--end", "4"]))
        self.assertEqual(out["before"]["atOrUnder"], 66.7)
        self.assertEqual(out["after"]["atOrUnder"], 100.0)
        ids = [c["id"] for c in out["commands"]]
        self.assertIn("captions.setTimes", ids)
        hold = next(c for c in out["commands"] if c["id"] == "captions.setTimes" and c["params"]["caption"] == 13)
        self.assertLessEqual(hold["params"]["endSeconds"], 1.6 - 2 / 30.0 + 1e-6)  # into the silence, not over 14


if __name__ == "__main__":
    unittest.main()
