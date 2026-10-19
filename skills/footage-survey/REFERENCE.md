# footage-survey reference

## Cues and restarts

**Recording cues** (phone footage often starts and ends with them): words said to the camera or the crew, not to
the viewer. Find them in `transcript.inspect` and `transcript.search`, and list each with media, seconds and kind:

- **start / end of a take**: "bắt đầu", "ok quay nhé", "3, 2, 1", "rolling", "action" in the first ~3 s; "xong",
  "ok rồi", "cut", "tắt đi" in the last ~3 s. Cut them off.
- **throw away what came before**: "cắt đoạn này", "bỏ đoạn đó", "nói lại", "làm lại", "cut that", "scratch that",
  "take two", "again": the phrase before it is a dead take; the next phrase that says nearly the same words is the
  one to use, unless the frame or the delivery says otherwise.
- **clap or slate**: no words; look at the first second's frames. It is a sync point, never in the cut.

A cue is yours to judge from its words and place, not from a word list: "làm lại" inside a sentence to the viewer
("tôi làm lại từ đầu") is content.

**Suspect words hide restarts.** Whisper merges a false start into one long word: "Hello mọi người, hôm nay mình
sẽ" said twice came back as one word "demo", 1.8 s at probability 0.24, and the restart reached the video.
`words_to_transcript.py` prints every word longer than ~1 s or under ~0.4 probability (`transcript.set` keeps no
confidence, so check them before importing). Re-transcribe just that window (±1 s) with another model and read
what was said. List each restart or repeated phrase (media, seconds, both takes) with the cues, for `bcp:rough-cut`.

## Outside transcribers

Any Whisper that writes word timestamps as JSON works with `words_to_transcript.py`:

```sh
# Apple Silicon
mlx_whisper clip.wav --model mlx-community/whisper-large-v3-turbo --language vi --word-timestamps True --output-format json
# any OS (pip install openai-whisper)
whisper clip.wav --model turbo --language vi --word_timestamps True --output_format json
```

A window only (a suspect word): export that range as WAV (`file.exportMedia {format: "wav", range: "custom",
startSeconds, endSeconds}`), transcribe it, and pass `--offset` = where the window starts in the media file so the
ticks land on the file's clock. Ticks are 254 016 000 000 per second, from the media item's start.

Other tools re-transcribe with a larger model or vocabulary hints when the mean word probability is under
0.7–0.85, depending on the language and the noise.

## `contact_sheet.py`

Standard library only. `plan` prints `file.exportFrame` steps (`target: "source"`, `time` in ticks, PNG files named
`<item>-<seconds>.png`) for one `command_batch`; `sheet` tiles PNGs in name order into one sheet (default 4 columns,
320 px cells), numbers each cell in its top-left corner, and prints the sheet path then `n file seconds` per cell.
It reads 8 or 16-bit PNGs that are not interlaced, about 1.5 s per 1080p frame. Several sheets for a long folder:
one per clip, at most six for the surveyor before it zooms in.
