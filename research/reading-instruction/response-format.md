# Response Format: Free Reply vs Multiple Choice

Purpose: decide whether readJson lessons should move from free-reply items (`short_answer`,
`cloze`) to `multiple_choice`. This note reviews the comparison literature only. It does not
change any lesson, schema, or `DESIGN_RULES` rule.

## 1. The question

Two different questions get bundled together, and the evidence answers them differently:

- **Assessment.** Do MC and free reply measure the same reading comprehension construct, and do
  they give the same score?
- **Practice.** Which format produces more learning when the item is a practice item with feedback,
  not a graded test?

readJson is a practice product. That distinction decides most of what follows.

## 2. Assessment: same construct, different scores

| Finding | Source | Confidence |
| --- | --- | --- |
| Across 102 studies and 392 effect sizes, MC and open-ended (OE) scores correlate at mean r = 0.67, but MC scores average 0.65 SD higher (d = -0.65). The two formats share about 45% of variance. | 42 | strong (meta-analysis) |
| The MC advantage scales with the guessing probability, not with the construct. True/false (50% guess) shows d = -1.51; 4-5 option single choice shows d = -0.60; written short answer is the narrowest gap at d = -0.66. | 42 | strong |
| Format effects are largest when the comparison uses different stems, between-subject designs, or random assignment, i.e. when format is confounded with item difficulty. Stem-equivalent items shrink the gap. | 43 | strong (meta-analysis, 56 data sources) |
| In L1 reading, MC is easier than OE with effects from small to large; in L2 reading no overall format effect is found. | 43 | strong |
| A 2-dimensional IRT analysis of 8,523 German grade-9 students fits better than a unidimensional model: MC items load only on the general dimension, OE items load on the general dimension plus a nested dimension. The nested (OE-only) dimension correlates with higher-order reading processes; the general dimension correlates with vocabulary, orthography and general ability. | 44 | moderate (single large study) |
| The OE-only advantage appears for girls and for mother-tongue students; MC items did not show those differences. Format can therefore hide group differences in comprehension. | 44 | moderate |
| Readers who read a text in order to answer MC items build a weaker whole-text macrostructure than readers who read to summarize it. High MC scores can coexist with poor global comprehension. | 45 | moderate (single study, L2, N small) |

**Reading.** MC is not a different construct, but it is a systematically easier and shallower
sample of the same construct. The loss is concentrated exactly where readJson's inference,
`main_idea`, `text_structure`, and `authors_craft` categories live: whole-text integration and
explanation.

## 3. Practice: format matters less than feedback and retrieval success

| Finding | Source | Confidence |
| --- | --- | --- |
| In 4 experiments (N = 372) with educational texts, short-answer, MC, and hybrid practice all beat restudy on a 1-week delayed test, for both verbatim and inference questions. Short answer had little or no advantage over MC in 3 of 4 experiments. | 46 | strong (multi-experiment) |
| Short answer beat MC only when the design raised initial retrieval success for the short-answer group. The authors conclude that retrieval *success*, not retrieval *effort*, drives the benefit. | 46 | strong |
| Taking an MC test increases later correct answers on tested material (testing effect) but also increases later endorsement of the lures that appeared as distractors, even when subjects are warned not to guess. More lures per item means more of this negative effect. | 47 | strong (replicated line of work) |

**Reading.** For a practice product, MC is defensible *if* two conditions hold: the reader succeeds
often enough to make retrieval productive, and every lure is explicitly corrected in feedback.
Without the correction, an MC practice item can install the misconception it was written to detect.
readJson already has the correction channel — the `if_they_say` branch and the `tell` field — so
the negative-suggestion risk is a design obligation, not a blocker.

## 4. What MC buys readJson specifically

1. **Deterministic scoring.** The current `short_answer` key is an `accept_ideas` set plus a
   language model's judgment (item-writing.md §4: "the app has no training set and no human
   rater"). MC removes paraphrase variance entirely.
2. **False misses disappear.** A correct idea in awkward wording can no longer be scored wrong.
3. **Cheaper items.** No `accept_ideas`, `normalize`, `not_required`, or `core_idea` fields, and no
   cold-chat branch rehearsal per paraphrase.
4. **A clean misconception signal.** Each wrong option is a single recorded misreading, so the
   branch is chosen rather than inferred.

## 5. What MC costs readJson specifically

1. **The inference categories get easier, and the app's selling point is inference.** Inference and
   synthesis items are the ones whose difficulty depends most on production. Converting them to
   selection lowers the ceiling of the hardest lessons.
2. **Guessing floor.** Three options give a 33% floor, four give 25%. With 3-4 items per lesson, an
   uninterested reader can pass a lesson without reading. The item-writing rule "a question that can
   be answered without reading is not a comprehension question" (E05) is about exactly this.
3. **Recognition replaces explanation.** The app's `tell` and `skill_frame` model *how* to reach an
   answer. Selecting an option does not rehearse the reasoning step that the lesson exists to teach.
