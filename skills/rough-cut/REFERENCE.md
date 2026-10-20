# Rough cut: reference

Detail for `bcp:rough-cut`. "T06 §n" cites BashCut's rough-cut research notes, where each number was measured.

## Ticks

FilmCraft times are ticks: **254 016 000 000 per second**. 61.42 s = 15 601 662 720 000 ticks. Word `start` /
`end` from the transcript are already ticks: copy them, never convert from rounded seconds. Commands that take
`seconds` or `frame` say so in their params (`timeline.place`, `playhead.set`).

## Words from outside (no Whisper build)

`transcript.models` → `"available": false` means `transcript.generate` cannot run. Transcribe outside (any tool
that gives word times), convert to ticks and import per media item:

```json
{"id": "transcript.set", "params": {"item": "<media id>", "transcript": {
  "language": "vi", "speakers": [{"name": "Host"}],
  "words": [{"text": "Lần", "start": 15602457600000, "end": 15729465600000, "speaker": 0},
            {"text": "đầu", "start": 15729465600000, "end": 15856473600000, "speaker": 0}]}}}
```

Every other `transcript.*` command then works on these words.

## tighten.py

```
"${BASHCUT_PYTHON:-python3}" <skill_dir>/tighten.py --words words.json --item 3 --keep 117-124,103-116,125-171 --fps 30
    [--min-pause 0.35] [--keep-pause 0.12] [--lang en|vi] [--fillers "um,uh,you know"] [--protect 40,41]
    [--wav scratch.wav [--wav-start 0]] [--track V1] [--label "short-01 tighten"]
```

| Flag | Default | What |
|---|---|---|
| `--words` | | `transcript.inspect` of a scratch sequence holding the whole item at 0 (word times on the item's clock) |
| `--keep` | | word-index ranges in story order (`from`-`to` of a `transcript.search` hit) |
| `--fps` | 30 | the output sequence's rate: `25`, `30000/1001` |
| `--min-pause` | 0.35 | a pause this long between kept words is cut |
| `--keep-pause` | 0.12 | quiet kept on each side of a cut pause (at most half the gap) |
| `--lang`, `--fillers` | en | en: um uh umm uhm erm er ah ahm hmm mm mhm; vi: ờ ừm ơ ờm hừm. Phrases allowed ("you know") |
| `--protect` | | word indices never dropped (a filler that is the content, a repeat on purpose) |
| `--wav` | | the scratch sequence exported as WAV: an edge the energy says is still in speech moves into quiet in the gap |

Output: `{"command": <bashcut.batch>, "report": {...}}`. The report's `edgesMovedBySound` stays 0 on words already
refined by `bashcut.transcript.generate`; `--wav` is for words imported with `transcript.set` when
`refineEdges` cannot run. Measured on a 167 s two-voice test (30 fps): three clips 22–34 s from 41–49 s of
selects, 11–20 cuts each, every filler and false start out, 0 `cutInWord` in `bashcut.review.run`.

The batch places from the media item (`timeline.place {item, track, frame, sourceIn, duration}`), back to back from
frame 0 of the active sequence: run it on an empty sequence, or shift `frame` by hand to append.

## Other ways to cut

### Subclips in story order

For a select record you can see in the project:

```json
{"id": "bashcut.batch", "params": {"label": "selects", "commands": [
  {"id": "source.open", "params": {"item": 3}},
  {"id": "clip.makeSubclip", "params": {"item": 3, "name": "S1-hook", "start": 15602457600000, "end": 19025798400000}},
  {"id": "clip.makeSubclip", "params": {"item": 3, "name": "S4-proof", "start": 47201000000000, "end": 52113000000000}}]}}
```

Ids are numbers (`item` from `project_inspect`, clips from `sequence_inspect`), never names like `M3`.
`clip.makeSubclip` is refused until a clip is open in the Source monitor, hence `source.open` first. It returns the
new item's id; read the ids from the batch's results, then `timeline.place {items: [...], track: "V1", seconds:
0}` puts them back to back. Subclips are not tightened: fillers and pauses inside them stay.

### Remove by text on a placed take

One clean take, mostly kept: place it, then remove what is not wanted, **last range first** so earlier word ids
keep their place:

```json
{"id": "bashcut.batch", "params": {"label": "trim take", "commands": [
  {"id": "timeline.place", "params": {"item": 3, "track": "V1", "seconds": 0}},
  {"id": "transcript.extract", "params": {"from": 412, "to": 431}},
  {"id": "transcript.extract", "params": {"from": 88, "to": 97}}]}}
```

- `transcript.extract` removes and closes the gap (ripple); `transcript.lift` leaves the gap (for cover footage
  dropped in later).
- `transcript.removeFillers {fillers}` and `transcript.removePauses {minSeconds, keepSeconds}` work on the placed
  words, without the false-start pass or the frame-exact edges of tighten.py. `keepSeconds` 0.2–0.3 keeps speech
  breathing.
- In Vietnamese "à", "ừ" can be meaningful answers: read the hits (`transcript.search`) before removing them.

`transcript.select {from, to}` selects the clip range of those words on the timeline, for a command that works on
the selection (`sequence.lift`, `sequence.extract`, `edit.rippleDelete`).

## Checking edges before the batch

For each planned edge, compare with the words from `transcript.inspect`:

- a cut at time T is **inside a word** when some word has `start < T < end`: move it to that word's `start` or
  `end`;
- the gap before / after the edge (next `start` − previous `end`): ≥ 400 ms clean, 150–400 ms look, < 150 ms
  unsafe (T06 §3);
- no recording cue ("cắt đoạn này", "take two", "làm lại", a clap) inside the range.

A cut inside a word is a blocking `cutInWord` in `bashcut.review.run` later (`bcp:review`); finding it now costs
nothing. tighten.py's edges pass this by construction; check the ones you place by hand.

## Selects record

The selects in the plan are the record of what was picked and why. Optional, visible in the app: a range marker
per select on the source (`markers.addRange {name, comment}` with the reason) or the reason on the subclip
(`metadata.set {item, field: "Comment", value}`).
