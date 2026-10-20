---
name: vlog-promo
description: Recipe for a promo, hype or showreel (brand hype, portfolio, motion comic): beat cuts, kinetic type, rolling counters, a declared transition motif of two or three kinds, sourced numbers, only the person's own work. Use after bcp:vlog-plan picks promo (identity, not a sale). Triggers: "promo", "teaser", "showreel", "portfolio", "hype video", "video hype", "motion comic".
---

# Promo, hype and showreel

Reply in the user's language. A promo says who someone is and makes the viewer feel it: energy and identity, often
music only. It is not an ad (bcp:vlog-product-ad sells one product with a truth source and variants); a promo has no
offer and never shows a price. Plan with bcp:vlog-plan, edit with bcp:edit-workflow. RC = the Reelcrew / AgentVid
study (measured 2026-10-07: a 36 s vertical motion-comic hype and a 38 s landscape showreel, filmstrips at 0.1 s a
frame); T-notes as in the other recipes.

## Three shapes

| Shape | What it shows | Output |
|---|---|---|
| Brand or product hype | the name, what it does in 3–4 powers, a reveal | TikTok, Reels, Shorts; YouTube 1080p for a launch page |
| Profile or portfolio showreel | a person's journey, numbers, real work and events, then their name card (RC: 16:9) | YouTube 1080p; a vertical cut-down as its own sequence (`file.newSequence`) |
| Motion-comic hype | a comic "issue": cover, numbered powers, "to be continued" (RC: 9:16) | TikTok, Reels, Shorts |

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Cuts | 12–13.3 hard cuts a minute, 4.0–4.5 s a shot (RC: comic 13.3 / 4.0 s, showreel 12.6 / 4.2 s); inside a shot something changes about every 2.7 s (RC comic) | slower where a counter or timeline must be read |
| Cuts on the beat | every cut and wipe on a beat or bar (bcp:beat-cut) | a voiced hype cuts on the phrase first, the beat second |
| Long shot | 5–6 s, with constant motion: mean picture change far above card explainers (RC) | a name card at the end holds longer |
| Frozen picture | 0.5–1 s: still frames 0–2 % (RC) | a manifesto line on black may hold for its reading time |
| Hook | vertical: 1–2 s, the logo or first big word already moving (RC comic: first cut 0.1 s); a landscape showreel may build up to 8 s under a ghost word (RC: first cut 8.0 s) | a feed is scrolled past, a portfolio page is chosen |
| Kinetic word hold | 1–3 words a card, held letters ÷ 15 + 1–1.5 s (T09 §3) inside the 4 s shot | a counter's final value holds; a ghost word never needs reading |
| Captions | voiced: one line in a caption box, 3–6 words, keyword highlighted (RC comic); music-only: none | — |
| Speech coverage | voiced: 0.85–0.95 (RC: silence 3.0–3.5 %); music-only: none, and no gap in the music | — |
| Music under the voice | the small end of 5–18 dB (T11 §3): the music drives a promo | a soft voice needs more room |
| Transition budget | a declared motif, far over the 1–3 a minute of other short form (T08 §3): RC comic about one every 2.7 s | the motif is the identity; write it in the plan |

## Structure

Sample lengths, not slots: the plan gives each section its range and a named range marker.

| Shape | Parts (RC timings) |
|---|---|
| Motion-comic hype, 30–40 s | cover: logo burst, "issue #01" (0–6 s) → powers ×3–4, each a "POWER #0n" title, a counter "n/04" and one proof card (a checklist, a chat bubble, a flow) (about 6 s each) → reveal: logo, "coming soon / to be continued" (6–8 s) |
| Profile showreel, 30–45 s | ghost word and a one-line belief (0–10 s) → the journey: years rolling (2005 → 2021) with places and roles → impact counters (100+, 10,500+) → proof: real events, press, a photo grid → the manifesto in two big words → name card: photo, name, role, URL (last 3–5 s) |
| Brand or product hype, 15–45 s | the name or promise in the first 1–2 s → 3–4 powers or facts, one per shot → the logo and one line to remember |

## Type, counters and pictures

- **Kinetic type is the picture**: one to three words a card in a heavy face, entering on the beat; a giant ghost word
  scrolling slowly behind at low opacity (RC "COMPLEXITY"); a two-colour word for the manifesto ("BUILD / CAPACITY.",
  `graphics.setCharStyle`). bcp:motion-graphics sets the timing; an installed `.fcgt` via `graphics.template.apply`,
  else `graphics.newText` (a series keeps its cards in a project template, `bashcut.template.save`).
- **Counters roll fast**: 10 → 24 → 29+ in about 0.3 s (RC), then hold the final number with its label; a journey of
  years as a timeline.
- **Screenshots slide in** from the edge, tilted, over the number they prove (RC): the user's real product, site or
  press page.
