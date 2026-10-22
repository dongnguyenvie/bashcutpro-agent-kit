---
name: setup
description: Connect Claude Code or Codex to BashCutPro: get the bashcutpro command line (source build or release) on macOS, Windows or Linux, register its MCP server headless (a project or the demo) or bridged to the running app (--control), and check command_list answers. Use when the BashCutPro tools are missing or fail to start. Triggers: "/bcp:setup", "setup BashCutPro", "connect BashCutPro", "install bashcutpro", "install filmcraft-cli", "MCP not connected", "cài BashCutPro", "kết nối BashCutPro".
---

# Setting up BashCutPro's MCP server

BashCutPro is driven through one MCP server, `bashcutpro mcp` (stdio). Every later skill assumes its tools
answer: `command_list`, `command_run`, `command_batch`, `doc_inspect`, `render_frame`. This skill gets the binary,
registers the server and proves it works. It changes nothing in the user's project.

Plain words: the user may not be technical. Ask before anything that takes long or installs software (a Rust
toolchain, a source build of several minutes, a download), and never remove or rewrite MCP servers that are not
`bashcutpro`.

## 1. Is it already working?

Call `command_list` with `{"filter": "razor"}`. A list of commands with ids such as `timeline.razor` means the
server is up: skip to step 5 to say which mode it runs in. Otherwise note the error (tool missing, server failed
to start, connection refused) and go on.

## 2. Get `bashcutpro`

`bashcutpro` (short name `bcpro`) is BashCutPro's command line. It runs the engine binary `filmcraft-cli`, which
always sits beside it, with the same arguments and exit code; a plain `filmcraft-cli` works too (an older build,
or upstream FilmCraft). Look for one first: `BASHCUTPRO_CLI` or `FILMCRAFT_CLI` in the environment, `bashcutpro`
then `filmcraft-cli` on `PATH`, a BashCutPro checkout's `target/release/bashcutpro` (`.exe` on Windows), then the
install places below. Check a candidate with `bashcutpro commands razor`: it prints JSON and exits 0.

**From source** (any OS; needs Rust from rustup.rs and a BashCutPro checkout):

```sh
git clone https://github.com/dongnguyenvie/BashCutPro && cd BashCutPro
cargo build --release -p bashcut-cli -p filmcraft-cli --features filmcraft-cli/whisper
# add -p filmcraft (and --features filmcraft/whisper) for the desktop app (bridge mode)
```

`--features filmcraft-cli/whisper` adds speech to text (`bashcut.transcript.generate`): captions, rough cuts by
quote and the review's cut-inside-a-word check all need words. Without it, words come from an outside transcriber
(bcp:footage-survey).

The binary is `target/release/bashcutpro` (it needs `target/release/filmcraft-cli` beside it). A first build takes several minutes; say so before starting it.

