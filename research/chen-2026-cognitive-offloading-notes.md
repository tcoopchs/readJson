# Chen et al. 2026 — Cognitive Offloading in AI-Assisted Proof Learning

Reading notes. Source: arXiv:2610.31481v1 [cs.HC], 22 Oct 2026, 14 pages.
Eason Chen, …, Jionghao Lin, Ken Koedinger (CMU + ). Revises/extends arXiv:2602.18807 and 2509.16778.
https://arxiv.org/html/2610.31481

## One-line claim

Giving students an open-ended AI chatbot alongside their coursework raised homework scores and did
nothing for the exam they had to take without AI; more chatbot messages predicted lower exam scores,
while a feedback interface that required a submitted proof attempt showed no such penalty.

## Setting and design

- Undergraduate proof-based math course (logic, sets, relations, proof writing), CMU.
  308 enrolled; 155 consented; 153 analyzed (75 early / 78 later access).
- Two interfaces, given **together**:
  1. **Homework-feedback interface.** Student must submit a written proof first. Returns overall
     feedback plus comments tied to specific parts of the proof. Instructors supplied the homework
     prompt and a reference solution as context; instructions told the model to critique rather
     than converse. (gpt-4o-2024-08-06 or o1-preview-2024-09-12.)
  2. **AI chatbot.** No attempt required, repeated exchanges allowed. System prompt said: no final
     answers, no complete steps, use Socratic questions/scaffolds/partial hints. Students could
     still ask for direct answers and press for more.
- Randomized individual assignment to early access (after Midterm 1) vs later access (after
  Midterm 2). Exams always taken without AI or other external resources.
- Phase 1 (staggered access): only early group could use tools for Homework 5-6. Outcome: those
  homeworks + Midterm 2 (unaided).
- Phase 2 (all have access, self-selected use): usage counted between Midterms 2 and 3; outcome
  Midterm 3. 659 chatbot sessions from 106 users.
- Baseline self-efficacy: 4 items adapted from Pintrich & De Groot (1990), 1-7 scale, α=.91,
  measured after Midterm 1 — i.e. *before* use was measured, so it is a genuine prior.

## Results (the numbers that matter)

RQ1 — randomized access:
- Early-access homework during the exclusive window: **+2.56 points** (SE 1.22, 95% CI [0.17, 4.94],
  p=.036), controlling for Homework 1-4 average. Raw: HW5 98.16 vs 95.77; HW6 100.48 vs 95.91.
- Midterm 2 (no AI): **no significant difference**, B=-2.47 (95% CI [-5.60, 0.66], p=.122).
  Direction was actually slightly negative.
- Interpretation: the homework gain did not transfer to unaided performance on similar problem
  types with different questions. Classic assistance dilemma (Koedinger & Aleven 2007).

RQ2 — who uses what, and what it predicts:
- 106/152 used the chatbot; 90/152 requested homework feedback.
- Holding Midterm 2 constant, **+1 point self-efficacy → 39% fewer chatbot messages** (p<.001) and
  **31% fewer feedback requests** (p=.002). Prior grade was not a significant predictor of use
  (IRR .982, p=.056; .989, p=.393). So it is confidence, not prior achievement, that drives use.
- **Each chatbot message → -0.0302 exam points** (95% CI [-.0567, -.0036], p=.026; N=148), i.e.
  **-3.02 points per 100 messages**, controlling for self-efficacy, Midterm 2, and feedback use.
- Robust to adding access-arm assignment (B=-.0284, p=.031) and to log(1+x) counts (B=-1.53, p=.007).
- **Homework-feedback requests: positive but not significant** (B=+0.084, p=.131). No penalty.

RQ3 — mediation (N=148, 5,000 bootstraps):
- Indirect path self-efficacy → chatbot use → Midterm 3: **B=+.622** (95% CI [.121, 1.560],
  Holm p=.021). One point lower baseline self-efficacy ≈ 0.62 fewer exam points *through chatbot
  use alone*.
- Path through Midterm 2: +1.975 (p<.001). Paths through feedback: none significant.
- Direct self-efficacy effect on M3: B=4.18 (β=.307, p<.001).

