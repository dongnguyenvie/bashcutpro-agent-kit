---
name: captions-text
description: Captions and on-screen text in BashCutPro: captions from speech (transcript.generate or imported words, then transcript.createCaptions), SRT/VTT import and export, fixing text and times with captions.*, the caption look per track, titles, place and chapter cards with graphics.* and .fcgt templates, Vietnamese fonts (fetch_font.py), size, contrast, safe area and sync. Triggers: "phụ đề", "sub", "caption", "chữ trên hình", "tiêu đề", "thẻ chương", "nhãn địa điểm", "font", "lỗi font tiếng Việt", "add subtitles".
---

# Captions and on-screen text

FilmCraft draws all text itself (captions tracks, graphics clips); never render text into a video with Pillow or
ffmpeg. The numbers below are ranges with their sources (T09 = BashCut's captions study): read the measurement
first, choose a value inside the range for this speaker, genre and frame, and say why. Detail:
`<skill_dir>/REFERENCE.md` (one section at a time).

A folder of clips that only need captions (an SRT and a styled preview each) is the `captions-draft` batch preset,
and Vietnamese subtitles for a folder `vietsub-folder` (`bcp:batch`).

## 1. Words first

Captions come from the words of the **edited** sequence, so make them after the cut (`bcp:rough-cut`) and the
voiceover are locked.

- **Whisper build** (`transcript.models` says `"available": true`): `transcript.generate {items, language}`
  (or `sequence.transcribe {track: "mix", language}`), `wait` on the job.
- **Default build**: transcribe outside, then `transcript.set {item, transcript}` per media item
  (`bcp:footage-survey`). The outside Whisper takes a vocabulary (REFERENCE "Vocabulary and Whisper").
- **A script or voiceover text exists**: show the script's exact words, never the recogniser's paraphrase (T09
  §2, §4). Align it: the `bashcut.align` plugin puts the script (or an SRT / VTT) on the heard words with word
  timing, writes them with `transcript.set` and one caption per line with `captions.import` (`--dry-run` first;
  listen to its `low` spans). Without the plugin: captions from speech, then `captions.setText` each cue to the
  script line it plays (REFERENCE "Script text").
- **SRT / VTT from elsewhere**: `captions.import {path}` makes a captions track; `captions.export {path,
  format}` writes one out.

Before grouping, read the words (`transcript.inspect`): the language, names and terms, the speaker's typical gap
between words and the speech rate (words per second).

- Speech recognition invents text over music, crowds, rooms and screen recordings ("hãy subscribe kênh…",
  "cảm ơn các bạn đã theo dõi", "ghiền mì gõ", repeated phrases). Delete those cues (`captions.delete`); a clip
  with only that text has no speech.
- A cue longer than ~10 s, or one word repeated many times ("à à à …"), is a recognition loop: its word timings
  are smeared (one 5 min talk lost 128–237 s to three such cues). Don't cut on them; transcribe that stretch again
  in ~20 s pieces outside and import those words.
- Fix product and place names (`captions.setText`); show acronyms read as words ("xê en xê") as letters (CNC).
  Each `captions.setText` is its own undo step: batch them, and note the `history.list` length first.

## 2. Group cues

`transcript.createCaptions {maxChars, lines, minSeconds, maxSeconds, gapFrames, name}` makes a captions track
from the words in groups. Choose its limits from the measurement, inside these ranges (T09 §3, §7):

| Delivery | Words per cue | Pause that breaks a cue | Characters per line |
|---|---|---|---|
| Energetic vertical (hooks, reactions) | 2–4 | 0.15–0.3 s | vertical: 15–32 Latin |
| Conversational (vlog, review, talking head) | 3–6 | 0.25–0.5 s | vertical: 15–32 Latin |
| Landscape subtitles (tutorial, interview) | 6–8, or full lines | 0.5–0.6 s | 32–42, two lines |

- `gapFrames` is the pause in frames (0.3 s at 30 fps = 9). Fast talkers need the low end; set the break near the
  speaker's own typical gap, not a house number. Cue length 0.5–5 s for social (`minSeconds`, `maxSeconds`), up to
  ~7 s for subtitles; one cue on screen at a time.
- Character limits depend on font width and size: CJK counts double, and rendered width matters more than the
  count (T09 §3). `lines`: 1 for punchy vertical styles, 2 for subtitles.
- No single number is "right": the sources contradict each other on words per cue (always 3 vs never fixed), the
  pause (250 vs 500 ms) and vertical line length (~28–30 vs 32) (T09 §3, §5).
- Reading speed: about 15–20 Latin characters per second is comfortable, above ~25 is hard (T09 §3). Captions of
  real speech follow the speech; look again at cues above ~20 cps and split (`captions.split`) or merge
  (`captions.merge`) them, but do not paraphrase.
- Break at meaning (phrase ends, commas), not only at the limit: after the rule pass, merge or split the cues that
  break a phrase (`captions.list` to read them with ids and times).

**After every cut, make the captions again from what is heard** (delete the old track: `captions.deleteTrack`).
Captions made before a cut keep words of lines cut away (one edit showed half a dropped sentence).

Word-by-word highlight (karaoke): `bashcut.captions.wordStyle {captions, style: {preset: "karaoke" | "pop" | "clean",
highlight, pop, bold, dim}}` after the cues are final (it turns them into graphic text layers, one per spoken word,
timed from the transcript; one undo step). The caption track is empty afterwards, so write any sidecar first
(`captions.export {path}` before it, else the .srt has 0 cues). Keep such cues to one line of 2–5 words and `pop` ≤ 1.25 (the line reflows).
Builds without it (`command_list`): short groups (2–3 words, one line) instead, and say so if the user asked for it.

## 3. Caption look

`captions.setStyle {track, font, size, color, background, backgroundColor, outline, outlineColor, anchor, margin,
align}` styles the **whole track**. Two looks at once (a speaker label and the speech, two languages): two tracks.

| Look | Style (starting point, then check a frame) |
|---|---|
| Bold outline (review, food, talking head) | white, bold sans, `outline` 3–5, `outlineColor` "#000000" |
| Plate (bright or busy footage) | white on `backgroundColor` "#000000a0" (≈ 0.6 opacity), `background: true` |
| Cinematic | small serif, warm off-white, no plate, thin outline |

White text over daylight measured 1.2–2:1 contrast, unreadable on a phone: plate or outline it. Burned in at
export (`file.exportMedia {burnCaptions: true}`) or delivered as a sidecar (`captionSidecar: "srt"`).

## 4. Titles and cards

Titles, place cards, chapter cards, keyword stickers and lower thirds are graphics clips:

- **Template first**: `graphics.template.list {query}` for an installed `.fcgt`; place it with
  `graphics.template.apply {template, values, time, track}`, change a field later with `graphics.template.set`.
  A new `.fcgt` installs with `graphics.template.install {path}` (`.mogrt` is refused). BashCut's library looks
  (stacked keyword, headline-subline, boxed keyword, two-tone pop) wait for their `.fcgt` conversions.
- **By hand**: `graphics.newText {text, size, font, position, seconds, time, track}`, then `graphics.set {props:
  {fill_color, stroke, stroke_width, background, shadow, align}}`; one word in another colour or font:
  `graphics.setCharStyle {start, end, style}`. A plate: `graphics.newRectangle` under the text. Keep a look you
  made with `graphics.template.export` so the next card matches.

A hook, a CTA, a label and a caption differ in role, not in kind: pick **one title look per video** (tone,
platform, footage) and use it whatever role the line plays. Write title text in 2–3 short lines, the keyword alone
on its line. In and Out animation: `bcp:effects`; animated graphics: `bcp:motion-graphics`.

## 5. Size, fonts, contrast

- **Size** (T09 §3): captions 3–6 % of frame **height** (measured glyphs), secondary text at least 3 %, hook text
  6–9 %. On 1080×1920 that is captions 58–115 px, hook 115–175 px (`graphics.newText` `size` is px). The sources
  disagree on the minimum (3 % to 5.2 %): judge on a phone-size frame (`render_frame {seconds, max_side: 390}`),
  not the number.
- Text is **read** (big, with contrast) or **texture** (dimmed or blurred so nobody tries): a line meant to be read
  that cannot be is enlarged or deleted; the closing URL or CTA is never the smallest line.
- **Fonts for Vietnamese** need every stacked mark (Ắ, Ở, Ữ). `fonts.list` lists what FilmCraft finds; check a
  frame with real words of the project. Helvetica Neue's condensed faces misplace stacked marks: avoid them. Open
  fonts with Vietnamese: `python3 <skill_dir>/fetch_font.py --subset vietnamese --category sans-serif`, then
  `--family "Be Vietnam Pro" --weights 600,800 --dest /abs/project/fonts --import` (REFERENCE "Fonts"). At most 2
  families a video; titles heavy or condensed, captions sans with a tall x-height, 600–800.
- **Contrast** is measured, not assumed: look at the frame behind the text; below about 4.5:1 (the AA level, T09
  §3) change fill or outline, add a plate or move the text, then look again.

## 6. Placement and sync

- **Safe area**: safe zones are facts per platform (its own published guide), not one set of numbers: keep text
  clear of the platform's UI (the bottom caption and name bar, the right-side buttons, the top header on vertical
  outputs) and use the strictest zone of the outputs that share a shape. Vertical caption height is the biggest contradiction in T09 (from 55–60 % of the
  height down to near the bottom bar): decide from faces, a picture-in-picture camera and cards on this frame, and
  keep one zone per sequence (`captions.setStyle {anchor, margin}`; `margin` is a fraction of frame height).
