"""The no-FilmCraft rule (AK2): user-facing text (skills, README, plugin.json) never says FilmCraft; the technical
names (filmcraft-cli, FILMCRAFT_CLI, BASHCUT_FILMCRAFT_CLI, FILMCRAFT_DATA_DIR, the `filmcraft` source-build package)
are spelled differently and pass. What may still say FilmCraft is the older data folder (read only) and the upstream
provenance field in scripts/commands.json. Standard library only."""
import re

NAME = re.compile(r"\bFilm ?[Cc]raft\b")
# A line may name the older data folder or the upstream provenance; nothing else.
ALLOWED_LINE = [
    re.compile(r"Support/FilmCraft|%APPDATA%\\+FilmCraft"),  # the older engine's data folder paths
    re.compile(r'\(\s*"FilmCraft"\s*,\s*"filmcraft"\s*\)'),  # per_user(("FilmCraft", "filmcraft"))
    re.compile(r"older engine's (\(?`?FilmCraft`?\)? )?(knowledge |data )?folder|older engine's \(FilmCraft\)"),
    re.compile(r"older engine name FilmCraft"),  # knowledge.py: names the older data folder
    re.compile(r'^\s*"upstream":\s*"FilmCraft '),  # scripts/commands.json provenance
]


def brand_leaks(text):
    """(line number, line) of every line that says FilmCraft outside the allowlist."""
    return [(n, line.strip()) for n, line in enumerate(text.splitlines(), 1)
            if NAME.search(line) and not any(p.search(line) for p in ALLOWED_LINE)]
