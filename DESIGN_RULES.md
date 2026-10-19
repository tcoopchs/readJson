# JSON Lesson File Design Ruleset

This document defines the content authoring rules for `readJson` lesson files. It applies to every
reading category, topic, Star band, and reader target. [README.md](README.md) is authoritative for
the repository's filenames, fixed categories, Star-band codes, starting-lesson mapping, and legacy
exceptions. This document is authoritative for passage, question, readability, routing, and lesson
content. Both override older examples when they conflict.

Every rule comes from a project decision, the foundational reading-harness authoring rules, or a
documented readability or plain-language standard. Add a source note when a rule depends on a
particular external standard. The server validates structure and filenames. The AI tutor applies
the authored lesson. This repository does not make the AI responsible for inventing content,
answers, or routes.

## 1. Reading Level: How to Tag and Control It

**1.1 Measure readability quantitatively.** Use Flesch-Kincaid grade level as the primary
readability check. It is available in Microsoft Word under File > Options > Proofing > Show
readability statistics and through other standard readability tools. If a Lexile measure is
needed, use the Lexile Analyzer or another documented Lexile tool. Record which measure was used
and where. Do not rely on intuition alone.

**1.2 `reading_level` labels the reader, not the filename.** `reader.reading_level` is the grade
target for the intended reader. It is independent of the Star-band code in the filename:

```text
inference_L1000_0001.json   # filename: 1000-1099 Star band
reader.reading_level: 9     # content: intended for a ninth-grade reader
```

A passage that scores FK 6.2 can still be appropriate for a ninth-grade reader when vocabulary,
background knowledge, inference distance, and working-memory load are controlled. State that
distinction in `reader.why_this_level`. Never put the reading grade into the filename's `L` code.

**1.3 Use the Common Core text-complexity bands as a sanity check.** A Grade 4-5 reader target is
roughly FK 4.51-7.73. A Grade 6-8 reader target is roughly FK 6.51-10.34. These are review
targets, not proof of placement. If a passage falls outside the intended band, rewrite it or change
the reader label. Do not relabel a passage merely to make the number fit.

**1.4 Control cognitive load separately from sentence length.** Readability formulas measure
sentence length and word frequency. They do not measure the number of steps, entities, clue
distances, or schema demands. Every `reader.why_this_level` must state the actual load in plain
language. For example: "one place, two times, people you can track one at a time" or "two gates,
small doors, where the boat is, which water is higher, and a reversed trip at the end."

## 2. Passage Design

**2.1 Length.** Target 100-200 words per displayed passage part. A lesson should contain roughly
3-4 short passage segments, each supporting 2-3 questions. A shorter passage is acceptable when
the skill is sentence-level; document a longer exception in `reader.why_this_level` or
`meta.authoring_exceptions`.

**2.2 Each Star band and reader target gets its own passage.** Do not generate runtime rewrites of
one passage to step difficulty. Write or select a separate passage for each authored lesson.
Adaptation moves across exact files named by exit routes, never across AI-authored rewrites.

**2.3 The passage must contain the evidence in plain sight.** Every inference, cloze, main-idea,
and author's-purpose answer must be derivable from text shown in the current lesson. If an item
depends on an earlier passage part, set `show_part` to that part. `show_part: null` is valid only
when the item is answerable from text already on screen, such as a quoted cloze sentence.

**2.4 Do not simplify the passage after the fact.** The AI presents passage text exactly as
written. If the text is too hard, rewrite the source before publishing. Do not ask the tutor to
simplify, paraphrase, or regenerate it during a session.

**2.5 Source discipline.** Use public-domain, openly licensed, or original text. An AI may draft a
candidate, but a human must review and edit it before it enters `passage` or `items`. State the
source basis and text status in `source.basis` and `source.text_status`. Never invent a citation.

## 3. Question Design

Every item must carry:

1. a plain-language student prompt;
2. a correct answer and the reasoning behind it;
3. each wrong answer and the specific misreading it represents;
4. a primary skill tag and a difficulty tag.

### 3.1 Comprehension and short-answer items

**3.1.1 One defensible answer.** Rewrite the item or passage if a reasonable student could produce
a different answer and still be correct under the prompt.

**3.1.2 Every distractor must represent a real misreading.** Write an `if_they_say` or `partial`
branch for it. If no credible student response would trigger the distractor, cut it.

**3.1.3 Answerable from the passage.** Do not use items that can be answered from general knowledge
alone. The student must use the displayed text.

**3.1.4 Use the three-level question framework as a design check.** Level 1 facts are the
baseline. Level 2 inference, analysis, and evidence-based explanation are the target. Level 3 open
judgment or evaluation is out of scope because it cannot be scored reliably against a stored key.

**3.1.5 Inference must require a reasoning chain.** The answer should not be stated outright.
Store the chain in `tutor_only.tell`, naming the facts in the passage and the conclusion they
support.

### 3.2 Cloze items

**3.2.1 The blank must be forced by context.** Test whether a reasonable student could choose a
different bank word and still be right. If so, tighten the context or remove the competing word.

