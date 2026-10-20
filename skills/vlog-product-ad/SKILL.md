---
name: vlog-product-ad
description: Recipe for an ad or selling video (paid, commerce, UGC, launch, channel teaser): a truth source, hook and CTA as a pair, an arc chosen from what the product has, beat proportions, disclosure rules, one-change A/B variants as sequences. Use after bcp:vlog-plan picks product-ad. Triggers: "product ad", "sales video", "UGC ad", "quảng cáo", "video bán hàng", "TVC", "chạy ads", "UGC", "A/B test".
---

# Product ad

Reply in the user's language. An ad sells one thing to one audience; a review (bcp:vlog-product-review) judges it.
Plan with bcp:vlog-plan, edit with bcp:edit-workflow. A measured reference ad the user points to wins over every
range here (T15 §7). Outputs: vertical → TikTok, Reels, Shorts; feed 4:5 or square; landscape promo → YouTube 1080p.

## 1. Ad brief first

Fill these before writing a word, in the brief JSON in `project.setNotes` (each value with a status and a source):

| Field | What |
|---|---|
| audience and pain | who, and the problem they feel |
| one core benefit | the single thing to remember |
| proof that exists | a demo in the footage, a sourced number, a real review the user can share |
| CTA | one action: buy, visit, comment, follow |
| placement | paid feed, organic commerce or UGC, launch film; the outputs |
| truth source | product page, spec sheet or the user, for every claim |
| channel name, @handle, logo (teasers) | exactly as the user spells them; the logo as a file |

Ask them in one intake round (name, handle and logo as one question). No answer: decide and write it as inferred,
with the reason. Never invent a handle or a logo: without them, the brand name as plain text.

## 2. Hook and CTA as a pair

Write them together; the CTA pays off what the hook promises (T14 §4), with bcp:vlog-hook-script (2–3 openings on
the real footage compared before locking one). One message: an ad that argues a second point fails. Hook and offer
must read with the sound off. After the rough cut, read both ends and check the close answers the opening and the
product is on screen when the placement needs it.

## 3. Pick an arc from what you have

