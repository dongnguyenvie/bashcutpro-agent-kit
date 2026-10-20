---
name: vlog-ideate
description: Find a vlog's angle before planning: footage first, 3–5 angles each backed by real shots, research only when it changes the choice, three hooks per angle screened against shots, a decision table, then the brief in the project notes. Use before bcp:vlog-plan when there is no clear angle or brief. Triggers: "what video can I make", "video ideas", "brainstorm", "làm video gì", "ý tưởng video", "góc kể", "nên kể gì", "footage này làm được gì".
---

# Ideate: find the angle

Reply in the user's language. This skill decides **what the video is about** and writes it down as the brief;
bcp:vlog-plan then decides how to make it. The footage limits which angles are honest: an idea the footage cannot
show is the most common failure of a footage-first editor (T01 §4). Numbers are sample ranges (T01 = ideation
notes); the user's own history and what the footage holds come first.

## 1. Read what is known

- `project.notes`: an existing brief; keep its `confirmed` fields, ask only about the rest.
- `doc_inspect`: the media (clips, lengths, shape, fps), capture dates from the files, what is already transcribed.
- `bashcut.template.list`: a series format the creator already saved (its slots show what each episode needs).
- `bashcut.profiles.list {seconds}`: the outputs the creator can pick, with each one's frame, loudness and file size.

## 2. Angles from the footage first

1. **Look.** Frames from each clip (bcp:footage-survey: `file.exportFrame` with `target: "source"` at a few
   times, tiled into a sheet). Note shot size, move, subjects, on-screen text, best moment, as facts.
2. **Listen.** For clips with speech, the words (`bashcut.transcript.generate` with the whisper build, else imported
   with `transcript.set`; read them with `transcript.inspect`). Strong lines, numbers said aloud, a question, a
   surprise; find each with `transcript.search` so its time is real, not guessed. Sound with no words:
   `bashcut.audio.loudness {clip}` (`silent`, or under about −35 LUFS: room tone only, so the angle needs a voice or
   music).
3. **Group** by place, time (one day, one evening, a route), people and speech moments.
4. **Derive 3–5 angles**, each from evidence you can name: "48 h in Đà Lạt: 6 places, prices said in 4 clips" or
   "the noodle stall: 3 min of the cook talking, one strong line at 01:12". Fewer when the footage is narrow (T01
   §3: 3–10 candidates, fewer when footage exists).

No footage yet (to be shot or generated): 5–10 angles from the prompt and research (T01 §3).

## 3. Research only when it changes the choice

Search the web only when a fact or trend would change which angle wins, and only with a tool that can search.
Never invent trends, numbers or "what is viral".

| Step | Sample range | Why it varies |
|---|---|---|
| Sub-questions | 1–4 (T01 §7) | one for a clear topic; more for a niche the user does not know |
| Trend lookback | 7–30 days (T01 §3) | none for evergreen topics; short for news |
| Depth | 8–12 items per source, deeper only for high stakes (T01 §3) | stop early when sources agree |
| Evidence floor | 2 or more independent sources (T01 §3) | engagement floors depend on platform size; do not copy them |
| Own history | at least 4 of the creator's videos to compare; confidence low under 10 (T01 §3) | only when the user gives their numbers |

Every idea carries its **source** (a clip and second, the user's words, a URL with its date) and, for a trend, **why
now**. Nothing corroborated: write **"nothing solid"** and what you looked at. Never pad a list (T01 §4).

## 4. Screen each angle with 3 hooks

Per angle, 3 hooks of different kinds (a number, a question, a contrast, the result first, a strong line from the
footage), each checked against an **actual shot**: the clip and second that would play under it (T01 §7). Drop an
angle when no hook has a shot behind it, or keep it and list the missing shots. No scores: composite "virality"
scores read as precise but measure nothing (T01 §4); compare in words.

## 5. Decision table

Show 2–3 angles and recommend one, with the reason:

| Angle | Best hook (with its shot) | Evidence and source | Missing | Length range | Outputs |
|---|---|---|---|---|---|
| … | "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" over C0012 at 3.2 s | 6 places, prices said in 4 clips | no night shot | 45–75 s | tiktok, reels |

Ask at most 1–3 questions, only what changes the result and cannot be read from the footage: platform, length,
audience (T01 §3), and for a new project the language of speech and captions (no default; offer the user's writing
language first). Each as a choice with your recommendation. A length range is a choice, not a rule: the platform's
cap is the only hard limit (T17 §3).

## 6. Write the brief

A JSON block in the project notes (`project.setNotes`, keeping the rest of the notes). Each field is
`{value, status, source}`: `stated` (the user said it), `inferred` (read from footage or prompt), `confirmed`
(approved at the brief gate). `outputs` are profile ids (`tiktok`, `reels`, `shorts`, `youtube`, `youtube-4k`,
`facebook-square`, or the creator's own): the edit reviews and exports each with `bashcut.review.run {profile}` and
`bashcut.profiles.apply`.

```json
{"goal": {"value": "a cost guide for a 2-day trip", "status": "inferred", "source": "prices said in 4 clips"},
 "audience": {"value": "students planning a cheap weekend", "status": "stated", "source": "user"},
 "outputs": {"value": ["tiktok", "reels"], "status": "inferred", "source": "41 of 44 clips portrait"},
 "angle": {"value": "48h in Đà Lạt, what it cost", "status": "inferred", "source": "decision table, A"},
 "lengthSeconds": {"value": {"min": 45, "max": 75}, "status": "inferred", "source": "6 places × 6–9 s"},
 "ideas": [{"angle": "48h cost guide", "hooks": ["48H Ở ĐÀ LẠT HẾT BAO NHIÊU?"], "evidence": "C0012 3.2 s", "chosen": true},
           {"angle": "the best cheap food", "missing": "close-ups of 3 dishes"}],
 "references": [{"url": "<link the user gave>", "learn": "cost overlays", "notToCopy": "their music and look"}]}
```

Write only what you know. For a reference, write what to learn **and what not to copy** (T01 §4).

**Brief gate (G1)**: show angle, length, outputs, audience and what is missing with a few frames; wait for the
user. Approved fields become `confirmed`. Then continue with bcp:vlog-plan.

## Avoid

- Ideas the footage cannot show; facts in a hook or title the video does not show (T01 §4).
- Unsourced statistics presented as grounded; generic industry averages instead of the creator's own history.
- A fixed story spine chosen before looking at the material; random template hooks; scores presented as truth.
