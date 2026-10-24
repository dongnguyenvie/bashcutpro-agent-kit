---
name: beat-cut
description: Give an edit rhythm by measurement: beat grid from music or word edges from speech, shot lengths per section, punch-ins, beat sync checked. Use when cutting to music or the cut feels flat. Not for cutting speech by quote (bcp:rough-cut) or transitions and speed (bcp:effects). Triggers: "cắt theo nhịp", "cắt theo beat", "khớp nhạc", "lệch nhịp", "bản dựng phẳng", "nhàm", "punch-in", "cut to the beat".
---

# Beat cutting and punch-in reframes

The loop: **measure → choose → cut → measure again → adjust**. Numbers are ranges with their source (the BashCut
kit's research notes, naming the editors' kits they came from). Starting points, not targets: a user's reference,
measured with `bcp:style-study`, wins.

## 1. Measure what drives the cuts

| Video | Cuts follow | Measure |
|---|---|---|
| Montage, travel teaser, MV, music-led | beat grid, music energy | `beats.py` on the music (section 2) |
| Talking, review, food with speech, tutorial | phrase edges; picture follows words | `transcript.inspect` word times, speech rate |

Speech-led: do **not** lay cuts on the grid first (one BashCut grid-first draft had 10 silent gaps, 21 s). Chain the
spoken lines, cut picture at phrase ends (the gap before a word), then put music under it. Speech rate is words
per second from `transcript.inspect` (syllables for Vietnamese); denser speech carries more per shot, so shots hold
longer. Before a music hit after a line, leave 0.1–0.6 s of air (bestagentkits ≥ 0.12 s, video-use 400–600 ms).

