---
name: vlog-hook-script
description: Write a vlog's words: story options, 3-5 hooks checked against real shots, the script as beats sized to the speaking rate, on-screen text and CTA. Use for a hook, script or boring opening. Not for voicing or TTS (bcp:voiceover), caption styling (bcp:captions-text) or finding the angle (bcp:vlog-ideate). Triggers: "write a hook", "write the script", "boring opening", "viết hook", "câu mở đầu", "mở đầu nhàm", "viết kịch bản", "viết lời đọc", "CTA".
---

# Hook and script

Reply in the user's language; write viewer-facing words in the video's language (the brief). Read the brief and
plan in `project.notes` first and use the chosen recipe's structure (bcp:vlog-plan). Numbers are sample ranges
(T02 = script notes, T10 = voiceover notes); a **measured** rate of this speaker or voice always replaces them.

## 1. Who owns the sound

Before writing a word, decide per stretch who owns the sound: real speech, action sound (a sizzle, a crowd), music,
silence or narration (T02 §4). Narration is a choice; **none** is valid when the footage speaks for itself.

- Where real speech is and its gaps: word times from `transcript.inspect`; a gap is the time between one word's end
  and the next word's start. Windows for narration are gaps at least one short sentence long.
- **Real speech first**: build from the person's own lines (keep the last clean take of a repeat); voiceover only
  for the gaps. Cut narration that describes what the picture shows (T02 §4), and narration that says what the
  person says next or just said ("Mình chỉ bạn làm từng bước nhé" before the presenter's own "mình sẽ hướng dẫn từng
  bước" said it twice).

## 2. Story options (create mode)

Write **2–3 story options** before the script (T00 §3, T02 §3): the spine in one sentence, which sections and shots
carry it, its hook, what it leaves out; recommend one. `directed` mode: one. `revision` mode: keep the `frozen`
sections' lines word for word. Store them in the plan's `options` and the choice in `decisions`.

## 3. The hook

A promise in the first seconds: one line on screen (a hook title, bcp:captions-text; two short lines with the
keyword alone on one) and, if someone speaks, the same idea said. Write **3–5 options of different kinds** (T02 §3,
§7) and pick against the best shot and, once a cut exists, the opening frames (`render_frame`).

| Kind | Example |
|---|---|
| cost / time + question | "48H Ở ĐÀ LẠT HẾT BAO NHIÊU?" |
| result first | "VIDEO NÀY DO AI DỰNG TRONG 5 PHÚT" |
| verdict as question | "3 TRIỆU CÓ ĐÁNG?" |
| number of things | "5 QUÁN PHẢI ĂN Ở QUẬN 4" |
| surprise / contrast | "QUÁN VỈA HÈ NGON HƠN NHÀ HÀNG?" |
| a strong line from the footage | the speaker's own sentence, moved to the start |

| Check | Sample range | Why it varies |
|---|---|---|
| Hook window | short-form 1–3 s; long-form up to about 15 s (T02 §3, sources contradict); a tool demo opens on the output for 5–7 s with its own sound | platform, length, whether the viewer chose to watch |
| Hook text | about 6 words or fewer per frame; at most about 60 characters in 9:16 (T14 §3) | font size, hold |

- **Text and speech in the opening say the same thing.** A title asking one question while the voice says another
  reads as two messages (a critic flagged it in a one-prompt ad): write the on-screen hook from the spoken line.
- The hook promises only what the body pays off, and the CTA closes it. Never open with a greeting or "hôm nay
  mình…". The pair is the plan's `promise` `{hook, payoff}`.

## 4. Budget from the measured rate

Size every line to its window with a **measured** rate, never a fixed table:

- **The creator speaks**: units per second of speaking time from `transcript.inspect` (syllables for Vietnamese,
  characters for Chinese, Japanese, Korean, else words); take p10 / p50 / p90 over phrases.
- **A synthesized voice** (bcp:voiceover): voice one test line and measure it the same way.
- Budget at p50, margin from the p10–p90 spread (T02 §7), not a fixed ×0.85.

Before any measurement, a sanity check only (T02 §3): Vietnamese articulation rate 4.7–5.3 syllables a second
(Bradlow, Interspeech 2019; Pellegrino et al., Language 2011); overall rate with pauses 200–245 syllables a minute
(read audiobooks, Vu et al., ACL 2025). No study measures vlog speech directly. English 2.0–3.5 words a second (150
wpm common, 210 measured for one creator); Chinese 3–4 characters a second.

A line that does not fit: cut or split its job, or move it. **Never speed the voice up to fit** (T02 §4); a mild
stretch up to about 1.1× only after rewriting failed, slow-down 0.82–0.95× (T10 §3). 0.3–1 s of silence at a line
end is often right (T10 §7).

## 5. The script as beats

| Beat | Section | Owner | Window and budget | Line (as heard) | Job | ON SCREEN | Source |
|---|---|---|---|---|---|---|---|
| b1 | hook | VO | 0–2.4 s, ~9 syllables | "Hai ngày Đà Lạt, hết bao nhiêu?" | claim (promise) | the pull at 120 fps + hook title | — |
| b4 | place 2 | real speech | C0031 0:40–0:46 | (the seller's line) | context | the seller, price board | C0031 0:41 |
| b5 | place 2 | VO | 3.1 s, ~12 syllables | "Bốn lăm nghìn một tô, rẻ nhất chuyến đi." | interpretation | price tag "45K" | price board, C0033 0:02 |

- **Job** per line: context, causal link, foreshadow, interpretation, transition, claim, CTA. A line without a job
  is deleted (T02 §4).
- **ON SCREEN**: what the picture shows and any text. Text repeats the key word or number, never the whole sentence;
  captions or a card carry a line, not both (T13 §4).
- **Source** for every fact (number, price, name, place, superlative): a frame, the user, or a link with its date.
  No source: cut the claim or ask (T02 §4).
- One fact or feeling per sentence; numbers as said ("bốn lăm nghìn"), digits on screen. Write for the ear.

## 6. Counterfactual review

Before showing the script (T02 §4): **delete each beat** in your head (still works → cut it); **mute the voiceover**
(lines that only describe the picture go, and lines the live speech beside them already says); **audio only** (does
it make sense?); **quote the weakest line exactly** and fix or remove it; check `promise.hook` against the last beat.
After the rough cut, check the pair on the edit: the close must answer the opening; if the cut changed either end,
update `promise` with a reason.

## 7. Into the plan, then the script gate

Write `beats` [{id, section, text, job, onScreen, source}] (text = the exact words heard) and the `promise` into the
plan; bcp:visual-plan turns beats into pictures. Show hook options, story options and script, and ask for G4
before any voice is made. After voiceover and editing, compare each beat with the words heard
(`transcript.inspect`): a beat with under about 0.6 of its words heard is rewritten or cut; fix the beats or the
edit, not the measurement. Lines of real speech and voiceover chain with about 0.14 s between them.

## On-screen text and CTA

- Captions from the words with `bashcut.captions.create` (≤ 20 cps, 2 lines, ≤ 42 characters a line; 20 on
  vertical) per bcp:captions-text; hook text inside the profile's safe area (`bashcut.review.run` checks it); titles and cards as bcp:vlog-plan says (the vlog library
  looks wait for `.fcgt` templates).
- CTA: one action (save, follow, comment a question, buy), held 1–6 s by platform and CTA (T07 §3). Examples, not
  rules: Shorts and TikTok often "follow", Reels "lưu lại", YouTube "xem video tiếp theo".
- Labels and sponsorship: bcp:vlog-plan §4.
