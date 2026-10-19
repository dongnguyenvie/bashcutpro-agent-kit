"""skills/variants/diff.py on two fixture versions: a sequence_inspect (ticks) and a timeline summary (seconds)."""

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures", "variants")
spec = importlib.util.spec_from_file_location("variants_diff", os.path.join(ROOT, "skills", "variants", "diff.py"))
diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diff)


def fixture(name):
    return diff.load(os.path.join(FIX, name))


class DiffTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b = fixture("a-inspect.json"), fixture("b-summary.json")

    def test_hook_cut_music_and_look_changes(self):
        d = diff.diff(self.a, self.b, fixture("a-review.json"), fixture("b-review.json"))
        self.assertEqual(d["duration"], {"a": 20.0, "b": 18.0, "change": -2.0})
        self.assertEqual(d["cuts"]["removed"], [6.0, 10.0])
        self.assertEqual(d["cuts"]["added"], [2.0, 8.0])
        self.assertEqual(d["clips"], {"removed": [], "added": []})  # same shots, moved
        self.assertEqual(d["hook"]["a"], ["talk.mp4"])
        self.assertEqual(d["hook"]["b"], ["broll-city.mp4", "talk.mp4"])
        self.assertEqual(d["music"], {"removed": ["bed-calm.wav"], "added": ["bed-upbeat.wav"]})
        self.assertEqual(d["looks"], {"lut": {"a": 0, "b": 1}})
        self.assertEqual(d["review"]["scores"]["sound"], {"a": 80, "b": 85})
        self.assertEqual(d["review"]["blocking"], {"a": 1, "b": 0})
        self.assertEqual(d["changed"], ["cut", "hook", "music", "look"])

    def test_same_sequence_has_no_change(self):
        d = diff.diff(self.a, self.a)
        self.assertEqual(d["changed"], [])
        self.assertNotIn("hook", d)

    def test_one_change_rule(self):
        b = json.loads(json.dumps(self.a))
        b["audio"][1]["items"][0]["item"] = 999
        b["audio"][1]["items"][0]["name"] = "bed-other.wav"
        self.assertEqual(diff.diff(self.a, b)["changed"], ["music"])
        out = io.StringIO()
        with redirect_stdout(out):
            code = diff.main([os.path.join(FIX, "a-inspect.json"), os.path.join(FIX, "b-summary.json"), "--one-change", "--text"])
        self.assertEqual(code, 1)
        self.assertIn("changed: cut, hook, music, look", out.getvalue())

    def test_a_cut_within_one_frame_is_the_same_cut(self):
        b = json.loads(json.dumps(self.a))
        nudge = diff.TPS // 60  # half a frame at 30 fps
        b["video"][0]["items"][0]["end"] += nudge
        b["video"][0]["items"][1]["start"] += nudge
        self.assertEqual(diff.diff(self.a, b)["cuts"]["added"], [])

    def test_mcp_tool_result_wrapper_is_read(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"content": [{"type": "text", "text": json.dumps(self.a)}]}, f)
        self.addCleanup(os.remove, f.name)
        self.assertEqual(diff.normalise(diff.load(f.name))["duration"], 20.0)

if __name__ == "__main__":
    unittest.main()
