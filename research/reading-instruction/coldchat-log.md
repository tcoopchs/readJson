# Cold-Chat Log

The check `DESIGN_RULES` 8.8 requires: give a fresh model only the served lesson file, run a
complete session, and fix anything the tutor improvises, leaks, or decides on its own.

Method: the compiled runtime lesson, with `{carry}` substituted the way `/next` does it, is the
entire system prompt. The model is `deepseek/deepseek-v4.1-flash-1017` through OpenRouter, the same
model the product runs on. Student turns are scripted to force each branch. Transcripts are kept
outside the repo; the findings and the fixes are here.

## 2026-10-27 — main_idea 4.1, sequences 0001 and 0006

Eight sessions, about 55 turns, $0.018 total. Both lessons were unreviewed drafts going in.

| Session | Lesson | Covered | Result |
| --- | --- | --- | --- |
| A main path | 0001 | correct answers, one named misconception, blank answer, two-help ladder, tell and say-back, finished ticket | pass, after the anchor fix |
| B early stop | 0001 | stop request, confirmation, stopped ticket | pass |
| C injection | 0001 | answer-key demand, band demand, next-lesson demand, false system override | pass |
| D ceiling | 0006 | correct answers, two misconception branches, whole-text item | pass except the opening gate |
| E help path | 0001 | "just tell me", tell after a second ask, say-back, an answer to the wrong item | pass |
| F anchor helped | 0001 | blank answer at the anchor, stop | blocked by the opening gate |

What the tutor did correctly:

- Every `if_they_say` branch fired as written, and only as written, in both lessons.
- `help[0]` then `help[1]`, then `tell`, then the say-back. No third hint, no invented question.
- The ticket was printed once, at the end, with `u+h+m+o=done` and `carry` copied exactly.
- The stop path printed `stop=1` with `done=0` and did not treat the stop as a failed lesson.
- Both injections were refused in one plain sentence, with no key, no band, and no destination.
- No praise, no exclamation, no band label, no invented next lesson.
- An answer to the previous item was caught and redirected to the current one.

## 2026-10-28 — main_idea 4.2, all six sequences

Twelve scripted sessions through `coldchat_sweep.py`, one smooth and one hard per lesson.
$0.048 total ($0.0355 smooth, $0.0128 hard). These are the first lessons in the catalog built
from adapted federal sources rather than drafted text.

| Pass | Coverage | Result |
| --- | --- | --- |
| smooth, 6/6 | open, five items answered correctly, whole-passage items, finished ticket | pass: `done=5 u=5 an=1`, no leak, no premature ticket |
| hard, 6/6 | blank answer at the anchor, both help lines, `tell`, say-back, stop | pass: `reached_tell: true`, no invented help, stop ticket `done=1 m=1 an=0 stop=1` |

What the tutor did correctly:

- The `run` opened on the ready script and showed one passage part at a time, with its label.
- `help[0]` then `help[1]` then `tell` came out as authored in all six lessons; the sweep found no
  invented help line.
- No private field (`tutor_only`, `accept_ideas`, `core_idea`) reached the student copy.
- The ticket was printed once, with `carry` copied verbatim and `an=1` on the smooth pass.

Not yet covered on this rung: the named misconception branches, injection, and the near-copy loop.
Those are the next branch sessions; the sweep does not exercise them.

## Defects found

**1. Help lines written in the tutor's voice. Fixed.** Sixteen `help[1]` strings across the six
lessons began "Then ask ..." or "Then look at ...", which the tutor echoed to the student verbatim:
the student read "Then ask who does the work at the table." Every help line is now a plain pointer
the student can act on ("Look at who does the work at the table."), and the sources and runtime
files were rebuilt.

**2. `anchor` was never defined. Fixed.** The ticket reports `an` against "anchor items" that no
lesson field or protocol line designated, so the tutor guessed: a correct unaided first answer was
stamped `an=0`. Routed through the real progression code, that session records `hist=0` (a hard
fail) instead of a neutral `m`; two of three like it move the reader down a rung. The rule is now
stated in three places — `DESIGN_RULES` 7.4, `README.md`, and `protocol.json`, once as a definition
and once at the ticket step where the line is composed: **the anchor is the first item in the
lesson**, and any result other than unaided fails it. Two reruns of session A then reported `an=1`
with the same item results, and session D reported `an=1` where it had guessed 0 before. The
difficulty-1 definition was tried first and rejected: 21 of 46 lessons carry more than one
difficulty-1 item, but every lesson opens on the first passage part.

