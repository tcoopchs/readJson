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

## 2. The shape of the plan: one band, filled across skills

**Decided 2026-10-26.** Work starts at **Band 4.1** and stays there until every vertical is complete
at that band. Band 3.1 is skipped: there is no population to serve at that level yet.

The order inside the band is by vertical, and `inference` is first:

```text
Phase 1   inference 4.1        8 lessons        <- current build
Phase 2   the other 7 verticals at 4.1   7 x 8 = 56 lessons
Phase 3   decide: stage 4.2, or 5.1 inference
```

Why band-first rather than a diagonal across bands: a student placed at 4.1 gets the whole skill
menu at their own level, and a teacher can switch skills without moving the reader. It also keeps
sourcing open — every work a cell needs is at one reading load.

Two consequences this decision creates, both needing an answer before Phase 2:

1. **Mastery at the top of 4.1 has nowhere to go.** `progression.py` advances along the ordered set
   list for a skill. With only `inference 4.1` in the inference list, a student who masters the
   eighth lesson hits `on_ceiling: hold` and is served the same lesson again. Nothing is broken or
   unsafe, but the band's strongest readers stop moving. The fix is the next set in that skill:
   either `inference 4.2` (stay in grade 4, use the stage axis) or `inference 5.1` (move up a grade).
   That choice should be made while 4.1 inference is being authored, not after Phase 2.
2. **Band 4.1 has no onboarding entry.** `onboarding.json` lists 4.1 with an empty `entries` object,
   so a finished `inference_band_4_1_0001` would still show "Lesson not available." Making 4.1
   selectable is a `readingHarness` change (`"4.1": {"inference": "inference_band_4_1_0001"}`), not
   a lesson change, and needs to be scheduled with the first publish.

Eight lessons per set is the target horizontal, so no set-size compromise is needed here.

### 2.0 The full grid

`onboarding.json` stores `entries` as a per-band dict of `skill -> lesson_id`, so a band can hold all
eight categories. Band 4.1 complete is `8 verticals x 8 lessons = 64 lessons`. That is the Phase 1-2
commitment, before any band above 4.1 exists.

Category order within the band is a separate decision from lesson content. Recommended, on the tier
logic:

| Order | Vertical | Why here |
| --- | --- | --- |
| 1 | `inference` | Decided. Highest-evidence comprehension move, and it anchors the band. |
| 2 | `main_idea` | Pairs with inference; gist is the other strong-evidence move and the easiest to key. |
| 3 | `vocab` | Word-level support must be available in the band a reader actually stalls in. |
| 4 | `text_structure` | Needs enough text to show visible organisation; 4.1 has it. |
| 5 | `process` | Reliable explanatory supply at this load. |
| 6 | `argument_evidence` | Harder at grade 4; needs multiple claims in one text. |
| 7 | `literary_text` | Needs modern fiction, which means original human-written text. |
| 8 | `authors_craft` | Shares the fiction supply; do it once the fiction pipeline exists. |

### Sourcing note for band 4.1

A cell needs eight disjoint passages of 100-200 words, so one work should carry ~4,000-6,000 words
at grade-4 reading load. That is a real constraint: grade-4-complexity prose comes in short pieces,
and long federal explainers at that load are uncommon. Expect some 4.1 cells to draw on two or three
works rather than one. That is allowed by 2.2 and reported as a note, and at this band it is the
likely shape rather than the exception.

### Genre inside a cell

Decided: no fiction and nonfiction tracks. Genres mix within the cell, so 4.1 stays at 64 lessons
instead of 128. Intended shape for inference 4.1 is five nonfiction and three fiction, with fiction
landing at `_0002`, `_0005`, and `_0008` so a student meets a story early, in the middle, and at the
top. Genre is recorded per lesson; difficulty knobs stay fixed across a genre switch.

Consequence for sourcing: the bank currently has zero fiction, so three works are needed before the
fiction slots can be authored. Two are public-domain adventures that measure in band (Treasure
Island 7.5, Call of the Wild 7.5); the third is either commissioned original fiction or the *Just YA*
pool if the product is non-commercial.

### Phase 1 — inference 4.1, eight lessons

Eight lessons on one cell. Build 0001 first, validate it, cold-chat test it, then use it as the
reference for 0002-0008. Sequence progression inside the cell should climb one knob at a time: clue
distance, competing details, or inference distance, not all three at once (`LESSON_AUTHORING_RULESET`
3.1).

