---
name: rough-cut
description: Build the rough cut in BashCutPro by quote: lines found in the transcript with transcript.search, word edges refined from the audio (bashcut.transcript.refineEdges), selects tightened on word edges by tighten.py (fillers, false starts and dead air cut, one bashcut.batch), selects kept with reasons, bashcut.review.run on every output; also long → short clips from a podcast or stream, one sequence per short. Triggers: "cắt thô", "rough cut", "chọn đoạn", "lọc câu hay", "cắt podcast thành short", "highlight", "selects", "cắt giữa chữ", "cut by quote".
---

# Rough cut by quote

You choose by **text**; the transcript's word times give the frames. Never type timestamps from memory or from
SRT lines: tools that let the model write times are off by 0.6–1.5 s (T06 §4). Every time you cut on comes from
a word's `start` / `end` (`transcript.search`, `transcript.inspect`). The ranges below are starting points; choose
within them for this footage.

A rough cut is selection and order only: no music, titles, grade or effects unless the user asks (T06 §4). Be
generous on the first pass and tighten later: a discarded moment is slow to find again (T06 §2). Detail and
examples: `<skill_dir>/REFERENCE.md`.

## Before selecting

1. **Words for each talking file.** With a Whisper build: `bashcut.transcript.generate {items, language, wait: true}`.
   It also moves word edges out of the pauses it measures on the audio (`edgesMoved`, `pauses`): Whisper runs word
   ends late into a pause and starts early. Words from elsewhere (`transcript.set {item, transcript: {language,
   words}}`, ticks; `bcp:footage-survey`): run `bashcut.transcript.refineEdges {items}` once after the import.
   `transcript.models` says which build you have. Words carry no confidence.