4. **Lure contamination.** Distractors are read as propositions. In a practice product aimed at
   readers who are still forming the idea, that is a real cost, and it argues for fewer options, not
   more.
5. **Loss of diagnosis granularity.** A wrong short answer tells the tutor what the reader thought.
   A wrong option tells it only which lure was most attractive.

## 6. Recommendation (design question, not applied)

Do not convert the corpus wholesale. Use format as a property of the item's move, not of the
lesson:

| Item role | Format | Reason |
| --- | --- | --- |
| Locate / anchor (tag 1) | MC is fine | Lowest production demand already; MC loses little. |
| Word in context | `cloze` stays | Already forced and deterministic; MC would add a synonym set. |
| Gist of one section (tag 2) | MC acceptable if options are full paraphrases | Paraphrase selection is still a comprehension judgment. |
| Join / interpret (tag 3) | Keep free reply | This is the production step the lesson teaches; MC pre-builds the inference. |
| Craft / structure naming | MC is a natural fit | "Which structure is this?" is a classification, and classification is selection. |
| Synthesis (tag 4) | Keep free reply or `rubric` | MC on a whole-text idea is the item type most vulnerable to lure contamination and guessing. |

If a lesson is fully MC, cap it at two options plus the key for tag-3+ items, or keep at least one
free-reply item per lesson so the reader still has to produce the relationship.

## 7. The symmetry objection

The obvious counter-argument, and it is correct: if the model cannot be trusted to judge a free
reply, it cannot be trusted to write a defensible multiple-choice item either. Both formats rest on
the same unaudited model.

The generated-item literature supports the objection. Recent distractor-generation work reports a
persistent gap in producing distractors that are plausible yet wrong, and lists answer leakage and
option repetition as characteristic LLM failures. Lee et al. (2026) show that even the *automatic
evaluation* of MC items is category-biased when an LLM estimates text informativity, and recommend
using those scores only within a category. So MC quality cannot be fully machine-assured.

The formats are not equally diagnosable, though, and that is the real asymmetry:

| Defect | How it shows up in free reply | How it shows up in MC |
| --- | --- | --- |
| Key too narrow / rejects a valid paraphrase | Silent. Surfaces only as a false miss, and only if someone re-scores. | Impossible: the key is an option, not a set of accepted ideas. |
| Two defensible answers | Surfaces as two stored `accept_ideas`. Visible in the file. | Item is broken and looks completely normal. |
| Question answerable without reading | Not mechanically testable. | Testable: strip the passage, ask a fresh model to pick the key. |
| Distractor nobody chooses | Not applicable. | Testable from logs: option chosen at ~0%. |
| Correct option cued by length or grammar | Not applicable. | Testable by arithmetic on option strings. |
| Plausible-but-not-a-real-misreading distractor | The equivalent field is `if_they_say`. | Same problem, same field, recorded per option. |
| Lure contaminating later knowledge | Not applicable. | Not detectable without a delayed re-test. |

What this table shows is that MC has more mechanically checkable defect classes and one
uncheckable one; free reply has fewer checkable ones and a silent, systematic one (the false miss).

Two conclusions follow, and they are the honest ones:

1. **Neither format is safe by default.** The choice is between defect classes you can measure and
   defect classes you cannot, not between a good option and a bad one.
2. **The misconception map is the shared bottleneck.** Rule R7 (every distractor names a real
   misreading) is unenforceable if the author invents the misreadings, and `if_they_say` has exactly
   the same exposure. Today the cold-chat log records tutor failures; once real students use the
   product it becomes the only source of actual misreadings, and it is format-independent. That
   asset is worth building in either case.

## 8. Resolving it with two cheap audits

Before any conversion, price both failure modes:

- **Free reply: false-miss audit.** Sample ~50 `short_answer` items, cold-score a corpus of realistic
  paraphrases (including deliberately awkward but correct ones), and count items that reject a valid
  answer. That yields the real cost of OE scoring.
- **MC: defect audit.** Blind-write MC versions of the same 50 items, then measure: (a) how often
  more than one option is defensible; (b) option-length and grammatical-parity violations;
  (c) passage-stripped solve rate — a fresh model given only prompt plus options, no passage, should
  be at chance, and any item above chance is answerable without reading; (d) whether each distractor
  survives a "is this a real misreading or a plausible-sounding invention?" judgment.

The passage-stripped test is the strongest of these because it mechanises the app's core validity
rule (E05) for the first time. Free reply has no equivalent, which is itself an argument for MC on
the *anchor* items.

## 9. Open questions

- Nothing in this literature tests an AI tutor against a human rater on free reply, so the
  "scoring risk" argument for MC is an inference from item-writing.md §4, not a measured defect.
  A small audit — sample 50 stored `short_answer` items, cold-score them, count false misses —
  would price the alternative properly.
- No evidence found on MC vs free reply *within a single chat lesson* with immediate feedback as the
  only difference. The practice literature (46, 47) uses written tests, not tutor dialogue.
- The Rauch finding (44) suggests MC and OE items should not be mixed into one score. readJson does
  not score lessons numerically today, so this is a constraint on any future progress metric.
