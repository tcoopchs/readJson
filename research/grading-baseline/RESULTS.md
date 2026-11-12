# S1 results: grading baseline, 2026-11-12

12 landed Band 4 items × 8 generated answers (96 answers). The answers were written by gpt-4o-mini;
the reference labels are the agent's, under DECISIONS.md D1–D6.

## Reference check (instead of an owner spot-check)
`openai/gpt-5.6-terra` labelled all 96 answers independently. It saw no key, only the passage, the
question and the decisions.
- It agreed with the agent on 85/96 (89%), on 17 of the 18 random spot-checks, and on 15 of the 17
  policy calls.
- All 11 disagreements sit on two boundaries:
  - Not clear yet vs Not quite on vague answers.
  - A half answer that gives the end of a cause chain without the middle (A019, A083).
- Those two boundaries are where any single judge is least reliable. Neither judge is ground truth
  for them.

## Tutor scoring: rules today vs decisions added (and 4 keys patched in memory)
| model | agreement r1 → r2 | wrong accepted r1 → r2 | right rejected r1 → r2 | Not clear yet used r1 → r2 |
|---|---|---|---|---|
| deepseek v4.1 flash | 74% → 86% | 6 → 6 | 6 → 2 | 13 → 5 |
| qwen3.8 flash | 76% → 88% | 5 → 4 | 7 → 3 | 12 → 6 |
| gpt-4o-mini | 79% → 81% | 3 → 4 | 12 → 9 | 1 → 1 |

All three models agreed on 71/95 answers in round 2, up from 64/94.

## Spend
API: $0.002 (answers) + $0.086 (round 1) + $0.324 (round 2) = about $0.41.
Agent session: about $1.0 across S1 and S1b.

## Files
- `items.json`, `answers.json`
- `labels_agent.json` (pre-decision), `labels_agent_v2.json` (decided)
- `grades.json` (round 1), `round2.json` (independent labels + round 2)
- `DECISIONS.md`, `REVIEW.md`
- scripts: `gen_answers.py`, `grade.py`, `round2.py`

Nothing in `lessons/`, DESIGN_RULES or protocol.json was changed.
