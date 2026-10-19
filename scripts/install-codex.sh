#!/bin/sh
# Make this kit available to Codex (macOS, Linux): link each skill into ~/.agents/skills as bcp-<name> and register
# BashCutPro's MCP server as `bashcutpro` (scripts/bashcutpro-mcp.sh). Run again after moving the kit or adding a
# skill. --uninstall removes the links and the MCP entry. Windows: see the setup skill.
set -e
KIT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
PREFIX="bcp-"
mkdir -p "$DEST"

# Remove bcp-<name> links into this kit that are no longer a skill (all of them on --uninstall), and dangling ones.
for target in "$DEST"/"$PREFIX"*; do
    [ -L "$target" ] || continue
    link="$(readlink "$target")"
    name="$(basename "$target")"
    if [ -e "$target" ]; then
        case "$link" in "$KIT"/*) ;; *) continue;; esac
        [ "$1" != "--uninstall" ] && [ -f "$KIT/skills/${name#"$PREFIX"}/SKILL.md" ] && continue
    fi
    rm "$target"
    echo "removed $name"
done

[ "$1" = "--uninstall" ] || for dir in "$KIT"/skills/*/; do
    [ -f "$dir/SKILL.md" ] || continue
    name="$PREFIX$(basename "$dir")"
    target="$DEST/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
        echo "skip $name: $target exists and is not a link from this kit" >&2
        continue
    fi
    ln -sfn "${dir%/}" "$target"
    echo "linked $name"
done

if command -v codex >/dev/null 2>&1; then
    codex mcp remove bashcutpro >/dev/null 2>&1 || true
    if [ "$1" != "--uninstall" ]; then
        codex mcp add bashcutpro -- "$KIT/scripts/bashcutpro-mcp.sh"
        echo "registered MCP server 'bashcutpro'"
    fi
else
    echo "codex not found: add the MCP server later with" >&2
    echo "  codex mcp add bashcutpro -- \"$KIT/scripts/bashcutpro-mcp.sh\"" >&2
fi
