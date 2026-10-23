"""scripts/bashcutpro-mcp.sh finds the CLI by exact name: `bashcutpro-cli`, then `bcpro`, then `filmcraft-cli`
(never plain `bashcutpro`, the desktop app), with fakes on PATH."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCHER = os.path.join(ROOT, "scripts", "bashcutpro-mcp.sh")
SH = shutil.which("sh")

FAKE = """#!/bin/sh
echo "{name} $*"
"""


@unittest.skipUnless(SH, "needs a POSIX sh")
class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.bin = os.path.join(self.dir, "bin")
        os.makedirs(self.bin)

    def fake(self, name):
        path = os.path.join(self.bin, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FAKE.format(name=name))
        os.chmod(path, 0o755)
        return path

    def launch(self, stdin="", **env):
        e = {k: v for k, v in os.environ.items() if k not in ("BASHCUTPRO_CLI", "BASHCUT_FILMCRAFT_CLI", "FILMCRAFT_CLI", "BASHCUT_MCP", "BASHCUTPRO_BRIDGE", "BASHCUTPRO_PROJECT")}
        e.update(
            PATH=os.pathsep.join([self.bin, os.path.dirname(SH)]),
            HOME=self.dir,
            BASHCUTPRO_CONFIG=os.path.join(self.dir, "none.env"),
            BASHCUTPRO_DEMO="1",
            BASHCUTPRO_NO_LOCK="1",
        )
        e.update(env)
        return subprocess.run([SH, LAUNCHER], capture_output=True, text=True, env=e, timeout=30, input=stdin)

    def test_only_bashcutpro_cli_on_path(self):
        self.fake("bashcutpro-cli")
        r = self.launch()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "bashcutpro-cli mcp --demo")

    def test_only_bcpro_on_path(self):
        self.fake("bcpro")
        r = self.launch()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "bcpro mcp --demo")

    def test_only_filmcraft_cli_on_path(self):
        self.fake("filmcraft-cli")
        r = self.launch()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "filmcraft-cli mcp --demo")

    def test_order_bashcutpro_cli_bcpro_filmcraft_cli(self):
        self.fake("filmcraft-cli")
        self.fake("bcpro")
        self.assertEqual(self.launch().stdout.strip(), "bcpro mcp --demo")
        self.fake("bashcutpro-cli")
        self.assertEqual(self.launch().stdout.strip(), "bashcutpro-cli mcp --demo")

    def test_plain_bashcutpro_is_never_the_cli(self):
        # /usr/bin/bashcutpro is the desktop app on Linux: an exact-name lookup must not pick it
        self.fake("bashcutpro")
        r = self.launch()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.fake("filmcraft-cli")
        self.assertEqual(self.launch().stdout.strip(), "filmcraft-cli mcp --demo")

    def test_env_names_it(self):
        self.fake("bashcutpro-cli")
        old = self.fake("filmcraft-cli")
        for var in ("BASHCUTPRO_CLI", "BASHCUT_FILMCRAFT_CLI", "FILMCRAFT_CLI"):
            self.assertEqual(self.launch(**{var: old}).stdout.strip(), "filmcraft-cli mcp --demo", var)

    def test_none_says_what_to_do(self):
        r = self.launch()
        self.assertEqual(r.returncode, 1)
        self.assertIn("BASHCUTPRO_CLI", r.stderr)

    def test_none_answers_initialize_with_the_hint(self):
        # a closed pipe shows as CONNECTION_CLOSED in Claude Code: the reason must travel in a JSON-RPC error instead
        init = '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"x","version":"1"}}}'
        note = '{"jsonrpc":"2.0","method":"notifications/initialized"}'
        call = '{"jsonrpc":"2.0","id":"abc","method":"tools/list"}'
        r = self.launch(stdin="\n".join([init, note, call]) + "\n")
        self.assertEqual(r.returncode, 1)
        replies = [json.loads(line) for line in r.stdout.splitlines()]
        self.assertEqual([x["id"] for x in replies], [0, "abc"])
        for x in replies:
            self.assertEqual(x["jsonrpc"], "2.0")
            self.assertIn("bashcutpro-cli not found: install BashCutPro or set BASHCUTPRO_CLI", x["error"]["message"])
            self.assertIn("/bcp:setup", x["error"]["message"])

    def test_none_with_quoted_path_in_hint_stays_valid_json(self):
        config = os.path.join(self.dir, 'we"ird.env')
        r = self.launch(stdin='{"jsonrpc":"2.0","id":7,"method":"initialize"}\n', BASHCUTPRO_CONFIG=config)
        self.assertIn("we\"ird.env", json.loads(r.stdout)["error"]["message"])

    def test_in_app_agent_wins_over_missing_cli(self):
        r = self.launch(stdin='{"jsonrpc":"2.0","id":1,"method":"initialize"}\n', BASHCUT_IN_APP_AGENT="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "")

    def test_in_app_agent_starts_no_server(self):
        # a CLI is on PATH and would print if started; inside BashCutPro's Agent panel the launcher steps aside
        self.fake("bashcutpro-cli")
        r = self.launch(BASHCUT_IN_APP_AGENT="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "")
        self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
        # other values do not step aside
        self.assertEqual(self.launch(BASHCUT_IN_APP_AGENT="0").stdout.strip(), "bashcutpro-cli mcp --demo")


if __name__ == "__main__":
    unittest.main()
