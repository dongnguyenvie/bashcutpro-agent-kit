"""skills/stock-images/resources.py finds the bashcut.resources plugin in BashCutPro's data dir (bashcut-dirs' order),
then in upstream FilmCraft's folder when no variable picks the folder."""

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("resources", os.path.join(ROOT, "skills", "stock-images", "resources.py"))
resources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resources)


class DataDirTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        # a bashcutpro-plugins checkout next to this kit would be found too: look from inside the temp folder only
        here = mock.patch.object(resources, "__file__", str(self.dir / "kit" / "resources.py"))
        cwd = mock.patch.object(resources.Path, "cwd", return_value=self.dir)
        here.start(), cwd.start()
        self.addCleanup(here.stop)
        self.addCleanup(cwd.stop)

    def env(self, **extra):
        values = {"HOME": str(self.dir), "USERPROFILE": str(self.dir), "APPDATA": str(self.dir), "XDG_DATA_HOME": str(self.dir)}
        return mock.patch.dict(os.environ, dict(values, **extra), clear=True)

    def install(self, data_dir):
        folder = Path(data_dir) / "bashcut-plugins" / "bashcut.resources"
        folder.mkdir(parents=True)
        (folder / "plugin.py").write_text("", encoding="utf-8")
        return folder

    def test_order_of_the_variables(self):
        with self.env(BASHCUTPRO_DATA_DIR="/bc", FILMCRAFT_DATA_DIR="/fc"):
            self.assertEqual(resources.data_dirs(), [Path("/bc")])
        with self.env(FILMCRAFT_DATA_DIR="/fc"):
            self.assertEqual(resources.data_dirs(), [Path("/fc")])

    def test_per_os_defaults(self):
        for platform, ours, theirs in (("darwin", "Library/Application Support/BashCutPro", "Library/Application Support/FilmCraft"),
                                       ("win32", "BashCutPro", "FilmCraft"), ("linux", "bashcutpro", "filmcraft")):
            with self.subTest(platform), self.env(), mock.patch.object(resources.sys, "platform", platform), \
                    mock.patch.object(resources.Path, "home", return_value=self.dir):
                self.assertEqual(resources.data_dirs(), [self.dir / ours, self.dir / theirs])

    def test_bashcutpro_install_wins_and_filmcraft_is_the_fallback(self):
        with self.env(), mock.patch.object(resources.Path, "home", return_value=self.dir):
            ours, theirs = resources.data_dirs()
            self.assertIsNone(resources.plugin_dir())
            old = self.install(theirs)
            self.assertEqual(resources.plugin_dir(), old)
            new = self.install(ours)
            self.assertEqual(resources.plugin_dir(), new)

    def test_a_variable_turns_the_filmcraft_fallback_off(self):
        with self.env(BASHCUTPRO_DATA_DIR=str(self.dir / "bc")), mock.patch.object(resources.Path, "home", return_value=self.dir):
            self.install(resources.per_user(("FilmCraft", "filmcraft")))
            self.assertIsNone(resources.plugin_dir())
            new = self.install(self.dir / "bc")
            self.assertEqual(resources.plugin_dir(), new)


if __name__ == "__main__":
    unittest.main()
