# JSON Lesson File Design Ruleset

This document defines the content authoring rules for `readJson` lesson sources and the runtime
lessons compiled from them. It applies to every reading category, instructional band, and reader
target. [README.md](README.md) is authoritative for filenames, fixed categories, Band codes,
starting-lesson mapping, source layout, compilation, and progression. This document is
authoritative for passage, question, readability, routing, and lesson content. Both override older
examples when they conflict.

New lessons are authored as
`lessons/src/<category>_band_<grade>_<stage>_<sequence>.source.json` using
`schema_version: 3` and `document_type: "lesson_source"`. The readingHarness compiler combines the
source with the shared protocol and writes the runtime JSON into `lessons/`. Do not hand-write the
shared tutor instructions, common scripts, result definitions, route thresholds, or ticket
templates into a source lesson.

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

**1.2 The IRL grade controls instructional placement.** Use the whole-number part of Star's
Instructional Reading Level (IRL). Do not use the Scaled Score, Percentile Rank, ZPD, or Grade
Equivalent to choose a curriculum grade:

```text
Star IRL 5.1 -> grade 5 -> inference_band_5_1_0001.json
reader.reading_level: 5
```

IRL 4.2 and IRL 4.7 both mean grade-4 instructional material. Grade 5 begins at IRL 5.0. A passage
that scores FK 6.2 can still be appropriate for a grade-9 reader when vocabulary, background
knowledge, inference distance, and working-memory load are controlled. State that distinction in
`reader.why_this_level`.

The `reader` block and `reader.reading_level` are authoring metadata only. The compiler removes them
from the student-facing runtime lesson. Student-facing labels use `Band <grade>.<stage>` and must
not reveal a grade, IRL, or below-grade comparison.

**1.2.1 A low-load text may sit one band above its target.** Topic quality matters to older readers.
A passage they want to read is worth more than a perfectly matched score, so a work whose idea load
is at or below the band may be placed in the lower band even when its language measures higher. The
allowance is bounded:

- the measured FK must still fall inside the Common Core band for the target grade (4.51-7.73 for a
  grade 4-5 target), so the stretch is at most about one grade;
- every word above the band that carries evidence must be supported in `help[0]` or `tell`;
- `reader.why_this_level` states the gap in plain words, for example: "Ideas are one-step and
  concrete. Three words (porosity, karst, aquifer) are above the band and are supported in the first
  help."

Never stretch more than one grade, and never stretch a text whose idea load is above the band. The
two-axis rule still decides: language load may be traded down for topic quality, idea load may not.

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

**2.2 One passage per lesson; a work serves one cell.** A cell is one `(category, grade, stage)`.
When a long, good work is worth milking, it may carry every lesson in the cell. It is also fine to
draw a cell's lessons from more than one work; that is a sourcing choice, not a defect. What is fixed
is the boundary: a work serves one cell only. The step from one Band to the next always brings new
material, so the one transition a student is certain to notice stays fresh.

Never display the same passage twice. No two lessons show the same words. A repeat lets the second
lesson be answered from a student's memory of the first, which corrupts the measure rather than the
variety.

Before committing to a work, confirm two things by reading it:

- it yields six disjoint, self-sufficient passages of 100-200 words, roughly 3,000-4,500 words of
  usable text. Four lessons carry a rung and two are retry text; a work that yields only four leaves
  the push-back without new passages;
- it is internally varied: chapters on different subtopics, a report with several distinct cases, an
  essay that moves through scenes, a novella. A single-mechanism explainer yields six passages that
  test one idea, and the back half of the rung becomes practice without progress.

This needs no register. The publish validator enforces it mechanically over the whole source set: it
groups lessons by cell and by the work named in `meta.source.attribution` or `meta.source.basis`, then
compares `passage` text. A repeated passage and a work spanning two cells both fail; a cell drawing
on several works is reported as a note. Give external works their exact URL so the grouping is
reliable.

Do not generate runtime rewrites of one passage to step difficulty. Adaptation happens at authoring
time only, into a fixed passage stored in the source, and is recorded under 2.5. The tutor never
rewrites, simplifies, paraphrases, or regenerates text during a session.

**2.2.1 Genre runs in two-band blocks, not per lesson.** A band teaches one genre, so a cell teaches
one construct and the routing label stays meaningful. No fiction and nonfiction tracks: that doubles
the catalog and teaches the same skill twice.

