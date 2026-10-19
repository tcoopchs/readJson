# readJson

Lesson files for the stateless reading harness server.

The server reads published lessons from the `lessons/` directory in this repository. It builds
its lesson catalog from the filenames and JSON `lesson_id` values at startup. There is no separate
hand-maintained lesson list or manifest.

## Repository layout

Keep all published lessons directly inside one flat directory:

```text
readJson/
|-- lessons/
|   |-- inference_L4_0001.json
|   |-- inference_L4_0002.json
|   |-- inference_L4_0003.json
|   |-- inference_L4_0004.json
|   |-- inference_L4_0005.json
|   |-- inference_L5_0001.json
|   `-- process_L9_0001.json
|-- drafts/                 # Optional; never served by the server
|-- README.md
`-- LICENSE
```

Configure the server with:

```dotenv
GITHUB_REPO=tcoopchs/readJson
GITHUB_REF=main
GITHUB_LESSON_PATH=lessons
```

Files must be directly inside `lessons/`. The server does not search nested subdirectories.

## Lesson filename format

Every published lesson must use this exact pattern:

```text
<category>_L<level>_<sequence>.json
```

Examples:

```text
inference_L4_0001.json
inference_L4_0002.json
inference_L5_0001.json
connotation_L6_0001.json
denotation_L9_0001.json
```

- `<category>` is a lowercase key configured on the server, such as `inference` or `vocab`.
- `<level>` is a whole-number grade band. It must be numeric, so `L4` and `L9` are valid while
  `L4a` and `L4b` are not.
- `<sequence>` is a positive whole number and should be zero-padded for readability.
- Levels and sequences are sorted numerically. Sequence `0010` comes after `0009`.
- Grade 4 is the baseline band. Grades 5 through 12 continue with the same `L` numbers.
- A category may have as many levels as needed.

The JSON file's `lesson_id` must match the filename without `.json`:

```json
{
  "lesson_id": "vocab_L4_0001"
}
```

Do not rename a lesson after its ID has appeared in a signed student bookmark.

## Grade and horizontal boundaries

The numeric level is the grade band. Grade 4 is the baseline. Every category at every level uses
exactly five sequence slots:

| Sequence | Purpose |
| --- | --- |
| `0001` | Baseline lesson for the grade band |
| `0002` | Horizontal variant A |
| `0003` | Horizontal variant B |
| `0004` | Horizontal variant C |
| `0005` | Horizontal variant D |

The last horizontal at a grade band is `_0005`. The next grade band starts with a new `_0001`:

```text
inference_L4_0001.json    # Grade 4 baseline
inference_L4_0002.json    # Grade 4 horizontal A
inference_L4_0003.json    # Grade 4 horizontal B
inference_L4_0004.json    # Grade 4 horizontal C
inference_L4_0005.json    # Grade 4 horizontal D
inference_L5_0001.json    # Grade 5 baseline
```

Do not create `_0006` or later within a grade band. A student who needs another attempt after
`_0005` stays at that level until the teacher or an authored route moves them, or advances to the
next grade band. The server validates filenames but does not infer or store a student's position
in the sequence.

The current test lessons are:

- `lessons/inference_L5_0001.json` at Grade 5.
- `lessons/process_L9_0001.json` at Grade 9.

## Core and horizontal lessons

Use sequence numbers to distinguish a core lesson from reteaching or horizontal variants at the
same level. The level stays numeric.

