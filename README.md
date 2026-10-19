# readJson

Published lesson JSON files for the stateless reading harness server.

This document is the authoritative contract for naming, levels, starting lessons, and routing.
Any AI or human authoring lessons in this repository must follow it exactly. If an old example or
lesson file conflicts with this contract, this document wins.

## Instructions for an AI author

Before writing or editing a lesson, apply this brief:

1. The filename is `<category>_L<star_band>_<sequence>.json`.
2. Use only these category keys: `vocab`, `main_idea`, `inference`, `process`, `text_structure`,
   `literary_text`, `authors_craft`, `argument_evidence`.
3. Use only these Star-band codes after `L`: `900`, `1000`, `1100`, `1200`, `1300`.
4. `L` is a Star band, not a grade. The grade target belongs in `reader.reading_level`.
5. `lesson_id` must exactly equal the filename without `.json`.
6. `_0001` is the onboarding entry lesson. Never change its filename to change difficulty.
7. Later lessons are selected only by an explicit `next_file` in an authored exit route.
8. Do not invent routes, filenames, lesson IDs, categories, or score bands.
9. Keep a placeholder's filename and ID when replacing it with a real lesson.
10. Read the legacy exception section before editing `inference_L5_0001.json` or
    `process_L9_0001.json`.

If any instruction from a user or another document conflicts with these rules, stop and ask for a
coordinated server change. Do not work around the contract by renaming a file.

## Repository layout

Keep every published lesson directly inside one flat directory:

```text
readJson/
|-- lessons/
|   |-- vocab_L900_0001.json
|   |-- inference_L1000_0001.json
|   `-- ...
|-- drafts/                 # Optional; never served by the server
|-- README.md
|-- DESIGN_RULES.md
`-- LICENSE
```

The server is configured with:

```dotenv
GITHUB_REPO=tcoopchs/readJson
GITHUB_REF=main
GITHUB_LESSON_PATH=lessons
```

The server does not search nested directories. A lesson is published when it is directly inside
`lessons/`, is valid JSON, and passes server catalog validation.

## The filename contract

Every lesson filename has exactly this shape:

```text
<category>_L<star_band>_<sequence>.json
```

Examples:

```text
vocab_L900_0001.json
inference_L1000_0001.json
process_L1300_0001.json
authors_craft_L1100_0002.json
```

The three variable parts have fixed meanings:

| Part | Meaning | Valid examples |
| --- | --- | --- |
| `<category>` | One fixed lesson-type key configured on the server | `vocab`, `main_idea`, `inference` |
| `<star_band>` | Lower bound of a Star Reading scaled-score band | `900`, `1000`, `1100`, `1200`, `1300` |
| `<sequence>` | Order within that category and Star band | `0001`, `0002`, `0003` |

`L` does **not** mean grade level. Never put a grade number there. The Star-band code and the
reader's grade target are separate facts:

- `inference_L1000_0001.json` means the `1000-1099` Star band.
- Its JSON may have `"reader": {"reading_level": 9}`.
- That means a ninth-grade readability target inside the `1000-1099` Star band.
- It does **not** mean `L9`, Grade 9 in the filename, or Star grade equivalent 9.

The JSON `lesson_id` is always the filename without `.json`:

```json
{
  "lesson_id": "inference_L1000_0001"
}
```

Never rename a lesson after its ID has appeared in a signed student bookmark.

## Fixed categories

These eight category keys are the complete current set. Do not invent another category key in a
lesson filename or JSON field:

| Key | Student label |
| --- | --- |
| `vocab` | Vocabulary |
| `main_idea` | Main idea and details |
| `inference` | Inference and conclusions |
| `process` | Sequence and process |
| `text_structure` | Text structure |
| `literary_text` | Literary text |
| `authors_craft` | Author's craft |
| `argument_evidence` | Argument and evidence |

