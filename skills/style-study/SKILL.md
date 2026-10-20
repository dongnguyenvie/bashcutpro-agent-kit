---
name: style-study
description: Learn a creator's or channel's editing style by measurement (pacing, shots, hook, speech, sound, colour, text) in a separate study project, using the survey, beat and colour tools, and turn it into a profile with tolerances, a look, caption and title presets and an edit plan, without copying content. Triggers: "học style", "phân tích kênh", "làm giống kênh X", "dựng theo phong cách này", "phân tích video của tôi", "kênh của tôi", "style study", "edit like this video".
---

# Study a style

**Measure → look at frames → profile with tolerances → differences.** Profile numbers come from the references,
never from this skill.

## Sources

Use the user's videos or download references (e.g. `yt-dlp`); keep them in a private folder outside any project
that will be published, and never re-upload them.

How many: one video to mimic that clip; a channel style needs several (5–15 in one study, 10–30 in another).
Confidence by sample count: under 10 low, 10–15 medium, above 15 higher; say the tier next to every number.

## 1. Measure

In a separate study project, never the one you publish: `file.newProject`, `bashcut.media.import {paths}`, then
one sequence per reference (`file.newSequence {name, fromItem}`) so its cuts and words sit on a timeline. The
analysis commands read the **active** sequence (`sequence.open {item}` per reference) and need no export: never
render a reference to a WAV or video to measure it.

| Facet | How | Record |
|---|---|---|
| Rhythm | `clip.sceneEditDetection {applyCuts: true, wait: true}` on the reference's sequence (the study copy is cut, not the file), then clip lengths from `bashcut.timeline.summary` (start / end / duration in seconds) | mean, median, cv, the most common length, cuts per minute; cuts per 10 s, a shot-length histogram |
| Shot sizes, moves | look at sheets and describe the shots (`bcp:footage-survey`: `contact_sheet.py`, `metadata.set`) | shares of each size, move, direction; runs of the same size and move |
| Hook and close | `contact_sheet.py plan --program --from 0 --to 3 --count 6`; the first words in `transcript.inspect` | first cut, first words, first text on screen, the last seconds |
| Speech | words via `bashcut.transcript.generate` or an outside transcriber + `transcript.set` (`bcp:footage-survey`) | rate p10 / p50 / p90 (syllables for Vietnamese), pauses, speech share |
| Music | `bashcut.audio.beats {clip}` on the reference's clip (BPM, beats in sequence seconds); cuts from the summary against the beats; `beats.py --cuts` (`bcp:beat-cut`) for downbeats and energy | tempo, how many cuts land within 2 frames (0.07 s at 30 fps) of a beat, beats per shot |
| Sound | `bashcut.audio.loudness {}` on the reference's sequence (integrated LUFS, true peak), `{series: true}` for the short-term curve, `{range}` over word spans and over gaps (`bcp:audio-mix`) | integrated LUFS, true peak; short-term level during words vs in the gaps |
| Stills | `bashcut.review.pictureChecks {}` (frozen and long-still stretches in seconds) | share of seconds with a still picture, the longest still |
| Colour | `scopes.read` at sampled times per shot; `grade.py measure` on the file (`bcp:color-grade`) | black, white, mid, saturation, tint per band, per reference |
| Text | by eye on the sheets: no OCR in BashCutPro | share of seconds with text, where it sits, size as a share of the frame, words per card, how long a card holds, case and look |
| Faces | by eye on the sheets | share of shots with a face, its size, where it sits |

Its sound is one mixed track: read music under voice from the gap level against the word level. A WAV export
(`file.exportMedia {format: "wav"}`) only when an outside script (`beats.py`, `loudness.py --curve`) is really needed.

## 2. Look before trusting a number

Numbers flag, eyes decide.

