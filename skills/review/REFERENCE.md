# review reference: measuring calls

Times in params are ticks (254 016 000 000 per second) unless a param says `seconds`.

## Cuts against words

`sequence_inspect` gives each clip's track, timeline start and end and source in-point; `transcript.inspect` gives
the words. A word on the timeline = its source time − the clip's source in-point + the clip's start, only while it
falls inside the clip. A cut is inside a word when it falls strictly between a placed word's start and end; a word
cut off at a clip edge by less than its full length is a clipped word. Captions: `captions.list` gives each
caption's times; compare its start with its first word's start (word-landing limit).

## Black and frozen picture

```json
{"id": "scopes.read", "params": {"scopes": ["waveform"], "waveformType": "luma", "seconds": 41.2}}
```

A waveform whose maximum stays near 0 is black. Sample each cut at −2, 0 and +2 frames and every gap on the main
video track. Frozen picture has no measure: two frames 0.5 s apart inside a clip that look identical on a sheet are
a suspect; look at more frames around it.

## Frames for looking

```sh
python3 "<skill_dir>/../footage-survey/contact_sheet.py" plan --program --at 0.5,1.5,2.5,8.0,12.4 --dir /abs/tmp/review-r1
python3 "<skill_dir>/../footage-survey/contact_sheet.py" sheet "/abs/tmp/review-r1/*.png" -o /abs/tmp/review-r1.png
```

Run the printed steps with `command_batch` between the two. One frame at phone width: MCP `render_frame {seconds,
max_side: 400}`.

## Loudness

```json
{"id": "file.exportMedia", "params": {"path": "/abs/tmp/review-mix.wav", "format": "wav", "wait": true}}
```

```sh
python3 "<skill_dir>/../audio-mix/loudness.py" /abs/tmp/review-mix.wav --curve --min-silence 2
```

Stems (mute the other tracks with `mixer.setStrip {muted: true}`, export, unmute) for the bed under the voice:
`loudness.py music.wav --speech voice.wav`. The delivery check: a WAV export with the same `loudnessLufs` as the
output; its `integratedLufs` within the tolerance and `truePeakDbtp` under the ceiling.

## What changed

`history.list` lists the edit journal: from round 2, look only at the clips and times the listed steps touched,
plus the previous round's findings.