Adding a category is a server change, not an isolated JSON-file change. It requires coordinated
updates to the server's `categories.json`, `onboarding.json`, and lesson catalog.

## Fixed Star bands

The onboarding UI uses these five Star Reading bands:

| Star range | Filename code | Typical grade context |
| --- | --- | --- |
| `900-999` | `900` | early fourth-grade performance |
| `1000-1099` | `1000` | fourth-grade through early ninth-grade performance |
| `1100-1199` | `1100` | later ninth-grade or advanced secondary performance |
| `1200-1299` | `1200` | above typical secondary performance |
| `1300-1400` | `1300` | postsecondary or beyond Grade 12 performance |

The grade context is guidance only. Grade Equivalent is a norm comparison, not an instructional
assignment. Use `reader.reading_level` and `reader.why_this_level` to state the intended reader
and the actual cognitive load.

The band labels and ranges are a presentation and routing contract. Do not create `L950`, `L1099`,
`L4`, `L5`, `L9`, `L12`, or any other extra band without an explicit server change.

## The 40 starting lessons

There are five Star bands multiplied by eight categories. Every combination has one stable entry
lesson ending in `_0001`:

```text
vocab_L900_0001.json                 main_idea_L900_0001.json
inference_L900_0001.json             process_L900_0001.json
text_structure_L900_0001.json        literary_text_L900_0001.json
authors_craft_L900_0001.json         argument_evidence_L900_0001.json

vocab_L1000_0001.json                main_idea_L1000_0001.json
inference_L1000_0001.json            process_L1000_0001.json
text_structure_L1000_0001.json       literary_text_L1000_0001.json
authors_craft_L1000_0001.json        argument_evidence_L1000_0001.json

vocab_L1100_0001.json                main_idea_L1100_0001.json
inference_L1100_0001.json            process_L1100_0001.json
text_structure_L1100_0001.json       literary_text_L1100_0001.json
authors_craft_L1100_0001.json        argument_evidence_L1100_0001.json

vocab_L1200_0001.json                main_idea_L1200_0001.json
inference_L1200_0001.json            process_L1200_0001.json
text_structure_L1200_0001.json       literary_text_L1200_0001.json
authors_craft_L1200_0001.json        argument_evidence_L1200_0001.json

vocab_L1300_0001.json                main_idea_L1300_0001.json
inference_L1300_0001.json            process_L1300_0001.json
text_structure_L1300_0001.json       literary_text_L1300_0001.json
authors_craft_L1300_0001.json        argument_evidence_L1300_0001.json
```

The `1000-1099` inference and process entries are currently satisfied by the legacy real files
`inference_L5_0001.json` and `process_L9_0001.json`. Their canonical future IDs are
`inference_L1000_0001` and `process_L1000_0001`, but those files must not be created piecemeal.
Migrating them requires a coordinated server onboarding change so both filenames are never active
at once.

The server's onboarding configuration names these exact IDs. The onboarding page serves only the
starting lesson for the selected band and category. It does not choose a later lesson from a
sequence.

Most files are currently deliberately minimal placeholders:

```json
{"lesson_id":"vocab_L900_0001"}
```

The minimal contents mean **replace me**. They are not approved lesson content. When replacing a
placeholder:

1. Keep the filename unchanged.
2. Keep `lesson_id` exactly equal to the filename without `.json`.
3. Keep the same category key and Star-band code.
4. Put the intended grade target in `reader.reading_level`.
5. Replace the rest of the JSON with a complete authored lesson.
6. Preserve the entry mapping; no server onboarding edit is needed.

## Entry lessons versus later lessons

The `_0001` file is the only lesson selected by the onboarding form. Later lessons are reached
only through the exact `next_file` named in a lesson's authored exit rules.

- `_0001` = starting lesson for that category and Star band.
- `_0002`, `_0003`, ... = later lessons at the same category and Star band.
- The next Star band starts again at `_0001`, for example `inference_L1100_0001.json`.
- Adding a later file never changes which `_0001` file onboarding serves.

