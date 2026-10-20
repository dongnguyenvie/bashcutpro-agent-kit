---
name: vlog-travel
description: Recipe for a travel vlog or guide, vertical by default: a cost or time hook, numbered place sections with place cards, a cost recap and a save CTA, with shot, rhythm, transition and graphic ranges. Use after bcp:vlog-plan picks travel, or for footage of a trip, city or route. Triggers: "travel vlog", "trip video", "check-in", "vlog du lịch", "review chuyến đi", "48h ở", "lịch trình".
---

# Travel vlog

Reply in the user's language. Survey, choose values from the ranges below and write them into the plan with
bcp:vlog-plan, then edit with bcp:edit-workflow. A measured reference replaces these ranges. Outputs: vertical →
TikTok, Reels, Shorts; landscape → YouTube 1080p.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Average shot | 3–4.5 s; 1–2 s in the hook and in lists (T07 §7) | longer with dense voiceover, landscape or a calm place, within the 2.5–6 s vlog band (T07 §3) |
| Longest shot | the top of the average band; one hero hold (the view at its best) at 1.5–2.5× the average (T07 §3) | a moving walking or drone take can hold; a locked-off view cannot |
| Shortest shot | about 0.6 s, under which bcp:beat-cut merges pieces (T07 §5) | a beat-cut list can go shorter on purpose |
| Photo or locked-off hold | 1.5–4 s, longer while a line is said over it (T07 §3) | a silent photo montage cannot hold |
| Jump cut | two clips of one place with the same framing back to back: fix with a punch-in | — |
| Hook | 2–3 s | later only when the number is said late and cannot move |
| Captions | vertical 15–32 characters, 1–2 lines; landscape 32–42 (T09 §3) | font width and size, speech rate |
| Music under the voice | the small end of 5–18 dB in montage parts, deeper under dense voiceover (T11 §3) | music carries a travel montage |

## Structure (45–75 s vertical)

Sample lengths, not slots: the plan gives each section its own range from the footage, and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | the most striking shot plus a hook question: a number the viewer wants (cost, hours, days) — "48H IN DA LAT / HOW MUCH?" |
| Sections ×4–6 | 6–8 s each | one place or step of the route; a section chip ("2/5 · CHỢ ĐÊM") as it starts, a place card with the name, a price tag when money is said |
| Recap | 4–6 s | the total (a cost table as stacked lines, or the route in one map shot) |
| CTA | 2–3 s | "LƯU LẠI ĐỂ ĐI NHÉ!" over the nicest wide shot |

The chip, card, tag and CTA looks: bcp:captions-text / bcp:motion-graphics (an installed `.fcgt` template, else
`graphics.newText`; a series keeps its cards in a project template, `bashcut.template.save`).

## Cuts and motion

- About 13–16 cuts a minute at 3–4.5 s a shot; faster in the hook and lists.
- Every still or locked-off shot moves: a Ken Burns drift (bcp:effects) at the rate below.
- Walking, driving and food shots: speed ramp through the boring middle (bcp:effects).
- Punch-in on a repeated framing: within the clip's headroom (source size ÷ sequence size) and while the framing
  still shows the place.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Tone bands | calm stretches 2–4 s a shot; urgent ones (a rush, a list) 0.4–1 s (T07 §3) | arrivals and views are calm; lists and transfers quick |
| Pattern interrupt | a new place, number or pace every 10–30 s short-form, 30–90 s long-form (T07 §3) | each place is one; a long walk needs one inside it |
| Breath before the payoff | one held 0.5–2 s moment before the best view, once or twice (T07 §3, §7) | a montage breathes on the drop |
| Transitions | between places a fast whip (0.2–0.4 s, same direction both sides) or a hard cut on a beat; inside a place hard cuts only (T08 §3, §7) | a calm landscape edit uses a short dissolve for time passing |
| Transition budget | special transitions 1–3 a minute of short form; whips 1–2 per short (T08 §3) | a many-place montage may use more as a declared motif |
| Ken Burns drift | 0.3–1.5 % a second, alternating direction (T08 §3) | bigger for short photos in a fast edit |
| Place card, section chip | at the section start, held letters ÷ 15 + 1–1.5 s (T09 §3) | longer names, busier backgrounds |
| Price tag | its entrance (0.15–0.6 s) ends on the word the price is said, held while said (T13 §3) | energy of the edit |
| Graphic density | about one card per section plus price tags, under explainers' 3–8 a minute (T13 §3, §7) | a cost guide has more numbers than a mood film |

## Shots to look for and to shoot

Establishing wide of each place, a detail (sign, food, ticket), the person in the place (selfie or from behind),
movement between places (feet, vehicle, window), the view at its best (sunset, night lights). No establishing shot:
the widest shot of the place, or a stock picture (bcp:stock-images), unlabelled and never named as the real place.

## Text, sound, look

- Captions from the voice (bcp:captions-text), bold outline, 3–6 words a line, above the platform's caption bar.
- Voiceover when the footage has none: one fact per section, sized with the voice's measured rate
  (bcp:vlog-hook-script, bcp:voiceover). A number said is always on screen (price, time, distance).
- Sound: upbeat bed ducked under the voice; each place's natural sound for the first second of its section; a whoosh
  on the whips (bcp:audio-mix).
- Look intent: bright, warm and clean, skies not blown out, skin natural; one look for the video, night shots may
  stay cooler. Measure first and grade to the intent (bcp:color-grade), never fixed numbers.

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | 13–16 cuts a minute (BashCut beat-cut: travel 13–16); 3–4.5 s a shot, 1–2 s in the hook and lists; nothing under 0.6 s |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | No frozen picture: every photo or locked-off view held over 1.5 s with nothing said drifts at 1–1.5 %/s, alternating direction; one hero hold may run 1.5–2.5× the average, moving |
| Captions | `transcript.createCaptions {maxChars: 32 (vertical) or 42 (landscape), lines: 2, minSeconds: 1.2, gapFrames: 0}` | ≤ 20 characters a second (none over 25), ≤ 42 characters a line, 2 lines, each cue starting and ending on a word edge |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `travel-vivid`, `clear-sky` (bright day), `golden-hour`, `city-night` (night), `teal-orange` (cinematic) |
| Places and prices | `transcript.search` for each place name and price said | each has its card, landing on the word (±0.3 s) |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`; `youtube` for landscape. `blocking` must be 0: fix
the findings (each has seconds and a `fix`) in one `bashcut.batch`, run the review again, at most 3 rounds; warnings
are fixed or kept with a reason in the plan; what still blocks after round 3 goes to the user. Then
bcp:vlog-publish: one `bashcut.profiles.apply` per output.

## Review notes

- Blockers a viewer notices: a place named but never labelled, a price said but not shown, a photo frozen with
  nothing said over it, two clips of one place with the same framing back to back.
- Deliberate: a long walking or drone take that keeps moving, the one hero hold, quick cuts in lists.
- `needs_user`: prices and place names, the route order when capture times are missing, whether stock or generated
  shots may fill a missing place, the music.

## Plan data

- `stages`: `{"captions": {"rules": ["place card at each location change; a number said is on screen"]}}`
- `checks`: `place-labelled` every place named is labelled; `price-shown` every price said is on screen;
  `no-silent-still` no photo held with nothing said or heard; `route-order` places follow the route or capture time,
  or the plan says why; `place-framing` no two clips of one place back to back with the same framing.
- `askAtIntake`: `["stockAllowed"]`.