**3.2.2 Do not define the target word in the prompt.** The definition belongs in the passage. The
prompt should quote the cloze sentence with the blank unchanged and ask for the missing word.

**3.2.3 Banked and open cloze.**

- Banked cloze: exact scoring, one word per blank, and no competing synonyms in the bank.
- Open cloze: store a bounded `accept_words` set with natural synonyms and documented spelling
  tolerance. Do not reject a valid synonym because it is absent from the set.

**3.2.4 Cloze is not universal.** Use it for context clues, grammar or connectives, cohesion, and
reference. Do not use it for whole-passage inference, theme, author's purpose, or summarization.

### 3.3 Summarize and retelling items

**3.3.1 Store a rubric, not a prose quality judgment.** Use `key_points`, `min_coverage`, and an
`order_matters` flag. The AI checks coverage against the stored rubric.

**3.3.2 The rubric must be specific.** "At least 3 of 5 key points, with events 2-4 in order" is a
rubric. "Good summary" is not.

### 3.4 Main idea and author's purpose items

**3.4.1 Store an acceptable-paraphrase set.** If a natural paraphrase is missing, the item is
incomplete. Add it or rewrite the item.

**3.4.2 Keep skill tags distinct.** Inference asks what the text implies. Main idea asks what the
whole text is about. Author's purpose asks why the text was written in that way. Separate tags are
required for separate adaptation rules.

## 4. Language and Tone

**4.1 Write for the reader, not down to the reader.** `reader.tone` must state: "Adult subject.
Plain sentences. The lesson must not make the reader feel small." Every prompt, confirm, help, and
tell line must obey that tone.

**4.2 Plain-language rules apply to all student-facing text.**

- Aim for sentences of 15 words or fewer.
- Prefer active voice: "The manager reads the note," not "The note is read by the manager."
- Prefer common words: "use," not "utilize"; "fix," not "remediate."
- Use consistent terms. If the passage says "cooler," the question says "cooler."
- Define essential skill terms once, in context, and only when needed.
- Do not use exclamation points or praise inflation.
- Do not use "just," "easy," "simple," "buddy," "kiddo," or similar condescending language.

**4.3 The `tell` line is the teaching moment.** State the fact and the reasoning in one or two
short sentences. "The food is not cold anymore. The milk is warm. The lettuce and ice cream are
soft." Do not write textbook abstractions when concrete wording will do.

**4.4 The help ladder is a gradient.** `help[0]` is a nudge toward the evidence. `help[1]` is a
stronger but still non-answer-bearing nudge. Neither may name the answer or present a closed list
that gives it away. Then use `tell` as the final authored explanation.

**4.5 The AI's voice is the teacher's voice.** The tutor sounds like a straightforward high-school
teacher: short sentences, plain words, no baby talk, no cheerleading, no invented encouragement.
Every authored student line must match that voice.

## 5. Structural Rules

**5.1 `show_part` rule.** Every item that depends on passage text must set `show_part` to the part
containing the evidence. If the evidence is in `part_1` and the item follows `part_2` items, set
`show_part: "part_1"`. Use `null` only when the answer is recoverable from text already on screen.

**5.2 `accept_ideas` contains ideas, not instructions.** Put spelling and normalization guidance in
`normalize`; put acceptable ideas in `accept_ideas`.

**5.3 `if_they_say` branches must identify real misreadings.** A branch that applies to every wrong
answer is too broad. Make it specific to the misconception.

**5.4 `reject_words` must be consumed.** Every rejected word needs an authored branch or an explicit
generic handling rule.

**5.5 Exit routes must be explicit and finite.** Name every possible `next_file` in `exit_rules` or
`rules.routes`. The AI must never invent a destination. The server rejects a ticket that names a
missing lesson.

**5.6 The ticket carries no PII.** `token_done` and `token_stopped` may contain only the category,
Star-band code, lesson ID, counts, and the exact next lesson. Never include a reader grade target,
name, student ID, email, IP address, or score history. The ticket's numeric `level` field is the
Star-band code from the filename, not `reader.reading_level`.

## 6. Skill Selection

**6.1 In-scope skills include:**

- passage-level comprehension and inference;
- main idea, theme, author's purpose, and text structure;
- summarization and retelling;
- cloze for context clues, grammar or connectives, cohesion, and reference;
- vocabulary in context.

**6.2 Out of scope:**

- fluency, reading speed, and pronunciation that require audio;
- phonemic awareness and phonics requiring oral observation;
- open-ended judgment or evaluation that cannot be scored against a stored key.

**6.3 Target one primary skill and at most one secondary skill.** Too many simultaneous strategies
raise cognitive load for struggling readers. The most useful combinations are deliberate, such as
main idea with text structure and retelling. Do not mix four skills into one file. The lesson's
primary skill must match one of the eight fixed filename categories in README.md.

## 7. Star Bands, Entry Lessons, and Exit Routing

**7.1 Filename convention.**

```text
<category>_L<star_band>_<sequence>.json
```

The category must be one of the eight fixed keys in README.md. The Star-band code must be exactly
`900`, `1000`, `1100`, `1200`, or `1300`. The code is the lower bound of the Star range; it is not
a grade. For example, `_L1000_` means Star `1000-1099`. Labels such as `L9`, `L950`, `L1099`, and
`L5a` are invalid for new lessons. The only legacy exceptions are the two files named in
README.md.

