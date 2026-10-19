---
name: outcomes
description: Learn from how a published video actually performed: read the platform's audience retention export (YouTube Studio, TikTok, Facebook) that the user downloaded, map drops and rewatches onto the exported sequence with outcomes.py (the cut, the section, what was on screen), mark them on a copy of the sequence, tie each to a cause on the frame, and record lessons through self-learn. Files the user provides only; nothing fetched from accounts. Triggers: "retention", "audience retention", "why did viewers leave", "analytics", "how did the video do", "drop-off", "tỉ lệ giữ chân", "người xem bỏ đi", "video chạy thế nào", "xem số liệu video", "outcomes".
---

# Outcomes

Reply in the user's language. A retention curve says **when** viewers left; the edit says **what** was on screen
then. Together they turn "the video flopped" into a lesson the next edit uses. Privacy: only files the user gives
you (an analytics export they downloaded); never log in, scrape or fetch from their accounts.

## 1. Gather

- **The export**: YouTube Studio → the video → Analytics → Engagement → Audience retention → export (CSV with
  "Video position (%)" and "Absolute audience retention (%)"); TikTok or Facebook retention exports (seconds and a
  viewers / retention column). Ask which file and which published video it is.
- **The edit that was published**: open the project, open the sequence that was exported (for a variant, its own
  sequence, `bcp:variants`), save `sequence_inspect` (or `bashcut.timeline.summary`) to a file. A video re-cut after
  publishing: use the version that was posted (a copy or the draft file's sequence), or the mapping is wrong.
- **Length**: a percent-position export needs the published video's length; the sequence gives it, `--duration`
  overrides when the upload was trimmed.

## 2. Map

```sh
python3 <skill_dir>/outcomes.py retention.csv --sequence seq.json --project /abs/film.fcproj \
  --video "launch-v1" --markers-out /abs/outcome-markers.json --text
```

It prints retention at 3 s, 30 s and the end, every **drop** (a fall of at least 3 points in 2 s and three times the
video's usual decline; the first 3 s are the hook figure, not a drop) and **rewatch** (a rise), each with the nearest
cut within 1 s, the section marker and the clips on screen, and writes the findings to
`<name>.fcproj.bashcut/outcomes/<video>.json`. Few viewers (under ~1,000 views) make a noisy curve: say so and treat
a single drop as a question, not a finding.

To see them on the timeline without touching the edit: duplicate the sequence (`project.select`, `edit.duplicate`,
`clip.rename` to `<base> — outcomes`), open it, then run the marker batch (`command_batch` with the file's
`commands`: `markers.add`, red for drops, green for rewatches).

## 3. Explain

For each drop, look before you conclude: `render_frame` just before and after the time, and read the words there
(`transcript.search` or the captions). Usual causes, in the order to check:

| On screen at the drop | Likely cause |
|---|---|
| a cut to a new shot or section | the promise of the hook paid off or dropped; a slow section start |
| a long hold, a list, an explanation | pacing: the same picture too long, nothing new to see |
| an intro card, logo, "subscribe" ask | a delay before the content |
| music change or silence | energy drop |
| text appearing over the face or off the safe area | the viewer could not read or see it |

A rewatch usually marks something worth more of: a reveal, a fast moment, a number on screen read twice.
Compare the hook figure with the platform's norm the user knows or earlier outcomes in the sidecar; across
several videos, the same kind of drop is the real lesson.

## 4. Learn

- `--learn` records each drop at a cut as a **proposed** lesson (tags `outcomes`, `pacing`) through
  `bcp:self-learn`'s `knowledge.py`, or counts the existing one as seen again. Then, with what the frames showed,
  rewrite its cause and fix (`knowledge.py update-lesson ID --cause … --fix … --status active`) once you and the user
  agree on the cause.
- A preference the user states while reading the curve ("intros are too long for my audience") goes in as a
  preference with their words.
- For a variant test, compare the curves of the variants at the changed moment (`bcp:variants`), not the whole video.

## Report

The figures (3 s, 30 s, end), the two or three biggest drops with time, what was on screen and the cause you see,
the rewatches, the lessons recorded or updated, and what the next edit should do differently.
