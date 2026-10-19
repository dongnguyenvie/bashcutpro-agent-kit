---
name: vlog-publish
description: Finish a reviewed vlog for posting: platform facts, one export per output at its own loudness target, another shape as its own sequence, a no-music version, cover candidates checked at phone size, YouTube chapters from section markers, post title, caption and hashtags. Use when the edit passed review and the user wants to export or post. Triggers: "export for TikTok", "post to YouTube", "make a cover", "xuất video", "đăng TikTok", "đăng Reels", "đăng YouTube", "hashtag", "ảnh bìa", "chương YouTube".
---

# Publish

Reply in the user's language. The brief in `project.notes` lists the outputs; the first is the primary platform.
Platform facts change: quote them with their date, check the platform's help page when a limit matters, and when a
fact is unknown say so instead of filling it in (T17 §4).

## 1. Platform facts

| Fact | YouTube (16:9) | Shorts | TikTok | Reels |
|---|---|---|---|---|
| Frame | 1920×1080 | 1080×1920 | 1080×1920 | 1080×1920 |
| Title | 100 characters (hard); about 40 show on mobile, 60 on desktop (T17 §3) | 100 (hard) | — | — |
| Caption / description | 5000 characters (hard) | 5000 | 2200 (hard, Content Posting API) | 2200 (hard) |
| Hashtags | all ignored past 60; tags 5–12 (T17 §3) | as YouTube | no official cap; 3–5 (T17 §3) | 5 at most (Instagram, Dec 2025) |
| Interface over the frame | — | bottom and right side | bottom about 24 % (caption bar), right side | bottom and right side |

- **Length**: the moment sets it; the platform's cap limits it. **Never trim to a "sweet spot"**: they contradict
  (Shorts 30–45 s in one source, "avoid 30–45 s" in another; TikTok 21–34 s or 15–30 s; T17 §3). Mention one only
  as context when asked, with its source.
- **Loudness**: each output exported to its own target, never one number for all (T11 §3, T17 §3); the targets and
  how to check them are bcp:audio-mix (nothing in FilmCraft measures loudness read-only).
- **AI disclosure**: each platform has an upload toggle for AI-made or altered content.

## 2. Before exporting

bcp:review passed on the last draft: no error left. Ask for the draft gate (G5): length, outputs, what was left
on purpose; wait for the user.

## 3. One export per output

`file.exportMedia` per output with `path`, the size, `loudnessLufs` at that output's target, and captions burned
in (`burnCaptions`) or as a sidecar file (`captionSidecar` srt or vtt). Vertical apps usually get them burned in;
YouTube landscape often a sidecar the viewer can switch off (T09 §7). Long exports: `wait`, or follow `jobs.list`.

- **Same shape** (Reels, TikTok, Shorts): one export each from the same sequence; only the name and target change.
  The edit must fit the strictest output first (interface zones, cap).
- **Another shape** (a 16:9 YouTube version of a vertical edit, a 4:5 feed version) or a **shorter cut**: its own
  sequence, in a project copy (`file.saveCopy`) or a new sequence of that shape (`file.newSequence`); reframe each
  shot, re-place the text, review again, export. Never squeeze one edit into both shapes (T17 §4).
- **A version without the music**: the same cut with voice and effects only, so the creator can add the
  platform's own sound. Offer it for TikTok, Reels or Shorts when the edit has a music bed; mute the music track for
  the export (bcp:audio-mix), name it `<name>-nomusic`, normalize it too. When the cut was timed to the beat, say a
  new track will not match the cuts.
- Bit rate only for a measured reason.

## 4. Cover

1. Pick 2–3 candidate frames from the edit: the hook's subject large, the hook text readable, no fake interface
   (T17 §4). Look with `render_frame`.
2. Write each at the outputs' cover shape: `file.exportFrame` at that time (16:9 for YouTube, 9:16 for the vertical
   apps; a frame of the other shape comes from that shape's sequence).
3. **Look at phone size**: view each at about 320 px wide. The text must still read and be at least about 1/8 of the
   frame's height; 3–5 big words, fewer is often better (T17 §3: tested at 320 px; ≤3 words in another source).
4. Report the chosen time and files. The user sets the cover in the app; YouTube takes the 16:9 still as a custom
   thumbnail.

## 5. Chapters (YouTube)

One `markers.addChapter` per section start, named for the viewer, from the plan's sections. YouTube's rule: the
first at 00:00, at least 3 chapters, each at least 10 s. Fix a failing rule in the edit's sections (merge a short
one, rename), not in the text. Write the list ("00:00 Hook") for the description from the markers in `doc_inspect`.

## 6. Title, caption and hashtags

In the video's language, inside the caps above.

| Item | Style (sample range) | Why it varies |
|---|---|---|
| YouTube / Shorts title | the hook's number or question inside the visible part (T17 §3) | the device most viewers use |
| TikTok / Reels caption | the hook line, one detail, a question or CTA, front-loaded: the feed shows a line or two | where the "more" cut falls |
| Hashtags | topic, place, format; TikTok and Reels 3–5, YouTube tags 5–12 (T17 §3) | a niche needs fewer, broader ones |
| YouTube description | the chapter list; sources and credits only when the user asks | — |

- Only claims with a source: prices, addresses, names and numbers the video shows or the brief sources (T01 §7).
- Disclosure: never burn an AI, stock or "minh hoạ" label into the video (it feels unnatural). When generated shots
  or voices are placed, tell the user to switch on the platform's AI label at upload. A sponsored video says so in
  its first seconds, on screen, in the user's wording.
- Credits: none on the video or in the post by default; when the user asks, list licensed music and stock in the
  description, never on the picture.

Report per output: the file, length, size and loudness target; the cover files and time; the chapter list and any
rule it fails; title, caption and hashtags per platform; which facts came from this table (and need a check) and
which are ranges you chose.
