"""scripts/brandcheck.py: no FilmCraft wording for users, technical names and the older data folder allowed."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from brandcheck import brand_leaks  # noqa: E402


class BrandTests(unittest.TestCase):
    def test_prose_is_flagged(self):
        self.assertEqual([n for n, _ in brand_leaks("ok\nOpen FilmCraft and export.\nthe Filmcraft app")], [2, 3])
        self.assertEqual(len(brand_leaks("Film Craft is open")), 1)

    def test_technical_names_pass(self):
        text = "\n".join([
            "run `filmcraft-cli mcp`", "set FILMCRAFT_CLI or BASHCUT_FILMCRAFT_CLI", "FILMCRAFT_DATA_DIR=/x",
            "cargo build -p filmcraft --features filmcraft/whisper", "$XDG_DATA_HOME/filmcraft",
        ])
        self.assertEqual(brand_leaks(text), [])

    def test_older_data_folder_and_provenance_pass(self):
        text = "\n".join([
            "Support/FilmCraft, %APPDATA%\\\\FilmCraft",
            'return [per_user(("FilmCraft", "filmcraft"))]',
            "read from the older engine's folder (`FilmCraft`)",
            '  "upstream": "FilmCraft dd525c93 (v0.10.0 + 20)",',
        ])
        self.assertEqual(brand_leaks(text), [])

    def test_kit_files_are_clean(self):
        paths = [os.path.join(ROOT, "README.md"), os.path.join(ROOT, ".claude-plugin", "plugin.json")]
        for folder, _, files in os.walk(os.path.join(ROOT, "skills")):
            paths += [os.path.join(folder, f) for f in files if f.endswith(".md")]
        for path in paths:
            with open(path, encoding="utf-8") as fh:
                self.assertEqual(brand_leaks(fh.read()), [], path)


if __name__ == "__main__":
    unittest.main()
