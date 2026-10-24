---
name: visual-plan
description: Decide what the viewer sees on every line of a talking video: one treatment per line (speaker, punch-in, B-roll, stock, icon, text, graphic, generated, screen) anchored to a word, written as visuals rows in the plan. Not for fetching the pictures (bcp:stock-images) or the script words (bcp:vlog-hook-script). Triggers: "minh hoạ", "kế hoạch hình ảnh", "câu này hiện gì", "b-roll cho script", "visual plan", "thêm hình cho lời nói".
---

# Visual plan

Building skills decide one moment; this plan decides the whole video first, so treatments vary, land on words and
reach the density and look needed. Plan and research here; the building skills build. The plan lives in the
project notes (`project.notes` to read, `project.setNotes {text, merge}` to write; bcp:edit-workflow REFERENCE
"Brief and plan in the notes").

## 0. When and where

Stage `visuals` (bcp:edit-workflow stage 5b), added at the story stage when words carry the video (none for a music
montage or a vlog told by pictures). It runs after the cut is locked (words and timing fixed) and before sound and
captions (SFX and caption mode depend on it). When the recipe did not add it, add it to `plan.stages` with every
other key kept: `"visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "talking
video"}`.

## 1. Read what is said and what exists

- **A written script** (`plan.beats` from bcp:vlog-hook-script): start from it, do not re-derive. Find each beat's
  words as heard (`transcript.search {query}` on its first words, `transcript.inspect` for the range: `at`, `end`
  and how much of the text was really said). A beat with an `onScreen` note is a draft row: `line` = text,
  `from`/`to` = its first and last word, `beat` = id, `show` = the note, `treatment` = its `treatment` or the
  table's name for what the note asks. Only check them (§2–§3) and fill gaps: a beat without a note, a long beat
  needing two rows, a beat whose words were mostly not said (under about 0.6 of its words heard: re-worded or cut,
  take its words from what is heard).
- **No script**: split the transcript (`transcript.inspect`) into lines at sentence or idea boundaries, with each
  line's first and last word times. No transcript: bcp:footage-survey first (`transcript.set` imports outside words).
- What exists: the described shots (item Descriptions from bcp:footage-survey, `project.items`), what is on screen
  now (`sequence_inspect` for the clips; the cuts and text on one contact sheet, bcp:edit-workflow "Look in
  batches").
- Targets, each with its source: a reference's measured profile (bcp:style-study), else the recipe's ranges, else
  the kit's (bcp:motion-graphics, bcp:effects).

## 2. One treatment per line

Ask of every line: what does the viewer imagine, and does the picture already show it?

| Treatment | Shows | Built with |
|---|---|---|
| `speaker` | the face carries it: opinion, feeling, punchline | nothing added |
| `punch-in` | same shot, closer, on the strongest word | bcp:beat-cut, bcp:effects |
| `own-broll` | the user's shot of what is said | bcp:rough-cut, `timeline.place` |
| `stock` | photo or video of a thing, place or action the footage lacks | bcp:stock-images |
| `icon` | small symbol: money, time, place, yes/no, arrow | bcp:stock-images (icons) |
| `text` | keyword, number or label as native text | bcp:captions-text |
| `graphic` | designed motion: kinetic type, counter, chart, pointer, mock screen, card, diagram | bcp:motion-graphics |
| `generated` | a picture that cannot be filmed or found | bcp:vlog-scene-prompt for the prompt, the [`bashcut.image-gen`](https://github.com/dongnguyenvie/bashcutpro-plugins/tree/main/plugins/image-gen) plugin to make it |
| `screen` | screen recording or screenshot of what is explained | `timeline.place`, bcp:effects (focus zoom) |
| `none` | bare on purpose so the next line lands | — |

Not a closed list: a new treatment needs a name, what it shows and who builds it. A combination is one treatment (a
`stock` photo with a `text` keyword is `stock`; `show` says both).

Guides, not rules:
- Concrete words (thing, number, place, step, comparison) can be shown; abstract or emotional lines are usually the
  speaker's.
- A number reads best counted or written, a process as steps or a diagram, a comparison side by side, a named object
  as the user's own shot, then stock, then an icon. `generated` is last: when nothing real exists (a scene from the
  past, an imagined place, a metaphor, a recurring mascot), never for a real product, place or person.
- Anchor each row to one word (`at`): entrances end on its first frame. Hold until the idea's narration ends,
  unless it is an accent.
- **Screen lines**: one `screen` row per narration line, `show` naming the panel the line names; a new row where
  the screen changes inside a line (scene cuts: `clip.sceneEditDetection`, frames from `render_frame`). Never one
  framing for every screen row. Check the rows at phone size on one contact sheet of their `at` times (`sheet --width 400`), not one
  `render_frame` per row (BashCutPro#219).
- Text and captions never say the same thing twice: decide the caption mode here (full, keywords only, none) and
  write it into `plan.stages.captions.rules`.

## 3. Balance the whole video

Check the rows end to end against the targets before researching:
- **Density and interval**: picture changes and graphics per minute within target; nothing in the hook's first
  1–3 s that does not serve the hook.
- **Variety**: one treatment on three lines in a row reads as a template unless the reference does exactly that;
  vary the device within it too.
- **Presence**: speaker screen share within target; keep the face on emotion, the hook's promise and the payoff.
- **Faces**: nothing covers the face while it speaks the point. No face detection exists: look at the rows' `at` frames (one
  contact sheet) and say where the face is.

Change rows until it fits; mark targets left on purpose `"deliberate": true` with the reason.

## 4. Research and look

Rows that need what the project lacks:
- `stock`, `icon`: 3–6 candidates per row (bcp:stock-images), a batch on one contact sheet
  (bcp:footage-survey's `contact_sheet.py`); look, pick, import.
- `own-broll`: matching described shots; check them together on one contact sheet of each shot's best moment.
- `graphic`: note each row's starting example (an installed template, `graphics.template.list`, or a hyperframes
  catalog example when that plugin is installed), or new; design happens at build.
- `generated`: the prompt idea and the look shared by every generated row (one style sentence, the reference
  pictures of a recurring character); generation and any price wait for the build (§6).

No good candidate: change treatment (often to `text` or `speaker`); never keep a weak picture.

## 5. Write the plan

Read the notes, add `plan.visuals` and write the whole block back (`project.setNotes`). Rows in time order:

```json
{"visuals": [
  {"line": "one of the best ways", "from": 0.0, "to": 1.2, "at": 0.4, "treatment": "graphic",
   "show": "serif lead-in, 'Best ways' slams in lime", "why": "the hook's claim, made to read in 1 s"},
  {"line": "which can boost", "from": 6.2, "to": 7.2, "at": 6.7, "treatment": "punch-in",
   "show": "1.12× on 'boost'", "why": "a strong verb the face sells"},
  {"line": "back in 1998 the street was a river", "from": 9.0, "to": 12.4, "at": 9.6, "treatment": "generated",
   "show": "flooded 1998 street, flat pastel, the mascot on a boat", "why": "no picture of it exists",
   "prompt": "a narrow Saigon street flooded knee-deep, 1998, a small fox mascot rowing a tin boat"}
]}
```

Times are timeline seconds; `show` is one phrase of what is seen; `why` is the line's need, not the treatment's
name; `beat` is the script beat's id. A row departing from its note says so in `why` ("note asked for a price
card; the board in shot already shows it"). The picture's source lives on the imported item (`metadata.set`
Description), not here. Generated rows also get `prompt`; the shared look goes once in `plan.visualStyle`
(`{"prompt": "…", "references": ["/abs/mascot.png"]}`).