| Batch | Lessons | What it establishes |
| --- | --- | --- |
| 1 | 0001-0002 | The cell opens; 0001 is the entry every 4.1 student sees, so it gets the most review |
| 2 | 0003-0004 | Mid-cell; the difficulty ladder is visible |
| 3 | 0005-0006 | Harder joins, longer clue distance |
| 4 | 0007-0008 | Top of the cell; step-down and ceiling behavior become observable |

At that point the set is `complete` with `expected_sequences` 1-8, and 4.1 inference is the first
fully working cell in the catalog.

### Phase 2 — the other seven verticals at 4.1

56 lessons in the order listed above. Each vertical repeats the Phase 1 loop: source the work, write
0001, review it, then the remaining seven. No vertical starts before the previous one is complete,
so the band is never half-open across skills.

### Phase 3 — decided later, on evidence

`inference 4.2`, `inference 5.1`, or a second pass over the band. The choice depends on where 4.1
students actually stall, which is not knowable until the band has run. Not scoped now.

### What the proof-of-concept lessons mean for this plan

The eight sources under `lessons/src/` carry `scope: prototype` and are not final. None of them is in
band 4.1, so they do not occupy the cell being built. They stay served while 4.1 is authored, and
they are replaced in place — same filenames and IDs — if a later band lands on one of their cells.
They do not set the category map, the batch order, or the quality bar.

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

This is the binding constraint, not the item writing. Phase 1 (inference 4.1) needs one work yielding
eight disjoint passages of 100-200 words. If that holds, the whole eight-vertical band needs roughly
eight to twenty works — more than eight because grade-4 prose comes in short pieces. Screening is a
first-pass read, not a title pick: budget roughly 3 candidates per committed work.

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
   Band 4.1 has no fiction vertical until `literary_text` (vertical 7), and that one needs original
   human-written prose or a rule change. Do not substitute an old story at this band.
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
   Source for eight even though the first batches author two at a time, or the set strands later. That
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
public-domain and CC text, which is overwhelmingly nonfiction. That is fine for inference and the
rest of the nonfiction verticals at 4.1. It becomes the wall at the fiction verticals, and it limits
modern fiction permanently below grade 12.

Also worth an audit: several existing sources say `source.basis: "Written for this lesson"`. If any
of those passages were AI-drafted during earlier work, they violate 2.5. I am not asserting they
were; I am saying the provenance is not recorded well enough to tell, and the 64 lessons in band 4.1
will multiply that ambiguity. Recommend recording `source.drafted_by` (initials) on every new lesson.

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

Designate one lesson as the **reference lesson** after Batch 1 (`inference_band_4_1_0002`, once it and
0001 pass review) and diff every subsequent lesson against it for section length, item mix,
and tone. Across eight lessons in one cell, drift is the main quality risk, not individual mistakes.

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

1. **Item count: five or ten to fifteen?** Five fits a 12-minute session and is what the prototype
   lessons use. `LESSON_AUTHORING_RULESET` 3 targets 10-15 for a bank lesson. Eight lessons at five
   items is 40 items per cell; at twelve it is 96. I recommend five for band 4.1 and revisit once a
   real student transcript exists.
2. **Where mastery goes after 4.1 lesson 8.** `inference 4.2` (same grade, next stage) or
   `inference 5.1` (next grade). Deciding now costs nothing and unblocks the last two lessons; leaving
   it means the band's strongest readers are held at the ceiling. I lean 5.1: a reader who masters
   eight grade-4 inference lessons has earned a grade-5 reading load.
3. **Human-drafting rule.** `DESIGN_RULES` 2.5 requires human-written passages and items. At band 4.1
   the supply is mostly public-domain and CC nonfiction, which is workable, but fiction (verticals 7
   and 8) needs original writing. Keep 2.5 as written, or allow AI-drafted prose with recorded human
   editing? This gates the last two verticals, not inference.
4. **Onboarding entry for 4.1.** A `readingHarness` change, not a lesson change. Without it, band 4.1
   stays invisible in the dropdown no matter how many lessons exist.

## Resolved

- **One passage per lesson; a work serves one cell.** 2.2 says this. A good work may be milked across
  a whole cell; a cell may also draw on several works. A work never serves two cells, so the step from
  one Band to the next always brings new material. Checked mechanically by `validate_lesson.py`, so
  nothing is tracked by hand.
- **Work starts at Band 4.1 and stays there until all eight verticals are complete.** 3.1 is skipped
  for lack of population. `inference` is the first vertical, eight lessons.
- **The eight proof-of-concept lessons are not final.** They are `scope: prototype`, sit outside band
  4.1, and set neither the category map nor the batch order. They stay served, and are replaced in
  place if a later band lands on their cell.
- **`text-bank.json` TB-002 is one passage in one cell.** Its second "best fit" entry was a bank
  defect and is removed.
