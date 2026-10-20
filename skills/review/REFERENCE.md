# review reference: measuring calls

Times in params are ticks (254 016 000 000 per second) unless a param says `seconds`.

## Cuts against words

`sequence_inspect` gives each clip's track, timeline start and end and source in-point; `transcript.inspect` gives
the words. A word on the timeline = its source time − the clip's source in-point + the clip's start, only while it
falls inside the clip. A cut is inside a word when it falls strictly between a placed word's start and end; a word
cut off at a clip edge by less than its full length is a clipped word. Captions: `captions.list` gives each
caption's times; compare its start with its first word's start (word-landing limit).

## Cut into a pause

`bashcut.review.run` reports `cutInWord` with the word and its span on the timeline (`start`, `end`, seconds) and
the clip in the message. Whisper's word times touch inside a phrase (0 s between words), and the bench checks cuts
against the audio's own voice activity, so a cut on a word's edge can still land in sound. Move it into a real
pause instead:

1. From `transcript.inspect` (the sequence's words, ticks), the pauses next to the word: the gap before its phrase
   and after it (at 190 words a minute they sat at commas and full stops, 0.15–0.9 s). A gap of 0.4 s or more is a
   clean cut, 0.15–0.4 s needs a look at the frames, under 0.15 s is unsafe (BashCut's rough-cut, T06 §3). Whisper
   hides long pauses inside the next word (BashCutPro#203): `loudness.py mix.wav --min-silence 0.3` (a WAV of the
   mix, `bcp:audio-mix`) lists the real silences.
2. Keep the word (cut later) or drop it (cut earlier), whichever keeps the line whole; the new cut is the middle of
   that pause.
3. `timeline.trim {clip, edge: "out", mode: "ripple", delta}` on the clip before the cut (`edge: "in"` on the one
   after), `delta` in ticks = new cut − old cut (positive extends; it needs source handles). Trimming the video
   clip moves its linked audio. Then `bashcut.review.run {checks: ["edit"], writeMarkers: false}`: `cutInWord`
   gone. Measured: a cut at 5.05 s inside "pause" (4.96–5.20 s) moved to 5.57 s (the comma pause 5.49–5.65 s) passed.

A rolling edit between two clips: `timeline.roll {left, right, delta}`.

## Black and frozen picture

```json
{"id": "scopes.read", "params": {"scopes": ["waveform"], "waveformType": "luma", "seconds": 41.2}}
```

A waveform whose maximum stays near 0 is black. Sample each cut at −2, 0 and +2 frames and every gap on the main
video track. Frozen picture has no measure: two frames 0.5 s apart inside a clip that look identical on a sheet are
a suspect; look at more frames around it.

## Frames for looking

```sh
"${BASHCUT_PYTHON:-python3}" "<skill_dir>/../footage-survey/contact_sheet.py" plan --program --at 0.5,1.5,2.5,8.0,12.4 --dir /abs/tmp/review-r1
"${BASHCUT_PYTHON:-python3}" "<skill_dir>/../footage-survey/contact_sheet.py" sheet "/abs/tmp/review-r1/*.png" -o /abs/tmp/review-r1.png
```

Run the printed steps with `command_batch` between the two. One frame at phone width: MCP `render_frame {seconds,
max_side: 400}`.

## Loudness

`bashcut.audio.loudness {series: true}` measures the mix on the timeline (integrated, short-term per second, true
peak, clipped samples): no export. Export only for what it cannot give: the music bed under the voice (stems) and
silences in a curve.

```json
{"id": "file.exportMedia", "params": {"path": "/abs/tmp/review-mix.wav", "format": "wav", "wait": true}}
```

```sh
"${BASHCUT_PYTHON:-python3}" "<skill_dir>/../audio-mix/loudness.py" /abs/tmp/review-mix.wav --curve --min-silence 2
```

Stems (mute the other tracks with `mixer.setStrip {muted: true}`, export, unmute) for the bed under the voice:
`loudness.py music.wav --speech voice.wav`. The delivery check is the export itself: `bashcut.profiles.apply` returns
`peakCheck` measured on the file (SKILL.md "The draft").

## What changed

`history.list` lists the edit journal: from round 2, look only at the clips and times the listed steps touched,
plus the previous round's findings.
