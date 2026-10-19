# Effects reference

Detail for the `effects` skill. Durations in seconds; frames = seconds x the sequence fps. Ticks: 254 016 000 000
per second. Effect and transition names are exactly the ones FilmCraft's catalogue shows; anything else is found
with `effects.list` at run time, never guessed.

## Genre: what fits

| Genre | Fits |
|---|---|
| Food / travel | whip, cut on action, place cards, pop stickers, speed ramp on food action, build-up then reveal |
| Review / ads | freeze + label, price as a keyword sticker, reverse-into-hand hook, crash-zoom on the product |
| Talking head | jump cuts with punch-in, keyword stickers, In/Out on captions and stickers, few transitions |
| Explainer / cards | slide or card turn between full-frame cards; an iris-like reveal to open a title card |
| Real estate | slow speed, keyword stickers for price and area |
| Event / MV, hype | beat cuts, flash, blink, crash-zoom, glitch, flicker, speed ramps |
| Cinematic, documentary | hard cuts, 0-1 special transitions a minute, slow drift at most |

## Transition lengths and sources

| Kind | Length | Source |
|---|---|---|
| Whip | 0.2-0.4 s; 1-2 per short; same direction on both sides, never back and forth in a row | assafkip, saas-motion-kit |
| Dissolve, dip to black | 0.3-1.0 s; bookend fades and chapter dips 0.5-1.0 s | openmontage |
| Blink, shutter, zoom, spin, wipe (slide, barn door, roll, crash) | quick 0.2-0.5 s, standard 0.7-1.5 s | digitalsamba (two tables in one repo disagree) |
| Swing, arc (next card turns in about an edge) | about 0.3 s between full-frame cards of an explainer; never between footage shots | Reelcrew study (30 videos, 2026-10-07) |
| Glitch (RGB split), halftone, other stylized | glitch 0.2-0.4 s, halftone 0.4-0.8 s; hype, showreel and comic edits only, about every 2.7 s at most | Reelcrew study |
| Text or sticker In / Out | entrance 0.2-0.6 s, exit shorter | talkcraft |
| Impact (slam, flash, crash-zoom) | 0.10-0.25 s after its target is fully visible | assafkip |

## BashCut kind to FilmCraft

"Look up" means: `effects.list {"kind": "VideoTransition"}` once (112 names; `"folder": "Video Transitions/Wipe"`
for the wipes), pick the entry whose name says that move, apply it with `sequence.applyVideoTransition`. Use the
fallback recipe when the list has nothing that fits, and say which one you used.

| BashCut kind or effect | FilmCraft name or recipe |
|---|---|
| `dissolve` | `Cross Dissolve` (`cross_dissolve`), 0.3-1.0 s |
| `dip-black` | look up a dip; fallback: Opacity keys 100 to 0 over the out clip's last frames and 0 to 100 over the in clip's first, nothing underneath (black) |
| `flash` (to white), `blink` | look up; fallback: `file.newColorMatte {"color": "#ffffff", "seconds"}` above the cut for 2-6 frames, Opacity keys up and down (blink: the same Opacity dip to black, 2-4 frames each side) |
| `double-exposure` | a long `Cross Dissolve` (1-2 s); or the next clip on a track above, overlapping, Opacity 40-60 % |
| `whip`, `whip-right`, `whip-up`, `whip-down` | look up (slide or push family); fallback: Motion position keys moving the frame off-screen over 4-8 frames each side, `Gaussian Blur` keyed up to the cut and down after |
| `wipe`, `wipe-right`, `wipe-up`, `wipe-down`, `barn-door`, `shutter`, `slide`, `slide-up` | `effects.list {"kind": "VideoTransition", "folder": "Video Transitions/Wipe"}`; direction with `params` (from `detail: true`) or `reverse` |
| `iris`, `diamond` | look up a shape transition; fallback: `masks.add {"shape": "ellipse"}` on the in clip, mask size keyed from 0 to beyond the frame with `masks.set` |
| `zoom`, `crash-zoom`, `crash-out` | look up; fallback: Motion scale keys 100 to 130 % over the out clip's last 3-6 frames (crash-out: 130 to 100 on the in clip's first), `Gaussian Blur` keyed with it |
| `spin`, `roll`, `roll-right` | look up; fallback: Motion rotation keys (90-360 degrees) with scale up 110-120 % to hide the corners |
| `swing`, `arc`, `arc-right` | look up; fallback: a Wipe-folder slide, or a hard cut between the cards |
| `infinite-zoom`, `infinite-out` | look up; fallback: the crash-zoom recipe with a larger scale (200 %+) over 0.5-1 s, eased in |
| `screen-in`, `screen-out` | Motion scale and position keys onto the device's screen (read its rectangle on `render_frame`), then a hard cut |
| `blur`, `seamless-zoom` | `Cross Dissolve` with `Gaussian Blur` keyed to a peak at the cut on both clips; seamless-zoom adds the crash-zoom scale keys |
| `glitch`, `color-shift` | `RGB Split` on both sides of the cut (split the clip edge with a razor if needed), keyed on then off over 0.2-0.4 s |
| `halftone`, `kaleidoscope` | look up in `effects.list {"kind": "Video"}`; none listed: use the glitch recipe or a hard cut, and say so |
| `flicker` | Opacity keys alternating with `hold` interpolation over 4-8 frames; or `Light Leaks` for a warm burst |
| shake (BashCut: not possible) | `Camera Shake` effect |
| covering a logo or burned-in text | `masks.add` + `masks.track` on a `Gaussian Blur` or `Mosaic` copy |
| black-and-white moment | `file.newAdjustmentLayer` over the range + `Lumetri Color` with saturation at 0 |
| sound crossfade | `sequence.applyAudioTransition` `Constant Power`; `constant_gain` or `exponential_fade` exist as defaults (`effects.setDefaultTransition`) |

