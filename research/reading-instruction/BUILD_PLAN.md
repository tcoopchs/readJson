# Curriculum Build Plan

Status: decisions recorded 2026-10-27. This supersedes the 2026-10-26 band plan. `DESIGN_RULES.md` is
normative wherever this plan summarizes it; 7.3.1 (the ladder), 7.6 (the carry field), and 2.6
(sourcing by band) are the rules this plan exists to serve.

Scope: what we build, in what order, at what rate, and under which sourcing rule.

---

## 1. The structure we build

One ladder per skill. Grade and stage are labels on a single ordered ramp; up and down are the only
moves; sequences are the road inside a rung.

```text
inference: 3.1 -> 4.1 -> 4.2 -> 4.3 -> 5.1 -> 5.2 -> 5.3 -> ...
```

- Six sequences per rung: four carry a reader through it, two are retry text.
- Three authored stages per grade (1-3). Stages 4-8 are reserved, appended later, never inserted,
  because a lesson ID is permanent once it has been served.
- Band 3.1 is the floor. Empty in onboarding, reachable only by a down-move. Below 3.1 a teacher, not
  a lesson.
- Promotion follows evidence, not lesson count: up on 2 of the last 3 lessons at 4+/5 with no help,
  down on 2 of the last 3 at 3 or fewer or any anchor item that needed help, stay otherwise. One move
  per day; two down-moves in a row holds and alerts.
- A student is never told their band. Band labels are internal and teacher-facing.

## 2. Where the catalog stands (verified 2026-10-27)

Forty-six compiled lessons. The inference ladder is complete from the floor through stage 4.3,
and `main_idea` runs from its floor through stage 4.1.

| Ladder | 3.1 | 4.1 | 4.2 | 4.3 | 5.1 | above |
| --- | --- | --- | --- | --- | --- | --- |
| `inference` | 6 ✓ | 8 ✓ | 6 ✓ | 6 ✓ | 2/6 | 6.1 at 1/6 |
| `main_idea` | 6 ✓ | 6 ✓ | — | — | — | 7.1 at 2/6 |
| other six | — | — | — | — | — | — |

Three facts that shape what comes next:

- **The floor exists and is wired.** 3.1 is built for inference and main_idea, empty in onboarding by
  design, and reachable by a down-move. `on_floor` is `restart_set`, so push-back serves unused text.
- **4.1 inference is selectable**, and a hard fail there now steps down to 3.1 instead of looping.
- **The engine matches the rules**: ticket v2, the three-lesson window, and the guard that refuses to
  move a reader into a set that is not `complete`. That guard is why a clear on main_idea 3.1 holds
  rather than jumping four grades to 7.1.

## 3. Sourcing rule by band

**Band 5 and above: human-written text only.** Verbatim, adapted from a named work under 2.5, or
written by a person for the lesson. No AI-drafted passage, no AI-drafted answer key. Screening stays
the bottleneck up here, and the daily cap below is not expected to hold.

**Below band 5 (3.x and 4.x): drafting is allowed** to reach volume, with a human review, recorded
provenance (`source.drafted_by`, `source.text_status: "drafted for the band, reviewed"`), and every
item re-checked against the text as published.

Three consequences worth stating up front:

- Grade 4 is the only part of the catalog that can be built at speed. Grade 5 and up cost what they
  cost.
- Modern fiction below band 5 is now reachable by drafting, so `literary_text` and `authors_craft` at
  4.x stop waiting on a source. The fiction supply problem moves up to grade 5, where it returns.
- Training data is not a source. A drafted passage is written to the band; it is not recalled from a
  work and it carries no attribution. Never invent a citation to make a drafted passage look sourced.

## 4. Rate

**Six lessons per day: one rung per day.** Stop at the rung boundary. A rung that fails
`validate_lesson.py --strict` does not roll into the next day; it is finished before a new rung
starts. Cold-chat test once per rung, not once per lesson.

At band 5 and above the cap is set from the first grade-5 batch rather than assumed, because human
sourcing adds screening that drafting removes.

## 5. Build order

### Phase 1 — finish the inference ladder (18 lessons, 3 days)

| Day | Set | Lessons | State |
| --- | --- | --- | --- |
| 1 | inference 3.1 | 0001-0006 — the floor | built |
| 2 | inference 4.2 | 0001-0006 | built |
| 3 | inference 4.3 | 0001-0006 | built |

Day 1 is the highest-value day in the plan: it is the only rung that removes a dead end. Write the
floor with the down-move in mind — a reader arriving there has just failed 4.1, so `_0001` must be
genuinely easier than anything in 4.1, not a relabelled version of it. The existing 4.1 set runs FK
5.3-7.6 and the grade-2-3 band tops out near 5.34, so 3.1 has to be written, not carved out of those
files. Inside the rung, climb one knob at a time: clue distance, competing details, or inference
distance, never all three at once.

