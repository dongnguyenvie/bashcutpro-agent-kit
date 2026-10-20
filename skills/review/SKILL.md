---
name: review
description: Review a BashCutPro edit before export as a capped loop of 1-3 rounds: bashcut.review.run on every output sequence, each finding fixed by its check (captions speed, cuts in words, gaps, frozen picture, loudness, true peak), measured from the timeline with one export per output, frames at phone size at every cut and text, judge each finding by what a viewer perceives, fix, re-measure, with an independent critic sub-agent. Triggers: "review", "kiểm tra video", "soát lỗi", "xem lại bản dựng", "chấm bản dựng", "QC", "trước khi xuất", "check my edit".
---

# Reviewing an edit

Measure, look, judge by what a viewer perceives, fix, measure again. Passing checks is not proof of a good video:
one tool's edit had all 29 actions on the beat and every cut on a bar line, and still had cramped frames, small
text and titles over the icons: "the model will satisfy whatever can be quantified" (guizang). Look at the pixels.

BashCutPro measures part of this itself: `bashcut.audio.loudness` (mix, track or clip: LUFS, true peak, clipping) and
`bashcut.review.pictureChecks {range?, samplesPerSecond?}` (black, frozen, long-still and flash stretches, in seconds).
Text contrast and the rest come from your eyes on rendered frames; a build without those ids falls back to
`loudness.py` on a WAV export (`bcp:audio-mix`) and `scopes.read`. Say what you could not measure; never report it as
passing.

## Severity: what the viewer perceives

By the viewer at normal speed and size on a phone, not by the metric:

- **blocker**: noticed and hurts understanding or trust: a black or frozen frame, a gap, a clipped word, unreadable
  or covered text, speech drowned by music, a missing promised moment, a hook that does not show the topic, wrong
  length or shape for the output.
- **polish**: visible only paused, zoomed or side by side. Fix when cheap; never a reason for another round.
- **taste**: a viewer could like it either way (pace, look, transition): ask the user.
- **needs user**: only the user can supply or decide it (a missing shot, the music, a name to spell).