## Dialogue evidence (the mechanism, illustrated)

Intent coding: 80-session random sample, two undergrad coders, κ=.780, then a GPT-5.2 classifier
(κ=.84 vs consensus on the same 80 — same-dev sessions, not a held-out test, which the authors flag).
Labels: help-seeking (explanation/guidance), answer-seeking (complete answer or full solution),
other/meta.

- **Case A (answer-seeking).** "Can you solve this? I'm going to try to make sense of your
  solution." Tutor offers the CRT construction and asks the student to verify it. Next student
  message: "Could you do the next step" — the invitation to verify is not taken up. Stated learning
  goal coexists with delegated reasoning. (The tutor also contains math errors: it swaps the
  inverses and assumes ms≡1 (mod n), which is not given.)
- **Case B (help-seeking).** Student lays out their own counting method for a card-hand problem and
  asks why it fails. Tutor asks a Socratic question, then gives an **incorrect** diagnosis
  ("overcounting" — the real issue is omission, not double counting). Student: "I am not sure."
  Moral: asking the student a question is not sufficient; the question must target the actual error,
  and neither withholding the answer nor eliciting another turn makes the guidance correct.
- Neither case ends with the student explaining the resolved reasoning.
- Interview (19 students): "I think, because I have access to [system name], I actually tend to
  forget a lot of things." And: AI made them feel more confident *after* a correct solution but not
  more confident with new problems.

## Authors' design conclusions

- **Recommend against an open-ended chatbot as a tutor.**
- Build the tutor **into the course activities**, and require students to **attempt and explain their
  reasoning before receiving further help**.
- Feedback should be **on the student's own work** — the attempt is what makes help diagnosable.
- Instructors: ask students to explain AI-assisted solutions in their own words; treat an answer
  request as a signal of where the student is stuck, not as misconduct; do not let usage labels
  drive grading.
- Evaluate on **both** AI-supported work and later independent performance. "Finished the assignment"
  and "used AI a lot/little" are both insufficient outcome measures.
- Proposed next study: 3 arms — answers, hints-without-answers, feedback-on-submitted-attempt —
  holding model and content constant, measuring immediate and unaided later performance.

## Limits (do not over-read)

- One course, one institution, proof writing, 153 consenting students; self-selection into consent.
- Access was randomized, **interface choice was not** — Phase 2 is observational, so the usage-exam
  association can carry unmeasured student differences (time on task, outside AI use, motivation).
  The authors call offloading an *interpretation*, not a measured mechanism: mental effort and use of
  received reasoning were never measured.
- The two interfaces were bundled in the randomized arm, so RQ1 cannot separate their effects; the
  differential usage slopes are not a test of different interface effects (Gelman & Stern).
- Exam is the ordinary course midterm, not a designed transfer or delayed-retention test.
- Counts combine users and nonusers; can't distinguish adoption from intensity.
- Labels describe the first message only; a session can start help-seeking and end answer-seeking.
- Classifier validated on its own prompt-development set.

## Why this hits a reading tutor harder than it hits a proof tutor

The paper's dependent variable is unaided construction of reasoning. A reading app's analogue is not
"did the student answer the in-app item" but "can the student read an unseen passage and answer
without scaffolds." The same two failure modes transfer:
1. **Scaffold replaces the work.** Telling the student the answer, or the reason, before they have
   committed to an interpretation, produces in-app success and no transfer — exactly the +2.56 / 0
   pattern.
2. **The least confident students consume the most help.** Self-efficacy, not prior score, drove
   usage here. Any hint economy that lets the unsure student click through to the answer will
   concentrate the damage on the students who most need to practice.

## Open questions for our design discussion

- Where in readJson can a student obtain the answer or the reason without first producing an attempt?
- Does the harness log attempt-before-help, and could that be an outcome variable at all?
- Do we have any unaided measure (cold passage, no scaffolds) as the outcome of record?
- Do our `if_they_say` branches ever *explain* rather than probe the student's stated misreading?
  (Case B: a probing question aimed at the wrong error is worse than useless.)
