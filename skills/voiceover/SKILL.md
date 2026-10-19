---
name: voiceover
description: Voiceover in BashCutPro: measured speaking rate and narration windows (narration.py), lines sized to them, text prepared for TTS, English lines with the built-in tts.* voices, Vietnamese lines with the bashcut.vieneu-tts plugin, every take checked against its text, re-takes in place, fit to picture, dubbing; the voice sub-agent runs a whole script. Triggers: "lồng tiếng", "thuyết minh", "đọc lời", "giọng AI", "clone giọng", "TTS", "dịch lồng tiếng", "voiceover", "narration".
---

# Voiceover

The numbers below are ranges with their source: choose with the measurements in hand, then measure again. Commands
and JSON shapes: [REFERENCE.md](REFERENCE.md). A whole script goes to the `voice` sub-agent (`agents/voice.md`);
no sub-agent (Codex): follow `<skill_dir>/../../agents/voice.md` yourself.

## Provider and voice

The content language decides (`brief.language` in the project notes, else the footage's):

| Language | Voice | Where it runs |
|---|---|---|
| English | `tts.*`: `tts.voices` lists them, `tts.create` places a line, `tts.edit` re-takes it | in the app. Headless MCP (`filmcraft-cli mcp`) has only the built-in formant voices, robotic; the natural Kokoro voices (`tts.downloadVoices`) exist only in the desktop app, so bridge to it (`bcp:setup`) for a narrator a viewer should believe |
| Vietnamese | the `bashcut.vieneu-tts` plugin (VieNeu-TTS v3 Turbo, 25 preset voices, cloning with consent) | out of process on this computer: wav takes, then `media_import` + `timeline.place` |
| another language | none built in | a recorded voiceover (`audio.voiceover.*`), or captions and on-screen text carry the lines |

- Never read Vietnamese with an English voice, nor the reverse. No voice for the language → say so, offer a
  recorded voiceover; until one serves, finish without voiceover (captions or on-screen text carry the lines) and
  say so in the final summary.
- VieNeu not installed (`VN check` → `not_installed`): tell the user it downloads about 1.4 GB and ask before
  `VN setup --download-model` (REFERENCE "VieNeu").
- Pick by region, style, gender and measured rate, then audition 2–3 voices on the **hardest** line, not the
  first; the first voice is rarely the pick (T10 §2). You cannot hear: give the user the takes to listen to.
- Cloning only when the user asks, of their own voice or one whose owner agreed in this conversation:
  `--reference clean-3-to-8-s.wav --clone-consent`. Never pass `--clone-consent` by default (T10 §6). Prefer the
  user's own voice when the video is theirs and they speak in it; a preset for a narrator, or when the clone
  sounds off on the hardest line.
- Never mark AI voiceover on the video (no "AI voice" text or sticker); the voice should simply sound natural.

## 1. Measure before writing

There is no normal speaking rate: it varies by voice, language, genre and energy (T10 §3). Measure it in the
content language's unit (syllables for Vietnamese, characters for Chinese/Japanese/Korean, else words): save
`transcript.inspect` to a file, then `narration.py rate words.json --speaker N` (each speaker in the footage);
for a voice, one test line voiced alone (REFERENCE "Test line") and its `unitsPerSecond` or the plugin's
`syllablesPerSecond`.

- When the voiceover should sound like the creator, size lines from the creator's own measured rate.
- Never reuse an English words-per-second figure for a syllable language (T10 §3).
- Published Vietnamese rates are a sanity check for a measurement, never a budget. Pauses removed (compare
  `articulation`): read speech 4.7–5.3 syllables a second (Bradlow, Interspeech 2019: 4.74; Pellegrino et al.,
  Language 2011: 5.22). Pauses inside phrases kept (compare `overall`): 200–245 a minute, 3.3–4.1 a second
  (Vu et al., ACL 2025, PhoAudiobook: audiobooks 201; news, YouTube and conversation sets 224–243). A measurement
  far outside these: check the transcript for dropped or merged words before sizing lines from it.
- No words yet: `transcript.generate` needs a Whisper build (`transcript.models` → `available`); otherwise
  words from an outside transcriber through `transcript.set` (`bcp:footage-survey`).

**Never say what the person is about to say.** `narration.py windows` quotes the live speech on each side of every
window (`before` / `after`, about 5 s each way): drop or rewrite a line that repeats it. "Mình chỉ bạn làm từng
bước nhé" right before the presenter said the same thing played the idea twice. A voiceover line bridges, sets up
or adds what the speech does not say.

Then `narration.py windows words.json --rate R --min-seconds S` gives speech-free windows (0.3 s kept from real
speech each side, `--margin`) with a unit budget each. Write each line to its budget, with slack from the voice's
p10–p90 spread. The `bashcut.align` plugin's `check --script lines.txt --rate R --windows windows.json` reports
every line over its window (`data.over`). A line that does not fit: **cut text**, never plan to speed the voice (T02 §4). TTS length drifts
(a 50 s script came out 40–45 s, T10 §3): final timing comes from the take, not the script.

## 2. Prepare the text

Spell out what gets misread:
- Numbers, years, times: `2026` → "hai nghìn không trăm hai mươi sáu", `7h30` → "bảy giờ ba mươi". Captions
  keep the digits (T10 §2).
- Units and symbols: km, %, °C, `k` (nghìn đồng).
- Acronyms as letters ("xê en xê" for CNC); show them as letters again in captions.
- English or unusual words in a Vietnamese line: rephrase in plain words rather than respelling ("chill" was read
  "chiều").
- Very short exclamations (≤ 5 words) with an expressive voice fail often; use a calm voice or a longer line.

When a phrase is misread in every take, **rewording beats regenerating** ("kín xe" → "chật cứng xe"). Change
approved text minimally and tell the user which words changed.

Keep the lines in the plan (project notes, `bcp:edit-workflow`): `plan.voiceover` [{id, text, caption, section,
seconds, pause}]; `text` as heard, `caption` with digits, `seconds` where the line starts. One line, one
sentence: the take is checked against it and the captions break on it.

## 3. Synthesize

**English** (`tts.*`): `tts.create {text, voice, pace, time, track: "A2"}` (`time` in ticks) voices and places one line
(REFERENCE "English with tts"). A whole script: one `command_batch` of `tts.create` steps at each line's start.
`tts.render {text, voice, sample: true}` or `tts.preview` auditions without placing.

**Vietnamese** (VieNeu): write the plan's lines to `lines.json` (`{"lines": [{id, text, seconds}]}`), then
`VN synthesize --lines lines.json --voice "…" --takes 2 --out <project dir>/voiceover/vieneu`: every take lands
as `<id>/take-N.wav` with `seconds` and `syllablesPerSecond` in `takes.json`, nothing placed. Place the kept takes
in one `media_import` + one `command_batch` of `timeline.place {item, track: "A2", seconds}` (REFERENCE
"VieNeu"). `VN speak` does both in one call when the plugin can reach the project itself.

- Pick the take yourself, for example the one whose rate is closest to the rate you sized the line with.
- Takes: 2–6, more for short or expressive lines (T10 §3); VieNeu varies them with `--variation`.
- A take whose rate is far from the voice's measured rate (video-recap flags beyond about ±30 %, T10 §3) has
  likely dropped, repeated or invented words: check it first.
- Style or emotion: compare with a neutral take of the same text: +25 % duration "took effect", < 5 % "not
  applied" (jianshuo, T10 §3).
- Keep unplaced takes in `voiceover/` next to the project; never delete them before the user approved the voice.

## 4. Check every kept take

The model misreads, drops or repeats words, mostly **at the start** of a line. Transcribe the take
(`transcript.generate {items: [take]}` in a Whisper build, then `transcript.inspect`; else an outside transcriber
on the wav) and compare: `narration.py check take.json --text "line" --min-similarity 0.9`. Read `unmatched`,
`extra` and `atStart`, not only `similarity`: a repeated word barely moves it. The threshold is your call (one kit
gates at 0.92 for Chinese, T10 §3). Recognition also mishears some regional accents (s→x, final n→ng): count only
errors a listener would hear. Fix by rewording or a re-take. Captions of the kept voiceover: align the script to it with the
`bashcut.align` plugin (`align --script lines.txt`), not a fresh transcription.

No transcription at all: say so and ask the user to listen to the lines with names and numbers; never call a take
checked when it was not.

## 5. Fit to picture

Fix in order of naturalness (T10 §4, jianshuo ladder):

1. **Shorten or reword the text**, then re-take.
2. **Provider rate**: `tts.create` / `tts.edit {pace}` for English (jianshuo slows −12…−15 % before
   stretching, T10 §3). VieNeu has no rate control: skip to 3.
3. **Change speed**: `clip.speedDuration {clips, speed}` (percent). Ranges seen: slowing to 82–95 % (floors 82
   jianshuo, 85 digitalsamba; imperceptible above ~92); speeding up to about 110 % and only after rewriting
   failed. How much goes unheard varies with the voice's timbre and the music masking it (T10 §3); the user
   listens to every changed line.
4. **Change the text more**, with the user's consent (it changes the captions).

Silence at a line end is often better than a stretched voice. Ranges seen: tail after the last word 0.1–0.5 s,
longer before a cut or reveal; gaps between sentences 0.2–0.8 s, up to 1–3 s after a key line (T10 §3). Set them
as each line's `pause` in the plan.

- Never over real speech. Keep a gap from real voices (0.3 s worked in our edits; `--margin`), and re-read
  `sequence_inspect` after placing: a line that runs into the next spoken clip is a blocker for `bcp:review`.
- Give each voiceover section b-roll longer than the line: a too-short clip made the voiceover run into the next
  spoken cut.
- Captions come from your `caption` text, timed by the take (`bcp:captions-text`). Level: against the music, not
  one number (`bcp:audio-mix`, `loudness.py` on a WAV export).

## 6. Re-take one line

English: `tts.edit {clip, text, pace}` re-voices the clip in place. Vietnamese: `VN synthesize --text "…" --takes
2`, import the pick, then replace the clip on A2 (REFERENCE "Re-take"). Check it again (§4), and fit again if its
length changed; re-time its caption.

## 7. Dubbing and localisation

1. **Transcribe** the original (`transcript.generate` or words through `transcript.set`) and measure both rates:
   the original speaker (`narration.py rate`) and the target voice (a test line).
2. **Translate** per cue, keeping cue boundaries at sentence ends. Languages differ in length (Mandarin takes
   60–80 % of the time Spanish does, jianshuo, T10 §2), so size each cue from the target voice's measured rate.
3. **Sample one cue first**: the most performance-sensitive one, not the first. Get the user's yes on voice and
   pace before batching (OpenMontage, T10 §2).
4. **Per cue, fit ladder**: shorten the text → re-take → speed within bounds → move the cue (`timeline.move`)
   into nearby silence. Tell the user which cues were shortened (it changes the meaning) and which moved.
5. **Keep the original audio as a bed** under the dub, not muted: jianshuo keeps it at 0.15–0.25 linear
   (≈ −16…−12 dB, T10 §3): `clip.audioGain {mode: "set", db}`, checked with `bcp:audio-mix`.
6. Check every cue (§4), then re-time captions from the takes.

## A recorded voiceover

The user records: `audio.voiceover.settings`, then `audio.voiceover.start {track, time}` and
`audio.voiceover.stop` (the app must have a microphone, so bridge mode). Measure and check it like a take.

## Report

Per line: id, voice, take, seconds, similarity (or "not checked" and why); lines reworded (old → new words); lines
sped up or moved; what you could not check (you cannot hear: tone, pronunciation of names). Write what changed in
the plan's `log`.
