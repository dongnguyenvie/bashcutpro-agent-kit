# color-grade reference: `grade.py` and `looks.json`

Both are carried over unchanged from bashcut-agent-kit. `grade.py` reads source video files with ffmpeg (needs
`ffmpeg` and `ffprobe` on `PATH`) and runs with [uv](https://docs.astral.sh/uv/), which installs numpy and Pillow
on first run. It never touches the project: you import what it writes.

```sh
G="<skill_dir>/grade.py"        # the folder SKILL.md is in
uv run "$G" looks                                          # the looks in looks.json
uv run "$G" measure /abs/clip.mp4 [--n 12] [--json]        # black/white point, saturation, tint per luma band
uv run "$G" match /abs/clip.mp4 matte-cinematic [--exposure S] [--wb R,G,B]   # JSON report, writes nothing
uv run "$G" lut matte-cinematic [--exposure S] [--wb R,G,B] -o /abs/project/luts-src/matte.cube
uv run "$G" preview /abs/clip.mp4 /abs/project/luts-src/matte.cube -o /abs/tmp/prev.jpg [--n 6]
```

Source paths: `project.items` (or `doc_inspect`) lists each media item's file. The scale is 0–100, the same as the
ranges in SKILL.md.

## Fitting a generated look

`match` reports the footage through the look against the look's `ref` and `range` in `looks.json` (`outside`: 0
inside, − below, + above, null with no range; each range has its `why`); it corrects nothing. You decide the
exposure (stops added to the look's) and white balance (R,G,B multipliers on the look's), try them with `match`
again, then write the LUT with `lut`. Leave the white balance alone on scenes meant to be coloured (sunset, neon,
screen recordings, graphics): the reference tint is the look's, not the scene's.

`match` and `preview` run on the source file only; the real check is BashCutPro's composite (`scopes.read`,
`render_frame`, SKILL.md step 4). Never read a `.cube` body; judge a LUT by its frames. Your own look: a params JSON
(keys in `grade.py -h`: exposure, wb, lift / gamma / gain, black, white, contrast, pivot, sat, sat_shadow,
sat_high, split, hue_shifts, skin_protect, fade) in place of a look name.

Then into the edit:

```json
{"id": "lut.import", "params": {"path": "/abs/project/luts-src/matte.cube", "name": "Matte"}}
{"id": "lumetri.setLook", "params": {"clip": "<adjustment clip>", "lut": "lib:<id from lut.import>"}}
```

## Not carried over

`grade.py candidates` (rank a LUT library, one numbered sheet, `--pick`) calls the `bashcut` CLI and BashCut's
Online Resources plugin (`fetch_luts.py`); neither exists for BashCutPro. Use `lumetri.presetThumbnails` and
`lut.list` for the candidate sheet instead (SKILL.md step 3). The docstring's `bashcut luts import` means
`lut.import` here.
