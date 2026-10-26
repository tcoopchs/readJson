# readJson

Published lesson JSON files for the stateless reading harness server.

This document is the authoritative contract for filenames, instructional placement, student-facing
bands, source layout, compilation, and routing. Any AI or human authoring lessons in this repository
must follow it exactly. If an older example, draft, or server document conflicts with this contract,
this document wins.

## Instructions for an AI author

1. The filename is `<category>_band_<grade>_<stage>_<sequence>.json`.
2. Use only these category keys: `vocab`, `main_idea`, `inference`, `process`, `text_structure`,
   `literary_text`, `authors_craft`, `argument_evidence`.
3. `<grade>` is the whole-number IRL grade, from `1` through `12`. Use the Star report's IRL, never
   its Scaled Score or Grade Equivalent.
4. `<stage>` is an authored instructional stage from `1` through `8` inside that grade.
5. `<sequence>` is the lesson position from `0001` through `0008` inside that stage.
6. The target horizontal is eight lessons in each `(category, grade, stage)` cell.
7. `lesson_id` must exactly equal the filename without `.json`.
8. Student-facing labels use `Band <grade>.<stage>`, such as `Band 5.1`. Do not show a grade or IRL
   label to a student.
9. Later lessons are selected only by the server from the lesson's `advance`, `retry`, or `stopped`
   route. Do not invent a route to a file that does not exist.
10. Edit the source in `lessons/src/`, compile it into `lessons/`, and commit both.

If a requested change conflicts with these rules, stop and coordinate the server and lesson changes.

## Repository layout

Published runtime lessons stay directly inside `lessons/`. Authored sources stay directly inside
`lessons/src/`.

```text
readJson/
|-- lessons/
|   |-- curriculum.json                    # set boundaries and completeness
|   |-- inference_band_5_1_0001.json       # generated runtime lesson
|   |-- inference_band_5_1_0002.json
|   `-- ...
|-- lessons/src/
|   |-- inference_band_5_1_0001.source.json
|   `-- ...
|-- drafts/
|   `-- legacy_placeholders/                # archived; never served
|-- README.md
|-- DESIGN_RULES.md
`-- LICENSE
```

The server downloads files only from the configured `GITHUB_LESSON_PATH`, which is `lessons` in the
production repository. Nested directories under `lessons/` are not served. `lessons/src/` is never
served.

## Star placement

Star reports three different measures. They have different jobs:

| Star measure | Use |
| --- | --- |
| Instructional Reading Level (IRL) | Choose the instructional grade and curriculum band. |
| Scaled Score (SS) | Record the test result and track growth or benchmark status. |
| Grade Equivalent (GE) | Do not use for lesson placement. It is a norm comparison, not an IRL. |
| Percentile Rank (PR) | Report the student's relative standing. Do not use for placement. |
| ZPD | Suggest an independent-reading range. Do not use for lesson routing. |

Use the whole-number part of IRL for the curriculum grade:

```text
IRL 4.2 -> grade 4 -> Band 4.1 is the entry stage
IRL 4.7 -> grade 4 -> Band 4.1 is the entry stage
IRL 5.0 -> grade 5 -> Band 5.1 is the entry stage
IRL 5.1 -> grade 5 -> Band 5.1 is the entry stage
```

IRL 4.7 is still grade-4 instructional material. Grade 5 begins at IRL 5.0. The decimal is a test
measurement, not a separate curriculum grade.

The student-facing selector uses opaque Band labels, such as `Band 5.1`. It must not show `Grade 5`,
`5th grade`, `IRL 5.1`, or any copy that tells a student their reading is below their school grade.

## The band contract

Every filename has exactly this shape:

```text
<category>_band_<grade>_<stage>_<sequence>.json
```

| Part | Meaning | Valid examples |
| --- | --- | --- |
| `<category>` | One fixed lesson-type key | `inference`, `process`, `main_idea` |
| `band_` | Fixed marker for the student-facing band scheme | `band_` |
| `<grade>` | Whole-number IRL grade | `3`, `5`, `9`, `12` |
| `<stage>` | Authored progression stage within the grade | `1` through `8` |
| `<sequence>` | Lesson within the horizontal stage | `0001` through `0008` |