Then, and only then: add `"4.1": {"inference": "inference_band_4_1_0001"}` to `onboarding.json` and
flip `on_floor` from `hold_and_alert` to `restart_set`.

### Phase 2 — the other seven verticals at grade 4 (168 lessons, 28 days)

Each vertical repeats the Phase 1 shape: 3.1, 4.1, 4.2, 4.3, six lessons each. Order:

| Order | Vertical | Why here |
| --- | --- | --- |
| 1 | `main_idea` | The other high-evidence comprehension move, and the easiest to key. |
| 2 | `vocab` | Word-level support must exist in the band a reader stalls in. |
| 3 | `text_structure` | Needs enough text to show visible organisation. |
| 4 | `process` | Reliable explanatory supply at this load. |
| 5 | `argument_evidence` | Harder at grade 4; needs several claims in one text. |
| 6 | `literary_text` | Fiction, now unblocked below band 5 by 2.6. |
| 7 | `authors_craft` | Shares the fiction supply; last because it inherits it. |

No vertical starts before the previous one is complete up its ladder, so a skill is never half-open.

### Phase 3 — grade 5 (144 lessons, rate set by screening)

8 verticals x 3 rungs (5.1, 5.2, 5.3) x 6 lessons. Human-written text only from here up. Do not start
until grade 4 is complete, because the first grade-5 batch is what tells us the real daily cap.

### Genre

Genre runs in two-grade blocks rather than per rung: **4-5 nonfiction, 6-7 fiction, 8-9 nonfiction,
10-11 fiction, 12 nonfiction.** Single-genre verticals are exempt — `process` and `argument_evidence`
stay nonfiction, `literary_text` stays fiction. Inside the flexible five a rung teaches one construct,
so `main_idea` at 4 is central idea and `main_idea` at 6 is theme, with no averaging inside a rung.

## 6. Sourcing mechanics (unchanged, restated for grade 5 and up)

### Source families, in priority order

| Family | Use for | License posture |
| --- | --- | --- |
| U.S. federal agencies — NPS, USGS, NOAA, USDA, CDC, NASA, Smithsonian | main_idea, text_structure, process, vocab | Public domain in the U.S.; verify it is a federal work, not a contractor page |
| OpenStax | process, text_structure, argument_evidence | CC BY; keep attribution |
| Our World in Data | argument_evidence, text_structure | CC BY; check per-chart vs per-article |
| The Conversation | argument_evidence, authors_craft on nonfiction | CC BY-ND — verbatim excerpt only, no adaptation |
| Project Gutenberg / standard public-domain texts | literary_text and authors_craft at 12.1 only | Public domain in the U.S.; pre-1929 |
| Text written for the lesson | any | `source.basis: written for this lesson` with `source.drafted_by` |

Reject without discussion: Wikipedia (share-alike complicates attribution), news wires and most
magazines, textbook scans, anything whose license is stated by the hosting site rather than the work.

### Rules that bite

1. **Licence verified per text, not per site.** Record the exact URL and access date.
2. **FK computed on the exact excerpt**, never the whole page.
3. **One work per rung; one passage per lesson.** The unit of uniqueness is the displayed passage. A
   long work may supply every lesson in one (category, grade, stage) rung, provided no two lessons
   display the same words. A work never serves two rungs, so every move brings fresh material.
4. **Milk the work.** Six disjoint passages of 100-200 words means roughly 3,000-4,500 words of usable
   text. Prefer a work that is internally varied: chapters on different subtopics, a report with
   several cases, an essay that moves through scenes. A single-mechanism explainer yields six
   passages testing one idea, and lessons four through six become practice without progress.
5. **Numbers and figures rechecked at authoring time.** Federal pages get revised.
6. **Screened-but-rejected goes in the table with a reason**, so the next author does not re-fetch.

Enforced without bookkeeping by one publish-gate check: group lessons by `(category, grade, stage)`
and by normalized attribution — two lessons in one rung citing different works fail, two lessons in
different rungs citing the same work fail — then compare 8-word shingles across `passage` within each
group. The current corpus passes: 8 sources, 8 distinct works, zero shingle overlap.

## 7. What "done" means for one lesson

1. Passage recorded in `text-bank.md` and `text-bank.json` with license or drafting provenance, exact
   URL or `source.drafted_by`, exact excerpt, FK measured on that excerpt, L/I/S/K scores, central
   idea, 3-5 supports, and a caution line.
