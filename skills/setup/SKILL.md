---
name: setup
description: Connect Claude Code or Codex to BashCutPro: install bashcutpro-cli, register its MCP server (headless or --control), check command_list; changes nothing without a yes. Use only when BashCutPro tools are missing or fail to start; not for editing. Triggers: "/bcp:setup", "setup BashCutPro", "connect BashCutPro", "install bashcutpro", "install bashcutpro-cli", "install bcpro", "MCP not connected", "cài BashCutPro", "kết nối BashCutPro".
---

# Setting up BashCutPro's MCP server

An id or param this engine rejects: run `command_list` (or `bashcutpro-cli describe <id>`) and use what it lists; never guess an id; if a skill's id is missing, say the kit and BashCutPro versions differ (bcp:setup).

BashCutPro is driven through one MCP server, `bashcutpro` (`bashcutpro-cli mcp`, stdio). Every later skill assumes
its tools answer: `command_list`, `command_run`, `command_batch`, `doc_inspect`, `render_frame`. This skill gets the
binary, registers the server and proves it works. It changes nothing in the user's project.

Plain words: the user may not be technical. Never remove or rewrite MCP servers that are not `bashcutpro`.
Inside BashCutPro's Agent panel (the app sets `BASHCUT_IN_APP_AGENT=1`; no shell command is needed to know it: the
first message or the `bashcutpro` tools already answering say so) skip registration (steps 2 to 4), do steps 1 and 5
only, and say in one sentence that setup runs inside BashCutPro.

## 0. How this skill runs

It works the same in an interactive terminal and in a session nobody answers mid-turn: BashCutPro's Agent panel,
`claude -p`, Batch. So:

- **Check first, change later.** Steps 1 and 2 only read (the commands in the table below). Anything that changes
  the machine (a build, a download, an install, a registration, writing `mcp.env`) is proposed with the exact
  command and runs only after the user says yes in a reply. End the turn with the proposal; never wait on a prompt.
- **No interactive commands.** Nothing that asks for input: no `sudo`, no password, no editor, no `read`. Every
  command below finishes on its own.
- **A denied command is an answer.** If a command is denied (permission refused, "requires approval", blocked),
  do not retry it, do not try another command that does the same, and do not ask for broader permission. Tell the
  user in one sentence what was denied and give the exact command to run in their own terminal, then go on with
  what you can check without it.
