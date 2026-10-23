# Edit workflow: reference

Detail for `bcp:edit-workflow`; read only the section a step names.

## Intake questions

One round, never one by one: AskUserQuestion in Claude Code, a numbered list in plain text elsewhere (Codex, chat
agents). At most 4, in this order; skip any the prompt or the notes answer, drop the least important to stay at 4
(a dropped one is decided and written `inferred`):

| Question | Your choice, first option | Other options |
|---|---|---|
| Which recipe | the best `bcp:vlog-<kind>` match, with the reason ("a 10 min portrait talk + a screen recording") | the close second; no recipe |
| The steps | "Đồng ý" with the stage list in the question text (`survey → story → rough cut → … → export`) | drop a stage (name it); add one |
| Length | the range the recipe and the footage support ("1:45–2:15, the best lines") | the platform's usual ranges |
| Where it will be posted | the shape of the footage (portrait → TikTok/Reels/Shorts) | YouTube (landscape); both |
| Language of speech and captions | the language the user writes in, or the one heard | English; other |

Every first option names the concrete choice, never a bare "auto": `AI chọn: talking-head + chèn màn hình
(Recommended)`, with the reason in its description. Text-only agents end the list with "Không trả lời: mình làm
theo lựa chọn 1 của mỗi câu". The user's writing language is a good first guess, not an answer: a Vietnamese prompt
can ask for an English video, and footage can speak another language. Language drives captions, fonts (Vietnamese
needs full diacritics, `bcp:captions-text`) and voices.

## Brief and plan in the notes

The project notes (`project.notes` to read, `project.setNotes {text, merge}` to write) hold one JSON block, so the
brief and plan survive a reset and travel with the `.fcproj`. A sidecar file (`<project>.plan.json` beside the
`.fcproj`) is fine when the notes already hold the user's own text. One write per stage, with every key that
changed (`stage` too); after a reset, resume from the notes, not memory.

Brief fields are `{value, status, source}`: `stated` (the user said it), `inferred` (your guess, reason in
`source`) or `confirmed` (approved at G1).

```json
{"brief": {
   "goal": {"value": "Show the night market in 60 s", "status": "stated", "source": "prompt"},
   "outputs": {"value": ["reels", "tiktok"], "status": "stated", "source": "prompt"},
   "lengthSeconds": {"value": {"min": 45, "max": 75}, "status": "inferred", "source": "Reels, a food vlog"},
   "language": {"value": "vi", "status": "inferred", "source": "speech heard"}},
 "plan": {
   "mode": "create", "stage": "story", "recipe": "bcp:vlog-food",
   "promise": {"hook": "Is the 20k bowl worth the queue?", "payoff": "Yes: the broth"},
   "sections": [{"id": "hook", "lengthSeconds": {"min": 2, "max": 4}, "reason": "best bite first"},
                {"id": "queue", "lengthSeconds": {"min": 8, "max": 15}, "reason": "the wait builds it"}],
   "cut": [{"section": "hook", "quote": "trời ơi ngon quá", "item": "<media id>"}],
   "checks": ["price visible at the payoff"],
   "decisions": [{"text": "no music under the vendor's lines", "why": "his voice carries it"}],
   "skipped": {"colour": "phone footage already matched"},
   "log": [{"stage": "rough-cut", "did": "batch of 14 steps, 0:58", "evidence": "sequence_inspect"}]}}
```

`mode`: `create` (footage and a goal: compare 2–3 story options), `directed` (the user said what to make: one
option, say where the footage cannot support it), `revision` (changes in place). Editorial numbers are ranges with
their source; choose within them for this footage and say why in `decisions`.

## Story

- **Hook in the first 1–3 s**: the best or most surprising moment, often the ending or loudest shot, then back to
  the start. A cold open of three shots (~8 s) worked well for travel and food vlogs.
- Tool demos, tutorials: hook on the tool's **output** with its own sound, then the presenter (below).
- Sections in time order after the hook, each with a length range and a reason, marked on the timeline with
  `markers.addRange {name}` once cut.
- Talking videos: a chain of spoken lines (real speech + voiceover, ~0.14 s gaps), picture cut to what is said,
  lines selected by quote (`bcp:rough-cut`). Music-led montages: cut on the beat (`bcp:beat-cut`).
