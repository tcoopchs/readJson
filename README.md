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
4. `<stage>` is an authored instructional stage from `1` through `3` inside that grade. Stages 4-8 are
   reserved: a new stage may be appended above `3` later, never inserted between two existing ones.
5. `<sequence>` is the lesson position from `0001` through `0008` inside that stage.
6. The target horizontal is six lessons in each `(category, grade, stage)` rung: four carry a reader
   through it and sequences `0005`-`0006` are retry text.
7. `lesson_id` must exactly equal the filename without `.json`.
8. Student-facing labels use `Band <grade>.<stage>`, such as `Band 5.1`. Do not show a grade or IRL
   label to a student.
9. Write `advance`, `retry`, and `stopped` so every `next_file` names a lesson that already exists.
   While the set is `incomplete`, the server does not follow those destinations. It serves the next
   existing lesson in that band and holds at the last one. Do not invent a route to a missing file.
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
| `<stage>` | Authored progression stage within the grade | `1` through `3` authored; `4`-`8` reserved |
| `<sequence>` | Lesson within the rung | `0001` through `0008` |

Examples:

```text
inference_band_5_1_0001.json
inference_band_5_1_0008.json
inference_band_5_2_0001.json
process_band_9_3_0004.json
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

The target progression cell is a rung:

```text
6 lessons in one category, grade, and stage
```

The set boundaries are declared in `lessons/curriculum.json`. The target size is a default, not a
hardcoded server constant. Each set lists its actual sequences and is marked `complete` only when
all of them exist:

```json
{
  "skill": "inference",
  "grade": 5,
  "stage": 1,
  "expected_sequences": [1, 2, 3, 4, 5, 6],
  "status": "complete"
}
```

An `incomplete` set does not use central progression. The default `on_incomplete_set` policy is
`hold_and_alert`. Finishing a lesson in that set serves the next file that already exists in the
same category, grade, and stage. Mastery does not leave the band. Finishing the last existing file
holds the student and reports the curriculum gap. After the next file is added and the server is
restarted, the same ticket serves that file. The set stays `incomplete` until every sequence in
`expected_sequences` exists. An authored route is used only when the protocol explicitly selects
`authored_route`. This prevents a partially authored set from treating its current last lesson as
the true end of the horizontal.

Within a rung, sequences run in order:

```text
inference_band_5_1_0001.json
inference_band_5_1_0002.json
...
inference_band_5_1_0006.json
```

Sequences `0001`-`0004` carry a reader through the rung. Sequences `0005` and `0006` exist so that a
push-back has text that has not been displayed. They are never the reason a student moves.

A reader moves along one ladder per category. Grade and stage are labels on that ladder, not separate
axes:

```text
inference: 3.1 -> 4.1 -> 4.2 -> 4.3 -> 5.1 -> 5.2 -> 5.3 -> ...
```

Up and down are the only moves. A move never changes the category: a student in inference Band 5.2
moves to inference Band 5.3 or back to inference Band 5.1, never to main idea.

A move is decided by the evidence window, not by finishing a rung or by a single lesson:

```text
up     2 of the last 3 lessons in the rung at 4 or more of 5 items with no help
down   2 of the last 3 at 3 or fewer, or any anchor item that needed a help or reached tell
stay   every other case; take the next sequence in the rung
```

At most one move per day. Two down-moves in a row hold the ladder and alert a teacher instead of
moving a third time. A stopped session never moves. Band `3.1` is the floor: it is empty in
onboarding so no student starts there, but a down-move may serve it.

### Moving down

A down-move lands on the middle of the previous rung in the same category:

```text
current Band 5.3, window says down
-> Band 5.2, sequence 0003
```

The server computes the middle from the previous set's actual `expected_sequences`. Six lessons use
sequence `0003`; five use `0003`; four use `0002`; one uses `0001`. If the current stage is the first
stage of a grade, the previous rung is the last authored stage of the grade below:

```text
current Band 5.1, window says down
-> Band 4.3, sequence 0003
```

If the student is already at the floor, `on_floor` governs. Set to `restart_set`, it serves the first
unused sequence of the current rung so the retry has text that has not been displayed. If the rung is
exhausted, hold and alert a teacher rather than repeating a passage:

```text
current Band 3.1, window says down, sequences 0005-0006 already used
-> hold, teacher alert with the item pattern
```

Do not apply the original IRL placement rule again after a step-down. The student has already been
placed; this is remediation inside the authored ladder.

### The window needs memory, and the ticket carries it

The server is stateless. It holds no history, no database, no cookies, and no student record, so it
cannot know "2 of the last 3" on its own. The continuation the server mints after a verified ticket
carries one field:

```text
carry=<stage>.<lessons-in-rung>.<clears>
```

Reset it on any move. A missing or unreadable carry means the first sequence of that rung; losing the
link costs at most two lessons of evidence and never moves a student up. A replayed carry buys a
repeated lesson, never a skipped one. The carry field is not a data model: nothing may be built on it
that needs history longer than three lessons.

To decide "no help" and "anchor item," the ticket must also report per-item results. `got_there`
counts unaided and helped together and cannot separate them. The anchor item is the first item in the
lesson: it is the one item whose help disqualifies the session, so `an=1` means the reader did the
opening move alone.

During sparse-content development, a step-down destination must already exist. If it does not,
point `retry` at the current lesson rather than inventing a missing file. That stored field keeps
startup from failing. The live hold does not read it.

## Completion routing

Every source lesson must contain finite, explicit `advance`, `retry`, and `stopped` destinations.
The compiler writes them into `rules.server_routes`. Each `next_file` must already exist, and
`next_irl` must match that file's grade. `stopped.next_file` names the current lesson.

The published protocol is `hold_and_alert`. While a set is `incomplete`, the server does not follow
`advance` or `retry`. It serves the next existing lesson in the band and holds at the last one.
Adding that next file and restarting the server lets the same ticket serve it.

Mark the set `complete` only when every sequence in `expected_sequences` exists. On a complete set,
`advance_min_got_there` (currently 4) is the per-lesson clear threshold: one lesson clears at 4 or
more of 5 items. Clearing does not by itself move a student; the three-lesson window above decides
the move. A stopped session returns the current lesson.

Those three destinations are the fallback used only when `on_incomplete_set` is `authored_route`.
Write `advance` as the first lesson of the next stage, `retry` as the next sequence in this stage,
and `stopped` as this lesson. Point a field at an existing lesson when the preferred file is not
authored yet.

The unsigned completion line is:

```text
v2|from=<lesson_id>|done=<items-with-a-result>|u=<unaided>|h=<helped>|m=<mercy>|o=<open>|an=<0-or-1>|carry=<carry>
```

`u+h+m+o` must equal `done`, and `an` is 1 only when every anchor item was unaided. The `carry` value
is filled in by the server when it serves the lesson; the lesson copies it unchanged. A stopped
session adds `|stop=1`. The AI reports only the current lesson and counts. It must not
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

Forty compiled lessons under `lessons/` are live content. The inference ladder is complete from the
floor through stage 4.3; the rest is prototype coverage:

| Band | Category | Authored | Set |
| --- | --- | --- | --- |
| 3.1 | inference | 6 | complete |
| 4.1 | inference | 8 | complete |
| 4.2 | inference | 6 | complete |
| 4.3 | inference | 6 | complete |
| 3.1 | main idea | 6 | complete |
| 5.1 | inference | 2 | incomplete |
| 6.1 | inference | 1 | incomplete |
| 7.1 | main idea | 2 | incomplete |
| 9.1 | process | 2 | incomplete |
| 10.1 | process | 1 | incomplete |

Band 3.1 is the floor and is not authored yet. Until it exists, `on_floor` stays `hold_and_alert`, so
a student who cannot hold 4.1 is held and reported rather than served a rung that is not there.

The remaining empty legacy placeholders were archived under `drafts/legacy_placeholders/`. Do not
publish them or recreate empty files in `lessons/`.

## Adding a lesson

1. Choose one of the eight category keys.
2. Determine the whole-number IRL grade.
3. Choose an authored stage from 1 through 3. Do not open a new stage until the rungs below it exist.
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
- [ ] The stage is from 1 through 3, unless a reserved stage is being appended above an existing one.
- [ ] The sequence is from 0001 through 0008, and the rung targets six.
- [ ] The rung's four required sequences and two retry sequences are both present.
- [ ] At band 5 and above the passage and items are human-written; below band 5, `source.drafted_by` and the reviewed `source.text_status` are recorded.
- [ ] `lesson_id` equals the filename without `.json`.
- [ ] `meta.reader.reading_level` equals the filename grade in the source.
- [ ] Student-facing text uses a Band label or no label, never a grade or IRL phrase.
- [ ] The generated runtime file contains no `reader` or `irl_grade` metadata.
- [ ] The source and generated file both use `meta.status: published`.
- [ ] The source has five items unless a documented exception changes the prototype target.
- [ ] `advance`, `retry`, and `stopped` name existing lessons.
- [ ] `next_irl` matches the destination filename grade.
- [ ] `stopped.next_file` names the current lesson.
- [ ] The set stays `incomplete` until every expected sequence exists. `advance` and `retry` are
      stored fallbacks; they do not choose the next lesson while the set is incomplete.
- [ ] `script_overrides.near_copy_2` is present. The shared instructions tell the tutor to say it.
- [ ] The set is listed in `curriculum.json` with its actual sequences and completeness status.
- [ ] The compiler `--check` passes.
- [ ] No empty placeholder is placed in `lessons/`.

## Publishing

Commit and push both lesson sources and generated runtime files, then restart or redeploy the
server. The server downloads a snapshot at startup and does not poll GitHub continuously.

Pin `GITHUB_REF` to a commit SHA when a deployment must remain on one known lesson set. Use `main`
when every restart should receive the latest published files.
