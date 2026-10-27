# Curriculum Build Plan — initial proposal

Status: proposal for discussion. Nothing here is implemented.
Scope: which lessons we author, in what order, against which progression, and under which
sourcing and authoring rules.
Authoritative inputs: `README.md` (naming, bands, progression), `DESIGN_RULES.md` (passage, items,
language), `readingHarness/server/progression.py` (what actually happens on finish).

---

## 1. Where the catalog actually stands (verified 2026-10-26)

Validation and compile check both pass on all eight sources:

```
validate_lesson.py --strict   8 files, 0 errors, 0 warnings
build_lessons.py --check      exit 0
```

But the catalog is thin in three separate ways, and they are not the same problem.

| Set | Lessons | Declared | Status |
| --- | --- | --- | --- |
| inference 5.1 | 2 | 8 | incomplete |
| inference 6.1 | 1 | 8 | incomplete |
| main_idea 7.1 | 2 | 8 | incomplete |
| process 9.1 | 2 | 8 | incomplete |
| process 10.1 | 1 | 8 | incomplete |
| all other cells | 0 | — | absent |

**Problem A — every live band holds after one or two lessons.** `on_incomplete_set` is
`hold_and_alert`. A student placed at 6.1 inference reads one lesson and is held, with a teacher
alert. This is the only *broken* student experience today, and it is the reason to fill the five
existing sets before opening new bands.

**Problem B — five of ten onboarding bands are empty.** Bands 3.1, 4.1, 8.1, 11.1, 12.1 have no
entries, so the dropdown shows "Lesson not available." Not broken, but unavailable.

**Problem C — three of eight categories exist.** `vocab`, `text_structure`, `literary_text`,
`authors_craft`, `argument_evidence` have no lessons, so a teacher cannot choose a skill.

**Problem D — mastery has nowhere to go in two categories.** `progression.py` orders sets *per
skill* by `(grade, stage)` and advances to the next set in that skill. `main_idea` has only 7.1, so
a student who masters it hits `on_ceiling: hold` at the same lesson. `process` 9.1 -> 10.1 works
until 10.1, then holds. `inference` will work across 5.1 -> 6.1 once both are complete.

Two consequences worth stating plainly:

- **Stages 2-8 are not needed yet.** The server's vertical axis is the ordered list of sets for a
  skill, regardless of stage. `5.1 -> 6.1` is a valid move today because no 5.2 exists. We do not
  have to author 8 stages per grade to get progression.
- **A complete 8-lesson set promotes a reader a whole grade on mastery.** With one set per grade,
  mastery is a full-grade jump. That is a real design question, not a data question (see §7).

---

## 2. The shape of the plan: a spine, then depth

Three possible strategies:

| Strategy | What it buys | What it costs |
| --- | --- | --- |
| Horizontal-first (8 lessons in one band) | One fully mature band, real step-down behavior | 7 more lessons before any second band works; most bands stay empty |
| Breadth-first (1 lesson in every cell) | Every band selectable | Every student holds after one lesson; nothing progresses |
| **Spine + depth (proposed)** | No holds anywhere, every category reachable, real cross-grade progression | 36 lessons before Release 1 |

Proposed: **four lessons per set, complete, then expand.** Four is the smallest set that lets a
student fail twice and still be inside the same stage, and it is legal — the server computes
step-down from `expected_sequences`, and `README.md` calls eight a target, not a constant. Sets are
declared complete at 4, then expanded to 8 later (safe: adding sequences and flipping to
`incomplete` serves the next existing lesson, then flips back to `complete`).

### 2.0 The real roadmap is the full matrix

`onboarding.json` stores `entries` as a per-band dict of `skill -> lesson_id`, so every band can hold
all eight categories. Nothing in the catalog, onboarding, or progression code favours one category
per band. The roadmap is therefore:

```
10 onboarding bands (3.1 - 12.1) x 8 categories = 80 cells
at 4 lessons per cell  = 320 lessons
at 8 lessons per cell  = 640 lessons
```

