#!/usr/bin/env python3
"""Refresh scripts/commands.json from a build's own `command_list` (the authority; refresh_bashcut.py only reads source).

  python3 scripts/refresh_commands.py --cli /abs/BashCutPro/target/debug/filmcraft-cli [--features "default"] [--dry-run]

Starts `<cli> mcp --demo`, calls `tools/list` and `tools/call command_list {}`, and rewrites `commands` (id, label, menu,
shortcut, params, enabled), `count`, `mcpTools` and the provenance lines. The `frontend` list (window-only ids) and
`pending` are kept as they are: a headless command_list does not have them. Prints what changed. Standard library only.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "scripts", "commands.json")
FIELDS = ("id", "label", "menu", "shortcut", "params", "enabled")


def mcp_session(cli):
    proc = subprocess.Popen([cli, "mcp", "--demo"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    state = {"n": 0}

    def call(method, params=None):
        state["n"] += 1
        msg = {"jsonrpc": "2.0", "id": state["n"], "method": method, "params": params or {}}
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        while True:
            line = proc.stdout.readline()
            if not line:
                sys.exit(f"{cli} mcp closed before answering {method}")
            reply = json.loads(line)
            if reply.get("id") == state["n"]:
                if "error" in reply:
                    sys.exit(f"{method}: {reply['error']}")
                return reply["result"]

    call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "refresh_commands", "version": "1"}})
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()
    tools = sorted(t["name"] for t in call("tools/list")["tools"])
    listed = call("tools/call", {"name": "command_list", "arguments": {}})
    proc.stdin.close()
    proc.wait(timeout=30)
    if listed.get("isError"):
        sys.exit(f"command_list failed: {listed}")
    return tools, json.loads(listed["content"][0]["text"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cli", required=True, help="the bashcutpro (or filmcraft-cli) binary of a BashCutPro build")
    ap.add_argument("--features", default="default features", help="how that build was made, for the provenance line")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    version = subprocess.run([a.cli, "--version"], capture_output=True, text=True).stdout.strip() or "filmcraft-cli"
    tools, real = mcp_session(a.cli)
    with open(CATALOGUE, encoding="utf-8") as f:
        cat = json.load(f)
    old = {c["id"]: c for c in cat["commands"]}
    new = [{k: c.get(k) for k in FIELDS} for c in real]
    changes = []
    for c in new:
        before = old.get(c["id"])
        if before is None:
            changes.append(f"+ {c['id']}")
        elif any(before.get(k) != c[k] for k in FIELDS):
            changes.append(f"~ {c['id']}")
    ids = {c["id"] for c in new}
    changes += [f"- {cid}" for cid in sorted(set(old) - ids)]
    if tools != cat.get("mcpTools"):
        changes.append(f"~ mcpTools: {tools}")
    cat["source"] = f"{version} mcp --demo, tools/call command_list {{}} ({a.features})"
    cat["generated"] = datetime.date.today().isoformat()
    cat["bashcut"] = "bashcut.* engine ids from the same build's command_list (scripts/refresh_commands.py)"
    cat["mcpTools"] = tools
    cat["commands"] = new
    cat["count"] = len(new)
    print("\n".join(changes) or "no change")
    print(f"commands: {cat['count']}, mcp tools: {len(tools)}")
    if not a.dry_run:
        with open(CATALOGUE, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=1, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
