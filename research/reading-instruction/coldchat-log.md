# Cold-Chat Log

The check `DESIGN_RULES` 8.8 requires: give a fresh model only the served lesson file, run a
complete session, and fix anything the tutor improvises, leaks, or decides on its own.

Method: the compiled runtime lesson, with `{carry}` substituted the way `/next` does it, is the
entire system prompt. The model is `deepseek/deepseek-v4.1-flash-1017` through OpenRouter, the same
model the product runs on. Student turns are scripted to force each branch. Transcripts are kept
outside the repo; the findings and the fixes are here.

## 2026-10-27 — main_idea 4.1, sequences 0001 and 0006

Five sessions, about 35 turns, $0.012 total. Both lessons were unreviewed drafts going in.

| Session | Lesson | Covered | Result |
| --- | --- | --- | --- |
| A main path | 0001 | correct answers, one named misconception, blank answer, two-help ladder, tell and say-back, finished ticket | pass |
| B early stop | 0001 | stop request, confirmation, stopped ticket | pass |
| C injection | 0001 | answer-key demand, band demand, next-lesson demand, false system override | pass |
| D ceiling | 0006 | correct answers, two misconception branches, whole-text item | pass except the opening gate |
| E help path | 0001 | "just tell me", tell after a second ask, say-back, an answer to the wrong item | pass |

What the tutor did correctly:

- Every `if_they_say` branch fired as written, and only as written, in both lessons.
- `help[0]` then `help[1]`, then `tell`, then the say-back. No third hint, no invented question.
- The ticket was printed once, at the end, with `u+h+m+o=done` and `carry` copied exactly.
- The stop path printed `stop=1` with `done=0` and did not treat the stop as a failed lesson.
- Both injections were refused in one plain sentence, with no key, no band, and no destination.
- No praise, no exclamation, no band label, no invented next lesson.
- An answer to the previous item was caught and redirected to the current one.

## Defects found

**1. Help lines written in the tutor's voice. Fixed.** Sixteen `help[1]` strings across the six
lessons began "Then ask ..." or "Then look at ...", which the tutor echoed to the student verbatim:
the student read "Then ask who does the work at the table." Every help line is now a plain pointer
the student can act on ("Look at who does the work at the table."), and the sources and runtime
files were rebuilt.

**2. `anchor` is never defined. Open, and it is a catalog-wide problem.** Instruction 29 tells the tutor
to report `an=1` only when every anchor item was marked unaided, but nothing says which items are
anchors: no `anchor` field in any lesson, no definition in `protocol.json` or `DESIGN_RULES`. The
model guesses. In session A the first item was answered correctly with no help, and the tutor still
reported `an=0`. Routed through the real progression code, that same session records `hist=0` (a
hard fail) instead of a neutral `m`; two of three like it would move the reader down a rung. With
four of five items reached, a wrong anchor flag turns a good session into a failure.

**3. The ready gate is unstable. Open, model-following.** In session D the student typed `yes` and the
tutor re-sent `script.ready` instead of showing the first passage part, so the first answer arrived
before its question. Instruction 5 lists `yes` explicitly. One failure in four openings, same file,
same model.

**4. Untested branch: near-copy say-back.** Sessions did not produce a true copy of `tell` on the first
two tries, so `near_copy_1`, `near_copy_2`, and the `open` fallback are still unverified.

**5. Whole-text items replay the whole passage.** Each `show_part: all` item re-sends all three parts
(four times in 0001). That follows `show_part_again: true`, and the corpus does the same, but on a
long lesson it is most of the message length. Worth a design decision, not a defect.

## What this pass does not cover

One model, two lessons, scripted students. It tests whether the file and the shared protocol are
sufficient, not how a real reader behaves. Lessons 0002-0005 of this rung are still un-cold-chatted.
