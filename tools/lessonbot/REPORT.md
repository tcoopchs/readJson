# LessonBot test — band 4, authors_craft 4.1

Date: 2026-11-11
Branch: `lessonbot-test-band4` (created from `main` at `c96c75f`)
Status: **rung authored; machine gates, fidelity gate, and cold-chat sample pass. Not committed,
not published. Reviewer findings adjudicated.**

## Verified on the re-run (DeepSeek author / Qwen reviewer)

| Check | Result |
| --- | --- |
| Compile and `--check` | pass |
| `validate_lesson.py --strict` (6 sources) | pass, 0 errors |
| `audit_lessons.py` scoped to the rung | pass (corpus has pre-existing findings in older cells) |
| Corpus reuse | pass, no repeated passage, no cross-cell work |
| `fidelity_gate.py` (independent) | pass: no invented question, hype, name, number, or control character |
| Cold-chat smooth, sample of 2 (lessons 3, 4) | 2/2: opened, 5/5 asked, ticket `done=5 u=5 an=1`, no leaks |
| Cold-chat hard, same sample | 2/2: reached tell, mercy recorded, no invented help, no leaks |
| Spend | **$0.31** of the $10 cap (343 model calls, including retries) |

Measured passages: 105-146 words per part, FK 4.7-7.6, all inside the band-4 window.

## Reviewer adjudication

The Qwen reviewer is useful as a finding generator but too literal as a pass/fail gate. On the
sample it flagged three real issues, all fixed:

1. Lesson 4 item 3 asked what warming does to yeast, which the passage only implies; the prompt
   now asks what the word "paused" suggests.
2. Lesson 3 had dropped the source's "commonly" from "make pretty clean work of it", changing the
   claim; restored.
3. Lesson 4 item 5 carried an implausible misconception branch; replaced.

The rest were overreach and are not defects: `quadrupeds` -> `four-legged animals` and
`suspended` -> `paused` are the common-word simplifications 2.5 requires; the help line it called
"non-existent" quotes a sentence that is present verbatim; and asking why an author repeats a word
is the `authors_craft` move, not an unsupported inference. `show_part: "all"` displays every part,
so an item comparing parts is answerable.

## Still owed

- Text-bank rows for the six lessons (measured span, central idea, supports, L/I/S/K scores).
- Reviewer calibration: a rubric that judges meaning, not token identity, before it can be a gate.
- Commit and publish decision: nothing is committed on `lessonbot-test-band4`.

## Fix applied after the failure

The free-rewrite adapter was replaced with a grounded editor:

- The source is split into three contiguous groups, one per part.
- The model may only emit one line per numbered source sentence: `keep`, `drop`, or
  `simplify|<text>`. It cannot add a sentence, so it cannot invent one.
- Every simplified line is checked against the source sentence it came from: shared content
  words, numbers, names, question marks, hype words, and control characters.
- A part that misses 100-150 words or the FK window is revised with the exact count, not a
  vague instruction.
- Authoring model switched to `deepseek/deepseek-v4.1-flash-1017`; the reviewer to
  `qwen/qwen3.8-flash`.
- Items are generated one per call (five focused prompts), not one large JSON blob.

On lesson 3, the worst offender in the first run, the fix removed all five invented
questions, the hype, and the control characters, and produced a passage that follows
Thoreau's sentences and a craft item on his word "planted".

## What was run (first run)

- Harness: `tools/lessonbot/bot.py` (one process, one rung, hard stop on a gate failure).
- Plan: six lessons, one rung, `authors_craft` band 4.1.
- Sources: six human-written public-domain works, one per lesson, license and URL recorded
  in `plan.json`; excerpts in `tools/lessonbot/sources/`.
- Budget: $10.00 cap; actual model spend **$0.0510**.
- Authoring: every passage adapted under DESIGN_RULES 2.5 from the named source. No passage
  was generated from scratch.

## Topic variety (passed)

| Seq | Domain | Subject |
| --- | --- | --- |
| 1 | arts and language | Poe on how a poem is composed |
| 2 | history and people | Grant on a street crossing under fire |
| 3 | science and nature | Thoreau on birds carrying cherry seeds |
| 4 | food and farming | Farmer on telling bread flour from pastry flour |
| 5 | work and trade | Brokaw and Starr on why a driver must know the car |
| 6 | science and nature | Darwin on linked variation |

