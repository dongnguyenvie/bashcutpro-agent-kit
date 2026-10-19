#!/usr/bin/env python3
"""Refresh BashCutPro's own ids in scripts/commands.json from a BashCutPro checkout, without a build.

  python3 scripts/refresh_bashcut.py --repo ../BashCutPro [--ref origin/main] [--dry-run]

- Engine commands: every `bashcut.*` CommandSpec in `crates/engine/src/bashcut/*.rs` (`id: "…"`, `id: CMD` with
  `const CMD: &str = "…"`, or a helper call `query("…", "label", r#"params"#, …)`), with its label and params string.
  New ids are added, changed labels / params updated, ids gone from the source removed.
- Frontend commands (the open window only, reached in bridge mode): `bashcut.ui.*`, `bashcut.agent.*`,
  `bashcut.batch.*`, `bashcut.plugins.*`, `bashcut.palette.*` from `crates/ui-egui/src/bashcut_ui/*.rs`, kept in the
  separate `frontend` list (they are not in a headless `command_list`).

Prints what changed. A build's `command_list` stays the authority: refresh from it in the build pass. Standard
library only.
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(ROOT, "scripts", "commands.json")
RAW = r'r(#+)"(.*?)"\1'


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def files(repo, ref, folder):
    names = git(repo, "ls-tree", "--name-only", f"{ref}:{folder}").split()
    out = {}
    for n in names:
        if n.endswith(".rs") and not n.endswith("tests.rs"):
            out[n] = git(repo, "show", f"{ref}:{folder}/{n}")
    return out


def engine_specs(sources):
    specs = {}
    for text in sources.values():
        consts = dict(re.findall(r'const ([A-Z_]+): &str = "(bashcut\.[A-Za-z0-9.]+)"', text))
        for m in re.finditer(r"CommandSpec \{(.*?)\n\s*\}", text, re.S):
            body = m.group(1)
            idm = re.search(r'\bid: (?:"(bashcut\.[A-Za-z0-9.]+)"|([A-Z_]+)),', body)
            if not idm:
                continue
            cid = idm.group(1) or consts.get(idm.group(2) or "")
            label = re.search(r'\blabel: "([^"]*)"', body)
            params = re.search(r"\bparams: " + RAW, body, re.S)
            if cid and label:
                specs[cid] = {"label": label.group(1), "params": params.group(2) if params else "{}"}
        # helper constructors: name("bashcut.x.y", "Label", r#"params"#, …)
        for m in re.finditer(r'\b[a-z_]+\(\s*"(bashcut\.[A-Za-z0-9.]+)",\s*"([^"]+)",\s*r(#+)"(.*?)"\3', text, re.S):
            specs.setdefault(m.group(1), {"label": m.group(2), "params": m.group(4)})
    return specs


def frontend_ids(sources):
    ids = {}
    for text in sources.values():
        for m in re.finditer(r'CommandInfo::new\(\s*"(bashcut\.[A-Za-z0-9.]+)",\s*"([^"]+)"', text):
            ids[m.group(1)] = m.group(2)
        for m in re.finditer(r'\[(.*?)\]\s*\.into_iter\(\)\s*\.map\(\|\(id, label\)\| CommandInfo::new\(&format!\("(bashcut\.[a-z.]+)\{id\}"', text, re.S):
            for a, b in re.findall(r'\("([A-Za-z.]+)",\s*"([^"]+)"\)', m.group(1)):
                ids[m.group(2) + a] = b
        sections = re.search(r"pub const SECTIONS.*?\n\];", text, re.S)
        if sections:
            for sid, title in re.findall(r'id: "([a-z]+)",\s*title: "([^"]+)"', sections.group(0)):
                ids[f"bashcut.ui.show.{sid}"] = title
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", required=True, help="a BashCutPro checkout")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = git(a.repo, "rev-parse", "--short", a.ref).strip()
    engine = engine_specs(files(a.repo, a.ref, "crates/engine/src/bashcut"))
    front = frontend_ids(files(a.repo, a.ref, "crates/ui-egui/src/bashcut_ui"))
    if not engine:
        sys.exit("no bashcut.* engine commands found: wrong --repo or --ref?")

    cat = json.load(open(CATALOGUE, encoding="utf-8"))
    old = {c["id"]: c for c in cat["commands"] if c["id"].startswith("bashcut.")}
    changes = []
    for cid in sorted(set(old) - set(engine)):
        changes.append(f"- {cid} (gone from the source)")
    for cid, spec in sorted(engine.items()):
        if cid not in old:
            changes.append(f"+ {cid}")
        elif (old[cid]["label"], old[cid]["params"]) != (spec["label"], spec["params"]):
            changes.append(f"~ {cid}")
    rest = [c for c in cat["commands"] if not c["id"].startswith("bashcut.")]
    ours = [{"id": cid, "label": s["label"], "menu": old.get(cid, {}).get("menu", []), "shortcut": old.get(cid, {}).get("shortcut"),
             "params": s["params"], "enabled": old.get(cid, {}).get("enabled", True)} for cid, s in sorted(engine.items())]
    cat["commands"] = rest + ours
    cat["count"] = len(cat["commands"])
    cat["bashcut"] = (f"bashcut.* engine ids read from BashCutPro {a.ref} {sha} (crates/engine/src/bashcut/) by "
                      "scripts/refresh_bashcut.py, not yet from a build's command_list; refresh from a build in the build pass")
    old_front = {f["id"] for f in (cat.get("frontend") or {}).get("ids", [])}
    for fid in sorted(set(front) - old_front):
        changes.append(f"+ {fid} (frontend)")
    for fid in sorted(old_front - set(front)):
        changes.append(f"- {fid} (frontend, gone)")
    cat["frontend"] = {
        "note": (f"BashCutPro's window commands (bashcut_ui, {a.ref} {sha}): only the open app has them, through the MCP "
                 "bridge (command_run in bridge mode, or ui_control engine.execute); a headless command_list does not list them"),
        "ids": [{"id": fid, "label": front[fid]} for fid in sorted(front)],
    }
    print("\n".join(changes) or "no change")
    print(f"engine bashcut.* ids: {len(engine)}, frontend ids: {len(front)}, commands: {cat['count']}")
    if not a.dry_run:
        with open(CATALOGUE, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=1, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
