---
name: vlog-plan
description: Start any vlog or short video: route the brief to the right recipe (travel, food, daily, review, ad, talking head, podcast, tutorial, explainer, news, promo), write the plan into project notes, hand to bcp:edit-workflow. Use first. Not for finding an angle (bcp:vlog-ideate) or the edit (bcp:edit-workflow). Triggers: "make a vlog", "plan a vlog", "shot list", "làm vlog", "dựng vlog", "một prompt ra video", "lên kịch bản vlog", "cần quay những gì".
---

# Plan a vlog

Reply in the user's language. The `vlog-*` skills are **recipes**: what one kind of vlog keeps (structure, hook,
text, sound and look intent) and **sample ranges** from published practice, each with why it varies. The numbers
are starting points, not settings: survey the footage, choose a value inside a range, and write it into the plan with
the reason. Two folders of the same genre can and should get different plans. Going outside a range is fine when the
footage or idea earns it: write the value, the reason and `"deliberate": true`.

How to cut, caption, mix and grade is the kit's other skills (bcp:edit-workflow and the skills it names); a
recipe says what to aim for. Citations such as (T07 §3) point at BashCut's analysis notes the ranges came from; RC is
the Reelcrew / AgentVid study of 30 explainer and promo videos (measured 2026-10-07).

**Priority of numbers** (T15 §7): the user's instruction → what the footage can hold → a measured reference (a
creator or video the user pointed to, measured with bcp:style-study) → the recipe's ranges. A reference replaces
the recipe's range for every value it measures. Name it in the plan.

**Library looks are not ported.** BashCut's vlog pack (hook, section, price, CTA, verdict, time-stamp and news text
styles, stickers, four transitions) waits for `.fcgt` (BashCutPro graphics template) conversions. Where a recipe names
a look ("a section chip", "a price tag"), build it with bcp:captions-text / bcp:motion-graphics: an installed
template (`graphics.template.list`, then `graphics.template.apply` with its values) when one exists, else plain
`graphics.newText`.

## 0. Read what exists

- `project.notes`: the brief and plan JSON blocks, if any (bcp:edit-workflow owns their shape). No brief and no
  clear angle in the prompt: run bcp:vlog-ideate first. A plan in `revision` mode: change only the sections the
  user named; leave `frozen` ones alone.
- `doc_inspect` / `sequence_inspect`: media, sequences, what is already cut.
- Gates (G1 brief, G2 strategy, G3 rough cut, G4 script, G5 draft) are asked in the conversation; never decide one
  is approved yourself.

## 1. Pick the recipe

The brief's angle chooses the recipe, not the other way round (T01 §7).

| Signals in the footage or the ask | Recipe |
|---|---|
| a trip, a city, places, a route, "đi đâu", "ở đâu", "48h ở" | bcp:vlog-travel |
| eating, cooking, a restaurant, a street stall, "quán", "món" | bcp:vlog-food |
| a day, a routine, "a day in my life", study or work with me | bcp:vlog-daily |
| a product judged: unboxing, comparison, "có nên mua", "đáng tiền không" | bcp:vlog-product-review |
| a video that sells one thing: ad, UGC, "quảng cáo", "video bán hàng", "TVC" | bcp:vlog-product-ad |
| one person to camera: opinion, story time, tips | bcp:vlog-talking-head |
| shorts cut from a long podcast, interview or livestream | bcp:vlog-podcast-clips |
| a screen recording, an app or tool demo, "cách làm", step by step | bcp:vlog-tutorial |
| a topic explained with cards, numbers and a voice, little or no footage | bcp:vlog-explainer |
| news or documentary from photos, archive, source screenshots, "tin nóng", "phóng sự" | bcp:vlog-news |
| energy and identity, no sale: brand hype, showreel, motion comic | bcp:vlog-promo |

Read the chosen recipe in full; its **Plan data** goes into the plan (§3). Two fit (a food stop inside a trip): take
the one the *whole* video is about and borrow single moves from the other. None fits: the nearest, and say so.
Words (hook, script, CTA) are bcp:vlog-hook-script; shots the footage lacks, bcp:vlog-scene-prompt; posting,
bcp:vlog-publish.

## 2. Intake and survey

One round of at most 4 questions on what the prompt and brief leave open: **where it is posted**, **how long**, for a
new project **the language** of speech and captions (no default; offer the user's writing language first), and the
recipe's `askAtIntake`. No answer: decide, mark the field `inferred` with the reason; never ask again later.
Defaults when the user does not care: vertical → TikTok, Reels, Shorts; landscape → YouTube.

1. Sequence in the output's shape: `file.newSequence` (1080×1920 vertical, 1920×1080 landscape, the footage's fps).
2. Survey with bcp:footage-survey: what each clip shows (shot size, move, subjects, best moment, written to
   `metadata.set` Description so plan rows can match them), source shot lengths, fps, speech and its words
   (`transcript.generate` with the whisper build, else words imported with `transcript.set`), the speaking rate.
3. Punch-in headroom per clip: source size ÷ sequence size; beyond 1× the picture is upscaled.

## 3. Write the plan

A JSON block in the project notes (`project.setNotes`; keep everything else in the notes). Write it before the
rough cut and keep it current, so work resumes from the notes alone.

- `recipe`: `"vlog-<x>"`; `promise`: `{hook, payoff}`, the question the opening raises and the line that closes it
  (first version from the angle; words by bcp:vlog-hook-script).
- `stages`: the recipe's deviations per stage (`required`, `why`, `skill`, `rules`); a pointless stage gets
  `{"required": false, "why": …}`.
