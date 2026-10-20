---
name: effects
description: Pick the effect that fits the moment and genre, then make it in BashCutPro with FilmCraft commands: video and audio transitions (Cross Dissolve, the Wipe folder, recipes for whip, crash-zoom, glitch, flash), Ken Burns and punch-in with Motion keyframes, speed ramps (Time Remapping), reverse, freeze frames, reframing to vertical (Auto Reframe, Motion, blurred backdrop), masks that follow and blur a logo, effect presets. Use when the user asks for transitions, motion, speed changes or a vertical reframe, or when a cut looks flat or repetitive. Triggers: "effects", "add a transition", "speed ramp", "Ken Burns", "punch-in", "freeze frame", "reframe to vertical", "hiệu ứng", "chuyển cảnh", "tua nhanh", "làm chậm", "zoom vào màn hình", "cắt khung dọc", "chữ nhảy".
---

# Effects: look, then when, then how

Decide **when** first; most cuts stay hard. The ranges below come from the editors' kits that BashCut's research
notes compared (T08 effects, T07 pacing, T19 reframing); a measured reference or the user's taste wins. Measure,
choose, act, look again. Tables, the transition name map and recipes: `<skill_dir>/REFERENCE.md`.

Effects are data, not commands. `effects.list {"kind": "Video"}` returns 130 video effects, `"VideoTransition"`
112 transitions, `"AudioTransition"` 3; `folder` narrows (`"Video Transitions/Wipe"`), `detail: true` adds each
one's parameters. Use names exactly as the list prints them; never guess one from another editor.

## 1. Read what the cut already does

`bashcut.timeline.summary` gives every clip with its id, start, end and duration in seconds (shot lengths, cuts
a minute); `sequence_inspect` adds the effect lists with keyframes and the transitions at each cut. Count from them:

- transitions by name, and runs of one name on neighbouring cuts;
- Motion keyframes per clip: shots that all push in the same way (one failure: all 12 shots a push-in,
  vox-director; T08 §2), one interpolation on most moves, long stretches with no motion at all;
- stills and locked-off shots: `bashcut.review.pictureChecks {range}` lists frozen and long-still stretches in
  seconds; each one with no speech over it needs motion (§3) or a cut;
- look at the frames that matter with `render_frame` (before, inside and after each cut you plan to touch).

Decide **motif or mistake** for each pattern; a motif is fine when it is a choice. Other kits warn on: the same
transition on two consecutive cuts, one kind more than 2x in a film under 60 s (3 when longer), fewer than 3
families when there are 5+ cuts, one ease on more than half the moves (saas-motion-kit `variety_audit`; T08 §2).
Prompts to look, not rules.

## 2. When

- **Effects serve a moment, not the whole video.** Special transitions: 1-3 per minute of short form, 0-1 in
  documentary or cinematic work (saas-motion-kit, openmontage, hyperframes; T08 §3); the rest are hard cuts on a
  sentence, beat or action. Speech-led, documentary and cinematic edits keep most cuts hard; motion-graphic and
  short-form ads rotate flavours.
- **Choose by what the cut means**, never by rotating kinds by shot number (student-kit; T08 §4): new place:
  whip, slide or cover-the-lens; same place, time skip: a short dip, Cross Dissolve or a jump cut; product or dish
  reveal: speed ramp, freeze or a crash-zoom into it; end of a chapter: dip to black; memory or dream: a long
  dissolve or a blur dissolve. A dissolve says time passed; between takes of one sentence use a snap punch-in
  instead (ghost-editor; T08 §3).
- **Never use a flash or transition to hide a missing action** or a moment that should be seen (ReelMimic).
- **Whole-frame hits are rare** (flash, blink, crash-zoom, flicker, full-frame zoom punch, exposure pop): each is
  a slam. One promo study kept about 2-4 per 30-60 s on the strongest beats and moved only an element on the other
  beats; event and MV edits use far more. FilmCraft has no beat analysis: take beats from markers or from
  bcp:beat-cut, and keep full-frame impacts at least 16 beats apart unless the genre wants more.
- **Every visible move gets a matching sound**, sized to it (bcp:audio-mix); cutting all music and SFX for 1-2 s
  on a punchline worked once.
- Cinematic: hard cuts, no whoosh; the look and serif captions carry the feel.

Which effects fit which genre: the genre table in `<skill_dir>/REFERENCE.md`.

## 3. Motion: camera-like moves

Made with Motion keyframes: `effects.setParam {"clip", "effect": "motion", "param", "value", "time",
"keyframe": true}`, then `effects.setInterpolation` on each key. Ranges (T08 §3):

