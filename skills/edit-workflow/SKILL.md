---
name: edit-workflow
description: The spine of every edit, raw footage to export: brief and plan, survey, cut on word edges, sound, captions, colour, review gate, export; names the one skill per stage. Use for any edit or revision. Not for picking a vlog recipe (bcp:vlog-plan) or many inputs (bcp:batch). Triggers: "dựng video", "cắt video", "làm vlog", "dựng giúp", "sửa lại video", "edit this", "edit my footage", "bắt đầu từ đâu", "video quảng cáo".
---

# Editing a video in BashCutPro

This skill runs the process; the stage skills hold the craft. Read **one section** of
`<skill_dir>/REFERENCE.md` when a step names it (`sed -n '/^## Intake/,/^## [A-Z]/p' <skill_dir>/REFERENCE.md`),
never the whole file. A recipe (`bcp:vlog-<kind>`, routed by `bcp:vlog-plan`) adds structure, ranges and checks to
the plan; this skill still runs the stages.

Every edit goes through BashCutPro's MCP server (`bcp:setup` if its tools are missing): `command_list {filter}` to
find a command, `command_run {id, params}` for one edit (one undo step), `bashcut.batch` for many in order (one
undo step, all or nothing), `doc_inspect` / `sequence_inspect` to read, `render_frame` to look. Use only ids that `command_list` returns.

**Turn budget.** A headless agent has a turn cap (bashcut-batch `maxTurns`), and one BashCutPro#219 tutorial ran out
at 80 turns with 34 single `render_frame` calls and 14 `command_list` calls. A whole edit, tutorial included, fits
well under 100 turns: one lookup per command, one `bashcut.batch` per stage, one contact sheet per look.

## Hard rules

- **Plan first, then one batch per stage.** Work the stage out on paper (the plan), then apply it as one
  `command_run {id: "bashcut.batch", params: {commands: [{id, params}], label: "<stage>"}}`: the stage is one undo
  step, and a failing step leaves the project unchanged and names the step (fix it, send the batch again).
- **Look commands up once.** Take the ids and params of the stage's commands in one go, from the kit's catalogue
  (`grep -A 6 '"id": "graphics.newText"' <kit>/scripts/commands.json`, or Grep for several ids at once) or one
  `command_list {filter}` per command family, and keep what it returned for the whole edit. Never look up the same
  id twice; `badParams` names the bad key, so fix that instead of listing again.
- **Read little.** `doc_inspect` at start (project, bins, items); then `bashcut.timeline.summary` (tracks and clips
  in seconds, only what differs from a plain clip, a few KB) after a gate or a failed batch. Otherwise trust what your
  own commands returned: `bashcut.batch` answers with `changed` (clips added / changed / removed) and `createdId`.
  Errors start with a code: `notFound` (re-read, fix the id), `badParams` (fix the params), `refused` (change the
  state or ask), `busy` (wait, retry), `offline` (relink or tell the user). Never print a whole transcript: search it (`transcript.search`) or read a range.
- **Look in batches: one contact sheet per pass.** List the times that matter (hook, each section start, every
  card, zoom and text), then `"${BASHCUT_PYTHON:-python3}" <kit>/skills/footage-survey/contact_sheet.py plan --program --at t1,t2,…
  --dir /abs/tmp/look-N` → one `command_batch {steps}` → `contact_sheet.py sheet "/abs/tmp/look-N/*.png" -o
  /abs/tmp/look-N.png --width 400` (phone size) → look at that one image. Never one `render_frame` per card or
  zoom; a single `render_frame {seconds, max_side: 540}` only for one frame in doubt.
- **You never certify yourself.** "Done" needs evidence (a frame, a command result, an export path). You cannot
  hear, but you can measure: `bashcut.audio.loudness` and `bashcut.review.run` read loudness, true peak, frozen
  and black picture, caption speed and safe area, and cuts in words from the timeline. Say which sound you did not
  listen to.
- **Render little.** Judge with `render_frame` and the review's measures, not draft exports: one export per output,
  after the review passes. Many inputs with one treatment are a batch (`bcp:batch`), not N edits by hand.
