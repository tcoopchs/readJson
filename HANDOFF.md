# Handoff — readJson / readingHarness

State as of 2026-10-31, written in the working tree through the `vocab` 4.2 rung and committed with
it. If `git status` shows the eighteen vocab sources uncommitted, the commit did not land and this
file is ahead of the tree.

Normative docs: `README.md` (naming, bands, routing), `DESIGN_RULES.md` (passage, items, ladder),
`research/reading-instruction/BUILD_PLAN.md` (what to build next). If this handoff and the rules
disagree, the rules win — and this file is wrong.

---

## Where the catalog stands

76 compiled lessons. The inference ladder is complete from the floor through stage 4.3, `main_idea`
is complete through stage 4.3, and `vocab` is complete from the floor through 4.2.

| Ladder | Rungs built | Notes |
| --- | --- | --- |
| `inference` | 3.1 ✓ (6) · 4.1 ✓ (8) · 4.2 ✓ (6) · 4.3 ✓ (6) · 5.1 2/6 · 6.1 1/6 | 5.1 and 6.1 are prototype files, incomplete |
| `main_idea` | 3.1 ✓ (6) · 4.1 ✓ (6) · 4.2 ✓ (6) · 4.3 ✓ (6) · 7.1 2/6 | 4.2 is one cell from six federal works; 4.3 is six drafted passages; the 7.1 gap is why a clear on 4.3 holds |
| `vocab` | 3.1 ✓ (6) · 4.1 ✓ (6) · 4.2 ✓ (6) | six drafted passages per rung under 2.6; TB-021 to TB-038; next rung is 4.3 |
| `the other five` | none | see Phase 2 in the build plan; `text_structure 3.1` is next |

`lessons/curriculum.json` matches reality: 4.1 inference keeps its eight files as road; 3.1, 4.2, 4.3,
main_idea 3.1, 4.1, 4.2 and 4.3, and vocab 3.1, 4.1 and 4.2 declare six each and are `complete`.

`main_idea` 4.3 (TB-015 to TB-020) is the rung the subject rule bit on: no two neighbours share a
domain, and the six span six of the seven domains — food and farming, arts and language, work and
trade, sport and play, history and people, places and travel.

## The start of the ladder is now wired

- **Ticket v2** (`readingHarness/server/tickets.py`): the completion line carries the result split and
  the rung memory. `an` is 1 only when every anchor item was unaided.
- **The window** (`server/progression.py`): up on 2 of the last 3 clears, down on 2 of the last 3 hard
  fails or any anchor miss, otherwise stay. One move per day by construction; a second consecutive
  down-move holds and alerts.
- **The guards**: a move never enters a set that is not `complete`, so the old four-grade jump from
  main_idea 3.1 to 7.1 is gone. At the floor, push-back serves the next unused sequence instead of
  re-showing text; when the rung is exhausted it holds for a teacher.
- **The memory rides in the signed link**: `carry=<stage>.<n>.<history>.<downs>` is minted into the
  `/next` ticket and injected into the served lesson's token line. No database, no accounts, no
  student records. A lost link costs at most two lessons of evidence and never moves a reader up.
- **Onboarding**: `4.1` now serves `inference_band_4_1_0001` and `main_idea_band_4_1_0001`. `3.1` stays empty on purpose — it is the
  floor and is reachable only by a down-move. `on_floor` is `restart_set`.

## What is verified

```bash
build_lessons.py --check          # exit 0
pytest                            # 57 passed
validate_lesson.py --strict       # 77 sources, 0 errors, 0 warnings
audit_lessons.py                  # 57 findings, the known ordinal backlog, none new in vocab
catalog load (76 lessons)         # ladders in order, onboarding rows valid, 3 vocab rungs complete
cold-chat sweep, 18 vocab lessons # smooth 18/18 ($0.0311); hard 18/18 ($0.0312), tell and an=0 stop
```

The sweep above was run after the ready-line change on 2026-10-28, so it covers the shared protocol
copy as it now stands: the ready line asks for `read`, and a first-message `read` draws exactly one
ready line (10 of 10 probes) rather than the previous coin flip with `yes`.

Vocab passed both sweeps on 2026-10-31 after the fixes below. Smooth 18 of 18 (`done=5 u=5 an=1`,
no leak, no early ticket). Hard 18 of 18: authored help only, `tell` reached, stopped ticket with
`an=0`, no private-field leak.

The first hard pass failed 11 of 18, and only part of that was lesson content. Ten lessons carried a
tutor-voice `help[1]` ("Then read the next sentence", "Ask what changes between them"), which the
model read aloud; all ten were rewritten as student-facing questions. The rest of the flag was the
sweep, not the copy: `hard()` compared every turn against item 1, so item 2's authored help and the
authored `tell` read as invented; it recognised only "say that back" while the tutor also writes
"Say it back", so the stop sequence never fired; and it answered a `use_word` say-back with the bare
word, which the tutor rightly rejects. The detector now checks authored copy only before `tell`, the
say-back matcher accepts either phrasing, the script answers with a sentence, and the turn budget is
16 because the described path needs two helps, two say-back tries, a stop request and a ticket.

