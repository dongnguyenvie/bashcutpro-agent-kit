import unittest


class SkillRouting(unittest.TestCase):
    @unittest.skip("test ticket: every skill description carries a 'Not for ... (bcp:<other>)' clause naming an existing skill")
    def test_not_for_clauses_name_real_skills(self):
        pass

    @unittest.skip("test ticket: negative routing cases, each prompt must not trigger the named skill (vlog-plan vs edit-workflow, rough-cut vs beat-cut, effects vs motion-graphics, library vs stock-images vs visual-plan, review vs outcomes, captions-text vs vlog-hook-script, batch vs single-video skills)")
    def test_negative_prompts_do_not_route(self):
        pass


if __name__ == "__main__":
    unittest.main()
