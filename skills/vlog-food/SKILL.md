---
name: vlog-food
description: Recipe for a food vlog or review, vertical by default: the bite or pour with the price as the hook, a place card, quick process inserts, tasting reactions, a verdict and address, with insert, slow-motion, sound and look ranges. Use after bcp:vlog-plan picks food, or for eating, cooking or a street stall. Triggers: "food review", "food vlog", "mukbang", "review món", "review quán", "vlog ăn uống", "nấu ăn".
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
`graphics.newText`; the vlog library looks are not ported yet).

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
