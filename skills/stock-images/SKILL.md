---
name: stock-images
description: Find and place pictures the footage lacks in a BashCutPro edit: stock photos and video (Wikimedia, Openverse, NASA, Internet Archive; Pixabay and Pexels with a key), animated emoji, brand logos, Iconify icons, illustration sets in one style, each file's licence recorded next to it; placed with media_import, timeline.place and Motion keyframes. Triggers: "ảnh minh hoạ", "video minh hoạ", "ảnh stock", "pexels", "lấy ảnh trên mạng", "icon", "emoji", "logo", "b-roll", "stock photo".
---

# Stock photos, video, emoji, logos and illustrations

The fetch scripts next to this skill (`fetch_stock.py`, `fetch_emoji.py`, `fetch_logos.py`,
`fetch_illustrations.py`) run BashCut's scripts through the `bashcut.resources` plugin of bashcutpro-plugins: same
flags (`--help`), same output lines, then one summary line with `files` (each saved file, its licence, author,
source and the `<file>.licence.json` record beside it) and `pending` (picks to place). Run them with
`python3 <skill_dir>/fetch_stock.py …` (`py -3` on Windows). No plugin found: they say how to get it. Contact
sheets need Pillow: the plugin's `setup` installs it once (ask first, about 65 MB). Sources, keys, slot sizing and
the Iconify recipe: `<skill_dir>/REFERENCE.md`.

## 0. What the project already has

`project.items {"recursive": true}` lists imported media; the project's `media/stock`, `media/emoji`,
`media/logos`, `media/illustrations` folders hold earlier downloads with their records. Reuse before fetching.

## 1. Search

