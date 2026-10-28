# Handoff — readJson / readingHarness

State as of 2026-10-27, uncommitted on `main`. Last commit is `16104a9`. Everything below is on
disk and verified, but **nothing since that commit is committed yet** — 70 files are modified or
untracked, including every runtime lesson, because the ticket-v2 change required recompiling the
whole catalog. Commit before handing this to anyone else.

Normative docs: `README.md` (naming, bands, routing), `DESIGN_RULES.md` (passage, items, ladder),
`research/reading-instruction/BUILD_PLAN.md` (what to build next). If this handoff and the rules
disagree, the rules win — and this file is wrong.

---

## Where the catalog stands

46 compiled lessons. The inference ladder is complete from the floor through stage 4.3, and
`main_idea` now runs from its floor through stage 4.1.

| Ladder | Rungs built | Notes |
| --- | --- | --- |
| `inference` | 3.1 ✓ (6) · 4.1 ✓ (8) · 4.2 ✓ (6) · 4.3 ✓ (6) · 5.1 2/6 · 6.1 1/6 | 5.1 and 6.1 are prototype files, incomplete |
| `main_idea` | 3.1 ✓ (6) · 4.1 ✓ (6) · 7.1 2/6 | the 7.1 gap is why a clear on 4.1 holds |
| the other six | none | see Phase 2 in the build plan |

`lessons/curriculum.json` matches reality: 4.1 inference keeps its eight files as road; 3.1, 4.2, 4.3
and main_idea 3.1 and 4.1 declare six each and are `complete`.

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
pytest                            # 54 passed
catalog load (46 lessons)         # ladders in order, onboarding rows valid
```

Routed against the live code: a clear on 3.1 → 4.1; a clear on 4.2 → 4.3; a second clear on 4.3
holds because 5.1 is incomplete; a hard fail on 4.2 → the middle of 4.1; a hard fail on 4.3 → the
middle of 4.2.

## What is NOT done

1. **Cold-chat coverage is two lessons.** main_idea 4.1 sequences 0001 and 0006 went through full
   sessions on 2026-10-27, covering misconceptions, blank answers, the help ladder, tell and
   say-back, early stop, and injection; both passed except one opening-gate miss. Findings are in
   `research/reading-instruction/coldchat-log.md`. The other 44 lessons are un-cold-chatted.
   `anchor` is now defined as the lesson's first item, in `DESIGN_RULES` 7.4, `README.md`, and the
   protocol at both the definition and the ticket step; the tutor had been guessing, and a correct
   unaided first answer was being stamped `an=0` and routed as a hard fail. The opening `ready` gate
   is still unreliable — two of six sessions in this pass drew `script.ready` again after `yes`, and
   one of them failed the gate across four consecutive turns.
2. **30 lessons are AI-drafted and unreviewed.** inference 3.1, main_idea 3.1, inference 4.2 and
   4.3, and main_idea 4.1 were drafted under `2.6` and every one says `drafted_by: "TC review
   pending"`. Band 5+ cannot use that route.
3. **No `text-bank` rows** for any of the 30 drafted passages. Provenance lives only in each source
   block.
4. **`validate_lesson.py` does not exist** in either repo, though the plan and the old handoff both
   cite it. `build_lessons.py --check` is the only automated gate that actually runs.

## Next actions, in order

1. Cold-chat `inference_band_3_1_0001`, then the rest of that rung. Fix source defects, not prompts.
2. `main_idea 4.2`, six lessons — Phase 2 finishes a vertical up its ladder before starting the next,
   so 4.2 and 4.3 come before `vocab 3.1`.
3. Backfill `text-bank` rows for the 30 drafted lessons, then commit in two parts: lessons repo, then
   the `readingHarness` config/code change.

## Rules a new author must not relearn the hard way

- One ladder per skill. Up and down only. Never move a reader sideways to another skill.
- Six sequences per rung: four carry, two are retry text. Never re-display a passage.
- Stage numbers are not IRL tenths. Never show a band label to a student.
- A lesson ID is permanent once it has been served. Append stages, never insert them.
- Below band 5, drafting is allowed with recorded review. At band 5 and above, human-written text only.