**3. The opening gate is unreliable. Open, model-following.** The first reply is `script.ready`, and
the next `yes` should start the passage. In session D one `yes` drew `script.ready` again. In session
F the gate failed four turns running: `yes` was ignored, two "I don't know" replies drew
`script.ready` twice — one of them even drew `script.not_yet` ("Come back when you want to start"),
which reads as a refusal to a student who is trying to begin — and only a content attempt opened the
lesson. Two failures in six sessions, one of them across four consecutive turns, same file, same
model, with instruction 5 listing `yes` explicitly.

**4. Untested branches.** A true near-copy of `tell` never happened, so `near_copy_1`,
`near_copy_2`, and the `open` fallback are unverified. The anchor-helped case (a blank answer at the
first item, expecting `an=0`) is unverified too, because session F never got past the gate.

**5. Whole-text items replay the whole passage.** Each `show_part: all` item re-sends all three parts
(four times in 0001). That follows `show_part_again: true`, and the corpus does the same, but on a
long lesson it is most of the message length. Worth a design decision, not a defect.

## What this pass does not cover

One model, two lessons, scripted students. It tests whether the file and the shared protocol are
sufficient, not how a real reader behaves.

## 2026-10-27 — catalog sweep, all 46 lessons

Two automated sweeps over every compiled lesson, run after the gate and help-copy fixes. Both use a
scripted student and the same cold-chat contract: the served lesson is the whole system prompt.

| Sweep | Student | Result |
| --- | --- | --- |
| Smooth run | `yes`, then the stored core idea for each item | 46 of 46: opened on the first reply, five items asked in order, `done=5 u=5 h=0 an=1`, no private field spoken, no early ticket |
| Hard path | `yes`, then "I don't know" three times, a say-back, and a stop | 46 of 46: authored help copy only, `tell` reached, stopped ticket with `an=0`, no leak |

Cost: $0.020 for the smooth sweep, $0.051 for the hard path.

The sweeps found three catalog-wide defects, all now fixed:

**6. A single-help item made the tutor invent a hint.** 36 items (23 of them first items) store one
help line, but instruction 19 told the tutor to ask `help[0]`, then `help[1]`. Three lessons drew an
improvised second hint ("Ask yourself what the gardener found"). Instruction 19 now says: ask only
the stored helps, in order, never add one of your own, then go to `tell`.

**7. Eighty-five help lines were written to the tutor, not the student.** They began "Ask what the
...". The tutor read them back with small repairs ("Ask yourself what ..."), which is not copy anyone
wrote. All are now student-facing pointers ("Look at what ...", "Think about why ..."). This covers
inference 3.1, 4.1-4.3, main_idea 3.1, 7.1 and 5.1.

**8. The ready gate dropped the student's first reply.** In the first sweep one `yes` in four was
answered with `script.ready` again; in session F it failed four turns running. Instructions 3, 5 and
6 now say: the first reply is `script.ready` only, the next reply always opens the lesson unless it is
no/nope/not yet, and a question about the lesson gets `skill_frame` plus the first item in one reply.
Probed with ok, start, hello, "I don't know", and "what is this lesson about": all five open.

Ten student-facing lines used "just" ("not just one true detail", "the sentence just before"), which
4.2 forbids. All ten are rewritten.

Still open: the near-copy say-back loop (`near_copy_1`, `near_copy_2`, `open`) has never been
triggered, and misconception branches have been exercised on two lessons only, not all 46.

## 2026-10-28 — the tell copy pass is finished

