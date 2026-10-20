---
name: vlog-news
description: Recipe for news and documentary from photos, archive and source screenshots: a vertical news short with fixed chrome, or a landscape documentary with date cards; honesty rules for every claim, picture, credit, date and quote. Use after bcp:vlog-plan picks news. Triggers: "news", "documentary", "breaking news", "tin tức", "bản tin", "tin nóng", "thời sự", "phóng sự", "phim tài liệu".
---

# News and documentary

Reply in the user's language. News carries facts the viewer will repeat: plan the facts and their sources first
(bcp:vlog-hook-script), then the pictures that prove them. Plan with bcp:vlog-plan, edit with bcp:edit-workflow.
RC = the Reelcrew / AgentVid study (measured 2026-10-07: a 45 s vertical news piece and three landscape documentaries
of 105–292 s); T-notes as in the other recipes.

## Two shapes

| Shape | When | Output |
|---|---|---|
| Vertical news | one recent story, 30–60 s (RC: 45 s) | TikTok, Reels, Shorts |
| Landscape documentary | an event or a history, 1.5–5 min (RC: 105–292 s) | YouTube 1080p |

Write the shape and its reason in the plan; a vertical cut-down of a documentary is its own sequence
(`file.newSequence`), not the same timeline reframed.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Cuts | vertical: about 12 hard cuts a minute, 4–4.5 s a picture (RC: 12.0, mean 4.49 s); documentary: 0.2–13 a minute (RC) | a documentary of photos cuts like news (RC: 13.1, 4.4 s); one of illustrations and cards morphs instead (RC: 0.2–0.8) |
| Long shot | vertical: 5–6 s; a documentary of morphing cards may hold longer, judged by motion (RC) | a quote card holds for its reading time |
| Frozen picture | 1.5–3 s: every photo drifts (Ken Burns 0.3–1.5 % a second, T08 §3); still frames 22 % in the news piece, 1–57 % in documentaries (RC) | a screenshot, quote or date card held to be read |
| Hook | vertical: 2–3.5 s, the most striking picture and one teasing line (RC: first line ends 3.0 s, first cut 3.4 s); documentary: 3–5 s, the question inside the cold open (RC) | the first picture must be the story's own, not a stock mood shot |
| Speech rate | about 200 syllables a minute in Vietnamese TTS news (RC: 201); silences 1–6 % | a documentary breathes on its date cards; size lines with the measured rate |
| Dead air | 0.5–1 s; one held beat on a date card or before the quote (T07 §3) | — |
| Captions | vertical: one keyword caption of 2–4 words over the photo, keyword in the accent (RC); documentary: full-sentence subtitles, 1–2 lines, 32–42 characters (T09 §3; RC) | the headline band already says the story |
| Smallest text | the credit line: it must read at phone width (`render_frame`) | longer outlet names; landscape has more room |
| Speech coverage | 0.9–0.97 (RC) | lower with music-only title sequences |
| Music under the voice | the deep end of 5–18 dB (T11 §3): a neutral bed or none | up on a documentary's titles and date cards |

## Structure

Sample lengths, not slots: the plan gives each section its range and a named range marker (`markers.addRange`).

