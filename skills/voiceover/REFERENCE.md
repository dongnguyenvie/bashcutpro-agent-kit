# Voiceover reference

Times are ticks (254 016 000 000 per second) unless a param says `seconds`. Clip and item ids come from
`sequence_inspect` and `doc_inspect`. Many edits at once go in one `bashcut.batch` (one undo step; `command_batch` without it).

## Words and narration.py

Save the words to a file first, then measure outside (read-only, standard library):

```sh
# words.json = the result of command_run transcript.inspect, saved as is
python3 "<skill_dir>/narration.py" rate words.json --speaker 0          # overall, articulation, p10/p50/p90
python3 "<skill_dir>/narration.py" windows words.json --rate 4.2 --min-seconds 1.5 --from 0 --to 95
python3 "<skill_dir>/narration.py" check take.json --text "Quán này mở từ bảy giờ sáng" --min-similarity 0.9
```

- `rate`: `overall` keeps pauses inside phrases (a gap of `--phrase-gap` 0.5 s or more ends a phrase),
  `articulation` counts only time inside words. p10–p90 is per phrase of 4 units or more: the slack for sizing
  lines.
- `windows`: the gaps between words inside `--from`/`--to`, shrunk by `--margin` (0.3 s) from real speech, at
  least `--min-seconds`; `budget` = seconds × rate, in the voice's unit. `before`/`after` quote the speech around
  each window. Words on a media item's clock rather than the sequence's: `--offset` = where that clip's source
  start sits on the timeline, in seconds.
- `check`: aligns the line's words with the take's; `unmatched` are line words not heard (dropped or misread),
  `extra` heard words not in the line (repeats, inventions), `atStart` true when either falls in the first three
  words, `unitsPerSecond` from the take's own span. It reads `transcript.inspect` output, `transcript.set` params
  or Whisper JSON (`openai-whisper`, `mlx_whisper`, `faster-whisper` with word timestamps).

## English with tts

```json
{"id": "tts.voices", "params": {}}
{"id": "tts.render", "params": {"text": "Three things nobody tells you about Hanoi.", "voice": "<id>", "sample": true, "wait": true}}
```

Test line: `tts.create` it on a spare track, read its duration from `sequence_inspect`, divide the line's words by
it, then `edit.undo`. A whole script, each line at its start (ticks), on A2:

```json
{"steps": [
  {"id": "tts.create", "params": {"text": "Three things nobody tells you about Hanoi.", "voice": "<id>", "pace": 1.0, "time": 508032000000, "track": "A2"}},
  {"id": "tts.create", "params": {"text": "First, the trains run through the streets.", "voice": "<id>", "pace": 0.95, "time": 2286144000000, "track": "A2"}},
  {"id": "file.save", "params": {}}
], "stop_on_error": true}
```

- `pace` 0.5–2 (1 = the voice's own); `pitch` `extraLow`…`extraHigh`; `dir` where the audio is written.
- `tts.inspect {clip}` reads a narration clip's text, voice and pace; `tts.edit {clip, text, voice, pace}`
  re-voices it in place (the clip keeps its start).
- Headless MCP has the formant voices only. In the desktop app, `tts.downloadVoices {wait: true}` fetches the
  natural (Kokoro) voices once; `tts.voices` then lists them. Name the voice set in the plan's `decisions`.

## VieNeu

The plugin lives in `bashcutpro-plugins` (`plugins/vieneu-tts`, its own skill `vieneu-tts` has the full command
list). `VN` = `python3 <plugin dir>/plugin.py` (`py -3 …` on Windows). Every command prints one JSON object
(`ok`, `message`, `data` or `error`).

```sh
VN check                                   # not_installed → ask, then: VN setup --download-model (≈1.4 GB)
VN voices                                  # 25 presets: region North/Central/South, style, gender
VN synthesize --text "Câu khó nhất của kịch bản" --voice "Mai Anh" --out voiceover/audition/mai-anh   # test line
VN synthesize --lines lines.json --voice "Mai Anh" --takes 2 --out <project dir>/voiceover/vieneu
```

`lines.json` is the plan's lines: `{"lines": [{"id": "l1", "text": "…", "seconds": 1.5}, …]}`. Takes land at
`<out>/<id>/take-N.wav`; `takes.json` lists each take's `seconds` and `syllablesPerSecond`. Then bring the kept
takes in yourself, over the same MCP connection the edit uses:

```json
{"steps": [
  {"id": "timeline.place", "params": {"item": "<l1 take id>", "track": "A2", "seconds": 1.5}},
  {"id": "timeline.place", "params": {"item": "<l2 take id>", "track": "A2", "seconds": 7.8}},
  {"id": "file.save", "params": {}}
], "stop_on_error": true}
```

after one MCP `media_import` (or `file.import {paths}`) of every kept wav; the import answers with the item ids. A
track A2 that does not exist yet: `sequence.addTracks {video: 0, audio: 1}` first (`video` defaults to 1). `timeline.place` onto an audio track puts
the sound alone there; check with `sequence_inspect` that nothing on A2 was overwritten.

`VN speak --lines lines.json --takes 2 --rate 4.5 --bridge 127.0.0.1:<port>` (the open app) or `--project
film.fcproj` (only when no MCP server holds that file open) does synthesize, import and place in one call, the take
closest to `--rate` per line; `data.placed[].replaced` lists clips it overwrote.

Settings: `--voice` (default `Hải Đăng`), `--variation` 0.3–1.2 (0.8; later takes add 0.05), `--python`;
cloning `--reference clip.wav --clone-consent`. CPU only: the first line of a run loads the model (tens of
seconds).

## Re-take

Vietnamese, one line: `VN synthesize --text "…" --takes 2 --out <project dir>/voiceover/vieneu/l3-r2`, import the
pick, then in one batch remove the old clip and place the new one at the same second:

```json
{"steps": [
  {"id": "edit.clear", "params": {"clips": ["<old clip>"]}},
  {"id": "timeline.place", "params": {"item": "<new take id>", "track": "A2", "seconds": 7.8}}
], "stop_on_error": true}
```

## Checking a take

- Whisper build: `bashcut.transcript.generate {items: ["<take item>"], language: "auto"}`, then `transcript.inspect`,
  saved, into `narration.py check`. Its words are on the take's own clock.
- No Whisper: run an outside transcriber on the take's wav with word timestamps (for example `mlx_whisper` or
  `faster-whisper`, `language vi`) and pass its JSON to `narration.py check` as is.
- Per line, record in the plan: `take` (path), `item`, `seconds`, `similarity`, `unmatched`.

## Fit and level

- Speed: `clip.speedDuration {clips: ["<clip>"], speed: 92}` (percent; `ripple: false` keeps the rest in place).
- Move a cue into silence: `timeline.move {moves: [{clip, track: "A2", time}], insert: false}`.
- Original audio as a bed under a dub: `clip.audioGain {clips, mode: "set", db: -14}`, then measure the voice and
  the bed from WAV stems (`bcp:audio-mix`, `loudness.py --speech`).
- Captions: one per line from `caption`, at the take's start for its length (`bcp:captions-text`).