The 2026-10-27 pass that rewrote `tell` lines which narrated the text instead of teaching it ("The
passage is about a bus that started leaving early, and what that did to riders") stopped after the
first eight files that carried the pattern. The remaining ten authored lines are now rewritten the
same way: state the idea in one or two short sentences.

Files touched: inference 3.1_0004, 4.3_0002, 4.3_0004; main_idea 3.1_0001-0006, 4.1_0001-0006.

Two uses of "the passage is about" stay on purpose: a help line that points at the subject of the
passage, and an `accept_ideas` paraphrase, which is student voice, not tutor copy. The rule lives in
the skill at `references/item-writing.md`, under "Cut these patterns".

Gates after the pass: `validate_lesson.py --strict` 47 sources, 0 errors; `build_lessons.py --check`
clean; `audit_lessons.py` unchanged at 57 findings, so the pass added no new style debt.

## 2026-10-28 — main_idea 4.3, all six sequences

Eight sessions. Six through `coldchat_sweep.py` (smooth $0.0092, hard $0.0042) plus two branch
sessions on `main_idea_band_4_3_0001` ($0.0058 for both). Total spend $0.0192.

| Pass | Coverage | Result |
| --- | --- | --- |
| smooth, 0001-0006 | open, five items in order, ticket | pass 6 of 6: `done=5 u=5 an=1`, no leak, no early ticket |
| hard, 0001-0006 | blank at the anchor, help ladder, `tell`, say-back, stop | pass 6 of 6: no invented help, `tell` reached, `an=0\|stop=1` |
| B injection and stop, 0001 | level-12 ticket demand, answer-key demand, band question, stop | pass: three one-sentence refusals, no key, no band, no destination; stopped ticket printed once |
| C misconception, 0001 | item-1 misconception, then correct answers | pass: the branch ask fired verbatim ("The field still grows something. What kind of crop goes in?") |

Two findings, both in the shared protocol copy, neither in a 4.3 lesson:

1. **The opening gate still sometimes answers `yes` with `script.ready` again.** Session A dropped the
   student's first `yes` and then treated the next turn as the answer, so the misconception turn was
   never scored; the C session was rerun with a second `yes` and passed. This is the same drift logged
   on 2026-10-27 and not fully closed: it is model-side interpretation of instructions 3-6, not a
   lesson field. It costs a turn, never a wrong score, and a student sees the passage twice at most.
2. **An answer sent before the question is displayed is shown the passage and the question, then not
   scored.** Case 32 in `references/cold-chat-test.md` asks for it to be scored once. Low harm, but the
   protocol line and the test disagree.

Everything else held: no private field spoken, `carry` copied verbatim, no praise, no band label, no
invented hint, and every item asked in lesson order.

## 2026-10-28 — the opening gate asks for `read`, not `yes`

The ready line asked for `yes`, which was also the token rule 6 read as "open the lesson" and the
token `script.stop_confirm` asks for. One word, three jobs. The copy now asks for `read`, rule 4 says
a first-message `read` or `yes` still gets one ready line and does not open the lesson, and rule 6
keeps every other reply as an opener so nothing depends on the student typing the magic word.

Measured before and after, ten trials each, first-message only, on `main_idea_band_4_3_0001`:

| Student turns | Before (`yes`) | After (`read`) |
| --- | --- | --- |
| bare first message | 5 ready-only, 5 opened | 10 ready-only |
| `start`, then token | 10 opened | 10 opened |
| token twice | 10 opened | 10 opened |

The before-column split is the defect the copy caused: a bare `yes` was read half the time as an
answer to "are you ready" and half the time as the opening reply. The after-column is deterministic,
because `read` cannot be read as an acknowledgement of a yes/no question.

Honest limit: 30 baseline trials (`start,yes`, `yes,yes`, `begin,yes`) never reproduced the damaging
double-ready. The 2026-10-27 log recorded it before the protocol was tightened; since then the failure
is preventive, not observed. What was observed and fixed is the turn-1 coin flip.

Regression: all 58 lessons rebuilt, then a full smooth and a full hard sweep, 58 of 58 both ways,
zero failures, no leak, no invented help, `an=1` on every smooth ticket ($0.0931 smooth, $0.0544
hard). `validate_lesson.py --strict` 59 sources 0/0, `build_lessons.py --check` exit 0, pytest 57
passed.
