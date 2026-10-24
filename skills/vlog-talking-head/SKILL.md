---
name: vlog-talking-head
description: Recipe for one person talking to camera (opinion, story time, tips): strongest line first, cuts on word edges, punch-ins every 4-6 s, captions, B-roll on claims. Use after bcp:vlog-plan picks talking-head. Not for clips from a long podcast (bcp:vlog-podcast-clips) or screen demos (bcp:vlog-tutorial). Triggers: "talking head", "story time", "opinion video", "video nói chuyện", "nói trước camera", "chia sẻ quan điểm".
---

# Talking head

An id or param this engine rejects: run `command_list` (or `bashcutpro-cli describe <id>`) and use what it lists; never guess an id; if a skill's id is missing, say the kit and BashCutPro versions differ (bcp:setup).

Reply in the user's language. Survey, choose values from the ranges below and write them into the plan with
bcp:vlog-plan, then edit with bcp:edit-workflow. A measured reference replaces these ranges. Outputs: vertical →
Shorts, TikTok, Reels; landscape → YouTube 1080p. Word times come from `transcript.inspect` after
`bashcut.transcript.generate` (it refines word edges on the audio), or `transcript.set` with imported timings
followed by `bashcut.transcript.refineEdges`.

## Ranges

| Check | Sample range | Why it varies |
|---|---|---|
| Pauses to cut | tighten pauses of 0.3–0.8 s and keep breaths (T06 §7); a kept pause is 0.15–0.5 s, scaled to the speaker's own median gap (T11 §3) | high energy and a fast talker cut to the low end; emotion, a joke's beat or a thoughtful line keep the pause |
| Cut padding | never by hand: a 0.1 s pad pulled the neighbouring words in (bcp:rough-cut). tighten.py keeps 0.1–0.15 s of quiet, at most half the gap; gaps ≥ 400 ms are clean cut points, 150–400 ms need a look (T06 §3) | a trailing reaction or laugh: a wider range, not a pad |
| Framing change | every 4–6 s (T07 §7) | a dense argument changes more often; a slow story less |
| Punch-in zoom | a slow drift 1.03–1.07× over a shot; a snap punch 1.1–1.15× on one word, about 4–6 in a 60 s reel; a reframe cut 1.15–1.3× (T08 §3); all within the clip's headroom | a 4K source in a 1080 sequence has room to 2×; a 1080 webcam has none, so the punch upscales; a face filling the frame leaves less to crop |
| Longest shot | the top of the framing-change band (each punch-in is a new shot) | a landscape podcast holds longer than a vertical tip |
| Shortest shot | 0.6 s; a piece under it merges with its neighbour (tighten.py's `shortSpans` lists those under 0.4 s) | a hard punch on one strong word is short on purpose |
| Hook | 1.5–3 s: the strongest complete sentence (T06 §7) | a long sentence needs the top of the band |
| Cuts on a word edge | ≥ 70 % of all cuts, 100 % of speech cuts (the bench counts every cut not inside a spoken word, 20 ms of tolerance) | B-roll and punch-in cuts may fall mid-word on purpose, under continuing speech |
| Cuts a minute | 15–30 in a vertical short | over 35 reads as a jump-cut machine: raise `--min-pause` |
| Captions | ≤ 20 cps; 2–4 words a group (T09 §7); vertical 15–20 characters a line at `size` 40, 2 lines; break groups on pauses of 0.15–0.6 s (T09 §3) | fast talkers need the low end; landscape subtitles 32–42 characters |
| Music under the voice | the deep end of 5–18 dB (T11 §3), or none | the voice is everything; music with vocals masks words |

## Structure (30–60 s)

Sample lengths, not slots: the plan gives each section its own range and a named range marker.

| Part | Length | What |
|---|---|---|
| Hook | 1.5–3 s | the strongest sentence of the take, moved to the start (a claim, a number, a question) |
| Points ×2–4 | 8–15 s each | one idea each; a keyword pop on its key word |
| Payoff | 3–6 s | the conclusion or the twist |
| CTA | 1–2 s | one short line, said or on screen |

## Cuts and motion

- Cut ums, false starts, repeats and dead air on word edges with bcp:rough-cut `tighten.py`: the take's ranges in
  story order (the hook range first), `--min-pause` and `--keep-pause` from the pause range above (0.35 / 0.1 for
  energy, 0.5 / 0.15 for a story). It prints one `bashcut.batch`; its edges never fall inside a word, so every speech
  cut counts as on a word edge. Read `removed` and `connectedSpeech` before running it. Keep the last complete take
  (T06 §3).
- Punch-in and B-roll cuts come after, on the tightened timeline: put them on a word's `start` from
  `transcript.inspect` of the edit sequence (bcp:beat-cut), so the share of cuts on a word edge stays ≥ 70 %.
- Alternate framing: normal → punch-in → normal at the zoom you chose, a snap punch on the strongest words: Motion
  scale keyframes with `effects.setParam` (bcp:effects); check the crop with `render_frame`. Never punch in on a
  sign or on-screen text.
- B-roll or a screenshot over any claim that can be shown (bcp:stock-images), 1.5–3 s, voice continuing under it.
- Designed graphics (kinetic keyword type, counters, full-frame cards): bcp:motion-graphics, an installed `.fcgt`
  through `graphics.template.apply`, else `graphics.newText` (the vlog library looks are not ported yet).
- Shorts cut from a long recording: bcp:vlog-podcast-clips picks them; each is then edited with this recipe.

## Rhythm, presence, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Pattern interrupt | a B-roll, a graphic, a framing change or a new point every 10–30 s short-form; 30–90 s long-form (T07 §3) | framing changes every 4–6 s are the small resets; this is the bigger one |
| Speaker presence | B-roll and cards cover about 30–50 % of edited reels; one explainer kit keeps the speaker on screen about 40 % (T13 §3); 25–60 % across tutorials and explainers (T19 §3). Audit it, do not cap it | an opinion or story keeps the face; tips with things to show cover more |
| Transitions | hard cuts and punch-ins; 0–1 special transitions per video (T08 §7); a blink (a 2–4 frame dip) only to hide a cut that still jumps | — |
| Keyword pops | entrance 0.15–0.6 s ending on the word, 0.5–2 s as an accent (T13 §3) | the word's weight |
| Graphic density | 3–8 graphics a minute of talking; leave some sentences bare (T13 §3, §4). Graphics-led tip shorts run far above: one measured reference changed the picture every ~1.6 s with about 30 graphics a minute, keywords only, no running captions (2026-10-09) | dense information high; a personal story low; a reference measured with bcp:style-study replaces it |
| Caption landing | captions start within 0.1–0.3 s of the word (T16 §3) | — |

## Text, sound, look

- Captions with bcp:captions-text: `bashcut.captions.create {maxChars: 20, lines: 2, maxCps: 20, breakSeconds: 0.4}`
  for the 2–4 word groups (a smaller `maxChars` gives shorter ones), then `captions.setStyle {track: "C1", size: 40,
  margin: 0.23, outline: 4, outlineColor: "#000000"}`: bold outline, above the platform's bottom band (TikTok and
  Reels: read `bashcut.profiles.get {profile}` `safeArea`). A word-by-word highlight: `bashcut.captions.wordStyle`.
