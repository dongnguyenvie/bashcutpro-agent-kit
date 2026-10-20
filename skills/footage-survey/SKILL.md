---
name: footage-survey
description: Survey footage before a BashCutPro edit: inventory, shot cuts found by scene detection, contact sheets from rendered frames, transcripts (Whisper build or an outside transcriber imported with transcript.set), recording cues and restarts, shot descriptions stored in metadata, missing coverage, silent audio, broken files, HDR or log, mixed orientation; a camera synced with a screen recording by sound. Use at the start of an edit; the surveyor sub-agent does it and returns hooks, quotes with times and angles. Triggers: "khảo sát footage", "xem footage", "contact sheet", "có những cảnh gì", "đồng bộ", "quay màn hình", "survey footage", "what's in this footage".
---

# Footage survey

Run this **first**, before promising anything about the edit. It reads and describes; it never edits the edit
sequence. **Then actually look at every sheet**, every cell: that is the whole value of this skill.

**Who does it.** In Claude Code, hand it to the `surveyor` sub-agent (`agents/surveyor.md` at the kit root) with
the goal (length, shape, platform, language, any angle) and the media ids; plan from its answer and never print the
transcript yourself. In Codex (no sub-agents), follow that same brief yourself: `<skill_dir>/../../agents/surveyor.md`.

## 1. Import and inventory

