"""skills/outcomes/outcomes.py with fixture retention exports (YouTube percent positions, TikTok seconds)."""

import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures", "outcomes")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


outcomes = module("outcomes", os.path.join(ROOT, "skills", "outcomes", "outcomes.py"))
knowledge = module("knowledge", os.path.join(ROOT, "skills", "self-learn", "knowledge.py"))


class OutcomesTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.edit = outcomes.edit_of(outcomes.load(os.path.join(FIX, "sequence-summary.json")))

    def found(self, name):
        return outcomes.analyse(outcomes.read_curve(os.path.join(FIX, name), self.edit["duration"]), self.edit)

    def test_youtube_percent_positions(self):
        found = self.found("youtube-retention.csv")
        self.assertEqual(found["hook"]["at3s"], 70.0)
        self.assertEqual(len(found["drops"]), 1)  # the hook's fall is not a drop
        drop = found["drops"][0]
        self.assertEqual((drop["cut"], drop["cutTo"], drop["section"]), (10.0, ["screen-demo.mp4"], "demo"))
        self.assertLess(drop["points"], -9)
        self.assertEqual(len(found["rewatches"]), 1)
        self.assertAlmostEqual(found["rewatches"][0]["time"], 15.5, delta=0.6)

    def test_tiktok_fractions_in_seconds(self):
        found = self.found("tiktok-retention.csv")
        self.assertEqual([d["cut"] for d in found["drops"]], [10.0])
        self.assertEqual(found["hook"]["at3s"], 70.0)

    def test_relative_retention_is_not_used(self):
        curve = outcomes.read_curve(os.path.join(FIX, "youtube-retention.csv"), 20.0)
        self.assertEqual(curve[0], (0.0, 100.0))  # the absolute column, not the flat relative one

    def test_percent_positions_need_a_length(self):
        with self.assertRaises(ValueError):
            outcomes.read_curve(os.path.join(FIX, "youtube-retention.csv"), None)

    def test_inspect_ticks_are_read(self):
        edit = outcomes.edit_of(outcomes.load(os.path.join(ROOT, "tests", "fixtures", "variants", "a-inspect.json")))
        self.assertEqual(edit["cuts"], [6.0, 10.0])
        self.assertEqual(edit["duration"], 20.0)

    def test_markers_batch(self):
        batch = outcomes.marker_batch(self.found("youtube-retention.csv"))
        names = [c["params"]["name"] for c in batch["commands"]]
        self.assertTrue(names[0].startswith("drop"))
        self.assertEqual({c["id"] for c in batch["commands"]}, {"markers.add"})
        self.assertEqual(batch["commands"][0]["params"]["color"], "Red")
        self.assertIn("screen-demo.mp4", batch["commands"][0]["params"]["comment"])

    def test_drop_at_a_known_cut_becomes_a_lesson(self):
        store = knowledge.Store(os.path.join(self.dir, "knowledge"))
        found = self.found("youtube-retention.csv")
        project = os.path.join(self.dir, "film.fcproj")
        first = outcomes.learn(found, "launch-v1", project, store)
        self.assertEqual(len(first), 1)
        lesson = store.find_lessons(tag="outcomes", status="proposed")[0]
        self.assertIn("screen-demo.mp4", lesson["title"])
        self.assertIn("0:10.0", lesson["evidence"][0])
        outcomes.learn(found, "launch-v2", project, store)  # the same cut again: seen, not a second lesson
        rows = store.find_lessons(tag="outcomes", status="proposed")
        self.assertEqual((len(rows), rows[0]["occurrences"]), (1, 2))

    def test_cli_writes_the_sidecar_and_markers(self):
        project = os.path.join(self.dir, "film.fcproj")
        markers = os.path.join(self.dir, "markers.json")
        out = io.StringIO()
        with redirect_stdout(out):
            code = outcomes.main([os.path.join(FIX, "youtube-retention.csv"), "--sequence", os.path.join(FIX, "sequence-summary.json"),
                                  "--project", project, "--video", "launch v1", "--markers-out", markers])
        self.assertEqual(code, 0)
        result = json.loads(out.getvalue())
        self.assertTrue(result["sidecar"].endswith(os.path.join("film.fcproj.bashcut", "outcomes", "launch-v1.json")))
        self.assertTrue(os.path.isfile(result["sidecar"]))
        with open(markers) as f:
            self.assertTrue(json.load(f)["commands"])

    def test_bad_csv_is_an_error_not_a_crash(self):
        bad = os.path.join(self.dir, "bad.csv")
        with open(bad, "w") as f:
            f.write("a,b\n1,2\n")
        out = io.StringIO()
        with redirect_stdout(out):
            code = outcomes.main([bad, "--sequence", os.path.join(FIX, "sequence-summary.json")])
        self.assertEqual(code, 2)
        self.assertIn("error", json.loads(out.getvalue()))


if __name__ == "__main__":
    unittest.main()