2. Source written in `lessons/src/` from `new_lesson.py`, never hand-named.
3. Evidence mapped: every item names the sentence or sentences that answer it.
4. `validate_lesson.py --draft` clean while authoring.
5. `validate_lesson.py --strict` clean, no warnings.
6. `build_lessons.py --check` clean.
7. Cold-chat test passed: correct, misconception, blank, help ladder, tell/say-back, stop, injection.
8. Student copy read aloud; no praise, no "just/easy/simple," no ordinal section references.
9. `curriculum.json` row matches reality; the set flips to `complete` only when the last file lands.

## 8. Authoring guidelines (condensed; DESIGN_RULES governs)

- 100-200 words per part, 3-4 parts, 2-3 items per part; five items per lesson.
- Adult subject, plain sentences. The reader is never told their level.
- Score language, idea, structure, knowledge separately; the rung follows the **highest** demand.
  `why_this_level` states the readability number and the cognitive load in plain words.
- FK is a sanity check. Never relabel to fit a score — and never move a file to a lower band on the
  strength of its label alone.
- Item order: anchor -> join -> interpret -> optional craft -> optional synthesis.
- One defensible answer; a second defensible answer means rewriting the prompt.
- Every distractor and `if_they_say` branch names a real misreading.
- `help[0]` points at evidence, `help[1]` narrows without naming the answer, then `tell` teaches in two
  concrete sentences. Two helps maximum.
- No exclamation points, no praise, no coach voice.
- Designate a reference lesson per rung after 0001-0002 pass review, and diff the rest against it.
  Drift across a rung is the main quality risk, not individual mistakes.

## 9. Deferred, deliberately

- **Growth measurement.** Teacher-facing growth evidence needs history longer than a carry field,
  which means an anonymous case ID and a store. That breaks the README's no-database promise, so it is
  a product decision, not a backlog item.
- **Star-band placement.** Where an IRL decimal enters the ladder is a server mapping question. Stage
  numbers are not IRL tenths and must not be presented as such.

## 10. Decisions recorded

- **One ladder per skill; up and down are the only moves.** Sequences are the road, not a second axis.
- **Six sequences per rung, four to carry and two for retry.** Retry needs text that has not been
  displayed, and 2.2 forbids re-displaying a passage.
- **Three authored stages per grade, numbered 1-3, appended never inserted.**
- **Band 3.1 is the floor and is built first.** It stays empty in onboarding by design.
- **Sourcing splits at band 5.** Human-written at 5 and above; drafting allowed below 5 with recorded
  review.
- **Six lessons a day, one rung a day, stop at the boundary.**
- **A down-move never restarts the rung the student just failed.** It lands on the previous rung's
  middle sequence.
- **Band 4.1 keeps its eight existing files, unrenamed.** They are road inside the grade-4 rungs, not
  the bottom of anything.
- **Superseded:** the 2026-10-26 decisions that work would stay at band 4.1 until all eight verticals
  were complete, that 3.1 was skipped for lack of population, that a set was eight lessons, and that
  adaptation was permitted only at 4.1.

## 11. Status board

Move a row when its state changes. **Built** means six sources compile and the set is `complete`.
**Done** means the cold-chat pass is recorded for every lesson in the rung. Nothing here is done yet.

| Item | State | Next action |
| --- | --- | --- |
| Engine: ticket v2, carry, window, guards | built | cold-chat the floor to see it in a real session |
| `inference` 3.1 | built, unreviewed | cold-chat 0001, then the rest |
| `inference` 4.1 | built, adapted text unreviewed | cold-chat 0001-0008 |
| `inference` 4.2 | built, unreviewed | cold-chat 0001 |
| `inference` 4.3 | built, unreviewed | cold-chat 0001 |
| `main_idea` 3.1 | built, unreviewed | cold-chat 0001 |
| `main_idea` 4.1 | built, unreviewed | cold-chat 0001 |
| `main_idea` 4.2 | absent | author six — next in Phase 2 |
| `vocab` 3.1 | absent | after `main_idea` 4.3 |
| `text_structure` 3.1 | absent | after vocab |
| `process` 3.1 | absent | after text_structure |
| `argument_evidence` 3.1 | absent, and may not fit grade-3 load | decide before authoring |
| `literary_text` 3.1 | absent | needs a short story |
| `authors_craft` 3.1 | absent, and may not fit grade-3 load | decide before authoring |
| `text-bank` rows for the 24 drafted lessons | not written | backfill after the cold-chat pass |

### Handoff checklist

1. `build_lessons.py --check` exits 0 and `pytest` passes.
2. `lessons/curriculum.json` matches the files on disk, including which rungs are `complete`.
3. `HANDOFF.md` is rewritten from this board — it is the file a new author reads first, and it is
   wrong the moment a rung lands.
4. Both repositories are committed: lessons first, then the `readingHarness` config and code change,
   so the served config never points at a lesson that is not published.
