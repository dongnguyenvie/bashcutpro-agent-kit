# Bench rubric

How [`score.py`](score.py) turns one output's measurements into a score (0–100 per category, a weighted total), and
how a job is won. Numbers come from measurements, never from reading the edit; a measurement that is missing leaves
its category out of the total ("not measured"), it is never a 0.

| Category | Weight | Measured with | 100 when | Loses points for |
|---|---|---|---|---|
| sound | 20 | `skills/audio-mix/loudness.py` on a WAV export of the final mix | integrated loudness within ±1 LU of the profile's target (−14 LUFS) | 20 per LU beyond ±1; 30 when the true peak is above the profile's ceiling (−1 dBTP) |
| captions | 20 | the exported SRT / VTT; safe area from review (`bashcut.review.run`, #57) or frames at phone size | every cue at or under 20 characters per second, all inside the safe area | the share of cues over 20 cps; the share over 25 cps counts again; up to 50 for cues outside the safe area |
| edit | 20 | cut times from `sequence_inspect` and word times from `transcript.inspect` | no cut inside a spoken word (20 ms tolerance at word edges) | the share of cuts inside a word |
| picture | 15 | review's picture checks (black / frozen frames, #36 / #57) | no black frames (except a deliberate fade at the ends) and nothing frozen | 10 per black frame, 20 per frozen second |
| review | 15 | review findings by severity | no findings | 25 per blocker, 10 per major, 3 per minor; polish is free |
| length | 10 | the output's duration | inside the job's target band | the share it is outside the band |

- **Total** of an output: the weighted mean of the categories measured. A job with several outputs (podcast: 3
  clips) averages its outputs.
- **Winner** of a job: the higher total by **3 points or more**; closer is a tie. Render time is reported, not
  scored (the two apps run on different machines and engines).
- **The owner's blind side-by-side** is recorded next to the numbers and does not change them: a job the numbers
  call a tie or a Pro win but the owner picks BashCut is a finding too.
- **Every job Pro loses** (by the numbers or the owner's pick) gets a follow-up issue in BashCutPro naming the
  categories it lost.

Targets per job are in [jobs.json](jobs.json) (`target`: length band, loudness, true peak, captions expected);
output profiles follow BashCutPro's output profiles (#43) when they exist.
