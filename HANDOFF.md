# Handoff — Band 4.1 inference

State as of commit `68e78a0` on `main`. Band 4.1 inference is authored, validated, compiled, and
published. Two items must still happen before a student can use it, and one of them is blocking.

## Still to do

### 1. Cold-chat test (blocking for quality, not for serving)

No session has been run against the compiled files. `DESIGN_RULES` 8.8 requires a full session per
lesson: correct answers, each named misconception, a blank answer, the help ladder, `tell` and
say-back, an early stop, and a prompt-injection attempt. This is the only check on the half of the
lesson the compiler cannot verify — whether the tutor improvises, leaks an answer, or invents a
destination.

Test the compiled file, not the source:

```text
lessons/inference_band_4_1_0001.json   (then 0002-0008)
```

Pass criteria: the tutor shows one part and one item at a time; a miss stays on the item through
help[0], help[1], tell, and say-back; no help line states the answer; the say-back terminates after
two near-copies; a stop prints the stopped line; the finished line is exactly
`v1|from=inference_band_4_1_000N|done=<n>|got_there=<n>` with no destination, signature, name, or
student data.

Record the result per lesson. Anything the tutor invents is a source defect to fix, not a prompt to
tighten.

### 2. Onboarding entry (blocking for access)

`server/config/onboarding.json` in `readingHarness` still reads:

```json
{"key": "4.1", "label": "Band 4.1", "entries": {}}
```

Until that changes, none of the eight lessons is selectable. The diff:

```json
{"key": "4.1", "label": "Band 4.1", "entries": {
  "inference": "inference_band_4_1_0001"
}}
```

That is a server-config change plus a restart, not a lesson change. It belongs in a separate commit
in the `readingHarness` repository so the lesson repo and the served config never disagree.

## Also outstanding

- **Human sign-off on the adapted passages.** Lessons 0001-0005 and 0007 are adapted under
  `DESIGN_RULES` 2.5, which requires a person to approve the text. They were produced by an AI and
  have not been reviewed. Each carries a one-line `source.adaptation` note naming what changed.
- **Measured readability is recorded per lesson** in `reader.why_this_level` (FK 5.3-7.6, all inside
  the grade 4-5 band). Re-measure if a passage is edited; do not relabel to fit a score.
- **Two documented length exceptions**: 0006 part 1 is 95 words and 0008 part 2 is 96, both
  verbatim excerpts. Extending either would add material no item uses.
- **Where mastery goes.** The set is complete, so a student who masters 0008 is held at the ceiling:
  the next set in the skill does not exist. Decide `inference 4.2` (same grade, next stage) or
  `inference 5.1` (next grade, already authored as prototype) before the band runs in front of
  students.

## Verification already passing

```bash
validate_lesson.py --strict --src-dir lessons/src --lessons-dir lessons \
    lessons/src/inference_band_4_1_*.source.json   # 0 errors, 0 warnings, corpus pass clean
build_lessons.py --check                            # exit 0
```