## Recipes

**Keyframes.** `effects.setParam {"clip", "effect": "motion"|index, "param", "value", "time": ticks, "keyframe":
true}` writes a key at a timeline time; a second call on the same param adds the next key. Then
`effects.setInterpolation {"clip", "effect", "param", "mediaTime", "interpolation"}` per key (`easeOut` on
entrances, `easeIn` on exits, `linear` for a constant drift, `hold` for a step). `effects.setKeyframe` sets
`inInfluence` / `outInfluence` for a sharper ease. Read keys back from `sequence_inspect`; their `mediaTime` is
what the key commands take.

**Index of a new effect.** `effects.apply` inserts the new effect before Motion, Opacity and Time Remapping.
Read the clip's effect list, apply, read again; the new entry's position is its index. Applying to several clips
at once: read each clip's list, since earlier effects differ per clip.

**Ken Burns.** Two Motion scale keys at the clip's start and end (rate from the skill's table; 0.5 %/s over 8 s:
100 to 104 %), optionally position keys a few pixels the other way; alternate direction on the next shot;
`linear`.

**Punch-in on a word.** Razor the clip at the word (`timeline.razor`), set the second piece's Motion scale to
110-115 % (static, no keyframe), position kept on the face. Check headroom first.

**Speed ramp.** On the clip's `Time Remapping` effect, key the speed: normal, then a fast or slow stretch, then
normal, each change eased over 4-10 frames. A constant speed is simpler with `clip.speedDuration`.

**Freeze + label.** `clip.insertFrameHoldSegment {"clip", "time", "seconds": 1.5-3}` at the frame, then the label
on a track above (bcp:captions-text). A hold of the whole clip: `clip.frameHold`; options in
`clip.frameHoldOptions`.

**Blurred backdrop for vertical.** Place the clip again on the track below (`timeline.place`), `clip.fillFrame`
on the lower copy plus `Gaussian Blur`, `clip.fitToFrame` on the upper one.

## Zooms on a screen recording

One framing per narration line, aimed at the panel that line names, changing when the screen changes. One
tutorial reused a single framing (zoom 1.9, one fixed offset) on every screen shot: each sentence named a
different panel and the zoom showed none of them.

1. **Where the screen changes**: `clip.sceneEditDetection {"generateMarkers": true, "applyCuts": false}` on the
   recording, then `render_frame` around each marker. A new page, dialog or menu inside a line starts a new
   framing there.
2. **What each line names**: the line's words (`transcript.inspect`, or `transcript.search` for its key word)
   and the frame under the key word; read the panel's rectangle in the recording's pixels.
3. **Build**: razor at line edges, then per piece Motion scale and position so that rectangle fills the frame;
   out to the full screen between steps. A move inside one line: two keyed framings, eased.
4. **Check every framing** with `render_frame` at the line's key word: the named panel fills the frame and its
   text reads, no neighbouring window. Two lines in a row with the same transform on different screens is a miss
   unless they name the same panel. One example: at zoom 1.9 a 1920 px recording showed 1010 px and a
   neighbouring window crept in; 2.6 isolated the panel.

## Presenter box over a screen recording

`Crop` on the camera clip (left, right, top, bottom as its parameters list them), or `masks.add {"shape":
"ellipse"}` for a circle; then Motion scale and position to size and place it: 0.25-0.6 of the width, smaller
when the screen text is dense, larger when the face carries the story (T19 §3). The visible part keeps its place
in the picture: an uneven crop (left 28 %, right 0) left the face off-centre until position moved it back by
(left - right) / 2 x frame width x scale.
