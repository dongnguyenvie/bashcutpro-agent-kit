---
name: library
description: Keeping a BashCutPro creator's reusable pieces in one library with the bashcut.library plugin: look there first (titles, lower thirds, looks, LUTs, effect presets, stickers, overlays, sounds, music beds, project templates, the brand kit), harvest what an edit made worth keeping, apply the brand kit, prune what is never used, and share packs. Triggers: "thư viện", "lưu lại để dùng sau", "dùng lại", "brand kit", "bộ nhận diện thương hiệu", "preset của tôi", "my library", "save this title", "reuse the look", "library pack".
---

# Library: grow it, harvest after an edit, prune

A creator's channel looks like itself because the same lower third, look, sting and caption style come back in
every video. The `bashcut.library` plugin (in `bashcutpro-plugins`, `plugins/library`; its own skill `library-plugin`
has every flag) keeps them in `<data dir>/bashcut/library/` with a purpose line, tags, licence, favourite and uses
per project, on top of what FilmCraft stores: `.fcgt` graphics templates, effect presets, LUTs and media exports.
`LB` = `python3 <plugin dir>/plugin.py` (`py -3 …` on Windows); `save`, `apply` and `brand apply` take
`--bridge 127.0.0.1:<port>` or `--project <file.fcproj>`. Every command prints one JSON object (`ok`, `message`,
`data` or `error`).

## 1. Look there first

At the plan stage (bcp:vlog-plan, bcp:edit-workflow), before any title, look, sting or music is made:

1. `LB brand show --id <kit>` when the creator has a brand kit (`LB search --kind brand-kit`): its fonts, colours
   and caption style are the defaults of this edit; write the kit id in the plan's `decisions`.
2. Per need, `LB search --query "<what it is for>" --kind <kind> --for-project <fcproj>`: favourites and the ones
   used in this project come first. Show the preview (`LB show`) and say which you would reuse and why.
3. Reuse beats remaking: apply with `LB apply --id <id>` (title at `--seconds` with `--values`, preset or look on
   `--clip`, sticker / sound / music placed on a track). The brand kit's parts: `LB brand apply --id <kit> --part
   lowerThird|logo|intro|outro|captionStyle` (the caption style goes through `captions.setStyle`).

## 2. Harvest after an edit

After the export gate (bcp:review passed), offer once, as a short list, what this edit made that is worth keeping;
save only what the user picks:

| Made in the edit | Save as | How |
|---|---|---|
| a title, lower third or card built with `graphics.*` | `title` / `text-style` | select it, `LB save --kind title` (`graphics.template.export`) |
| an effect stack tuned on a clip (punch-in, blur, glow) | `effect-preset` | `LB save --kind effect-preset --clip <id>` (`presets.save`, `presets.export`) |
| a look fitted for the creator (bcp:color-grade) | `look` | from the app's LUT library: `LB save --kind look --lut lib:<id>` (`lut.export`); a `.cube` file: `LB add --kind look --file` |
| a sting, whoosh or music bed cut to length | `sound` / `music` | `LB save --kind sound --start <s> --end <s>` (`file.exportMedia`, wav) |
| a sticker or overlay with alpha | `sticker` / `overlay` | `LB save --kind overlay --start <s> --end <s>` (ProRes 4444) |
| the project set up as a starting point | `template` | where the build has templates: a bundle with slots, `bashcut.template.save {"name", "slots": [footage, music bed, logo items]}` (kept in `<data dir>/bashcut/templates/`, listed by `bashcut.template.list`, reused with `bashcut.template.instantiate`); else a plain copy, `LB add --kind template --file <copy.fcproj>` |

Every item gets a purpose line ("lower third for guest names, two lines"), 2–5 tags (genre, mood, colour, the
channel), and its licence: "own" for what the creator made, the source's licence for fetched files (bcp:stock-images
records them), "unknown" said aloud otherwise. A brand kit is updated, not duplicated: `LB brand set --id <kit>
--lower-third <id>`.

Never harvest without asking, never save a stranger's face or voice as a reusable piece, never put API keys or
client material in a pack.

## 3. Prune

Every few edits, or when search returns too much: `LB stats`.

- `neverUsed` items older than a few months: propose removing them (`LB remove --id <id>`), one list, user's yes.
- Two items that do the same job: keep the one used more, remove the other.
- `noLicence`: fix the licence or remove before the item is used in a published video.
- Favourites (`LB favourite --id <id>`) are the creator's current style: keep them few, so they stay on top.

## 4. Packs

To move a library to another computer or share a style: `LB pack-export --tags <channel> --out <file.zip>`;
`LB pack-import --path <file.zip>` skips identical items and renames clashing ids (`data.renamed`). Say what a pack
contains and the licences in it before sharing it.