- Every video opens a question and must close it: `promise.payoff` answers `promise.hook`.
- Script check (a voiceover or scripted piece): compare the plan's lines with the words heard
  (`transcript.inspect`) before G3; a line missing or changed is a finding.

## Screen recording with a presenter

| The user says | Build |
|---|---|
| "video giới thiệu tool", "demo phần mềm", "tutorial", "N phút" | hook = the tool's output (5–7 s, its own sound), then the presenter: prompt → tool working (fast-forward) → how it works, one panel per sentence → limits and next steps |
| "video desktop làm nền", "màn hình làm nền" | screen recording on V1, cut to the same moments as the speech (sync by sound: `clip.synchronize`, `bcp:footage-survey`); on a portrait sequence a blurred copy below fills the bars (`bcp:effects`) |
| "người nói ở trên video", "khung mặt" | presenter camera on V2 in front of the screen, Motion scale ~37 % (a 9:16 camera becomes ~400 px wide), bottom centre; captions between screen and face. "Ở trên" can mean the track order or the top of the frame: bottom centre was kept without complaint; ask when unsure |
| "ẩn giọng desktop", "tắt tiếng màn hình" | mute the screen clips; speech comes from the camera (`bcp:audio-mix`) |
| (unsaid, always) | one zoom per narration line onto the panel it names, changing when the screen changes; fast-forward waiting and typing (`bcp:effects`) |
| (unsaid, with a voiceover) | live speech within ~2 LU of the voiceover, music 15–20 LU under both (`bcp:audio-mix`); no voiceover line repeating the presenter |

Real case: a 5 min session (camera + screen) became a 2:00 intro, speech over 92% of it; dropped: fillers, muddled
lines, reactions to bugs, sentences where the camera mic heard the laptop playing the output. The first cut opened
on the presenter's "hello"; the user sent it back: "end user muốn biết output".

## Gates

| Gate | When | Show (cheap to look at) |
|---|---|---|
| G1 brief | after intake | the brief in 4–6 lines, `inferred` fields marked |
| G2 strategy | after story | 4–8 sentences + the section table, a frame of the hook shot |
| G3 rough cut | after the cut | the cut list from `bashcut.timeline.summary`, duration and cuts a minute against the plan, 4–6 frames |
| G4 script | before any speech is synthesized | the lines with their timing windows |
| G5 draft | after review | per output: the `bashcut.review.run` verdict, blocking and warnings left, fixed and kept issues, 4–6 frames, what was not checked |

`approved`: go on. Changes: apply the note, show again. Rejected: stop and ask. The user may say up front "no gates"
or "only the draft": then G1–G4 become a one-line notice and you go on, but G5 is always shown. Never render an
export only to earn a gate a frame or a cut list can show.

## Working efficiently

Every call resends the whole context, so cost is roughly calls × context. Measured on BashCut runs: one ad took
778 calls (159 state reads); a lean path made a 45 s ad in about 20 main calls.

- **One batch per stage**, not one `command_run` per edit; send independent reads together.
- **Read once**: `doc_inspect` on start, after a gate and after a failed batch; keep what your commands returned.
- **Search, don't print**: `transcript.search {query}` for a quote; a 25k-character transcript printed once was
  paid again by 25 later turns.
- **Sub-agents read, you decide**: the survey and the critic run as sub-agents that return a short answer.
- **Wait, don't poll**: long commands take `wait: true`; else `jobs.list` once when you need the result.
- **Look in sheets**: a contact sheet of 12–24 frames (`skills/footage-survey/contact_sheet.py`) costs about 1/15 of
  the same frames one by one; one frame every 2 s judges pace.
- **Render once per output**: the bench measured Pro's render time at 5–10× BashCut's from draft exports and
  re-exports. Frames and `bashcut.review.run` replace the draft; `file.exportMedia {format: "wav"}` (audio only,
  ~0.02 s for 24 s) when a script needs the sound; one `bashcut.profiles.apply` per output at the end.

## Window commands (bridge mode)

Connected to the open BashCutPro window (`mcp --bridge`), its own panels answer `command_run` too; a headless engine
does not have them (`scripts/commands.json` lists them under `frontend`):

