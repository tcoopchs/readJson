# Evidence Table

One row per usable finding. A row is usable only if it changes a passage, question, scaffold, or
item decision in this app.

Columns:
`ID | Area | Finding (one sentence) | Source | App implication | Confidence | Notes`

Confidence: `strong` (federal guide with strong evidence rating or replicated research),
`moderate` (single study or moderate evidence rating), `practitioner` (method with wide use but
weak causal evidence).

## Section 1 seed

These are the findings already established in the quick survey. Later sections verify, expand, or
cut them.

| ID | Area | Finding | Source | App implication | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| E01 | Adolescent instruction | Explicit vocabulary instruction improves adolescent reading, with strong evidence. | 1, 2 | Vocabulary must be taught in context and revisited; do not assume word knowledge. | strong | Grades 5-12. |
| E02 | Adolescent instruction | Direct, explicit comprehension strategy instruction improves adolescent reading, with strong evidence. | 1, 2 | The lesson must name and model the skill, not only ask questions. | strong | Fits `skill_frame` plus `correct_reason`/`tell`. |
| E03 | Adolescent instruction | Extended discussion of text meaning has moderate evidence. | 1, 2 | The app cannot hold open discussion; convert discussion moves into scored prompts. | moderate | Design constraint, not a reason to skip the move. |
| E04 | Adolescent instruction | Motivation and engagement supports have moderate evidence. | 1, 2 | Passage interest and relevance matter, especially for older struggling readers. | moderate | Supports user's fiction/nonfiction mix. |
| E05 | Question design | A question answerable without the text is not a reading comprehension question. | 6 | Every scored item must require evidence from the displayed passage. | practitioner | Core validity test. |
| E06 | Question design | Text-dependent sequences move from literal anchors to inference, vocabulary, structure, and what the text leaves unstated. | 4 | Build part-level ladders instead of a flat mix of question types. | practitioner | Needs testing in the app's 2-3 item parts. |
| E07 | Question design | Literal questions are easier than inferential ones; text-joining inference is easier than text-plus-background inference. | 5 | Order items by inference distance; keep background-knowledge inference out of scored items unless the fact is supplied. | moderate | Study population: ages 10-14. Verify transfer to older readers. |
| E08 | Question design | Questioning the Author uses open queries at planned stopping points and follow-ups that extend meaning. | 3 | Use QtA moves to generate prompts, but store bounded acceptable answers because the AI cannot facilitate. | practitioner | See Section 4 for conversion rules. |
| E09 | Text complexity | Complexity has quantitative, qualitative, and reader/task dimensions. | 8 | Placement must score language load and idea load separately. | strong | CCSS model. |
| E10 | Adult literacy | Comprehension depends on decoding, vocabulary, and strategy use together; explicit strategy instruction helps adults. | 7 | Older readers may need word-level support inside a comprehension lesson. | strong | Verify adult-specific limits in Section 3. |
| E11 | Text types | Narrative and expository text place different demands on inference and background knowledge. | 5 | Use separate question templates for fiction and nonfiction. | moderate | Directly supports the fiction/nonfiction split. |
| E12 | Item design | Named misconceptions are more instructionally useful than generic wrong-answer feedback. | 3, 6 | Every distractor and `if_they_say` branch must name a real misreading. | practitioner | Verify with assessment-design sources in Section 6. |

## Gaps to fill

| Gap | Section |
| --- | --- |
| What changes for grades 9-12 versus grades 4-8 | 2 |
| How adult readers differ from adolescent readers | 3 |
| Checkable question ladder for each of the eight categories | 4 |
| Idea-load rubric that is not just a word count | 5 |
| Distractor and acceptable-paraphrase rules | 6 |
| Evidence on AI-run or computer-adaptive comprehension tasks | 9 (if time) |
| Fiction-specific question design beyond generic inference | 4, 8 |