2. **Classify the source** (T06 §4): **words** (the content is what is said: talks, interviews, tutorials),
   **reactions** (laughter, surprise: watch the picture; laughter and "clip that" lag the moment they react to) or
   **visual** (demonstrations, sport: the transcript is weak evidence, use the survey's descriptions).
3. **The brief and plan** (project notes, `bcp:edit-workflow`): length, outputs and sections decide what is worth
   keeping.
4. **Recording cues** from the survey: no range starts, ends or runs across a cue; after "cut that", "take two" or
   "làm lại" the dead take is not a candidate. Between two takes of a line the **later one wins** unless you
   looked and the earlier is better; say which in the select's reason.
5. **Restarts and repeated phrases**, including ones the transcript hides (a word over ~1 s long is often two
   attempts merged). A select never holds a phrase said twice; keep the later, complete take.

## The select-by-quote loop

For each moment: `transcript.search {"query": "the first time I opened the app it crashed"}`. It returns the
matching words (ids, times); pick among several hits by context (the later take, the complete sentence).

- **A partial match** means the quote is not there as you remember it: read the words around the hit
  (`transcript.inspect`) and quote what was said. A misheard word is fine; a hit holding one or two of your words
  is not a match, never place it.
- **Sentence edges.** An edge mid-sentence is allowed only when you mean it (a deliberate interruption). Otherwise
  move it to the nearest sentence end (punctuation, or a gap ≥ 400 ms) and search again.
- **Padding: cut on the words, never pad by hand.** In connected speech the next word starts within ~0.1 s: a
  0.1 s pad pulled the neighbouring words in (one ad edit). Cut at the first word's `start` and the last word's
  `end`; extend only into a gap of quiet, and at most half of it. `tighten.py` does exactly this.
- **Gaps as cut points** (T06 §3): ≥ 400 ms of quiet is a clean cut; 150–400 ms needs a look at the picture
  (`render_frame`); < 150 ms is unsafe. Word ends from Whisper-style transcribers run late into pauses: check a
  doubtful edge with a frame or by the next word's `start`.
- **Takes**: default to the last complete take ("people warm up", T06 §3), then confirm by reading or asking; a
  fluent take is not always better.
- **Long lifts**: removing more than 10–20 s at once needs a look (T06 §3): quiet is not empty picture in a
  screen demo.

Write your choices as selects in the plan (project notes) before any edit:

```json
{"selects": [{"id": "S1", "item": "<media id>", "quote": "the first time I opened the app it crashed",
  "from": "<word id>", "to": "<word id>", "start": 15602457600000, "end": 19025798400000,
  "reason": "hook: the problem in one sentence", "evidence": "sentence ends; last complete take of three",
  "status": "kept", "mustKeep": true}]}
```

`status` is `candidate`, `kept` or `rejected` (with the reason); `mustKeep` marks lines the edit cannot lose. Give
`order` when the story order differs from the recording order. Never undo a user's rejection; ask instead.

## Blind second pass (long → short, or many candidates)

Propose about 2× the clips you need (T06 §3): 30–45 % of AI picks are duds. Then judge them blind: a fresh
sub-agent (or you, ignoring your reasons) gets each candidate's text with one sentence of context on each side and
returns a verdict with one sentence why:

- **publish**: stands alone and pays off; `kept`.
- **review**: promising but needs a trim, a different start or the user's eye; stays `candidate` with the note.
- **drop**: fails the standalone test or quote-mines; `rejected` with the reason.

Prefer these tiers to a weighted score (T06 §3). Order by narrative for one video, by strength for a batch of
shorts (T06 §2).

### The standalone test

A clip shown without the rest must make sense (T06 §2):

- no unresolved "he", "this", "that one" pointing outside the clip; no "as I said";
- no long lead-in before the point; setup, turn and payoff are inside;
- it does not stop before the payoff or on a comma;
- a stitch of two ranges never makes a meaning that was not said: do not stitch across a "but" or "however".

## Length

Length follows the moment: setup + turn + payoff, then capped by the platform (T06 §3).

| Kind | Range | What moves it |
|---|---|---|
| vertical short | 15–90 s | one-liners shorter, story arcs longer; the platform's cap |
| topic or chapter clip | 1–6 min | source length and platform |
| sum of selects vs the plan's length | ±10–15 % | report the drift; strict for fixed slots |
| yield from a long source | no quota; often about 1 per 2–10 min | report the candidate count and why you kept N |

Never cut natural speech short to hit a quota or a "sweet spot" (T06 §4).

## Building the cut

**Tighten the selects with `tighten.py`** (standard library; REFERENCE "tighten.py" has every flag). It takes the
words of the whole item and the selects as word ranges in story order, and prints one `bashcut.batch` of
`timeline.place` steps plus a report:

1. Words on the item's own clock: a scratch sequence with the item at 0 (`file.newSequence`, `timeline.place {item,
   track: "V1", frame: 0}`), `file.save`, then write them with the command line (`BASHCUTPRO_CLI` from
   `~/.config/bashcutpro/mcp.env`), never by retyping a tool result: `printf
   '{"id":"sequence.open","params":{"item":<scratch>}}\n{"id":"transcript.inspect","params":{}}\n' | <cli>
   --compact --project <project.fcproj> run - | tail -1 > words.json`. It only reads the saved file (no save, no
   lock), so it runs while the editor holds the project.
2. `"${BASHCUT_PYTHON:-python3}" <skill_dir>/tighten.py --words words.json --item <id> --keep 117-124,103-116,125-171 --fps 30`: a hook
   moved first is just the first range. Inside each range it drops fillers (`--lang en|vi`, `--fillers`, `--protect`
   for a filler that is content) and false starts (a 1–3 word phrase said twice in a row keeps the later; a first
   copy ending a sentence is emphasis and stays), and cuts every pause ≥ `--min-pause` (0.35 s) down to
   `--keep-pause` (0.12 s) of quiet each side. Clips are whole frames; the source in point is exact, so no edge
   lands inside a kept or a neighbouring word, even in connected speech.
3. Read the report before running anything: `cuts`, `cutsPerMinute`, `removed` (each filler and repeat with its
   time), `connectedSpeech` (edges with < 0.15 s of quiet: look at a frame), `shortSpans` (< 0.4 s: often a lone
   word to merge or drop).
4. `command_run` the printed `command` on the output's sequence: one undo step, all or nothing. Save.

| Pace (cuts a minute of output) | Typical | Lever |
|---|---|---|
| Podcast or interview clip | 12–25 (8–15 in a 40 s clip) | `--min-pause` 0.5–0.8 keeps breaths and slows it |
| Talking head, vertical | 15–30, ≥ 70 % of cuts on a word edge | `--min-pause` 0.35, `--keep-pause` 0.1 |
| Tutorial, explainer | 10–20 | measured silences (`bcp:vlog-tutorial`) |
| Over 35 | reads as a jump-cut machine | raise `--min-pause`; keep the pause before a payoff |

Other ways, when tighten.py does not fit (REFERENCE "Other ways to cut"): subclips placed in story order for a
select record you can see in the project, or `transcript.extract` / `transcript.lift` on one placed take (last
range first). A pause with a reaction or a look in it is content: check it with `render_frame` first.

After it, `bashcut.timeline.summary` for the cut list and duration; `render_frame` at doubtful joins (same framing
on both sides is a jump cut to come: `bcp:beat-cut` punch-in or cover footage, never over text). Mark sections with
`markers.addRange {name}`.

Then **G3** (`bcp:edit-workflow`): the duration against the plan's range, N selects, cuts a minute, what was dropped
and why, 4–6 frames. Wait for the user's answer before rhythm, sound and text when they asked to see gates.

**Review.** Every output sequence ends with `bashcut.review.run {profile, sequence}` (`bcp:review`): `cutInWord`
is blocking and points at the clip; the fix is the select's range or `--protect`, then tighten again (at most 2
rounds). A `cutInWord` inside a measured silence is the transcriber stretching a word: run
`bashcut.transcript.refineEdges`, then tighten again.

## Several shorts from one source

FilmCraft has no project derive: **one sequence per short** in the same project. For each kept short,
`file.newSequence {name: "short-03-crash-story", width: 1080, height: 1920, fps}`, then its ranges tightened into
it (`tighten.py` per short, the hook range first); finish each through the stages of `bcp:edit-workflow` (its own
captions and `bashcut.review.run`). A separate file per short when the user wants them apart: `file.saveCopy
{path}` after building, one copy per short. Write the list (short → sequence, selects, length) in the plan.