- Scene detection misses dissolves, whips and fades through black, fast camera moves score like cuts, and a hard
  cut in a dark scene can score very low. Look: a sheet at about one frame a second for structure, frames around a
  suspect cut, a lower or higher `sensitivity` for another pass; `edit.undo` and rerun, or fix the cut by hand.
- Open the 3–5 longest shots and the opening on frames before writing about them.
- Speech recognition invents text over music: check the words against the frames before counting speech.
- A beat grid on a song with rubato or speech over it is weak (`bcp:beat-cut` section 2): report the confidence.
- Mark anything you estimated (by eye, from a few frames) as `est.`.

## 3. Profile with tolerances

Per facet: median and p25–p75 across the references (not only a mean), with n, files and date. Tolerance:

- ±20–40 % for shot length, cut rate and duration, as a **preference**, not a gate; sources contradict (one: ±30 %
  a must; another: ×0.7–1.3 "a preference, not a hard rule"). Tighten for "exactly like X"; widen when our footage
  has less coverage than the reference or the length differs a lot.
- Keep the cut **rate** per section type (hook, body, payoff), not the total number of cuts, when our video is
  longer or shorter. Hand the band to `bcp:beat-cut` as a range.
- Priority: the user's instruction > what our footage allows > the reference.
- Colour and sound are raw values (black / white point, saturation, tint; level under words and in gaps), not
  labels like "matte" or "punchy".

## Own-channel mode

The creator's own history is the benchmark, not genre averages. With view counts, rank each video by its
**multiple over the channel's own median** (needs at least 4 videos); report it and let the creator judge (one
source flags 1.5–3×). The multiple says a video did well, not why: compare the outliers' profile with the rest and
call it a pattern to test, with its confidence tier. Without view counts, the profile is "how you edit now".

## 4. Differences, not a copy

- Per reference, one learn / don't-take note: what to learn (rhythm, structure, transition type, camera idea,
  holds) and what not to take.
- Never reproduce their text, music, graphics, logos or characters, their exact sequence of shots, or a look so
  close it passes for theirs.
- Before planning, list 3–5 deliberate differences across structure, opening, signature move, look, music and
  ending; one source asks that at least 4 of these 6 differ.
- After the cut, measure ours the same way (`bashcut.timeline.summary`, `scopes.read`, `bashcut.audio.loudness`,
  `bashcut.audio.beats`), put
  frames of ours and theirs side by side (`contact_sheet.py sheet` with both sets of PNGs), and check the
  differences are still there.

## 5. Into the edit

1. **Profile and edit plan** in the publishing project's notes (`bcp:edit-workflow`, a `style` key next to the
   plan): the profile table (facet, median, p25–p75, tolerance, n, confidence, source and date), the learn /
   don't-take notes, the differences, and 5–10 rules, each with its number. The plan's sections take their length
   bands and cut rates from it.
2. **Look**: start from the closest pack look (`bashcut.looks.list {tags}`, drawn on our frame with
   `bashcut.looks.thumbnail {look, frame: true}`) and its `intensity`; when none is close, move a `grade.py` look
   toward the measured values (`grade.py match` against the profile's numbers). On the adjustment layer
   (`bcp:color-grade`); keep it with `presets.save` and `lut.export` (a pack look: `bashcut.looks.export {look, path}`).
3. **Text**: one caption restyle (`captions.setStyle`) and title templates (`graphics.template.export`) built from
   the measured placement and size (`bcp:captions-text`); a signature move as an effect preset (`presets.save`).
4. **Review limits**: when the user wants the style checked, set the plan's `review` limits (shot lengths, cut
   rate) from the profile's range (`bcp:review`). After the edit, `bashcut.review.run {profile}` on every output
   sequence (`sequence.open` first) must report `blocking: 0`, and ours measured again must sit inside the profile's
   tolerance (median shot length and cuts a minute within ±30 %, loudness within 1 LU of the output's target, not the
   reference's).

Tell the user the rules that matter most (numbers, n, confidence) and the differences you will keep.