A measured warning is not automatically a blocker (a locked-off interview is a "long static shot", a deliberate
long title a "long still"): fix it, change the limit for this video, or keep it with a reason. In a vertical
(short-form) review, a `longStill` with nothing said over it is a warning (BashCutPro#185): fix it unless the plan
says the hold is meant. It is the usual end-card trap: a 6 s near-still shot under the closing text reads as frozen.
Cut the still to 2–4 s, punch in or move it (Motion keyframes), or put a moving shot under the card.

## Before round 1: the limits

Choose limits for this genre and footage from the ranges below, write them into the plan's `review` key in the
project notes (`bcp:edit-workflow`) with the source and reason, and tell the user. Platform numbers (length,
loudness, safe zones) come from the brief's outputs: `bashcut.profiles.get {"profile"}` where the build has output
profiles (`loudnessLufs`, `truePeakDbtp`, `safeArea` as fractions of the frame), else `bcp:edit-workflow` REFERENCE
"Export".

| Limit | Range seen in other review tools | What moves it |
|---|---|---|
| black, minimum length that counts | 0.1–0.5 s | intended dips to black (a fade-through, an end card) |
| exact freeze | 0.8–1 s | a freeze on video media is usually a decode or render fault |
| longest shot with little motion | 3–6 s | genre: a calm vlog keeps long stills, a montage does not |
| silence in the whole mix | 2–5 s | ASMR or a calm vlog tolerates more; a gap inside speech is ~0.8 s |
| word landing (caption or title vs its word) | 0.1–0.3 s | correctness, not taste |
| text contrast | 3–4.5 : 1 | WCAG 2.x: 3:1 large text (titles), 4.5:1 body text (captions) |
| loudness tolerance | 1–2 LU | the platform and the delivery file |
| true peak | −1 to −0.5 dBTP | lossy codecs need −1 |
| length vs plan | 2–15 % | strict for ads and fixed slots, loose for vlogs |
| rounds | 1–3 | 1 when the user is waiting and nothing blocks; up to 3 unattended |

## Every output, every round

A review covers **every output sequence** (one per output in the plan: three clips are three sequences), not the
one that is open: the bench's podcast job shipped two clips with 5 blocking caption findings because only the active
sequence was reviewed. `bashcut.review.run` reads the active sequence only, so per output:

```json
{"id": "sequence.open", "params": {"item": 41}}
{"id": "bashcut.review.run", "params": {"profile": "shorts", "sequence": 41}}
```

(sequence ids from the plan's outputs or MCP `project_inspect`; the profile is that output's). Keep a table per round:
output, verdict, blocking, warnings, scores. An output is done when its verdict is `pass` and every warning is fixed
or kept with a reason.

**Measure from the timeline, export once.** Every round measures without rendering: `bashcut.review.run` (sound
from the mix, picture from sampled frames), `bashcut.audio.loudness`, `render_frame {max_side: 400}` at chosen times
only. No WAV or video export per round (the bench's renders took 5–10× BashCut's); the one export per output is
the draft (below).

## Each round

1. **Read the edit once.** `bashcut.timeline.summary` (clips, tracks, length in seconds; `sequence_inspect` when you
   need effect params or transitions); `transcript.inspect` for the words; the plan from `project.notes`. Every
   stage the plan requires (effects, sound, colour) that is still open is a blocker, whatever else passes: one
   BashCut tutorial passed review with its effects stage not done, one zoom reused on every screen shot.
2. **Measure** every output with `bashcut.review.run` as above: findings for sound, picture, captions and the edit,
   each with `check`, severity, range in seconds, the number and a fix, written as Review markers
   (`writeMarkers: false` to only read), a score per category and `verdict` (`needsFix` when anything blocks). What
   it lists under `skipped` (music over speech, caption safe area and contrast) and a build without it use the
   checks in REFERENCE.md. Caption findings exist only while the cues are captions: review them before
   `bashcut.captions.wordStyle` (`bcp:captions-text`).
3. **Look in batches.** Frames at every cut and every text, the opening and the ending:
   `contact_sheet.py plan --program --at …` (in `bcp:footage-survey`), one `command_batch`, then `sheet`. Text at
   the width a viewer sees: `render_frame {seconds, max_side: 400}` (360–420 px). A cut in doubt: frames at
   ±0.4–1.5 s at 10–12 fps, wider for dialogue cuts, narrower for beat cuts.
4. **Critic, always.** Hand the review to the `critic` sub-agent (`agents/critic.md`) with only the plan's brief,
   the output sequences and the round, plus the `bashcut.review.run` findings per output: without your reasons it
   sees what a viewer sees. No sub-agent (Codex): audit yourself by `<skill_dir>/../../agents/critic.md`, and say
   the audit was your own.
5. **Decide each finding** by severity and fix it with the table below: one `bashcut.batch` per area per sequence
   (one undo step each), through that area's skill. Change the limit when it is wrong for this video (say why),
   keep it with a reason, or list it for the user. Never hide a fault with a transition or a flash.
6. **Measure each fix again**: `bashcut.review.run` on the sequences you changed. Say "fixed" only with the new
   number: "looks better" does not count. Then look only at what changed (`history.list` shows the round's edits).
7. **Log the round** in the plan's `log` (per output: fixed, kept with reasons, left).

| `check` (category) | Severity in review.run | Fix |
|---|---|---|
| `readingSpeed`, `lineLength`, `lines`, `overlap` (captions) | warning over 20 cps, blocking over 25 / overlap | `captions_fit.py plan` → one `bashcut.batch` (`bcp:captions-text` §2); after a word style, undo it, fix, style again |
| `cutInWord` (edit) | blocking | move the cut into the nearest real pause (≥ 0.15 s, usually a phrase end), not to the word's edge: `timeline.trim {clip, edge, mode: "ripple", delta}` (REFERENCE "Cut into a pause"). A cut inside a measured silence is Whisper stretching the next word over the pause (BashCutPro#203): keep it with that reason |
| `gap` (edit), `black` inside the edit (picture) | blocking | `sequence.closeGap {track: "V1", time}` or fill it |
| `shortClip`, `shortGap` (picture) | warning | delete the sliver or `timeline.roll` the cut; `sequence.closeGap` |
| `offline` (edit) | blocking | relink or replace the clip |
| `frozen` (picture) | warning | a stuck video source or a frame hold: cut it or cover it (`bcp:beat-cut`). A still screen or a locked-off speaker **under speech** is not a fault (BashCutPro#193/#196): keep it with a reason |
| `longStill` (picture) | info (silent in a short-form edit: see Severity, #185) | the genre's limit: a punch-in or zoom (`bcp:effects`), or keep it |
| `flash` (picture) | warning | a dissolve or cut it |
| `loudness`, `loudSegment`, `silence` (sound) | blocking past 2 × tolerance, else warning | `bcp:audio-mix`: `bashcut.audio.polish {clips, profile}` on the voice, the bed's gain; the export by profile normalizes the mix |
| `truePeak`, `clipping` (sound) | blocking over 0 dBTP / ≥ 48 clipped samples, else warning | lower that clip's gain (`clip.audioGain`); the export's `peakCheck` re-exports when the file is over |

The bench counts a blocking finding as 25 points, a warning as 3, info as nothing: zero blocking on every output
first, then the cheap warnings (caption speed, a sliver).

## Rounds and stopping

- Cap: the rounds limit above (never more than 3; 2 fix rounds unattended, as `bashcut-batch` `fixRounds: 2`).
- From round 2, first confirm the previous fixes, then **only a new blocker fails the round**. New polish and
  taste findings are listed, not chased: rubric creep is how loops never end.
- Stop early when a round fixes nothing. What is left goes to the user with reasons, never silently shipped.
- A finding that repeats (the same kind in two rounds, or one a lesson already names: `python3
  <skill_dir>/../self-learn/knowledge.py lessons --query "<words>"`) becomes a lesson or `--seen` on the old one,
  with `bcp:self-learn`.

## The draft

One export per output, last: `bashcut.profiles.apply {profile, path, wait: true}` on each output sequence (its
size, bitrate, loudness and captions). It measures the exported file's true peak and exports again with a lower
limit when it is over (`peakCheck`: `truePeakDbtp`, `reexported`); report that number, not the setting. A `burn`
profile writes no SRT: export one first (`bcp:captions-text`). Where ffmpeg is installed, `ffmpeg -i out.mp4 -af
ebur128=peak=true -f null -` on the file gives integrated LUFS and true peak as the bench measures them. Then the
draft gate.

## Report

A few lines: rounds; whether the critic or you audited; fixes (finding → edit → new number); limits changed and
findings kept, with reasons; what needs the user; what was not checked (sound by ear, motion between frames,
text contrast by number). Per output: verdict, blocking, warnings, scores, LUFS and true peak of the file. Example: "Review: 2 rounds, critic audited. Closed a 1.2 s gap at 0:41 (now 0 gaps),
raised the caption out of the Reels bar. Kept: the 9 s shot at 0:12 (locked-off interview). Not checked: the music
under your voice by ear."