**Vertical news (30–60 s)**: hook 2–3.5 s (the most striking picture and one teasing line, RC: "Tên lửa bay ngang mặt
trời…") → what happened 10–12 s (who, what, when, where; the date said and on screen) → the latest in numbers 12–16 s
(2–3 numbers, each on its picture or a counter) → the quote 4–6 s (verbatim, speaker, role and date; "(lời dịch)"
when translated) → what's next 5–7 s (the next date or step; a follow CTA only if the user wants one). About one
picture per sentence of 4.5–6 s, cut in the pause after it (RC: eight sentences, nine cuts).

**Landscape documentary (1.5–5 min)**: cold open 10–30 s (a present-day headline screenshot, then the question) →
chapters ×3–6, 20–60 s each (a date card, then the archive pictures, screenshots and charts of that moment) → return
10–20 s (back to today, a chart over the years) → close 5–10 s (the question again, now answerable, on a card; RC:
"Tri thức, hay cạm bẫy?").

## Pictures and frame chrome

- **Pictures**, in order: the user's own; public-domain or open archives (NASA, Wikimedia Commons); screenshots of the
  real source, cropped, the key line highlighted, outlet and date named (RC); stock (bcp:stock-images) only for
  generic places and objects, never as the event; charts and maps from data. Off-aspect photos fill with a blurred copy.
- **Generated pictures**: never of a real person, place or event as if photographed. An illustration (a
  reconstruction, an engraving of an ancient scene, a diagram) is allowed in one style for the whole film
  (bcp:vlog-scene-prompt) and, unlike the other recipes, carries a label on screen ("ảnh tạo bằng AI", RC): a news
  viewer takes pictures as evidence.
- **Vertical chrome stays on** (RC): a breaking tag ("TIN NÓNG") and credit line top-left, the photo in the top half
  with the keyword caption at its foot, the headline band mid-frame (topic chip, then 2–3 lines), the blurred photo
  below. Only the photo and caption change; the chrome never moves; inside the safe zone.
- **Documentary chrome**: a date card per chapter ("30.04.1993"), the source under each screenshot, subtitles at the
  bottom; the brand's logo small in a corner when there is one.
- Tag, band, credit and date-card looks, counters, charts, timelines and quote cards: bcp:captions-text /
  bcp:motion-graphics (an installed `.fcgt` via `graphics.template.apply`, else `graphics.newText` and
  `graphics.newRectangle`; a series keeps its cards in a project template, `bashcut.template.save`).

## Transitions

- Vertical news: plain hard cuts on the sentence pauses; no transitions, no whips (RC).
- Documentary: a cross dissolve of 0.3–0.5 s (9–15 frames at 30 fps) between pictures, staggered: the title fades out,
  then the picture dissolves, then the new title fades in (RC). A date card into its archive picture: a dip to black
  over 0.5–1 s. Paper looks (torn edges, paper sliding in): one motif per film. Kinds from `effects.list` (bcp:effects).

## Facts and honesty (not taste)

- Every claim, number, date and name has a source in the script beats: the outlet, the official page, the document.
  No source, or sources that disagree: say so or leave it out. Background figures (population, dates, places) from a
  named reference; the news itself comes from the outlet.
- The date of the news is said or shown; a story older than a few days says when it happened ("ngày 30/8").
- Quotes verbatim, the speaker named with role and date; a translated quote says "(lời dịch)"; never shorten a quote
  so it says something else.
- Every picture keeps its credit on screen while it shows (outlet, agency, archive): the one recipe with a credit by
  default. Licence notices stay off screen unless the user asks.
- No defamation: an accusation is attributed ("theo …", "cáo buộc"), never stated as fact; no private person's face,
  name or address without a public reason.

## Sound and look

A clear voice at the measured rate (bcp:voiceover), a neutral bed deep under it or none, a soft hit on date cards
(bcp:audio-mix). News calm and serious, one accent for the tag and the caption keyword; a documentary paper or dark
archive. Archive photos keep their own colour (bcp:color-grade only to match exposure).

## Measure and finish

Measure the edit, not a render: these read the sequence directly. Look with `render_frame` at phone size
(`max_side` ~400), never a test export.

| Check | Command | This recipe |
|---|---|---|
| Shot lengths, cut rate | `bashcut.timeline.summary` (V1 clip `start` / `end` in seconds) | vertical news about 12 cuts a minute, 4–4.5 s a picture, cut in the pause after a sentence; documentary 0.2–13 a minute by shape |
| Cuts in speech | in and out points from `transcript.search` (`start` / `end` in ticks ÷ 254 016 000 000: the first word's start, the last word's end), never typed times | 0 `cutInWord` findings |
| Frozen and still | `bashcut.review.pictureChecks {}` | Every photo and screenshot drifts at 0.3–1.5 %/s while it shows (still frames read as a stuck video); a date or quote card held to be read is a `longStill` kept with a reason |
| Captions | `transcript.createCaptions {maxChars: 24 (vertical; 32 wrapped to 4 lines at the default size in a 1080-wide frame) or 42 (landscape), lines: 2, minSeconds: 1.2, gapFrames: 0}` | ≤ 20 characters a second (none over 25), ≤ 42 characters a line, 2 lines, each cue starting and ending on a word edge |
| Safe area | `bashcut.profiles.get {profile}` (`safeArea`, `safeAreaPx`) **before** placing any text | captions `captions.setStyle {margin}` at the bottom fraction + 0.01 (`tiktok`, `reels`, `shorts`: 0.21); titles and stamps below the top band (`reels` 14 %, 269 px; `tiktok` 8 %, `shorts` 10 %) and left of the right band; the review cannot see caption boxes, so check one `render_frame` |
| Loudness | `bashcut.audio.loudness {}` | −14 LUFS ± 1 (`facebook-square` −16), true peak ≤ −1 dBTP; music 5–18 dB under the voice |
| Look | `bashcut.looks.apply {look, intensity: 0.6–1.0}` on one adjustment layer (bcp:color-grade) | `news-neutral`, `archive-warm` (documentary); archive photos keep their own colour |
| Dates and quotes | `transcript.search` for each date and quote | each date on screen while said; each quote card verbatim with speaker |

**Captions read at 20 characters a second because the cue spans the pauses**, not because it is short: on one
voice, 2-line cues of 24–42 characters had 83–90 % of cues at or under 20 cps, 1-line 16-character cues only 76 %
with one over 25. Fix a `readingSpeed` finding by stretching the cue into the pause after it (`captions.setTimes`),
merging it with a short neighbour (`captions.merge`, then check `lines`) or dropping a filler word, never by
splitting it smaller.

**Review every output.** On each output sequence (`sequence.open {item}` first; the review reads the active one):
`bashcut.review.run {profile}` with `tiktok`, `reels`, `shorts` (news); `youtube` (documentary). `blocking` must be
0: fix the findings (each has seconds and a `fix`) in one `bashcut.batch`, run the review again, at most 3 rounds;
warnings are fixed or kept with a reason in the plan; what still blocks after round 3 goes to the user. Then
bcp:vlog-publish: one `bashcut.profiles.apply` per output.

## Review notes

- Blockers: a picture without its credit, a date said but not shown, a quote with no speaker, a stock shot posing as
  the event, a caption over the headline band, chrome that jumps, a photo that stands still.
- Deliberate: identical chrome in every shot, plain hard cuts in vertical news, long morphing shots in a documentary
  of cards.
- `needs_user`: the facts and sources, the shape, the voice, unclear licences, generated illustrations, the brand.

## Plan data

- `stages`: `{"voiceover": {"required": true, "why": "the voice carries the facts; pictures are cut to its phrases"}, "captions": {"rules": ["the chrome is placed once and never moves", "every date and number said is on screen"]}, "colour": {"rules": ["archive pictures keep their own colour; match exposure only"]}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "every line gets a sourced picture, a screenshot, a chart or a card"}}`
- `checks`: `fact-sourced` every claim, number and date has a source; `credit-visible` every picture keeps its credit;
  `date-shown` the date of the news or chapter is on screen; `quote-verbatim` quotes match their source, speaker
  named; `generated-labelled` no generated picture shows a real event, every illustration labelled; `chrome-fixed`
  the chrome stays put; `nothing-frozen` no photo stands still beyond its reading time; `attributed` accusations are
  attributed.
- `askAtIntake`: `["factSources", "shape", "brandKit"]`.
