# Quality bench: Pro vs BashCut

Proves, with numbers, that BashCutPro makes better videos than the Swift BashCut, and keeps it true
(BashCutPro#58). This folder holds the harness only; the runs need a built BashCutPro (`bashcutpro`) and the
batch runner (#45), and the first scorecard is **pending the build pass**.

| File | What |
|---|---|
| [jobs.json](jobs.json) | the fixed bench set: 6 jobs (talking head → short, vlog → 60 s, podcast → 3 clips, b-roll montage to music, tutorial with captions, Vietnamese subtitles), their inputs under the raw folder, brief, skills, output profile and targets |
| [rubric.md](rubric.md) | how an output is scored and a job is won |
| [score.py](score.py) | `plan` (the files each job gets), `score` (the scorecard from measured runs), `blind` (A / B labels for the owner) |
| [scorecard-template.md](scorecard-template.md) | the scorecard's layout |

## Running it

1. **Inputs**: the workspace's raw footage (`resources/raw/`, never committed; licences in its `SOURCES.md`).
   `python3 bench/score.py plan --raw /abs/resources/raw` lists the files each job gets and flags a missing folder.
2. **Pro**: each job through the batch runner with an agent step that follows the job's `skills` from its `brief`,
   exported with its `profile`, into `<runs>/pro/<job id>/`.
3. **BashCut**: the same brief in the Swift BashCut on a mac, exported to `<runs>/bashcut/<job id>/`.
4. **Measure** each output into `metrics.json` next to it (format in `score.py`'s help): a WAV export through
   `skills/audio-mix/loudness.py`, the caption file, `sequence_inspect` cuts and `transcript.inspect` words, review
   findings and picture checks, the render time.
5. **Score**: `python3 bench/score.py score --runs <runs> --out scorecard.md`.
6. **Blind**: `python3 bench/score.py blind --runs <runs> --out <dir>`; make a contact sheet per side
   (`skills/footage-survey/contact_sheet.py` on frames of each output), show A and B to the owner, record the pick,
   then open `key.json`.
7. **Publish**: the scorecard and thumbnails (no footage) in BashCutPro as `bashcut/bench/<date>.md`; open a
   follow-up issue for every job Pro loses. Re-run after big changes.

Unit tests: `python3 -m unittest tests.test_bench` from the kit's root.
