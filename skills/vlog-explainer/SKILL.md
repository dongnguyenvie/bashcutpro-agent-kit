---
name: vlog-explainer
description: Recipe for an explainer with little or no footage: a question-and-number hook, one data graphic per section timed to the voice (table, chart, map, counter), fixed frame chrome, every number sourced, a voiced or music-only version. Use after bcp:vlog-plan picks explainer. Triggers: "explainer", "infographic", "knowledge video", "video giải thích", "video kiến thức", "lịch sử", "luật", "bất động sản".
---

# Explainer

Reply in the user's language. An explainer carries its meaning in the words and the graphics, not in footage: plan
the script and the facts first (bcp:vlog-hook-script), then one graphic per section that builds while the voice says
it. Plan with bcp:vlog-plan, edit with bcp:edit-workflow. RC = the Reelcrew / AgentVid study (30 explainer and promo
videos measured 2026-10-07); T-notes as in the other recipes.

Order: the script with sources → the voice (bcp:voiceover; numbers spelled out as heard, captions with digits) →
word times (`transcript.inspect`) → one graphic per section landing on its word (bcp:motion-graphics) → captions
(bcp:captions-text) → music and SFX (bcp:audio-mix). Place them together per stage with one `bashcut.batch` (one undo
step), not one by one. Data graphics wait for a graphics plugin: until then, an installed `.fcgt` (`graphics.template.list`,
`graphics.template.apply`) or plain `graphics.newText` and `graphics.newRectangle` built up line by line (a series keeps its cards in a project template, `bashcut.template.save`).

## Ranges

Outputs: vertical → TikTok, Reels, Shorts; landscape → YouTube 1080p (a 2–5 min science or history piece usually is, RC).

| Check | Sample range | Why it varies |
|---|---|---|
| Cuts | 0–1.5 hard cuts a minute: scenes change by a card swinging away, a dissolve or a graphic building (RC) | news and promos cut every 4–4.5 s (RC); a calm card piece does not cut at all |
| Long shot | one card per section is fine; judge pace by motion (RC) | a sequence of photos does cut: use the photo hold below |
| Frozen picture | 1–2 s: every picture drifts and every graphic builds (RC: still frames 0–14 % in voiced pieces; 14–66 % in older music-only kits, which read as slides) | a quote or dense table held to be read |
| Photo or illustration hold | 2–4 s with a Ken Burns drift of 0.3–1.5 % a second (T08 §3); 3–6 s under a line | a photo with a graphic holds while it builds |
| Hook | 1–3 s: a question and one big concrete number on screen ("Lãi thật mỗi đơn 37.000đ?", "938 · Trận Bạch Đằng") (RC) | landscape long-form may say the question over a title for 3–5 s |
| Speech rate | 165–236 syllables a minute in Vietnamese TTS explainers; silences 0–6 % (RC) | dense legal or science text sits low; size lines with the voice's measured rate |
| Dead air | 0.5–1 s between sections; one held beat before the payoff (T07 §3) | music-only: no gap in the music instead |
| Captions | one line of 3–6 words, keyword highlighted, on a pill (RC); vertical 15–32 characters (T09 §3); above the caption bar (TikTok covers the bottom ~24 %) | music-only: no captions, the cards carry the words |
| Speech coverage | 0.85–0.95 voiced (RC) | music-only: none |
| Music under the voice | the deep end of 5–18 dB (T11 §3): every word is information | music-only: music is the only layer |

## Structure (45–90 s vertical, 2–5 min landscape)

Sample lengths, not slots: the plan gives each section its range and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 1–3 s | the question + the big number, on a card or the most striking picture |
| Sections ×4–7 | 6–8 s each vertical (RC); 20–60 s landscape | chip "n/N" + header bar, one graphic that builds with the voice, one picture behind it |
| Recap | 4–6 s | the answer to the hook in one card: total, ranking, route, verdict |
| CTA | 2–3 s | save, follow, the next part |