| Move | Range | Source |
|---|---|---|
| Slow drift, Ken Burns | 0.3-1.5 %/s, about 103-107 % scale over a shot; alternate direction between shots | talkcraft, jianshuo, digitalsamba |
| Snap punch on a word | 110-115 % | kinocut, ghost-editor |
| Size change at a cut | 115-130 %, capped by headroom | bcp:beat-cut |
| Beat pulse | 2 % or less as texture; full-frame impacts at most 3 per film, 16+ beats apart | bestagentkits, guizang |

- **No frozen picture.** A photo, a screenshot or a locked-off shot held over 1.5 s with nothing said over it reads
  as a stuck video (the review's `frozen` finding): give it a drift (0.5–1 %/s) from its first frame to its last.
- State drift as a rate so short and long shots feel alike: end scale = 100 x (1 + rate x seconds); 0.5 %/s over
  8 s is about 104 %.
- **The ceiling is resolution, not taste.** Source size over the sequence frame size (both in `doc_inspect`) is
  the zoom you can take at native sharpness; past one output pixel per source pixel it upscales, so look at
  `render_frame` before keeping it. A 1080p clip in a 1080p sequence has no headroom: keep its punch small.
- Two moves in a row read as a glitch: merge them into one gesture, front-load the travel (student-kit). Ease out
  on entrances, in on exits (`easeOut` / `easeIn`), `linear` only for a constant drift.
- Camera shake is the `Camera Shake` effect; a shaky source wants `Warp Stabilizer` first, not more motion.

## 4. Speed and time

Speed changes break lip sync: b-roll and action only, never talking shots.

- `clip.speedDuration {"clips", "speed": percent, "reverse", "ripple", "interpolation"}`: a constant speed or a
  reverse. `ripple: true` keeps the cut closed after the clip gets shorter or longer.
- Ramps: keyframe the clip's `Time Remapping` effect (find its index in the clip's effect list), with eased keys
  either side of the change.
- Freeze: `clip.frameHold` holds one frame for the whole clip; `clip.insertFrameHoldSegment {"clip", "time",
  "seconds"}` inserts a held stretch, the usual freeze + label.
- Real slow motion needs 50/60/120 fps sources; slowing 30 fps below about 50 % stutters (T08 §3). If it must,
  try `clip.setTimeInterpolation {"mode": "opticalFlow"}` and watch 1–2 s of it with `render_preview`.
- A few frames short: slow the clip slightly (102-110 %, vox-director), never freeze its last frame.
- Fast-forward: 150-200 % when narrated over, 400-2000 % for silent waiting (digitalsamba, vlog tutorial; T19
  §3). One example: a 65 s typing stretch read clearly at 16x (about 4 s) with no presenter or captions and one
  label saying what happens (the action, never the speed or effect name).

## 5. Transitions

`sequence.applyVideoTransition {"clip", "effect", "frames", "edge": "in"|"out", "params", "reverse"}` puts one on
a clip's edge; `sequence.applyAudioTransition` the same for sound (`Constant Power` for a smooth crossfade).
Frames = seconds x the sequence fps. Change one later with `sequence.setTransition` (duration, alignment),
remove with `sequence.removeTransition`. `effects.setDefaultTransition` sets what `trim.applyDefaultTransition`
adds.

| Kind | Length |
|---|---|
| Whip, slide | 0.2-0.4 s; 1-2 per short; same direction on both sides, never back and forth in a row |
| Dissolve, dip to black | 0.3-1.0 s; bookend fades and chapter dips 0.5-1.0 s |
| Zoom, spin, wipe and similar | quick 0.2-0.5 s, standard 0.7-1.5 s |
| Card turns (swing, arc) | about 0.3 s, between full-frame cards of an explainer; never between footage shots |
| Glitch (RGB split) | 0.2-0.4 s; hype, showreel and comic edits only, about every 2.7 s at most |
| Impact (slam, flash, crash-zoom) | 0.10-0.25 s after its target is fully visible |

Only `Cross Dissolve` (and the audio `Constant Power`) are known by name. For anything else, list the 112
transitions once (`effects.list {"kind": "VideoTransition"}`, or the Wipe folder) and pick by its name; when none
fits, build it from Motion, Opacity, Gaussian Blur or RGB Split keyframes around the cut. BashCut's 39 kinds,
each with its FilmCraft name or recipe: the map in `<skill_dir>/REFERENCE.md`.

## 6. Effects on a clip

`effects.apply {"clips": [id], "effect": "Gaussian Blur"}` (names or ids such as `gaussian_blur`). The new effect
goes **before** the intrinsic Motion, Opacity and Time Remapping in the clip's effect list, so its index is not
the last one and Motion's index moves. Read the clip's effect list before and after (`sequence_inspect`) and use
the index of the entry that appeared; address Motion as `"effect": "motion"`, never by an old index.

