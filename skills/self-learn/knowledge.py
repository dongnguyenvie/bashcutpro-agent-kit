#!/usr/bin/env python3
"""What the kit learns, kept as plain files: lessons, the user's preferences, project facts, proposed skill changes.

    knowledge.py intake --project P.fcproj [--tags captions,audio]     # what to know before an edit (prints text)
    knowledge.py add-lesson TITLE --symptom S --cause C --fix F [--tags a,b] [--evidence "quote"] [--check Q]
                 [--status active|proposed] [--project P]
    knowledge.py lessons [--tag T] [--query Q] [--status S] [--all]
    knowledge.py update-lesson ID [--seen] [--status S] [--fix F] [--check Q] [--evidence "quote"] [--tags a,b] [--project P]
    knowledge.py remove-lesson ID
    knowledge.py set-pref KEY VALUE [--words "the user's words"] | set-pref KEY --remove ;  prefs
    knowledge.py set-fact KEY VALUE --project P | set-fact KEY --remove --project P ;  facts --project P
    knowledge.py propose SKILL FILE --summary S --reason R ;  proposals
    knowledge.py record-correction TEXT [--project P] ;  corrections [--clear]
    knowledge.py export [--out FILE]
    knowledge.py hook correction|after-compact     # Claude Code hooks (hooks/hooks.json), on only with the setting

Global store: `<data dir>/bashcut/knowledge/` (older engine name FilmCraft: FILMCRAFT_DATA_DIR, else ~/Library/Application
Support/FilmCraft, %APPDATA%\\FilmCraft, $XDG_DATA_HOME/filmcraft or ~/.local/share/filmcraft; BASHCUT_KNOWLEDGE_DIR
overrides): `lessons.jsonl` (one lesson per line), `prefs.json` ({key: {value, words, updated}}), `skills/` (proposed
skill changes, never applied by this script), `corrections.jsonl` (lesson candidates the hook kept). Per project:
`<name>.fcproj.bashcut/facts.json` next to the project file. Commands other than intake and hook print JSON.
Standard library only.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys

STATUSES = ("active", "proposed", "disabled")
# A user message that reads like a correction or a "remember this" (English and Vietnamese). Candidates only.
CORRECTION = re.compile(
    r"\b(no|not that|don't|do not|stop|instead|wrong|actually|i said|remember|next time|never|always)\b"
    r"|không phải|đừng|sai rồi|thật ra|nhớ là|lần sau|chứ không|làm lại|không được|đã bảo",
    re.I)


def now():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


# The environment variables that pick the data dir, first set wins (bashcut-dirs' order).
OVERRIDES = ("BASHCUTPRO_DATA_DIR", "FILMCRAFT_DATA_DIR")


def per_user(names, env):
    """`names` (macOS / Windows folder, XDG folder) under this user's data folder."""
    home = env.get("HOME") or os.path.expanduser("~")
    if sys.platform == "darwin":
        return os.path.join(home, "Library", "Application Support", names[0])
    if sys.platform == "win32":
        return os.path.join(env.get("APPDATA") or home, names[0])
    if env.get("XDG_DATA_HOME"):
        return os.path.join(env["XDG_DATA_HOME"], names[1])
    return os.path.join(home, ".local", "share", names[1])


def data_dir(env=None):
    env = os.environ if env is None else env
    for name in OVERRIDES:
        if env.get(name):
            return env[name]
    return per_user(("BashCutPro", "bashcutpro"), env)


def store_dir(env=None):
    env = os.environ if env is None else env
    return env.get("BASHCUT_KNOWLEDGE_DIR") or os.path.join(data_dir(env), "bashcut", "knowledge")


def filmcraft_store_dir(env=None):
    """The older engine's (FilmCraft) knowledge folder, read only; None when a variable picks the folder."""
    env = os.environ if env is None else env
    if env.get("BASHCUT_KNOWLEDGE_DIR") or any(env.get(name) for name in OVERRIDES):
        return None
    return os.path.join(per_user(("FilmCraft", "filmcraft"), env), "bashcut", "knowledge")


def sidecar(project):
    """`<name>.fcproj.bashcut/`, next to the project file."""
    return os.path.abspath(project) + ".bashcut"