- `checks`: the recipe's checks that apply, at most 8, `{id, text}`.
- `sections`: one per part of the structure, each with a length *range* from recipe and footage and the reason
  ("3 places with good footage, 1 with two clips → 4 sections of 6–9 s"). Mark each in the edit with a named
  `markers.addRange` so the user and review see the structure.
- **Establish or hook** (T03 §3), in `decisions` with why. *Hook first*: the strongest moment, line or number in
  the first 1–3 s; short-form and anything scrollable. *Establish first*: the widest placing shot; narrative scenes,
  travel arrivals, long-form the viewer chose.
- `shots` (T03 §4): one row per shot the viewer must see, not per clip: `{id, section, purpose, size, move,
  mustShow, targetSeconds, source}`; `size` ECU, CU, MCU, MS, MWS, WS, EWS or insert; `move` static, pan, tilt, push,
  pull, track, orbit, handheld, zoom, crane; `source` footage, stock or generated. Neighbours change size, angle or
  subject; two alike need a reason, three usually mean merge. About runtime ÷ average shot rows (45–60 s holds 10–14
  shots); key rows only.
- `ranges`: per value you will check, the range, its source and the reason.

```json
{"mode": "create", "stage": "story", "recipe": "vlog-food",
 "promise": {"hook": "45K for this bowl — worth it?", "payoff": "Yes, if you come before 7 — save it"},
 "sections": [{"id": "hook", "lengthSeconds": {"min": 1.5, "max": 2.5}, "reason": "the pour is 1.8 s at 120 fps"}],
 "shots": [{"id": "s1", "section": "hook", "purpose": "the noodle pull, steam visible", "size": "CU",
            "move": "static", "mustShow": ["noodles"], "targetSeconds": 1.8, "source": "footage"}],
 "decisions": [{"text": "Hook first: the pull, not the shop front — vertical feed, the bite is the promise"}],
 "ranges": {"maxShotSeconds": {"min": 2, "max": 3, "source": "food recipe (T07 §3)", "reason": "bites, one 4 s hero hold"}}}
```

## 4. Shared by every recipe

The recipes do not repeat these. Check them on the edit with bcp:review (clip lengths from `sequence_inspect`,
word times from `transcript.inspect`, frames with `render_frame`).

| Check | Sample range | Why it varies |
|---|---|---|
| Monotony | 6+ shots in a row with length variation (CV) under ~0.15 read flat (T07 §3) | a calm run on purpose is fine; say so |
| Pattern interrupt | a new beat every 10–30 s short-form, 30–90 s long-form (T07 §3) | sources contradict; "change" may be a cut or a new idea |
| Payoff / CTA hold | ≥1 s, up to 4–6 s for a CTA (T07 §3) | platform and CTA |
| Dead air | cut silences over about 1.5 s (T11 §3); one held ~2 s silence before a payoff, once (T07 §3) | — |
| Music under the voice | 5–18 dB under speech (T11 §3) | less when music carries it; more for dense information, a soft voice, vocals |
| Length | the platform's cap is the only hard limit; "sweet spots" contradict (T17 §3) | the moment sets it; never trim to a sweet spot |
| Text hold | about letters ÷ 15 + 1–1.5 s (T09 §3) | longer on busy backgrounds |

- **Loudness is per output, never one number**: each export takes its platform's target (bcp:vlog-publish).
  `bashcut.audio.loudness` measures the timeline and `bashcut.review.run {profile}` checks it per output
  (bcp:audio-mix).
- Vietnamese text needs a font with every tone mark (bcp:captions-text). The brand (palette, fonts, logo) sets the
  look when there is one.
- Nothing generated, stock or AI is labelled on the video (news is the exception); AI disclosure is the platform's
  upload toggle. Sponsorship is said in the first seconds, on screen, in the user's wording.
- Captions: `bashcut.captions.create` at ≤ 20 cps, 2 lines, `maxChars` 42 landscape or 20 vertical (with
  `captions.setStyle {size: 40, margin}` above the platform band); word-by-word highlight with
  `bashcut.captions.wordStyle` (bcp:captions-text).
- Transition kinds and their lengths: bcp:effects.

## 5. Strategy gate, then coverage

1. Show the plan in 4–8 sentences plus the section table (T00 §3): hook and the establish-or-hook choice, sections
   and ranges, shot rows, each chosen value with its reason, what is missing. Check it carries one message and the
   payoff answers the hook, it fits the brief, each `inferred` field is still a fair guess, and the recipe's
   checks are in the plan. Ask for G2 with a few frames attached and wait.
2. **Coverage**: match each shot row to a clip as placed, found (a described clip fits) or missing. Missing: offer,
   in order, a cutaway from the footage, a punch-in on a wider shot within its headroom, a stock picture
   (bcp:stock-images, `source: stock`), a generated shot (bcp:vlog-scene-prompt, given the row and its
   neighbours so it cuts in). A gap found later at G3 goes back to the survey or effects once per row, not in a
   loop.
3. **Not shot yet**: give the missing rows as a checklist to film (what, how long, which angle).

## 6. Hand over

Set the plan's `stage`, then hand over to bcp:edit-workflow from the rough cut on; it applies the plan in
one `bashcut.batch` per stage (the cut from bcp:rough-cut `tighten.py`), names the skill per stage and ends
with `bashcut.review.run` on every output sequence. Where a kit skill asks for a value (cut rate, caption grouping,
punch-in, music level), choose inside the plan's range and say why. If the cut shows a range was wrong, change the
plan with a reason instead of forcing the edit. Finish with bcp:vlog-publish.

Report: the recipe, the outputs, sections and ranges with reasons, what was left on purpose, and what the user still
has to decide.
