# Protocol change — 2026-11-11

Status: live on `main` (readJson `88972ca`, readingHarness `2018a89`).

## The change

A wrong answer no longer enters a help ladder. The tutor now says:

1. **"Not quite."**
2. `tutor_only.tell` — the full stored explanation.
3. **"Say that back in your own words."**

Then it advances. There is no `help[0]`, no `help[1]`, no `if_they_say` question, and no
attempt to coax the answer.

Result mapping (unchanged ticket/server contract):

| Student path | Result | Counts toward `got_there` |
| --- | --- | --- |
| Correct first try | `unaided` | yes |
| Wrong, then a good say-back | `mercy` | no |
| Wrong, then a failed say-back | `open` | no |

`helped` is now unreachable. `unaided + mercy + open` still sums to `done`; the anchor is still
item 1; `advance_min_got_there` still counts unaided only. No server, ticket, or progression change.

## Why

A real exchange on the Grant lesson (`authors_craft_band_4_1_0002`, item 3):

- The student read "My horse was under fire only at street crossings" as describing the outward
  ride, and said the return "simply says he made it." That is a referent error, not a wrong
  inference.
- The tutor answered: "Not quite. The horse was under fire at the street crossings, which shows
  that the ride was dangerous." That is the explanation, not a help. It skipped the stored
  `help[1]`.
- The student then echoed "that it was dangerous," and the tutor said **"Correct."** It had
  delivered the answer and then marked the echo as unaided understanding.

The failure had three parts: the model improvised a hint, skipped the stored ladder, and
confirmed a parroted answer. It is not a one-off wording problem — it is the model having too
many degrees of freedom inside a turn. The new flow removes those degrees of freedom and keeps
immediate corrective feedback: one explanation, one say-back, next question.

## What does not change

- No lesson source changed. `help` and `if_they_say` remain in every item and are still
  schema-required; the flow just does not use them.
- Every compiled lesson was rebuilt, because the protocol is embedded in each runtime file.
- The ticket format, `tickets.py`, `progression.py`, and the anchor rule are untouched.

## Impact to discuss

1. **Teachability.** The student now reads the explanation instead of producing the answer after
   a hint. The say-back is the only generative act left. Is that enough for a lesson, or does it
   become a test with commentary?
2. **Data.** `helped` is gone. `mercy` and `open` now carry the "was told" signal. Placement is
   cleanly first-attempt-correct. Is the routing threshold still right?
3. **Misconception specificity.** A generic `tell` explains the right answer but not necessarily
   the student's specific mistake. The "which ride" case needs a richer `tell` or a branch that
   names the referent error. This is authoring per known confusion, not a catalog rewrite.
4. **Copy audit.** Some `tell` strings are tutor instructions, not student copy. Grant item 4 is
   the example: "Point to the sentence… Explain that…" would be read aloud.
5. **Docs are stale.** `DESIGN_RULES` 6.4/8.3 and the `readjson-lessons` skill still describe the
   help ladder, attempt-before-help, and the `helped` category. The protocol is now the source of
   truth; the docs need a follow-up pass.
6. **Cross-model behavior.** Gemini was the model in the observed exchange. DeepSeek follows the
   new flow; `gpt-4o-mini` prints script keys literally and skips the ready line. The outcome
   words are now spelled out for that reason.

## Related changes the same day

- `DESIGN_RULES` 2.5/2.6: the band-5 pre-approval gate was removed. Every band now records
  `drafted_by` / `text_status` and relies on the random spot-check rotation; `reviewed_by` is
  written only when a person actually read the file. The passage still traces to human-written
  text; an AI may adapt, never invent.
- Poe moved to `authors_craft_band_12_1_0001` (verbatim, FK 14.8/13.1/25.6; part 3 is above a
  normal grade-12 load and is flagged for review).
- The other five Grant/Thoreau/Farmer/Brokaw/Darwin lessons stay at Band 4.1 for level review.
  That set is now incomplete (5/6, `_0001` gone) and its onboarding entry points at `_0002`.
- Outcome feedback was added and then fixed twice: first the protocol said "say script.correct"
  and weaker models printed the key; now it says "Correct.", "Almost.", "Not quite." literally,
  and the rule sits after the opening-gate instructions.

## Follow-up: the say-back gate

The first Gemini retest showed the new flow failing in two places:

- Item 3 was marked **"Correct."** for a mechanism answer ("he rode so fast the enemy fired after
  he crossed"), then the confirmation supplied the danger idea the student had not said.
- Item 4 looped on the say-back, then accepted **"no"** as **"Correct — that's in your words."**

Fixes:

- `Correct.` only when the answer states the idea in `confirm`. A related detail or a mechanism
  is a miss: `Not quite.` + `tell` + say-back.
- Say-back: one re-ask at most. A refusal (`no`, `idk`, blank), a literal restatement, or a
  non-answer closes the item as `open` and advances. Never `mercy` on a refusal.
- Near-copy gets one re-ask; if the next reply is still a near-copy, a refusal, or does not
  state the idea, the item closes `open`. No third ask.
- A wrong first answer is never `unaided`. The item closes as `mercy` or `open` only.
- The ticket must satisfy `unaided + helped + mercy + open == done`; the model recounts before
  printing.
- Item 3 gained a `partial` for the speed/safety reading and for the outward-ride referent
  error. Item 4 gained a `partial` for the literal "not injured / safe" reading, and its `tell`
  was rewritten as student copy.

Replay result on `authors_craft_band_4_1_0002`:

- Item 3: **Not quite.** + tell + say-back; a good say-back → **mercy**.
- Item 4: **Not quite.** + tell; `no` → advance with `open`, no false mercy.
- Ticket: `done=5|u=3|h=0|m=1|o=1|an=1`, consistent.

## Question design: the prompt must name the move

The second Gemini retest exposed a deeper cause than the say-back gate. Item 4 asked "What does this
plain phrase show about the ride?" — "He was safe" is literally correct. Item 3 asked "What does the
sentence about street crossings show about the writer's ride back?" — "He was safe" and "he rode fast"
are both defensible. The keys wanted danger/understatement, so the model had to guess whether the
literal answer counted; it guessed differently on the two items.

Rewrites:

- Item 3: "The writer says his horse was under fire at the street crossings. What does that sentence
  show about the danger of the ride?"
- Item 4: "The writer called the ride 'an exposed one', and he got out 'without a scratch'. What does
  that plain phrase make the danger sound like?"

The skill now carries a prompt-stem table by category and a literal-answer test: answer the prompt
literally from the passage before storing a key; if the literal answer is defensible but not the key,
rewrite the prompt. The design check asks whether the prompt names the move it grades.

Replay: "He was safe" and "It was easy" now miss; "the ride wasn't a problem for him" closes open
instead of being accepted as a say-back.

## Carry placeholder

The ticket template has `{carry}` but no lesson supplied it; Gemini wrote `carry=none`, which the
server rejects. Compiled `rules` now includes `"carry": ""`, and the protocol says to print `carry=`
when it is empty. The model still guessed `1.0..0` in replay; the real carry is session state, so the
next fix is for the server to inject it when serving the lesson, not for the model to invent it.
