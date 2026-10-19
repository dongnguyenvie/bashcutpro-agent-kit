---
name: vlog-product-review
description: Recipe for a product review or unboxing: a verdict or price-question hook, what it is, two to four points shown in use with pros and cons, a verdict card with the price and who it is for, sponsorship disclosed early, true-to-life colour. Use after bcp:vlog-plan picks product-review. Triggers: "product review", "unboxing", "is it worth it", "review sản phẩm", "đập hộp", "có nên mua", "đáng tiền không", "so sánh".
---

# Product review

Reply in the user's language. Survey, choose values from the ranges below and write them into the plan with
bcp:vlog-plan, then edit with bcp:edit-workflow. A measured reference replaces these ranges. Outputs: vertical →
TikTok, Reels, Shorts; long-form review → YouTube 1080p. An ad that sells the product rather than judging it:
bcp:vlog-product-ad.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Cut rate | about 10–14 cuts a minute (T07 §3) | dense spec talk holds longer, within the 2.5–6 s vlog band; a quick unboxing cuts faster |
| Detail insert | 1–1.5 s between talking shots, so a claim always has a picture | a spec to read holds longer |
| Longest shot | the top of the talking-shot length; one hero hold (the reveal) at 1.5–2.5× the average (T07 §3) | landscape long-form holds much longer |
| Product photo or held hero | 1.5–4 s, longer while a line is said over it (T07 §3) | a spec card to read holds longer |
| Hook | 2–3 s vertical; long-form up to 3–5 s (T07 §3) | the price question must land inside it |
| Talking parts | as bcp:vlog-talking-head (pauses, punch-ins, framing) | — |
| Captions and numbers | vertical 15–32 characters, 1–2 lines; numbers held for reading time (T09 §3) | long specs need a card instead of a caption |
| Music under the voice | 5–18 dB under, light (T11 §3) | the product's own sound (a click, a motor) leads when it is the point |

## Structure (45–90 s vertical)

Sample lengths, not slots: the plan gives each section its own range and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 2–3 s | hero shot + the verdict as a question with the price ("3 TRIỆU CÓ ĐÁNG?"), never "hôm nay mình review…" |
| What it is | 4–6 s | unboxing or the product in hand, name and a price tag |
| Points ×2–4 | 8–12 s each | one claim each, shown not told: the feature in use, then the result; a section chip ("1/3 · PIN"), pro and con labels |
| Verdict | 3–5 s | a verdict card (score or "NÊN MUA nếu…"), who it is for |
| CTA | 2–4 s (T14 §3) | where to buy, or "comment câu hỏi" |

Chips, labels and cards: bcp:captions-text / bcp:motion-graphics (an installed `.fcgt` template, else
`graphics.newText`; the vlog library looks are not ported yet).

## Cuts and motion

- Hero shots: a slow push-in or orbit (a Ken Burns drift on a still, bcp:effects).
- Talking parts follow bcp:vlog-talking-head (punch-ins, short caption groups).

## Rhythm, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Pattern interrupt | each point is a new beat; 8–12 s points sit inside the 10–30 s band, long-form 30–90 s (T07 §3) | long-form needs inserts inside each point |
| Hook and verdict | the verdict answers the hook's question; the hook promises only what the points pay off (T14 §4) | — |
| Transitions | hard cuts between talking and inserts; a zoom hit on the reveal; a short dissolve between points (T08 §7) | an unboxing montage may whip; say so |
| Transition budget | special transitions 1–3 a minute of short form (T08 §3) | landscape long-form uses fewer |
| Section chip | 2–3 s at the point's start (T13 §7) | longer labels need longer |
| Pro / con labels | entrance 0.15–0.6 s ending on the claim word (T13 §3, §7) | energy |
| Spec card | one idea 3–8 s, held through its line; a comparison table 8–14 s (T13 §3) | words on the card, narration length |
| Graphic density | 3–8 a minute of talking footage (T13 §3) | dense specs high; a feel-based review low |

## Shots

Hero (product alone, clean background), unboxing hands, every claimed feature in use, the result (a photo it took,
the battery %, the skin after), the person using it, a size comparison. A claim without its shot: cut the claim or
show the spec as text.

## Text, sound, look

- Every number on screen (price, battery hours, weight). Pros green, cons red.
- Sponsored or gifted: said in the first seconds and on screen ("Hợp tác cùng …"); ask the user.
- Sound: light music under the voice, a click or pop on labels, the product's real sound when it has one.
- Look intent: true-to-life colour (the product's real colour matters more than mood), clean whites; product shots
  graded to match each other. Measure first (bcp:color-grade).

## Review notes

- Blockers: a claim with no picture, a number said but not shown, the product's colour wrong, a sponsored video
  that does not say so early.
- Deliberate: repeated framing in the talking parts, held spec cards.
- `needs_user`: sponsored or gifted and the disclosure wording, the price and where to buy, the user's own verdict.

## Plan data

- `stages`: `{"colour": {"required": true, "why": "the product's true colour"}, "captions": {"rules": ["every number said is on screen"]}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "each claim gets a detail shot, a number card or the face"}}`
- `checks`: `claim-shown` every claim has its picture; `numbers-on-screen` every number said is shown; `true-colour`
  the product's colour matches the real one; `disclosure-early` sponsored or gifted said in the first seconds;
  `verdict` a verdict that says who it is for.
- `askAtIntake`: `["sponsored", "truthSource"]`.