- Keep text off faces (the `bashcut.vision` plugin's `subjects` writes face boxes per clip to
  `<project>.vision.json`; without it, look at the frames) and labels clear of each other (a top-left step
  label and a top-right tag collided in one project).
- **Sync** (T09 §3): captions start 0–0.15 s before the word; cards and graphics lead by 0.15–0.6 s
  (`captions.move`, `captions.setTimes`; a word's time from `transcript.search`).
- Hold authored text at least its reading time, plus 1–1.5 s after its animation ends; a hook can be shorter when
  the same words are spoken (T09 §3). Copy budget: hook text 3–8 words, overlays ≤ 6; on-screen text repeats only
  the key word or number of the spoken line.
- **No captions while a title or card is on screen**: remove or shorten the cues under a hook title, a price card or
  a CTA card; the same words twice read as a mistake (captions repeated the title and the price card in one ad).
- **Content only, no production notes**: no "AI voice", effect or speed names ("x8", "slow motion"), sources or
  credits on screen (credits: `bcp:stock-images`).
- Place card at each location change, with the real place and time. Chapter cards only in tutorials and list
  videos: in one narrative vlog, cards with a flash and boom at every section felt disjointed; a hard cut, a
  bridging voiceover sentence and a small quiet date label worked better.

## 7. Verify

`captions.list` (or `captions.export` to an SRT) for cps, gaps and overlaps; `render_frame` at phone size on the
longest-line cue, every title and the opening: readable, off faces, inside the safe area, no collision with
another text? Fix in one batch, look again. Stop after about three rounds of fixes and show the user what is left
(T09 §7).
