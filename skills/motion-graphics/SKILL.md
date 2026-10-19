---
name: motion-graphics
description: Designed, animated graphics over footage in BashCutPro: stat and checklist cards, counters, lower thirds, charts, diagrams, maps, kinetic type. Whether a sentence needs one, which tool makes it (graphics.* and .fcgt templates for simple cards, the bashcut.hyperframes plugin for HTML/GSAP rendered outside and imported with alpha), timed to the word with transcript.search, held and checked with render_frame. Triggers: "đồ hoạ", "motion graphic", "thẻ thông tin", "số liệu chạy", "counter", "lower third", "infographic", "animation chữ", "biểu đồ", "bản đồ".
---

# Motion graphics

Sources: T13 = motion-graphics study, T22 = renderer study. Choose inside each range from this video's speech, genre
and frame; say why. Captions and plain titles: bcp:captions-text; transitions, punch-ins, a clip's In/Out:
bcp:effects. BashCutPro has no graphics renderer of its own: simple cards are native graphics clips, everything
that needs real motion design is rendered **outside** the app by a plugin and imported with alpha.

## 1. Does this sentence need a graphic?

With `plan.visuals` in the project notes (bcp:visual-plan; read them with `project.notes`), build its `graphic` rows
at their `at` word, showing their `show`; question a row only when building shows it fails, and update the plan.
Without one: a graphic shows what the words don't (example, number, relationship, consequence). Read the words
(`transcript.inspect`): what did the speaker make the viewer imagine?
- Skip it when the card would restate the caption: captions and on-screen text take one role each, never both
  (openmontage). Leave some sentences bare so the next card lands (ghost-editor).
- Change the graphic when the content changes, never on a timer ("every 15 s" is an anti-pattern, digitalsamba).
- Graphics over talk keep the voice under them; never cut to a silent standalone card (vibetube).
- Vary the device; one card on every point reads as a template (T13).

## 2. Pick the cheapest tool that does it

1. **Native text** (bcp:captions-text), first choice: titles, labels, keyword stickers, place and chapter cards.
   Editable in the app, no render.
2. **A `.fcgt` template** for simple cards, lower thirds and static counters: `graphics.template.list {query}`,
   then `graphics.template.apply {template, values, time, track}`; change a field later with
   `graphics.template.set {clip, values}`. None fits: build the card once by hand and keep it as a template (§4),
   so every card of the series is one `apply` with new values.
3. **The `bashcut.hyperframes` plugin** (§5): kinetic type, a number that counts, chart, table, map or route,
   clicking pointer, mock screen, full-frame card, a diagram that builds. HTML/CSS + GSAP rendered in headless
   Chrome to a PNG sequence (or ProRes 4444) with alpha, imported with `file.importImageSequence` and placed on a
   video track above the picture; rendered again and swapped when its words change.
4. **The user's Remotion or After Effects project**: they render it (ProRes 4444 or a PNG sequence with alpha);
   import it with `file.importImageSequence {path}` (first frame) or `media_import`. Never run Remotion renders
   for them (licence, T22).

Say which and why. A graphics-led reference or genre (a dense explainer short of designed type and cards) needs
the plugin for most sentences.

## 3. Timing (anchor to words, not seconds)

| What | Range | Sources and why it varies |
|---|---|---|
| Entrance lands on the payoff word | entrance end = the word's start; entrance 0.15–0.6 s | video-use, vibetube (~0.4 s), student-kit (0.15–0.6 s); shorter for energetic cuts, ≤0.15 s for impacts |
| Hold, one idea | 3–8 s, and at least its narration + about 1 s | video-use (floor 3, simple 5–7), vibetube (≥ narration + 1 s), openmontage (3–5 s cap). They conflict: tie the hold to the narration span |
| Hold, diagram that builds | 8–14 s | video-use; complexity and words on it |
| Accent hit | 0.5–2 s, recognisable not readable | video-use, openmontage; only for emphasis or music hits |
| Final-frame hold | 0.5–1.5 s | video-use (≥1 s); longer for a number the viewer must remember |
| Stagger between elements | 0.06–0.10 s opener, 0.3–0.4 s narrative, 0.5–0.6 s dramatic | student-kit; one new element at a time when each is read |
| Entrance / exit | 0.2–0.8 s / 0.15–0.5 s, entrance stronger | talkcraft |
| Words on a card | ≤ about 2–3 per second of hold | student-kit, guizang (6–9 CJK chars/s); measure the real text |
| Density, talking footage | 3–8 graphics a minute, sparser for long videos; a measured reference replaces it | openmontage (3–6/min), hyperframes (card every 6–20 s by length); high for tutorials and explainers, low for vlogs and when the face carries the emotion. Graphics-led explainer shorts run far above: one measured reference changed the picture every ~1.6 s with about 30 graphics a minute. With a user reference, take the number from bcp:style-study |
| First graphic | within the first ~5 s, usually the hook title | vibetube |

Taste stated as law ("never linear", "no bounce") is not a rule: linear suits constant pans and counters; overshoot
1.05–1.12 suits playful, none calm or premium (shotcraft, saas).

Steps: the payoff word's time W (`transcript.search {query}` gives each match's start in seconds) → entrance length
E → the graphic starts at W − E (its entrance takes E) → hold until the narration it illustrates ends + 0.5–1 s.
Times inside a rendered graphic (a counter's `at`, each row's `at`) are seconds from the graphic's start:
word time − (W − E).

