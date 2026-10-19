---
name: audio-mix
description: Balance sound in a BashCutPro edit by measurement: voice levelled with Essential Sound auto match, a fixed music bed under the voice (ducking only for long silences), fades, volume keyframes, SFX at cuts, music retimed with remix, licensed music and SFX found with fetch_audio.py, loudness measured from WAV exports with loudness.py and set per output. Triggers: "trộn âm thanh", "cân âm lượng", "nhạc to quá", "thêm sfx", "tìm nhạc", "nhạc không bản quyền", "meme sound", "audio mix", "ducking", "loudness".
---

# Audio mix

You cannot listen: measure, change, measure again, and report the numbers. Lock the cut first (`bcp:beat-cut`).

## Commands

| Need | Command |
|---|---|
| Clip level | `clip.audioGain {clips, mode: "set" \| "adjust", db}`; `normalizeMax` for peaks |
| Volume over time (swell at a drop, dip for one line) | `clipMixer.set {clip, effect: "volume", param: "level", value, keyframe: true, time}` |
| Track level, mute, solo | `mixer.setStrip {strip: "A2", volumeDb, muted, solo}`; automation `mixer.setKeyframe` / `mixer.writeAutomation`; `mixer.inspect` reads it |
| Fades and joins | `sequence.applyAudioTransition {clip, effect: "constant_power", frames, edge: "in" \| "out"}` |
| Roles | `essentialSound.setType {clips, type: "dialogue" \| "music" \| "sfx" \| "ambience"}`; `essentialSound.inspect` |
| Voice to a loudness | `essentialSound.autoMatch {clips, target}` (dialogue clips): applies gain and reports the measured LUFS |
| Ducking | `essentialSound.set {clips: [music], key: "ducking.reduceDb", value}` (other `ducking.*` keys in `essentialSound.inspect`), then `essentialSound.generateDucking {clips: [music]}` writes volume keyframes under the dialogue |
| Music to a length | `clip.remix {clip, seconds}` (rebuilds the song at that length on its own phrase joins) |
| Peaks, sync | `clip.audioPeak {clips}`; a second camera by sound `clip.synchronize {method: "audio", clips, reference}` |
| Place a sound | `file.import {paths}` (or MCP `media_import`), `timeline.place {item, track: "A3", time}`; more tracks `sequence.addTracks {audio: 1}` |
| Final loudness | `file.exportMedia {loudnessLufs}` |

Clip ids and cut times: `sequence_inspect`. Times are ticks (254 016 000 000 per second) unless a param says
`seconds`. Many edits at once go in one `command_batch` (each step its own undo step).

## 1. Measure before fixing

`bashcut.audio.loudness {clip?, track?, range?: {start, end}, series?}` measures without changing anything: one clip,
a track's input (`track: "A1"`) or the whole mix (neither), integrated / short-term LUFS, LRA, true peak and clipped
samples; `series: true` adds short-term LUFS per second (times in seconds). Use it first. For silences, the bed under
the voice, or a build whose `command_list` lacks the id, export and measure outside:

```json
{"id": "file.exportMedia", "params": {"path": "/abs/tmp/mix.wav", "format": "wav", "wait": true,
 "range": "custom", "startSeconds": 0, "endSeconds": 60}}
```

```sh
python3 "<skill_dir>/loudness.py" /abs/tmp/mix.wav --curve      # integrated LUFS, LRA, true peak, silences
python3 "<skill_dir>/loudness.py" /abs/tmp/music.wav --speech /abs/tmp/voice.wav   # bed under the voice vs gaps
```

**Stems**: mute every track but the voice (`mixer.setStrip {muted: true}`), export `voice.wav`; the same for the
music, then unmute. Both over the same range, so `--speech` lines them up. Music under speech = the voice's
integrated LUFS − the music's `insideMedianLufs`. A single file (a music candidate, a take) is measured from its
own WAV, or exported alone. Change the **ratio** (bed level, duck depth, keyframes), never the master; measure
again after each change.

## 2. Levels: ranges and what moves them

