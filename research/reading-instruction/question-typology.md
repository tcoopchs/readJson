# Question Typology v1

Purpose: turn practitioner question design into prompts an AI tutor can score without a human
facilitator. Every move below must end in a stored answer key, accepted-idea set, or rubric.

## 1. Question-answer relationship policy

QAR distinguishes four relationships between question and answer: Right There, Think and Search,
Author and Me, and On My Own. [22, 23]

| QAR type | Where the answer is | App policy |
| --- | --- | --- |
| Right There | One sentence or one paragraph | Allowed. Use as the anchor item for a part. |
| Think and Search | Two or more places in the passage | Allowed, and preferred for inference. This is the core comprehension move. |
| Author and Me | Text plus the reader's background knowledge | Allowed only when the passage supplies the needed background. Otherwise the AI cannot judge it. |
| On My Own | Entirely outside the text | Banned as a scored item. |

This is the operational form of the text-dependent rule: a question that can be answered without
reading the passage is not a reading comprehension question. [6, 27]

## 2. The part-level ladder

Each passage part should carry two or three items, not a flat list. The default sequence:

1. **Anchor.** A Right There item that establishes the facts the later items depend on.
2. **Join.** A Think and Search item that connects two textual facts.
3. **Interpret.** An inference item that requires the join and states a conclusion the passage
   does not state outright.
4. **Craft or structure.** Optional. Only when the author's choice is visible and checkable.
5. **Synthesis.** Optional, and usually one per lesson. A main-idea, theme, or process-summary
   item that uses the whole passage.

Do not put a craft item before the reader has the facts. Do not ask for synthesis on part 1 of a
three-part passage. [4, 26]

## 3. Move typology

| Move | Student task | Item type | Categories | Example stem | What must be stored |
| --- | --- | --- | --- | --- | --- |
| Locate | Find a stated fact | short_answer | all | "What does the passage say happens first?" | Exact accepted facts; `show_part`. |
| Join | Connect two stated facts | short_answer | inference, process, main_idea | "The note and the repair shop both point to one problem. What is it?" | Both evidence sentences in `correct_reason`. |
| Interpret | State an unstated conclusion | short_answer | inference, literary_text | "Why does she keep the door locked?" | The chain from facts to conclusion in `tell`. |
| Word in context | Explain a word as used | short_answer or cloze | vocab, all | "What does 'sluice' mean in this part?" | `accept_words`, `normalize`, context clue. |
| Gist | State what a section is mostly about | short_answer or rubric | main_idea | "What is this part mostly about?" | 2-3 acceptable paraphrases; not a single wording. |
| Central idea | State the whole-text point | rubric | main_idea | "What does the whole passage explain?" | Key points, `min_coverage`. |
| Sequence | Put steps in order or explain order | short_answer or cloze | process | "Why does the water leave before the gate opens?" | Causal link, not just step number. |
| Structure | Name how the text is organized | short_answer | text_structure, argument_evidence | "How is this part organized: cause and effect, comparison, or sequence?" | The signal words and the structure name. |
| Craft | Explain an author's choice | short_answer | authors_craft, literary_text | "Why does the author repeat the word 'level'?" | The effect and the evidence; no purely aesthetic judgment. |
| Character | Explain motive, change, or conflict | short_answer | literary_text | "What does this action show about her?" | Trait plus the action that shows it. |
| Claim and evidence | Identify a claim or the evidence for it | short_answer or multiple_choice | argument_evidence | "Which sentence supports the claim that the plant is overloaded?" | Claim, evidence, and why it supports. |
| Counterclaim | Name the opposing view | short_answer | argument_evidence | "What objection does the passage answer?" | The objection, not the student's opinion. |

## 4. Category-specific sets

### vocab

- Context clue: what does the word mean here?
- Contrast: which word could replace it without changing the meaning?
- Morphology: what does the prefix or root tell you?
- Reference: what does "it" or "they" point to?

Do not ask for a dictionary definition when the passage uses a specialized sense. Test the
passage sense. [17, 26]

### main_idea

