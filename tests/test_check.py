"""scripts/check.py: the skill -> command id index (scripts/skill-commands.json) and the engine-check sentence."""

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check  # noqa: E402

with open(check.ENGINE_CHECK_PATH, encoding="utf-8") as _f:
    SENTENCE = _f.read().strip()
# Two real engine ids, deliberately out of alphabetical order.
ID_B, ID_A = sorted(check.COMMANDS)[-1], sorted(check.COMMANDS)[0]


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class FixtureKit(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        write(os.path.join(self.root, ".claude-plugin", "plugin.json"), json.dumps({"version": "9.9.9"}))
        write(os.path.join(self.root, "skills", "demo", "SKILL.md"),
              f"---\nname: demo\n---\nUse `{ID_B}` then `{ID_A}`, plugin `bashcut.vision`, file `grade.py`, "
              "unknown `zzz.thing`.\n")
        write(os.path.join(self.root, "agents", "helper.md"), f"Calls `{ID_A}`.\n")
        check.problems.clear()
        self.addCleanup(check.problems.clear)


class SkillIndexTests(FixtureKit):
    def test_index_emitted_from_fixture_skill(self):
        index = check.build_index(self.root)
        self.assertEqual(index["kit"], "9.9.9")
        self.assertEqual(index["skills"], {"demo": sorted([ID_A, ID_B])})
        self.assertEqual(index["agents"], {"helper": [ID_A]})
        self.assertEqual(check.index_text(index), check.index_text(check.build_index(self.root)))

    def test_stale_index_fails(self):
        check.check_index(check.build_index())
        self.assertEqual(check.problems, [], "the committed index is up to date")
        index = check.build_index()
        index["kit"] = "0.0.0-changed"
        check.check_index(index)
        self.assertTrue(any("stale" in p for p in check.problems))
        check.problems.clear()
        index = check.build_index()
        index["skills"][sorted(index["skills"])[0]].append("grade.extra")
        check.check_index(index)
        self.assertTrue(any("stale" in p for p in check.problems))

    def test_plugin_ids_excluded(self):
        self.assertEqual(check.named_ids("`bashcut.vision` `grade.py` `looks.json` `zzz.thing` `foo.bar.baz`"), [])
        self.assertEqual(check.named_ids(f"`{ID_A}` `bashcut.vision`"), [ID_A])
        self.assertEqual(check.build_index(self.root)["skills"]["demo"], sorted([ID_A, ID_B]))


class EngineCheckTests(unittest.TestCase):
    def setUp(self):
        check.problems.clear()
        self.addCleanup(check.problems.clear)

    def test_missing_sentence_fails(self):
        check.check_engine_check("demo", f"Use `{ID_A}` here.\n", SENTENCE)
        self.assertEqual(len(check.problems), 1)
        self.assertIn("lacks the sentence", check.problems[0])

    def test_edited_sentence_fails(self):
        reworded = SENTENCE.replace("never guess an id", "do not guess ids").replace("never guess", "do not guess")
        self.assertNotEqual(reworded, SENTENCE)
        check.check_engine_check("demo", f"Use `{ID_A}`.\n\n{reworded}\n", SENTENCE)
        self.assertTrue(check.problems)
        check.problems.clear()
        check.check_engine_check("demo", f"Use `{ID_A}`.\n\n{SENTENCE}\n\nRun `command_list` (or `bashcutpro-cli describe x`).\n", SENTENCE)
        self.assertTrue(any("edited copy" in p for p in check.problems))

    def test_verbatim_sentence_passes(self):
        check.check_engine_check("demo", "No ids here, only `grade.py` and `bashcut.vision`.\n", SENTENCE)
        self.assertEqual(check.problems, [])
        check.check_engine_check("demo", f"Use `{ID_A}`.\n\n{SENTENCE}\n", SENTENCE)
        self.assertEqual(check.problems, [])


if __name__ == "__main__":
    unittest.main()
