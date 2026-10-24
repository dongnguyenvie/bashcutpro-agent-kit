---
name: batch
description: Run one edit pipeline over many inputs with the batch runner: presets (Vietsub a folder, podcast to shorts, every platform), writing a pipeline, running it in parallel, retrying failed items. Not for a single video (bcp:edit-workflow). Triggers: "batch", "batch these", "do this for every clip", "a whole folder", "100 videos", "làm hàng loạt", "cả thư mục", "xuất hàng loạt", "vietsub cả thư mục", "chạy batch", "process all".
---

# Batch runs

Reply in the user's language. `bashcut-batch` runs one pipeline over many inputs: **every input becomes its own
project** (open and fix any of them later), up to `concurrency` items run at once, each step in its own
`bashcutpro-cli` (engine) process, and the job book survives the app, the runner or the machine stopping. The app does not need
to be open. Format, job book and caps: BashCutPro `bashcut/batch.md`; this skill is how to use it well.

## 1. Batch or not

- **Batch** when the same recipe fits every input and judgement per item is small or can be capped: subtitles for a
  folder, clean audio, a caption draft, the same exports for many clips, shorts from many recordings.
- **Not a batch** when each video needs its own plan, gates and taste (`bcp:edit-workflow`), or there are fewer than
  three inputs: edit them one by one, then reuse the steps that worked as a pipeline next time.
- Run one item first (`--input` a single file) and look at its project and exports before the whole folder.

## 2. Built-in presets

Install once from the plugins repo: `bashcut-batch presets install <bashcutpro-plugins>/packs/batch`, then
`bashcut-batch presets list` shows them with a description.

| Preset | Steps | Needs | Before you rely on it |
|---|---|---|---|
| `vietsub-folder` | transcribe, `bashcut.captions.create` 42 × 2, translate (`translate-captions`), cover burned-in subtitles, caption style; `tiktok` + `youtube` | the plugin; a key, else each item hands off (see 5) | Vietnamese cues keep the English timing: run `captions_fit.py plan` on one item and look at `left` |
| `podcast-shorts` | transcribe, then an agent step (`bcp:rough-cut`): 3 vertical 20–60 s shorts, word captions, `shorts` exports | an agent (`claude`) with this kit | its brief makes captions with `createCaptions` and word style, without the speed fix or an SRT: copy it and use the brief in 3 |
| `every-platform` | transcribe, captions 42 × 2, an agent step makes one reframed sequence per aspect and exports every profile | an agent; `bashcut.vision` for face-following reframes | – |
| `captions-draft` | transcribe, `bashcut.captions.create` 42 × 2, caption review, SRT, `clean` word style, a `youtube` preview | – | measured on 2 clips: 90 % and 100 % of cues at or under 20 cps, 0 over 25 |
| `clean-audio` | `bashcut.audio.polish {amount: 0.5, target: -16}` on every clip, a loudness reading, a WAV each | – | – |

```sh
bashcut-batch run --preset vietsub-folder --input ~/clips --projects ~/clips/out
```

Prefer a preset; copy it into a pipeline file only to change it (`bashcut-batch presets show NAME > my.json`).

## 3. Writing a pipeline

A `bashcut-batch/1` JSON file (full example in <skill_dir>/REFERENCE.md):

- `inputs`: files, folders (media files in them, not recursive), `.fcproj` projects (copied, never edited in place);
  `projectsFolder` for the item projects, `outputsFolder` for exports (default `<projectsFolder>/exports`).
- `template`: `{"project": "…fcproj"}` copied per item (made with `bashcut.template.save`), or `{"commands": […]}`;
  default: import the input and make a sequence from it.
