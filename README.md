# BashCutPro agent kit

Editing skills for Claude Code and Codex that drive [BashCutPro](https://github.com/dongnguyenvie/BashCutPro)
(a fork of FilmCraft) through its MCP server (`filmcraft-cli mcp`) and command ids.

The skills carry over the editing craft of [bashcut-agent-kit](https://github.com/dongnguyenvie/bashcut-agent-kit)
(how to cut, mix, caption and review well), rewritten against FilmCraft's command model: `command_list` to find a
command, `command_run {id, params}` or `command_batch` to edit (undoable), `doc_inspect` to read the project and
sequence, `render_frame` to look. They do not map BashCut's own tools. Plan and order:
[`bashcut/migration.md`](https://github.com/dongnguyenvie/BashCutPro/blob/main/bashcut/migration.md) in BashCutPro,
tracked in [BashCutPro#24](https://github.com/dongnguyenvie/BashCutPro/issues/24).

## Skills

| Skill | Use it for |
|---|---|
| `captions-text` | Captions from speech or imported words (`transcript.createCaptions`), a script or SRT aligned to the speech with the `bashcut.align` plugin, SRT/VTT, fixing and styling captions, titles and cards with `graphics.*` and `.fcgt` templates, Vietnamese fonts (`fetch_font.py`), size, contrast, safe area, sync |
| `edit-workflow` | The spine of every edit, raw footage to export: intake, brief and plan in the project notes, stages with the one skill to read for each, `command_batch` per stage, the user's gates, draft and export |
| `rough-cut` | The rough cut by quote: lines found with `transcript.search`, word-exact edges, takes and recording cues, fillers and pauses, selects with reasons, the blind second pass, long → short as one sequence per short |
| `effects` | Choosing transitions, motion, speed and reframes that fit the moment and genre, then making them with FilmCraft effects and keyframes (Cross Dissolve and the transition map, Motion Ken Burns and punch-ins, Time Remapping ramps, freeze, Auto Reframe, masks) |
| `vlog-plan` | Planning any vlog from a brief: the routing table to the right recipe, intake and survey, the plan as JSON in the project notes with section range markers, shared checks and ranges, then the hand-over to `edit-workflow` |
| `vlog-ideate` | Turning a vague idea or a folder of footage into a brief: angle, audience, hook ideas and outputs, read from the footage first, stored in the project notes, the idea gate asked in conversation |
| `vlog-hook-script` | Writing the hook, beats and voiceover script sized to the voice's measured rate, 2–3 openings compared on the real footage, the counterfactual check, the script gate |
| `visual-plan` | Deciding what the viewer sees on every line of a talking video: one treatment per line anchored to a word, balanced for density, variety and the face, written as visuals rows in the plan, AI pictures made in one locked style with the `bashcut.image-gen` plugin |
| `vlog-publish` | Finishing for posting: platform facts, one export per output at its own loudness, another shape as its own sequence, a no-music version, cover frames checked at phone size, YouTube chapters, title, caption and hashtags |
| `vlog-scene-prompt` | Writing cinematic prompts for AI video and image models when a shot is missing, reference images, continuing a series, fixing a failed generation, comparing takes and bringing the kept one in |
| `vlog-travel` | Travel vlogs and guides: cost or time hook, numbered place sections with place cards and price tags, whips between places, a cost recap and a save CTA |
| `vlog-food` | Food vlogs and reviews: the bite or pour as the hook, quick process inserts, slow motion within the source frame rate, real sizzle and crunch up front, appetising colour, price and address |
| `vlog-daily` | Daily-life vlogs (a day in my life, routines, study with me): time-stamped moments in order, calm holds and quick sequences, a diary voice, one calm music bed |
| `vlog-product-review` | Product reviews and unboxings: a price-question hook, claims shown in use, pros and cons, a verdict card, sponsorship disclosed early, true-to-life colour |
| `vlog-product-ad` | Ads and selling videos: the ad brief with a truth source, hook and CTA as a pair, an arc from what the product has, beat proportions, truth rules, one-change A/B variants as sequences (`bcp:variants`) |
| `vlog-talking-head` | One person talking to camera: the strongest line first, fillers and pauses cut with breaths kept, punch-ins every 4–6 s, short caption groups, B-roll on claims |
| `vlog-podcast-clips` | Shorts from a long podcast, interview or livestream: clips by quote with word-exact edges, the standalone test, a blind second pass, the user picks, one sequence per clip |
| `vlog-tutorial` | Tutorials and tool demos: the result first, step cards, one zoom per narration line onto what is clicked, waiting sped up, the presenter levelled to the voiceover, a vertical cut |
| `vlog-explainer` | Explainers with little footage: a question-and-number hook, one data graphic per section timed to the voice, fixed frame chrome, every number sourced, voiced or music-only |
| `vlog-news` | News shorts and documentaries from photos, archive and screenshots: fixed chrome or date cards, credits on every picture, verbatim quotes, attributed claims |
| `vlog-promo` | Promos, hype videos and showreels: beat cuts, kinetic type, rolling counters, a declared motif of two or three transitions, sourced numbers, only the person's own work |
| `setup` | Getting `filmcraft-cli` (source build or release, macOS / Windows / Linux), registering its MCP server headless (a project, the demo, or empty) or bridged to the running app, and checking `command_list` answers |
| `audio-mix` | Mixing by measurement: voice levelled per clip, a fixed music bed under it (ducking for long silences), fades, keyframes, SFX at cuts, music retimed, music and SFX found (`fetch_audio.py`), loudness read from WAV exports (`loudness.py`) and set per output |
| `color-grade` | Grading by measurement: scopes on the brightest, darkest and skin-heavy frames, Lumetri presets and LUTs (`grade.py` generates fitted looks), damage checks and backing off, shot match, one adjustment layer |
| `footage-survey` | The survey before an edit: inventory, scene detection, contact sheets from rendered frames (`contact_sheet.py`), transcripts (outside words imported with `words_to_transcript.py`), cues and restarts, shot descriptions in metadata, coverage gaps; run by the `surveyor` sub-agent |
| `review` | The review before export, 1–3 rounds: limits from sourced ranges, cuts against words, black frames from scopes, frames at phone size at every cut and text, loudness from a WAV export, severities by what a viewer sees, fixes re-measured; an independent `critic` sub-agent each round |
| `beat-cut` | Rhythm by measurement: word edges for speech-led edits, a beat grid from `beats.py` (an out-of-process estimate on a WAV: tempo, beats, downbeats, energy, cut sync) for music-led ones, shot lengths per section, cuts in one batch, punch-ins from zoom headroom |
| `style-study` | Learning a creator's or channel's style by measurement in a study project (pacing from scene detection, shots, hook, speech, music with `beats.py`, sound with `loudness.py`, colour from scopes), a profile with tolerances, deliberate differences, then a look, text presets and the edit plan's bands |
| `outcomes` | Learning from a published video's retention export (YouTube Studio, TikTok, Facebook, files the user provides): `outcomes.py` maps drops and rewatches to the cut, section and shot on screen, writes the sidecar and markers on a copy sequence, and records lessons through self-learn |
| `self-learn` | Lessons (symptom, cause, fix), the user's preferences in their own words and project facts kept as plain files by `knowledge.py`, printed at every edit's intake; correction candidates kept by optional Claude Code hooks; proposed kit changes |
| `variants` | A/B versions as sequences in the same project (`<base> — <variant>`, brief in the sidecar), compared with `diff.py` (cuts, length, opening, music, looks, captions, review scores), one-change ad tests, length cuts, each exported with its profile |
| `voiceover` | Voiceover by measurement: speaking rate and narration windows from the words (`narration.py`), lines sized to them (checked with the `bashcut.align` plugin), text prepared for TTS, English with `tts.*`, Vietnamese with the `bashcut.vieneu-tts` plugin, every take checked against its text, fit to picture, re-takes, dubbing; run by the `voice` sub-agent |
| `stock-images` | Pictures the footage lacks: stock photos and video, emoji, logos, Iconify icons, illustration sets in one style, fetched through the resources plugin with each file's licence recorded, placed with `media_import`, `timeline.place` and Motion keyframes |
| `motion-graphics` | Graphics over footage: whether a sentence needs one, the cheapest tool (native text, `.fcgt` template cards built once with `graphics.*` and reused with `graphics.template.apply`, or the `bashcut.hyperframes` plugin rendering HTML/GSAP outside and importing it with alpha), timing to the word, facts and Lottie from `bashcut.resources`, frames checked at phone size |
| `library` | Reusing the creator's pieces with the `bashcut.library` plugin: look in the library first (titles, looks, presets, stickers, sounds, templates, the brand kit), harvest what an edit made worth keeping after the export gate, prune what is never used, share packs |

Claude Code shows them under the plugin name (`/bcp:setup`); Codex as `bcp-<name>`. The editing skills
(`edit-workflow`, `rough-cut`, `captions-text`, …) follow in BashCutPro#5–#7, once the command catalogue (#3) lands.

**Agents.** Claude Code also gets sub-agents from [`agents/`](agents): `surveyor` (reads the footage for
`footage-survey` and answers in under 450 words), `critic` (judges a draft for `review` without the maker's
reasons, in under 300 words) and `voice` (voices and checks a script for `voiceover`, in under 200 words). Codex has no sub-agents: its skills follow the same brief
themselves.

## Requirements

- `filmcraft-cli` from a BashCutPro source build (`cargo build --release -p filmcraft-cli`) or a release. The
  `setup` skill walks through it.
- For bridge mode, the desktop app started with `filmcraft --control <port>`.
- Claude Code or Codex.

## Install

**Claude Code** (one command each, in a terminal):

```sh
claude plugin marketplace add dongnguyenvie/bashcutpro-agent-kit
claude plugin install bcp@bashcutpro-agent-kit
```

Or inside Claude Code: `/plugin marketplace add dongnguyenvie/bashcutpro-agent-kit`, then
`/plugin install bcp@bashcutpro-agent-kit`. The plugin brings the skills and a `bashcutpro` MCP server whose
launcher, [`scripts/bashcutpro-mcp.sh`](scripts/bashcutpro-mcp.sh), finds `filmcraft-cli` (`FILMCRAFT_CLI`, then
`PATH`, then the usual install places) and picks the mode from `~/.config/bashcutpro/mcp.env`. Then run
`/bcp:setup`, which writes that file. To try a local checkout for one session:
`claude --plugin-dir /path/to/bashcutpro-agent-kit`.

On Windows the launcher (a POSIX shell script) may not start; `/bcp:setup` registers `filmcraft-cli.exe`
directly instead.

**Codex** (macOS, Linux):

```sh
git clone https://github.com/dongnguyenvie/bashcutpro-agent-kit
sh bashcutpro-agent-kit/scripts/install-codex.sh
```

It links each skill as `~/.agents/skills/bcp-<name>` and registers the launcher as the `bashcutpro` MCP server;
`--uninstall` removes both. On Windows, see the `setup` skill.

### Launcher settings

`mcp.env` (or the environment, which wins) holds plain `NAME=value` lines:

| Name | Effect |
|---|---|
| `FILMCRAFT_CLI` | the `filmcraft-cli` binary |
| `BASHCUTPRO_BRIDGE` | `host:port` of the running app: `mcp --bridge` |
| `BASHCUTPRO_PROJECT` | headless: `mcp --project` this `.fcproj` |
| `BASHCUTPRO_DEMO` | `1`: headless on the demo project |
| `BASHCUTPRO_DATA_DIR` | headless: `--data-dir` (user presets) |

With none of the mode names set, the server is headless with an empty project.

## Layout

```
.claude-plugin/plugin.json        plugin "bcp" (skills show as /bcp:<name>)
.claude-plugin/marketplace.json   marketplace "bashcutpro-agent-kit", serving this repository as the plugin
.mcp.json                         the plugin's MCP server "bashcutpro" (scripts/bashcutpro-mcp.sh)
agents/<name>.md                  Claude Code sub-agents (surveyor, critic, voice); skills point Codex at the same brief
skills/<name>/SKILL.md            the skills (Agent Skills format, shared by Claude Code and Codex)
skills/<name>/REFERENCE.md        detail a skill reads on demand (keeps SKILL.md under 250 lines)
scripts/commands.json             FilmCraft command catalogue (copy of BashCutPro bashcut/commands.json); check.py
                                  rejects command ids a skill names that are not in it
hooks/hooks.json                  optional Claude Code hooks (self-learn's correction candidates; off unless BASHCUTPRO_SELF_LEARN=1)
tests/                            unit tests of the kit's scripts: python3 -m unittest discover -s tests
skills/<name>/agents/openai.yaml  Codex policy, only for a user-only skill (disable-model-invocation: true)
scripts/bashcutpro-mcp.sh         finds filmcraft-cli and starts `filmcraft-cli mcp` in the configured mode
scripts/install-codex.sh          Codex setup
scripts/check.py                  checks skills, links, the Skills table and the packaging files
```

## Writing skills

- English instructions; trigger phrases may be in any language users speak (Vietnamese included).
- Frontmatter: `name` (the folder name), `description` (what and when, at most 1024 characters) ending in
  `Triggers: "phrase", "phrase", …`.
- Use FilmCraft command ids found with `command_list`, never BashCut's commands; say what to do and why.
- Only rules that were observed (a measurement, an error, a user's correction), with the number that proves it.
- Run `python3 scripts/check.py` and `python3 -m unittest discover -s tests` before committing. A change to `skills/` raises `version` in
  `.claude-plugin/plugin.json`: Claude Code caches an installed plugin per version.

## License

MIT. See [LICENSE](LICENSE).