`main_idea` 4.3 ran a smooth and a hard sweep on 2026-10-28, six of six both ways. Smooth: opened on
the first reply, five items in order, `done=5 u=5 an=1`, no leak, no early ticket ($0.0092). Hard:
only authored help reached the student, `tell` was reached, no invented help, stopped ticket with
`an=0|stop=1` ($0.0042). One branch session on `main_idea_band_4_3_0001` fired the item-1
misconception verbatim and refused two injections and a band question in one sentence each.

Routed against the live code: a clear on 3.1 → 4.1; a clear on 4.2 → 4.3; a second clear on 4.3
holds because 5.1 is not authored; a hard fail on 4.3 → the middle of 4.2.

The 4.2 rung's `advance` now names `main_idea_band_4_3_0001` instead of pointing back at itself, so
the authored route and the ladder agree.

## What is NOT done

1. **Every lesson has been swept, but not every branch.** On 2026-10-27 all 46 lessons ran a smooth
   path (open, five items, `u=5 an=1`, no leak, no early ticket) and a hard path (blank answers, the
   authored help ladder, `tell`, say-back, stop with `an=0`), 46 of 46 both ways. main_idea 4.2 and
   4.3 have since passed both. main_idea 4.1 sequences 0001 and 0006 also went through misconception,
   injection, and stop sessions, and 4.3 sequence 0001 has now had a misconception session and an
   injection session. Still untested anywhere: the near-copy say-back loop, and misconception
   branches on the other five 4.3 lessons. Findings and fixes are in
   `research/reading-instruction/coldchat-log.md`.
   Three catalog-wide defects were fixed to get this far: help lines written to the tutor instead of
   the student (85 lines), a single-help item making the tutor invent a second hint, and a ready gate
   that dropped `yes`. `anchor` is now defined as the lesson's first item in `DESIGN_RULES` 7.4,
   `README.md`, and the protocol at both the definition and the ticket step.
2. **54 lessons are AI-drafted and unreviewed.** inference 3.1, main_idea 3.1, inference 4.2 and
   4.3, main_idea 4.1, the six main_idea 4.3 lessons, and the eighteen new vocab lessons were drafted
   under `2.6`, and every one says `drafted_by: "TC review pending"`. Band 5+ cannot use that route.
3. **No `text-bank` rows** for 30 of those drafted passages. Provenance lives only in each source
   block. The six adapted `main_idea` 4.2 passages are banked (TB-009 to TB-014), the six drafted
   4.3 passages are banked (TB-015 to TB-020), and the eighteen vocab passages are banked (TB-021 to
   TB-038), each with measured FK, complexity scores, central idea, supports, and a caution line.
4. **`validate_lesson.py` is in the skill, not in either repo.** It lives at
   `~/.hermes/skills/productivity/readjson-lessons/scripts/validate_lesson.py`, so the plan's paths
   point at nothing. Run it from the skill against this repo:

   ```
   python3 ~/.hermes/skills/productivity/readjson-lessons/scripts/validate_lesson.py \
     --strict --src-dir lessons/src --lessons-dir lessons lessons/src/*.source.json
   ```

   It validated all 59 sources at 0 errors and 0 warnings on 2026-10-28. `build_lessons.py --check`
   remains the second gate: sources and compiled files must agree.
5. **57 `audit_lessons.py` style findings stand** (bare ordinal section references such as "What is
   the second part mostly about?", mainly in main_idea 4.1). These are a known backlog, not errors,
   and they need a copy decision before any sweep: the section ordinals are how the passage parts are
   named to the reader. 4.3 was written without them; one slipped in and was fixed.
6. **The four thin source families are still untested.** 4.3 met its domain debt by drafting, so
   USDA/extension, OSHA/BLS, Smithsonian recreation, and public-domain manuals have no rung that
   exercises them yet.

## Next actions, in order

1. `vocab 4.3`, six lessons — the last rung of the vocab ladder before the next vertical. Then
   `text_structure 3.1`. A vertical is finished up its ladder before the next starts, and
   `argument_evidence` and `authors_craft` need the grade-3 load decision before authoring.
2. TC review of the six 4.3 passages and the 30 older drafted ones; replace `drafted_by` with the
   reviewer's name as each is read.
3. Branch sessions on `main_idea` 4.3: misconception, injection, and stop on 0002-0006, plus the
   near-copy say-back loop, which has never been run anywhere.
4. Backfill `text-bank` rows for the 30 older drafted lessons.

## Rules a new author must not relearn the hard way

- One ladder per skill. Up and down only. Never move a reader sideways to another skill.
- Six sequences per rung: four carry, two are retry text. Never re-display a passage.
- Stage numbers are not IRL tenths. Never show a band label to a student.
- A lesson ID is permanent once it has been served. Append stages, never insert them.
- Below band 5, drafting is allowed with recorded review. At band 5 and above, human-written text only.
- Rotate the topic domain across a rung, and record it in `meta.topic_domain` before authoring, not after.
- When a rung lands above one that pointed back at itself, move the lower `advance` up in the same commit.