Long pauses, fillers and false starts in talking clips: bcp:rough-cut `tighten.py` (`--min-pause 0.4 --keep-pause
0.1` were BashCut's starting point: shorter for a fast talker, more kept for a slow one). Its edges come from word
times already refined on the audio (`bashcut.transcript.generate`, or `bashcut.transcript.refineEdges` after
imported words), so no cut lands inside a word. Look at the long pauses before running its batch (`render_frame` on
both sides): a long "pause" can be a reaction, a laugh or b-roll sound; `--protect` its words or split the range.
Then section 6.

## 2. Read the music

Music on the timeline: `bashcut.audio.beats {clip, writeMarkers?}` returns `bpm`, `confidence`, `beats` and
`downbeats` in sequence seconds; `writeMarkers: true` adds them as markers (Beat / Downbeat) in one undo step. Use it
first. `beats.py` in this folder stays the fallback (a WAV not on the timeline, `alternates` and `phaseScores`, or a
build without the command): a small out-of-process estimate, standard-library Python, a WAV in, JSON out.

1. A WAV of the music: the file itself when it is WAV, else place the music, mute the other tracks
   (`mixer.setStrip {muted: true}`), `file.exportMedia {format: "wav", range: "custom", startSeconds, endSeconds,
   wait: true}` over the clip, unmute.
2. `"${BASHCUT_PYTHON:-python3}" "<skill_dir>/beats.py" music.wav` → `tempo`, `alternates`, `confidence`, `beats`, `downbeats`,
   `fit.rmsErrorMs`, `phaseScores`, `strengths`, `energy`. Seconds are on the WAV's clock: a beat lands on the
   timeline at clip start + (beat − source in-point) (`--at`, `--source-in` do it for you).
3. `beats.py music.wav --markers --at START [--source-in S] [--duration D] [--downbeats]` prints the `markers.add`
   steps for one `bashcut.batch`, so the grid shows on the timeline.

Judge the grid before cutting on it. You cannot listen: a weak grid means ask the user, or cut on phrases.

| Fact | Strong | Weak → do |
|---|---|---|
| `fit.rmsErrorMs` | small next to a frame (33 ms at 30 fps); kits gate at mean < 10 ms (shotcraft), median < 15 ms (jianshuo) | tempo drifts: run per song or section, cut on phrases |
| `confidence` | stands out from the alternates | rubato, ambient, speech-heavy: energy lifts / drops and phrases |
| `alternates` | one tempo clearly stronger | similar (often double or half: 120 vs 60): pick by how fast the music moves, rerun with `--bpm`, ask the user. One BashCut example: 58.7 BPM detected, truth 117 |
| `downbeats`, `phaseScores` | one phase clearly highest | close: a grid can lock onto hi-hats, every cut half a beat late. Ask the user to check a downbeat hits |
| `strengths` | — | "the hit table is a candidate pool, not a trigger" (shotcraft) |

Several songs: run each. Find moments in `energy` yourself: a **lift** is the level rising several dB over ~2 s
against the 2 s before, a **drop** the reverse, a **breath** a 0.5–2 s dip before a lift. Snap each to the nearest
beat or downbeat. Pointers, not cut points: they shape a section, build → breath → hit on a downbeat → hold
(reelmimic). One breath of 0.5–2 s before the main hit, a payoff hold of ≥ 1 s.

## 3. Choose shot lengths and cut points

Pick a band per section, then move inside it by content:

| Genre / section | Median shot | Source |
|---|---|---|
| Fast short-form, montage, ads, food inserts | 0.6–2 s | assafkip, iart, znyupup |
| Speech-led vertical | 2–4 s | shot grammar notes |
| Narrative, vlog, b-roll travel | 2.5–6 s (travel 3–4.5 s) | higgsfield, vox-director, vlog plugin |
| Calm vs urgent tone | 2–4 s vs 0.4–1 s | saas-motion-kit |
| Hero hold | one per film, 1.5–2.5× the average | higgsfield |

- **Shorter**: high-motion, low-information shots, energy lifts and drops; **longer**: dense speech, text to read,
  landscapes, calm tone, after a breath.
- Cuts per minute seen: dialogue 14–16 (davinci, "descriptive, NOT a target"), daily vlog 8–12, review 10–14,
  travel 13–16 (vlog plugin), food TikTok 30–40, cinematic vlog 12–20 (style-study). Compare, don't aim.
- **Beats per shot 2–8**, fewer at peaks (opuscar); cutting every beat for over ~8 beats reads as noise. Seconds =
  beats × 60 / BPM (4 beats: 2 s at 120, 2.7 s at 90): choose the count from the band, not a pattern.
- Vary the rate: one acceleration, one breath, a hero hold. Open with the hook for short form, establish first for
  narrative, real estate or a travel arrival; the plan says which.

One BashCut example (travel / food vlog, not a rule): cold open 6 beats (~2.6 s), busy sections 4 (2 on peaks,
~1.6–2.0 s), quiet ending 4 on slow music (~3.5–4 s); a uniform 3.6 s cut felt flat whatever the content; pieces
under ~0.6 s were merged. Its cold open: about 8 s, three shots (the ending, the loudest, the quietest), then
chronological, with a place label at each change of location. A high cuts-a-minute count is a choice: say why.

## 4. Cut in one batch

Plan in beats and seconds, convert last. Per section: cut points → (clip, in-point) from its moments in turn → one
`bashcut.batch {label: "<section>", commands}` of `timeline.place {item, track, frame, sourceIn, duration}` (or
`timeline.razor` / `timeline.trim` on what is placed), the label also in the plan's log. Spread in-points across sources; never reuse one spot.
`timeline.roll` nudges a cut onto a beat or word gap; `timeline.slip` changes what a clip shows. Times are ticks
(254 016 000 000 per second).

## 5. Punch-in reframes from measured headroom

The most effective change when the footage has one angle. Read each clip's Motion scale in `sequence_inspect`.

- **Headroom** is the largest zoom before upscaling: media size over the size it fills in the sequence (media
  size from `bashcutpro-cli probe` or `project.items`). ~2 for 4K in a 1080 landscape sequence, 1.0 for
  same-resolution footage (every punch-in upscales), ~1.125 for 4K landscape filling 1080×1920.
- **Step** by purpose: size change at a cut 1.15–1.3, snap punch on a word 1.1–1.15, slow drift 1.03–1.07 over the
  shot. Aim for one described size step (wide → medium → close), within headroom where you can.
- Past headroom is a judgement, not a limit: look at `render_frame` first. One BashCut example: same-resolution
  footage looked acceptable at 1.28, soft beyond.
- `effects.setParam {clip, effect: "motion", param: "Scale" | "Position", value}`; `keyframe: true` for a drift.
  Pan and tilt need margin. Place the crop on what matters, seen in the frame, never a blind centre
  (`bcp:effects`).
- Never punch in on signs or text (one example: 1.28 cut "Lẩu Bò Nồi Đất" to "Nồi Đấ").

Neighbouring cuts keep the same framing only by choice. One edit's rotation (zoom, x, y): (1.00,0,0)
(1.28,60,−25) (1.14,−50,15) (1.22,0,30) (1.00,0,0) (1.18,70,10). Talking heads: punch-ins every 4–6 s seen (vlog
talking-head recipe; ghost-editor 4–6 per 60 s reel), timed to sentence starts, not a clock.

## 6. Measure again, then adjust

From `bashcut.timeline.summary` (cut times, clip lengths) and the same `beats.py` run:

- **Rhythm** (overall, per section): median, cv (standard deviation / mean), cuts per minute against your band. 6+
  consecutive shots varying under ~0.15 cv (davinci) or one length over ~60 % of shots (saas-motion-kit) is
  monotony: break it unless the calm is intended.
- **Runs of the same size and move** (the survey's descriptions in `metadata.get`): 2 → look; 3+ → change size,
  angle or relation, or say why (a motif, a locked-off talk) (higgsfield). A talking head is one setup: punch-ins
  make the change. The same source just before and after a cut with a small gap is a jump cut.
- **Beat sync**: `beats.py music.wav --at START --cuts t1,t2,… --fps F` gives each cut's offset. Hard cuts within
  ±1–2 frames; 3 is perceptible (shotcraft pass ≤ 3 f, ideal ≤ 1.5 f). A median away from 0 with a tight p10–p90:
  the grid's phase or the whole music is off, shift once or recheck the downbeat, not cut by cut. A wide spread:
  cuts are off the grid, roll them.
- **Whole-picture hits**: a cut on the beat changes *when*, not *how hard*. Hits on every kick read as the camera
  shaking. One promo study: ~2–4 per 30–60 s, on the strongest beats, ~16 beats apart; other accents moved one
  element (title, card, number), not the frame. MV, event and hype edits use many more on purpose.
- **Word sync**: `bashcut.review.run {profile, checks: ["edit"], writeMarkers: false}` lists every `cutInWord`
  (blocking) and gap; a cut inside a word clips it: roll it into the gap. At least 70 % of all cuts on a word edge.

Then look: `render_frame` on three consecutive cuts in one scene (three shot sizes?) and across a doubtful cut.
Adjust with roll / slip, measure again; stop after 3 rounds or when a round changes nothing, and say what is left
and why. Lock the cut before `bcp:audio-mix`.
