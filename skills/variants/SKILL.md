---
name: variants
description: A/B versions of an edit as sequences in the same project (named "<base> — <variant>", each with its brief in the project sidecar), compared with diff.py (cuts, length, opening, music, looks, captions, review scores) and exported each with its own output profile. Hooks and openings A/B, look A/B, length cuts (60 / 30 / 15 s), one-change ad tests. Use when the user wants several versions to compare or test. Triggers: "A/B", "A/B test", "variant", "two versions", "another version", "hook B", "shorter version", "phiên bản khác", "làm 2 bản", "bản ngắn hơn", "thử hook khác", "so sánh hai bản".
---

# Variants

Reply in the user's language. A variant is a **second sequence in the same project**, not a second project: the
footage, bins and lessons stay shared and the versions sit side by side. A revision the user asked for is made in
place (`bcp:edit-workflow`, "Revisions"); a variant is for comparing or testing.

## 1. Make one

Finish, review (`bcp:review`) and save the base first: every variant is measured against it.

1. Find the base sequence's item id (`project.items`, `type` Sequence) and its name.
2. One batch: `project.select {"items": [base]}`, `edit.duplicate {}` (answers `{"items": [new]}`), then
   `clip.rename {"item": new, "name": "<base> — <variant>"}` (an em dash, the variant named for its change:
   `main — hook B`, `main — 30s`, `main — warm look`), and `sequence.open {"item": new}`.
3. Write its brief to the sidecar `<name>.fcproj.bashcut/variants.json`, one entry per variant:
   `{"sequence": "main — hook B", "base": "main", "change": "opens on the result shot instead of the face",
   "why": "test which opening holds past 3 s", "profile": "tiktok", "status": "draft"}`, and one line in the plan
   notes (`project.setNotes {"merge": "variants"}`) naming the variants.
4. Make **only** that change in the copy, with the skill that owns it (`bcp:rough-cut` for the opening,
   `bcp:color-grade` for the look, `bcp:audio-mix` for music), then review the copy like any draft.

## 2. Compare

Save `sequence_inspect` (or `bashcut.timeline.summary` where the build has it) of each sequence to a file, and the
review result of each when there is one, then:

```sh
python3 <skill_dir>/diff.py base.json variant.json [--review-a rb.json --review-b rv.json] --text [--one-change]
```

It reports the length change, cuts added and removed (one frame tolerance), shots added and removed, what plays in
the first 3 s (`--hook N`), music beds, looks (effects per clip), captions and review scores, and `changed`: the
kinds of change found. Anything in `changed` beyond the declared change is a mistake: undo it in the variant.
`--one-change` exits 1 when more than one kind changed.

Show the user the comparison in a few lines plus a frame of each at the moment that differs (`render_frame` with the
variant's sequence open): the opening for a hook test, a skin-heavy frame for a look test.

## 3. What to vary

| Test | The one change | Keep identical |
|---|---|---|
| Hook / opening | the first 1–3 s: line, shot or text | everything after the hook |
| Look | the grade (one adjustment layer or Lumetri preset) | the cut, the sound |
| Length | 60 → 30 → 15 s: drop whole sections from the plan, keep the hook and the CTA | the order of what stays |
| CTA | the CTA wording or card | the rest |
| Music | the bed | the cut (re-check cut sync with `bcp:beat-cut` only if music leads) |
| Voice | the voice or take | the words |

- **Ads** (`bcp:vlog-product-ad`): one change per variant, always. Naming a winner needs real numbers: several
  hundred to about 1,000 impressions per variant over 3–7 days; `bcp:outcomes` reads the platform's retention once
  they are published.
- **Length cuts** are not a one-change test: their `changed` lists `cut` and maybe `hook` when the opening moved;
  the hook and CTA must survive every length.

## 4. Export

One export per variant, each from its own sequence, named `<project>-<variant>.mp4` and made with that variant's
output profile: `bashcut.profiles.apply {"profile", "path", "sequence": <variant item>, "wait": true}` where the build
has profiles, else `sequence.open` then `file.exportMedia` with the platform's size, loudness and caption mode
(`bcp:vlog-publish`). Set the variant's `status` to `exported` with the file path in the sidecar.

## Report

The variants made (name, change, profile), what diff.py found beyond the change (should be nothing), the review
scores side by side, the files exported, and for a test: what to measure and for how long.
