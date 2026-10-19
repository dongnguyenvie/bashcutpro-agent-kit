---
name: review
description: Review a BashCutPro edit before export as a capped loop of 1-3 rounds: limits chosen from sourced ranges, measure what can be measured (cut list against the words, frames at phone size at every cut and text, scopes, loudness of a WAV export), judge each finding by what a viewer perceives, fix, re-measure, with an independent critic sub-agent. Triggers: "review", "kiểm tra video", "soát lỗi", "xem lại bản dựng", "chấm bản dựng", "QC", "trước khi xuất", "check my edit".
---

# Reviewing an edit

Measure, look, judge by what a viewer perceives, fix, measure again. Passing checks is not proof of a good video:
one tool's edit had all 29 actions on the beat and every cut on a bar line, and still had cramped frames, small
text and titles over the icons: "the model will satisfy whatever can be quantified" (guizang). Look at the pixels.

BashCutPro measures less than BashCut did. Nothing reads loudness, black or frozen frames or text contrast without
help: loudness comes from a WAV export (`bcp:audio-mix`'s `loudness.py`), black frames from `scopes.read`, the rest
from your eyes on rendered frames. Say what you could not measure; never report it as passing.

## Severity: what the viewer perceives

By the viewer at normal speed and size on a phone, not by the metric:

- **blocker**: noticed and hurts understanding or trust: a black or frozen frame, a gap, a clipped word, unreadable
  or covered text, speech drowned by music, a missing promised moment, a hook that does not show the topic, wrong
  length or shape for the output.
- **polish**: visible only paused, zoomed or side by side. Fix when cheap; never a reason for another round.
- **taste**: a viewer could like it either way (pace, look, transition): ask the user.
- **needs user**: only the user can supply or decide it (a missing shot, the music, a name to spell).

A measured warning is not automatically a blocker (a locked-off interview is a "long static shot", a deliberate
long title a "long still"): fix it, change the limit for this video, or keep it with a reason.

## Before round 1: the limits

Choose limits for this genre and footage from the ranges below, write them into the plan's `review` key in the
project notes (`bcp:edit-workflow`) with the source and reason, and tell the user. Platform numbers (length,
loudness, safe zones) come from the brief's outputs (`bcp:edit-workflow` REFERENCE "Export").

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

## Each round

1. **Read the edit once.** `sequence_inspect`: clips, gaps, tracks, length; `transcript.inspect` for the words;
   the plan from `project.notes`. Every stage the plan requires (effects, sound, colour) that is still open is a
   blocker, whatever else passes: one BashCut tutorial passed review with its effects stage not done, one zoom
   reused on every screen shot.
2. **Measure.** (REFERENCE.md has the exact calls.)
   - **Cuts against words**: every cut time from `sequence_inspect` against the word spans: a cut inside a word
     clips it; a caption or title more than the word-landing limit off its word.
   - **Gaps and black**: gaps in `sequence_inspect` on the main video track; `scopes.read {scopes: ["waveform"],
     seconds}` at each cut ± a few frames and at every gap: a luma maximum near 0 is black.
   - **Shot lengths**: from the clip list against the limits; runs of the same framing (`bcp:beat-cut`).
   - **Sound**: export the mix as WAV, `loudness.py --curve`: silences over the limit, jumps between sections,
     true peak; voice and music stems with `--speech` for the bed under the voice (`bcp:audio-mix`).
   - **Colour jumps**: `scopes.read` at the middle of neighbouring clips; a jump between clips meant to match
     goes to `bcp:color-grade`.
   - **Length and shape** against the plan and the outputs.
3. **Look in batches.** Frames at every cut and every text, the opening and the ending:
   `contact_sheet.py plan --program --at …` (in `bcp:footage-survey`), one `command_batch`, then `sheet`. Text at
   the width a viewer sees: `render_frame {seconds, max_side: 400}` (360–420 px). A cut in doubt: frames at
   ±0.4–1.5 s at 10–12 fps, wider for dialogue cuts, narrower for beat cuts.
4. **Critic, always.** Hand the review to the `critic` sub-agent (`agents/critic.md`) with only the plan's brief,
   the sequence and the round: without your reasons it sees what a viewer sees. No sub-agent (Codex): audit
   yourself by `<skill_dir>/../../agents/critic.md`, and say the audit was your own.
5. **Decide each finding** by severity: fix it (one batch of commands per area, through that area's skill), change
   the limit when it is wrong for this video (say why), keep it with a reason, or list it for the user. Never hide
   a fault with a transition or a flash.
6. **Measure each fix again** with the same measurement that found it. Say "fixed" only with the new number:
   "looks better" does not count. Then look only at what changed (`history.list` shows the round's edits).
7. **Log the round** in the plan's `log` (fixed, kept with reasons, left).

| Finding | Look and measure | Fix with |
|---|---|---|
| black, frozen picture, gap, long static shot | `render_frame`, `scopes.read`, the clip list | `bcp:beat-cut`, `bcp:effects`; a gap: `sequence.closeGap` |
| jump cut, repeated framing, cut inside a word | frames around the cut, cut times vs words | `bcp:rough-cut`, `bcp:beat-cut` |
| cut or text off the beat or the word | cut and text times vs beats (`bcp:beat-cut` `beats.py`) and words | `bcp:beat-cut`, `bcp:captions-text` |
| text in a safe zone, too small, overlapping, low contrast, over a face or burned-in text | `render_frame {max_side: 400}` at the text; face and text boxes from the `bashcut.vision` sidecar when there is one | `bcp:captions-text` |
| no hook, slow opening | the first 3 s: frames, words, first text | story (`bcp:edit-workflow`), `bcp:captions-text` |
| dead air, music gaps, voice drowned, one SFX repeated like a machine gun | `loudness.py` on the mix and stems | `bcp:audio-mix` |
| live speech and voiceover at different levels | each speech stem within ~2 LU, music 15–20 LU under | `bcp:audio-mix` |
| a restart or a phrase said twice | suspect words from the survey, the words around each cut | `bcp:rough-cut` |
| colour jumps between clips | `scopes.read` per clip, `render_frame` | `bcp:color-grade` |
| a promised shot or line missing | the plan's cut list against `sequence_inspect` and the words | `bcp:rough-cut`, ask |
| loudness, true peak of the delivery | a WAV export with the delivery's `loudnessLufs`, `loudness.py` | `bcp:audio-mix` |

## Rounds and stopping

- Cap: the rounds limit above (never more than 3).
- From round 2, first confirm the previous fixes, then **only a new blocker fails the round**. New polish and
  taste findings are listed, not chased: rubric creep is how loops never end.
- Stop early when a round fixes nothing. What is left goes to the user with reasons, never silently shipped.
- A finding that repeats (the same kind in two rounds, or one a lesson already names: `python3
  <skill_dir>/../self-learn/knowledge.py lessons --query "<words>"`) becomes a lesson or `--seen` on the old one,
  with `bcp:self-learn`.

## The draft

Loudness and the delivered file are measured last, from a normalized export (`file.exportMedia {loudnessLufs,
wait: true}`, `bcp:edit-workflow`), plus a WAV export at the same settings for `loudness.py`. Review once more,
then the draft gate.

## Report

A few lines: rounds; whether the critic or you audited; fixes (finding → edit → new number); limits changed and
findings kept, with reasons; what needs the user; what was not checked (sound by ear, motion between frames,
text contrast by number). Example: "Review: 2 rounds, critic audited. Closed a 1.2 s gap at 0:41 (now 0 gaps),
raised the caption out of the Reels bar. Kept: the 9 s shot at 0:12 (locked-off interview). Not checked: the music
under your voice by ear."