- Plugins and their runs: `bashcut.plugins.list`, `bashcut.plugins.run` (progress in the Runs section),
  `bashcut.plugins.job`, `bashcut.plugins.cancel`.
- The in-app agent's gates: `bashcut.agent.gate`, then `bashcut.agent.approve` or `bashcut.agent.change`.
- The Batch section: `bashcut.batch.prefill` (files into a new batch), `bashcut.batch.run`, `bashcut.batch.state`;
  outside the window use `bashcut-batch` (`bcp:batch`).
- Showing the user something: `bashcut.ui.show.looks`, `bashcut.ui.show.batch`, `bashcut.ui.show.agent`.

Driving the window (`ui.click`, `ui.key`, `ui.type`, `ui.drag`, `ui.elements`, `ui.inspect`, `ui.set`,
`ui.screenshot`): these wait for a drawn frame. When the window draws none (minimised on Windows, covered on some
macOS setups) a request answers `window not in front … call ui.focus {}` after about 11 s, and the original
request may still land late. On that reply call `ui.focus {}` once, then re-read the state (`ui.elements` or
`ui.screenshot`) before deciding; never repeat the click blindly, it may already have happened. `ui.focus` and
`ui.menu.invoke` are not capped, so they answer even when the window is hidden.

## Limits

- Loudness and true peak are measured on the timeline (`bashcut.audio.loudness`, `bashcut.review.run`) and on the
  exported file (`bashcut.profiles.apply` `peakCheck`); what the review cannot judge is taste: a cut that feels
  late, music that fights the voice. Say in the hand-off what was not listened to.
- No revision guard: if the user edits in the app meanwhile (bridge mode), `doc_inspect` before the next batch.
- Speech needs a Whisper build for `transcript.generate`; otherwise words come from an outside transcriber and
  `transcript.set` (`bcp:footage-survey`).

## Export

**Output profiles first.** Builds with BashCutPro's profiles (`command_list {"filter": "bashcut.profiles"}` lists
them) export each output with `bashcut.profiles.apply {"profile": "tiktok", "path": "/abs/out/name-tiktok.mp4",
"wait": true}`: the platform's frame size and fps, codec, bitrate from upload guidance, loudness and true peak,
captions burned in or as a sidecar, all from the profile. Built-ins: `tiktok`, `reels`, `shorts` (1080×1920),
`youtube` (1080p), `youtube-4k`, `facebook-square`; the user's own in `<data dir>/bashcut/profiles/*.json` (same `id`
replaces a built-in). `bashcut.profiles.get {"profile"}` gives its `loudnessLufs`, `truePeakDbtp`, `captions` and
`safeArea` (review uses them); `bashcut.profiles.list {"seconds"}` adds the estimated file size. `sequence` exports
another sequence (a variant), `queue: true` adds to the export queue instead. For `bashcutpro-cli export --preset`,
`bashcut.profiles.compile` writes the presets (`BashCut TikTok`, …).

Builds without them (no `bashcut.profiles.*` in `command_list`), a watch copy the user asks for, or the master, use
`file.exportMedia`:

| Output | `file.exportMedia` params |
|---|---|
| Watch copy (asked for) | `format: "h264"`, `height: 960` (portrait) or `540` (landscape), `loudnessLufs: -14`, `burnCaptions: true`, `wait: true` |
| TikTok, Reels, Shorts | 1080×1920, `format: "h264"`, `loudnessLufs: -14`, captions burned in |
| YouTube | 1920×1080 (or source size), `format: "h264"`, `loudnessLufs: -14`, `captionSidecar: "srt"` |
| Master / archive | `format: "prores"`, `proresProfile: "hq"`, no loudness change |

`export.quick {preset}` and the `export.presets.*` commands use saved presets; a whole queue goes through
`export.queue.*`. Check the file exists and its length matches `sequence_inspect` before saying it is exported.

## Hand-off report

From the plan's `log` and `skipped`, not chat memory: stages run and skipped (with the reason), each gate with the
user's answer, review rounds (fixed, kept), what was measured and what was not (sound not listened to, loudness not
measured), the review verdict per output, every kept issue with its reason, the export paths. Example: "Review: 2 rounds. Closed a 1.2 s gap at
0:41, raised the caption out of the Reels bar. Kept: the 9 s shot at 0:12, the hook you chose. Not listened to: the
music under your voice."