- Gist of one part.
- Central idea of the whole passage.
- Which detail supports the central idea and which is incidental.
- Best title, with a reason.

Accept paraphrase sets, not one sentence. [26]

### inference

- Join two facts.
- Explain a motive or cause.
- Predict what happens next and cite the evidence.
- Explain what the text leaves uncertain.

Avoid questions that require outside knowledge the passage does not supply. [5, 22]

### process

- What happens first, next, last?
- Why must step 2 happen before step 3?
- What happens if one step fails?
- Which detail shows the process is repeated or reversed?

The reasoning must be causal, not merely ordinal. [9]

### text_structure

- Is this part organized by sequence, cause and effect, comparison, or problem and solution?
- Which signal words show that structure?
- How does the structure help the reader follow the idea?

### literary_text

Use the Notice and Note fiction signposts as planning prompts, not as student jargon: contrasts
and contradictions, aha moment, tough questions, words of the wiser, again and again, memory
moment. [24, 25]

- What does this contradiction show about the character?
- What does the repeated detail suggest?
- What did the character realize, and what changed after it?
- What is the theme, and which two moments support it?

### authors_craft

- Why this word instead of a plainer one?
- What does the repetition accomplish?
- How does the sentence length or punctuation affect pace?
- What is the narrator's or author's point of view?

Only ask when a student can point to the words and defend the effect. [4, 26]

### argument_evidence

- What is the claim?
- Which sentence is evidence for it?
- What reasoning connects the evidence to the claim?
- What counterclaim does the author answer?
- Which evidence is weakest, and why?

Use the nonfiction Notice and Note signposts: extreme or absolute language, numbers and stats,
quoted words, word gaps, contrasts. [24]

## 5. What does not work in a single-chat AI lesson

| Professional move | Why it fails here | Replacement |
| --- | --- | --- |
| "What surprised you?" | No stored answer; invites invention | "Which fact in paragraph 2 is unusual for a plant? Why?" with a key. |
| Personal connection prompt | Answerable without reading | Text-dependent join or interpretation item. |
| Open QtA discussion | Needs a facilitator and peers | Convert the query into a prompt with accepted ideas and a misconception branch. |
| Evaluative "do you agree?" | No defensible key | Ask what evidence the author gives, not what the reader believes. |
| Asking students to generate their own questions | Unscorable | Not in scope for this app. |
| Whole-class theme debate | Many defensible answers | Theme item with a rubric of required textual supports. |

## 6. Five-item lesson template

For a two-part passage with five items:

| Item | Part | Move | Purpose |
| --- | --- | --- | --- |
| q1 | part_1 | Locate or gist | Establish the facts and the section's point. |
| q2 | part_1 | Word in context or cloze | Handle the one word that blocks meaning. |
| q3 | part_2 | Join | Connect two facts across the passage. |
| q4 | part_2 | Interpret or craft | State the unstated conclusion or explain the author's choice. |
| q5 | whole | Synthesis or process | Whole-passage main idea, theme, or process summary. |

This is a default, not a rule. A vocabulary lesson can use more word items; a process lesson can
use more sequence items. [9, 17]

## 7. Scoring rules attached to the typology

1. One defensible answer. If two answers are defensible, rewrite the prompt or add both to the
   accepted set. [6]
2. Store the evidence. `correct_reason` names the sentence(s) that carry the answer. [4]
3. Store specific misreadings. Every `if_they_say` names a real wrong relationship: outside
   knowledge, a different QAR level, a detail mistaken for the main idea, a sequence error.
4. Do not accept a keyword without the relationship. "Cooler" alone is not an inference; the
   answer must say what the cooler did or failed to do. [5]
5. Craft and theme items use rubrics when more than one textual support is valid.

## 8. Authoring cautions

- The ladder assumes a two- or three-part passage. Verify it against the repo's existing
  two-part, five-item lessons.
- QAR "Author and Me" may still be usable if the passage supplies the background; test one item
  in a model lesson.
- The five-item template is the current prototype target. It remains an authoring choice to test,
  not a validated density threshold.
