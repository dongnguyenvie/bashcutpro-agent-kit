# stock-images reference

## How the scripts run

`fetch_*.py` here are thin launchers: they find the `bashcut.resources` plugin and run
`plugin.py fetch --script <name> --args <json list>`. The plugin runs BashCut's scripts unchanged and answers their
BashCut-only calls itself (see the plugin's README, "How the scripts run here"):

| The script would call | Here |
|---|---|
| `library add` (a pick, a logo, an emoji) | the file stays in `--dest`; its licence goes to `<file>.licence.json` |
| `library place … --at-frame N --duration N` | reported as `pending` `{file, frame, duration}`: place it with `timeline.place` |
| `--import` (`media import DIR`) | reported only; import with `media_import` yourself |
| the project's illustration set and palette | kept by the plugin (one set per project still holds) |

Where the plugin is looked for: `$BASHCUTPRO_RESOURCES_DIR`, `<FilmCraft data dir>/bashcut-plugins/bashcut.resources`,
then a `bashcutpro-plugins/plugins/resources` checkout in this kit's or the working folder's parents. The scripts'
indexes and downloads are kept in the plugin's data folder (`shared/`, `cache/`).

The summary line after the script's own lines:

```json
{"files": [{"path": "/abs/media/stock/wikimedia-41936.jpg", "license": "CC BY-SA 4.0", "author": "…",
            "source": "https://commons.wikimedia.org/wiki/File:…", "record": "/abs/media/stock/wikimedia-41936.jpg.licence.json"}],
 "pending": [{"file": "/abs/media/stock/pot-3.jpg", "frame": 120, "duration": 90}]}
```

## Sources and keys

| Source (`--source`) | What | Key | Licence |
|---|---|---|---|
| `pexels` | photos and video, vertical video, Vietnamese queries work | `PEXELS_API_KEY` (pexels.com/api) | Pexels licence |
| `pixabay` | photos and video | `PIXABAY_API_KEY` (pixabay.com/api/docs) | Pixabay content licence; cache, never hotlink |
| `free` | Wikimedia Commons + Openverse photos | none | per file (CC0, CC BY, CC BY-SA; some NonCommercial: check) |
| `nasa` | space and science photos and video | none | public domain (NASA media) |
| `archive` | Internet Archive photos and footage: newsreels, home movies; `--year 1960-1975`, `--public-domain` | none | per item |
| `documentary` | archive + Wikimedia + Openverse photos; video: archive | none | per item |

Keys come from the environment only. Never ask the user to paste a key into the chat.

## How many slots

Ranges that worked in BashCut edits (tune per video): up to 30 s, 4–8 slots × 6–8 candidates; 30–90 s, 8–16 × 6–10;
1.5–5 min, 16–40 × 6–10; longer, 6–10 slots a minute × 5–8. Cap video downloads at about 150 MB a minute of edit
(`--max-mb`).

## Placing details

- Ticks: 254 016 000 000 a second. `timeline.place` also takes `frame` (sequence frames) or `seconds`; `duration`
  is always ticks. A still's default length is the project's still length: pass `duration`.
- Several stills back to back on one track: `timeline.place {"items": [a, b, c], "track": "V2", "seconds": S}`
  (one undo step); then set each clip's length with `timeline.trim` if they differ.
- The clip ids come back as `{"clips": [id]}`; the Motion effect is `"effect": "motion"` with params `scale`
  (percent), `position` ([x, y] pixels), `rotation`, `anchor`. Keyframes: `keyframe: true` with `time` in ticks;
  ease with `effects.setInterpolation`.
- A picture card (zoom under 100 %) over the footage: scale 40–70, a `graphics.newRectangle` behind it for a plate
  if the picture's edges fight the footage.

## Iconify recipe

Iconify: 200k+ vector icons, free API, no key, ~0.2 s per call (tested October 2026):

```sh
curl -s "https://api.iconify.design/search?query=cash&limit=20"           # icons ["mdi:cash", "solar:wallet-bold", …]
curl -s "https://api.iconify.design/collections?prefixes=mdi,solar"       # each set's licence
curl -s -o cash.svg "https://api.iconify.design/mdi/cash.svg?color=%23FFD400&height=512"
rsvg-convert -w 512 -h 512 cash.svg -o cash.png    # or: magick -background none -density 1536 cash.svg -resize 512x512 cash.png
```

- Import PNG, not SVG. Never convert with `qlmanage`: it paints a white background.
- Prefer filled sets (`solid`, `fill`, `bold`; `fluent-emoji-flat` for colour emoji): thin outlines vanish on a phone.
  `?color=` recolours one-colour icons only.
- Save under `media/stock/icons/` with a licence record of your own if you want credits later
  (`{"file", "license", "author", "source"}` as `<file>.licence.json`).

## What BashCut had that is not here

- The library (search, tags, `library place`): files stay in the project's media folders.
- `library generate` (AI B-roll) and `image.generate`: the image-gen plugin and `bcp:visual-plan`.
- `project credits`: `resources.py credits <folder>`, written where the user wants them.