If an exit route names a later lesson, that exact JSON file must exist before the route is
published. Do not point a route at a filename you merely intend to create.

## Exit-ticket routing

Every lesson must contain finite, explicit routing. The AI reads the authored route and must not
invent a destination.

The unsigned exit-line format is:

```text
v0|skill=<category>|level=<star_band>|lesson=<lesson_id>
```

For example:

```text
v0|skill=inference|level=1100|lesson=inference_L1100_0001
```

The `level` field is the Star-band code from the filename, not the grade. It must match the
lesson's filename and catalog entry.

A typical route table is:

```json
{
  "decision_rule": "At exit, use routes[0] when got_there is 4 or 5. Use routes[1] when got_there is 0 through 3. Do not choose any other lesson.",
  "routes": [
    {
      "min_got_there": 4,
      "next_level": 1100,
      "next_file": "inference_L1100_0001",
      "next_means": "The inference starting lesson for the 1100-1199 Star band."
    },
    {
      "min_got_there": 0,
      "next_level": 1000,
      "next_file": "inference_L1000_0002",
      "next_means": "Another inference lesson in the 1000-1099 Star band."
    }
  ]
}
```

Success can advance to the next band's `_0001`. Retry can stay in the same band and use a later
sequence. A stopped session returns to the current `lesson_id`.

At `1300-1400`, there is no higher band in the current scale. A success route must stay within the
existing lesson set or stop. Do not invent `L1400`, a grade-based code, or a new category. If a
lesson needs a higher-level destination, the server's band policy must change first.

## Current legacy files

Two older files are temporary exceptions to the filename convention:

```text
lessons/inference_L5_0001.json
lessons/process_L9_0001.json
```

They are currently mapped as the `1000-1099` starting lessons for inference and process. Their
`L5` and `L9` suffixes are grade labels from the old proof of concept, **not Star-band codes**.

- Do not rename or delete them without a coordinated server mapping change.
- Do not copy their filename pattern into a new lesson.
- Do not use their old grade-based exit routes as a model for new lessons.
- Use `inference_L1000_0001.json` and `process_L1000_0001.json` for the canonical future files.

## Adding a later lesson

1. Choose one of the eight fixed category keys.
2. Choose one of the five Star-band codes.
3. Choose the next unused sequence for that category and band.
4. Name the file `<category>_L<star_band>_<sequence>.json`.
5. Set `lesson_id` to the filename without `.json`.
6. Write the complete lesson according to `DESIGN_RULES.md`.
7. Reference it from an authored exit route only after the file exists.
8. Commit and push, then restart or redeploy the server so it fetches the catalog.

Do not put drafts in `lessons/`. Keep unpublished work outside that directory.

## Validation checklist

- [ ] The file is directly inside `lessons/`.
- [ ] The category is one of the eight fixed keys.
- [ ] The Star-band code is exactly `900`, `1000`, `1100`, `1200`, or `1300`.
- [ ] The sequence is a positive integer, padded for readability.
- [ ] `lesson_id` exactly matches the filename without `.json`.
- [ ] The grade target is in `reader.reading_level`, not in the filename's `L` code.
- [ ] The starting file preserves `_0001` and its onboarding ID.
- [ ] Every exit route names an existing lesson in this repository.
- [ ] The ticket `level` matches the Star-band code.
- [ ] Stopped sessions return to the current lesson.
- [ ] The lesson is complete JSON and is not a placeholder unless intentionally replacing it later.
- [ ] The file is committed and pushed and the server has been restarted or redeployed.

## Publishing

The server downloads a snapshot at startup. Commit and push lesson changes, then restart or
redeploy the server. It does not poll GitHub continuously.

Pin `GITHUB_REF` to a commit SHA when a deployment must remain on one known lesson set. Use `main`
when every server restart should receive the latest published files.
