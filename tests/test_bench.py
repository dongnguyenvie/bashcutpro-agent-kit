"""bench/score.py: measurements to scores, the winner rule, the scorecard, plan and blind labels."""

import importlib.util
import json
import os
import random
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("bench_score", os.path.join(ROOT, "bench", "score.py"))
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

SRT = """1
00:00:00,000 --> 00:00:02,000
Short line.

2
00:00:02,000 --> 00:00:03,000
This caption is far too long for one second
"""


def metrics(lufs=-14.2, peak=-1.5, findings=(), seconds=50.0, cuts=(1.0, 2.5), black=0):
    return {"output": "out.mp4", "seconds": seconds, "loudness": {"integratedLufs": lufs, "truePeakDbtp": peak},
            "review": {"findings": [{"severity": s} for s in findings]}, "captions": "out.srt",
            "safeArea": {"outside": 0, "checked": 2}, "cuts": list(cuts), "words": [[0.0, 0.9], [2.0, 3.0]],
            "picture": {"blackFrames": black, "frozenSeconds": 0.0}, "renderSeconds": 30.0}


class BenchTests(unittest.TestCase):
    def setUp(self):
        self.runs = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.runs)
        self.jobs = score.load_json(os.path.join(ROOT, "bench", "jobs.json"))
        self.job = self.jobs["jobs"][0]

    def put(self, side, job, value):
        folder = os.path.join(self.runs, side, job)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "metrics.json"), "w") as f:
            json.dump(value, f)
        with open(os.path.join(folder, "out.srt"), "w") as f:
            f.write(SRT)

    def test_jobs_cover_the_six_cases(self):
        self.assertEqual(len(self.jobs["jobs"]), 6)
        for job in self.jobs["jobs"]:
            self.assertTrue(job["inputs"] and job["brief"] and job["skills"] and job["profile"])
            for skill in job["skills"]:
                self.assertTrue(os.path.isfile(os.path.join(ROOT, "skills", skill, "SKILL.md")), skill)

    def test_measurements(self):
        path = os.path.join(self.runs, "a.srt")
        with open(path, "w") as f:
            f.write(SRT)
        speeds = score.reading_speeds(score.srt_cues(path))
        self.assertEqual(len(speeds), 2)
        self.assertLess(speeds[0], 20)
        self.assertGreater(speeds[1], 25)
        self.assertEqual(score.cut_on_word_rate([1.0, 2.5], [[0.0, 0.9], [2.0, 3.0]]), 0.5)
        self.assertEqual(score.cut_on_word_rate([0.9], [[0.0, 0.9]]), 1.0)  # on the edge is fine

    def test_scores_and_missing_measurements(self):
        out = score.score_output(metrics(lufs=-17.0, peak=-0.2, findings=("blocker", "minor")), self.job["target"], self.runs)
        self.assertEqual(out["parts"]["sound"]["score"], 30.0)  # 2 LU beyond the band (-40), peak over (-30)
        self.assertEqual(out["parts"]["review"]["score"], 72.0)
        self.assertEqual(out["parts"]["length"]["score"], 100.0)
        bare = score.score_output({"seconds": 50.0}, self.job["target"], self.runs)
        self.assertEqual(bare["parts"]["sound"]["note"], "not measured")
        self.assertEqual(bare["parts"]["captions"]["note"], "captions missing")  # expected but absent: a real 0
        self.assertAlmostEqual(bare["total"], 100.0 / 3)  # length 100 (weight 10), captions 0 (20); the rest left out

    def test_engine_review_severities(self):
        value, note = score.score_review({"review": {"findings": [{"severity": "blocking"}, {"severity": "warning"},
                                                                  {"severity": "info"}]}})
        self.assertEqual(value, 100 - 25 - 3)
        self.assertEqual(note, "1 blocker, 1 minor, 1 polish")

    def test_winner_and_scorecard(self):
        self.put("pro", self.job["id"], metrics(cuts=(0.9, 2.0)))
        self.put("bashcut", self.job["id"], metrics(lufs=-18.0, findings=("blocker",), black=2))
        rows = score.score(self.runs, self.jobs)
        self.assertEqual(rows[0]["winner"], "pro")
        self.assertEqual(rows[1]["winner"], "pending")
        with open(os.path.join(ROOT, "bench", "scorecard-template.md")) as f:
            text = score.render(rows, "2026-10-20", f.read())
        self.assertIn("# Quality bench: Pro vs BashCut, 2026-10-20", text)
        self.assertIn("5 of 6 jobs not run yet.", text)
        self.assertNotIn("{{", text)
        self.put("bashcut", self.job["id"], metrics(cuts=(0.9, 2.0), lufs=-14.0))
        self.put("pro", self.job["id"], metrics(lufs=-20.0, findings=("blocker", "blocker")))
        rows = score.score(self.runs, self.jobs)
        self.assertEqual(rows[0]["winner"], "bashcut")
        with open(os.path.join(ROOT, "bench", "scorecard-template.md")) as f:
            self.assertIn("open a follow-up issue", score.render(rows, "d", f.read()))

    def test_several_outputs_are_averaged(self):
        podcast = next(j for j in self.jobs["jobs"] if j["id"] == "podcast-3-clips")
        self.put("pro", podcast["id"], [metrics(seconds=40.0), metrics(seconds=40.0, findings=("blocker",))])
        side = score.score_side(self.runs, "pro", podcast)
        self.assertEqual(len(side["outputs"]), 2)
        self.assertAlmostEqual(side["total"], sum(o["total"] for o in side["outputs"]) / 2)

    def test_plan_and_blind(self):
        raw = os.path.join(self.runs, "raw")
        os.makedirs(os.path.join(raw, "talking-head"))
        open(os.path.join(raw, "talking-head", "take1.mp4"), "w").close()
        plan = {p["job"]: p for p in score.plan(raw, self.jobs)}
        self.assertEqual(plan["talking-head-short"]["files"], ["talking-head/take1.mp4"])
        self.assertTrue(plan["vlog-60s"]["missing"])
        sheet, key = score.blind(self.runs, self.jobs, os.path.join(self.runs, "blind"), random.Random(1))
        self.assertEqual(len(sheet), 6)
        for job, sides in key.items():
            self.assertEqual(sorted(sides.values()), ["bashcut", "pro"])
        self.assertNotIn("pro", json.dumps([s["pick"] for s in sheet]))


if __name__ == "__main__":
    unittest.main()
