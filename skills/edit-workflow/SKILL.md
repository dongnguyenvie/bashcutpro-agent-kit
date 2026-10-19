---
name: edit-workflow
description: The spine of every BashCutPro edit, raw footage to export: intake questions, a brief and plan kept in the project notes, survey, story, the cut applied with command_batch, sound, text, colour, effects, review, draft and final export, through the user's gates; names the one skill to read per stage. Use at the start of any edit or revision. Triggers: "dựng video", "cắt video", "làm vlog", "dựng giúp", "sửa lại video", "edit this", "edit my footage", "bắt đầu từ đâu", "video quảng cáo".
---

# Editing a video in BashCutPro

This skill runs the process; the stage skills hold the craft. Read **one section** of
`<skill_dir>/REFERENCE.md` when a step names it (`sed -n '/^## Intake/,/^## [A-Z]/p' <skill_dir>/REFERENCE.md`),
never the whole file. A recipe (`bcp:vlog-<kind>`, routed by `bcp:vlog-plan`) adds structure, ranges and checks to
the plan; this skill still runs the stages.

Every edit goes through BashCutPro's MCP server (`bcp:setup` if its tools are missing): `command_list {filter}` to
find a command, `command_run {id, params}` for one edit (one undo step), `bashcut.batch` for many in order (one
undo step, all or nothing; `command_batch` on a build without it),
`doc_inspect` / `sequence_inspect` to read, `render_frame` to look. Use only ids that `command_list` returns.

## Hard rules

- **Plan first, then one batch per stage.** Work the stage out on paper (the plan), then apply it as one
  `command_run {id: "bashcut.batch", params: {commands: [{id, params}], label: "<stage>"}}`: the stage is one undo
  step, and a failing step leaves the project unchanged and names the step (fix it, send the batch again). A build
  without `bashcut.batch` (not in `command_list`): `command_batch` with `stop_on_error: true`, where each step is its
  own undo step, so note the `history.list` length before it to know how far `edit.undo` must go back.
- **Read little.** `doc_inspect` at start (project, bins, items); then `bashcut.timeline.summary` (tracks and clips
  in seconds, only what differs from a plain clip, a few KB) after a gate or a failed batch. Otherwise trust what your
  own commands returned: `bashcut.batch` answers with `changed` (clips added / changed / removed) and `createdId`.
  Errors start with a code: `notFound` (re-read, fix the id), `badParams` (fix the params), `refused` (change the
  state or ask), `busy` (wait, retry), `offline` (relink or tell the user). Never print a whole transcript: search it (`transcript.search`) or read a range.
- **Look in batches.** `render_frame {seconds, max_side: 540}` at the frames that matter (hook, each section start,
  every text), phone size, not every second.
- **You never certify yourself.** "Done" needs evidence (a frame, a command result, an export path). You cannot
  hear: say which sound you did not check. Nothing measures loudness read-only today (REFERENCE "Limits").
- **Only the user answers a gate.** Silence or an earlier "go ahead" is not approval.
- **Save after every stage**: `file.save` (a headless server with no path: `file.saveAs {path}` once).
- Files named in English, lowercase, hyphens (`draft-v1.mp4`).

## Stages

| # | Stage | Read | Gate after it |
|---|---|---|---|
| 0 | intake: questions, brief | this skill, REFERENCE "Intake questions"; a recipe via `bcp:vlog-plan` | **G1 brief** |
| 1 | survey: what the footage holds | `bcp:footage-survey` | — |
| 2 | story: promise, sections, options | REFERENCE "Story", the recipe | **G2 strategy** |
| 3 | rough cut: selects by quote, no music, titles or grade | `bcp:rough-cut` | **G3 rough cut** |
| 4 | rhythm: cut on the beat, punch-ins | `bcp:beat-cut` | — |
| 5 | voiceover, when the plan has lines | `bcp:voiceover` | **G4 script**, before speech is made |
| 5b | visuals, when words carry the video | `bcp:visual-plan`, `bcp:stock-images` | — |
| 6 | sound: levels, music bed, ducking, SFX | `bcp:audio-mix` | — |
| 7 | captions, titles, cards | `bcp:captions-text`, `bcp:motion-graphics` | — |
| 8 | colour | `bcp:color-grade` | — |
| 9 | effects, transitions, motion | `bcp:effects` | — |
| 10 | review: look, measure what can be measured, fix | `bcp:review` | **G5 draft** |
| 11 | export per output | this skill, "Export" | — |

Lock the cut (stages 3–4) before music and SFX: changing clip lengths later breaks every sync point. A stage the
plan does not need is skipped with its reason written in the plan (`"colour": "skipped: screen recording"`). Want
to copy a reference video's style first: `bcp:style-study` before stage 2.

## 0. Intake

