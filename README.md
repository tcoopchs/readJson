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
|   |-- inference_L1_0001.json
|   |-- inference_L1_0002.json
|   |-- inference_L2_0001.json
|   |-- vocab_L1_0001.json
|   `-- vocab_L1_0002.json
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
inference_L1_0001.json
inference_L1_0002.json
vocab_L2_0001.json
connotation_L3_0001.json
denotation_L3_0001.json
```

- `<category>` is a lowercase key configured on the server, such as `inference` or `vocab`.
- `<level>` is a positive whole number. It must be numeric, so `L1` and `L2` are valid while
  `L1a` and `L1b` are not.
- `<sequence>` is a positive whole number and should be zero-padded for readability.
- Levels and sequences are sorted numerically. Sequence `0010` comes after `0009`.
- A category may have as many lessons and levels as needed.

The JSON file's `lesson_id` must match the filename without `.json`:

```json
{
  "lesson_id": "vocab_L1_0001"
}
```

Do not rename a lesson after its ID has appeared in a signed student bookmark.

## Core and remedial lessons

Use sequence numbers to distinguish a core lesson from reteaching or horizontal variants at the
same level. The level stays numeric.

```text
lessons/
|-- vocab_L1_0001.json    # core lesson
|-- vocab_L1_0002.json    # reteach variant A
|-- vocab_L1_0003.json    # reteach variant B
|-- vocab_L1_0004.json    # reteach variant C
|-- vocab_L1_0005.json    # reteach variant D
`-- vocab_L2_0001.json    # next level
```

`/start?skill=vocab&level=1` opens `vocab_L1_0001.json` because it has the lowest numeric sequence
at that category and level. A lesson's authored exit rules choose the next exact lesson:

- A student who is ready can be routed to `vocab_L2_0001`.
- A student who needs more practice can be routed to `vocab_L1_0002`,
  `vocab_L1_0003`, or another Level 1 variant.

This keeps the student at the same level without advancing them. The AI applies the lesson's exit
rules; the server verifies that the named lesson exists and enforces the pacing gate.

For a simple starting convention:

- `_0001` is the core entry lesson.
- `_0002` and later are alternate or remedial lessons at the same level.

Document any more detailed sequence convention here as the lesson bank grows.

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
v0|skill=vocab|level=1|lesson=vocab_L1_0002
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
