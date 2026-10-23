# Motion graphics reference

## Template cards

`time` is ticks (254 016 000 000 per second); `seconds` is a length. Positions are pixels of the sequence frame: a
rectangle's `position` is its **centre** (the plate below spans x 120–960, y 1320–1620), a point text's is its first
baseline.

**Build the first card** (a stat card: plate, number, label): make the plate, read its `clip` from the result, then
one `command_batch` that adds the layers to that clip (`<clip>` below):

```json
{"id": "graphics.newRectangle", "params": {"position": [540, 1470], "size": [840, 300], "seconds": 4,
  "time": 3048192000000, "track": 2}}
```

```json
[
  {"id": "graphics.newText", "params": {"clip": <clip>, "text": "11,2 ha", "position": [170, 1450], "size": 140,
    "font": "Be Vietnam Pro", "fontStyle": "Black"}},
  {"id": "graphics.newText", "params": {"clip": <clip>, "text": "Hồ Gươm · mặt hồ", "position": [170, 1550], "size": 56,
    "font": "Be Vietnam Pro"}},
  {"id": "graphics.set", "params": {"clip": <clip>, "layer": 0, "props": {"fill_color": "#111111", "opacity": 85}}},
  {"id": "graphics.setCharStyle", "params": {"clip": <clip>, "layer": 1, "start": 5, "style": {"color": "#ffcc00"}}},
  {"id": "graphics.setResponsiveTime", "params": {"clip": <clip>, "introSeconds": 0.4, "outroSeconds": 0.3}}
]
```

`newText` with `clip` adds a layer to that graphic (result `{"clip": <clip>, "layer": 1}`); without `clip` it starts
a new graphic clip of its own, so the card falls apart into three clips.
Check it at phone size (`render_frame {seconds, max_side: 390}`) before keeping it: the template copies its mistakes into every card.

**Keep it** with one control per field that changes. Name controls by what they mean, not by layer:

```json
{"id": "graphics.template.export", "params": {"clip": "<clip id>", "name": "Stat card", "category": "My Templates",
  "description": "Number and label on a dark plate", "controls": [
    {"layer": 1, "param": "text", "name": "Number", "kind": "text"},
    {"layer": 2, "param": "text", "name": "Label", "kind": "text"},
    {"layer": 1, "param": "fill_color", "name": "Accent", "kind": "color"}]}}
```

`embedFonts: true` (with `fontLicense`) only when the font's licence allows it and the template leaves this machine.

**Every later card**: one `graphics.template.apply` per card in one `command_batch`, `time` = (W − E) in ticks:

```json
[
  {"id": "graphics.template.apply", "params": {"template": "Stat card", "values": {"Number": "1,54 km",
    "Label": "Một vòng hồ"}, "time": 5334336000000, "track": 2}},
  {"id": "graphics.template.apply", "params": {"template": "Stat card", "values": {"Number": "1428",
    "Label": "Năm dời đô"}, "time": 9906624000000, "track": 2}}
]
```

Then set each card's length to its hold (trim its out point, bcp:effects); responsive time keeps the entrance and
exit. A changed field later: `graphics.template.set {clip, values}`; what a placed card exposes:
`graphics.template.controls {clip}`. A preview image for the library: `graphics.template.thumbnail`.

What a template is for: a fixed layout with changing words and colours, entrance and exit by keyframes. What it
is not for: a number that counts, a bar that grows, a chart, a map, a diagram that builds, kinetic type word by
word. Those are plugin renders.

## Graphics brief

A brief for a sub-agent that designs, renders and places a video's graphics so the editor never reads a graphics
skill, a composition or a render log. Paste it with: the kit's skills folder `K`, the project (`.fcproj` or the
bridge address), the rows to build (`plan.visuals` rows with line, `at` word and `show`), the facts and numbers,
the look and whether the voice is final.

1. Read what you need, once, and nothing else: timing (`sed -n '/^## 3\./,/^## 4\./p;/^## 6\./,/^## Report/p'
   K/motion-graphics/SKILL.md`), the plugin (`HF check`; not ready and `HF setup` cannot fix it: stop and say
   why), its skill's command section and the widgets (`HF examples`; `HF examples NAME` for the variables of the
   ones you use). Never read the plugin's `lib/` scripts or an example's HTML to learn a variable. The rows: from
   the project notes (`project.notes`), once.
2. Take data from the plugin's tools (`HF osm-map` for places, routes and areas) and the facts table; never work
   it out. Fill widgets with `--set`; give the series one look with the same `--brand brand.json` on every call:
   the project's colours and fonts, else the same `accent`, `background`, `text`, `headingFont`, `bodyFont`. No
   credit, source or licence line on the picture unless the user asks. Write HTML (read the plugin skill's
   composition rules first) only for what no variable can draw.
3. Word times: `transcript.search {query}` per payoff word; the graphic starts at W − E; a time inside the
   graphic (`at`) is seconds from its start. One graphic per call, in time order:
   ```sh
   HF place stat-counter --seconds 41.3 --track V2 --draft --brand brand.json \
     --set label="Hồ Gươm · mặt hồ" --set to=11.2 --set decimals=1 --set locale=vi-VN --set unit=" ha" \
     --set at=0.4 --project video.fcproj
   ```
   **Short graphics, never one long one.** Over ~10 s or more than one section: one graphic per section (or group
   of 2–3 voice lines), so a fix re-renders seconds, not the video.
   **Look before you render.** `--snapshot 0.4,1.2,3` (seconds from the graphic's start) gives the same
   composition, values and brand as PNGs in seconds, nothing placed. Tweak with snapshots until the frames in
   step 4 are right, then render once.
4. Look and fix before you return (the editor sends no rounds back and does not look for you). Snapshot every
   graphic at its checkpoints: the first second (never an empty stage), each element's landing word, the payoff,
   the last second. Check each: readable at phone size, on its word, inside the safe area and clear of the caption
   band, on-style, nothing crowding a label. After placing, `render_frame {seconds, max_side: 390}` on each
   landing frame against the real picture under it. A fix: `HF rerender <record> --set …`. At most two full
   renders per graphic.

Answer in under 200 words, nothing else: per graphic, its record path, clip, span (seconds) and the word it lands
on; renders and snapshot calls used; problems left; what you changed against the editor's rows and why; what you
could not check (motion between frames).

## Not ported from BashCut

BashCut's `plan.cut.graphics` rows built by one `graphic plan` call, `@words` times, frame chrome (`backdrop`,
`chip`, `callout`, `float`) and `bashcut timeline sheet` have no BashCutPro command: word times come from
`transcript.search`, each graphic is one `HF place`, and the look comes from `--brand` and widget variables.
