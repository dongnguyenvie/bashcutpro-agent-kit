"""skills/audio-mix/loudness.py --tighten: commands that cut measured silences down, last first."""

import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("loudness", os.path.join(ROOT, "skills", "audio-mix", "loudness.py"))
loudness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loudness)


class TightenTests(unittest.TestCase):
    def test_last_silence_first_keeping_half_each_side(self):
        t = loudness.tighten([[2.0, 5.2], [8.8, 12.9], [18.6, 21.3]], 0.4)
        self.assertEqual(t["cuts"], 3)
        self.assertEqual(t["removedSeconds"], 8.8)
        self.assertEqual(t["commands"][:3], [
            {"id": "markers.markIn", "params": {"seconds": 18.8}},
            {"id": "markers.markOut", "params": {"seconds": 21.1}},
            {"id": "sequence.extract", "params": {}}])
        self.assertEqual(t["commands"][-3]["params"], {"seconds": 2.2})

    def test_short_silences_and_offset(self):
        t = loudness.tighten([[1.0, 1.45], [3.0, 4.0]], 0.4, offset=10.0)
        self.assertEqual(t["cuts"], 1)  # 0.45 s leaves under 0.1 s to cut
        self.assertEqual(t["commands"][0]["params"], {"seconds": 13.2})


if __name__ == "__main__":
    unittest.main()
