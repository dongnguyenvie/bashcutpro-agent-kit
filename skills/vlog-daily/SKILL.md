---
name: vlog-daily
description: Recipe for a daily-life vlog (a day in my life, routines, study or work with me): time-stamped moments in order, a calm pace with holds and quick sequences, diary voiceover or small captions, one calm music bed, a soft look. Use after bcp:vlog-plan picks daily. Triggers: "a day in my life", "daily vlog", "morning routine", "study with me", "một ngày của tôi", "vlog đời thường".
---

# Daily vlog

Reply in the user's language. Survey, choose values from the ranges below and write them into the plan with
bcp:vlog-plan, then edit with bcp:edit-workflow. A measured reference replaces these ranges. Outputs: vertical →
TikTok, Reels, Shorts; long-form (YouTube, 4–10 min) → 1080p landscape.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Hold when something happens | 3–6 s (T07 §7); calm tone 2–4 s; about 8–12 cuts a minute (T07 §3) | pouring coffee or a view holds; landscape long-form and a calm voice hold longer, within the 2.5–6 s vlog band |
| Longest shot | the top of the hold band; one hero hold at 1.5–2.5× the average (T07 §3) | a study-with-me or long-form edit holds much longer; slow shots are the genre |
| Quick sequence | about 1 s a shot for 3–4 repeated actions (getting ready, cooking), then a longer shot | how many were filmed |
| Frozen picture | 1.5–4 s, longer while a line is said over it (T07 §3) | a window-light photo under the diary voice holds; a frozen screen with nothing said does not |
| Hook | 2–3 s | a quiet opening needs a time stamp or a question early |
| Captions | 3–6 words, small and low (T09 §7); vertical 15–32 characters, 1–2 lines; landscape 32–42 (T09 §3) | speech rate and frame shape |
| Pauses in the diary voice | keep 0.15–0.5 s breaths, scaled to the speaker's own median gap (T11 §3) | a slow, thoughtful voice keeps longer pauses |
| Music under the voice | 5–18 dB under, one calm bed (T11 §3) | music carries the wordless parts |

## Structure (30–90 s vertical)

Sample lengths, not slots: the plan gives each section its own range and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most interesting moment of the day, or a question or number ("5H SÁNG THỨC DẬY ĐỂ LÀM GÌ?") |
| Moments ×5–10 | 4–10 s each | in time order; a time stamp ("07:30 · SÁNG") at each new part of the day |
| Close | 3–5 s | the end of the day, a thought in one line, over a shot that still moves (a still under the closing card reads as frozen; BashCutPro#185) |
| CTA | 1–3 s | soft: "theo dõi để xem ngày mai" |

The time stamp look: bcp:captions-text (an installed `.fcgt` template, else `graphics.newText`; the vlog library
looks are not ported yet).

## Cuts and motion

- Let a shot breathe when something happens in it.
- Short sequences of quick shots for repeated actions, then a longer shot.
- Speed up commutes and long tasks (`clip.speedDuration`, bcp:effects) at the speeds below.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Tone bands | calm 2–4 s a shot; a quick sequence about 1 s a shot (T07 §3) | the mood of the part of the day |
| Pattern interrupt | a new part of the day, place or activity every 10–30 s short-form, 30–90 s long-form (T07 §3) | long-form changes less often |
| Breath | one held silence of about 2 s, once, before the close (T07 §3) | a diary voice with pauses already breathes |
| Transitions | hard cuts as the base; a cross dissolve of 0.3–1.0 s for time passing; a short dip to black for a jump in time (T08 §3, §7) | a documentary-style day dissolves; a fast routine cuts |
| Transition budget | 0–1 special transitions a minute besides the time-passing dissolves (T08 §3) | a playful routine may use more; say so |
| Speed | 2–4× for a commute or task under voice; 4–20× for silent waiting (T19 §3) | how much of the action must still read |
| Time stamps | at each new part of the day, held letters ÷ 15 + 1–1.5 s (T09 §3) | a busy background needs longer |
| Graphic density | low: time stamps and the odd keyword, far under explainers' 3–8 a minute (T13 §3, §7) | a study-with-me adds a timer |

## Shots

Wake-up, window light, hands doing things, the person in the room, outside, food, the work or study desk, a time
cue (clock, phone, sky). Missing time cues: put the time stamps on screen.

## Text, sound, look

- A diary voice: short sentences, first person, present tense; captions small and low.
- Sound: one calm bed for the whole video, ducked under speech; keep room tone and small sounds (cup, door)
  (bcp:audio-mix).
- Look intent: soft and bright, gentle contrast, a little warmth, consistent indoor and outdoor. Measure first
  (bcp:color-grade).

## Review notes

- Blockers: a frozen screen with nothing said, a jump in time with no cue, the music changing mood inside a moment.
- Deliberate: slow, long shots, held breaths in the diary voice, the same calm bed throughout.
- `needs_user`: what is private (other people's faces, addresses, screens), the music, whether to add a diary
  voiceover.

## Plan data

- `stages`: `{"voiceover": {"required": false, "why": "a diary voice only when the user wants one"}, "sound": {"rules": ["one calm bed for the whole video, ducked under speech"]}}`
- `checks`: `time-cues` each new part of the day has a time cue; `no-silent-freeze` no frozen screen with nothing
  said; `music-steady` the music never changes mood inside a moment; `privacy` no face, address or screen the user did
  not clear.
- `askAtIntake`: `["private"]`.