- `bashcut.media.import {paths}` (runs the plugins' import hooks; else `file.import {paths}` or MCP `media_import`)
  the whole folder's files in one call; importing does not touch a
  sequence. `project.items` lists them with their ids.
- Per file: `media.status` (offline, missing), `media.colorInfo` (transfer: HDR or log), CLI `bashcutpro probe
  <file>` (fps, size, rotation, streams, length).
- A scratch sequence holds the clips for the commands that need clips: `file.newSequence {name: "Survey",
  fromItems: [...]}` (back to back). Survey there; never in the edit sequence. `bashcut.timeline.summary` lists each
  clip's id, item and start / end in seconds on it.

## 1b. Measure (no export, no render)

On the survey sequence, in one pass, before looking:

| What | Command | Read |
|---|---|---|
| Sound per clip | `bashcut.audio.loudness {clip}` | `integratedLufs`, `truePeakDbtp`, `silent`; speech clips sit around −24 to −16 LUFS, a clip under about −35 LUFS has room tone or wind only (a noise-only test clip read −38) |
| Stuck, black, still | `bashcut.review.pictureChecks {}` | `frozen` (≥ 1 s unchanged), `longStill` (≥ 5 s), `black`, `flash` stretches in sequence seconds: a frozen stretch inside a video file is a decode fault or a phone pause; a locked-off shot shows as `longStill` |
| Music files | `bashcut.audio.beats {clip}` | `bpm` and beats in sequence seconds, for bcp:beat-cut |
| Camera cuts | `clip.sceneEditDetection` (below) | cuts per file |

These cost seconds; a WAV export and an outside script only when a number is missing here (`bcp:audio-mix`).

## 2. Look

```sh
python3 "<skill_dir>/contact_sheet.py" plan --item ITEM --seconds LEN --count 12 --dir /abs/tmp/frames/ITEM
```

prints the `file.exportFrame` steps for one `command_batch` (source frames, evenly spread); then

```sh
python3 "<skill_dir>/contact_sheet.py" sheet "/abs/tmp/frames/ITEM/*.png" -o /abs/tmp/ITEM-sheet.png
```

tiles them into one numbered sheet and prints each cell's source second. Read the image. Clips that change inside
need more cells: 3–6 per shot plus one every 10–15 s inside a long shot (other tools' range), fewer when the token
budget is tight; `--from/--to` zooms into a stretch. A frame at full size: MCP `render_frame {seconds}` on the
survey sequence, or one `file.exportFrame`.

**Shot cuts inside a file**: `clip.sceneEditDetection {clips, applyCuts: false, generateMarkers: true, wait: true}`
on the survey sequence marks the camera's own cuts (read them in `sequence_inspect`). `sensitivity` (default 50)
is the cut limit; screen recordings, fast action and dissolves each need their own: lower it when the sheet shows
a cut it missed. Numbers only point; the frame confirms.

## 3. Words

`transcript.models` says whether the build has Whisper. With it: `bashcut.transcript.generate {items, language, wait:
true}` for every clip with sound in one call (a clip with only music or ambience reports `noSpeech` or 0 words).
Without:
an outside transcriber on the clip's sound (export it: `file.exportMedia {format: "wav", range: "custom",
startSeconds, endSeconds}` over the clip on the survey sequence), then

```sh
python3 "<skill_dir>/words_to_transcript.py" whisper.json --item ITEM --language vi > params.json
```

and `command_run transcript.set` with that params object. It lists suspect words on stderr (REFERENCE.md has the
transcriber commands). Read with `transcript.inspect`, find with `transcript.search {query}` (its `start` and `end`
are ticks: ÷ 254 016 000 000 for seconds, and they are the first word's start and the last word's end, so a cut
there sits on a word edge); never print a long transcript twice.

**Speech rate**, per speaker: characters (Vietnamese: syllables) a second over the spoken stretches. Captions are
held to 20 characters a second: a speaker at 15–17 cps fits one 2-line cue per phrase, one at 20+ needs shorter cues
cut at word gaps (bcp:captions-text). Write the rate into the survey notes.

## Honesty and hygiene checklist

Say each of these plainly before planning; each one has spoiled a real edit somewhere:

- **Broken files**: camera cards hold ~1 KB stub `.MP4`s that fail to import; a moved file shows offline in
  `media.status`. Leave them out.
- **Variable frame rate** (phone screen recordings often are, `probe`): check sync and in-points on the frame, not
  by arithmetic.
- **HDR or log** (`media.colorInfo`): tell `bcp:color-grade` before anyone judges the colour.
- **Truncated audio** (the sound stream shorter than the picture in `probe`): cut before the sound ends.
- **Silent clips**: no audio stream, `bashcut.audio.loudness {clip}` reports `silent`, or it stays under about −35
  LUFS. Speech sits 10–15 dB over a clip's own floor (more margin in a quiet room, less on a street): a clip that
  never gets that far above its floor has no usable sound (`{clip, series: true}` gives the short-term curve). Plan
  voiceover or music.
- **Frozen inside a file** (`pictureChecks` `frozen` on a video clip): cut around it; it renders frozen in every
  output.
- **Portrait and landscape mixed**: phones often store 1920×1080 with a −90 rotation, which is portrait. Check it
  before choosing the sequence size.
- **fps**: other rates play fine, but true slow motion needs 50/60/120 fps sources.
- **Not transcribed or not looked at**: name them in the plan; never fill them with a guess ("no speech found" is
  not "silent" unless the levels say so).
- **Recording cues** and **restarts**: list each with media, seconds and kind before planning, so the plan never
  quotes one (REFERENCE.md, "Cues and restarts").

## Reading a contact sheet

| You see | Conclusion |
|---|---|
| Frames of one clip clearly differ | the clip has coverage and several usable moments |
| Frames of one clip are identical | locked-off camera: the clip gives **one** shot size |
| Many clips look alike | repeated scenes: the edit will feel monotonous |
| Rows with texture and no people (smoke, rain, objects, hands) | often the best cutaways: prioritise them |

## When coverage is missing, say so

No editing technique creates shots that were never filmed. Real case: two 4-minute clips, 22–24 frames each, all
nearly identical: 9 minutes of footage gave two shot sizes. Then:

1. State the limit, with the contact sheet as evidence.
2. Offer what can be saved: punch-in reframes (`bcp:beat-cut`), stock or illustration images, voiceover over
   b-roll.
3. Give a shot list for next time. Per location a few shots of about 10 s (long enough to trim both ends): hands
   doing something (close, fill the frame); the shop front or sign before entering; the food or product right when
   it arrives; walking feet or a slow pan of the space.

## Two recordings of one session (camera + screen)

Filename clocks lie (82 s and 101 s apart by name, 2.44 s by sound once the recording had been trimmed). Put both
on the survey sequence and `clip.synchronize {method: "audio", clips, reference}`; read the offset from the clips'
new positions (`sequence_inspect`). Check one moment on the frame (a click, a clap) before trusting it. Matching
caption sentences instead was too rough in BashCut (−1.5 to −4.8 s for a true −2.44).

## Time and place

Phones write a capture time and often a place (`probe`, `metadata.get`); most action cameras write neither, but
put it in the name: `DJI_20260808201922_0400_D.MP4` → 20:19:22 on 08/08. Use it for the order of the trip and for
place or time labels (`bcp:captions-text`). Subfolders may reuse the same clip numbers: keep the folder in the
description.

## Describe what you saw

Write each clip's shots down so other skills and later sessions need not look again:
`metadata.set {item, fields: {"Description": ..., "Scene": ..., "Log Note": ...}}`, one line per shot in
Description: `0–4.2 WS eye pan-left: market, vendor, 3 people; best 2.6 (looked 0.5, 2.6, 4.0)`. Sizes ECU…EWS,
insert. Facts only: no pairings or verdicts ("good opener"): those belong to the plan. Say how sure you are when you
saw one frame of a fast move. With the `bashcut.vision` plugin, `describe` hands you each clip's frames and
`describe-apply` keeps your descriptions in `<project>.vision.json`; `ocr` adds the on-screen text with boxes and
`subjects` the faces. Coverage gaps, silent clips, cues and restarts go into a `survey` key of the project
notes' JSON block (`bcp:edit-workflow`).

## Picking in-points

- Look at the frame full size before committing: motion blur hides at sheet size.
- Speech recognition invents text over music, crowd noise and silence ("hãy subscribe kênh…", "cảm ơn các bạn đã
  theo dõi"): drop lines like that, and treat a clip whose only text is that as having no speech. If the speech is
  in another language than the project, say so before cutting on it.
- After the survey, place only the clips you will use (`bcp:rough-cut`).
