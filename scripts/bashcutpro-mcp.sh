#!/bin/sh
# Start BashCutPro's MCP server (`filmcraft-cli mcp`) on stdio, for Claude Code (.mcp.json) and Codex.
#
# Settings come from the environment, else from the config file the `setup` skill writes
# (${XDG_CONFIG_HOME:-~/.config}/bashcutpro/mcp.env, plain NAME=value lines); the environment wins.
#   FILMCRAFT_CLI          the filmcraft-cli binary; else filmcraft-cli on PATH, then the usual install places
#   BASHCUTPRO_BRIDGE      host:port of the running app (`filmcraft --control <port>`): drive it instead of headless
#   BASHCUTPRO_PROJECT     headless: open this .fcproj
#   BASHCUTPRO_DEMO=1      headless: open the demo project (when no project is set)
#   BASHCUTPRO_DATA_DIR    headless: user presets folder (--data-dir)
# Neither bridge, project nor demo: a headless session with an empty project.

CONFIG="${BASHCUTPRO_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/bashcutpro/mcp.env}"
if [ -f "$CONFIG" ]; then
    # Read NAME=value lines without running the file; a value already in the environment is kept.
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            FILMCRAFT_CLI=*|BASHCUTPRO_BRIDGE=*|BASHCUTPRO_PROJECT=*|BASHCUTPRO_DEMO=*|BASHCUTPRO_DATA_DIR=*) ;;
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
for candidate in "${FILMCRAFT_CLI-}" "$(command -v filmcraft-cli 2>/dev/null)" \
    "$HOME/.local/bin/filmcraft-cli" "/usr/local/bin/filmcraft-cli" "/opt/homebrew/bin/filmcraft-cli" \
    "/usr/bin/filmcraft-cli"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        cli="$candidate"
        break
    fi
done
if [ -z "$cli" ]; then
    echo "filmcraft-cli not found. Run the kit's setup skill, or set FILMCRAFT_CLI in $CONFIG" >&2
    echo "(build it with: cargo build --release -p filmcraft-cli, in a BashCutPro checkout)." >&2
    exit 1
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
