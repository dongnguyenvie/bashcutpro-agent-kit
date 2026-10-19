# Batch: a full pipeline

```json
{
  "schema": "bashcut-batch/1",
  "name": "talking-head-shorts",
  "description": "Talking-head clips: fillers out, word captions, TikTok and YouTube Shorts",
  "inputs": ["clips/"],
  "projectsFolder": "out/projects",
  "outputsFolder": "out/exports",
  "concurrency": 2,
  "agentConcurrency": 1,
  "onFailure": "skip",
  "steps": [
    {"label": "transcribe", "command": "sequence.transcribe", "params": {"language": "auto"}, "timeoutSeconds": 3600},
    {"label": "tighten", "commands": [
      {"id": "transcript.removeFillers", "params": {}},
      {"id": "transcript.removePauses", "params": {"minSeconds": 0.6, "keepSeconds": 0.25}}
    ]},
    {"label": "captions", "commands": [
      {"id": "transcript.createCaptions", "params": {"maxChars": 32, "lines": 1}},
      {"id": "bashcut.captions.wordStyle", "params": {"style": {"preset": "pop"}}}
    ]},
    {"label": "polish", "agent": {"skill": "vlog-talking-head", "brief": "Add punch-ins every 4-6 s on {name}; keep the face in frame.", "maxTurns": 30, "maxMinutes": 15, "fixRounds": 1}}
  ],
  "outputs": [
    {"name": "{name}-tiktok.mp4", "profile": "tiktok"},
    {"name": "{name}-shorts.mp4", "profile": "shorts"}
  ]
}
```

- Placeholders: `{input}`, `{media}` (the input file), `{name}` (the item name, from `outputName`, default the file
  stem), `{project}`, `{itemDir}` (the item's folder in the job book), `{outputs}`, `{cli}`, `{plugins}`.
- Job book: `<projectsFolder>/.bashcut-batch/<id>/state.json`; each step's scripts and logs in `items/<name>/`
  (`<step>.out`, `<step>.err`; agent steps: `<step>.round-N.out` transcripts and the review per round).
- Agent steps get the MCP server `bashcut-mcp --headless --project <item>` with writes limited to the item folder
  and the outputs, when `bashcut-mcp` is installed next to `bashcut-batch`.
