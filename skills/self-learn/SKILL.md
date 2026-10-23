---
name: self-learn
description: Turn what went wrong or what the user corrected while editing in BashCutPro into lasting knowledge kept as plain files (knowledge.py): lessons (symptom, cause, fix), the user's preferences in their own words, project facts (names, brand, spelling, people), or a proposed kit change. Use after a failed or redone step, a user correction, repeated review findings, or at session end. Triggers: "rút kinh nghiệm", "học từ lỗi này", "nhớ lần sau", "lần sau đừng", "nhớ là", "cập nhật skill", "remember this", "next time", "learn from this", "self-learn".
---

# Self-learn

A problem solved in chat but not written down **will happen again**. The kit keeps what it learns as files
(`<skill_dir>/knowledge.py`, standard library), not in the app: lessons and preferences for every project in
`<data dir>/bashcut/knowledge/` (BashCutPro's data dir; a file it does not have yet is read from the older engine's folder (`FilmCraft`),
never moved), facts for one project in `<name>.fcproj.bashcut/facts.json` next to it.

```sh
K="${BASHCUT_PYTHON:-python3} <skill_dir>/knowledge.py"
$K intake --project /abs/film.fcproj --tags captions,audio   # what edit-workflow prints at intake
```

Run it once the problem is solved (you need the real cause), not mid-step. At the end of a session, sweep for
anything missed, starting from `$K corrections`: with the hooks on (below) they hold, quoted, every user message
that read like a correction, also across a compaction. They are candidates: most become one lesson, some are
one-off instructions. Clear them with `$K corrections --clear` once handled.

Worth recording: the user corrects you ("không, dùng X", "thật ra…", "X chứ không phải Y", "no, use X") or rejects
a proposed action; says to remember ("nhớ là…", "lần sau đừng…", "next time…"); a command fails or a result had to
be redone; `bashcut.review.run` reports the same `check` (`readingSpeed`, `cutInWord`, `frozen`, `truePeak`…) in two rounds
or two projects, or a blocking finding is still there after the last round. Quote the finding (its `check`,
`measured`, `limit` and seconds) in `--evidence` and tag it with its category (`captions`, `edit`, `picture`,
`sound`). A question, a one-off instruction for
this clip or vague feedback ("chưa ổn") is not a lesson.

## 1. Write the lesson

Symptom → cause → what to do, with the number or error text that proves it.

| Good | Bad |
|---|---|
| "Cross Dissolve refused: the clips were not adjacent on V1 (a 3-frame gap). Close the gap first." | "Transitions are tricky." |
| "Music dipped 11 dB at every loop: the song has a quiet intro. Trim 2.6 s off its start before repeating." | "Watch the music." |

Only what was **observed** this session (an error, a measurement, the user's words); a guess is not a lesson.
First search: `$K lessons --tag transitions`, `$K lessons --query "gap"` (the same problem is often worded
differently). If it exists, `$K update-lesson ID --seen --project P` and add the quote with `--evidence` when it says
something new, instead of a second lesson.

```sh
$K add-lesson "Dissolve refused on non-adjacent clips" \
  --symptom "transition refused: clips not adjacent" --cause "a 3-frame gap on V1" \
  --fix "close the gap before adding a transition" --evidence "error text, rev 41" \
  --check "Are the two clips touching on one track?" --tags transitions --project /abs/film.fcproj
```

- **The user's words quoted, not paraphrased** in `--evidence` (a paraphrase loses which title the user meant).
  Feedback unclear about *which* element: confirm the target before changing anything.
- **A `--check` question** for before the next draft ("Does every caption stay off the face?").
- **Status:** `active` (default) when the cause is proven; `--status proposed` when unsure: intake counts proposed
  lessons and the user reviews them (`$K lessons --status proposed`, then `update-lesson ID --status active`).
- **Tags:** one or two areas (captions, audio, pacing, color, transitions, export, voice, plugin id…), the same words
  edit-workflow passes to `intake --tags`.

**How often and how lately** come from `occurrences`, `lastSeen` and `sources` on the rows, not your memory:
- seen three or more times although active: its fix or check does not work; rewrite the fix, or propose a kit
  change (step 3) when it is about how a skill tells you to work;
- a workaround from before an app update where the plain way now works: `--status disabled`, say why in
  `--evidence`. Old alone is never a reason.

## 2. Put it in the right place

| About | Goes to |
|---|---|
| A mistake that can happen again (any project) | a lesson (`add-lesson`, `--project` records where it came from) |
| The user's taste (length, pace, voice, caption style, music) | `$K set-pref pace calm --words "nhịp chậm thôi"`: a short stable key (`pace`, `caption.style`, `music.genre`), so a later value replaces it |
| This project: names, brand, spelling, people, what the user approved | `$K set-fact host "Lan, speaks fast" --project P` |
| A kit rule wrong, missing or too vague; a skill that should have loaded | a proposed kit change (step 3) |
| A plugin's skill wrong or missing a step | a lesson tagged with the plugin id |
| BashCutPro itself (a bug, a missing command) | a note for the maintainers with the command, input and error |

Wrong or outdated: `update-lesson ID --status disabled` (kept for the record) or `remove-lesson ID`;
`set-pref KEY --remove`; `set-fact KEY --remove --project P`. `$K export --out file.json` copies everything.

## 3. Changing the kit

Installed skills are managed by the plugin system; edits there are lost on update. Instead write a copy of the
skill with the change (a few lines, never a rewrite, each line backed by what happened), show it to the user, then:

- the kit repository is local and the user agrees: apply it there on a branch and open a PR;
- otherwise `$K propose beat-cut SKILL.md --summary "close gaps before a transition" --reason "refused twice on a
  3-frame gap"`: it waits in `<data dir>/bashcut/knowledge/skills/` (`$K proposals`); nothing installed changes.

## Hooks (optional, Claude Code)

The kit's `hooks/hooks.json` keeps correction candidates: on every message that reads like a correction
(English or Vietnamese) it appends the quote to `corrections.jsonl`, and after a compaction it puts the last ten
back into the conversation. Off unless `BASHCUTPRO_SELF_LEARN=1` is in the environment or in
`~/.config/bashcutpro/mcp.env`; ask the user before turning it on. Codex has no hooks: sweep at session end.

## Report

Short: what went wrong → where the lesson went → the lines added. Nothing worth recording: say so in one line.
