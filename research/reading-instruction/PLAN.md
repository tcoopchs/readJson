# Reading Instruction Survey — Sectioned Plan

Goal: an evidence-based design guide for passages, questions, scaffolds, and item types that an
AI tutor can execute from a single lesson file.

Constraint: run in 30-minute sections. Each section is self-contained, writes its output to disk,
and stops at a section boundary even if incomplete. Later sections read the files, not the chat.

## Cost discipline

Time is a weak control: a section with no retrieval finishes in two minutes, while one heavy
extraction can burn more than a quiet half hour. Work units are the real budget.

- 6-8 sources per section, maximum. No broad crawls.
- `web_extract` with `char_limit` 6000-8000, and no more than the section's extract cap.
- Every section ends by writing a file. No section relies on remembering earlier chat.
- No subagents. They duplicate retrieval and multiply tokens.
- Citations are registered once in `research/reading-instruction/sources.md`.
- Checkpoint at roughly 15 minutes: finish the source in hand, write `STATE:` to the output file,
  and report. Resume from that state next turn.

Per-section retrieval budget:

| Section | New sources | Extracts | Retrieval expected |
| --- | --- | --- | --- |
| 1 | 0 | 0 | none (setup) |
| 2 | 6 | 4 | moderate |
| 3 | 6 | 4 | moderate |
| 4 | 7 | 5 | heavy |
| 5 | 6 | 4 | moderate |
| 6 | 7 | 4 | moderate |
| 7 | 0 | 0 | none |
| 8 | 0-1 | 0-1 | none |
| 9 | 0-2 | 0-1 | light |

If a section needs more than its cap, stop and report the reason before spending more.

## Files

```text
research/reading-instruction/
  PLAN.md                 this plan
  sources.md              numbered source ledger, one line each
  evidence-table.md       principle -> source -> app implication
  question-typology.md    question moves mapped to item types and categories
  complexity-rubric.md    placement beyond Lexile
  text-bank.md            screened passages with genre, grade, band, measure
  text-bank.json          machine-readable version of the same bank
  design-guide.md         the synthesis, in authoring language
  model-lessons/          2-3 worked examples
  REVIEW.md               resolved decisions and cautions
```

## Sections (9 x 30 min = 4.5 h)

### 1. Frame and evidence map
- Record the five questions the survey answered.
- Fix the source classes: research reviews, practitioner guides, assessment design, text
  complexity, adult literacy.
- Seed `evidence-table.md` with the eight sources already found.
- Output: `evidence-table.md` skeleton, `sources.md` seeded, `REVIEW.md` with scope decisions.
- Stop: no new retrieval after the skeleton is written.

### 2. Adolescent literacy and struggling readers
- IES/WWC adolescent literacy guide, Reading Next, and one recent review of interventions for
  grades 4-12.
- Extract: what changes instruction for older readers, what does not transfer from early grades.
- Output: 8-12 rows in `evidence-table.md`.

### 3. Adult and postsecondary readers
- TEAL/QEd adult literacy evidence, adult comprehension strategy studies.
- Extract: decoding and vocabulary gaps in older readers, respect/tone constraints, motivation.
- Output: 6-8 rows; a short "what this means for tone and difficulty" note.

### 4. Question design
- Text-dependent questioning, close reading sequences, Questioning the Author, inference types.
- Extract: a question ladder (literal anchor -> text-joining inference -> craft/structure ->
  synthesis), with the checkable version of each move.
- Output: `question-typology.md` v1.

### 5. Text complexity beyond Lexile
- CCSS three-part model, qualitative dimensions, knowledge demands, cohesion, task fit.
- Extract: a placement rubric with language load and idea load scored separately.
- Output: `complexity-rubric.md` v1.

### 6. Item writing and scoring
- Distractor design, acceptable paraphrase sets, rubric summaries, inference distance, avoiding
  background-knowledge-only items.
- Extract: rules that fit `short_answer`, `cloze`, `multiple_choice`, `rubric`.
- Output: 10-15 item rules appended to `question-typology.md`.

### 7. Synthesis
- Turn the evidence table into authoring rules: passage selection, item sequence, help ladder,
  tell, say-back.
- Map each rule to a field in schema v3, or mark it as guidance only.
- Output: `design-guide.md` v1.

### 8. Model lessons
- Build 2-3 worked examples: fiction at Band 3.1, nonfiction at Band 9.1 (wastewater-style idea
  load), and a Band 12.1 literary passage.
- Each shows passage selection, question sequence, and stored keys.
- Output: files in `model-lessons/`, checked against `validate_lesson.py --draft`.

### 9. Review and integration
- Resolve conflicts, cut weak rules, verify every claim against `sources.md`.
- Produce the final guide and the skill reference `references/reading-material.md`.
- Propose `DESIGN_RULES.md` amendments as a separate diff, not applied without approval.
- Output: `REVIEW.md` closed, final guide, integration diff.

## Start protocol

Say `section 1` (or `go`) to run the next section. Each run starts by reading `PLAN.md` and the
last output file only. At the end of each section I report what was written and the next section's
exact scope. Decisions are resolved in `REVIEW.md`.
