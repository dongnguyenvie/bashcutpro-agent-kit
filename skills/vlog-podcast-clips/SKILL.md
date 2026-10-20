---
name: vlog-podcast-clips
description: Recipe for shorts cut from a long podcast, interview, livestream or talk: clips proposed by quote with word-exact edges, the standalone test, a blind second pass, the user picks, one sequence per clip edited as a talking head. Use after bcp:vlog-plan picks podcast-clips. Triggers: "podcast clips", "long to short", "clips from a livestream", "cắt podcast", "cắt clip ngắn từ video dài", "cắt shorts từ livestream".
---

# Podcast clips (long → short)

Reply in the user's language. One long source becomes several shorts, each its own sequence. The selection is the
hard part: the select-by-quote loop is bcp:rough-cut's; this recipe adds the genre's ranges and order. Each clip is
then edited with bcp:vlog-talking-head. Plan with bcp:vlog-plan. A measured reference (shorts from a channel the
user points to) wins over these ranges (T15 §7).

Many recordings with the same treatment: the `podcast-shorts` batch preset (`bcp:batch`) runs this recipe per
recording as a capped agent step, each reviewed with `bashcut.review.run`; pick and polish the best by hand after.

## Ranges

Outputs per clip: vertical → Shorts, TikTok, Reels; a topic clip for YouTube → 1080p landscape.

| Check | Sample range | Why it varies |
|---|---|---|
| Short clip length | 15–90 s; one-liners shorter, stories longer (T06 §3) | the moment sets it (setup + turn + payoff), then the platform cap |
| Topic clip length | 1–6 min (T06 §3) | source length and platform |
| Yield | not a quota: about 1 clip per 2–3 min of source against 1 per 5–10 min (T06 §3, a contradiction) | how dense the talk is; fewer is fine; report why you kept N |
| Candidates | about 2× the clips needed, expecting 30–45 % duds (T06 §3) | a sharp talk has fewer duds |
| Hook | the strongest **complete** sentence, 1.5–3 s (T06 §7) | a cold open (a later line moved to the start) only when the best line is more than about 10 s into the clip |
| Cut edges | on word or sentence edges from `transcript.inspect`, no hand padding: a 0.1 s pad pulls in the next word in connected speech | a trailing reaction or laugh: take a wider quote |
| Clean cut points | gaps of 400 ms or more are clean; 150–400 ms need a look; under 150 ms are unsafe (T06 §3) | music or room noise under the gap |
| Length vs target | within ±10–15 % of the planned length (T06 §3) | a clip that needs its full payoff runs over; say so |
| Pauses, framing, captions | as bcp:vlog-talking-head | — |
| Two cameras: shot dwell | 3–12 s, varied with energy, never random; listener cutaways 2–4 s (T19 §3, §7) | a fast debate cuts sooner; a long answer holds |

## 1. Read and classify the source

1. Transcribe (`bashcut.transcript.generate`, or `transcript.set` with imported word timings), then read words and gaps with
   `transcript.inspect`.
2. Classify it (T06 §4): **words** (trust the transcript), **reactions** (laughs, a heated exchange: listen and look;
   a laugh is a lagging marker of the moment before it) or **visual** (a demo, a reveal: look at frames with
   `render_frame`).
3. Two cameras or a separate recorder: sync them first (bcp:footage-survey).

## 2. Propose by quote, never by typed times

1. Read the transcript and pick about twice the clips you need.
2. Find each by what was said: `transcript.search` with the words as said, then snap both edges to the nearest
   sentence edge (or a word edge with a clean gap) from `transcript.inspect`. Never type raw seconds (T06 §4).
3. Store each as a subclip named with its quote (`clip.makeSubclip`), with the reason (setup, turn, payoff in one
   line), the evidence and the status `candidate` in its Comment (`metadata.set`).

**Standalone test** (T06 §7): no unresolved "he / it / that" pointing outside the clip, no "as I said earlier", the
payoff inside the clip, no stitching across "but / however". A clip that fails is dropped or widened.

## 3. Blind second pass

Hand the candidates to a fresh sub-agent that sees only each clip's text with one sentence of context on each side,
not your reasons (T06 §4). It returns **publish**, **review** or **drop** with a one-line reason. Mark drops
`rejected` with the reason in the Comment. Expect about a third to drop.

## 4. The user picks

Show the table: quote, length, the hook sentence, the verdict, and why you rank it. Ask the strategy gate (G2) in
conversation: "N clips proposed, M recommended", and wait. Mark the chosen ones `kept`.

## 5. One sequence per clip

Per kept clip, a new sequence of the output shape (`file.newSequence`, named for the clip) holding only that range;
for separate deliveries, a project copy per clip (`file.saveCopy`). Edit each as a short:

- Hook: the strongest complete sentence first (the cold-open rule above), then the clip in order.
- Tighten pauses, punch-ins at word boundaries, short caption groups: bcp:vlog-talking-head.
- A landscape source in a vertical output: reframe each shot on the speaker with Motion scale and position
  (bcp:effects) and check it with `render_frame`. Never trust a blind centre crop of a two-shot; when nobody fits,
  use a fitted frame instead (T19 §4).
- A title card or chapter label only when the clip needs context the first sentence does not give.

## Rhythm, transitions and graphics

| What | Sample range | Why it varies |
|---|---|---|
| Framing change | every 4–6 s (T07 §7), by punch-in or a camera switch | a dense argument changes more often |
| Snap punch | 1.1–1.15× on a strong word; 4–6 in a 60 s reel (T08 §3) | the clip's headroom |
| Transitions | hard cuts and punch-ins; 0–1 special transitions per clip (T08 §7) | — |
| Graphics | 0–2 per clip: a keyword on the claim word, a name label at the start (T13 §3: 3–8 a minute is for explainers) | the face carries the clip |

Keyword and name label looks: bcp:captions-text (an installed `.fcgt`, else `graphics.newText`; the vlog library
looks are not ported yet).

## Review notes

- One camera repeats its framing by nature; jump cuts are still fixed with punch-ins.
- Blockers: a clip that starts mid-thought, a cut inside a word, a laugh with its joke cut off. A slightly long
  pause is not.
- `needs_user`: which clips to keep, the speakers' names and titles, permission to post a guest's words, the outputs
  per clip.

## Plan data

- `stages`: `{"voiceover": {"required": false, "why": "the source's own speech"}, "rough-cut": {"rules": ["blind second pass; every clip passes the standalone test"]}, "visuals": {"skill": "bcp:visual-plan", "after": "voiceover", "required": true, "why": "each line gets the speaker, a keyword or a picture"}}`
- `checks`: `clean-start` no clip starts mid-thought; `standalone` the clip makes sense without the source;
  `joke-kept` a laugh keeps its joke; `no-cut-in-word` no cut inside a word.
- `askAtIntake`: `["guestPermission", "outputsPerClip"]`.