```text
4-5 nonfiction     6-7 fiction     8-9 nonfiction     10-11 fiction     12 nonfiction
```

Two rules keep the cycle honest:

- **Only one knob moves at a genre boundary.** The first lesson of a band that changes genre sits at
  or slightly below the difficulty of the last lesson of the preceding band. The reader meets a new
  genre, not a new genre and a harder text at once.
- **The item set follows the band's genre.** Fiction cells use character motive, change, conflict,
  and the narrative signposts. Nonfiction cells use claim, cause, sequence, and the expository
  signposts. A generic inference template flattens both.

Record `meta.genre` on every lesson so a cell's genre can be audited, and a fiction lesson is never
scored with an expository key.

**Verticals that cannot alternate are exempt.** `process` and `argument_evidence` are exposition by
construct; `literary_text` is fiction by definition. Those cells follow their own genre at every band
and are never left empty to satisfy the cycle. Genre alternation applies only to `vocab`, `inference`,
`main_idea`, `text_structure`, and `authors_craft`.

**Prefer complete short stories to novel excerpts.** An excerpt cannot deliver the payoff that makes
a story worth reading, so a fiction lesson built on chapter fragments asks a reader to care about
something it never finishes. A complete story of 1,200-2,500 words fits a lesson and supports
whole-text items — theme, character change, ending-dependent inference — that an excerpt cannot.

**2.3 The passage must contain the evidence in plain sight.** Every inference, cloze, main-idea,
and author's-purpose answer must be derivable from text shown in the current lesson. If an item
depends on an earlier passage part, set `show_part` to that part. `show_part: null` is valid only
when the item is answerable from text already on screen, such as a quoted cloze sentence.

**2.4 Do not simplify the passage after the fact.** The AI presents passage text exactly as
written. If the text is too hard, rewrite the source before publishing. Do not ask the tutor to
simplify, paraphrase, or regenerate it during a session.

**2.5 Source discipline.** Every passage traces to one of three routes, and `source.basis` plus
`source.text_status` must say which:

1. **Verbatim.** Human-written source text used as written, within its license.
2. **Original.** Written for the lesson. At band 5 and above a person writes it. Below band 5, see
   2.6.
3. **Adapted.** A human-written source rewritten to the band's reading load. The rewrite may be
   produced by an AI from a named source under these conditions:

   - **The license must permit derivative works**: public domain, CC0, or CC BY. Never adapt
     NoDerivatives material, and never adapt ShareAlike material into a lesson file. Adaptation of a
     CC BY work must say that changes were made, as that license requires.
   - **A human reviews and approves the final text** before it is banked. Unreviewed output is a
     draft, whatever produced it.
   - **Adaptation may simplify, never invent.** Shorter sentences, common words, split clauses,
     removed asides. It may not add facts, examples, or explanations the source does not contain,
     and it may not change the argument or the sequence of events.
   - **Record the provenance.** `source.basis` names the base work, `source.text_status` says
     "adapted, reading load reduced," and `source.adaptation` states in one line what was done
     ("split long sentences, replaced six technical terms, dropped the second paragraph").
   - **Re-map the evidence afterwards.** A simplified sentence can delete the clue an item depended
     on. Write or rewrite every item against the adapted text, never against the original.

At band 5 and above, items are never AI-drafted: the answer key is authored. Below band 5, 2.6
applies. Never invent a citation.

**2.6 Sourcing depends on the band.** Band 5 and above: every passage is based on human-written text —
verbatim, adapted from a named work under 2.5, or written by a person for the lesson. No AI-drafted
passage and no AI-drafted answer key at any band 5 or above. Below band 5 (bands 3.x and 4.x): a
passage and the item set keyed to it may be drafted by an AI when the catalog needs volume, on three
conditions:

- a human reads and approves the whole file before it is banked;
- `source.drafted_by` names the reviewer and `source.text_status` says "drafted for the band,
  reviewed";
- every item is re-checked against the text as published, because a drafted passage carries no audit
  trail and no source to re-read.

Two habits carry over from the old 4.1-only exception:

- **Land at the band's ceiling, not its floor.** Below-5 drafting exists to fill a band with usable
  text, not to teach a register the next band does not use.
