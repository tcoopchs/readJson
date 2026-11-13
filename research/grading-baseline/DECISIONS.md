# Scoring decisions (S1), decided by the agent on the owner's instruction, 2026-11-12

Draft rules. Not yet written into DESIGN_RULES or protocol.json.

**D1. Yes/no prompts.** Rewrite every yes/no prompt to ask for the reason ("Is that shown? What in the
passage tells you?"). Until a prompt is rewritten, a bare verdict that answers the prompt as written is
Correct: the protocol grades only the job in the prompt. *Why:* a bare verdict is a coin flip and
practises nothing, so the fix belongs in the prompt, not in the student's score.

**D2. Half answers.** Not quite, then tell. A key declares its required parts. When it needs both
parts, the prompt must ask for both, and its accept list may not contain a single part. A prompt that
asks two questions ("what … and why") is split, as 3.1.7 already requires. *Why:* the 11-11 protocol
dropped the help ladder, and "say the rest" is a hint. The tell already supplies the missing link.

**D3. A true but shallower answer.** Correct, and rewrite the prompt so that the shallow answer no
longer satisfies it (3.1.6). *Why:* the student answered the question that was asked. The defect is
the prompt.

**D4. A passage-supported answer missing from the key.** Correct, and fix the key. The tutor still
never invents an accepted answer at runtime; the fix is made at authoring time, caught by the
"alternative" probe. *Why:* 3.1.1. A key that rejects a defensible answer teaches the reader that
careful reading does not pay.

**D5. Quoting the passage sentence.** Correct only when the sentence itself answers the prompt.
Reporting what happens, where the prompt asks why, what it shows, or what something did, is Not quite
(the literal reading, 3.1.7). *Why:* finding the evidence is half the move. Saying what it shows is
the other half.

**D6. Not clear yet** (added; the baseline showed the models disagree on it). Use Not clear yet only
when the answer names something from the passage that could be the key idea but cannot be pinned
down, such as an unclear "it", or a word with two readings ("earn"). An answer with no passage content
("it comes from something", "it makes things better") is Not quite. Allow one Not clear yet per item;
if the next answer is still unclear, it is Not quite. *Why:* gpt-4o-mini used it once in 96 answers,
deepseek and qwen about 13 times each, including on contentless answers. Without a bound, the student's
outcome depends on which model is the tutor.

## Owner adjudication, 2026-11-13 (sample item B, gallop rhythm)

- **A supported effect is Correct.** "It makes the ride feel fast and exciting" is right, because the
  passage's own words carry it (galloped; men "shouting, cheering, firing"; clipped sentences). The
  rule is not "no feelings"; it is "the effect must be pointable in the text". Recorded in
  DESIGN_RULES 3.1.7. The item's accepts were widened to match.
- **A contentless answer is Not quite, not Not clear yet.** "It makes things happen" gets the
  explanation, not a second prompt. D6 stands, now owner-confirmed.
- Consequence for the curated set: agreement with the owner is not the measure. Each disagreement is
  adjudicated into (a) my error, (b) an owner slip, or (c) a rule gap; only (c) changes the rules.
  Two of the six sample answers produced a rule change, which is the argument for a small set read by
  the owner rather than a large one labelled by a model.

## Owner sample, round 2 (2026-11-13): items A and C

- **A (lock keeper).** "What did a lock keeper do?" left the quantity open while the key credited any one
  task. Fixed by prompt ("Name one task …") and recorded as DESIGN_RULES 3.1.11. An answer that names
  the domain but no task ("He did stuff with the boats") is Not clear yet, not a miss: it names
  something from the passage that cannot be pinned down.
- **A5 closed.** "He did stuff with the boats" is Not quite: a noun from the passage does not earn Not
  clear yet when an empty verb carries the answer. Not clear yet needs a term that could be doing the
  explaining ("it is a short turn"). Owner and all three tutor models now agree; the sample is 18 of 18.
- **C (second bus).** Owner: C, C, C, U, M, M. This exposed that the item was marked
  `one_idea_is_enough: false` while its accepts credited one part — my earlier automated rule
  over-set the flag. 56 Band 4 items with a single-question prompt had the flag flipped back to true
  (prompts that genuinely ask two things keep false). Cores untouched.
- **U vs M rule.** Not clear yet is for an answer that takes a term from the passage without saying
  what it means for the question ("it is a short turn"). An answer with no such term ("nobody needs
  it") is a miss. A worked pair was added to the protocol, which moved all three tutor models to the
  owner's labels on both.
- **Two protocol fixes found by scoring the owner's own labels:**
  1. The tutor was told to score against `tutor_only.confirm`, which is a full sentence and raised the
     bar above the key. It now scores against `core_idea` or any single `accept_ideas` entry.
  2. An `accept_ideas` entry counts when the student says the same idea in fewer words, provided no
     quantity, negation, sequence, cause, or comparison changes.