**7.2 `_0001` is the onboarding entry lesson.**

For each category and Star band, `_0001` is the starting lesson selected by the onboarding form.
Later sequences are reached only through authored exit routes. There is no fixed `_0005` ceiling.
Choose the next unused sequence deliberately; do not invent a horizontal lesson merely because a
slot exists.

The server's onboarding mapping names exact lesson IDs, so adding `_0002`, `_0003`, or later never
changes which lesson the dropdown serves.

**7.3 `lesson_id` must equal the filename without `.json`.** Never rename a lesson after its ID has
appeared in a signed bookmark.

The grade target is not part of the ID. Record it in `reader.reading_level` and explain it in
`reader.why_this_level`.

**7.4 Exit routing is authored, not calculated.** Every lesson must contain an explicit
`decision_rule` and finite `routes`:

```json
{
  "decision_rule": "At exit, use routes[0] when got_there is 4 or 5. Use routes[1] when got_there is 0 through 3. Do not choose any other lesson.",
  "routes": [
    {
      "min_got_there": 4,
      "next_level": 1100,
      "next_file": "inference_L1100_0001",
      "next_means": "The inference starting lesson for the 1100-1199 Star band.",
      "student_line": "You put most of these facts together on your own. The next reading is another inference lesson."
    },
    {
      "min_got_there": 0,
      "next_level": 1000,
      "next_file": "inference_L1000_0002",
      "next_means": "Another inference lesson in the same 1000-1099 Star band.",
      "student_line": "You have the basic move. The next reading is another inference lesson."
    }
  ]
}
```

The standard rule is:

- `got_there` 4-5: advance to the next Star band's entry lesson;
- `got_there` 0-3: stay in the current Star band and move to the next authored sequence.

For a lesson in the top `1300-1400` band, there is no next Star band. Use an existing authored
lesson at the same band or stop. Do not invent `L1400` or any other code outside the five bands in
README.md. Changing the top of the band scale is a server change, not a lesson-file choice.

The AI fills `{next_file}` from the chosen route. It must not calculate, guess, or invent a
filename. A referenced lesson must exist before its route is published; otherwise `/sign` cannot
produce a working ticket.

**7.5 Stopped sessions return to the same lesson.** `stopped.next_file` must name the current
`lesson_id` unless a deliberately authored continuation lesson exists. A stopped ticket does not
replace or repeat an item mid-session and does not imply a grade change.

## 8. Authoring Workflow

**8.1 Draft the passage first.** Write or adapt the source text, run a readability check, and
verify the target band before writing questions.

**8.2 Identify the evidence points.** For each item, point to the sentence or sentences in the
passage that support the answer. If you cannot point to the evidence, the item is not ready.

**8.3 Write the item.** Add the prompt, answer and reasoning, specific distractors, `show_part`, and
the primary skill and difficulty tags.

**8.4 Write the help ladder and tell.** Nudge toward the evidence, narrow without giving the answer,
then teach with the complete authored explanation.

**8.5 Write the misreading branches.** Name the specific misconception and author the response for
it.

**8.6 Write the exit route.** Choose the exact next lesson for success and the exact later lesson
for retry. Use the Star-band code, not a grade, in `next_level`. Confirm both files exist before
publishing.

**8.7 Test cold.** Upload the file to the AI and complete a full session. Test correct answers,
misconceptions, blank answers, the help ladder, tell and say-back, stopping, and prompt injection.
Fix every point where the tutor improvises or discloses private data.

**8.8 Read every student-facing line aloud.** Check for condescension, worksheet cliches, vague
language, and unsupported claims.

## 9. The One Rule That Overrides All Others

If a rule conflicts with a defensible pedagogical judgment for a specific passage, the pedagogical
judgment wins. Record the reason in one sentence in `reader.why_this_level`,
`meta.authoring_exceptions`, or a nearby authored note. Do not leave a silent exception. The rules
exist to make files consistent and defensible; they do not replace knowledge of the readers.

## 10. Final Checklist

- [ ] Filename and `lesson_id` match and use one of the eight fixed categories and five Star-band codes.
- [ ] `_0001` remains the onboarding entry lesson; later sequences are changed only through authored routes.
- [ ] `reader.reading_level` contains the grade target, not the filename's `L` code.
- [ ] `reader.why_this_level` states both the readability evidence and the cognitive load.
- [ ] 100-200 words per passage part unless an exception is documented.
- [ ] Every item has one defensible answer, a reasoning chain, and specific misreadings.
- [ ] Every evidence-dependent item has the correct `show_part`.
- [ ] The help ladder does not reveal the answer.
- [ ] Student-facing language is plain, direct, and non-condescending.
- [ ] There is one primary skill and no more than one secondary skill.
- [ ] `decision_rule` and every finite route are explicit.
- [ ] Every `next_file` exists in the repository.
- [ ] Stopped sessions return to the current lesson.
- [ ] The ticket contains no PII.
- [ ] The file passes JSON validation and a cold-chat test.