Release 1 fills **one cell per band** — a coverage diagonal, not a statement about which category
belongs at which grade. Category priority is a tier property, not a band property:

| Tier | Categories | Bands | Why |
| --- | --- | --- | --- |
| Universal | `vocab`, `main_idea`, `inference` | all 10 | Word-level support must exist wherever a reader stalls, and it is needed most where text turns abstract, not least. Gist and text-joining inference are the two highest-evidence comprehension moves. |
| Broad | `text_structure` | 4.1 up | Needs enough text to have visible organisation. |
| Band-dependent | `process`, `argument_evidence`, `literary_text`, `authors_craft` | by supply and load | Argument needs multiple claims and evidence; fiction needs a licence that permits it. |

Consequence for later releases: `vocab` is a full row of ten cells, not a single low-band entry, and
it is a better use of Release 3 than a second scattered category per band.

### Release 1 — "no student ever hits a wall" (44 lessons, 36 to write)

Eleven sets, four lessons each, all marked complete.

This table is a **coverage diagonal**, not a placement theory. Each row means "this band's first
authored cell." Where a cell already exists, the diagonal follows it. Where it does not, the choice
is driven by which category has a reliable modern-text supply at that load — not by a claim that the
band's other seven categories do not belong there. Every band is expected to hold all eight
eventually; see the tier table in §2.0.

| Band | First category | Now | New | Basis for choosing it as the opener |
| --- | --- | --- | --- | --- |
| 3.1 | vocab | 0 | 4 | Readers this far below grade level stall on words as often as on ideas; short parts are natural and the supply is plain nonfiction. Not exclusive to this band. |
| 4.1 | main_idea | 0 | 4 | Gist is the highest-evidence comprehension move and the easiest to key defensibly. |
| 5.1 | inference | 2 | 2 | Existing. Entry already wired in `onboarding.json`. |
| 6.1 | inference | 1 | 3 | Existing. Completes the only two-grade ladder we can test end to end. |
| 7.1 | main_idea | 2 | 2 | Existing. |
| 8.1 | text_structure | 0 | 4 | High-school band with the largest likely population and no content; structure has reliable expository supply. |
| 9.1 | process | 2 | 2 | Existing. |
| 10.1 | process | 1 | 3 | Existing. Gives process a two-grade ladder. |
| 11.1 | argument_evidence | 0 | 4 | Claim/evidence/reasoning is scorable from a stored key and the supply is adequate at this load. |
| 12.1 | literary_text | 0 | 4 | First fiction band; the only band where canonical older prose is allowed. One novella or long story carries the set. |
| 12.1 | authors_craft | 0 | 4 | Craft needs its own work; a second 12.1 work is the one extra find. |

Coverage after Release 1: 8/8 categories reachable, 10/10 onboarding bands with at least one cell,
0 incomplete sets, 0 holds except deliberate ceiling holds at the top of each skill's ladder. It
leaves 69 of 80 cells empty, which is the point of a release-1 diagonal.

Sourcing is **eleven works, not thirty-six documents**. Each work must sustain eight disjoint
passages even though Release 1 authors four. That is one deep read per cell instead of four shallow
ones, and every lesson after the first is nearly free to source.

### Order of work — nine batches of four

Ordered by "cheapest proof first," not by grade.

| # | Batch | New | What it proves |
| --- | --- | --- | --- |
| 1 | inference 6.1 | 3 | Loop works; completes a set with the least new prose |
| 2 | inference 5.1 | 2 | Cross-grade mastery 5.1 -> 6.1, plus step-down at the floor |
| 3 | main_idea 7.1 | 2 | Ceiling-hold behavior is intentional, not a bug |
| 4 | process 9.1 | 2 | — |
| 5 | process 10.1 | 3 | Two-grade ladder, then ceiling hold |
| 6 | text_structure 8.1 | 4 | First new band, first new category since the survey |
| 7 | main_idea 4.1 | 4 | Band below the current floor; tests grade-4 supply |
| 8 | argument_evidence 11.1 | 4 | First argument category |
| 9 | literary_text 12.1 + authors_craft 12.1 | 8 | First fiction; two works carry eight lessons |

