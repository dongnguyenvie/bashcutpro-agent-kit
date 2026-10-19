"""skills/self-learn/knowledge.py: lessons, preferences, facts, proposals, correction hook, intake."""

import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("knowledge", os.path.join(ROOT, "skills", "self-learn", "knowledge.py"))
knowledge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(knowledge)


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.store = knowledge.Store(os.path.join(self.dir, "knowledge"))
        self.project = os.path.join(self.dir, "film.fcproj")

    def run_cli(self, *argv, stdin=None):
        code, text = knowledge.run(list(argv), self.store, stdin)
        return code, (json.loads(text) if text.startswith(("{", "[")) else text)

    def test_add_search_update_remove(self):
        code, lesson = self.run_cli("add-lesson", "Dissolve refused", "--symptom", "not adjacent", "--fix", "close the gap",
                                    "--tags", "Transitions", "--project", self.project)
        self.assertEqual((code, lesson["id"], lesson["tags"]), (0, "dissolve-refused", ["transitions"]))
        _, again = self.run_cli("add-lesson", "Dissolve refused", "--symptom", "x", "--fix", "y")
        self.assertEqual(again["id"], "dissolve-refused-2")
        self.assertEqual(len(self.run_cli("lessons", "--tag", "transitions")[1]), 1)
        self.assertEqual(len(self.run_cli("lessons", "--query", "GAP")[1]), 1)
        _, updated = self.run_cli("update-lesson", "dissolve-refused", "--seen", "--evidence", '"no, close it first"')
        self.assertEqual(updated["occurrences"], 2)
        self.assertEqual(self.run_cli("lessons")[1][0]["id"], "dissolve-refused")  # most seen first
        self.assertEqual(self.run_cli("update-lesson", "nope", "--seen")[0], 1)
        self.run_cli("remove-lesson", "dissolve-refused-2")
        self.assertEqual(len(self.run_cli("lessons", "--all")[1]), 1)

    def test_proposed_lessons_are_not_active(self):
        self.run_cli("add-lesson", "Maybe", "--symptom", "s", "--fix", "f", "--status", "proposed")
        self.assertEqual(self.run_cli("lessons")[1], [])
        self.assertIn("1 proposed lesson", self.store.intake())

    def test_prefs_and_facts(self):
        self.run_cli("set-pref", "pace", "calm", "--words", "nhịp chậm thôi")
        self.run_cli("set-pref", "pace", "fast")
        self.assertEqual(self.run_cli("prefs")[1]["pace"]["value"], "fast")
        self.run_cli("set-fact", "host", "Lan", "--project", self.project)
        self.assertTrue(os.path.isfile(self.project + ".bashcut/facts.json"))
        self.assertEqual(self.run_cli("facts", "--project", self.project)[1]["host"]["value"], "Lan")
        self.assertEqual(self.run_cli("set-fact", "missing", "--remove", "--project", self.project)[0], 1)
        self.run_cli("set-pref", "pace", "--remove")
        self.assertEqual(self.run_cli("prefs")[1], {})

    def test_propose_copies_the_file(self):
        draft = os.path.join(self.dir, "SKILL.md")
        with open(draft, "w") as f:
            f.write("changed")
        _, entry = self.run_cli("propose", "beat-cut", draft, "--summary", "s", "--reason", "r")
        self.assertTrue(os.path.isfile(os.path.join(self.store.root, "skills", entry["file"])))
        self.assertEqual(len(self.run_cli("proposals")[1]), 1)

    def test_hook_is_off_without_the_setting(self):
        with mock.patch.dict(os.environ, {"BASHCUTPRO_SELF_LEARN": "0"}):
            self.run_cli("hook", "correction", stdin=json.dumps({"prompt": "no, don't use that font"}))
        self.assertEqual(self.store.corrections(), [])

    def test_correction_in_one_session_is_printed_by_the_next_intake(self):
        with mock.patch.dict(os.environ, {"BASHCUTPRO_SELF_LEARN": "1"}):
            # session 1: the hook keeps the correction, ignores a plain request, survives a compaction
            self.run_cli("hook", "correction", stdin=json.dumps({"prompt": "Không phải font này, lần sau dùng Be Vietnam Pro"}))
            self.run_cli("hook", "correction", stdin=json.dumps({"prompt": "export the draft please"}))
            self.run_cli("hook", "correction", stdin="not json")
            _, text = self.run_cli("hook", "after-compact", stdin="{}")
        self.assertEqual(len(self.store.corrections()), 1)
        self.assertIn("Be Vietnam Pro", text)
        self.assertIn("1 correction candidate", self.store.intake(self.project))
        # self-learn at the end of session 1 turns it into a lesson and clears the inbox
        quote = self.store.corrections()[0]["text"]
        self.run_cli("add-lesson", "Vietnamese captions font", "--symptom", "the user rejected the caption font",
                     "--fix", "use Be Vietnam Pro for Vietnamese captions", "--evidence", quote, "--tags", "captions",
                     "--project", self.project)
        self.run_cli("corrections", "--clear")
        # session 2: intake for a captions edit prints it; an unrelated tag does not
        _, text = self.run_cli("intake", "--project", self.project, "--tags", "captions")
        self.assertIn("Be Vietnam Pro", text)
        self.assertNotIn("correction candidate", text)
        _, text = self.run_cli("intake", "--tags", "audio")
        self.assertNotIn("Be Vietnam Pro", text)

    def test_damaged_line_is_skipped(self):
        self.run_cli("add-lesson", "A", "--symptom", "s", "--fix", "f")
        with open(os.path.join(self.store.root, "lessons.jsonl"), "a") as f:
            f.write("{broken\n")
        self.assertEqual(len(self.store.lessons()), 1)


if __name__ == "__main__":
    unittest.main()
