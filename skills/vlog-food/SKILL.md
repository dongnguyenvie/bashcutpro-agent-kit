---
name: vlog-food
description: Recipe for a food vlog or review, vertical by default: the bite or pour with the price as hook, place card, process inserts, tasting reactions, verdict and address. Use after bcp:vlog-plan picks food. Not for product reviews (bcp:vlog-product-review) or trips (bcp:vlog-travel). Triggers: "food review", "food vlog", "mukbang", "review món", "review quán", "vlog ăn uống", "nấu ăn".
---

# Food vlog

Reply in the user's language. Survey, choose values from the ranges below and write them into the plan with
bcp:vlog-plan, then edit with bcp:edit-workflow. A measured reference replaces these ranges. Outputs: vertical →
TikTok, Reels, Shorts.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Insert length | 0.5–1.5 s (T07 §7); fast short-form averages 0.6–2 s (T07 §3) | shorter for high-motion, low-information shots (steam, sauce); longer when a price must be read |
| Longest shot | 2–4 s for bites and reactions; one hero hold (a plating reveal, a cheese pull) at 1.5–2.5× the average (T07 §3) | a talking verdict holds longer than a bite |
| Shortest shot | about 0.5 s (T07 §7) | quick inserts are the style |
| Held plate or photo | 1.5–4 s, longer while a line is said over it (T07 §3) | a menu board to read holds longer |
| Hook | 1.5–2 s | longer only when the price or question is spoken and cannot be cut |
| Slow motion | as slow as the source has real frames: sequence fps ÷ source fps (60 fps in a 30 fps sequence → 50 %, 120 fps → 25 %) | a 30 fps source at 50 % repeats frames and stutters: ramp or full speed instead |
| Punch-in on a reaction | up to the clip's headroom (source size ÷ sequence size), face and food still framed | a 4K source in a 1080 sequence has room; a phone 1080 clip has none |
| Captions | vertical 15–32 characters, 1–2 lines (T09 §3) | energetic talk 2–4 words a group, calm talk 3–6 (T09 §3) |
| Music under the voice | 5–18 dB under (T11 §3), dipping further under ASMR moments | the real sizzle and crunch lead (T11 §7) |

Slow motion is `clip.speedDuration` (speed in percent; bcp:effects for ramps).

## Structure (25–45 s)

Sample lengths, not slots: the plan gives each section its own range and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 1.5–2 s | the best bite, pull or pour in close-up, slowed if the source allows, with a price tag or a question ("45K CÓ ĐÁNG?") |
| Place | 3–4 s | sign or shop front + a place card (name · district), the price tag if not in the hook |
| Process | 4–8 s | 3–5 quick inserts (0.5–1.5 s): cooking, plating, sauce, steam |
| Tasting | 8–15 s | 2–3 bites, each: close-up of the food → the bite → the face; a pro or con label for what is said |
| Verdict | 3–4 s | a score or one-line verdict, price and address |
| CTA | 2–3 s | "LƯU LẠI ĐỂ ĂN THỬ" |

Tags, cards and labels: bcp:captions-text / bcp:motion-graphics (an installed `.fcgt` template, else
`graphics.newText`; a series keeps its cards in a project template, `bashcut.template.save`).

## Cuts and motion

- The fastest recipe: inserts and bites from the ranges above.
- Slow motion on pours, cheese pulls, steam and the first bite, at the speed the source allows; a punch-in on the
  reaction within headroom.
- A held plate gets a slow push-in rather than sitting still.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Tone bands | process inserts 0.5–1.5 s; tasting slower, 2–4 s a bite (T07 §3, §7) | a calm cooking video holds longer everywhere |
| Pattern interrupt | a new step, bite or verdict every 10–30 s (T07 §3) | a 30 s short changes almost every section |
| Breath before the bite | one near-silent 0.5–2 s moment before the first bite's sound, once (T07 §3; T11 §7) | an ASMR-style edit uses more |
| Transitions | a zoom hit into the dish at a section start; a fast whip between shops; none inside the tasting (T08 §3) | one shop needs almost none |
| Transition budget | special transitions 1–3 a minute of short form (T08 §3) | a declared motif (a whip every dish) may go over; say so |
| Price tag | entrance 0.15–0.6 s ending on the word the price is said, held while said and read (T13 §3) | a price read from a board needs longer |
| Stickers | at most one keyword sticker per bite, 0.5–2 s as an accent (T13 §3) | a review-style video uses pro/con labels on the claim word |