- **Keep a band's last sequence at the band's upper load.** Leaving a band should be a step up, not a
  shock.

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
that gives it away. Then use `tell` as the final authored explanation. A miss stays on the current
item through this ladder, `tell`, and say-back. It never moves the student to another item or
lesson mid-session.

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

**5.5 Exit routes must be explicit and finite.** Name the `advance`, `retry`, and `stopped`
destinations in the source lesson. The AI must never choose or name a destination. The compiler
writes those destinations into `rules.server_routes`; the server validates them and rejects a
missing or mismatched lesson at startup.

**5.6 The completion ticket carries no PII and no destination.** The AI reports the current lesson
ID and outcome counts using the shared token format. It must not include a name, student ID, email,
IP address, score history, next lesson, or signed value. The server selects the route and creates
the signed, dated next-lesson link.

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

## 7. Instructional Bands, Horizontals, and Exit Routing

**7.1 Filename convention.**

```text
lessons/src/<category>_band_<grade>_<stage>_<sequence>.source.json
```

The category must be one of the eight fixed keys in README.md. The grade is the whole-number IRL
grade from 1 through 12. The stage is an authored progression stage: 1 through 8 is reserved, stages
1 through 3 are the authored rungs per grade, and stages 4 through 8 may be appended later but never
inserted. The sequence is a lesson position from 0001 through 0008. For example,
`inference_band_5_2_0003.json` is the third grade-5 inference lesson in stage 2, the second rung of
grade 5.

The target horizontal is six lessons for one category, grade, and stage: four are expected to carry
a reader through the rung, and sequences 5 and 6 are retry text. Do not use tenths of an IRL point
as independent curriculum grades. Use stages to create finer progression inside a grade.
After compilation, the runtime file drops `.source` and is written directly into `lessons/`.

Set boundaries live in `lessons/curriculum.json`. Each set declares `expected_sequences` and a
`status` of `complete` or `incomplete`. A set may be marked `complete` only when every expected
lesson exists. The target size is a default; the server uses the set's actual sequence list.

**7.2 `_0001` is the entry lesson for a stage.**

For each category and stage, `_0001` is the starting lesson an onboarding Band key may name. Later
sequences are reached only through server-selected routes. A stage may contain fewer than six
lessons while it is being authored, but the target is six.

The server's onboarding mapping names exact lesson IDs, so adding `_0002` or later never changes
which lesson the dropdown serves.

**7.3 `lesson_id` must equal the filename without `.json`.** Never rename a lesson after its ID has
appeared in a signed bookmark.

The source records the same whole-number grade in `meta.reader.reading_level` and explains the load
in `reader.why_this_level`. The compiler removes that block from the runtime lesson.

**7.3.1 One ladder per skill.** Grade and stage are labels on a single ordered ramp. The only moves
are up and down. Sequences are the road inside a rung, not a second progression.

```text
inference: 3.1 -> 4.1 -> 4.2 -> 4.3 -> 5.1 -> 5.2 -> 5.3 -> ...
```

A move never changes the category. It follows the evidence, not the lesson count:

- **Up** when 2 of the last 3 lessons in the rung reach 4 or more of 5 items with no help.
- **Down** when 2 of the last 3 reach 3 or fewer, or when the anchor item — the first item — needed a
  help or reached `tell`.
- **Stay** in every other case, and take the next sequence in the rung. This is the normal state;
  the rung is a place a student lives for weeks, not a turnstile.
- At most one move per day. Two down-moves in a row holds the ladder and alerts a teacher instead of
  moving a third time.
- A stopped session never moves.

Six sequences per rung. Four carry a reader through it; sequences 5 and 6 exist so that a push-back
has text that has not been displayed. A down-move lands on the previous rung's middle sequence. A
rung's `_0001` sits at or below the previous rung's last sequence only at a grade boundary, because
that is where genre and register change; inside a grade the ramp rises across stages.

**Floor and ceiling.** Band 3.1 is the bottom of the catalog. Its onboarding `entries` stay empty so
no student starts there, but a down-move may serve it. Below 3.1 there is nothing: hold the student
and alert a teacher rather than serving a lesson that cannot help. At the top authored rung, hold.

**Sparse content.** While a set is incomplete, the server serves the next existing lesson in the rung
and holds at the last one it has. A move is never chosen from a set that is not complete.