Examples:

```text
inference_band_5_1_0001.json
inference_band_5_1_0008.json
inference_band_5_2_0001.json
process_band_9_8_0004.json
```

`Band 5.1` means grade-5 instructional content, stage 1. It does not mean IRL 5.1 exactly. The
grade controls the reading load; the stage controls authored progression inside that grade.

The JSON `lesson_id` is always the filename without `.json`:

```json
{
  "lesson_id": "inference_band_5_1_0001"
}
```

## Horizontal and vertical progression

The target progression cell is a horizontal:

```text
8 lessons in one category, grade, and stage
```

The set boundaries are declared in `lessons/curriculum.json`. The target size is a default, not a
hardcoded server constant. Each set lists its actual sequences and is marked `complete` only when
all of them exist:

```json
{
  "skill": "inference",
  "grade": 5,
  "stage": 1,
  "expected_sequences": [1, 2, 3, 4, 5, 6, 7, 8],
  "status": "complete"
}
```

An `incomplete` set does not use central progression. The default `on_incomplete_set` policy is
`hold_and_alert`: a student who reaches the last authored lesson is held there and the curriculum
gap is reported. An authored route is used only when the protocol explicitly selects
`authored_route`. This prevents a partially authored set from treating its current last lesson as
the true end of the horizontal.

Within a horizontal, sequences run in order:

```text
inference_band_5_1_0001.json
inference_band_5_1_0002.json
...
inference_band_5_1_0008.json
```

A student may advance before all eight lessons are exhausted if they meet the mastery rule. The
eight lessons are the full practice pool, not a requirement to repeat material after mastery.

Vertical movement follows stages first, then grades:

```text
5.1 -> 5.2 -> ... -> 5.8 -> 6.1
```

Every vertical move keeps the same category. A student in inference Band 5.2 moves to inference
Band 5.3, not to main idea or to an unrelated grade.

### Completing the last lesson without mastery

If a student completes the last lesson in the set and still does not meet the advance rule, do not
force them upward. Move them down to the middle of the previous progression:

```text
current Band 5.3, last lesson completed without mastery
-> previous Band 5.2, sequence 0004
```

The server computes the middle from the previous set's actual `expected_sequences`. Eight lessons
use sequence `0004`; five use `0003`; seven use `0004`; one uses `0001`. If the current stage is the
first stage of a grade, the previous progression is the last authored stage of the grade below:

```text
current Band 5.1, last lesson completed without mastery
-> Band 4.8, sequence 0004
```

If the student is already at the bottom band supported by the catalog, restart at the beginning of
that band:

```text
current lowest Band, last lesson completed without mastery
-> lowest Band, sequence 0001
```

Do not apply the original IRL placement rule again after a step-down. The student has already been
placed; this is remediation inside the authored progression.

The server does not need a cross-lesson counter. It derives the next lesson from the current
lesson's category, grade, stage, and sequence plus the manifest. A stopped session resumes the
current lesson and does not trigger the step-down.

During sparse-content development, a step-down destination must already exist. If it does not,
point `retry` at the current lesson rather than inventing a missing file.

## Completion routing

Every source lesson must contain finite, explicit `advance`, `retry`, and `stopped` destinations.
The compiler writes them into `rules.server_routes`. The server chooses the route.

The unsigned completion line is:

```text
v1|from=<lesson_id>|done=<completed-items>|got_there=<unaided-or-helped>
```

A stopped session adds `|stop=1`. The AI reports only the current lesson and counts. It must not
name or choose a destination.

Routes use `next_irl` for the target band grade. The filename supplies the target stage and sequence.