- `steps`, each exactly one of:
  - `command` + `params`, or `commands` (several in one process: all saved or none). Use command ids from
    `command_list`; `{name}`, `{media}`, `{project}`, `{outputs}`, `{itemDir}` are filled in per item.
  - `plugin` `{argv}`: a plugin action, e.g. `["python3", "{plugins}/bashcut.translate-captions/plugin.py",
    "translate", "--project", "{project}", "--cli", "{cli}", "--target", "vi"]`.
  - `agent` `{skill, brief, agent?: "claude" | "codex", maxTurns? (120), maxMinutes? (30), fixRounds? (2, at most
    5), review? (true), reviewProfile?}`: a kit skill run headless on the item. Afterwards the runner opens and
    reviews **every sequence the agent made** with `bashcut.review.run` (`reviewProfile` as its profile, BashCutPro#195)
    and sends the blocking findings, each naming its sequence, back for at most `fixRounds` rounds; findings left end
    the item `needsFix`. An agent out of turns does not lose the item: the rest of it (exports included) runs on
    its last save and the item ends `needsAttention` (BashCutPro#219); `retry` runs the agent again, `retry --done`
    keeps the result. A multi-skill brief (a tutorial: cut, cards, zooms, captions) sets `maxTurns` 150. Set `reviewProfile` to the outputs' profile, else the review judges loudness at −14 LUFS.
    Keep the brief to one task with a measurable end, and name the numbers the review and the bench check:

    > 3 standalone 30–60 s clips by quote from {name}, one 1080×1920 sequence each named short-1..3. Cuts in pauses
    > between phrases, never inside a word. Captions per clip with bcp:captions-text (`bashcut.captions.create`, 26–32 × 2,
    > ≥ 90 % of cues ≤ 20 cps), reviewed, an SRT per clip in {outputs} before any word style. Voice with
    > `bashcut.audio.polish {profile: "shorts"}`. Review every clip with bcp:review, then one `bashcut.profiles.apply
    > {profile: "shorts", path: "{outputs}/{name}-short-N.mp4", wait: true}` each. Save the project.

  - **Give agents the kit**: `bashcut-batch run --kit /abs/bashcutpro-agent-kit` (or `BASHCUT_KIT`, or a copy in
    `<data dir>/bashcut-kit`). Claude Code then gets it as `--plugin-dir` with the tools its scripts need (`Skill`,
    `Read`, `Write`, `Bash(python3:*)`, ffmpeg), and every agent a prompt line with the skills path (BashCutPro#204) and the interpreter to type for its
    scripts (`BASHCUT_PYTHON`, `{python}` in a pipeline: `python` on Windows, BashCutPro#223).
    Without it the agent has only the MCP tools and cannot run `loudness.py` or `contact_sheet.py`. `"kit": false`
    opts a step out; `"allowedTools": [...]` adds tools. `{kit}` is a placeholder for plugin steps.
  - A command step runs no review: end a pipeline without an agent with a `bashcut.review.run {profile}` step (before
    any word style), and read its verdict in the step's `.out`.
- `outputs`: `{"name": "{name}-tiktok.mp4", "profile": "tiktok"}` (output profiles: `bashcut.profiles.list`), or
  `preset` / `format` / `settings` for a plain export preset.
- `onFailure`: `skip` (default: the item stops, others go on) or `stop`. `concurrency`: start at 2;
  `agentConcurrency`: 1 unless the user accepts the cost. `resources` caps memory per item.

Check it before running: `bashcut-batch validate my.json --input ~/clips` lists the items and projects it would make.
A project that already exists is never overwritten: pick another `--projects` folder.

## 4. Running and watching

```sh
bashcut-batch run my.json --id vietsub-oct --input ~/clips --projects ~/clips/out
bashcut-batch status ~/clips/out/.bashcut-batch/vietsub-oct --wait     # JSON: items, steps, errors, timings
bashcut-batch list ~/clips/out                                            # every job in that folder
bashcut-batch cancel <job>                                                # stops it; running steps are killed
```

`run` prints a summary (counts, agent turns / tokens / cost, peak memory) and exits 0 only when every item is done.
Report to the user: items done, which need attention and why, where the projects and exports are. Long batches keep
the machine awake; after a restart `bashcut-batch resume <job>` goes on where it stopped.

## 5. Fixing what did not finish

Read each item's `error.category` in `status`:

| Category / status | What to do |
|---|---|
| `command`, `usage` | the step's command or params are wrong for this input: open `items/<name>/<step>.err`, fix the pipeline, `retry` |
| `offlineMedia` | the input could not be read: check the file, then `retry --items <name>` |
| `tripped` | the step was running when the runner stopped; it is never re-run blindly. Open the item's project, check what the step did, then `retry --items <name>` |
| `handoff` (needs attention) | a plugin needs you, e.g. translation without a key: follow that plugin's skill on the item's project (`export-lines`, translate, `apply`), then `retry` |
| `needsFix` | review findings the agent did not fix: fix them in the project (`bcp:review`), then `retry` or leave it for the user |
| `limit`, `timeout` | the agent step ran out of turns or minutes: shorten the brief or raise the cap, `retry` |
| `resources` | the machine was short of memory or disk; it runs again by itself, or lower `concurrency` |

`bashcut-batch retry <job>` reopens every failed, cancelled, needs-attention and needs-fix item (`--items a,b` for
some); finished steps are kept.

## 6. Afterwards

Spot-check two exports at phone size and one project in the app before telling the user it is done. A pipeline that
worked is worth keeping: `bashcut-batch presets save NAME my.json`, and a lesson through `bcp:self-learn` when a step
needed changing.
