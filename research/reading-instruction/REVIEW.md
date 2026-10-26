# Review and Decisions

## Scope decisions (Section 1)

**Population.** Older students: grades 6-12 plus postsecondary/adult learners reading below
grade level. Early-elementary evidence is used only when it describes a mechanism that plausibly
transfers (for example, inference distance), never as direct proof for this population.

**Skill focus.** Comprehension, vocabulary in context, and text-structure/craft decisions that can
be scored from a stored key. Decoding, fluency, and pronunciation are out of scope except when a
word-level gap blocks comprehension; in that case the lesson supplies the support inline.

**Text types.** Fiction and nonfiction both in scope. Narrative and expository passages get
separate question templates because they demand different inference work.

**Material rule (user decision).** Passages are human-written and free to use: original work
written for the lesson, public domain, or permissive license (CC BY / CC0). No AI-drafted
passages. Modern text by default. Canonical old text only at the top grade (11-12).

**Placement rule (user decision).** Reading level is not Lexile alone. Score language load and
idea load separately. A simple-sentence passage with stages, dependencies, or abstraction can sit
above its readability score.

**Protocol rule.** The AI executes within one chat, with no human facilitator and no open
discussion. Every instructional move must be converted into a stored prompt, accepted-idea set,
misconception branch, help line, tell, or say-back. Moves that cannot be stored are out of scope.

## The five questions the survey answered

1. What instructional practices have credible evidence for older readers, and how strong is each?
2. How do experienced instructors and authors choose a text, and how do they separate language
   difficulty from idea difficulty?
3. How do they design and sequence questions for comprehension, inference, vocabulary, structure,
   literary text, author's craft, and argument?
4. How do they write answer keys, acceptable paraphrases, distractors, and feedback so scoring is
   defensible?
5. Which of those practices survive translation into a single-chat AI lesson with no teacher, and
   which must be redesigned?

## Resolved questions for the user

| # | Question | Why it changes the work |
| --- | --- | --- |
| Q1 | Is the primary reader a high-school student, an adult learner, or both? | Adult evidence stresses different motivation and dignity constraints. |
| Q2 | Is the old-text cutoff grade 11 or grade 12? | Resolved: grades 11-12 may use canonical old text. |
| Q3 | For fiction, is the goal literary analysis, inference, or engagement first? | Changes the question ladder for `literary_text` and `authors_craft`. |
| Q4 | Should model lessons use existing repo placeholders or brand-new sequences? | Resolved: use banded filenames and banded sequences. |
| Q5 | Is a 5-item prototype still acceptable? | Resolved: five items per prototype lesson. |

## Conflicts and cautions

- `README.md` and `DESIGN_RULES.md` both require human-written passages. AI drafting is not
  allowed.
- Most adolescent evidence is about classroom instruction with a teacher. The app removes the
  teacher, so effect sizes do not transfer directly.
- QtA depends on open discussion. Only its question moves transfer; its discussion mechanics do
  not.
- Text-complexity systems assume a human judgment layer. The app needs a written rubric that an
  author applies consistently.

## Decisions added in Sections 2-4

- Do not lower the passage band by default. The Lupo ninth-grade RCT found no comprehension
  benefit from easier texts for most students. Scaffold the stretch text instead. [13]
- Each lesson should include at least one gist/main-idea move and one text-joining inference,
  because those are the comprehension practices with strong evidence. [9, 17]
- Word-level support stays available in comprehension lessons; older readers are not a single
  profile. [12, 15, 21]
- Adult lessons must be purposeful, respectful, and free of remedial framing. Relevance and
  self-efficacy are instructional variables. [18, 19]
- Only Right There, Think and Search, and text-supplied Author-and-Me questions may be scored.
  On My Own questions are banned. [22, 27]
- The part-level ladder is anchor -> join -> interpret -> optional craft -> optional synthesis.
  Craft before facts is a design error. [4, 26]
- Fiction uses Notice and Note signposts as authoring prompts; nonfiction uses the nonfiction
  signposts. Student copy does not use the jargon. [24, 25]

## Section status

- Section 1: complete. Files: `sources.md`, `evidence-table.md`, `REVIEW.md`.
- Section 2: complete. File: `evidence-2-adolescent.md`. Sources 9-15. Cost delta $0.0067.
- Section 3: complete. File: `evidence-3-adult.md`. Sources 16-21. Cost delta $0.0071.
- Section 4: complete. File: `question-typology.md`. Sources 22-28. Cost delta $0.0072.
- Section 5: complete. File: `complexity-rubric.md`. Sources 29-34. Cost delta $0.0077.
- Section 6: complete. File: `item-writing.md`. Sources 35-41. Cost delta $0.0104.
- Each section stayed under the $0.02 cap. Total for Sections 2-6: $0.0391.
- Stopping here by user decision. Sections 7-9 (synthesis, model lessons, integration) are not
  started.
- The survey is a design input, not an efficacy study. The next useful step is a model lesson and
  a cold-chat test, not more retrieval.
