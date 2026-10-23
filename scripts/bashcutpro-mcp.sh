#!/bin/sh
# Start BashCutPro's MCP server on stdio, for Claude Code (.mcp.json) and Codex.
#
# With `bashcut-mcp` installed (BashCutPro apps/bashcut-mcp, #51) it runs that: it bridges to the open BashCutPro
# window on its own (the window publishes <data dir>/bashcut/automation.json while its control channel runs), else
# starts a headless engine holding the project's engine lock (a second engine on the same .fcproj is refused), and
# refuses writes outside the project folder and BASHCUTPRO_ROOTS. Without it, `bashcutpro-cli mcp` directly.
#
# Settings come from the environment, else from the config file the `setup` skill writes
# (${XDG_CONFIG_HOME:-~/.config}/bashcutpro/mcp.env, plain NAME=value lines); the environment wins.
#   BASHCUTPRO_CLI         the BashCutPro command line (`bashcutpro-cli`, alias `bcpro`); else BASHCUT_FILMCRAFT_CLI,
#                          FILMCRAFT_CLI, else bashcutpro-cli, bcpro, filmcraft-cli on PATH, then the usual install
#                          places (exact names, never plain `bashcutpro`: that is the desktop app)
#   BASHCUTPRO_BRIDGE      host:port of the running app (`bashcutpro --control <port>`): drive it instead of headless
#   BASHCUTPRO_PROJECT     headless: open this .fcproj
#   BASHCUTPRO_DEMO=1      headless: open the demo project (when no project is set)
#   BASHCUTPRO_DATA_DIR    FilmCraft data dir (--data-dir): user presets, and where bashcut-mcp finds the window
#   BASHCUT_MCP            the bashcut-mcp binary; else bashcut-mcp next to the CLI, on PATH, the usual places
#   BASHCUTPRO_ROOTS       more folders agents may write to (path list), read by bashcut-mcp
#   BASHCUTPRO_NO_LOCK=1   skip bashcut-mcp: plain bashcutpro-cli mcp (no window lookup, lock or write guard)
# Neither bridge, project nor demo: bashcut-mcp looks for the window, else a headless session with an empty project.

CONFIG="${BASHCUTPRO_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/bashcutpro/mcp.env}"
if [ -f "$CONFIG" ]; then
    # Read NAME=value lines without running the file; a value already in the environment is kept.
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            BASHCUTPRO_CLI=*|BASHCUT_FILMCRAFT_CLI=*|FILMCRAFT_CLI=*|BASHCUTPRO_BRIDGE=*|BASHCUTPRO_PROJECT=*|BASHCUTPRO_DEMO=*|BASHCUTPRO_DATA_DIR=*) ;;
            BASHCUT_MCP=*|BASHCUTPRO_ROOTS=*|BASHCUTPRO_NO_LOCK=*) ;;
            *) continue;;
        esac
        name="${line%%=*}"
        value="${line#*=}"
        value="${value#\"}"; value="${value%\"}"
        eval "current=\${$name-}"
        [ -n "$current" ] || eval "$name=\$value"
    done < "$CONFIG"
fi

cli=""
# bashcutpro-cli, then its alias bcpro, then upstream's filmcraft-cli (an older or upstream build), by exact name;
# never plain bashcutpro: that is the desktop app (/usr/bin/bashcutpro on Linux)
for candidate in "${BASHCUTPRO_CLI-}" "${BASHCUT_FILMCRAFT_CLI-}" "${FILMCRAFT_CLI-}" \
    "$(command -v bashcutpro-cli 2>/dev/null)" "$(command -v bcpro 2>/dev/null)" \
    "$(command -v filmcraft-cli 2>/dev/null)" \
    "$HOME/.local/bin/bashcutpro-cli" "/usr/local/bin/bashcutpro-cli" "/opt/homebrew/bin/bashcutpro-cli" \
    "/usr/bin/bashcutpro-cli" "/Applications/BashCutPro.app/Contents/MacOS/bashcutpro-cli" \
    "$HOME/.local/bin/bcpro" "/usr/local/bin/bcpro" "/opt/homebrew/bin/bcpro" "/usr/bin/bcpro" \
    "$HOME/.local/bin/filmcraft-cli" "/usr/local/bin/filmcraft-cli" "/opt/homebrew/bin/filmcraft-cli" \
    "/usr/bin/filmcraft-cli"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        cli="$candidate"
        break
    fi
done
if [ -z "$cli" ]; then
    echo "bashcutpro-cli (or bcpro, filmcraft-cli) not found. Run the kit's setup skill, or set BASHCUTPRO_CLI in $CONFIG" >&2
    echo "(build it with: cargo build --release -p bashcutpro-cli, in a BashCutPro checkout)." >&2
    exit 1
fi

# bashcut-mcp, unless asked not to, or for the demo (it has no demo mode)
mcp=""
if [ "${BASHCUTPRO_NO_LOCK-}" != "1" ] && { [ -z "${BASHCUTPRO_DEMO-}" ] || [ -n "${BASHCUTPRO_PROJECT-}${BASHCUTPRO_BRIDGE-}" ]; }; then
    for candidate in "${BASHCUT_MCP-}" "$(dirname "$cli")/bashcut-mcp" "$(command -v bashcut-mcp 2>/dev/null)" \
        "$HOME/.local/bin/bashcut-mcp" "/usr/local/bin/bashcut-mcp" "/opt/homebrew/bin/bashcut-mcp"; do
        if [ -n "$candidate" ] && [ -x "$candidate" ]; then
            mcp="$candidate"
            break
        fi
    done
fi
if [ -n "$mcp" ]; then
    export BASHCUTPRO_ROOTS="${BASHCUTPRO_ROOTS-}"
    set -- --cli "$cli"
    [ -n "${BASHCUTPRO_DATA_DIR-}" ] && set -- "$@" --data-dir "$BASHCUTPRO_DATA_DIR"
    [ -n "${BASHCUTPRO_BRIDGE-}" ] && set -- "$@" --bridge "$BASHCUTPRO_BRIDGE"
    [ -n "${BASHCUTPRO_PROJECT-}" ] && set -- "$@" --project "$BASHCUTPRO_PROJECT"
    exec "$mcp" "$@"
fi

if [ -n "${BASHCUTPRO_BRIDGE-}" ]; then
    exec "$cli" mcp --bridge "$BASHCUTPRO_BRIDGE"
fi
set -- mcp
[ -n "${BASHCUTPRO_DATA_DIR-}" ] && set -- "$@" --data-dir "$BASHCUTPRO_DATA_DIR"
if [ -n "${BASHCUTPRO_PROJECT-}" ]; then
    set -- "$@" --project "$BASHCUTPRO_PROJECT"
elif [ "${BASHCUTPRO_DEMO-}" = "1" ]; then
    set -- "$@" --demo
fi
exec "$cli" "$@"
