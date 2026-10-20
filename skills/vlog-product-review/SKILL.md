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
`graphics.newText`; a series keeps its cards in a project template, `bashcut.template.save`).

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

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | 10–14 cuts a minute (BashCut beat-cut: review 10–14): talking shots 2.5–6 s with a punch-in every 4–6 s, detail inserts 1–1.5 s |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | No frozen picture: a held hero or spec card drifts at 0.3–1.5 %/s; a locked-off talking shot is a `longStill` only past 5 s: punch in or cut on a sentence before that |
| Captions | `transcript.createCaptions {maxChars: 24 (vertical; 32 wrapped to 4 lines at the default size in a 1080-wide frame) or 42 (landscape), lines: 2, minSeconds: 1.2, gapFrames: 0}` | ≤ 20 characters a second (none over 25), ≤ 42 characters a line, 2 lines, each cue starting and ending on a word edge |
| Safe area | `bashcut.profiles.get {profile}` (`safeArea`, `safeAreaPx`) **before** placing any text | captions `captions.setStyle {margin}` at the bottom fraction + 0.01 (`tiktok`, `reels`, `shorts`: 0.21); titles and stamps below the top band (`reels` 14 %, 269 px; `tiktok` 8 %, `shorts` 10 %) and left of the right band; the review cannot see caption boxes, so check one `render_frame` |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `product-true` (colour as sold); `clean-skin` or `warm-presenter` on the talking parts if they differ |
| Price and claims | `transcript.search` for the price and each claim | the price tag lands on its word; every claim has its shot within 1 s |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`; `youtube` for the long review. `blocking` must be
0: fix the findings (each has seconds and a `fix`) in one `bashcut.batch`, run the review again, at most 3 rounds;
warnings are fixed or kept with a reason in the plan; what still blocks after round 3 goes to the user. Then
bcp:vlog-publish: one `bashcut.profiles.apply` per output.

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