Batch 9 is double-sized because two 12.1 cells need two different works. With one work per cell, each
still supplies four passages, so the sourcing cost is two finds, not eight.

### Release 2 — depth (target horizontal, 88 lessons)

Expand all eleven sets from 4 to 8 sequences. This is the state `README.md` describes as the target
horizontal, and the point at which a student who needs eight attempts has eight.

### Release 3 — not in this plan

Second category per band, stages 2-8, bands below 3.1 or above 12.1. Each needs its own decision.
Do not scope them now.

---

## 3. What "done" means for one lesson

A lesson is done when all of these are true, in this order:

1. Passage banked in `text-bank.md` **and** `text-bank.json` with license, exact URL, exact excerpt,
   FK measured on that excerpt, L/I/S/K scores, central idea, 3-5 supports, and a caution line.
2. Source written in `lessons/src/` from `new_lesson.py`, never hand-named.
3. Evidence mapped: every item names the sentence(s) that answer it.
4. `validate_lesson.py --draft` clean while authoring.
5. `validate_lesson.py --strict` clean, no warnings.
6. `build_lessons.py --check` clean.
7. Cold-chat test passed: correct, misconception, blank, help ladder, tell/say-back, stop, injection.
8. Student copy read aloud; no praise, no "just/easy/simple," no ordinal section references.
9. `curriculum.json` row matches reality; set flips to `complete` only when the last file lands.

---

## 4. Sourcing plan

The sourcing rules themselves live in `DESIGN_RULES.md` 2.2 and are repeated here only as the working
summary for this plan. If the two disagree, `DESIGN_RULES.md` wins.

This is the binding constraint, not the item writing. Release 1 needs **up to eleven works** — one
per cell where a single work can carry it, which is the cheapest shape — each yielding eight disjoint
passages of 100-200 words. Screening is a first-pass read, not a title pick: budget roughly 3
candidates per committed work, so ~30 deep reads.

### Source families, in priority order

| Family | Use for | License posture |
| --- | --- | --- |
| U.S. federal agencies — NPS, USGS, NOAA, USDA, CDC, NASA, Smithsonian | main_idea, text_structure, process, vocab | Public domain in the U.S.; verify it is a federal work, not a contractor page |
| OpenStax | process, text_structure, argument_evidence | CC BY; keep attribution |
| Our World in Data | argument_evidence, text_structure | CC BY; check per-chart vs per-article |
| The Conversation | argument_evidence, authors_craft on nonfiction | CC BY-ND — verbatim excerpt only, no adaptation; verify per article |
| Project Gutenberg / standard public-domain texts | literary_text and authors_craft at 12.1 only | Public domain in the U.S.; pre-1929 |
| Original text written for the lesson | any, and the only route to modern fiction | `source.basis: written for this lesson`; human-authored |

Reject without discussion: Wikipedia (CC BY-SA share-alike complicates attribution), news wires and
most magazines (all rights reserved), textbook scans, anything whose license is stated on the
hosting site rather than the work.

### Sourcing rules that actually bite

1. **Licence verified per text, not per site.** Record the exact URL and access date.
2. **FK computed on the exact excerpt**, never the whole page.
3. **One work per band; one passage per lesson.** 2.2 stands as written. The unit of uniqueness is
   the displayed passage, not the source. A single long work may supply every lesson in one
   (category, band) cell, provided no two lessons display the same words. A work never serves two
   cells. No runtime rewrite of a passage to step difficulty, either.
4. **No modern fiction below grade 11.** PD fiction is pre-1929, which breaks the modern-text rule.
   Release 1 puts fiction only at 12.1 for exactly this reason. Any fiction below 12.1 requires
   either original human-written text or a rule change.
5. **Numbers and figures rechecked at authoring time.** Federal pages get revised.
6. **Screened-but-rejected goes in the table with a reason**, so the next author does not re-fetch.