The transition is server-owned. A stopped session resumes the current lesson. Lesson files still
store `advance`, `retry`, and `stopped`. Those fields do not
choose the next lesson while `on_incomplete_set` is `hold_and_alert`, and they do not choose it on
a complete set either. They are used only when the protocol selects `authored_route`.

During sparse-content development, mark the set `incomplete` in `curriculum.json`. The server then
serves the next lesson that already exists in the band. It holds a student who reaches the last
authored lesson and reports the curriculum gap. Adding the next file and restarting the server lets
the same ticket serve that file. The set stays `incomplete` until every expected sequence exists.
Never mark a partially authored set complete.

**7.4 Exit routing data is authored; threshold selection is server-owned.** Every source lesson
must contain exactly three finite destinations: `advance`, `retry`, and `stopped`.

```json
{
  "advance": {
      "next_irl": 5,
      "next_file": "inference_band_5_2_0001",
      "next_means": "The first lesson in the next inference stage.",
      "student_line": "You put most of these facts together on your own. The next reading is another inference lesson."
  },
  "retry": {
      "next_irl": 5,
      "next_file": "inference_band_5_1_0002",
      "next_means": "Another inference lesson in the same stage.",
      "student_line": "You have the basic move. The next reading is another inference lesson."
  },
  "stopped": {
      "next_irl": 5,
      "next_file": "inference_band_5_1_0001",
      "next_means": "This same lesson, so it can be finished."
  }
}
```

The shared policy in `server/config/protocol.json` decides the next lesson. The published setting
is `hold_and_alert`.

- A stopped session returns the current lesson. `stopped.next_file` must name that lesson.
- While the set is `incomplete`, `advance` and `retry` are not followed. The next existing lesson
  in the band is served. The last existing lesson holds the student.
- On a complete set, the move is decided by the window rule in 7.3.1, not by `got_there` alone.
  `advance_min_got_there` stays as the per-lesson clear threshold: one lesson clears at 4 or more of
  5 items, and the window decides whether that clear changes the rung.
- `authored_route` is the only setting that serves the stored `advance` or `retry` destination.

Startup fails when a destination is missing or `next_irl` does not match that file's grade. Write
all three destinations even though the published policy does not follow `advance` and `retry`.

At grade 12 stage 8, there is no higher authored band. Hold at that band or flag the student for a
teacher; do not invent grade 13. Adding content above the ceiling is a curriculum and server change.

The AI never fills `{next_file}` and never chooses a route. It reports only:

```text
v2|from=<lesson_id>|done=<items-with-a-result>|u=<unaided>|h=<helped>|m=<mercy>|o=<open>|an=<0-or-1>|carry=<carry>
```

`an` is 1 only when the anchor item was marked unaided, otherwise 0. `u+h+m+o` must equal `done`.
**The anchor item is the first item in the lesson**, the literal or part-level move every lesson opens
with; no separate field marks it, and a lesson has exactly one. Any result other than unaided — helped,
mercy, or open — fails the anchor, so a clear needs 4 unaided items including the first, and a helped
first item records the lesson as a hard fail. For a stopped session the line appends `|stop=1`. A referenced runtime lesson must exist before its
route is published; otherwise server startup fails.

**7.5 Stopped sessions return to the same lesson.** `stopped.next_file` must name the current
`lesson_id`. The server returns that lesson and does not follow a different stopped destination.
A stopped ticket does not replace or repeat an item mid-session and does not imply a grade change.
A stop is not a failed lesson and must not trigger a step-down.

**7.6 The ticket carries the memory.** The server is stateless by design, so a move decision cannot
depend on history the server does not hold. The continuation the server mints after a verified ticket
carries one field:

```text
carry=<stage>.<lessons-in-rung>.<history>.<downs>
```

- `history` holds up to three results, oldest first: `1` a clear, `0` a hard fail, `m` neither.
- `downs` counts down-moves taken inside this rung, so a second one holds for a teacher instead of
  stepping down again.
- Reset it on any move.
- A missing or unreadable carry means the first sequence of that rung. Losing the link costs at most
  two lessons of evidence and never moves a student up.
- A replayed carry buys a repeated lesson, never a skipped one.
- The ticket also reports the per-item result counts and whether an anchor item needed help. "No
  help" and "anchor item" cannot be decided from `got_there` alone, which counts unaided and helped
  together.