```text
lessons/
|-- vocab_L4_0001.json    # Grade 4 baseline
|-- vocab_L4_0002.json    # Grade 4 horizontal A
|-- vocab_L4_0003.json    # Grade 4 horizontal B
|-- vocab_L4_0004.json    # Grade 4 horizontal C
|-- vocab_L4_0005.json    # Grade 4 horizontal D
`-- vocab_L5_0001.json    # Grade 5 baseline
```

`/start?skill=vocab&level=4` opens `vocab_L4_0001.json` because it has the lowest numeric sequence
at that category and level. A lesson's authored exit rules choose the next exact lesson:

- A student who is ready can be routed to `vocab_L5_0001`.
- A student who needs more practice can be routed to `vocab_L4_0002`,
  `vocab_L4_0003`, `vocab_L4_0004`, or `vocab_L4_0005`.

This keeps the student at the same level without advancing them. The AI applies the lesson's exit
rules; the server verifies that the named lesson exists and enforces the pacing gate.

The five-slot boundary applies to every level. If a category needs more horizontal attempts at
one grade band, change this policy deliberately rather than overloading `_0006` and beyond.

## Exit-ticket routing

Every lesson must state its exit choice explicitly in `exit_rules`. The AI does not calculate a
filename. It reads the authored route and fills `{next_file}` from that route.

The standard two-branch rule is:

```json
{
  "decision_rule": "At exit, use routes[0] when got_there is 4 or 5. Use routes[1] when got_there is 0 through 3. Do not choose any other lesson.",
  "routes": [
    {
      "min_got_there": 4,
      "next_level": 6,
      "next_file": "inference_L6_0001",
      "next_means": "The baseline inference lesson for Grade 6.",
      "student_line": "You put most of these facts together on your own. The next reading would be the Grade 6 inference lesson."
    },
    {
      "min_got_there": 0,
      "next_level": 5,
      "next_file": "inference_L5_0002",
      "next_means": "The next horizontal inference lesson at the same Grade 5 level.",
      "student_line": "You have the basic move. The next reading would be another Grade 5 inference lesson at the same level."
    }
  ]
}
```

The rule is hardwired in each JSON file, not inferred by the server:

- Four or five `got_there` results: advance to the next grade band's baseline `_0001`.
- Zero through three `got_there` results: stay at the current grade band and move to the next
  horizontal sequence.

The server validates the exact `next_file` named by the chosen route. If that file does not yet
exist, signing fails and the student cannot receive a broken next lesson. Add the referenced
lesson before publishing a route that points to it.

The current test lessons use `inference_L6_0001` and `inference_L5_0002`, and
`process_L10_0001` and `process_L9_0002`, respectively. Those files are not in this repository
yet.

## Adding a category

Adding a category requires coordinated changes in this repository and on the server:

1. Add the category key and display order to the server's `categories.json`.
2. Add at least one lesson to `lessons/` using that category key.
3. Add entry levels for the category to the server's `onboarding.json`.
4. Commit and push the lesson files here.
5. Restart or redeploy the server so it fetches the new catalog.

Valid category keys use lowercase letters, digits, underscores, and hyphens. Examples include
`inference`, `vocab`, `connotation`, and `denotation`.

The category itself is defined on the server. This repository stores the lesson content, while
the server configuration controls category labels, display order, and Star-score entry levels.

## Adding a lesson

1. Choose its category and numeric level.
2. Choose the next unused numeric sequence at that category and level.
3. Name the file with the required pattern.
4. Set `lesson_id` to the filename without `.json`.
5. Confirm the lesson is published, not a draft.
6. Commit and push the file.
7. Restart or redeploy the server.

Do not place drafts or work in progress inside `lessons/`. A draft lesson causes the server to
reject the whole catalog at startup. Keep unpublished files outside that directory.

## Routing from one lesson to the next

Each lesson's `exit_rules` or schema-v2 `rules.routes` must name an exact destination lesson in
this repository. The AI prints an unsigned exit line for the selected destination:

```text
v0|skill=vocab|level=4|lesson=vocab_L4_0002
```

The student submits that line to the server. The server checks that the category, level, and
lesson exist, signs the ticket, and starts the 3-day pacing gate. The ticket then downloads the
named JSON file.

The destination must match the lesson's actual location and metadata:

- `skill` is the category key.
- `level` is the numeric level.
- `lesson` is the filename without `.json`.

## Publishing

The server does not watch GitHub continuously. Publication is:

```text
Commit and push lesson files to this repository
        |
        v
Restart or redeploy the server
        |
        v
Server downloads and validates the latest catalog
```

Pin the server's `GITHUB_REF` to a commit SHA when a deployment must remain on one known lesson
set. Use `main` when every server restart should immediately receive the latest published files.

## Validation checklist

- [ ] The file is directly inside `lessons/`.
- [ ] The filename follows `<category>_L<level>_<sequence>.json`.
- [ ] The category is configured on the server.
- [ ] The level and sequence are positive integers.
- [ ] `lesson_id` matches the filename without `.json`.
- [ ] The lesson is published, not a draft.
- [ ] Every route names an existing lesson in this repository.
- [ ] The file is valid JSON.
- [ ] Remedial routes keep the student at the intended level.
- [ ] The file has been committed and pushed.
- [ ] The server has been restarted or redeployed.