### Milk the work; never repeat the passage

The product goal is that a student reads something new every lesson. The operative unit is the
passage, not the source. Within one (category, band) cell:

- **One work may supply every lesson.** If a long piece is interesting and well written, take all
  eight passages from it. This is cheaper, and it is better instruction: by lesson five the reader
  carries the work's knowledge forward, so inference demand rises while background-knowledge demand
  stays flat. That is a controlled variable, not a monotony problem.
- **No passage may repeat.** Two lessons in one cell never display the same words. That is the whole
  rule, and it is the one case where a repeat actually corrupts the measure.
- **Each work serves exactly one cell.** Not two bands, not two categories. The step from Band 5.1 to
  Band 6.1 is the one transition a student is guaranteed to notice, so it gets fresh material.

### What makes a work worth milking

Two criteria, both settled by reading, not by a score:

1. **It can yield eight disjoint passages of 100-200 words**, each self-sufficient for its items.
   Source for eight even though Release 1 authors four, or expanding the set later strands it. That
   is roughly 4,000-6,000 words of usable text.
2. **It is internally varied.** Chapters on different subtopics, a report with several distinct
   cases, an essay that moves through scenes, a novella. A 3,000-word explainer of one mechanism
   yields eight passages that test the same idea, and lessons five through eight become practice
   without progress.

### How the rule is enforced without bookkeeping

`source.attribution` already carries the URL and author. One `audit_lessons.py` check, run at the
publish gate:

1. Group lessons by `(category, band)` and by normalized attribution. Two lessons in the same cell
   citing different works fail. Two lessons in different cells citing the same work fail.
2. Within each group, compare 8-word shingles across `passage`. Any substantial overlap fails.

No registry and no cross-referencing beyond files already in `lessons/src/`. The author's only added
step is banking the work before writing, which is already required. The current corpus passes: 8
sources, 8 distinct works, zero shingle overlap.

**Bank note:** `text-bank.json` TB-002 now carries one passage and one cell
(`main_idea_band_7_1_0002`). The USGS page itself may supply the rest of Band 7.1 main_idea if it
yields eight disjoint prose passages — its caution line says the page is table-heavy, so that is
doubtful, and it should not be banked for a second cell (`text_structure_band_7_1_0001`) either way.

### The rule I need a decision on

`DESIGN_RULES.md` 2.5 and `README.md` both say the passage and items must be **human-written**, and
that an AI may locate, compare, or fact-check but must not draft. Under that rule the supply is
public-domain and CC text, which is overwhelmingly nonfiction. It is fine for Release 1 as scoped.
It becomes the wall at Release 3, and it limits fiction permanently.

Also worth an audit: several existing sources say `source.basis: "Written for this lesson"`. If any
of those passages were AI-drafted during earlier work, they violate 2.5. I am not asserting they
were; I am saying the provenance is not recorded well enough to tell, and 36 new lessons will
multiply that ambiguity. Recommend recording `source.drafted_by` (initials) on every new lesson.

---

## 5. Authoring guidelines (condensed; DESIGN_RULES governs)

I am not restating all 413 lines of `DESIGN_RULES.md`. These are the rules that decide whether a
lesson passes review, plus the ones most often broken in the existing files.

### Passage

- 100-200 words per part, 3-4 parts, 2-3 items per part. Grade-3 vocab lessons may run shorter with
  a documented exception.
- Evidence in plain sight, within the part the item displays.
- No simplification at runtime. If it is too hard, re-source it.
- Adult subject, plain sentences. The reader is never told their level.

### Placement

- Score language, idea, structure, knowledge separately; the band follows the **highest** demand.
- `reader.why_this_level` states the readability number **and** the cognitive load in plain words
  ("two gates, small doors, which water is higher").
- FK is a sanity check. Never relabel to fit a score.

### Items

