"""skills/audio-mix/fetch_audio.py: music under every licence unless --safe-licence (CC0 / CC BY / CC BY-SA), the
licence on every row and in <file>.licence.json. Fake HTTP: no network."""

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.parse
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "audio-mix"))
spec = importlib.util.spec_from_file_location("fetch_audio", os.path.join(ROOT, "skills", "audio-mix", "fetch_audio.py"))
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


def hit(n, licence, version="4.0"):
    return {"url": f"https://cdn.example/{n}.mp3", "filetype": "mp3", "title": f"Track {n}", "duration": 90_000,
            "license": licence, "license_version": version, "creator": f"artist{n}",
            "foreign_landing_url": f"https://www.jamendo.com/track/{n}"}


# What Openverse sends back; with --safe-licence the script must drop NC / ND even if the API ignored the filter.
RESULTS = {"results": [hit(1, "by-nc-nd", "3.0"), hit(2, "cc0", "1.0"), hit(3, "by"), hit(4, "by-sa"),
                       hit(5, "by-nc"), hit(6, "by-nd")]}


class FakeWeb:
    def __init__(self):
        self.calls = []

    def __call__(self, url, *args, **kwargs):
        self.calls.append(url)
        if url.startswith("https://api.openverse.org/"):
            return json.dumps(RESULTS).encode()
        if url.startswith("https://cdn.example/"):
            return b"mp3"
        raise OSError(f"curl exit 22 for {url}")

    def openverse_query(self):
        url = next(u for u in self.calls if u.startswith("https://api.openverse.org/"))
        return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)


def run(argv, web):
    out = io.StringIO()
    with mock.patch.object(audio, "get", web), mock.patch.dict(os.environ, {}, clear=True), redirect_stdout(out):
        audio.main(argv)
    return out.getvalue()


class MusicLicenceTests(unittest.TestCase):
    def test_default_takes_every_licence(self):
        web = FakeWeb()
        with mock.patch.object(audio, "get", web):
            rows = audio.music_candidates("calm acoustic", 3, 30)
        self.assertNotIn("license", web.openverse_query())
        self.assertIn("CC BY-NC-ND 3.0", [r["license"] for r in rows])

    def test_safe_licence_asks_openverse_for_safe_licences_and_drops_the_rest(self):
        web = FakeWeb()
        with mock.patch.object(audio, "get", web):
            rows = audio.music_candidates("calm acoustic", 3, 30, any_licence=False)
        self.assertEqual(web.openverse_query()["license"], ["cc0,by,by-sa"])
        self.assertEqual([r["license"] for r in rows], ["CC0", "CC BY 4.0", "CC BY-SA 4.0"])

    def test_cli_default_lists_every_licence(self):
        with tempfile.TemporaryDirectory() as folder:
            out = run(["--dest", folder, "--music", "calm acoustic", "--music-count", "2", "--no-library"], FakeWeb())
        self.assertEqual([json.loads(line)["license"] for line in out.splitlines()], ["CC BY-NC-ND 3.0", "CC0"])

    def test_json_lines_carry_the_licence_and_a_record_sits_next_to_each_file(self):
        with tempfile.TemporaryDirectory() as folder:
            out = run(["--dest", folder, "--music", "calm acoustic", "--music-count", "2", "--no-library",
                       "--safe-licence"], FakeWeb())
            lines = [json.loads(line) for line in out.splitlines()]
            self.assertEqual([(l["file"], l["license"]) for l in lines],
                             [("music-track-2-1.mp3", "CC0"), ("music-track-3-2.mp3", "CC BY 4.0")])
            record = json.loads(Path(folder, "music-track-3-2.mp3.licence.json").read_text())
        self.assertEqual({k: record[k] for k in ("file", "license", "author", "source", "kind")},
                         {"file": "music-track-3-2.mp3", "license": "CC BY 4.0", "author": "artist3",
                          "source": "https://www.jamendo.com/track/3", "kind": "music"})

    def test_candidate_table_has_a_licence_column(self):
        with tempfile.TemporaryDirectory() as folder:
            out = run(["--dest", folder, "--music", "calm", "--music-count", "4", "--no-library", "--safe-licence"],
                      FakeWeb())
        header, *rows = out.splitlines()
        column = header.split("\t").index("licence")
        self.assertEqual([r.split("\t")[column] for r in rows], ["CC0", "CC BY 4.0", "CC BY-SA 4.0"])
        self.assertTrue(all(len(r.split("\t")) == len(header.split("\t")) for r in rows))

    def test_nothing_allowed_says_what_to_do(self):
        web = FakeWeb()
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.dict(RESULTS, {"results": [hit(1, "by-nc-nd")]}):
            out = run(["--dest", folder, "--music", "calm", "--no-library", "--safe-licence"], web)
        self.assertIn("--safe-licence", json.loads(out.splitlines()[0])["error"])

    def test_short_music_category_fills_up_from_uncategorised_audio_of_that_length(self):
        def web(url, *args, **kwargs):
            calls.append(urllib.parse.parse_qs(urllib.parse.urlparse(url).query))
            if "category=music" in url:
                return json.dumps({"results": []}).encode()  # what Jamendo leaves under the safe licences
            return json.dumps({"results": [dict(hit(7, "cc0"), duration=20_000), hit(8, "by")]}).encode()

        calls = []
        with mock.patch.object(audio, "get", web):
            rows = audio.music_candidates("calm acoustic", 2, 30, any_licence=False)
        self.assertEqual([c.get("category") for c in calls], [["music"], None])
        self.assertEqual(calls[1]["license"], ["cc0,by,by-sa"])
        self.assertEqual([(r["title"], r["license"]) for r in rows], [("Track 8", "CC BY 4.0")])

    def test_openverse_sfx_safe_licence_uses_the_same_filter(self):
        web = FakeWeb()
        with mock.patch.object(audio, "get", web):
            rows = audio.openverse_sfx("pop", 120, 2, any_licence=False)
        self.assertEqual(web.openverse_query()["license"], ["cc0,by,by-sa"])
        self.assertNotIn("category", web.openverse_query())
        self.assertTrue(all("NC" not in r["license"] and "ND" not in r["license"] for r in rows))


if __name__ == "__main__":
    unittest.main()
