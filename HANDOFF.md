# Handoff — readJson / readingHarness

State as of 2026-10-28, committed on `main` through the `main_idea` 4.2 rung. The catalog is
clean: `git status` shows nothing uncommitted, and every runtime lesson matches its source.

Normative docs: `README.md` (naming, bands, routing), `DESIGN_RULES.md` (passage, items, ladder),
`research/reading-instruction/BUILD_PLAN.md` (what to build next). If this handoff and the rules
disagree, the rules win — and this file is wrong.

---

## Where the catalog stands

52 compiled lessons. The inference ladder is complete from the floor through stage 4.3, and
`main_idea` now runs from its floor through stage 4.2.

| Ladder | Rungs built | Notes |
| --- | --- | --- |
| `inference` | 3.1 ✓ (6) · 4.1 ✓ (8) · 4.2 ✓ (6) · 4.3 ✓ (6) · 5.1 2/6 · 6.1 1/6 | 5.1 and 6.1 are prototype files, incomplete |
| `main_idea` | 3.1 ✓ (6) · 4.1 ✓ (6) · 4.2 ✓ (6) · 7.1 2/6 | 4.2 is one cell from six federal works; the 7.1 gap is why a clear on 4.2 holds |
| the other six | none | see Phase 2 in the build plan |

`lessons/curriculum.json` matches reality: 4.1 inference keeps its eight files as road; 3.1, 4.2, 4.3
and main_idea 3.1, 4.1, and 4.2 declare six each and are `complete`.

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
validate_lesson.py --strict       # 53 sources, 0 errors, 0 warnings
audit_lessons.py                  # no finding in any 4.2 lesson
catalog load (52 lessons)         # ladders in order, onboarding rows valid
```

`main_idea` 4.2 ran a smooth and a hard sweep on 2026-10-28, six of six both ways: smooth ends
`u=5 an=1` with no leak and no early ticket; hard reaches `tell`, invents no help, and stops with
`an=0`. Spend for both passes was $0.048.

Routed against the live code: a clear on 3.1 → 4.1; a clear on 4.2 → 4.3; a second clear on 4.3
holds because 5.1 is incomplete; a hard fail on 4.2 → the middle of 4.1; a hard fail on 4.3 → the
middle of 4.2.

## What is NOT done

1. **Every lesson has been swept, but not every branch.** On 2026-10-27 all 46 lessons ran a smooth
   path (open, five items, `u=5 an=1`, no leak, no early ticket) and a hard path (blank answers, the
   authored help ladder, `tell`, say-back, stop with `an=0`), 46 of 46 both ways. main_idea 4.1
   sequences 0001 and 0006 also went through misconception, injection, and stop sessions. Still
   untested anywhere: the near-copy say-back loop, and misconception branches outside those two
   lessons. Findings and fixes are in `research/reading-instruction/coldchat-log.md`.
   Three catalog-wide defects were fixed to get there: help lines written to the tutor instead of the
   student (85 lines), a single-help item making the tutor invent a second hint, and a ready gate that
   dropped `yes`. `anchor` is now defined as the lesson's first item in `DESIGN_RULES` 7.4,
   `README.md`, and the protocol at both the definition and the ticket step.
2. **30 lessons are AI-drafted and unreviewed.** inference 3.1, main_idea 3.1, inference 4.2 and
   4.3, and main_idea 4.1 were drafted under `2.6` and every one says `drafted_by: "TC review
   pending"`. Band 5+ cannot use that route.
3. **No `text-bank` rows** for any of the 30 drafted passages. Provenance lives only in each source
   block. The six adapted `main_idea` 4.2 passages are banked (TB-009 to TB-014) with licence, URL,
   access date, measured FK, complexity scores, central idea, supports, and a caution line.
4. **`validate_lesson.py` is in the skill, not in either repo.** It lives at
   `~/.hermes/skills/productivity/readjson-lessons/scripts/validate_lesson.py`, so the plan's paths
   point at nothing. Run it from the skill against this repo:

   ```
   python3 ~/.hermes/skills/productivity/readjson-lessons/scripts/validate_lesson.py \
     --strict --src-dir lessons/src --lessons-dir lessons lessons/src/*.source.json
   ```

   It validated all 52 sources at 0 errors and 0 warnings on 2026-10-28. `build_lessons.py --check` remains the
   second gate: sources and compiled files must agree.
5. **57 `audit_lessons.py` style findings stand** (bare ordinal section references such as "What is
   the second part mostly about?", mainly in main_idea 4.1). These are a known backlog, not errors,
   and they need a copy decision before any sweep: the section ordinals are how the passage parts are
   named to the reader.

## Next actions, in order

1. `main_idea 4.3`, six lessons — Phase 2 finishes a vertical up its ladder before starting the next,
   so 4.3 comes before `vocab 3.1`. Drafting is not available here by choice: 4.2 established the
   adapted-federal-source route at grade 4, and 4.3 should follow it.
2. Branch sessions on `main_idea` 4.2: misconception, injection, and stop per rung. The smooth and
   hard sweeps are clean, so what is left is the copy that only a branch reaches.
3. Cold-chat `inference_band_3_1_0001`, then the rest of that rung. Fix source defects, not prompts.
4. Backfill `text-bank` rows for the 30 drafted lessons.

## Rules a new author must not relearn the hard way

- One ladder per skill. Up and down only. Never move a reader sideways to another skill.
- Six sequences per rung: four carry, two are retry text. Never re-display a passage.
- Stage numbers are not IRL tenths. Never show a band label to a student.
- A lesson ID is permanent once it has been served. Append stages, never insert them.
- Below band 5, drafting is allowed with recorded review. At band 5 and above, human-written text only.
