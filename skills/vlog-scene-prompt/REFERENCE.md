# Scene prompt reference

Sections moved from `<skill_dir>/SKILL.md` to keep it short; read the one a step names.

## Duration Rules

- Choose by playable content, not text length: count beats, lines, actions, emotional turns, reaction pauses,
  location changes, camera moves and the ending breath. 30 s is the maximum per prompt.
- Under 15 s when it fits (6, 8, 12 s). 16–30 s only for longer dialogue, several people reacting, a complete
  emotional curve, one-take drama blocking, montage progression or a scene that would feel rushed; never stretch a
  simple beat.
- Longer stories keep the requested scope (highlight, causal clip sequence, or a question when hard limits clash).
  Novel excerpts: the workload tiers in `style_patterns.md`, below the requested coverage; a long passage alone needs
  no approval round.
- Past 1300 characters (≤15 s), 2400 (16–24 s) or 3000 (25–30 s, soft; 4000 absolute), every extra detail must
  improve stability, emotional clarity, space, sound or performance timing, or prevent a model failure.
- Leave the reaction and ending breath: key lines or peak action end 1–2 s before the end unless an abrupt end is
  asked for. Time follows dramatic weight; in short prompts cut events before cutting the reaction.
- No fixed dialogue word ceiling: dense, overlapping or urgent dialogue can stay when line order, lip-sync, breaths,
  reactions and the ending still play. Estimate by local pace; simplify camera and secondary action before cutting
  lines; a real conflict is stated, with a split or a question before changing key lines.

## Continuation Workflow

When the user says continue, next segment, next shot, "the first is good, write the second", or follows up after
approving a prompt. Rules: `Continuation and Clip-Bridging Workflow`, `Character Consistency Bible` and `Scene Spatial
Continuity Bible` in `<skill_dir>/references/style_patterns.md`, after `continuity_director_contract.md`. In short:

- Continue from the previous **story state**, not by habit from its tail frame; choose the bridge (new size and
  angle, match on action, or a new shot group for a finished mini-arc). The tail frame only when exact posture,
  blocking, damage or object position matters.
- Keep identity (age, face, hair, clothing, injury or makeup, emotional residue, body position), setting (layout,
  light direction, weather, time, palette, key objects, sound bed) and key props.
- Emotion progresses, never replays (shock → denial, action, numbness, anger or collapse); one main event or turn per
  15 s.
- Restate only the anchors needed; give fresh descriptions and reference prompts only for a new character, place,
  costume or injury state, or key prop; otherwise say to reuse the existing references.
- Continuous short-film mode keeps a character bible and scene sheet with an anchor budget: 4–6 identity anchors for
  the lead, 3–5 for an important supporting character, 4–6 space and light anchors per recurring scene, 1–2 for
  background groups; temporary state (held or placed props, missing accessories, wet or injured, position, travel
  direction, voice, emotional residue) is tracked apart and causally needed state overrides the budget. Trim
  decorative identity before causality, direction, prop state, key dialogue or the ending reaction. Print the bible
  only when it helps.
- A new direction from the user is followed; a bare "continue" takes the most natural consequence.

```text
【Story diagnosis】
Visible change in this segment and duration risk:
【Cinematic adaptation strategy】
Performance, cut points and camera choices:
【Continuation check】
End state of the previous segment:
Emotional progression in the next segment:
Continuity notes:
【Reference asset status】   (only when the path or a new anchor needs it)
Reused / bridge / new character, scene, prop references:
【Final video prompt for the next segment】
Overview:
```

## Output Format

Workshop by default: diagnosis and strategy short and correctable, then the current path's deliverable; no empty
sections.

```text
【Story diagnosis】
Emotional core:
Visual core:
Structure:
Duration:
Trade-offs and additions:
【Cinematic adaptation strategy】
【Final video prompt】
Overview:
```

Reference-first stage 1 replaces the final prompt with 【Reference image plan】 (needed now, not generated separately)
and 【Reference image prompts】 (type and purpose, prompt); after the images exist, use the reference-driven shape in
`reference_first_video_workflow.md`.

Final-prompt components, only those the scene needs: length and structure (in `Overview`, e.g. "an 18-second
continuous emotional dialogue"), related context, shot number or timeline, shot size and focal length, angle and
movement, subject and composition, light and atmosphere, performance, micro-reactions, dialogue / inner monologue /
voice-over, sound design, ending, and negative constraints only for scene-specific risks.

## Visual Reference Image Prompts

Optional stills that anchor identity, setting, costume, product, props or atmosphere before video; the user may skip
them. How references and video text divide control: `reference_first_video_workflow.md`; field standards, types and
counts: `Visual Reference Image Prompt Patterns` in `style_patterns.md`. Never a full reference set and a full
self-contained video prompt together by default.

- Character references fix identity, not fashion: 4–6 recurring identity or costume anchors plus one emotional
  baseline from the field menu, more only when the current state depends on it. A **single-character reference shows
  only that person**: no other person, hands, hugging, holding, protecting or looking at someone named.
- Scene references: 4–6 topology and light anchors that affect blocking (layout, depth layers, exits, action path,
  obstacles, source light, materials, era, palette); `no people` for a clean plate.
- Key props only when the object drives the story. Most scenes need 1–2 references, complex period, product or large
  scenes 2–3. A relationship / two-shot reference only when height, distance, blocking or chemistry must be
  controlled.
- Continuation or split clips update a reference only when the visible state changes (costume, wet, dusty or injured,
  hair, new prop or place, a clearly different emotional baseline).
- Typical sets: emotional close-up → character; dialogue or intimacy → characters plus scene when space matters;
  product or person texture film → subject plus environment; period drama → costume plus scene; large scene → lead
  plus crowd environment; object-led memory → prop plus scene.

## Anti-Patterns and Red Flags

Do not:
- storyboard prose sentence by sentence or keep exposition with no screen equivalent;
- cram several turns into 30 s or put the key line at the last instant without reaction time;
- replace a plot-changing spoken fact with "the other person delivers the news";
- stack camera moves, lens changes, light jargon, slow motion and cuts without a dramatic job each;
- reset face, costume, injury, held object, screen direction, layout, light or emotional residue between clips;
- produce every reference type by default, or a second person inside a single-character reference;
- repeat full static descriptions in a reference-driven prompt, or treat the first frame as one fixed size, angle and
  composition for the whole clip;
- import a planned object or state the selected image does not clearly show;
- squeeze a horizontal two-shot, group, wide action or landscape into 9:16 without re-blocking;
- treat reference-driven and no-reference prompts as interchangeable;
- use labels like "cinematic feel", "premium look", "epic" instead of concrete action, light source, sound,
  composition and timing;
- hide an overloaded scene in dense fragments to meet the limit: cut events or split.