- **Frame chrome**: a thin viewfinder frame with small labels ("01 / SIMPLIFY", a timecode) for a showreel; the logo
  and an issue counter "n/04" for the comic (RC). It stays put; only the content swaps.
- **Pictures**: the person's or brand's own work, photos, events and press only; stock only for textures and
  abstract backgrounds; generated art in one style for a comic (bcp:vlog-scene-prompt), never presented as real work.

## Transitions

Sized from the RC filmstrips at 30 fps; pick the nearest kinds from `effects.list` (bcp:effects), apply with
`sequence.applyVideoTransition`. A kinetic word can also take a kind as its own in and out.

| Moment | Kind | Duration |
|---|---|---|
| kinetic word to word, showreel | glitch (RGB split + jitter) | 3–6 frames (0.1–0.2 s) |
| comic panel to panel | halftone, often through a flash | 12–15 frames (0.4–0.5 s) |
| comic power to power | colour-stripe wipe or slide | 6–9 frames (0.2–0.3 s) |
| section to section, showreel | wipe or barn door in the accent | 3–6 frames |
| a hit on the drop | white flash or dip to black | 2–4 frames |
| card to card | swing | about 9 frames (0.3 s) |

Pick two or three kinds for the whole promo and repeat them: the repeated set is the identity.

## Truth rules (not taste)

- Every number on a counter is real and sourced (the user, a dashboard, a press page) and written in the plan; no
  rounding up past the source ("10,500+" only when 10,500 is true). No source: no counter.
- A showreel uses only the person's own work, roles and events; a client logo or TV appearance only when the user
  confirms it happened and may be shown.
- No invented testimonials, awards or "as seen on".

## Sound and look

Music first: one track with a clear beat, cut to it (bcp:beat-cut); a riser into the drop, whooshes on wipes, a
glitch hit on glitches, a paper or print sound on halftones (bcp:audio-mix, licensed or CC0). A voice, if any, on top
at its measured rate (bcp:voiceover). One palette, one heavy display face and one text face. Intent: a showreel dark
and restrained with one accent; a comic saturated and loud (RC: saturation 63 against the showreel's 48) with halftone,
sunburst and paper textures. Footage graded toward the palette (bcp:color-grade).

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | 12–13 cuts a minute, 4.0–4.5 s a shot with something changing inside about every 2.7 s; every cut within 2 frames of a beat from `bashcut.audio.beats {clip}` (or a bar for a voiced hype, on the phrase first) |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | Still frames 0–2 %: frozen picture 0.5–1 s at most (a manifesto line held for reading is kept with a reason); kinetic type and counters always move |
| Captions | `transcript.createCaptions {maxChars: 32 (vertical) or 42 (landscape), lines: 2, minSeconds: 1.2, gapFrames: 0}` | ≤ 20 characters a second (none over 25), ≤ 42 characters a line, 2 lines, each cue starting and ending on a word edge |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `punchy-shorts`, `teal-orange`, `silver-grit` (sport), `moody-green` |
| Beat sync | `bashcut.audio.beats {clip}` against the V1 cuts from the summary | 90 %+ of cuts within 2 frames (0.07 s at 30 fps) of a beat |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`; `youtube` for a showreel. `blocking` must be 0: fix the findings (each has seconds and a
`fix`) in one `bashcut.batch`, run the review again, at most 3 rounds; warnings are fixed or kept with a reason in
the plan; what still blocks after round 3 goes to the user. Then bcp:vlog-publish: one `bashcut.profiles.apply` per
output.

## Review notes

- Blockers: a cut off the beat, a word gone before it is read, a still frame, a counter ending on an unsourced number,
  three different transition looks fighting, the logo missing at the end.
- Deliberate: many transitions (the declared motif), 4 s shots with constant motion, music-only versions.
- `needs_user`: the shape, the numbers and their sources, which work, clients and events may be shown, the music,
  the brand.

## Plan data

- `stages`: `{"voiceover": {"required": false, "why": "music-led; a voice only when the user wants one"}, "rhythm": {"required": true, "skill": "bcp:beat-cut", "why": "cuts and wipes land on the beat"}, "effects": {"required": true, "skill": "bcp:motion-graphics", "why": "kinetic type, counters and screenshots are the picture"}}`
  (voiced: `voiceover` required, and `visuals` with bcp:visual-plan after the voiceover).
- `checks`: `on-beat` every cut and wipe on a beat; `numbers-sourced` every counter has a source; `own-work` only the
  person's own work and confirmed clients; `word-readable` every kinetic word holds its reading time; `nothing-still`
  no still frame beyond 1 s; `motif` transitions from the declared set; `logo-close` the name or logo at the end.
- `askAtIntake`: `["shape", "truthSource", "brandKit"]`.