- Anchor -> join -> interpret -> optional craft -> optional synthesis. Never craft before facts.
- One defensible answer. If a second answer is defensible, rewrite the prompt.
- Key the **minimum idea** in `core_idea`; put details the prompt does not demand in `not_required`.
- Accept meaning-preserving synonyms on `short_answer`; keep `cloze` and `multiple_choice` exact.
- Every distractor and `reject_words` entry has a named misreading branch.
- `show_part` points at the evidence; whole-passage items use `show_part: "all"` +
  `show_part_again: true`.
- No ordinal section references. "The passage above," or a quoted opening.
- Ban: "what do you think," "do you agree," On-My-Own items, parenthetical definitions in prompts.

### Ladder and voice

- `help[0]` points at evidence, `help[1]` narrows without naming the answer, then `tell` teaches in
  one or two concrete sentences. Two helps maximum.
- No exclamation points. No "just," "easy," "simple," "awesome," "great job."
- Every line should sound like a straightforward high-school teacher, not a coach.

### Consistency mechanism

Designate one lesson as the **reference lesson** after Batch 1 (`inference_band_6_1_0004`, the newest
4-item-complete lesson) and diff every subsequent lesson against it for section length, item mix,
and tone. At 36 lessons, drift is the main quality risk, not individual mistakes.

---

## 6. Cost and work units

Follows the same discipline as the survey: bounded batches, measured spend, stop at the cap.

| Unit | Bound |
| --- | --- |
| Batch | 4 lessons = 1 set |
| Screening | 12 candidates reviewed, 4 banked, 4 rejected with reasons |
| Authoring | 1 passage-derived item ladder per lesson, 5 items |
| Verification | `--draft`, `--strict`, `--check`, 1 cold-chat per batch (plus 1 per new category) |
| Human review | read-aloud pass on 4 lessons |
| Spend | measure Batch 1 with `usage_delta.py`, then set the cap. Do not guess a dollar figure first. |

Estimate to check against Batch 1 data: ~45-60 minutes of wall time per batch, dominated by
screening, not by writing items. If a batch exceeds its cap, stop at the set boundary and report
rather than continuing into the next.

---

## 7. Decisions I need from you

1. **Set size at Release 1: 4 or 8?** I recommend 4-and-complete, then expand. Eight means 72 new
   lessons before a single band is trustworthy.
2. **Is the diagonal the right Release 1?** Eleven first-cells across ten bands, versus going wide on
   the universal tier first (`vocab`/`main_idea`/`inference` at every band = 30 cells). The diagonal
   is cheaper and gets one working lesson per band; the tier approach is more coherent but leaves
   bands 3.1/4.1 empty longer. I lean diagonal for Release 1, then `vocab` as an entire row.
3. **Item count: five everywhere?** Five fits a 12-minute session. Production banks were targeted
   at 10-15. I recommend five for all of Release 1 and revisit at Release 2.
4. **Grade-jump on mastery.** With one set per grade, mastery at the top of a 4-lesson set jumps a
   whole grade. Options: accept it, require 8 lessons before advancing (Release 2 first), or insert
   stage-2 sets at the same grade. This changes the Release 2 shape.
5. **Human-drafting rule.** Keep 2.5 as written, or allow AI-drafted passages with recorded human
   editing? Keeping it is cheaper for nonfiction and blocks modern fiction. This decision gates
   everything past Release 1.

## Resolved

- **One work per (category, band) cell; one passage per lesson.** 2.2 needs no amendment. A good work
  is milked across the whole cell; no displayed passage ever repeats. A work never serves two cells,
  so the step from Band 5.1 to Band 6.1 always brings new material. Checked mechanically by
  `audit_lessons.py`, so nothing is tracked by hand.
- **Sourcing targets long, internally varied works** that can yield eight disjoint passages of
  100-200 words, even when only four are authored now. Eleven works carry Release 1, not 36.
- **Category priority is a tier property, not a band property.** `vocab`, `main_idea`, `inference`
  are universal; every band is expected to hold all eight categories eventually.
- **`text-bank.json` TB-002 is one passage in one cell.** Its second "best fit" entry was a bank
  defect and is removed.
