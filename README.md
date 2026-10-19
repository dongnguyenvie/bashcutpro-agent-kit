# BashCutPro agent kit

Editing skills for Claude Code and Codex that drive [BashCutPro](https://github.com/dongnguyenvie/BashCutPro)
(a fork of FilmCraft) through its MCP server (`filmcraft-cli mcp`) and command ids.

The skills carry over the editing craft of [bashcut-agent-kit](https://github.com/dongnguyenvie/bashcut-agent-kit)
(how to cut, mix, caption and review well), rewritten against FilmCraft's command model: `command_list` to find a
command, `command_run {id, params}` or `command_batch` to edit (undoable), `doc_inspect` to read the project and
sequence, `render_frame` to look. They do not map BashCut's own tools. Plan and order:
[`bashcut/migration.md`](https://github.com/dongnguyenvie/BashCutPro/blob/main/bashcut/migration.md) in BashCutPro,
tracked in [BashCutPro#24](https://github.com/dongnguyenvie/BashCutPro/issues/24).

## Skills

| Skill | Use it for |
|---|---|
| `edit-workflow` | The spine of every edit, raw footage to export: intake, brief and plan in the project notes, stages with the one skill to read for each, `command_batch` per stage, the user's gates, draft and export |
| `setup` | Getting `filmcraft-cli` (source build or release, macOS / Windows / Linux), registering its MCP server headless (a project, the demo, or empty) or bridged to the running app, and checking `command_list` answers |
| `color-grade` | Grading by measurement: scopes on the brightest, darkest and skin-heavy frames, Lumetri presets and LUTs (`grade.py` generates fitted looks), damage checks and backing off, shot match, one adjustment layer |

Claude Code shows them under the plugin name (`/bcp:setup`); Codex as `bcp-<name>`. The editing skills
(`edit-workflow`, `rough-cut`, `captions-text`, …) follow in BashCutPro#5–#7, once the command catalogue (#3) lands.

## Requirements

- `filmcraft-cli` from a BashCutPro source build (`cargo build --release -p filmcraft-cli`) or a release. The
  `setup` skill walks through it.
- For bridge mode, the desktop app started with `filmcraft --control <port>`.
- Claude Code or Codex.

## Install

**Claude Code** (one command each, in a terminal):

```sh
claude plugin marketplace add dongnguyenvie/bashcutpro-agent-kit
claude plugin install bcp@bashcutpro-agent-kit
```

Or inside Claude Code: `/plugin marketplace add dongnguyenvie/bashcutpro-agent-kit`, then
`/plugin install bcp@bashcutpro-agent-kit`. The plugin brings the skills and a `bashcutpro` MCP server whose
launcher, [`scripts/bashcutpro-mcp.sh`](scripts/bashcutpro-mcp.sh), finds `filmcraft-cli` (`FILMCRAFT_CLI`, then
`PATH`, then the usual install places) and picks the mode from `~/.config/bashcutpro/mcp.env`. Then run
`/bcp:setup`, which writes that file. To try a local checkout for one session:
`claude --plugin-dir /path/to/bashcutpro-agent-kit`.

On Windows the launcher (a POSIX shell script) may not start; `/bcp:setup` registers `filmcraft-cli.exe`
directly instead.

**Codex** (macOS, Linux):

```sh
git clone https://github.com/dongnguyenvie/bashcutpro-agent-kit
sh bashcutpro-agent-kit/scripts/install-codex.sh
```

It links each skill as `~/.agents/skills/bcp-<name>` and registers the launcher as the `bashcutpro` MCP server;
`--uninstall` removes both. On Windows, see the `setup` skill.

### Launcher settings

`mcp.env` (or the environment, which wins) holds plain `NAME=value` lines:

| Name | Effect |
|---|---|
| `FILMCRAFT_CLI` | the `filmcraft-cli` binary |
| `BASHCUTPRO_BRIDGE` | `host:port` of the running app: `mcp --bridge` |
| `BASHCUTPRO_PROJECT` | headless: `mcp --project` this `.fcproj` |
| `BASHCUTPRO_DEMO` | `1`: headless on the demo project |
| `BASHCUTPRO_DATA_DIR` | headless: `--data-dir` (user presets) |

With none of the mode names set, the server is headless with an empty project.

## Layout

```
.claude-plugin/plugin.json        plugin "bcp" (skills show as /bcp:<name>)
.claude-plugin/marketplace.json   marketplace "bashcutpro-agent-kit", serving this repository as the plugin
.mcp.json                         the plugin's MCP server "bashcutpro" (scripts/bashcutpro-mcp.sh)
skills/<name>/SKILL.md            the skills (Agent Skills format, shared by Claude Code and Codex)
skills/<name>/REFERENCE.md        detail a skill reads on demand (keeps SKILL.md under 250 lines)
scripts/commands.json             FilmCraft command catalogue (copy of BashCutPro bashcut/commands.json); check.py
                                  rejects command ids a skill names that are not in it
skills/<name>/agents/openai.yaml  Codex policy, only for a user-only skill (disable-model-invocation: true)
scripts/bashcutpro-mcp.sh         finds filmcraft-cli and starts `filmcraft-cli mcp` in the configured mode
scripts/install-codex.sh          Codex setup
scripts/check.py                  checks skills, links, the Skills table and the packaging files
```

## Writing skills

- English instructions; trigger phrases may be in any language users speak (Vietnamese included).
- Frontmatter: `name` (the folder name), `description` (what and when, at most 1024 characters) ending in
  `Triggers: "phrase", "phrase", …`.
- Use FilmCraft command ids found with `command_list`, never BashCut's commands; say what to do and why.
- Only rules that were observed (a measurement, an error, a user's correction), with the number that proves it.
- Run `python3 scripts/check.py` before committing. A change to `skills/` raises `version` in
  `.claude-plugin/plugin.json`: Claude Code caches an installed plugin per version.

## License

MIT. See [LICENSE](LICENSE).