1. `doc_inspect` (what is open), then the project: an existing `.fcproj` → `file.open {path}`; a template the user
   names or a series they repeat (`bashcut.template.list`) → `bashcut.template.instantiate {"template", "fills":
   [{"slot", "file"}], "saveAs": "/abs/new.fcproj"}` (their cut, effects and captions with this footage in the slots,
   one undo step); else `file.newProject {name}` and a sequence shaped for where it will be watched:

   | Watched on | `file.newSequence` |
   |---|---|
   | TikTok, Reels, Shorts | `{"name": "main", "width": 1080, "height": 1920, "fps": 30}` |
   | YouTube, computers | `{"name": "main", "width": 1920, "height": 1080, "fps": 30}` |
   | Feeds (square) | `{"name": "main", "width": 1080, "height": 1080, "fps": 30}` |

   Match the footage's frame rate when it is 25 or 29.97 (from `project.items` / `media.status` after import).
2. Import all footage in one call: `bashcut.media.import {"paths": ["/abs/path/a.mp4", …]}` where the build has it
   (`file.import` plus the installed plugins' import hooks, e.g. a transcript on import; `bashcut.hooks.list` shows
   them), else MCP `media_import` or `file.import {paths}`. Absolute paths only. The same recipe over many inputs
   (a folder, a series) is a batch, not one edit: `bcp:batch`. Then read what earlier edits taught: `python3 <skill_dir>/../self-learn/knowledge.py intake
   --project /abs/film.fcproj --tags <the genre and the stages ahead>` (lessons, the user's preferences, this
   project's facts); follow them, and do not ask what a preference already answers.
3. **Ask once** (at most 4 questions, REFERENCE "Intake questions"), each led by the choice you would make
   ("AI chọn: …"). User away: take your choices, mark them `inferred`, never ask later.
4. Write the brief and the plan into the project notes (REFERENCE "Brief and plan in the notes"), then **G1**:
   show the brief in 4–6 lines.

## 1–2. Survey and story

Follow `bcp:footage-survey`: inventory, shots, transcript (words imported with `transcript.set` when the build has
no Whisper), descriptions in `metadata.set`. It returns a digest; plan from it, never from re-reading media.

Story (REFERENCE "Story"): the promise (the question the hook opens, the payoff that closes it), sections with a
length range and a reason each, the hook in the first 1–3 s. In create mode compare 2–3 options in the plan.
**G2**: the strategy in 4–8 sentences plus the section table, with a frame of the hook shot.

## 3–4. The cut as one batch

`bcp:rough-cut` turns quotes into word-exact ranges and applies them; `bcp:beat-cut` adjusts edges to the music.
Check the batch on paper before sending it: no cut inside a word (compare planned times with word `start` / `end`
from `transcript.inspect`), the order of sections, the total against the length range. Then one batch:

```json
{"steps": [
  {"id": "timeline.place", "params": {"items": ["<sub1>", "<sub2>", "<sub3>"], "track": "V1", "seconds": 0}},
  {"id": "markers.addRange", "params": {"time": 0, "duration": 1524096000000, "name": "hook"}},
  {"id": "file.save", "params": {}}
], "stop_on_error": true}
```

(`time` / `duration` are ticks: 254 016 000 000 per second; most commands also take `seconds` or `frame`.)
**G3**: the cut list from `sequence_inspect` (duration against the plan) and 4–6 frames at section starts.

## 5–9. Voice, sound, text, colour, effects

One stage at a time, each its skill, each one batch and a save. Write what each changed in the plan's `log`
(one `project.setNotes` per stage, REFERENCE "Brief and plan in the notes"). Order matters:

- Voiceover before sound (its length moves the music); captions after the cut and voice are locked (captions
  from words: `transcript.createCaptions`).
- Text that sits over the picture: plate it or outline it; white text over daylight measured 1.2–2:1 contrast,
  unreadable on a phone (`bcp:captions-text`).
- Effects only where a moment needs one (`bcp:effects`): a transition on every cut reads as a template.

## 10. Review and draft

Follow `bcp:review`: frames at phone size at every cut and every text, the cut list against the words (no cut
inside a word, no gap, no flash frame), the plan's checks. Fix in one batch, look again at what changed. Then the
draft:

```json
{"id": "file.exportMedia", "params": {"path": "/abs/out/draft-v1.mp4", "format": "h264", "height": 960,
 "loudnessLufs": -14, "burnCaptions": true, "wait": true}}
```

**G5**: the draft path, its length, what review fixed and what it kept, and what was not checked (sound by ear).

## 11. Export

After G5, one export per output (REFERENCE "Export"), each with its output profile where the build has them
(`bashcut.profiles.apply {profile, path, wait: true}`: size, bitrate, loudness and captions from the profile), else
`file.exportMedia` at full size, the platform's loudness, captions burned in or as a sidecar (`captionSidecar: "srt"`). A cover frame: `file.exportFrame {path, time}` at the hook. YouTube
chapters: `markers.addChapter` per section, then write the chapter text from the markers. End with the hand-off
report (REFERENCE "Hand-off report").

At the end of the session (after G5 or the export), `bcp:self-learn`: what failed, was redone or corrected becomes a
lesson, preference or fact, so the next intake prints it.

## Revisions

Same project, in place. Re-enter at the stage that owns the change (a shorter hook → stage 3, louder music → 6),
mark untouched sections `frozen` in the plan, export `draft-v2` next to `draft-v1`. Two versions to compare: a
second sequence (`file.newSequence {fromItems}`) or `file.saveCopy {path}`. The latest feedback wins.