- **In BashCutPro's Agent panel** (the app sets `BASHCUT_IN_APP_AGENT=1`; the plugin's launcher then exits at once
  with one stderr line and serves nothing) the app brings its own `bashcutpro` server bridged to the open window: never
  register another one there (Claude would see two copies of the same tools) and never ask for a global plugin install
  (the app loads the kit itself). If its tools are missing, the fix is
  in the app (step 5's table), not in Claude's settings.

The only shell commands this skill runs, all short and non-interactive (`<cli>` is a candidate from step 2:
`bashcutpro-cli`, `bcpro`, `filmcraft-cli` or an absolute path to one of them):

| When | Command | Why |
|---|---|---|
| check | `command -v bashcutpro-cli bcpro filmcraft-cli` | which CLI is on `PATH` (git-bash on Windows too) |
| check | `printenv BASHCUTPRO_CLI BASHCUT_FILMCRAFT_CLI FILMCRAFT_CLI BASHCUT_MCP` | a CLI named in the environment (exit 1 just means one is unset) |
| check | `<cli> commands razor` | the candidate is the engine: prints JSON, exits 0 |
| change, after yes | `claude mcp add -s user bashcutpro -- <cli> mcp <mode>` | direct registration (step 4), never in the Agent panel |
| change, after yes | `codex mcp add bashcutpro -- <cli> mcp <mode>` or `sh scripts/install-codex.sh` | Codex (step 4) |
| change, after yes | `git clone https://github.com/dongnguyenvie/BashCutPro` and the `cargo build` in step 2 | source build, several minutes |

Files are read with the Read tool, not the shell: `~/.config/bashcutpro/mcp.env` (`$XDG_CONFIG_HOME` if set),
`<data dir>/bashcut/automation.json`, the install places in step 2. `mcp.env` is written with the Write tool after
the user's yes. MCP tools used: `command_list`, `doc_inspect`, `ui_inspect` of the `bashcutpro` server.

## 1. Is it already working?

Call `command_list` with `{"filter": "razor"}`. A list of commands with ids such as `timeline.razor` means the
server is up: skip to step 5 to say which mode it runs in. Otherwise note the error (tool missing, server failed
to start, connection refused) and go on.

## 2. Get `bashcutpro-cli`

`bashcutpro-cli` (short name `bcpro`, the same program) is BashCutPro's command line: the editor's engine, the
same one the app uses. Plain `bashcutpro` is the desktop app, not the command line (on Linux it is
`/usr/bin/bashcutpro`); never register it as the server. `filmcraft-cli` is the older engine name (older builds);
it works too. Look for one first, by exact name: `BASHCUTPRO_CLI`, `BASHCUT_FILMCRAFT_CLI` or `FILMCRAFT_CLI` in
the environment, then `bashcutpro-cli`, `bcpro`, `filmcraft-cli` on `PATH`, a BashCutPro checkout's
`target/release/bashcutpro-cli` (`.exe` on Windows), then the install places below. Check a candidate with
`<cli> commands razor`: it prints JSON and exits 0.

**From a release** (the easy way). Install a [BashCutPro release](https://github.com/dongnguyenvie/BashCutPro/releases);
every package carries the CLI next to the app:

| OS | Where the CLI is after installing |
|---|---|
| Windows (MSI, portable zip) | `C:\Program Files\BashCutPro\bashcutpro-cli.exe` (and `bcpro.exe`) by default, not on `PATH`; the portable zip has them in its folder |
| Linux (deb, rpm) | `/usr/bin/bashcutpro-cli` and `/usr/bin/bcpro` (`/usr/bin/bashcutpro` is the desktop app) |
| macOS | `/Applications/BashCutPro.app/Contents/MacOS/bashcutpro-cli` (and `bcpro`), or the separate CLI zip asset; unzip it to `~/.local/bin` or another folder on `PATH` |

Installing is the user's step: give them the link and the file to pick for their OS. If macOS refuses to open a
downloaded binary, the user can allow it in System Settings › Privacy & Security.

**From source** (any OS; needs Rust from rustup.rs). Propose it with the time it takes (a first build is several
minutes) and run it only after a yes:

```sh
git clone https://github.com/dongnguyenvie/BashCutPro && cd BashCutPro
cargo build --release -p bashcutpro-cli --features bashcutpro-cli/whisper
# add -p filmcraft (and --features filmcraft/whisper) for the desktop app (bridge mode); a source build keeps the
# older engine name for it: the package and binary are called filmcraft
```

`--features bashcutpro-cli/whisper` adds speech to text (`bashcut.transcript.generate`): captions, rough cuts by
quote and the review's cut-inside-a-word check all need words. Without it, words come from an outside transcriber
(bcp:footage-survey). The binary is `target/release/bashcutpro-cli` (`bcpro` beside it is the same program).

**Python for the kit's scripts.** The skills write `"${BASHCUT_PYTHON:-python3}" <script>`: `BASHCUT_PYTHON` names
the interpreter when it is set (bashcut-batch sets it for every agent step and names it in the prompt,
BashCutPro#223). In a headless agent, type that name itself (`python <script>`): allow rules such as
`Bash(python:*)` match the command's first word, so a variable needs approval. Unset on Windows: use `python` (or
`py`), never `python3`, which is usually the Microsoft Store stub; set `PYTHONUTF8=1` so Vietnamese text prints.

## 3. Pick the mode

| Mode | Server arguments | When |
|---|---|---|
| Headless, project | `mcp --project /abs/path/p.fcproj` | edit a project file with no window |
| Headless, demo | `mcp --demo` | try things on the built-in demo project |
| Headless, empty | `mcp` | start from nothing |
| Bridge | `mcp --bridge 127.0.0.1:9876` | drive the app the user has open; also unlocks `ui_*` tools |

Headless also takes `--data-dir DIR` (user presets). Any other option is rejected with exit 2. For the bridge
the app must be running with its control channel, which listens on `127.0.0.1` only. It is on by default (a free
port, written to `<data dir>/bashcut/automation.json`); `bashcutpro --control 9876` picks the port (a source
build: `filmcraft --control 9876`). The channel needs a session token: the app makes one per launch and writes it to `automation.json` (owner-only),
and `bashcutpro-mcp` / `bashcutpro-cli` pick it up. If a tool says "control authentication failed", the user restarts
BashCutPro and the agent; never print the token. Starting the app is the user's step.

If a `ui_*` request answers `window not in front … call ui.focus {}`, call `ui.focus {}` once, then re-read
(`ui.elements`, `ui.screenshot`) before acting again; details in `bcp:edit-workflow` (`REFERENCE.md`).

Default to headless with the user's project when they name one, the bridge when they want to watch the app.

## 4. Register the server

Always use absolute paths. Show the user the exact file content or command first; run it after their yes. In
BashCutPro's Agent panel, skip this step (step 0).

**Claude Code with this kit's plugin** (macOS, Linux). The plugin already declares a `bashcutpro` server; its
launcher (`scripts/bashcutpro-mcp.sh`) reads `~/.config/bashcutpro/mcp.env` (`$XDG_CONFIG_HOME` if set), so
write the binary and mode there, one `NAME=value` per line (no quotes needed, no comments after a value):

```sh
BASHCUTPRO_CLI=/abs/path/BashCutPro/target/release/bashcutpro-cli
BASHCUTPRO_PROJECT=/abs/path/p.fcproj
```

The mode line is one of `BASHCUTPRO_PROJECT=…`, `BASHCUTPRO_DEMO=1` or `BASHCUTPRO_BRIDGE=127.0.0.1:9876`;
keep one: the bridge wins over a project, a project over the demo. `BASHCUTPRO_DATA_DIR` sets
`--data-dir`. The same names in the environment override the file. Then the user reconnects the server
(`/mcp` › bashcutpro › Reconnect) or restarts Claude Code. With `bashcutpro-cli` (or `bcpro`) on `PATH` and an
empty headless project wanted, no file is needed.

When BashCutPro's `bashcut-mcp` is built (`cargo build --release -p bashcut-mcp`, next to `bashcutpro-cli`, or set
`BASHCUT_MCP`), the launcher runs it instead: with no mode line it reaches the open BashCutPro window by itself (the
channel is on by default, found through `<data dir>/bashcut/automation.json`), else runs headless. A second headless engine on the same project is refused,
and writes outside the project folder and `BASHCUTPRO_ROOTS` are refused. `BASHCUTPRO_NO_LOCK=1` turns it off.

**Claude Code without the plugin, or on Windows.** Register the binary directly, in the user's scope so every
project sees it:

```sh
claude mcp add -s user bashcutpro -- /abs/path/bashcutpro-cli mcp --demo
claude mcp add -s user bashcutpro -- "C:\Program Files\BashCutPro\bashcutpro-cli.exe" mcp --bridge 127.0.0.1:9876
```

The plugin's launcher is a POSIX shell script; if its `bashcutpro` server does not start on Windows, the user
disables it in `/mcp` and keeps the direct entry under another name (`bashcutpro-direct`) so the two do not clash.

**Codex.** On macOS and Linux, from a clone of this kit: `sh scripts/install-codex.sh` links the skills as
`~/.agents/skills/bcp-<name>` and registers the same launcher, which reads the same `mcp.env`. On Windows, copy
each `skills/<name>` folder to `%USERPROFILE%\.agents\skills\bcp-<name>` and register the binary directly:

```sh
codex mcp add bashcutpro -- "C:\Program Files\BashCutPro\bashcutpro-cli.exe" mcp
```

To change modes later, edit `mcp.env` (or remove and re-add the direct entry) and reconnect.

## 5. Check it works

1. `command_list` with `{"filter": "razor"}` returns commands. Without a filter it returns the whole catalogue
   (about a thousand ids), so filter when you only need to know it answers. Then `command_list {"filter":
   "bashcut."}`: BashCutPro's own commands (`bashcut.review.run`, `bashcut.timeline.summary`, `bashcut.batch`,
   `bashcut.profiles.*`, `bashcut.looks.*`, `bashcut.template.*`, `bashcut.audio.*`) that the skills use first; an
   older engine (`filmcraft-cli`) has none, and the skills fall back to plain commands. `transcript.models` says
   whether Whisper is in (`available: true`) and which model is installed.
