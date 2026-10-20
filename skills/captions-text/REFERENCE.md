# Captions and text: reference

Detail for `bcp:captions-text`; read only the section a step names.

## Vocabulary and Whisper

FilmCraft's own `transcript.generate` takes a model and a language, no vocabulary. Names and terms it misspells
are fixed afterwards with `captions.setText`. An outside Whisper run (the default build has no Whisper, so words
come from outside anyway) can be steered before it runs; these held in BashCut's Whisper captions plugin
(mlx-whisper, large-v3 turbo):

- **Vocabulary as the initial prompt**: places, people and terms of this video, comma separated (for example
  "Buôn Đôn, Buôn Ma Thuột"), at most ~500 characters. Whisper reads the prompt as preceding text, so the names it
  lists come out spelled the same way. Ask the user for them at intake when the video names places or products.
- **Set the language** (`vi`, `en`) when you know it; auto-detection on a short or music-heavy clip guesses wrong.
- **`condition_on_previous_text: false`** stops one misheard line from repeating through the rest of the file
  (the loops above).
- **Word timestamps on** (`word_timestamps: true`): `transcript.set` needs word times.
- **Drop doubtful segments** before importing: average log-probability below −1.0, compression ratio above 2.4
  (a repeated phrase), no-speech probability above 0.8. large-v3 turbo reports no-speech 0.0 for every segment, so
  a score that is the same everywhere says nothing: skip that rule then.
- **Drop stock credit lines** Whisper learned from subtitled video: "ghiền mì gõ", "subtitles by", "amara.org", and
  outro lines ("cảm ơn các bạn đã theo dõi", "hãy subscribe kênh…") over a stretch with no speech.
- **Re-run a stretch** in ~20 s pieces when a loop smeared it; shift the words by the piece's start before
  `transcript.set` (times are of the whole file).

Import: words in ticks (254 016 000 000 per second), `{"text", "start", "end", "speaker"}` each, one
`transcript.set {item, transcript: {language, speakers, words}}` per media item.

## Script text

A voiceover or a scripted read: the script's words are the captions.

1. `transcript.createCaptions` from the speech (it gives the timing).
2. `captions.list` for the cues with ids and times.
3. Pair each cue with the script line it plays (by order and words), then one batch of `captions.setText {caption,
   text}`, a `captions.merge` where two cues hold one line, a `captions.split {caption, time}` where one holds two
   (the time from `transcript.search`).
4. Lines that do not match (an ad-lib, a cut line) are findings: say which, never invent timing for words not said.

Each `captions.setText` is its own undo step (a batch of 40 is 40 undo steps).

## A captions batch

One `bashcut.batch` (SKILL.md §2; on a build without `bashcut.captions.create`, `captions_fit.py group` and a
`captions.import {path, name}` in its place):

```json
{"id": "bashcut.batch", "params": {"label": "Captions", "commands": [
  {"id": "captions.deleteTrack", "params": {}},
  {"id": "bashcut.captions.create", "params": {"maxChars": 32, "lines": 2, "maxCps": 20}},
  {"id": "captions.setStyle", "params": {"font": "Be Vietnam Pro", "size": 64, "color": "#ffffff",
   "outline": 4, "outlineColor": "#000000", "anchor": "bottom", "margin": 0.28, "align": "center"}}
]}}
```

`captions.deleteTrack` and `captions.setStyle` without `track` act on the first caption track; leave the delete out
when there is none yet. Values are a vertical talking-head start; take them from the measurement and the table in
SKILL.md, then look at a frame. `size` and `outline` are in the track's own units: check the result at phone size
rather than trust the number. Then, in order: `bashcut.review.run {checks: ["captions"], writeMarkers: false}`,
`captions.export {path: "/abs/exports/<output>.srt"}`, and only then `bashcut.captions.wordStyle` if the look asks
for it.

## Titles by hand

```json
{"steps": [
  {"id": "graphics.newText", "params": {"text": "CHỢ ĐÊM\nĐÀ LẠT", "size": 150, "font": "Be Vietnam Pro",
   "fontStyle": "ExtraBold", "position": [540, 760], "seconds": 2.5, "time": 0, "track": 3}},
  {"id": "graphics.set", "params": {"props": {"align": "center", "fill_color": "#ffffff", "stroke": true,
   "stroke_width": 8, "shadow": true}}},
  {"id": "graphics.setCharStyle", "params": {"start": 8, "end": 14, "style": {"color": "#ffd400"}}}
], "stop_on_error": true}
```

`graphics.set` and `graphics.setCharStyle` act on the clip just made when no `clip` is given; pass `clip` when
the batch makes several. Position is in sequence pixels. Text with two looks per line: `graphics.setCharStyle`
ranges, one per look.

## Fonts

`fetch_font.py` (standard library, needs `curl`; `python3` or `uv run`) searches the Fontsource catalogue and
downloads whole `.ttf` files from Google Fonts:

```sh
python3 <skill_dir>/fetch_font.py --subset vietnamese --category sans-serif --weight 800   # one JSON line per family
python3 <skill_dir>/fetch_font.py --family "Be Vietnam Pro" --weights 600,800 --dest /abs/project/fonts --import
```

`--import` copies each file into the user's font folder (macOS `~/Library/Fonts`, Linux `~/.local/share/fonts`,
Windows `%LOCALAPPDATA%\Microsoft\Windows\Fonts`). Then `fonts.list` should name the family; a running app may need
a restart to see it. On Windows a font copied there may need a double-click install to register. A family not on
Google Fonts has no whole file here; the result line says where to get it.

System fonts that drew Vietnamese tone marks right in BashCut (macOS): San Francisco (System Condensed Black),
Verdana Bold, Marker Felt Wide, Arial Bold, Times. Arial and Times also cover Greek and Cyrillic, not CJK or Thai. Helvetica Neue's condensed faces have the letters but misplace stacked marks (Ắ, Ở). Always look at
a frame with the project's real words: a font missing a letter falls back to another font silently.
`graphics.fonts.used` lists the fonts a project's graphics use; `file.replaceFonts {from, to}` swaps one
everywhere.

## Limits of this build

- Word-by-word styles (`bashcut.captions.wordStyle`) are graphic text layers: no caption is left to review or
  export afterwards, and a one-word cue stays a plain caption.
- No measured contrast, safe-zone or face check: look at `render_frame` frames at phone size.
- `captions.setStyle` is per track: a different look for one cue means another track.
