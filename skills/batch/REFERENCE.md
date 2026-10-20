# Batch: a full pipeline

Run on two generated clips (`bashcut-batch run p.json --speech-model whisper-base`): 2 items done in 47 s; the
SRTs read 92.3 % of cues at or under 20 cps (a 190 wpm voice), the exports −14.0 LUFS and −1.6 to −1.8 dBTP.

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
    {"label": "captions at 20 cps", "plugin": {"argv": ["python3", "/abs/bashcutpro-agent-kit/skills/captions-text/captions_fit.py",
      "apply", "--cli", "{cli}", "--project", "{project}", "--max-chars", "32", "--lines", "2", "--trim-hedges"]}},
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

- The kit path in the plugin step is absolute (the pipeline has no kit placeholder). `captions_fit.py apply` prints
  its `after` numbers and `left` to the step's `.out`.
- Pauses: `transcript.removePauses` finds none on Whisper words (they swallow the silences, BashCutPro#203); tighten
  from the sound in an agent step (`bcp:vlog-tutorial` "Pace").

- Placeholders: `{input}`, `{media}` (the input file), `{name}` (the item name, from `outputName`, default the file
  stem), `{project}`, `{itemDir}` (the item's folder in the job book), `{outputs}`, `{cli}`, `{plugins}`.
- Job book: `<projectsFolder>/.bashcut-batch/<id>/state.json`; each step's scripts and logs in `items/<name>/`
  (`<step>.out`, `<step>.err`; agent steps: `<step>.round-N.out` transcripts and the review per round).
- Agent steps get the MCP server `bashcut-mcp --headless --project <item>` with writes limited to the item folder
  and the outputs, when `bashcut-mcp` is installed next to `bashcut-batch`.

## Agent with the kit's scripts

```json
{"label": "edit", "agent": {"skill": "vlog-tutorial", "brief": "…", "fixRounds": 2, "reviewProfile": "youtube",
  "argv": ["claude", "-p", "{prompt}", "--output-format", "stream-json", "--verbose", "--max-turns", "60",
           "--mcp-config", "{mcpConfig}", "--plugin-dir", "/abs/bashcutpro-agent-kit",
           "--allowedTools", "mcp__bashcutpro", "Bash(python3:*)", "Bash(ffmpeg:*)", "Read", "Skill"]}}
```

`{session}` is empty on the first round, so this argv cannot pass `--resume`: each fix round is a new session that
gets the findings in its prompt. Until BashCutPro#204 adds the kit and tools to the built-in adapter, prefer plugin
steps for the scripts and the plain agent step for judgement.
