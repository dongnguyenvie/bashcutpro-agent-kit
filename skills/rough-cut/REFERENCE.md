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

## Two ways to cut

### Additive: subclips in story order

```json
{"steps": [
  {"id": "source.open", "params": {"item": 3}},
  {"id": "clip.makeSubclip", "params": {"item": 3, "name": "S1-hook", "start": 15602457600000, "end": 19025798400000}},
  {"id": "clip.makeSubclip", "params": {"item": 3, "name": "S4-proof", "start": 47201000000000, "end": 52113000000000}},
  {"id": "source.open", "params": {"item": 1}},
  {"id": "clip.makeSubclip", "params": {"item": 1, "name": "S2-setup", "start": 2540160000000, "end": 6350400000000}},
  {"id": "timeline.place", "params": {"items": ["<S1-hook id>", "<S2-setup id>", "<S4-proof id>"], "track": "V1", "seconds": 0}},
  {"id": "file.save", "params": {}}
], "stop_on_error": true}
```

Ids are numbers (`item` from `project_inspect`, clips from `sequence_inspect`), never names like `M3`.
`clip.makeSubclip` is refused until a clip is open in the Source monitor, hence `source.open` first. It returns the new item's id; the place step needs those ids, so run the subclip steps as one
batch, read the ids from its results, then the place batch. Alternatively place each range straight from the
media with `timeline.place {item, sourceIn, duration, seconds}` (each its own undo step), without subclips; the
subclips are the select record you can see in the project.

### Subtractive: remove by text on a placed take

```json
{"steps": [
  {"id": "timeline.place", "params": {"item": 3, "track": "V1", "seconds": 0}},
  {"id": "transcript.extract", "params": {"from": "<word id>", "to": "<word id>"}},
  {"id": "transcript.removeFillers", "params": {"fillers": ["ờ", "à", "ừm", "um", "uh"]}},
  {"id": "transcript.removePauses", "params": {"minSeconds": 0.6, "keepSeconds": 0.25}},
  {"id": "file.save", "params": {}}
], "stop_on_error": true}
```

- `transcript.extract` removes and closes the gap (ripple); `transcript.lift` leaves the gap (for cover footage
  dropped in later). Work from the **end of the take backwards**, so earlier word ids keep their place.
- `removePauses`: `keepSeconds` 0.2–0.3 keeps speech breathing; tighter reads as a jump-cut machine. A pause with
  a reaction or a look in it is content: check it with `render_frame` before removing pauses wholesale on a
  reactions source.
- `removeFillers`: give the fillers of the language spoken. In Vietnamese "à", "ừ" can be meaningful answers:
  read the hits (`transcript.search`) before a wholesale removal.

`transcript.select {from, to}` selects the clip range of those words on the timeline, for a command that works on
the selection (`sequence.lift`, `sequence.extract`, `edit.rippleDelete`).

## Checking edges before the batch

For each planned edge, compare with the words from `transcript.inspect`:

- a cut at time T is **inside a word** when some word has `start < T < end`: move it to that word's `start` or
  `end`;
- the gap before / after the edge (next `start` − previous `end`): ≥ 400 ms clean, 150–400 ms look, < 150 ms
  unsafe (T06 §3);
- no recording cue ("cắt đoạn này", "take two", "làm lại", a clap) inside the range.

A cut inside a word is a review error later (`bcp:review`); finding it now costs nothing.

## Selects record

The selects in the plan are the record of what was picked and why. Optional, visible in the app: a range marker
per select on the source (`markers.addRange {name, comment}` with the reason) or the reason on the subclip
(`metadata.set {item, field: "Comment", value}`).
