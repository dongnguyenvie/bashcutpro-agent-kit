---
name: vlog-daily
description: Recipe for a daily-life vlog (day in my life, routines, study with me): time-stamped moments, calm pace, diary voiceover or small captions, one music bed, soft look. Use after bcp:vlog-plan picks daily. Not for trips (bcp:vlog-travel). Triggers: "a day in my life", "daily vlog", "morning routine", "study with me", "một ngày của tôi", "vlog đời thường".
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
| Held picture | 1.5–4 s, longer while a line is said over it (T07 §3), always moving (a drift of 0.3–1.5 %/s, bcp:effects) | a window-light photo under the diary voice holds; a frozen screen with nothing said does not |
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

The time stamp look: bcp:captions-text (an installed `.fcgt` template, else `graphics.newText`; a series keeps its cards in a project template, `bashcut.template.save`).

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

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | 8–12 cuts a minute (BashCut beat-cut: daily vlog 8–12); moments 3–6 s, calm stretches 2–4 s, a quick sequence about 1 s a shot; nothing under 0.6 s outside a quick sequence |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | **0 s frozen.** Every photo, tripod or desk shot held over 1.5 s with nothing said over it drifts at 0.3–1.5 %/s (bcp:effects); the last shot keeps moving to the end or fades out over 0.5–1 s; no clip runs past the end of its media and no `clip.frameHold` (both repeat one frame). A study-with-me desk shot is a `longStill` by design: keep it with a reason |
| Captions | `bashcut.captions.create {maxChars: 20, lines: 2, maxCps: 20, breakSeconds: 0.4}` + `captions.setStyle {track: "C1", size: 36, margin: 0.23}` vertical (1080×1920; all caps: `size` 32); `{maxChars: 42, lines: 2, maxCps: 20, breakSeconds: 0.5}` at the default size landscape (bcp:captions-text) | ≤ 20 characters a second (none over 25; `after.atOrUnder` aim 100 %), ≤ 42 characters a line, 2 lines drawn, each cue starting and ending on a word edge; again after every cut |
| Safe area | `bashcut.profiles.get {profile}` (`safeArea`, `safeAreaPx`) **before** placing any text | captions at `margin` 0.23 on `tiktok`, `reels`, `shorts` (the review wants the box 2 % above the 20 % bottom band) and 20 characters at `size` 36 clear the right band (130 px; at 40 "ramen place downtown" drew 21 px into it); titles and stamps below the top band (`reels` 14 %, 269 px; `tiktok` 8 %, `shorts` 10 %) and left of the right band; `bashcut.review.run {profile}` measures every caption box: a blocking `safeArea` / `lines` finding's `limit` (`marginAtLeast`, `sizeAtMost`) goes into `captions.setStyle`, or a smaller `maxChars` into `bashcut.captions.create` |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `morning-light`, `soft-pastel`, `cafe-warm`; `golden-hour` for an evening outside |
| Time cues | `bashcut.timeline.summary` (text clips on the title track) | a time stamp at each new part of the day, held letters ÷ 15 + 1–1.5 s |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`; `youtube` for long-form. `blocking` must be 0: fix
the findings (each has seconds and a `fix`) in one `bashcut.batch`, run the review again, at most 3 rounds; warnings
are fixed or kept with a reason in the plan; what still blocks after round 3 goes to the user. Then
bcp:vlog-publish: one `bashcut.profiles.apply` per output.

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