- Sound: the voice clean and even; music very low or none; a subtle whoosh on punch-ins (bcp:audio-mix).
- Look intent: natural skin, eyes bright, background a little darker than the face. Measure first
  (bcp:color-grade).

## Review and export

`bashcut.review.run {profile, sequence}` on the edit sequence (bcp:review): 0 blocking before the export. The
caption fixes come from the finding's `limit` (`marginAtLeast`, `sizeAtMost`) or a smaller `maxChars`; a
`cutInWord` from the range edge. At most 2 fix rounds. Then one export: `bashcut.profiles.apply {profile, path,
wait: true}`.

## Review notes

- One camera repeats its framing by nature; jump cuts are still fixed with punch-ins.
- Blockers a viewer notices: a cut inside a word, captions that come late, a pause cut so tight the breath is gone,
  music with vocals under speech. A slightly long pause is not.
- `needs_user`: the speaker's name and title for a label, which take when two are equally clean, sources for claims
  made on camera, music or none.

## Plan data

- `stages`: `{"voiceover": {"required": false, "why": "the speaker's own lines"}, "rhythm": {"rules": ["a framing change every 4–6 s; jump cuts fixed with punch-ins"]}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "each line gets a picture, a punch-in or the face on purpose"}}`
- `checks`: `no-cut-in-word` no cut inside a word, ≥ 70 % of cuts on a word edge; `captions-on-time` captions start within 0.1–0.3 s of the word;
  `breath-kept` no pause cut so tight the breath is gone; `no-vocal-music` no music with vocals under speech.
- `askAtIntake`: `["speakerName"]` (name and title for the label).
