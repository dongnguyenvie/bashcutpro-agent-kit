---
name: setup
description: Connect Claude Code or Codex to BashCutPro: get filmcraft-cli (source build or release) on macOS, Windows or Linux, register its MCP server headless (a project or the demo) or bridged to the running app (--control), and check command_list answers. Use when the BashCutPro tools are missing or fail to start. Triggers: "/bcp:setup", "setup BashCutPro", "connect BashCutPro", "install filmcraft-cli", "MCP not connected", "cài BashCutPro", "kết nối BashCutPro".
---

# Setting up BashCutPro's MCP server

BashCutPro is driven through one MCP server, `filmcraft-cli mcp` (stdio). Every later skill assumes its tools
answer: `command_list`, `command_run`, `command_batch`, `doc_inspect`, `render_frame`. This skill gets the binary,
registers the server and proves it works. It changes nothing in the user's project.

Plain words: the user may not be technical. Ask before anything that takes long or installs software (a Rust
toolchain, a source build of several minutes, a download), and never remove or rewrite MCP servers that are not
`bashcutpro`.

## 1. Is it already working?

Call `command_list` with `{"filter": "razor"}`. A list of commands with ids such as `timeline.razor` means the
server is up: skip to step 5 to say which mode it runs in. Otherwise note the error (tool missing, server failed
to start, connection refused) and go on.

## 2. Get `filmcraft-cli`

Look for one first: `FILMCRAFT_CLI` in the environment, `filmcraft-cli` on `PATH`, a BashCutPro checkout's
`target/release/filmcraft-cli` (`.exe` on Windows), then the install places below. Check a candidate with
`filmcraft-cli commands razor`: it prints JSON and exits 0.

**From source** (any OS; needs Rust from rustup.rs and a BashCutPro checkout):

```sh
git clone https://github.com/dongnguyenvie/BashCutPro && cd BashCutPro
cargo build --release -p filmcraft-cli              # add -p filmcraft for the desktop app (bridge mode)
```

The binary is `target/release/filmcraft-cli`. A first build takes several minutes; say so before starting it.

**From a release.** Use a [BashCutPro release](https://github.com/dongnguyenvie/BashCutPro/releases) when one is
published. Until then an upstream [FilmCraft release](https://github.com/storytold/filmcraft/releases) runs the
same server without BashCutPro's own additions; tell the user which one they get.

| OS | Where the CLI is after installing |
|---|---|
| Windows (MSI) | `C:\Program Files\FilmCraft\filmcraft-cli.exe` by default, not on `PATH` |
| Linux (deb, rpm) | `/usr/bin/filmcraft-cli` |
| macOS | the separate `filmcraft-cli-<version>-macos-<arch>.zip` asset (the `.app` holds only the desktop app); unzip it to `~/.local/bin` or another folder on `PATH` |

If macOS refuses to open a downloaded binary, the user can allow it in System Settings › Privacy & Security.

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
filmcraft --control 9876          # or FILMCRAFT_CONTROL_PORT=9876; from source: target/release/filmcraft
```

Default to headless with the user's project when they name one, the bridge when they want to watch the app.

## 4. Register the server

Always use absolute paths.

**Claude Code with this kit's plugin** (macOS, Linux). The plugin already declares a `bashcutpro` server; its
launcher (`scripts/bashcutpro-mcp.sh`) reads `~/.config/bashcutpro/mcp.env` (`$XDG_CONFIG_HOME` if set), so
write the binary and mode there, one `NAME=value` per line (no quotes needed, no comments after a value):

```sh
FILMCRAFT_CLI=/abs/path/BashCutPro/target/release/filmcraft-cli
BASHCUTPRO_PROJECT=/abs/path/p.fcproj
```

The mode line is one of `BASHCUTPRO_PROJECT=…`, `BASHCUTPRO_DEMO=1` or `BASHCUTPRO_BRIDGE=127.0.0.1:9876`;
keep one: the bridge wins over a project, a project over the demo. `BASHCUTPRO_DATA_DIR` sets
`--data-dir`. The same names in the environment override the file. Then the user reconnects the server
(`/mcp` › bashcutpro › Reconnect) or restarts Claude Code. With `filmcraft-cli` on `PATH` and an empty
headless project wanted, no file is needed.

When BashCutPro's `bashcut-mcp` is built (`cargo build --release -p bashcut-mcp`, next to `filmcraft-cli`, or set
`BASHCUT_MCP`), the launcher runs it instead: with no mode line it reaches the open BashCutPro window by itself (the
app started with `--control <port>`), else runs headless. A second headless engine on the same project is refused,
and writes outside the project folder and `BASHCUTPRO_ROOTS` are refused. `BASHCUTPRO_NO_LOCK=1` turns it off.

**Claude Code without the plugin, or on Windows.** Register the binary directly, in the user's scope so every
project sees it:

```sh
claude mcp add -s user bashcutpro -- /abs/path/filmcraft-cli mcp --demo
claude mcp add -s user bashcutpro -- "C:\Program Files\FilmCraft\filmcraft-cli.exe" mcp --bridge 127.0.0.1:9876
```

The plugin's launcher is a POSIX shell script; if its `bashcutpro` server does not start on Windows, disable it
in `/mcp` and use the direct entry under another name (`bashcutpro-direct`) so the two do not clash.

**Codex.** On macOS and Linux, from a clone of this kit: `sh scripts/install-codex.sh` links the skills as
`~/.agents/skills/bcp-<name>` and registers the same launcher, which reads the same `mcp.env`. On Windows, copy
each `skills/<name>` folder to `%USERPROFILE%\.agents\skills\bcp-<name>` and register the binary directly:

```sh
codex mcp add bashcutpro -- "C:\Program Files\FilmCraft\filmcraft-cli.exe" mcp
```

To change modes later, edit `mcp.env` (or remove and re-add the direct entry) and reconnect.

## 5. Check it works

1. `command_list` with `{"filter": "razor"}` returns commands. Without a filter it returns the whole catalogue
   (about a thousand ids), so filter when you only need to know it answers.
2. `doc_inspect` returns the project tree: the user's project, the demo's bins, or an empty project.
3. Bridge only: `ui_inspect` returns the app's tool, workspace and panels.

Tell the user in one or two sentences what is connected (headless with which project, or the open app) and what
they can ask for next.

| Symptom | Cause and fix |
|---|---|
| `filmcraft-cli not found` from the launcher | no binary found: set `FILMCRAFT_CLI` in `mcp.env` (step 4) |
| Tools missing, server "failed" | run the registered command by hand in a terminal; it should wait silently for input. An error there names the problem |
| Bridge: connection refused | the app is not running with `--control`, or on another port; start it as in step 3 |
| Exit 2 at start | an option the server does not take (only `--project`, `--demo`, `--data-dir`, `--bridge`) |
| `isError` from `command_run` | the engine's message; read it, then `command_list {"filter": "<id>"}` for the command's params |