```json
{
  "advance": {
    "next_file": "inference_band_5_2_0001",
    "next_irl": 5,
    "next_means": "The first lesson in the next inference stage.",
    "student_line": "You have the move. The next reading is another inference lesson."
  },
  "retry": {
    "next_file": "inference_band_5_1_0002",
    "next_irl": 5,
    "next_means": "The next inference lesson in this stage.",
    "student_line": "The next reading is another inference lesson in this band."
  },
  "stopped": {
    "next_file": "inference_band_5_1_0001",
    "next_irl": 5,
    "next_means": "This same lesson, so it can be finished."
  }
}
```

Every destination file must already exist. Do not publish a route to a planned lesson.

## Onboarding bands

The server's `onboarding.json` lists exact entry lessons for student-facing Band keys. A key such as
`5.1` displays as `Band 5.1` and points to the `_0001` entry for that category and stage.

An empty `entries` object means that band is visible but has no authored lesson for that category.
The server must not substitute a different grade or stage.

## Current content status

Only the eight compiled lessons under `lessons/` are live content. They are prototype coverage, not
a completed eight-lesson horizontal:

| Band | Category | Authored |
| --- | --- | --- |
| 5.1 | inference | 2 |
| 6.1 | inference | 1 |
| 7.1 | main idea | 2 |
| 9.1 | process | 2 |
| 10.1 | process | 1 |

The remaining empty legacy placeholders were archived under `drafts/legacy_placeholders/`. Do not
publish them or recreate empty files in `lessons/`.

## Adding a lesson

1. Choose one of the eight category keys.
2. Determine the whole-number IRL grade.
3. Choose an authored stage from 1 through 8.
4. Choose the next unused sequence from 0001 through 0008.
5. Create `<category>_band_<grade>_<stage>_<sequence>.source.json` in `lessons/src/`.
6. Set `lesson_id` to the filename without `.json`.
7. Set `meta.reader.reading_level` to the whole-number grade.
8. Set `meta.status` to `published` before the lesson enters `lessons/`.
9. Write five items for the prototype lesson and follow `DESIGN_RULES.md`.
10. Rebuild the runtime JSON.
11. Update `lessons/curriculum.json` and reference the lesson from a route only after the generated
    file exists.

## Building lessons

From the readingHarness repository:

```bash
uv run python scripts/build_lessons.py \
  --source-dir /path/to/readJson/lessons/src \
  --output-dir /path/to/readJson/lessons
```

Check generated files:

```bash
uv run python scripts/build_lessons.py \
  --source-dir /path/to/readJson/lessons/src \
  --output-dir /path/to/readJson/lessons \
  --check
```

Do not edit generated runtime files by hand. The compiler removes the authoring `reader` block,
`irl_grade`, and other placement-only metadata from the student-facing JSON.

## Validation checklist

- [ ] The filename uses `<category>_band_<grade>_<stage>_<sequence>.json`.
- [ ] The category is one of the eight fixed keys.
- [ ] The grade is a whole number from 1 through 12.
- [ ] The stage is from 1 through 8.
- [ ] The sequence is from 0001 through 0008.
- [ ] `lesson_id` equals the filename without `.json`.
- [ ] `meta.reader.reading_level` equals the filename grade in the source.
- [ ] Student-facing text uses a Band label or no label, never a grade or IRL phrase.
- [ ] The generated runtime file contains no `reader` or `irl_grade` metadata.
- [ ] The source and generated file both use `meta.status: published`.
- [ ] The source has five items unless a documented exception changes the prototype target.
- [ ] `advance`, `retry`, and `stopped` name existing lessons.
- [ ] `next_irl` matches the destination filename grade.
- [ ] The set is listed in `curriculum.json` with its actual sequences and completeness status.
- [ ] The compiler `--check` passes.
- [ ] No empty placeholder is placed in `lessons/`.

## Publishing

Commit and push both lesson sources and generated runtime files, then restart or redeploy the
server. The server downloads a snapshot at startup and does not poll GitHub continuously.

Pin `GITHUB_REF` to a commit SHA when a deployment must remain on one known lesson set. Use `main`
when every restart should receive the latest published files.
