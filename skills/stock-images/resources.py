#!/usr/bin/env python3
"""Runs a fetch script of the bashcut.resources plugin (bashcutpro-plugins) and prints what the script prints.

    python3 resources.py <stock|emoji|logos|illustrations|…> [script args…]
    python3 resources.py credits <folder>              # credit lines from the licence records in a folder

The skill's fetch_*.py files call run(). The plugin runs BashCut's scripts unchanged, writes `<file>.licence.json`
next to every file they save, and reports picks (`--pick "slot=n@frame:duration"`) as `pending` placements for
the agent to place with `timeline.place`. The plugin is found from $BASHCUTPRO_RESOURCES_DIR, the BashCutPro
install folder (<data dir>/bashcut-plugins/bashcut.resources; the data dir in the order of BashCutPro's bashcut-dirs:
$BASHCUTPRO_DATA_DIR, else $FILMCRAFT_DATA_DIR, else ~/Library/Application Support/BashCutPro, %APPDATA%\BashCutPro or
$XDG_DATA_HOME/bashcutpro; with neither variable set, upstream FilmCraft's folder next), or a bashcutpro-plugins
checkout next to this kit.
Standard library only.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

INSTALL_HINT = ("the bashcut.resources plugin was not found: git clone https://github.com/dongnguyenvie/bashcutpro-plugins "
                "and set BASHCUTPRO_RESOURCES_DIR=<checkout>/plugins/resources")


OVERRIDES = ("BASHCUTPRO_DATA_DIR", "FILMCRAFT_DATA_DIR")  # bashcut-dirs' order, the first set one wins


def per_user(names):
    """`names` (macOS / Windows folder, XDG folder) under this user's data folder."""
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / names[0]
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or home) / names[0]
    return Path(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share") / names[1]


def data_dirs():
    """BashCutPro's data dir, then upstream FilmCraft's (read only) when no variable picks the folder."""
    for name in OVERRIDES:
        if os.environ.get(name):
            return [Path(os.environ[name])]
    return [per_user(("BashCutPro", "bashcutpro")), per_user(("FilmCraft", "filmcraft"))]


def plugin_dir():
    here = Path(__file__).resolve().parent
    candidates = [os.environ.get("BASHCUTPRO_RESOURCES_DIR")]
    candidates += [d / "bashcut-plugins" / "bashcut.resources" for d in data_dirs()]
    for start in (here, Path.cwd()):
        candidates += [p / "bashcutpro-plugins" / "plugins" / "resources" for p in (start, *start.parents)]
    for candidate in candidates:
        if candidate and (Path(candidate) / "plugin.py").is_file():
            return Path(candidate)
    return None


def plugin(*args):
    root = plugin_dir()
    if root is None:
        return 1, {"ok": False, "error": {"code": "no_plugin", "message": INSTALL_HINT}}
    env = dict(os.environ, PYTHONIOENCODING="utf-8")  # its JSON is UTF-8 whatever the console's code page is
    done = subprocess.run([sys.executable, str(root / "plugin.py"), *args], stdout=subprocess.PIPE, env=env)
    try:
        return done.returncode, json.loads(done.stdout.decode("utf-8"))
    except ValueError:
        return done.returncode or 1, {"ok": False, "error": {"code": "bad_output", "message": done.stdout.decode("utf-8", "replace")[:300]}}


def run(script, argv):
    code, result = plugin("fetch", "--script", script, "--args", json.dumps(argv))
    data = result.get("data") or {}
    for line in data.get("lines") or []:
        print(json.dumps(line, ensure_ascii=False))
    for text in data.get("text") or []:  # what the script printed that is not JSON, such as --help
        print(text)
    summary = {k: data[k] for k in ("files", "pending") if data.get(k)}
    if not result.get("ok"):
        summary["error"] = result.get("error")
    if summary:
        print(json.dumps(summary, ensure_ascii=False))
    return code


def main(argv):
    if argv[:1] == ["credits"] and len(argv) == 2:
        code, result = plugin("credits", "--folder", argv[1])
        print(json.dumps(result.get("data") or result, ensure_ascii=False, indent=1))
        return code
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    return run(argv[0], argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
