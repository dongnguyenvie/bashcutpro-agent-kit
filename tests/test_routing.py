"""Skill descriptions: the "Not for ... (bcp:<other>)" routing clauses and the trigger phrases."""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
MAX_DESCRIPTION = 460
# bcp:setup is user-invoked, it has no neighbour to route away from.
NO_NOT_FOR = {"setup"}


def descriptions():
    out = {}
    for name in sorted(os.listdir(SKILLS)):
        path = os.path.join(SKILLS, name, "SKILL.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            out[name] = re.search(r"^description:[ \t]*(.*)$", text, re.M).group(1).strip()
    return out


def triggers(desc):
    return [p.lower() for p in re.findall(r'"([^"]+)"', desc.split("Triggers:", 1)[1])]


def fires(desc, prompt):
    """Whether the prompt carries one of the skill's trigger phrases (what the description routes on)."""
    return any(t in prompt.lower() for t in triggers(desc))


# (prompt, skill it belongs to, skill it must not route to): trigger phrases are the other skill's.
NEGATIVE = [
    # vlog-plan / edit-workflow / rough-cut / vlog-ideate
    ("make a shot list for my trip", "vlog-plan", "edit-workflow"),
    ("sửa lại video giúp mình", "edit-workflow", "vlog-plan"),
    ("what video can I make from this footage", "vlog-ideate", "vlog-plan"),
    ("what video can I make from this footage", "vlog-ideate", "rough-cut"),
    ("selects from the interview, cut by quote", "rough-cut", "vlog-ideate"),
    ("selects from the interview, cut by quote", "rough-cut", "edit-workflow"),
    # rough-cut / beat-cut
    ("cut to the beat of the song", "beat-cut", "rough-cut"),
    # effects / motion-graphics
    ("add a transition between these shots", "effects", "motion-graphics"),
    ("add a lower third with the name", "motion-graphics", "effects"),
    ("thêm infographic số liệu chạy", "motion-graphics", "effects"),
    # library / stock-images / visual-plan
    ("save to my library and reuse the look", "library", "stock-images"),
    ("save to my library and reuse the look", "library", "visual-plan"),
    ("lấy ảnh stock trên pexels", "stock-images", "library"),
    ("lấy ảnh stock trên pexels", "stock-images", "visual-plan"),
    ("câu này hiện gì trên hình", "visual-plan", "stock-images"),
    ("câu này hiện gì trên hình", "visual-plan", "library"),
    # review / outcomes
    ("check my edit before export", "review", "outcomes"),
    ("why did viewers leave at the start", "outcomes", "review"),
    # captions-text / vlog-hook-script
    ("add subtitles to the video", "captions-text", "vlog-hook-script"),
    ("write a hook for the opening", "vlog-hook-script", "captions-text"),
    # batch vs single-video skills
    ("do this for 100 videos in a whole folder", "batch", "edit-workflow"),
    ("dựng video này giúp mình", "edit-workflow", "batch"),
    ("edit this clip", "edit-workflow", "batch"),
]


class SkillRouting(unittest.TestCase):
    def test_not_for_clauses_name_real_skills(self):
        descs = descriptions()
        for name, desc in descs.items():
            if name in NO_NOT_FOR:
                continue
            self.assertIn("Not for ", desc, f"{name}: no 'Not for' clause")
            named = re.findall(r"\(bcp:([\w-]+)\)", desc.split("Triggers:", 1)[0])
            self.assertTrue(named, f"{name}: 'Not for' names no (bcp:<skill>)")
            for other in named:
                self.assertIn(other, descs, f"{name}: 'Not for' names missing skill bcp:{other}")
                self.assertNotEqual(other, name, f"{name}: 'Not for' names itself")

    def test_description_length(self):
        for name, desc in descriptions().items():
            self.assertLessEqual(len(desc), MAX_DESCRIPTION, f"{name}: description is {len(desc)} chars")

    def test_negative_prompts_do_not_route(self):
        descs = descriptions()
        for prompt, owner, other in NEGATIVE:
            self.assertTrue(fires(descs[owner], prompt), f"{prompt!r} should trigger bcp:{owner}")
            self.assertFalse(fires(descs[other], prompt), f"{prompt!r} must not trigger bcp:{other}")


if __name__ == "__main__":
    unittest.main()