- **All stock rows at once** (the plan's visuals that need stock): `slots.json` `[{"slot": "pot", "query": "clay
  pot", "kind": "photo", "orientation": "portrait", "count": 8}, …]`, then `fetch_stock.py --slots slots.json
  --dest <project dir>/media/stock --max-mb <cap>` downloads every candidate and draws numbered sheets. Look at each
  sheet once, then `--pick "pot=3@120;river=2@300:90"`: candidate n for timeline frame 120 (:length in frames).
- **One lookup**: `fetch_stock.py --query "clay pot" --orientation portrait` prints candidates with their
  previews; `--ids <id>,<id> --dest <dir>` downloads the chosen ones.
- **Sources** (`--source`; default the first with a key, else `free`): `pexels`, `pixabay` (keys `PEXELS_API_KEY`,
  `PIXABAY_API_KEY`, environment only; the only vertical stock video), `free` (Wikimedia + Openverse photos, licence
  per file), `nasa` (public domain), `archive` (Internet Archive, by `--year`; slow, ~0.3 MB/s), `documentary`. No
  video key: say so and use stills with motion.

## 2. Bring in and place

Picks print as `pending` `{file, frame, duration?}`; downloads as `files`. Then, in one `command_batch` where the
ids are known:

1. `bashcut.media.import {"paths": [<absolute files>]}` (runs the plugins' import hooks; else MCP `media_import`)
   → the new item ids.
2. **Stills and overlays** on a track above the footage: `timeline.place {"item", "track": "V2", "frame": F,
   "duration": <ticks>}` (254 016 000 000 ticks a second; `sequence.addTracks {"video": 1}` when V2 is missing).
   A still that does not move looks frozen (the review's `frozen` finding): two keyframes on Motion scale from its
   first frame to its last, a drift of 0.3–1.5 % a second (bcp:effects; e.g. `effects.setParam {"clip", "effect":
   "motion", "param": "scale", "value": 100, "keyframe": true, "time": <start>}` then `102` at the end of a 4 s
   still);
   alternate push-in and pull-out between neighbours; a card is smaller (scale 40–70) with `position` set.
3. **Stock video replacing a moment** on V1: `timeline.place {"item", "track": "V1", "seconds": S, "sourceIn",
   "duration", "audio": false}`. `audio: false` keeps the original sound; without it the stock's sound overwrites
   A1 too. Over the footage instead: V2.
4. Put the import, places and keyframes of all pictures in one `bashcut.batch {commands}` (one undo step) once the
   item ids are known.
5. Look at the frames with `render_frame {"seconds"}` (the first and last frame of each picture) before going on.
6. On **every output sequence** (`sequence.open {item}`): `bashcut.review.run {profile: "<its output profile>",
   checks: ["picture", "edit"]}`. Fix a `frozen` still with motion, a gap or clip under 3 frames, and run it again,
   at most 3 rounds.

Never place a Pixabay URL: download first (Pixabay asks that files are cached, not hotlinked).

## 3. Credits and licences

- Every file the scripts saved has `<file>.licence.json`. A file with no licence (shown without one in `files`):
  check it before the video is published, or drop it.
- **No credits on the video** or in its description unless the user asks. Then:
  `python3 <skill_dir>/resources.py credits <folder>` prints the credit lines; put them in the description, an end
  card (`bcp:captions-text`), or the project notes with `project.setNotes` (it replaces the whole text: read
  `project.notes` first and keep it).

## 4. Rules

- **No labels on the picture.** Never write "minh hoạ", "stock", "AI", a source or a licence on the video: it
  makes the cut feel unnatural. Real footage stays the main picture; stock reads as illustration by context (over
  or between real shots, tied to the words). Never present stock as the real place in narration or titles.
- Tie each picture to its words ("nồi đất" → clay pot); 1.4–2 s each, a soft pop sound (`bcp:audio-mix`).
- How many: the plan's stock and icon rows; without a plan, 2–3 per video at most. Always off faces. Avoid
  identifiable people.

## Emoji for keyword pops (Noto Animated, OpenMoji)

All pops in one call: `fetch_emoji.py --words "wow,money,fire,tiền" --dest <project dir>/media/emoji` draws one
sheet, a row per word (English or Vietnamese). One look, then `--pick "wow=1@120:30;money=2@300:30"`. Place each
like a still on V2, small (scale 25–40), on the payoff word, off faces, with a pop. Noto's are animated WebP; if
`media_import` refuses one or it plays still, pick the OpenMoji PNG (`--set openmoji`): FilmCraft plays animated
GIF and APNG.

## Brand and tool logos (Simple Icons)

`fetch_logos.py --brands "figma@120:90,notion@210:90" --dest <project dir>/media/logos --on dark` renders each in the
brand colour (white or black under 3:1 contrast) as a transparent PNG; a near miss prints close slugs: run again
with the slug. Logos are trademarks: only to name the product shown or reviewed, never to suggest sponsorship,
endorsement or partnership, never recoloured to the channel's palette or altered.

## Illustrations in one style (open sets)

For explainers and promos an open set beats generating: no cost, one style. Sets: `undraw` (~1,800 flat topic
scenes, one accent), `humaaans` (90 flat people), `open-peeps` (93 hand-drawn people), `open-doodles` (33 sketchy
scenes). One set per video, never mixed (the first `--set` is stored for the project).

`slots.txt` (`slot: words` lines), then `fetch_illustrations.py --slots slots.txt --dest <project
dir>/media/illustrations --set undraw --palette "#accent,#second"` draws numbered sheets. One look per sheet, then
`--pick "hook=1@0:90;idea=3@300:75"` renders transparent PNGs to place. Generate only what no set draws (a named
place, a product, a mascot): `bcp:visual-plan`.

## Icons (Iconify)

For a small idea (money, pin, clock, check) an icon reads better than a photo: the recipe is in REFERENCE.md.
512 px PNG, placed like a still, small (scale 25–40), with a pop.

## Free fallback: blurred own footage

For a background (a horizontal clip in a vertical frame, an info card): the same clip again on the track below,
`effects.setParam` Motion `scale` up to fill, `effects.apply {"effect": "Gaussian Blur"}` and a darker Lumetri
exposure until the subject reads; values depend on the picture, check with `render_frame`. Same colours, no
licence question (`bcp:effects` has the vertical-backdrop recipe).