## Shots to look for and to shoot

Macro of the dish (top-down and 45°), the pour or pull, steam, the bite from the side, the face right after, the
shop front, the menu or price board, the cook's hands. Shoot pours and pulls at 60 fps or more when slow motion is
planned. No close-up of the food is the most common gap: say so before editing; a punch-in on a wider shot is the
fallback when headroom allows.

## Text, sound, look

- The price always on screen; one keyword sticker per bite at most.
- Sound: the real sizzle, crunch and slurp up front, music dipping under them; a short pop or ding on price tags
  (bcp:audio-mix for SFX).
- Look intent: warm, rich, appetising; never green-tinted or grey; highlights on sauce kept. Measure first
  (bcp:color-grade), no fixed numbers.

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | short form 20–40 cuts a minute (BashCut beat-cut: food TikTok 30–40): inserts 0.5–1.5 s, bites 2–4 s; a calm cooking video 10–14 |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | No frozen picture: a held plate or menu board drifts at 0.3–1.5 %/s; slow motion only at the speed the source has frames for (a 30 fps clip under 100 % shows as stutter or a `frozen` second) |
| Captions | `bashcut.captions.create {maxChars: 20, lines: 2, maxCps: 20, breakSeconds: 0.4}` + `captions.setStyle {track: "C1", size: 36, margin: 0.23}` vertical (1080×1920; all caps: `size` 32); `{maxChars: 42, lines: 2, maxCps: 20, breakSeconds: 0.5}` at the default size landscape (bcp:captions-text) | ≤ 20 characters a second (none over 25; `after.atOrUnder` aim 100 %), ≤ 42 characters a line, 2 lines drawn, each cue starting and ending on a word edge; again after every cut |
| Safe area | `bashcut.profiles.get {profile}` (`safeArea`, `safeAreaPx`) **before** placing any text | captions at `margin` 0.23 on `tiktok`, `reels`, `shorts` (the review wants the box 2 % above the 20 % bottom band) and 20 characters at `size` 36 clear the right band (130 px; at 40 "ramen place downtown" drew 21 px into it); titles and stamps below the top band (`reels` 14 %, 269 px; `tiktok` 8 %, `shorts` 10 %) and left of the right band; `bashcut.review.run {profile}` measures every caption box: a blocking `safeArea` / `lines` finding's `limit` (`marginAtLeast`, `sizeAtMost`) goes into `captions.setStyle`, or a smaller `maxChars` into `bashcut.captions.create` |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `fresh-food`, `cafe-warm` |
| Price and bite | `transcript.search` for the price; `bashcut.audio.loudness {range}` over the bite | the price card lands on its word; the crunch sits within 6 dB of the voice |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`. `blocking` must be 0: fix the findings (each has
seconds and a `fix`) in one `bashcut.batch`, run the review again, at most 3 rounds; warnings are fixed or kept with
a reason in the plan; what still blocks after round 3 goes to the user. Then bcp:vlog-publish: one
`bashcut.profiles.apply` per output.

## Review notes

- Blockers: food that looks grey or green, a price never shown, a crunch buried under music, slow motion that
  stutters (a 30 fps source slowed).
- Deliberate: inserts under 0.6 s, a held plating reveal as the hero hold.
- `needs_user`: price, shop name and address, whether the meal was free or sponsored (disclosure), the music.

## Plan data

- `stages`: `{"colour": {"required": true, "why": "food must look appetising"}, "sound": {"rules": ["real sizzle, crunch and slurp up front; music dips under them"]}}`
- `checks`: `price-shown` the price is on screen; `place-card` shop name and district on a card; `food-colour` no
  grey or green food; `bite-audible` the crunch is not buried; `slowmo-smooth` no stuttering slow motion.
- `askAtIntake`: `["sponsored", "shopAddress"]`.
