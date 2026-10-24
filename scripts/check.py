#!/usr/bin/env python3
"""Check the kit: every skill's frontmatter (name matches its folder, description within limits and ending in
trigger phrases), its size, the files it references and the command ids it names (against scripts/commands.json,
copied from BashCutPro's bashcut/commands.json plus its merged bashcut.* ids and a `pending` list); relative links in every Markdown file; the README's
Skills table; the plugin, marketplace and MCP files; scripts/skill-commands.json (skill -> command ids, for the engine check)
is up to date; every skill naming command ids carries the shared sentence scripts/shared/engine-check.md verbatim.
`--write-index` rewrites that index. Prints one line per skill, then OK or the problems; exit 1
on any problem. Standard library only."""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brandcheck import brand_leaks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
MAX_LINES = 250
problems = []

# Command ids are checked only in namespaces the catalogue knows, so `grade.py` or `looks.json` are not ids.
CATALOGUE = json.load(open(os.path.join(ROOT, "scripts", "commands.json"), encoding="utf-8"))
COMMANDS = {c["id"] for c in CATALOGUE["commands"]}
# BashCutPro's window commands (bashcut.ui.*, bashcut.agent.*, bashcut.batch.*, …): bridge mode only.
COMMANDS |= {c["id"] for c in (CATALOGUE.get("frontend") or {}).get("ids", [])}
NAMESPACES = {i.split(".", 1)[0] for i in COMMANDS}
# Planned bashcut.* ids a skill may name (with a fallback) before they are merged.
PENDING = set((CATALOGUE.get("pending") or {}).get("ids") or {})
ID = re.compile(r"`([a-z][A-Za-z0-9]*(?:\.[A-Za-z0-9]+)+)`")
FILE_EXT = {"py", "json", "md", "sh", "cube", "fcgt", "fcproj", "srt", "vtt", "wav", "mp4", "png", "yaml", "txt"}


def named_ids(text):
    """The engine command ids a Markdown text names (plugin ids and file names excluded), sorted."""
    ids = set()
    for cid in ID.findall(text):
        if cid.rsplit(".", 1)[1] in FILE_EXT or cid.split(".", 1)[0] not in NAMESPACES:
            continue
        if cid.startswith("bashcut.") and cid.count(".") == 1:
            continue  # a plugin id (`bashcut.vision`), not an engine command (`bashcut.profiles.apply`)
        ids.add(cid)
    return sorted(ids)


def check_command_ids(path):
    for cid in named_ids(open(path, encoding="utf-8").read()):
        if cid in PENDING:
            continue
        if cid not in COMMANDS and not any(c.startswith(cid + ".") for c in COMMANDS):
            problems.append(f"{rel(path)}: command `{cid}` is not in scripts/commands.json")


ENGINE_CHECK_PATH = os.path.join(ROOT, "scripts", "shared", "engine-check.md")
# Any line that talks like the shared sentence must be the sentence, so a reworded copy cannot drift.
ENGINE_CHECK_MARKERS = ("never guess an id", "command_list` (or `bashcutpro-cli describe")


def check_engine_check(name, text, sentence):
    """A skill naming engine ids carries the shared engine-check sentence verbatim, and no edited copy of it."""
    if named_ids(text) and sentence not in text:
        problems.append(f"skills/{name}/SKILL.md: names command ids but lacks the sentence in scripts/shared/engine-check.md")
    for n, line in enumerate(text.splitlines(), 1):
        if sentence not in line and any(m in line for m in ENGINE_CHECK_MARKERS):
            problems.append(f"skills/{name}/SKILL.md:{n}: edited copy of the engine-check sentence (use scripts/shared/engine-check.md verbatim)")