## 4. Simple cards as `.fcgt` templates

A card the series repeats (a stat card, a lower third, a price tag, a chapter card) is built once and reused:

1. Build it on the first use: `graphics.newRectangle` (the plate; `position` is its centre), `graphics.newText {text, size, font, position,
   seconds, time, track}` into the same clip (`clip`), `graphics.set {props}` for fill, stroke, background and
   shadow; `graphics.setCharStyle` for the keyword or number in the accent.
2. Motion that survives length changes: `graphics.setResponsiveTime {introSeconds, outroSeconds}` keeps the
   entrance and exit keyframes while the hold stretches; the entrance itself is opacity, position and scale
   keyframes on the clip (bcp:effects), 0.2–0.5 s.
3. Keep it: `graphics.template.export {clip, name, category, controls}` with one control per field that changes
   (the text layers, the accent colour). `graphics.template.controls` shows them.
4. Every later card: `graphics.template.apply {template, values, time, track}`, all of a video's cards in one
   `command_batch`. A `.fcgt` someone sends: `graphics.template.install {path}` (`.mogrt` is refused).

A template cannot count a number up, draw a chart or build a diagram: those go to the plugin. Details and a
worked batch: REFERENCE "Template cards".

## 5. Render with the HyperFrames plugin

The [`bashcut.hyperframes`](https://github.com/dongnguyenvie/bashcutpro-plugins/tree/main/plugins/hyperframes)
plugin is a command line next to its own skill (`hyperframes`): read that skill before the first graphic; its 31
examples and the HyperFrames catalog are raw material. Below, `HF` means `python3 <plugin dir>/plugin.py`
(`py -3 …` on Windows), with the connection `--project <file.fcproj>` (headless, saved unless `--no-save`) or
`--bridge 127.0.0.1:<port>` (the open app).

- `HF check` first. `dependency_missing`: `HF setup` (about 350 MB: HyperFrames, GSAP and Chrome headless shell);
  `no_node`: the user installs Node.js 22 LTS — you cannot. While it waits or fails, use a template or native text
  and say what is missing.
- `HF examples` lists what each example draws and its variables; `HF examples NAME` its pitfalls. Fill an example
  with `--set k=v` instead of editing its HTML.
- Look before you render: `HF place NAME --seconds S --set … --snapshot 0.4,1.2,3` gives PNGs in seconds, nothing
  placed. Then `HF place NAME --seconds S --draft --set … --project …` renders, imports and places on V2 (added
  when missing) over the picture; it prints the record path.
- A change later: `HF rerender <record> --set …` renders from the recorded inputs and repoints every use with
  `media.replaceFootage`. Before export: `HF finalise --project …` renders every draft at full fps and swaps it.
- One graphic per call, one render at a time. A graphic over more than ~10 s is one render per section, so fixing
  one section re-renders seconds, not the video. Many graphics over one voice: one call each, in time order, the
  same `--brand brand.json` on every call for one look.
- A place video (real estate, a venue): all location data from one `HF osm-map` call into a copy of
  `amenity-radius`; every count, minute and km on screen comes from its output.

Hand the plugin a brief, not a template: words, payoff time, what the viewer sees, hold, look (style profile,
reference frames, the video's titles). Many rows: a sub-agent can build them all from REFERENCE "Graphics brief".

**Numbers on a card: facts table first.** Before searching the web, ask open data for every figure in one call
with the [`bashcut.resources`](https://github.com/dongnguyenvie/bashcutpro-plugins/tree/main/plugins/resources)
plugin: `RS fetch --script facts --args "--questions facts.jsonl --json"`, one question per number (a Wikidata
property, a World Bank indicator for a country, or a Wikipedia summary; `--args "--help"` for the fields). Check
each matched the right place or thing. Rows go straight into widget values: `value` → a counter's `to` or a
bar's `value`, `" " + unit` → `unit`; keep credit, date and source URL with the script line in the notes (on the
picture only when the user asks). Search the web only for rows that came back `none`, never to replace an answered
one; a figure the table cannot hold (a price, a fee) is a web row from the start.

**Animated accents (Lottie)**: a check, an arrow, a loader, confetti. All of a video's in one call: `RS fetch
--script lottie --args "--words check,arrow,loader,confetti --dest <project dir>/media/lottie"`, one look at the
sheet, then `--pick "check=2;confetti=1"`; one accent = one `HF place lottie --set file=<the picked .json>`.
Lottie files are JSON for the plugin, never for `media_import`. Never `.lottie` zips or animations with image
assets.

## 6. Check

- Landing frame and entrance: `render_frame {seconds: W, max_side: 390}` (phone size) and two or three frames
  across the entrance. Readable at phone size, on the word, the face clear (look at the frame: nothing detects
  faces), clear of the platform's caption band and of other text.
- A draft moves at 15 fps: judge timing and layout on it, smoothness only after `HF finalise`.
- Re-timing the voice moves words, not the graphic: after cuts there, run `transcript.search` again, then move the
  clip or `HF rerender` with new `at`s. A render that changed length (`lengthChanged`): trim or extend the clip.
- Never export over drafts: `HF finalise` first (bcp:vlog-publish).

## Report

Which sentences got a graphic and why, the tool for each (native, template, plugin), its timing against the word,
the render numbers (frames, seconds, draft or final) and where it sits (seconds, track, record), and what was
left bare on purpose.