**A housing project (bất động sản)**, 35–60 s vertical, four sections: 1 the project's photo or render, 3–5 s with a
drift, no AI or "minh hoạ" label (the platform's AI toggle at upload, bcp:vlog-publish); 2–3 routes to landmarks and
amenities in one map graphic, 8–10 s, every minute, km, count and "nearest" from a named map source, never counted by
hand, landmarks within ~6 km, a kind with none nearby left off (never shown as "0"); 4 the price with its source and
date, then the CTA, 4–6 s. Hook 1–3 s on the price or a count ("4 trường trong 1 km"); 0–2 cuts a minute.

## What each section shows

One graphic per section, chosen by what the words say, each landing on its word; bcp:motion-graphics decides what it
shows and how long it holds.

| The section says | Show |
|---|---|
| prices, costs, a budget | a cost table: rows adding up to a total |
| a comparison, a trend, a ranking | a bar chart |
| a day plan, a history, the steps of a process | a timeline |
| a system that grows across sections | one growing diagram for all of them |
| a place, a route, distances, travel times | a route map from a named source |
| conditions, rules, what to bring | a checklist card |
| one number that matters | a counter |
| a quote, a law article, a definition | a paper card |

Two sections in a row with the same graphic need a reason. Density sits at the top of 3–8 a minute (T13 §3).

## Pictures and frame chrome

- **Pictures**, in order: the user's own; stock (bcp:stock-images); public-domain or open archives (Wikimedia, NASA);
  cropped screenshots of a real source; generated illustrations (bcp:vlog-scene-prompt). Never present a generated
  picture as a photo of a real place, person or event.
- **One illustration style for the whole video** (RC: crayon, engraving, paper-cut collage, isometric): written in
  the plan with the prompt fragment that keeps it.
- **Frame chrome stays across scenes** (RC): section chip and header bar, the user's avatar or mascot in a corner if
  any; only the content swaps; inside the safe zone. No credit or licence line unless the user asks. A mascot only
  from the user's own image or an approved style.
- **Scene changes**: a card swings away as the next enters (0.3–0.45 s overlap; about 9 frames at 30 fps, RC); between
  photos a cross dissolve of 0.3–0.5 s, the title fading out first, then the picture, then the new title in (RC).
  Nearest kinds from `effects.list` (bcp:effects).

## Facts and honesty

- Every number, date, price, distance and legal claim has a source in the script beats: the user, an official page,
  an open dataset. A number without a source is called an example ("số liệu minh hoạ") or left out.
- Maps: real coordinates and route figures from the user or a named source, rounded on screen ("≈ 16 phút · 7,5 km").
- Law, health and money: name the law, article and date; say "check with a professional" when advice depends on the
  viewer's case.

## Two versions: voice or music only

The references ship both (RC). Music-only: the cards carry every word (held letters ÷ 15 + 1–1.5 s, T09 §3), no
captions, its own checks. Make it its own sequence (`file.newSequence`) or project copy (`file.saveCopy`), never a mix.

## Sound and look

Voice first at the measured rate, music deep under it, a soft whoosh on card swings and a tick on checklist items when
they help (bcp:audio-mix). The older music-only kits shipped 17 dB too quiet (RC): normalize per output. One palette
and one font family from the brand or a reference (bcp:style-study); a paper, kraft or dark textured background;
photos graded to the palette's warmth (bcp:color-grade); generated illustrations left as made.

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | 0–1.5 hard cuts a minute; a new card, picture or graphic step every 6–8 s (vertical), 20–60 s sections landscape |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | Nothing stands still over 1–2 s with nothing new on it: photos drift at 0.3–1.5 %/s, graphics build; a quote or table held to be read is a `longStill` kept with a reason |
| Captions | `transcript.createCaptions {maxChars: 24 (vertical; 32 wrapped to 4 lines at the default size in a 1080-wide frame) or 42 (landscape), lines: 2, minSeconds: 1.2, gapFrames: 0}` | ≤ 20 characters a second (none over 25), ≤ 42 characters a line, 2 lines, each cue starting and ending on a word edge |
| Safe area | `bashcut.profiles.get {profile}` (`safeArea`, `safeAreaPx`) **before** placing any text | captions `captions.setStyle {margin}` at the bottom fraction + 0.01 (`tiktok`, `reels`, `shorts`: 0.21); titles and stamps below the top band (`reels` 14 %, 269 px; `tiktok` 8 %, `shorts` 10 %) and left of the right band; the review cannot see caption boxes, so check one `render_frame` |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `news-neutral`, `screen-clean` (screenshots), `archive-warm` (history) |
| Numbers on screen | `transcript.search` for every number said | each on screen while said; its source in the plan |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts`; `youtube` for 2–5 min landscape. `blocking` must be
0: fix the findings (each has seconds and a `fix`) in one `bashcut.batch`, run the review again, at most 3 rounds;
warnings are fixed or kept with a reason in the plan; what still blocks after round 3 goes to the user. Then
bcp:vlog-publish: one `bashcut.profiles.apply` per output.

## Review notes

- Blockers: a number said but not on screen, a card before or long after its word, a graphic that never moves, two
  sections built the same way, text too small at phone width, captions over a graphic.
- Deliberate: one card for a whole section, no hard cuts, the same chrome on every scene.
- `needs_user`: the facts and sources, voice or music only, the illustration style, mascot, avatar and palette,
  whether generated pictures may be used.

## Plan data

- `stages`: `{"voiceover": {"required": true, "why": "the voice carries it; graphics are timed to its words"}, "effects": {"required": true, "skill": "bcp:motion-graphics", "why": "one graphic per section"}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "every line gets a graphic, a picture or the chrome alone, on purpose"}}`
  (music-only: `voiceover` `{"required": false, "why": "cards carry the words"}`).
- `checks`: `number-shown` every number said is on screen; `number-sourced` every number has a source or is marked
  as an example; `graphic-on-word` each graphic lands on its word; `one-graphic-per-section` neighbours differ;
  `nothing-frozen` nothing stands still beyond its reading time; `one-style` generated pictures share one style.
- `askAtIntake`: `["voiceOrMusicOnly", "factSources", "brandKit"]`.