Five distinct domains, no adjacent repeat, spanning 5 of 7. The user's list is covered
(classic education, military history, botany, cooking, car repair, biology).

## Gates (passed)

- `build_lessons.py` compile and `--check`: pass.
- `validate_lesson.py --strict` on the six sources: pass after normalizing `say_back`,
  `one_idea_is_enough`, and exclamation marks.
- Corpus reuse: pass, no `source.passage-repeat`, no `source.work-cross-cell`.
- `audit_lessons.py`: no finding in this rung; the corpus carries pre-existing findings in
  `main_idea` and `text_structure` cells.

## Defects found (terminated the run)

1. **Invented content in lesson 3 (Thoreau).** The passage adds rhetorical questions and
   metaphors that are not in the source: "Have you ever wondered how trees grow?", "How cool
   is that?", "Isn't nature clever?", "a secret garden, ready to bloom", "a beautiful puzzle
   of trees growing together". DESIGN_RULES 2.5 permits simplification, never invention.
   This is the most serious defect: the lesson teaches an invented voice, not Thoreau's.

2. **Corrupted punctuation in lessons 3 and 4.** The source JSON contains `\u0019` and
   `\u001a` where an apostrophe belongs: `It\u0019s`, `Isn\u001a0t`, `Pillsbury\u0019s`.
   The model emitted control characters in place of the smart quote; `json.dumps` wrote them
   as escapes. `validate_lesson.py --strict` does not catch control characters.

3. **Provenance mismatch in lesson 4.** `source.adaptation` says "dropped brand names", but
   the passage keeps `King Arthur`, `Pillsbury's Best`, and `Best St. Louis`. The record and
   the text disagree, which defeats the point of recording the adaptation.

4. **Help lines leak the answer category.** Lesson 4 item 1 asks for a fact about choosing
   flour, and `help[0]` says "Look for specific brands mentioned" — the brands are the answer.
   The rule is that a help line points at evidence or narrows; it never names the answer.

5. **Near-zero source overlap across the rung.** Longest shared 5-gram counts were 0/319,
   6/330, 5/330, 0/307, 0/324, 13/320. Rewriting to the band is allowed, but a full paraphrase
   with no retained phrasing is what let lesson 3 drift into invented prose, and it leaves no
   text to re-read when an item is challenged.

6. **Text-bank rows were not written.** The skill requires the six rows (measured span,
   central idea, supports, L/I/S/K scores) in the same commit as the rung. The bot wrote the
   lessons only.

## Root cause

The adapter prompt asked for a grade-4 rewrite that "keeps the author's craft visible", but it
did not forbid new rhetorical questions, new metaphors, or a change of register. The model
optimized for a lively children's-magazine voice, which is exactly the failure the user's
"all reading samples must come from human authors" rule is meant to prevent. The gates check
schema and reuse; they do not check fidelity to the named source, and they do not detect
control characters.

## Recommendation before any further run

1. Make adaptation **verbatim-first**: prefer a short verbatim excerpt, and allow rewriting
   only to shorten sentences and swap rare words. Forbid new questions, metaphors, examples,
   and any sentence without a source sentence behind it.
2. Add a **fidelity gate**: per-passage 4-gram overlap against the named excerpt, a ban on
   question marks the source does not contain, and a banned-hype scan (`Have you ever`,
   `How cool`, `Isn't`, `amazing`, `wonder`, `secret`, `beautiful`).
3. Add a **control-character sanitizer** (`\x00-\x1f` → apostrophe or removed) before writing,
   and a validator check for it.
4. Use a **stronger adapter model** or per-part calls with the source sentence quoted for each
   rewritten sentence.
5. Write the text-bank rows in the same commit, and require the six rows before the rung is
   called built.
6. Keep the human spot-check: the second-model review found lesson 3 and 4 in a sample of two,
   which is a 100% defect rate in the sample and enough to reject the rung.

## Repo state

Uncommitted on `lessonbot-test-band4`: six `lessons/src/*.source.json`, six compiled
`lessons/*.json`, a modified `lessons/curriculum.json`, and the new `tools/lessonbot/`.
`git checkout main` (or deleting the branch) restores the pre-test state. Pre-existing
uncommitted files (`research/reading-instruction/sources.md`, `response-format.md`) were not
touched.