2. `doc_inspect` returns the project tree: the user's project, the demo's bins, or an empty project.
3. Bridge only: `ui_inspect` returns the app's tool, workspace and panels.

Tell the user in one or two sentences what is connected (headless with which project, or the open app) and what
they can ask for next.

| Symptom | Cause and fix |
|---|---|
| `bashcutpro-cli not found: install BashCutPro or set BASHCUTPRO_CLI` from the launcher (also the JSON-RPC error `/mcp` shows) | no binary found: set `BASHCUTPRO_CLI` in `mcp.env` (step 4) |
| The server starts the desktop app, or exits at once with the app's usage | `BASHCUTPRO_CLI` (or the direct entry) names `bashcutpro`, the desktop app: point it at `bashcutpro-cli` (or `bcpro`) instead |
| Tools missing, server "failed" | the user runs the registered command by hand in a terminal; it should wait silently for input. An error there names the problem |
| Agent panel: tools missing | the app's control channel is off: the user turns on "Allow AI agents to control BashCutPro" (Agent section) or unsets `BASHCUT_CONTROL=0`, then sends the prompt again |
| Bridge: connection refused | the app is not running, or the user turned off "Allow AI agents to control BashCutPro" (Agent section) or set `BASHCUT_CONTROL=0`; the port is in `<data dir>/bashcut/automation.json` |
| A command or tool call is denied | not a bug to work around: tell the user what was denied and the command to run in their terminal (step 0) |
| Plugin server shows `failed` in `system/init` or `/mcp` | the launcher answers every request with a JSON-RPC error `bashcutpro-cli not found: ...` (also on its stderr) when it finds no CLI: install one (step 2) or set `BASHCUTPRO_CLI` in `mcp.env`; a path in `BASHCUTPRO_CLI` that does not exist counts as not found |
| Not signed in to Claude Code (`authentication_failed`) | the user runs `claude` in a terminal and types `/login`; never handle credentials |
| Exit 2 at start | an option the server does not take (only `--project`, `--demo`, `--data-dir`, `--bridge`) |
| `isError` from `command_run` | the engine's message; read it, then `command_list {"filter": "<id>"}` for the command's params |

## Kit and engine versions differ

When `command_run` answers "unknown command" for an id a skill names, or `command_list` lacks it, do not try other
ids. Run `command_list` (or `bashcutpro-cli describe <id>`), tell the user the kit and BashCutPro versions differ,
and fix the older side: update BashCutPro, or in the app's Plugins section choose Download kit. Then go on with the
ids the engine lists.