def build_index(root=ROOT):
    """skill -> command ids named in its SKILL.md and REFERENCE.md, agent -> ids in agents/<name>.md, plus the
    kit version and the catalogue the ids were checked against (read by the doctor and the Agent panel)."""
    def ids_of(*paths):
        text = "\n".join(open(p, encoding="utf-8").read() for p in paths if os.path.isfile(p))
        return named_ids(text)

    skills_dir, agents_dir = os.path.join(root, "skills"), os.path.join(root, "agents")
    names = sorted(n for n in os.listdir(skills_dir) if os.path.isfile(os.path.join(skills_dir, n, "SKILL.md")))
    agent_files = sorted(f for f in os.listdir(agents_dir) if f.endswith(".md")) if os.path.isdir(agents_dir) else []
    plugin = json.load(open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    return {
        "kit": plugin.get("version"),
        "catalogue": CATALOGUE.get("source"),
        "skills": {n: ids_of(*(os.path.join(skills_dir, n, f) for f in ("SKILL.md", "REFERENCE.md"))) for n in names},
        "agents": {f[:-3]: ids_of(os.path.join(agents_dir, f)) for f in agent_files},
    }


def index_text(index):
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


INDEX_PATH = os.path.join(ROOT, "scripts", "skill-commands.json")


def check_index(index):
    try:
        committed = open(INDEX_PATH, encoding="utf-8").read()
    except OSError:
        problems.append("scripts/skill-commands.json is missing: run python3 scripts/check.py --write-index")
        return
    if committed != index_text(index):
        problems.append("scripts/skill-commands.json is stale: run python3 scripts/check.py --write-index and commit it")


def rel(path):
    return os.path.relpath(path, ROOT)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w[\w-]*):[ \t]*(.*)$", m.group(1), re.M)) if m else None


def check_skill(name):
    path = os.path.join(SKILLS, name, "SKILL.md")
    text = open(path, encoding="utf-8").read()
    meta = frontmatter(text)
    if meta is None:
        problems.append(f"{name}: no frontmatter")
        return
    if meta.get("name") != name:
        problems.append(f"{name}: name '{meta.get('name')}' does not match the folder")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"{name}: name must be lowercase words joined by '-' (max 64)")
    # The model belongs to Claude-only sub-agents (agents/*.md); SKILL.md frontmatter is shared with Codex.
    if "model" in meta:
        problems.append(f"{name}: no model in SKILL.md frontmatter (put it in agents/*.md)")
    desc = meta.get("description", "").strip()
    if not desc:
        problems.append(f"{name}: no description")
    elif len(desc) > 1024:
        problems.append(f"{name}: description is {len(desc)} characters (max 1024)")
    # Triggers are what users type; the description ends with them so both agents pick the skill up.
    triggers = re.search(r"Triggers:\s*(.+)$", desc)
    phrases = re.findall(r'"([^"]+)"', triggers.group(1)) if triggers else []
    if not phrases:
        problems.append(f'{name}: description must end with Triggers: "phrase", "phrase", …')
    for ref in re.findall(r"<skill_dir>/([\w./-]+)", text):
        if not os.path.exists(os.path.join(SKILLS, name, ref)):
            problems.append(f"{name}: <skill_dir>/{ref} does not exist")
    # A user-only skill must be user-only in Claude Code and in Codex alike.
    user_only = meta.get("disable-model-invocation", "").strip() == "true"
    policy = os.path.join(SKILLS, name, "agents", "openai.yaml")
    codex_off = os.path.isfile(policy) and re.search(
        r"^\s*allow_implicit_invocation:\s*false\s*$", open(policy, encoding="utf-8").read(), re.M) is not None
    if user_only != codex_off:
        problems.append(f"{name}: disable-model-invocation: true and agents/openai.yaml "
                        "policy.allow_implicit_invocation: false go together")
    lines = text.count("\n")
    if lines > MAX_LINES:
        problems.append(f"{name}: {lines} lines (max {MAX_LINES}); move detail into REFERENCE.md")
    print(f"{name:16s} {lines:4d} lines  description {len(desc):4d} chars  {len(phrases)} triggers")


