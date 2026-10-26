# Item Writing and Scoring v1

Purpose: rules that make a reading item defensible when an AI tutor scores it from stored fields.
Applies to `short_answer`, `cloze`, `multiple_choice`, and `rubric`.

## 1. Fifteen rules

### R1. One defensible answer

Write the answer first, in the exact terms the prompt allows. If a reasonable reader could produce
a second answer and defend it from the passage, rewrite the prompt or store both answers. [35]

### R2. Stem carries the task, not the options

Put the central idea in the stem; do not make the options complete the thinking. Avoid window
dressing and excess reading in the stem. [35]

### R3. Word the stem positively

Avoid NOT, EXCEPT, and double negatives. If a negative is unavoidable, capitalize and bold it.
[35]

### R4. Keep the item independent

No item should reveal the answer to another item. Shared evidence is fine; shared conclusions are
not. [35]

### R5. Keep item reading easier than passage reading

A prompt that is harder to parse than the passage measures the prompt, not the text. Use the
passage's terms and short sentences. [35]

### R6. Three options are enough

For multiple choice, use one correct option and two plausible distractors. Three options perform
as well as four or five in classroom assessment, and extra options add reading load. [35, 36]

### R7. Every distractor is a named misconception

Write each distractor from a real student error, not from an arbitrary wrong fact. Store the
misreading in `if_they_say.when` or `distractors[letter].misreading`. A distractor that no one
would choose is decoration. [35, 36]

### R8. Make options parallel and non-cueing

Same grammatical form, similar length, logical order. Do not repeat stem words in the correct
option. No "all of the above," no "none of the above," no always/never cues. [35, 37]

### R9. Only one option is correct

If two options can be defended, the item is broken. Fix the passage, the stem, or the options
before publishing. [36]

### R10. Accept ideas, not sentences

Store concept-level acceptable answers. Paraphrase, synonym, and spelling variation belong in
`normalize` or in additional `accept_ideas`, not in a demand for exact wording. [38, 40]

### R11. Do not score spelling or grammar

Unless the skill is explicitly word-level, a misspelling that still names the intended idea is
correct. Say so in `normalize`. Summary rubrics should state that grammar is not scored. [40]

### R12. Short answers may be fragments

A phrase is a real answer. Do not require a full sentence on the first attempt. When
`one_idea_is_enough` is true, accept the first complete idea and stop. [1, 35]

### R13. Cloze has one forced word

The blank must be determined by context, not by preference. One word per blank. No competing
synonym in a banked cloze. The definition belongs in the passage, not the prompt. [6]

### R14. Summaries use key points, not holistic quality

Store `key_points`, `min_coverage`, and `order_matters`. Count coverage. Do not assign a prose
quality score. The ETS summary rubric is the model: global idea, local ideas, no verbatim copying,
no inaccuracies. [40]

### R15. Pretest the wrong-answer branches

Every distractor and every `if_they_say` branch must be exercised in a cold chat. If the tutor
cannot recognize the misreading from the student's wording, rewrite the branch. [35]

## 2. Difficulty tags

Use a 1-4 tag that matches the question ladder:

| Tag | Move | What the reader must do |
| --- | --- | --- |
| 1 | Locate | Find one stated fact. |
| 2 | Join | Connect two stated facts. |
| 3 | Interpret or craft | State an unstated conclusion, or explain an author's choice with evidence. |
| 4 | Synthesis | Use the whole passage: central idea, theme, process summary, or claim evaluation. |

Tags describe the cognitive move, not the grade. A grade-9 reader can get a tag-1 item.

## 3. Item-type checklists

### short_answer

- [ ] Prompt asks one job.
- [ ] `accept_ideas` has at least two natural paraphrases.
- [ ] `one_idea_is_enough` is explicit.
- [ ] `partial` names the missing part.
- [ ] Every `if_they_say` names a real misreading.
- [ ] `normalize` handles spelling and named equivalents.
- [ ] `correct_reason` names the evidence sentences.
- [ ] `show_part` points at the evidence.

### cloze

- [ ] Prompt quotes the sentence with `____` unchanged.
- [ ] Answer is forced by context.
- [ ] `accept_words` is bounded and includes natural variants.
- [ ] `normalize` states spelling tolerance.
- [ ] Every `reject_words` entry has a branch.
- [ ] `say_back` is `use_word` with `word` and `word_also`.
- [ ] The definition is in the passage, not the prompt.

### multiple_choice

- [ ] Prompt contains the labeled options.
- [ ] One correct option only.
- [ ] Two plausible distractors, each with a named misreading.
- [ ] Options parallel in length and grammar.
- [ ] No cueing words, no all/none of the above.
- [ ] Options ordered logically.

### rubric

- [ ] 3-6 key points, each with an id.
- [ ] `min_coverage` is achievable and below the total.
- [ ] `order_matters` is explicit.
- [ ] `required_order` references known ids.
- [ ] No holistic quality language.

## 4. AI scoring limits

- Automatic short-answer scoring works best when the item is built around a small set of concepts
  and the model can check paraphrase or entailment, not keyword overlap. [38]
- Modern LLM scoring can reach high agreement with human scores on short answers in a well-defined
  domain, but agreement is not the same as validity. [39]
- The app has no training set and no human rater. The lesson's `accept_ideas` set is the whole
  scoring model. That makes generous paraphrase coverage and narrow prompts more important, not
  less.
- When the AI is uncertain whether an answer matches, the defensible move is to ask the say-back
  or move to `tell`, not to guess.

## 5. What to cut

| Weak item pattern | Why it fails | Fix |
| --- | --- | --- |
| "What do you think?" | No key | Ask what the text supports. |
| "Which is the best answer?" with two defensible options | Ambiguous | Rewrite the prompt or accept both. |
| Distractor built from a random false fact | Not a real misreading | Use an observed or named misconception. |
| Long, ornate prompt | Measures prompt reading | Shorten and use passage terms. |
| Exact-wording answer key | Punishes paraphrase | Store ideas and normalize. |
| Summary scored on "quality" | Unstable judgment | Count key points and accuracy. |

## 6. Open issues

- The 1-4 difficulty tag needs testing against actual student performance; it is a design label,
  not a calibrated scale.
- There is no local evidence yet on how often an LLM tutor mis-scores a paraphrase. The cold-chat
  test is the only current check.
- Multiple-choice is in scope, but the existing repo lessons use only short answer and cloze.
  Treat MC as optional until a lesson needs it.
