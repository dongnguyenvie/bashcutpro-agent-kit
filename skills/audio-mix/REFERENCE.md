# audio-mix reference

## Finding music and SFX online

Policy (decided in BashCut): download what fits and record nothing: the user handles rights. Dead ends: Bensound,
BBC SFX, ProductionCrate.

| Source | How | Licence |
|---|---|---|
| **Freesound API** (SFX) | `FREESOUND_API_KEY` (free, freesound.org/apiv2/apply), through `fetch_audio.py` | CC0 taken first, then CC BY (credit line); NonCommercial never |
| **Openverse API** (Jamendo, ccMixter, Freesound, Wikimedia) | `curl`, no key, searchable, gives licence and duration | per file: CC0 free; CC BY needs the credit line |
| **Pixabay Music / Sound Effects** | no API, blocks `curl`: a browser on `pixabay.com/music/search/<q>/` or `/sound-effects/search/<q>/` (Vietnamese under `/vi/`), else Mixkit or Openverse | Pixabay Content License: commercial use, no credit; some tracks are registered in Content ID, so keep the page URL as proof |
| **Mixkit** (music and SFX) | no API: the file URL on `mixkit.co/free-stock-music/tag/<lo-fi\|chill\|upbeat\|cinematic>/` or `/free-sound-effects/<whoosh\|pop\|ding\|click>/` | Mixkit free licences: commercial use, no credit; not resold or shared as stand-alone sound |
| **tiengdong.com** (Vietnamese meme sounds: "ting ting", "bụp bụp", "oh nooo") | download the one that fits | "All rights reserved", many clipped from shows: organic posts only, never ads or monetised YouTube |

### `fetch_audio.py`

Carried over unchanged from BashCut's Online Resources plugin, with `fetch_stock.py` (its download helper:
`curl` with retries). Standard library and `curl`; runs with `python3` or `uv run`.

```sh
python3 "<skill_dir>/fetch_audio.py" --dest /abs/project/media/audio --music "lofi chill" --sfx whoosh,pop --no-library
python3 "<skill_dir>/fetch_audio.py" --dest /abs/project/media/audio --slots slots.json --no-library --max-mb 150
```

Music comes from Openverse; SFX from Freesound with a key, else Mixkit, else Openverse. It prints one JSON line per
file (`--slots`: a table and `candidates.json`). Then bring them in with `file.import {paths}` (or MCP
`media_import`) and place them with `timeline.place`.

Always pass `--no-library`, and never `--import` or `--pick`: those call the `bashcut` CLI (BashCut's library,
media import and placing), which does not exist here. Without the library there is no LUFS, onset or BPM column:
measure the candidates you consider with `loudness.py` (convert a non-WAV file to WAV first, or place it alone and
export that range) and `bcp:beat-cut`'s `beats.py`.

- **Fetch more than you need, choose by numbers.** `--slots slots.json` (`[{"slot": "cut-whoosh", "sfx":
  "whoosh", "count": 10}, {"slot": "bed", "music": "lofi chill", "count": 6}]`). Ranges (tune; SFX slots from the
  plan's cuts, transitions, graphic entrances, keyword pops): ≤ 30 s 4–8 kinds × 6–10, 1 bed × 4–6; 30–90 s 8–15 ×
  8–12, 1–2 × 5–8; 1.5–5 min 15–30 × 8–12, 2–4 × 5–8; cap ~150 MB a minute (`--max-mb`).
- **Openverse** by hand: `curl "https://api.openverse.org/v1/audio/?q=lofi&license=cc0,by&category=music"` (SFX:
  drop `category`; `duration` in ms). Freesound's CDN is slow (~12 s a MB); the script fetches in parallel.
- Good keywords: "lofi chill", "upbeat corporate", "cinematic ambient", "meme". Download into the project's
  `media/audio/`; nothing goes on the video or in its description unless the user asks.

## `loudness.py`

ITU-R BS.1770 / EBU R128 on a WAV file, read-only, standard library. Output fields: `integratedLufs` (gated),
`lraLu`, `samplePeakDbfs`, `truePeakDbtp` (4x oversampled estimate), `maxMomentaryLufs`, `maxShortTermLufs`,
`silences` (momentary under `--silence-lufs`, default −50, for `--min-silence` s), `windows` (with `--speech` or
`--windows`: median momentary loudness inside and outside the speech windows), `shortTerm` (with `--curve`).
Times are on the WAV's clock: an export with `startSeconds: S` puts timeline second S at 0, so pass `--from` and
`--to` on the file's clock, or export the exact range.

## Real speech vs voiceover

Required whenever both are in the edit:

1. Export the voiceover stem and each live-speech stem (or range) as WAV; `loudness.py` each.
2. Per live-speech clip, read its true peak first: the gain you can add is the ceiling (−1 dBTP) minus that peak.
   One +12 dB raise put a clip at +5 dBTP.
3. Set each clip's gain (`clip.audioGain`) to bring it within ~2 LU of the voiceover; where its peaks cap the gain,
   raise to the cap and pull its loudest words down with a volume keyframe (`clipMixer.set`), or lower the
   voiceover to meet it.
4. Set the bed 15–20 LU under the quieter of the two voices: a bed fitted to the voiceover sat only 0–4 LU under a
   quiet presenter.
5. Measure again: every speech window within ~2 LU, the bed's `insideMedianLufs` at least 15 LU under the voice in
   camera windows too, and no true peak over the ceiling on the mix. Report the numbers.