| Stem | Range | Moves it |
|---|---|---|
| Voice (real speech or voiceover), per stem before the mix | −16 to −20 LUFS | Level each speaking clip first: cameras can differ by 15–20 dB. `essentialSound.autoMatch` does it per clip. |
| Real speech beside a voiceover | each live-speech clip within ~2 LU of the voiceover | One tutorial left the presenter's camera at −31 LUFS against a −17.5 LUFS voiceover: it sounded like another room. |
| Music under speech | 5–18 dB under the voice | Less when the music carries the piece (montage-like vlog, sparse speech); more for dense information, a soft voice, music with vocals or strong 1–4 kHz energy, accessibility. Sources: ~5 dB, with ~10 dB reported by viewers as "there is no music" (bestagentkits); 10–14 (reelmimic); 18–20 (openmontage). |
| Music under continuous voiceover | one fixed level 14–18 dB under the voice (default 16) | No level change between lines (owner's correction). |
| Music in speech gaps | short gaps (under 2.5 s) never rise; only a silence of 2.5 s or more (intro, montage break, outro) may rise toward voice level | Read the measured gaps, not the setting. |
| Duck timing (ducking on) | attack 5–200 ms, release 350–600 ms, hold 2.5 s | The hold keeps the bed down through gaps between lines. |
| Duck depth (ducking on) | 6–14 dB | Then check the measured ratio. |
| SFX, relative to the voice's peaks | subtle UI −16…−12, transitions −14…−8, impacts and memes −8…−3 dB | By role (ghost-editor). Files differ by 20 dB, so measure the file. |
| SFX density | 6–12 subtle per minute plus 1–3 memes (ghost-editor); none for a calm tutorial | Genre. Never the same sample twice in a row. |
| SFX sync | audible peak within 2 frames of its anchor | A correctness rule (guizang, shotcraft). |
| Joins, music tail | joins 10–40 ms fades; music tail 1–5 s | Tail by ending style. |

Seen in BashCut edits (not targets): SFX peaking near −21 dB were audible without covering words; a soft piano sat
under a calm male voice ducked 8 dB with nothing to fix.

**Fixed bed first**: one level from the measured voice, set with `clip.audioGain` on the music: voice LUFS − N −
the music file's LUFS at 0 dB (N from the range above). Ducking only when the edit has silences of 2.5 s or more
where the music should come up. Ducking that rises between closely spaced lines pumps: the bed comes and goes with
every line and sounds worse than a steady level. After `generateDucking`, measure `--speech` again: judge the
measured bed under speech, not the duck setting (a quiet take gets almost no ducking from the same setting).

## Two mixing styles

**Review / food / talking**: one structured song under everything at one fixed level near the deep end of the
range; a whoosh or pop on the hook's special transition; SFX matched to on-screen motion.

**Narrative / cinematic**: music is not a constant bed. Loud in montage (rising only in silences of 2.5 s or more),
down while information is spoken. No whoosh on ordinary cuts. SFX only with a reason (shutter on a photo cut, real
foley pushed up on a montage cut). Silence is a tool: drop the music 1.5–3 s before the punchline (razor the music
clip and fade out), leave the most honest line with no music. Keep the music continuous across section changes.

## Choosing music

- Prefer **one structured track** at least as long as the video (intro → build → drop → break) and align the
  drop with the hook's special moment. A flat loop measured as perfectly even was still judged boring. Too long or
  short: `clip.remix {seconds}` instead of a hard trim.
- Songs with a quiet intro dip ~11 dB every time they loop: trim the intro before repeating it.
- Put song changes and loop points **on a hard picture cut**: the eye takes the scene change and the ear ignores
  the join.
- Under a talking voice compare the candidates' `lraLu` and level (`loudness.py`): a calm piano at LRA 2 LU sat
  better than lofi at 5.3 under the same voice.
- Under speech use instrumental music; lyrics mask the words. Never use songs from a platform's library (TikTok
  and CapCut trending sounds): they are muted when posted on another platform or run as an ad.
- Never generate music. Finding and downloading it: REFERENCE.md (`fetch_audio.py`, sources and licences).

## Real speech, voiceover, screen recordings

- Never two voices at once. B-roll under voiceover often has people talking: razor at the voiceover's edges and
  mute only that piece (`clipMixer.set` level or a split clip); keep the original sound everywhere the voiceover is
  silent.
- Real speech and voiceover in one edit: match them (REFERENCE.md, "Real speech vs voiceover"): each live-speech
  clip within ~2 LU of the voiceover, the bed 15–20 LU under the quieter of the two, no true peak over −1 dBTP.
- Screen recordings: speech comes from the presenter's camera; mute the screen recording (it held the same voice
  2.5 s late via the room mic). To keep a demo's own output sound, place that output file at the measured sync
  offset (`clip.synchronize {method: "audio"}`), never the speaker leak.
- After the mix, report seconds of real speech vs voiceover.

## SFX

- Size the sound to the motion: soft whoosh for a slow move, short whoosh for a hard zoom, pop for stickers and
  labels, ding on a final number, hit on the shocking line. Never the same whoosh on every cut.
- A whoosh peaks on the cut; a riser ends on the reveal. Cut times from `sequence_inspect`; place every effect in
  one `command_batch` of `timeline.place`, offset so the peak (not the file start) lands on the cut.
- Judge a short hit by its peak against the voice at the same moment, a riser or bed by its loudness: 400 ms
  loudness reads a 0.2 s effect several dB low. Far under both is lost: raise it or move it off the words.
- **Runs of one sound** (list items popping in, cards dealing): the same file at the same level and spacing sounds
  mechanical. Alternate two samples, step the gain down along the run (one that worked: −8 → −12 dB over six
  hits), let the spacing follow the motion.

## Loudness per output

- **Each export is normalized to its own target** with `file.exportMedia {loudnessLufs}`. Values seen: −14 LUFS
  short-form, −16 podcast, web or voice-only, broadcast −23/−24; true peak −1 to −1.5 dBTP, lower when the
  platform re-encodes. Override only for a reason the user gave.
- Before export: `loudness.py --curve` on the mix for silences and jumps between sections (one source keeps
  chapters within 2 LU, another warns at ±1 LU).
- **Camera-mic speech with short peaks** (laughs, plosives, bangs) can cap normalization at the true-peak ceiling:
  one BashCut edit stayed at −16 LUFS against −14. Lower the gain (or a volume keyframe) on each loud line until its
  peaks sit with the rest, then export again.
- Trust the delivered file, not the setting: export the same settings as WAV and run `loudness.py` on it.
- Report the numbers and list the joins and voiceover windows for the user to play.