Choose the arc for something the footage has ("a visible before/after → Before/After"); examples, not slots (T14 §7):
PAS (a pain the audience feels), before/after (a visible change), demo loop (use is the proof), feature cascade
(several small features, one shot each), testimonial (a real customer or the creator's honest use), channel or brand
teaser (question → proof → reveal → a new loop: the CTA "follow @handle for the next one" opens the next).

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Promise | visual + verbal promise in 1–3 s; the full hook 2–8 s (T14 §3) | shorter for paid feed and commerce; longer for a launch film |
| Product first on screen | commerce with a cart link: within about 3 s; brand or launch: at the reveal, after the pain (T14 §3, a contradiction) | placement and arc; say which |
| Total length | 6–15 s paid cut-down; 15–45 s organic or UGC; 30–60 s launch or SaaS promo (T14 §3) | placement, proof, speech density; the platform cap is the only hard limit |
| Beat proportions | hook 10–15 %, problem 15–25 %, solution or demo 30–45 % (the longest), proof 15–25 %, CTA 7–15 % (T14 §3) | the arc; how long the product action takes |
| Montage / demo shot | 0.6–1.2 s in a music montage; 2–3 s per demo beat; longer for hero and proof (T14 §3) | music tempo; the action's length |
| Longest shot | the top of the demo band; one hero hold at 1.5–2.5× the average (T07 §3) | a demo that must be followed holds longer |
| CTA hold | 2–4 s paid social; 5–9 s when the end card carries a URL or logo (T14 §3) | CTA words and reading time |
| Re-hook | one per about 10–20 s; a soft mid-roll CTA only past about 20 s (T14 §3) | sources disagree on closing the loop before the CTA; record which |
| On-screen copy | about 6 words a frame or fewer; hook text up to about 60 characters in 9:16 (T14 §3) | font, hold, sound-off viewing |
| Speech rate | the speaker's or voice's measured rate (`transcript.inspect`); never sped up to fit (T02 §4, T14 §3) | speaker, language, voice |
| Music under the voice | 5–18 dB (T11 §3) | the product's own sound leads when it is the point |

## Truth rules (not taste)

- Every number, price, superlative and comparison has a source in the brief. No source: cut it or show only what the
  footage proves (T14 §7).
- One feature per shot, each shot new information. A claim without its shot is cut or shown as text with its source.
- Never invent capabilities, customers, reviews, numbers, urgency ("chỉ hôm nay") or logos (T14 §4).
- Sponsorship said in the first seconds and on screen, in the user's wording. AI-made people, voices or shots: no
  label on the video; the platform's upload toggle (bcp:vlog-publish).
- Price and offer exactly as the merchant states them; ask when unsure.

## Variants: change one thing

Variants are for a real A/B test only; a revision is made in place. Each changes **one** thing and shares the rest,
including the cut (T14 §3, §4):

1. Finish, review (bcp:review) and save the base version first.
2. One sequence per variant in the same project (`bcp:variants`: duplicated and named `<base> — <change>`); make
   only that change, review it.
3. Compare it with the base (`bcp:variants` `diff.py --one-change`): anything beyond the declared change is a
   mistake to undo.
4. Check one variant in every output shape at the hook and the CTA (`render_frame`) before making the batch.
5. Typical single changes: the hook, the opening shot, the CTA wording, the voice, the music.

Naming a winner needs real numbers: several hundred to about 1,000 impressions per variant over 3–7 days (T14 §3).

## Shots, text, sound, look

- Shots: hero (product alone, clean background), in use, the result, the pain (before), hands, scale against
  something known, the CTA background. Missing: stock (bcp:stock-images) or generated (bcp:vlog-scene-prompt).
- Offer and CTA cards with @handle and logo: bcp:motion-graphics (an installed `.fcgt` via `graphics.template.apply`,
  else `graphics.newText`; a series keeps its cards in a project template, `bashcut.template.save`). The offer readable on mute.
- One music bed under the voice, a sized sound on the reveal (bcp:audio-mix).
- Colour: true to life first, mood second; measure first (bcp:color-grade).
- Transitions: hard cuts as the base; a zoom hit or crash zoom on the reveal (bcp:effects); one or two special
  transitions a minute at most (T08 §3).

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | paid cut-down 30–60 cuts a minute in the montage (0.6–1.2 s a shot), demo beats 2–3 s; organic or UGC 15–25 |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | No frozen picture: the hero and the CTA card move (a 1–2 %/s push or a building element); the CTA card holds 2–4 s (5–9 s with a handle or URL) and still moves |
| Captions | `transcript.createCaptions {maxChars: 24 (vertical; 32 wrapped to 4 lines at the default size in a 1080-wide frame) or 42 (landscape), lines: 2, minSeconds: 1.2, gapFrames: 0}` | ≤ 20 characters a second (none over 25), ≤ 42 characters a line, 2 lines, each cue starting and ending on a word edge |
| Safe area | `bashcut.profiles.get {profile}` (`safeArea`, `safeAreaPx`) **before** placing any text | captions `captions.setStyle {margin}` at the bottom fraction + 0.01 (`tiktok`, `reels`, `shorts`: 0.21); titles and stamps below the top band (`reels` 14 %, 269 px; `tiktok` 8 %, `shorts` 10 %) and left of the right band; the review cannot see caption boxes, so check one `render_frame` |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `product-punch` (ad), `product-true` when colour is a claim |
| Hook and CTA | `bashcut.timeline.summary` | product on screen inside 3 s (commerce); CTA held 2–4 s |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`; `facebook-square` (−16 LUFS) for a square feed cut;
`youtube` for a launch film. `blocking` must be 0: fix the findings (each has seconds and a `fix`) in one
`bashcut.batch`, run the review again, at most 3 rounds; warnings are fixed or kept with a reason in the plan; what
still blocks after round 3 goes to the user. Then bcp:vlog-publish: one `bashcut.profiles.apply` per output.

## Review notes

- Blockers: the product missing from the opening (commerce), an offer unreadable on mute, a CTA gone before it is read.
- Montage shots under 1 s are the style.
- `needs_user`: the truth source, the placement, sponsorship wording, the exact price and offer, which variants, music.

## Plan data

- `promise`: the hook and CTA pair (§2).
- `stages`: `{"effects": {"required": true, "skill": "bcp:motion-graphics", "why": "offer card, CTA card with @handle and logo"}, "colour": {"rules": ["true-to-life product colour first"]}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "each line gets the product, a proof or a card"}}`
- `checks`: `claims-sourced` every number and claim has a source; `product-first` commerce: product on screen within
  the hook; `offer-on-mute` the offer reads with the sound off; `cta-hold` 2–4 s, 5–9 s with a handle or URL;
  `cta-handle` @handle and logo through the CTA (teaser); `new-loop` teaser: the reveal answers the opening and the
  CTA opens a new one; `disclosure` a sponsored ad says so early; nothing else is labelled on the video.
- `askAtIntake`: `["truthSource", "placement", "channelName", "handle", "logo"]` (the last three only for a teaser).
