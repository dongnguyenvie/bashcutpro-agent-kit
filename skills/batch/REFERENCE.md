# Batch: a full pipeline

Run without its agent step on two generated clips (a 28 s talk, a 71 s tutorial; `bashcut-batch run p.json
--speech-model whisper-base`): 2 items done in 1:31; the SRTs read 92.3 % and 100 % of cues at or under 20 cps
(none over 25), the exports −14.0 LUFS and −1.7 / −1.8 dBTP.

```json
{
  "schema": "bashcut-batch/1",
  "name": "talk-captions",
  "description": "Talking clips: readable captions, word style, voice polish, YouTube",
  "inputs": ["clips/"],
  "projectsFolder": "out/projects",
  "outputsFolder": "out/exports",
  "concurrency": 2,
  "onFailure": "skip",
  "steps": [
    {"label": "transcribe", "command": "sequence.transcribe", "params": {"language": "auto"}, "timeoutSeconds": 3600},
    {"label": "captions at 20 cps", "command": "bashcut.captions.create", "params": {"maxChars": 32, "lines": 2, "trimHedges": true}},
    {"label": "style and review", "commands": [
      {"id": "captions.setStyle", "params": {"size": 64, "color": "#ffffff", "outline": 4, "outlineColor": "#000000"}},
      {"id": "bashcut.review.run", "params": {"profile": "youtube"}}
    ]},
    {"label": "SRT, then word style", "commands": [
      {"id": "captions.export", "params": {"path": "{outputs}/{name}.srt"}},
      {"id": "bashcut.captions.wordStyle", "params": {"style": {"preset": "pop", "pop": 1.2}}}
    ]},
    {"label": "voice", "commands": [
      {"id": "edit.selectAll", "params": {}},
      {"id": "bashcut.audio.polish", "params": {"amount": 0.5, "profile": "youtube"}}
    ]},
    {"label": "punch-ins", "agent": {"skill": "vlog-talking-head", "brief": "Add punch-ins every 4-6 s on {name}; keep the face in frame; cuts only in pauses.", "maxTurns": 30, "maxMinutes": 15, "fixRounds": 2, "reviewProfile": "youtube"}}
  ],
  "outputs": [
    {"name": "{name}-youtube.mp4", "profile": "youtube"}
  ]
}
```

- `bashcut.captions.create` prints its `after` numbers and `left` to the step's `.out`. On a build without it, the
  same step as a kit script: `{"plugin": {"argv": ["python3", "{kit}/skills/captions-text/captions_fit.py", "apply",
  "--cli", "{cli}", "--project", "{project}", "--max-chars", "32", "--lines", "2"]}}` (needs `--kit`).
- Pauses: `transcript.removePauses` finds none on Whisper words (they swallow the silences, BashCutPro#203); tighten
  from the sound in an agent step (`bcp:vlog-tutorial` "Pace").

- Placeholders: `{input}`, `{media}` (the input file), `{name}` (the item name, from `outputName`, default the file
  stem), `{project}`, `{itemDir}` (the item's folder in the job book), `{outputs}`, `{cli}`, `{plugins}`.
- Job book: `<projectsFolder>/.bashcut-batch/<id>/state.json`; each step's scripts and logs in `items/<name>/`
  (`<step>.out`, `<step>.err`; agent steps: `<step>.round-N.out` transcripts and the review per round).
- Agent steps get the MCP server `bashcut-mcp --headless --project <item>` with writes limited to the item folder
  and the outputs, when `bashcut-mcp` is installed next to `bashcut-batch`.

## Agent with the kit

`bashcut-batch run my.json --kit /abs/bashcutpro-agent-kit` is all it takes (BashCutPro#204): agent steps load the
kit's skills and may run its scripts, fix rounds resume the session. Measured: a 1-item batch whose agent step ran
`captions_fit.py` through the kit finished `done` in 1:34 (17 turns, $0.58), review pass. Compound shell commands
(`cat … | python3 …`) still need approval in headless mode: ask for single `python3` calls in the brief.