- No database, no account, no student record. A carry field is not a data model: nothing may be
  built on it that needs history longer than three lessons.

## 8. Authoring Workflow

**8.1 Draft the passage first.** Write or adapt the source text, run a readability check, and verify
the target IRL grade before writing questions. At band 5 and above the passage and items must be
human-written as required by 2.5; below band 5, 2.6 governs.

**8.2 Identify the evidence points.** For each item, point to the sentence or sentences in the
passage that support the answer. If you cannot point to the evidence, the item is not ready.

**8.3 Write the item.** Add the prompt, answer and reasoning, specific distractors, `show_part`, and
the primary skill and difficulty tags.

**8.4 Write the help ladder and tell.** Nudge toward the evidence, narrow without giving the answer,
then teach with the complete authored explanation.

**8.5 Write the misreading branches.** Name the specific misconception and author the response for
it.

**8.6 Write the three route destinations.** Choose the exact next lesson for success, the exact
later lesson for retry, and the current lesson for an early stop. Use the destination's
whole-number grade in `next_irl`. Confirm all referenced runtime files exist before publishing.

The route is chosen only after the final item. Record why each item missed, but do not change its
route until the session exits.

**8.7 Compile the source.** Run the compiler from the readingHarness repository. Do not edit the
generated runtime file. Run the compiler again with `--check` after review to confirm the source
and generated file still match.

**8.8 Test cold.** Upload the compiled runtime lesson to the AI and complete a full session. Test
correct answers, misconceptions, blank answers, the help ladder, tell and say-back, stopping, and
prompt injection. Fix every point where the tutor improvises, chooses a destination, or discloses
private data.

**8.9 Read every student-facing line aloud.** Check for condescension, worksheet cliches, vague
language, and unsupported claims.

## 9. The One Rule That Overrides All Others

If a rule conflicts with a defensible pedagogical judgment for a specific passage, the pedagogical
judgment wins. Record the reason in one sentence in `reader.why_this_level`,
`meta.authoring_exceptions`, or a nearby authored note. Do not leave a silent exception. The rules
exist to make files consistent and defensible; they do not replace knowledge of the readers.

## 10. Final Checklist

- [ ] Source uses `schema_version: 3` and `document_type: "lesson_source"`.
- [ ] Source filename and `lesson_id` match and use one of the eight categories, grades 1-12, an authored stage from 1-3, and sequences 1-8.
- [ ] The passage and items are human-written at band 5 and above; below band 5, 2.6's review and provenance are recorded.
- [ ] `_0001` remains the onboarding entry lesson. Later sequences are served by the server from the files that exist, not by the stored `advance` or `retry` fields, while the set is incomplete.
- [ ] `script_overrides.near_copy_2` is a lesson-specific say-back line. The shared instructions require it.
- [ ] `reader.reading_level` equals the whole-number IRL grade in the filename.
- [ ] The rung has six sequences: four that carry a reader through it and two kept as retry text.
- [ ] The prototype lesson has five items unless a documented exception changes that target.
- [ ] The set is listed in `curriculum.json` with its actual expected sequences and correct completeness status.
- [ ] Every live source and generated lesson has `meta.status: published`.
- [ ] A move is decided by the 7.3.1 window, is capped at one per day, and never restarts the band the student just failed.
- [ ] `reader.why_this_level` states both the readability evidence and the cognitive load.
- [ ] No displayed passage repeats anywhere in the catalog; a work never serves two cells.
- [ ] Any work expected to carry a whole rung yields six disjoint passages of 100-200 words.
- [ ] 100-200 words per passage part unless an exception is documented.
- [ ] Every item has one defensible answer, a reasoning chain, and specific misreadings.
- [ ] Every evidence-dependent item has the correct `show_part`.
- [ ] The help ladder does not reveal the answer.
- [ ] Student-facing language is plain, direct, and non-condescending.
- [ ] There is one primary skill and no more than one secondary skill.
- [ ] `advance`, `retry`, and `stopped` destinations are explicit.
- [ ] Every route destination exists in the compiled repository and has the matching `next_irl` grade.
- [ ] Stopped sessions return to the current lesson.
- [ ] The ticket contains no PII beyond the `carry` field of 7.6.
- [ ] Shared instructions, scripts, results, thresholds, and token formats were not copied into the source.
- [ ] Compiler output passes `--check` and a cold-chat test.
