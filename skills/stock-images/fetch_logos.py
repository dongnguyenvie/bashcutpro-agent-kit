#!/usr/bin/env python3
"""Runs fetch_logos.py of the bashcut.resources plugin, the one copy the plugin uses too: same flags (`--help`), same
output lines, then one line with the licence record of every file it saved and the picks left to place. Needs a
bashcutpro-plugins checkout or install (see resources.py). Standard library only."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resources import run  # noqa: E402

if __name__ == "__main__":
    sys.exit(run("logos", sys.argv[1:]))