**From a release.** Use a [BashCutPro release](https://github.com/dongnguyenvie/BashCutPro/releases) when one is
published. Until then an upstream [FilmCraft release](https://github.com/storytold/filmcraft/releases) runs the
same server without BashCutPro's own additions; tell the user which one they get.

| OS | Where the CLI is after installing |
|---|---|
| Windows (MSI) | `C:\Program Files\BashCutPro\bashcutpro.exe` by default, not on `PATH` (FilmCraft: `C:\Program Files\FilmCraft\filmcraft-cli.exe`) |
| Linux (deb, rpm) | `/usr/bin/bashcutpro` (FilmCraft: `/usr/bin/filmcraft-cli`) |
| macOS | the separate `bashcutpro-cli-<version>-macos-<arch>.zip` asset (FilmCraft: `filmcraft-cli-…`; the `.app` holds the desktop app); unzip it to `~/.local/bin` or another folder on `PATH`, keeping `bashcutpro` and `filmcraft-cli` together |

If macOS refuses to open a downloaded binary, the user can allow it in System Settings › Privacy & Security. 

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
the app must be running with the control channel on the same port, which listens on `127.0.0.1` only:

```sh
filmcraft --control 9876          # BashCutPro serves 127.0.0.1:9876 (or a free port) by default; read <data dir>/bashcut/automation.json
```

Default to headless with the user's project when they name one, the bridge when they want to watch the app.

## 4. Register the server

Always use absolute paths.

**Claude Code with this kit's plugin** (macOS, Linux). The plugin already declares a `bashcutpro` server; its
launcher (`scripts/bashcutpro-mcp.sh`) reads `~/.config/bashcutpro/mcp.env` (`$XDG_CONFIG_HOME` if set), so
write the binary and mode there, one `NAME=value` per line (no quotes needed, no comments after a value):

```sh
BASHCUTPRO_CLI=/abs/path/BashCutPro/target/release/bashcutpro
BASHCUTPRO_PROJECT=/abs/path/p.fcproj
```

The mode line is one of `BASHCUTPRO_PROJECT=…`, `BASHCUTPRO_DEMO=1` or `BASHCUTPRO_BRIDGE=127.0.0.1:9876`;
keep one: the bridge wins over a project, a project over the demo. `BASHCUTPRO_DATA_DIR` sets
`--data-dir`. The same names in the environment override the file. Then the user reconnects the server
(`/mcp` › bashcutpro › Reconnect) or restarts Claude Code. With `bashcutpro` (or `filmcraft-cli`) on `PATH` and an empty
headless project wanted, no file is needed.

When BashCutPro's `bashcut-mcp` is built (`cargo build --release -p bashcut-mcp`, next to `bashcutpro`, or set
`BASHCUT_MCP`), the launcher runs it instead: with no mode line it reaches the open BashCutPro window by itself (the
channel is on by default, found through `<data dir>/bashcut/automation.json`), else runs headless. A second headless engine on the same project is refused,
and writes outside the project folder and `BASHCUTPRO_ROOTS` are refused. `BASHCUTPRO_NO_LOCK=1` turns it off.

**Claude Code without the plugin, or on Windows.** Register the binary directly, in the user's scope so every
project sees it:

```sh
claude mcp add -s user bashcutpro -- /abs/path/bashcutpro mcp --demo
claude mcp add -s user bashcutpro -- "C:\Program Files\BashCutPro\bashcutpro.exe" mcp --bridge 127.0.0.1:9876
```

The plugin's launcher is a POSIX shell script; if its `bashcutpro` server does not start on Windows, disable it
in `/mcp` and use the direct entry under another name (`bashcutpro-direct`) so the two do not clash.

**Codex.** On macOS and Linux, from a clone of this kit: `sh scripts/install-codex.sh` links the skills as
`~/.agents/skills/bcp-<name>` and registers the same launcher, which reads the same `mcp.env`. On Windows, copy
each `skills/<name>` folder to `%USERPROFILE%\.agents\skills\bcp-<name>` and register the binary directly:

```sh
codex mcp add bashcutpro -- "C:\Program Files\BashCutPro\bashcutpro.exe" mcp
```

To change modes later, edit `mcp.env` (or remove and re-add the direct entry) and reconnect.

## 5. Check it works

1. `command_list` with `{"filter": "razor"}` returns commands. Without a filter it returns the whole catalogue
   (about a thousand ids), so filter when you only need to know it answers. Then `command_list {"filter":
   "bashcut."}`: BashCutPro's own commands (`bashcut.review.run`, `bashcut.timeline.summary`, `bashcut.batch`,
   `bashcut.profiles.*`, `bashcut.looks.*`, `bashcut.template.*`, `bashcut.audio.*`) that the skills use first; an
   upstream FilmCraft binary has none, and the skills fall back to plain commands. `transcript.models` says whether
   Whisper is in (`available: true`) and which model is installed.
2. `doc_inspect` returns the project tree: the user's project, the demo's bins, or an empty project.
3. Bridge only: `ui_inspect` returns the app's tool, workspace and panels.

Tell the user in one or two sentences what is connected (headless with which project, or the open app) and what
they can ask for next.

| Symptom | Cause and fix |
|---|---|
| `bashcutpro (or filmcraft-cli) not found` from the launcher | no binary found: set `BASHCUTPRO_CLI` in `mcp.env` (step 4) |
| `bashcutpro: filmcraft-cli.exe was not found next to this program or on PATH` | `bashcutpro` was copied without the engine: keep `filmcraft-cli` in the same folder |
| Tools missing, server "failed" | run the registered command by hand in a terminal; it should wait silently for input. An error there names the problem |
| Bridge: connection refused | the app is not running, or the user turned off "Allow AI agents to control BashCutPro" (Agent section) or set `BASHCUT_CONTROL=0`; the port is in `<data dir>/bashcut/automation.json` |
| Exit 2 at start | an option the server does not take (only `--project`, `--demo`, `--data-dir`, `--bridge`) |
| `isError` from `command_run` | the engine's message; read it, then `command_list {"filter": "<id>"}` for the command's params |
