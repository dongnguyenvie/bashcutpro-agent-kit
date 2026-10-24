"""scripts/check.py: the skill -> command id index (scripts/skill-commands.json)."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


class SkillIndexTests(unittest.TestCase):
    @unittest.skip("test ticket: build_index on a fixture kit lists each skill's and agent's ids, sorted, with kit version")
    def test_index_emitted_from_fixture_skill(self):
        pass

    @unittest.skip("test ticket: a changed skill id or version makes check_index report scripts/skill-commands.json stale")
    def test_stale_index_fails(self):
        pass

    @unittest.skip("test ticket: plugin ids (bashcut.vision), file names and unknown namespaces are not in the index")
    def test_plugin_ids_excluded(self):
        pass


class EngineCheckTests(unittest.TestCase):
    @unittest.skip("test ticket: a skill naming command ids without the engine-check sentence fails check.py")
    def test_missing_sentence_fails(self):
        pass

    @unittest.skip("test ticket: a reworded copy of the engine-check sentence fails check.py")
    def test_edited_sentence_fails(self):
        pass

    @unittest.skip("test ticket: a skill naming no ids needs no sentence; the verbatim sentence passes")
    def test_verbatim_sentence_passes(self):
        pass


if __name__ == "__main__":
    unittest.main()