def check_links(path):
    """Relative Markdown links and images must point at a file or folder in the kit."""
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # code blocks are not links
    for target in re.findall(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
        if re.match(r"[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
            continue
        file = target.split("#", 1)[0]
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), file))):
            problems.append(f"{rel(path)}: broken link {target}")


def load_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        problems.append(f"{rel(path)}: {e}")
        return {}


def main():
    skills = sorted(n for n in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, n, "SKILL.md")))
    for name in skills:
        check_skill(name)
        for f in ("SKILL.md", "REFERENCE.md"):
            if os.path.isfile(os.path.join(SKILLS, name, f)):
                check_command_ids(os.path.join(SKILLS, name, f))
    for f in sorted(os.listdir(os.path.join(ROOT, "agents"))) if os.path.isdir(os.path.join(ROOT, "agents")) else []:
        if f.endswith(".md"):
            check_command_ids(os.path.join(ROOT, "agents", f))

    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "_scratch")]
        for f in files:
            if f.endswith(".md"):
                check_links(os.path.join(folder, f))

    # The README's Skills table lists every skill, once, and nothing else.
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    table = re.search(r"^## Skills\n(.*?)^## ", readme, re.S | re.M)
    listed = re.findall(r"^\| `([a-z0-9-]+)` \|", table.group(1), re.M) if table else []
    if not table:
        problems.append("README.md: no ## Skills section")
    for name in sorted(set(skills) - set(listed)):
        problems.append(f"README.md: skill {name} missing from the Skills table")
    for name in sorted(set(listed) - set(skills)):
        problems.append(f"README.md: Skills table lists {name}, which is not a skill")
    for name in sorted({n for n in listed if listed.count(n) > 1}):
        problems.append(f"README.md: Skills table lists {name} twice")

    # Packaging: the marketplace serves this plugin, and the MCP server's launcher exists and runs.
    plugin = load_json(os.path.join(ROOT, ".claude-plugin", "plugin.json"))
    market = load_json(os.path.join(ROOT, ".claude-plugin", "marketplace.json"))
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(plugin.get("version", ""))):
        problems.append(".claude-plugin/plugin.json: version must be MAJOR.MINOR.PATCH")
    served = [p for p in market.get("plugins", []) if p.get("name") == plugin.get("name")]
    if not served or served[0].get("source") != "./":
        problems.append(f".claude-plugin/marketplace.json: must list plugin '{plugin.get('name')}' with source ./")
    for server, spec in load_json(os.path.join(ROOT, ".mcp.json")).get("mcpServers", {}).items():
        command = spec.get("command", "").replace("${CLAUDE_PLUGIN_ROOT}", ROOT)
        if command.startswith(ROOT) and not os.access(command, os.X_OK):
            problems.append(f".mcp.json: {server} command {rel(command)} is missing or not executable")

    # No FilmCraft wording for users (AK2): skills, README, plugin.json; scripts/commands.json keeps its provenance field.
    branded = [os.path.join(ROOT, "README.md"), os.path.join(ROOT, ".claude-plugin", "plugin.json"),
               os.path.join(ROOT, "scripts", "commands.json")]
    for folder, dirs, files in os.walk(SKILLS):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        branded += [os.path.join(folder, f) for f in files if f.endswith((".md", ".json", ".py", ".sh", ".yaml"))]
    for path in branded:
        for n, line in brand_leaks(open(path, encoding="utf-8").read()):
            problems.append(f"{rel(path)}:{n}: says FilmCraft (use BashCutPro, or the older engine): {line[:80]}")

    index = build_index()
    if "--write-index" in sys.argv[1:]:
        open(INDEX_PATH, "w", encoding="utf-8", newline="\n").write(index_text(index))
        print(f"wrote {rel(INDEX_PATH)}")
    else:
        check_index(index)

    print("\n".join(problems) or "OK")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