Useful ones: `Gaussian Blur`, `Crop`, `RGB Split`, `Light Leaks`, `Camera Shake`, `Mosaic`, `Warp Stabilizer`,
`Lumetri Color` (looks: bcp:color-grade), `Auto Reframe`. An effect over a range of several clips (a black-and-white
moment) goes on an adjustment layer: `file.newAdjustmentLayer {"seconds"}` on a track above, then the effect on it.
A setup worth reusing: `presets.save {"clip", "effects", "name", "keyframes": "scale"}`, then `presets.apply`.

## 7. Reframe: crop only to what matters

A crop decides what the viewer loses. Look first, never crop blind.

1. **Look** at the start, middle, end and action peaks of each shot with `render_frame`. FilmCraft has no face or
   subject boxes; the `bashcut.vision` plugin finds them (`subjects`, into `<project>.vision.json`), and
   `subjects --clip <id> --reframe` writes Motion scale and position keyframes that follow the main face in the
   sequence's shape. Without the plugin, read the subject's place off the frames. Check the result either way.
2. **Auto Reframe** (`effects.apply`) when one subject moves through the shot and the frames show it stays
   inside the new shape; check the result at the same frames.
3. **Fixed crop when what matters fits**: Motion scale and position, locked for the shot ("don't move unless you
   must", hotclip; T19 §2). Leave 0.3-0.5 of the face size around a face, more for a gesturing presenter
   (openmontage, hotclip). Keyframe position only when the subject really moves; no smooth drift on a talking head.
4. **Fall back to fit** when it does not fit (two people far apart, a wide landscape, a sign): `clip.fitToFrame`,
   then a blurred backdrop (the clip again on a lower track, `clip.fillFrame`, `Gaussian Blur`), which suits
   screens, slides and photos, not footage with a subject (nateherkai; T19 §3). Order: fit, a fixed crop at a
   position you checked, the original shape. A centre crop without a frame check is the anti-pattern.

Zooms on a screen recording (one framing per narration line) and the presenter box: `<skill_dir>/REFERENCE.md`.

## 8. Text and stickers: In and Out

A caption, title or sticker that is not part of a video cut gets its own entrance and exit: Opacity and Motion
keyframes on the graphic clip (entrance 0.2-0.6 s, exit shorter; talkcraft), or a `.fcgt` template with built-in
animation (`graphics.template.apply`; `graphics.setResponsiveTime` keeps intro and outro intact when the clip is
trimmed). Building the text itself: bcp:captions-text, bcp:motion-graphics.

## 9. Apply in one batch

`bashcut.batch {commands: [{id, params}], label}` runs steps in order as one undo step; a failing step leaves the
project unchanged and names the step. Without it, `command_batch` with `stop_on_error` (each step its own undo step:
on a mistake undo step by step with `edit.undo` or fix forward). Ticks: 254 016 000 000 per second.
Example at 30 fps: a 15-frame Cross Dissolve out of clip 12, and a Ken Burns drift on clip 13 (8 s, 100 to 104 %)
starting at 40 s:

```json
{"label": "Dissolve and drift", "commands": [
  {"id": "sequence.applyVideoTransition", "params": {"clip": 12, "effect": "Cross Dissolve", "frames": 15, "edge": "out"}},
  {"id": "effects.setParam", "params": {"clip": 13, "effect": "motion", "param": "scale", "value": 100, "time": 10160640000000, "keyframe": true}},
  {"id": "effects.setParam", "params": {"clip": 13, "effect": "motion", "param": "scale", "value": 104, "time": 12192768000000, "keyframe": true}}
]}
```

Take the clip ids (numbers) from `bashcut.timeline.summary` and the parameter names from `effects.list {"detail":
true}` (spelling as printed); then set interpolation with `effects.setInterpolation` (`linear` for this drift). If a
step is refused, `command_list {"filter": "<id>"}` shows its params.

## Not possible yet: say so and offer the alternative

Typewriter text and counting numbers outside a template, beat detection, AI-generated transitions. (Text behind
a person and face detection need the `bashcut.vision` plugin: `cutout` puts the person on the track above, the text
goes between.) Note it as a feature request (BashCutPro or a plugin); never
fake it with a pre-rendered file without telling the user.

## Verify

`bashcut.timeline.summary` and `sequence_inspect` again: the runs you meant to break are gone, the rest are motifs
you can name, the new effects sit on the clips you meant. Look before, inside and after each effect with
`render_frame` (first, middle and last frame of a move); `render_preview` only across a transition or ramp, 1–2 s of
it, never the whole edit. After a reframe, what matters is still in frame. Ask the user to listen to the sound.

Then, on **every output sequence** (`sequence.open {item}`): `bashcut.review.run {profile: "<its output
profile>"}`. Blocking findings (black frames inside the edit, clips or gaps under 3 frames, a cut inside a word)
are fixed and the review run again, at most 3 rounds; `frozen` warnings on a still you meant are fixed with motion
(§3) or kept with a reason. What is left after round 3 goes to the user. The full review: bcp:review.