- **Only the user answers a gate.** Silence or an earlier "go ahead" is not approval.
- **Save after every stage**: `file.save` (a headless server with no path: `file.saveAs {path}` once). A batch
  agent that runs out of turns is exported from its last save (BashCutPro#219), so an unsaved stage is lost.
- Files named in English, lowercase, hyphens (`draft-v1.mp4`).

## Stages

| # | Stage | Read | Gate after it |
|---|---|---|---|
| 0 | intake: questions, brief | this skill, REFERENCE "Intake questions"; a recipe via `bcp:vlog-plan` | **G1 brief** |
| 1 | survey: what the footage holds | `bcp:footage-survey` | — |
| 2 | story: promise, sections, options | REFERENCE "Story", the recipe | **G2 strategy** |
| 3 | rough cut: selects by quote, tightened on word edges (`tighten.py`), no music, titles or grade | `bcp:rough-cut` | **G3 rough cut** |
| 4 | rhythm: cut on the beat, punch-ins | `bcp:beat-cut` | — |
| 5 | voiceover, when the plan has lines | `bcp:voiceover` | **G4 script**, before speech is made |
| 5b | visuals, when words carry the video | `bcp:visual-plan`, `bcp:stock-images` | — |
| 6 | sound: voice polished to the profile, music bed, SFX | `bcp:audio-mix` | — |
| 7 | captions (`bashcut.captions.create`), titles, cards | `bcp:captions-text`, `bcp:motion-graphics` | — |
| 8 | colour | `bcp:color-grade` | — |
| 9 | effects, transitions, motion | `bcp:effects` | — |
| 10 | review: `bashcut.review.run` on every output sequence, fix, 1–3 rounds | `bcp:review` | **G5 draft** |
| 11 | one export per output and profile | this skill, "Export" | — |

Recipes add their own skill per stage (a podcast's clips: `bcp:vlog-podcast-clips` at stages 2–3 and 7; a talking
head: `bcp:vlog-talking-head` at 3–4 and 7; a tutorial: `bcp:vlog-tutorial`). Lock the cut (stages 3–4) before
music and SFX: changing clip lengths later breaks every sync point. A stage the
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
   (a folder, a series) is a batch, not one edit: `bcp:batch`. Then read what earlier edits taught: `"${BASHCUT_PYTHON:-python3}" <skill_dir>/../self-learn/knowledge.py intake
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

`bcp:rough-cut` turns quotes into word ranges and `tighten.py` turns the ranges into one `bashcut.batch`: fillers,
false starts and dead air out, every edge on a word edge, clips back to back from frame 0. Read its report before
sending: the total against the length range, `cuts` a minute against the recipe (podcast clip 12–25, talking head
15–30, tutorial 10–20), what was removed. `bcp:beat-cut` then adjusts edges to the music and adds punch-ins. Mark
sections in one more batch:

```json
{"id": "bashcut.batch", "params": {"label": "sections", "commands": [
  {"id": "markers.addRange", "params": {"time": 0, "duration": 1524096000000, "name": "hook"}},
  {"id": "file.save", "params": {}}]}}
```

(`time` and `duration` are ticks: 254 016 000 000 per second; many commands also take `seconds` or `frame`.)
Footage whose size differs from the sequence's sits small inside black bars: same aspect, `clip.fitToFrame {clips}`
(720p in a 1080p sequence → 150 %); another aspect (16:9 into 9:16), `fitToFrame` letterboxes, so fill instead: Motion
`scale` = sequence height / source height × 100 (`effects.setParam`), framed on the subject (`bashcut.vision`
`subjects --reframe` follows a face). Look at a frame either way.
**G3**: the cut list from `bashcut.timeline.summary` (duration against the plan, cuts a minute) and 4–6 frames at
section starts.

## 5–9. Voice, sound, text, colour, effects

One stage at a time, each its skill, each one batch and a save. Write what each changed in the plan's `log`
(one `project.setNotes` per stage, REFERENCE "Brief and plan in the notes"). Order matters:

- Voiceover before sound (its length moves the music); captions after the cut and voice are locked:
  `bashcut.captions.create {maxCps: 20, lines: 2, maxChars}` (42 landscape; 20 vertical with `captions.setStyle
  {size: 40, margin}` above the profile's bottom band), cues on word edges (`bcp:captions-text`).
- Sound to the output profile: `bashcut.audio.polish {clips, profile}` on the voice clips, music at one level about 16 dB under
  it, ducked only for silences ≥ 2.5 s, SFX 0.1 s early so the peak lands on the moment (`bcp:audio-mix`).
- Text that sits over the picture: plate it or outline it; white text over daylight measured 1.2–2:1 contrast,
  unreadable on a phone (`bcp:captions-text`).
- Effects only where a moment needs one (`bcp:effects`): a transition on every cut reads as a template.

## 10. Review: the gate

Follow `bcp:review` on **every output sequence** (`sequence.open`, then `bashcut.review.run {profile, sequence}`):
loudness and true peak, caption speed, lines and safe area, cuts inside words, gaps, frozen or black picture, each
finding with its fix and limit. Fix the blocking ones in one batch per round and run it again: 1–3 rounds, then what
is left is kept with its reason. Add frames at phone size at the hook, every text and doubtful cuts
(one contact sheet, above), and the plan's checks.

**G5**: per output the verdict, blocking and warnings left, what the rounds fixed and kept, 4–6 frames, and what
was not checked (sound by ear). No draft export: an export is made only when the user asks to watch one, at
`height: 960` (`file.exportMedia {path, format: "h264", height: 960, burnCaptions: true, wait: true}`).

## 11. Export

After G5, one export per output (REFERENCE "Export"), each with its output profile:
`bashcut.profiles.apply {profile, path, wait: true}` (size, bitrate, loudness and captions from the profile; its
`peakCheck` measures the file's true peak and exports again when it is over). Builds without profiles:
`file.exportMedia` at full size, the platform's loudness, captions burned in or as a sidecar (`captionSidecar: "srt"`). A cover frame: `file.exportFrame {path, time}` at the hook. YouTube
chapters: `markers.addChapter` per section, then write the chapter text from the markers. End with the hand-off
report (REFERENCE "Hand-off report").

At the end of the session (after G5 or the export), `bcp:self-learn`: what failed, was redone or corrected becomes a
lesson, preference or fact, so the next intake prints it.

## Revisions

Same project, in place. Re-enter at the stage that owns the change (a shorter hook → stage 3, louder music → 6),
mark untouched sections `frozen` in the plan, export `draft-v2` next to `draft-v1`. Two versions to compare: a
second sequence (`file.newSequence {fromItems}`) or `file.saveCopy {path}`. The latest feedback wins.