Gate: when the brief asks to approve visuals, or rows need paid generation, show the rows by treatment, the
targets and the contact sheet in the conversation and wait for the user's answer; otherwise go on.

## 6. Hand off and close

Build in this order, each row by its skill: picture that replaces a moment (`own-broll`, `stock` video, `screen`)
→ `graphic` → `generated` → `stock` photos and `icon` → `text` → `punch-in`. Each visual's sound is
bcp:audio-mix's, at the row's `at`.

**Generated rows** with the `bashcut.image-gen` plugin (its skill `image-gen` has the details):
1. Show the user the service, model, the number of pictures and their prompts; generation spends their key, so
   wait for a yes. No plugin or no key: deliver the prompts (bcp:vlog-scene-prompt) and say generation is theirs.
2. One `scenes.json` with every generated row: `{"scenes": [{"id": "<row id>", "prompt": "<row prompt>",
   "seconds": <at or from>, "duration": <to − seconds>}], "style": <plan.visualStyle>, "width": W, "height": H}`
   (W × H = the sequence's frame size).
3. `"${BASHCUT_PYTHON:-python3}" <plugin dir>/plugin.py illustrate --scenes scenes.json --project <file.fcproj>` (or `--bridge
   127.0.0.1:<port>`): one batch in one locked style, imported with `media_import`, each item labelled
   AI-generated (`metadata.set`), placed on V2 with `timeline.place`. Refused rows come back in `data.failed`:
   rewrite and run those again, or change treatment.
4. Look at them all at their `at` times on one contact sheet; motion on a still with bcp:effects. A real person's likeness, a logo
   or a product shown as real is never generated.

Record the stage in `plan.log` (`{"stage": "visuals", "did": "<row count by treatment>", "evidence": "<contact
sheet path>"}`) and `file.save`. The review checks every row against the timeline (bcp:review: each row's `at`
against `bashcut.timeline.summary` and a frame) and runs `bashcut.review.run` on every output sequence, so a
picture over a caption or a frozen still is caught before the export.

## Report

Targets and sources, rows by treatment with shares (speaker on screen, graphics a minute, mean picture change),
what you rejected, the caption mode, targets left on purpose, which pictures are AI-generated (and with what
model).