def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
    except (OSError, ValueError):
        return default
    return value if isinstance(value, type(default)) else default


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def read_lines(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue  # a damaged line is skipped, the rest still loads
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        pass
    return rows


def write_lines(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def tags_of(text):
    return [t.strip().lower() for t in (text or "").split(",") if t.strip()]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "lesson"


class Store:
    def __init__(self, root=None, fallback=None):
        """`fallback` is read when a file is missing in `root`; by default the older engine's folder for the default root."""
        if root is None:
            root, fallback = store_dir(), filmcraft_store_dir()
        self.root, self.fallback = root, fallback

    def path(self, name):
        return os.path.join(self.root, name)

    def source(self, name):
        """Where `name` is read: ours, else the fallback's copy when ours has none (it is never moved)."""
        ours = self.path(name)
        if self.fallback and not os.path.exists(ours):
            old = os.path.join(self.fallback, name)
            if os.path.exists(old):
                return old
        return ours

    # Lessons ------------------------------------------------------------------------------------------------
    def lessons(self):
        return read_lines(self.source("lessons.jsonl"))

    def add_lesson(self, title, symptom, cause, fix, tags=(), evidence=None, check=None, status="active", project=None):
        if status not in STATUSES:
            raise ValueError("status is one of %s" % ", ".join(STATUSES))
        if not (title and symptom and fix):
            raise ValueError("a lesson needs a title, a symptom and a fix")
        rows = self.lessons()
        ids = {r.get("id") for r in rows}
        base = slug(title)
        lid, n = base, 2
        while lid in ids:
            lid, n = "%s-%d" % (base, n), n + 1
        lesson = {"id": lid, "title": title, "symptom": symptom, "cause": cause or "", "fix": fix,
                  "tags": list(tags), "check": check or "", "evidence": [evidence] if evidence else [],
                  "status": status, "occurrences": 1, "created": now(), "lastSeen": now(),
                  "sources": [os.path.basename(project)] if project else []}
        rows.append(lesson)
        write_lines(self.path("lessons.jsonl"), rows)
        return lesson

    def find_lessons(self, tag=None, query=None, status="active"):
        out = []
        q = (query or "").lower()
        for r in self.lessons():
            if status and r.get("status") != status:
                continue
            if tag and tag.lower() not in r.get("tags", []):
                continue
            if q and q not in " ".join(str(r.get(k, "")) for k in ("title", "symptom", "cause", "fix", "check")).lower():
                continue
            out.append(r)
        out.sort(key=lambda r: r.get("lastSeen", ""), reverse=True)
        out.sort(key=lambda r: -int(r.get("occurrences", 1)))  # most seen first, then most recent
        return out

    def update_lesson(self, lid, seen=False, project=None, **fields):
        rows = self.lessons()
        for r in rows:
            if r.get("id") != lid:
                continue
            if fields.get("status") and fields["status"] not in STATUSES:
                raise ValueError("status is one of %s" % ", ".join(STATUSES))
            for key in ("status", "fix", "check", "cause", "symptom", "title"):
                if fields.get(key):
                    r[key] = fields[key]
            if fields.get("tags"):
                r["tags"] = list(fields["tags"])
            if fields.get("evidence"):
                r.setdefault("evidence", []).append(fields["evidence"])
            if seen:
                r["occurrences"] = int(r.get("occurrences", 1)) + 1
                r["lastSeen"] = now()
            if project and os.path.basename(project) not in r.setdefault("sources", []):
                r["sources"].append(os.path.basename(project))
            write_lines(self.path("lessons.jsonl"), rows)
            return r
        raise KeyError(lid)

    def remove_lesson(self, lid):
        rows = self.lessons()
        kept = [r for r in rows if r.get("id") != lid]
        if len(kept) == len(rows):
            raise KeyError(lid)
        write_lines(self.path("lessons.jsonl"), kept)

    # Preferences --------------------------------------------------------------------------------------------
    def prefs(self):
        return read_json(self.source("prefs.json"), {})

    def set_pref(self, key, value=None, words=None, remove=False):
        prefs = self.prefs()
        if remove:
            if prefs.pop(key, None) is None:
                raise KeyError(key)
        else:
            prefs[key] = {"value": value, "words": words or "", "updated": now()}
        write_json(self.path("prefs.json"), prefs)
        return prefs.get(key)

    # Project facts ------------------------------------------------------------------------------------------
    @staticmethod
    def facts(project):
        return read_json(os.path.join(sidecar(project), "facts.json"), {})

    @staticmethod
    def set_fact(project, key, value=None, remove=False):
        facts = Store.facts(project)
        if remove:
            if facts.pop(key, None) is None:
                raise KeyError(key)
        else:
            facts[key] = {"value": value, "updated": now()}
        write_json(os.path.join(sidecar(project), "facts.json"), facts)
        return facts.get(key)

    # Proposed skill changes ---------------------------------------------------------------------------------
    def propose(self, skill, file, summary, reason):
        folder = self.path("skills")
        os.makedirs(folder, exist_ok=True)
        stamp = now().replace(":", "")
        target = os.path.join(folder, "%s-%s.md" % (slug(skill), stamp))
        shutil.copyfile(file, target)
        entry = {"skill": skill, "file": os.path.basename(target), "summary": summary, "reason": reason, "created": now()}
        index = self.proposals()
        for old in index:  # the files of proposals read from the fallback are copied next to the new index
            name = os.path.basename(str(old.get("file") or ""))
            if name and not os.path.exists(os.path.join(folder, name)) and os.path.isfile(self.source(os.path.join("skills", name))):
                shutil.copyfile(self.source(os.path.join("skills", name)), os.path.join(folder, name))
        index.append(entry)
        write_json(os.path.join(folder, "index.json"), index)
        return entry

    def proposals(self):
        return read_json(self.source(os.path.join("skills", "index.json")), [])

    # Correction candidates (the hook) -----------------------------------------------------------------------
    def corrections(self):
        return read_lines(self.source("corrections.jsonl"))

    def record_correction(self, text, project=None):
        row = {"text": text.strip()[:600], "at": now()}
        if project:
            row["project"] = os.path.basename(project)
        rows = self.corrections()[-199:]  # a bounded inbox
        rows.append(row)
        write_lines(self.path("corrections.jsonl"), rows)
        return row

    def clear_corrections(self):
        write_lines(self.path("corrections.jsonl"), [])

    # Intake -------------------------------------------------------------------------------------------------
    def intake(self, project=None, tags=(), limit=12):
        """The text an edit starts with: matching active lessons (most seen first), preferences, project facts,
        lessons waiting for review and correction candidates not yet turned into lessons."""
        wanted = set(tags)
        active = self.find_lessons()
        if wanted:
            matching = [r for r in active if wanted & set(r.get("tags", [])) or not r.get("tags")]
        else:
            matching = active
        lines = []
        if matching:
            lines.append("Lessons (%d of %d active):" % (min(limit, len(matching)), len(active)))
            for r in matching[:limit]:
                seen = " (seen %dx)" % r["occurrences"] if int(r.get("occurrences", 1)) > 1 else ""
                lines.append("- [%s] %s%s: %s -> %s" % (r["id"], r["title"], seen, r["symptom"], r["fix"]))
                if r.get("check"):
                    lines.append("    check: %s" % r["check"])
        prefs = self.prefs()
        if prefs:
            lines.append("Preferences:")
            for key, p in sorted(prefs.items()):
                words = ' ("%s")' % p["words"] if p.get("words") else ""
                lines.append("- %s = %s%s" % (key, p.get("value"), words))
        if project:
            facts = self.facts(project)
            if facts:
                lines.append("Project facts (%s):" % os.path.basename(project))
                for key, f in sorted(facts.items()):
                    lines.append("- %s: %s" % (key, f.get("value")))
        proposed = self.find_lessons(status="proposed")
        if proposed:
            lines.append("%d proposed lesson(s) wait for the user's review (lessons --status proposed)." % len(proposed))
        pending = self.corrections()
        if pending:
            lines.append("%d correction candidate(s) from earlier sessions: turn them into lessons with self-learn "
                         "(corrections), then `corrections --clear`." % len(pending))
        return "\n".join(lines) or "Nothing learned yet."

    def export(self):
        return {"schema": "bashcut-knowledge/1", "lessons": self.lessons(), "prefs": self.prefs(),
                "proposals": self.proposals(), "corrections": self.corrections()}


# Hooks ------------------------------------------------------------------------------------------------------
def hooks_enabled(env=None):
    """On only with BASHCUTPRO_SELF_LEARN=1, in the environment or in ~/.config/bashcutpro/mcp.env."""
    env = os.environ if env is None else env
    if env.get("BASHCUTPRO_SELF_LEARN"):
        return env["BASHCUTPRO_SELF_LEARN"] == "1"
    home = env.get("HOME") or os.path.expanduser("~")
    try:
        with open(os.path.join(home, ".config", "bashcutpro", "mcp.env"), encoding="utf-8") as f:
            return any(line.strip() == "BASHCUTPRO_SELF_LEARN=1" for line in f)
    except OSError:
        return False


def hook(kind, stdin, store):
    """`correction` (UserPromptSubmit): keep a message that reads like a correction. `after-compact` (SessionStart
    after a compaction): print the candidates so they survive it. Never fails the user's turn."""
    if not hooks_enabled():
        return ""
    try:
        event = json.loads(stdin or "{}")
    except ValueError:
        event = {}
    if kind == "correction":
        text = str(event.get("prompt") or "")
        if text and CORRECTION.search(text):
            store.record_correction(text)
        return ""
    if kind == "after-compact":
        rows = store.corrections()[-10:]
        if not rows:
            return ""
        quoted = "\n".join('- "%s"' % r["text"] for r in rows)
        return "Correction candidates kept before the compaction (self-learn turns them into lessons):\n" + quoted
    return ""


def parser():
    p = argparse.ArgumentParser(prog="knowledge.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("intake")
    s.add_argument("--project")
    s.add_argument("--tags", default="")
    s.add_argument("--limit", type=int, default=12)
    s = sub.add_parser("add-lesson")
    s.add_argument("title")
    s.add_argument("--symptom", required=True)
    s.add_argument("--cause", default="")
    s.add_argument("--fix", required=True)
    s.add_argument("--tags", default="")
    s.add_argument("--evidence")
    s.add_argument("--check")
    s.add_argument("--status", default="active", choices=STATUSES)
    s.add_argument("--project")
    s = sub.add_parser("lessons")
    s.add_argument("--tag")
    s.add_argument("--query")
    s.add_argument("--status", default="active", choices=STATUSES)
    s.add_argument("--all", action="store_true", help="every status")
    s = sub.add_parser("update-lesson")
    s.add_argument("id")
    s.add_argument("--seen", action="store_true", help="it happened again: count it")
    for name in ("status", "fix", "check", "cause", "symptom", "title", "evidence", "tags", "project"):
        s.add_argument("--" + name)
    s = sub.add_parser("remove-lesson")
    s.add_argument("id")
    s = sub.add_parser("set-pref")
    s.add_argument("key")
    s.add_argument("value", nargs="?")
    s.add_argument("--words", help="the user's words, quoted")
    s.add_argument("--remove", action="store_true")
    sub.add_parser("prefs")
    s = sub.add_parser("set-fact")
    s.add_argument("key")
    s.add_argument("value", nargs="?")
    s.add_argument("--project", required=True)
    s.add_argument("--remove", action="store_true")
    s = sub.add_parser("facts")
    s.add_argument("--project", required=True)
    s = sub.add_parser("propose")
    s.add_argument("skill")
    s.add_argument("file")
    s.add_argument("--summary", required=True)
    s.add_argument("--reason", required=True)
    sub.add_parser("proposals")
    s = sub.add_parser("record-correction")
    s.add_argument("text")
    s.add_argument("--project")
    s = sub.add_parser("corrections")
    s.add_argument("--clear", action="store_true")
    s = sub.add_parser("export")
    s.add_argument("--out")
    s = sub.add_parser("hook")
    s.add_argument("kind", choices=("correction", "after-compact"))
    return p


def run(argv, store=None, stdin=None):
    """Returns (exit status, text to print)."""
    args = parser().parse_args(argv)
    store = store or Store()
    c = args.command
    try:
        if c == "intake":
            return 0, store.intake(args.project, tags_of(args.tags), args.limit)
        if c == "hook":
            try:
                return 0, hook(args.kind, sys.stdin.read() if stdin is None else stdin, store)
            except Exception:  # noqa: BLE001 - a hook never breaks the session
                return 0, ""
        if c == "add-lesson":
            out = store.add_lesson(args.title, args.symptom, args.cause, args.fix, tags_of(args.tags), args.evidence,
                                   args.check, args.status, args.project)
        elif c == "lessons":
            out = store.lessons() if args.all else store.find_lessons(args.tag, args.query, args.status)
        elif c == "update-lesson":
            out = store.update_lesson(args.id, seen=args.seen, project=args.project, status=args.status, fix=args.fix,
                                      check=args.check, cause=args.cause, symptom=args.symptom, title=args.title,
                                      evidence=args.evidence, tags=tags_of(args.tags))
        elif c == "remove-lesson":
            store.remove_lesson(args.id)
            out = {"removed": args.id}
        elif c == "set-pref":
            if not args.remove and args.value is None:
                raise ValueError("set-pref KEY VALUE, or KEY --remove")
            out = {args.key: store.set_pref(args.key, args.value, args.words, args.remove)}
        elif c == "prefs":
            out = store.prefs()
        elif c == "set-fact":
            if not args.remove and args.value is None:
                raise ValueError("set-fact KEY VALUE --project P, or KEY --remove --project P")
            out = {args.key: store.set_fact(args.project, args.key, args.value, args.remove)}
        elif c == "facts":
            out = store.facts(args.project)
        elif c == "propose":
            out = store.propose(args.skill, args.file, args.summary, args.reason)
        elif c == "proposals":
            out = store.proposals()
        elif c == "record-correction":
            out = store.record_correction(args.text, args.project)
        elif c == "corrections":
            out = store.corrections()
            if args.clear:
                store.clear_corrections()
        else:  # export
            out = store.export()
            if args.out:
                write_json(os.path.abspath(args.out), out)
                out = {"out": os.path.abspath(args.out)}
    except KeyError as error:
        return 1, json.dumps({"error": "not found: %s" % error.args[0]}, ensure_ascii=False)
    except (ValueError, OSError) as error:
        return 1, json.dumps({"error": str(error)}, ensure_ascii=False)
    return 0, json.dumps(out, ensure_ascii=False, indent=2)


def main(argv=None):
    code, text = run(sys.argv[1:] if argv is None else argv)
    if text:
        print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
