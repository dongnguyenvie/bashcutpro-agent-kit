---
name: vlog-tutorial
description: Recipe for a tutorial or tool demo: the result first, dead air cut from measured silences (loudness.py --tighten) and silent waiting sped up, numbered steps with step cards, one zoom per narration line onto what is clicked, presenter levelled to the voiceover, limits and next steps; landscape plus a vertical cut. Use after bcp:vlog-plan picks tutorial. Triggers: "tutorial", "how to", "software demo", "screen recording", "video hướng dẫn", "demo phần mềm", "cách làm", "từng bước", "quay màn hình".
---

# Tutorial and tool demo

Reply in the user's language. Survey, choose values from the ranges below and write them into the plan with
bcp:vlog-plan, then edit with bcp:edit-workflow. A measured reference replaces these ranges. Outputs: landscape →
YouTube 1080p plus a vertical Shorts cut; vertical-first (a 30–60 s tip) → Shorts, TikTok, Reels.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Longest shot | the next visual change at most 15 s apart in some long-form sources, 30–45 s in others (T07 §3, a contradiction) | a zoom or click inside one screen shot is a change without a cut; vertical tips cut much faster |
| Frozen screen | at least the reading time of what is on it: letters ÷ 15 + 1–1.5 s; key text held ≥5 s (T09 §3, §7) | a dialog to read holds; a loading spinner does not |
| Speechless stretch | look again at any stretch over 10–20 s with no speech: silence is not empty picture in a demo (T06 §3) | a silent demonstration may be the step itself |
| Shortest shot | long enough to see the click and its result | a vertical tip cuts tighter |
| Zoom onto the screen | 1.5–2.5× as a start, eased, within the clip's headroom; one framing per narration line, aimed at the panel it names | a Retina recording in a 1080 sequence zooms without upscaling; a 1080 recording does not; a small panel needs more |
| Live speech beside the voiceover | each camera clip within about 2 LU of the voiceover | camera mics differ by 15–20 dB; one presenter sat at −31 LUFS against a −17.5 LUFS voiceover |
| Hook | 5–7 s landscape; a vertical tip 1.5–3 s | the result must play with its own sound before the explanation |
| Captions | landscape 6–8 words or 32–42 characters × 2 lines; vertical 15–32 characters (T09 §3, §7) | landscape takes a sidecar file, vertical burns them in (T09 §7) |
| Music under the voice | 15–20 dB under the quieter voice (the deep end of T11 §3's 5–18), or none | dense instruction needs every word; a bed set for the voiceover sat only 0–4 LU under the presenter |

## Structure (1–3 min landscape, 30–60 s vertical)

Sample lengths, not slots: the plan gives each section its own range and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 5–7 s | the **result** (the finished output, with its own sound) + one line on what the viewer will be able to do |
| Intro | 3–5 s | the presenter: who and why, one sentence |
| Steps ×3–6 | 15–40 s each (5–10 s vertical) | a step card ("BƯỚC 1"); show the action, zoom onto it, say why |
| Result | 5–10 s | the output again, now understood |
| Limits | 3–5 s | what it does not do, a warning sticker |
| CTA | 2–3 s | link, next video, "comment nếu bị lỗi" |

Step cards and stickers: bcp:captions-text / bcp:motion-graphics (an installed `.fcgt` via
`graphics.template.apply`, else `graphics.newText`; the vlog library looks are not ported yet).

## Turn budget (BashCutPro#219)

A tutorial is the longest recipe (tighten, cards, zooms, captions, presenter, Shorts cut). In a batch it ran out of
turns at 80 by checking each card and zoom with its own `render_frame` (34 calls) and listing commands again and
again (14 `command_list`). Keep it well under 100 turns: the ids and params of `effects.setParam`,
`graphics.newText`, `bashcut.captions.create`, `clip.speedDuration` and `sequence.addEditAllTracks` looked up once
(`<kit>/scripts/commands.json`), one `bashcut.batch` per stage (all steps' zooms and cards together is fine), one
contact sheet per look, one `bashcut.captions.create {dryRun: true}` before the real one, and `file.save` after
every stage. A batch pipeline running this recipe sets `maxTurns` 150.

## Pace: tighten first (bench numbers)

The bench tutorial lost on pace: Pro kept 191.6 of 192 s with 4 cuts, BashCut cut 171 s from the same recording
with 58 (about 20 a minute). Whisper hides pauses inside the next word ("Now" 1.90–5.34 s over a 3.2 s silence,
BashCutPro#203), so `transcript.removePauses` finds none: measure silence from the sound.

1. **Find the silences**: export the sequence mix as WAV (`file.exportMedia {path: "/abs/tmp/mix.wav", format:
   "wav", wait: true}`, audio only: 0.02 s for 24 s), then `python3 <skill_dir>/../audio-mix/loudness.py
   /abs/tmp/mix.wav --min-silence 0.8 --tighten 0.4`: `silences` in sequence seconds and `tighten.commands`.
2. **Look inside every silence of 2 s or more** (frames at its start, middle and end, `contact_sheet.py plan
   --program`): a still screen is dead air, cut it; a screen that changes (loading, a render, typing) is the step's
   action, speed it up instead.
3. **Cut dead air** in one `bashcut.batch {commands: tighten.commands, label: "Tighten pauses"}` (mark in, mark out,
   `sequence.extract` per silence, last first; one undo step). Drop the commands of the silences you speed up.
   Measured: 24.4 s → 15.5 s, no silence of 0.3 s or more left.
4. **Speed up the action**: `sequence.addEditAllTracks {time}` at both ends of the stretch, then `clip.speedDuration
   {clips: [the video and audio pieces], speed: 400–2000, ripple: true}` (measured: a 3.8 s wait at 800 % played
   0.48 s), and mute that piece's sound when it is only room tone (`clipMixer.set` level).

| Pace check | Target | Why it varies |
|---|---|---|
| Pause inside narration | at most 0.4–0.6 s kept (`--tighten 0.4`) | a pause before a result or a key line may stay 0.8–1 s |
| Dead air (no speech, still screen) | none over 0.8 s | a dialog to read holds its reading time (below) |
| Silent action (loading, rendering, typing) | sped 4–20×, or cut to its result | narrated action 1.5–2× |
| A visual change (cut, zoom, card) | every 5–15 s landscape, 2–5 s vertical | a zoom inside one screen shot counts |
| Cuts a minute after tightening | 10–20 landscape (BashCut's tutorial: ~20) | a dense screen holds longer |

Review afterwards: `cutInWord` findings at these cuts are Whisper's stretched words (#203). Keep them with that
reason when the cut sits inside a measured silence (`silences` above); every other `cutInWord` is real
(`bcp:review` "Cut into a pause"). Or correct those words' start times to the silence's end with `transcript.set`
(one end-to-end run did: review then passed). A still screen flagged `frozen` under narration is not a fault (#193).

## Cuts and motion

- Zoom onto the part of the screen each line talks about: one framing per narration line, aimed at the panel the
  line names, a new one where the screen changes (find changes with `clip.sceneEditDetection` and a look at frames).
  Build it with Motion scale and position keyframes (`effects.setParam`, bcp:effects) and check them all on one
  contact sheet at the lines' key words (below). Never one framing reused across the screen shots: one edit kept the same
  zoom 1.9 on every screen and missed each line's panel. Back out between steps.
- One `bashcut.batch` per step (one undo step): its zoom keyframes (`effects.setParam {clip, effect: "motion",
  param: "scale" | "position", value, time, keyframe: true}`, eased in 0.3–0.6 s) and its card (`graphics.newText
  {text: "STEP 2", size, position, seconds: 2.5, time, track: 1}` or the template). Then **one contact sheet for
  all steps** (`contact_sheet.py plan --program --at <every key word and card>` → one `command_batch` → `sheet
  --width 400`, bcp:edit-workflow "Look in batches"): on each cell the scaled screen must still cover the frame (a
  position past the headroom showed a black edge at 180 %) and the card stay clear of the panel in use. Fix the
  cells that fail in one more batch and one more sheet of just those times.
- Speed up typing, loading and waiting (above), or cut it; a frozen screen holds only while there is something to
  read.
- Presenter on an upper track at the bottom centre (landscape: a corner), captions between screen and face, never
  over the part being clicked.

## Presence, rhythm, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Presenter presence | 25–60 % of the runtime (T19 §3; one kit about 40 %, T13 §3). Audit it, do not cap it | a dense screen needs the room; intro, result and limits are the presenter's |
| Presenter size (picture in picture) | 0.25–0.6 of the frame width (T19 §3, a contradiction) | smaller over dense screen text; larger when the face carries the story |
| Demo speed | 1.5–2× when narrated over; 4–20× for silent waiting (T19 §3) | how much of the action must still read |
| Pattern interrupt | a zoom, a new step or a result every 10–30 s in a vertical tip; long-form sources say ≤15 s against 30–45 s (T07 §3) | a zoom inside one screen counts as a change |
| Transitions | hard cuts inside a step; a short cross dissolve (0.3–1.0 s) between steps; 0–1 special transitions a minute (T08 §3) | — |
| Step card | 2–4 s at the step start (T13 §7); key text held 5 s or more (T09 §3) | the label's length |
| Shortcut, menu path, value | on screen while said, held letters ÷ 15 + 1–1.5 s (T09 §3) | how long the path is |
| Graphic density | 3–8 a minute (T13 §3, §7) | a quick tip has fewer |

## Text, sound, look

- Captions from the presenter after the tightening (bcp:captions-text §2): `bashcut.captions.create {maxChars: 42, lines: 2,
  breakSeconds: 0.5}` (not `transcript.createCaptions`: it ignores reading speed; builds without it: `captions_fit.py
  group`) for landscape (the `youtube` profile writes the SRT sidecar), 26–32 × 2 for the
  vertical cut; target 90 % of cues at or under 20 cps. Every shortcut, menu path and value on screen ("⌘K → Export").
- Sound: the presenter's voice; mute the screen recording unless its sound is the result; a quiet bed or none.
  With a voiceover beside the presenter, level each camera clip to the voiceover (about 2 LU), set the bed 15–20 LU
  under the quieter voice and keep true peak under the ceiling (bcp:audio-mix).
- Words: cut restarts the transcript hides (a word lasting over about 1 s or low confidence in `transcript.inspect`:
  re-transcribe that window, bcp:footage-survey); a voiceover line never repeats the presenter's line beside it
  (bcp:voiceover).
- Look: leave the screen recording ungraded; grade only the presenter camera to natural skin (bcp:color-grade).

For the Shorts output, a vertical sequence of the hook and one step (bcp:vlog-publish).

## Review notes

- Blockers: screen text too small at phone width, a frozen spinner, a zoom that misses the click or panel the line
  names, the presenter covering the part in use, a presenter much quieter than the voiceover, the intro said twice.
- Do not pass review while the effects or sound stage is not done: do it, or record it skipped with the reason.
- Deliberate: screen shots held while there is something to read, the repeated framing of one recording.
- `needs_user`: private details on screen to blur or cut (emails, keys, names), the app version, the CTA link.

## Plan data

- `stages`: `{"effects": {"required": true, "why": "one zoom per narration line onto the panel it names, fast-forward waiting"}, "sound": {"required": true, "why": "camera speech levelled to the voiceover, music 15-20 LU under both"}, "colour": {"rules": ["leave the screen recording ungraded; grade only the presenter"]}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "each step gets the screen, a zoom or a step card"}}`
- `checks`: `paced` no dead air over 0.8 s and silent waiting sped up (loudness.py `silences` after the edit), 10–20 cuts a minute; `result-first` the hook shows the output; `screen-readable` screen text reads at phone width;
  `zoom-on-click` each line's zoom lands on the panel or click it names, one framing per line; `presenter-clear` the
  presenter never covers the part in use; `private-hidden` no email, key or name on screen; `shortcuts-shown` every
  shortcut and menu path on screen; `voice-match` live speech within about 2 LU of the voiceover, music 15–20 LU
  under; `no-restart` no restart or phrase said twice.
- `askAtIntake`: `["privateOnScreen", "ctaLink"]`.
