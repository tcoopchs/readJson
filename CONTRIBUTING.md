# Contributing a lesson

readJson lessons are written as **sources** and compiled into the runtime files the server serves. A
source is the only thing you edit; the compiled copy in `lessons/` is generated.

## Before anything else: the text must be free to use

A contribution without a named, freely usable source is not reviewed. One of:

- **public domain** (US federal works; pre-1929 works; Project Gutenberg for US use),
- **CC0**, or
- **CC BY** — which requires that you say changes were made.

Never adapt NoDerivatives or ShareAlike material. Text written for the lesson is fine, and must say so.
Record it in `meta.source`: `basis`, `attribution` (a full citation with the exact URL and access
date), and `text_status`. See `DESIGN_RULES.md` 2.5 and 2.6 for the exact wording of each field.

Write the passage for a reader, not a test: modern prose except at the top band, adult subjects, plain
sentences, nothing that makes the reader feel small.

## The loop

```bash
git clone https://github.com/ctroy978/readingHarness ../readingHarness   # public, no venv needed
git checkout -b lesson/<category>_band_<grade>_<stage>_<sequence>
#   write lessons/src/<same-name>.source.json
python3 tools/check.py --harness ../readingHarness lessons/src/<your>.source.json
python3 tools/compile.py --harness ../readingHarness      # writes lessons/<your>.json
```

`tools/check.py` runs three gates and prints PASS only when all three pass:

1. the compiled output matches the sources,
2. the validator is clean over the whole corpus (strict: warnings are errors),
3. the new-lesson key checks pass on the files you named.

If it fails, the message names the check. Fix the source, re-run, then commit **both** the source and
the compiled file.

## What the machines cannot see

A passing `check.py` means the lesson is well formed. It does not mean it is good. A reviewer will
read the passage and the five keys and ask:

- Is the text worth a reader's time, and is the band label honest about its idea load?
- Does every item have one defensible answer, and does the prompt name the move it grades?
- Are the misreading branches real misunderstandings, or invented ones nobody would produce?
- Is every answer keyed to text that is actually displayed for that item?

Three things are checked after you open the pull request, not before: the key probe (five items through
three tutor models, a few cents), the passage read, and the licence record.

## Conventions

- One lesson per pull request. Branch `lesson/<lesson-id>`.
- Five items: anchor, join, interpret, then craft or synthesis. See `DESIGN_RULES.md` section 3.
- Do not edit `lessons/curriculum.json` unless you are adding a set; say so in the PR.
- Do not touch `tools/` or the protocol copy in the harness; those are maintainer files.
- Compile with the harness clone at the pin recorded in the PR description, so a reviewer can reproduce
  the output exactly.
