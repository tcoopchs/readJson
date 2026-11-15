# Review notes for the inference 5.1 stack (PRs #1, #2, #4, #5)

**Temporary file.** Delete it once the four pull requests are merged. It exists because the bot that
wrote these lessons cannot read GitHub review comments where it runs, so the notes live in the repo
instead.

Four lessons, 0003 through 0006, one per PR, each branched off the last. The lessons themselves are
good: licences verified (NASA and NPS, all public domain, and the text matches the source pages
verbatim), reading levels honest (FK 5.0–6.7 inside the grade 4–5 window), five items ascending in
each. What follows is what has to change before they merge.

---

## Blocker common to all four: `advance` points backwards

Every lesson in the stack has:

```json
"advance": { "next_file": "inference_band_5_1_0001" }
```

`advance` means **this reader cleared the lesson, send them on**. Pointing it at the first lesson of
the same rung sends the reader backwards, so clearing a lesson would demote them. The rung's own
existing lessons show the convention:

- `inference_band_5_1_0001` → `advance: inference_band_5_1_0002` (the next lesson)
- `inference_band_5_1_0002` → `advance: inference_band_6_1_0001` (the next rung)

Correct destinations for this stack:

| lesson | `advance` | `retry` | `stopped` |
| --- | --- | --- | --- |
| 0003 | `inference_band_5_1_0004` | `inference_band_5_1_0004` | itself |
| 0004 | `inference_band_5_1_0005` | `inference_band_5_1_0005` | itself |
| 0005 | `inference_band_5_1_0006` | `inference_band_5_1_0006` | itself |
| 0006 | `inference_band_6_1_0001` | `inference_band_6_1_0001` | itself |

The habit to carry: **the last lesson of a rung advances to the next rung**, never to a lesson inside
the rung it just finished. And `retry` must never name the lesson itself — a reader who needs another
attempt needs different text.

Rule: `DESIGN_RULES.md` 7.4. The destinations are authored, not chosen by the tutor, so they have to be
written to behave the way their names promise.

---

## PR #1 — `inference_band_5_1_0003` (aerodynamics)

### q5 refers to a shape the reader cannot see

> Name one shape that meets less drag than the shape next to it in the passage.

"the shape next to it in the passage" is an ordinal the reader has to guess at. A prompt must carry its
own anchor. Either name them — *"The passage says a round shape meets less drag than a flat one. What
does that tell you about why a shape is chosen?"* — or quote the sentence they appear in. The same
applies to `confirm`, `tell` and every branch.

Rule: `DESIGN_RULES.md` 2.3.1 and the skill's "refer to text precisely".

### One correct answer is missing

The key probe (three tutor models) rejected

> Airplanes go up because of lift from their wings.

for q2 ("A balloon rises because the air inside is light. What sends an airplane up instead?"). That
answer is right: lift is the force. The key prefers the pressure difference, which is fine — the `tell`
teaches it — but a correct shorter answer must not be marked wrong. Add to `accept_ideas`:

```json
"lift from the wings sends it up",
"the wings make lift"
```

---

## PR #2 — `inference_band_5_1_0004` (C&O Canal lift locks)

### The passage carries the source page's typos into the lesson

Verbatim is faithful, and it is faithful — those errors are really on the NPS page. But a reading
lesson is a model of written English, so a student must not meet:

- "averaged a drop **if** 8 feet" → **of**
- "Boats can **navagate**" → **navigate**
- "600 feet of elevation **possibl**" → **possible**
- "Lift Locks created flat water levels, this limited the amount of water current" — a comma splice
  left by flattening the page's bullet list into sentences

Fix them, then record that you did:

```json
"text_status": "Adapted, reading load reduced and typographical errors corrected."
```

and one line in `source.adaptation` — "corrected three typographical errors, joined the bullet
fragments into sentences". U.S. federal text is public domain, so a derivative is permitted; recording
it is the point of the field.

Better still, rewrite part 1 as prose. "Lift Locks are important for many reasons. Here are just a
few:" reads like a bulleted page with the bullets removed.

Rule: `DESIGN_RULES.md` 2.5 — adaptation may simplify and correct, never invent, and must be recorded.

### What to keep

q5 — "How do you know the water raises the boat, rather than a machine in the lock?" — is the best item
in the four lessons. It asks for a conclusion the passage never states, plus the evidence for it. Write
more like that.

---

## PR #4 — `inference_band_5_1_0005` (Project Mercury)

No scoring problems: the probe found nothing across the five items, and q5 earns its difficulty-3 tag.
The only change is the `advance` destination in the table above.

---

## PR #5 — `inference_band_5_1_0006` (Earth)

Marking the rung `complete` is correct: 0001 and 0002 already existed and this supplies the last of the
six. Three fixes besides the routes.

### 1. q5 asks two questions and the key answers one

> Earth's distance from the sun changes from January to July. **What is that change, and what in the
> passage tells you it is natural** rather than caused by people?

Two jobs — and the item is also marked `one_idea_is_enough: false` while every accept answers only the
first. The tutor cannot demand two parts and credit one. Pick a shape:

- **One job.** "Earth's distance from the sun changes from January to July. Why is that change not
  caused by people?" — key: the change is natural; the orbit brings Earth nearer in January and
  farther in July.
- **Two parts, declared.** Keep the prompt, keep `false`, and make every accept state both parts with
  no single-part accept in the list.

Rule: `DESIGN_RULES.md` 3.1.7 (one job per prompt) and 3.1.9 (`one_idea_is_enough` must agree with the
prompt and the accept list).

### 2. q4 has the same shape, milder

> Name one group, other than scientists, that uses the satellite record, and say what that group does
> with it.

The accepts each carry a group plus its use, so it mostly works, but the prompt asks two things while
claiming one idea is enough. Cut it to "Name one group, other than scientists, that uses the satellite
record." and let the accept carry the use.

### 3. One correct answer is missing

Two of three models rejected

> Both kinds help us understand Earth better.

for q3 ("Why keep both kinds in the record?"). The key says they "belong in the record scientists use to
predict"; "understand better" is the same idea at lower resolution. Add:

```json
"both kinds help scientists understand and predict what Earth will do"
```

---

## Before you push

```bash
python3 tools/check.py --harness ../readingHarness lessons/src/<your>.source.json
python3 tools/compile.py --harness ../readingHarness
```

`check.py` must print `PASS - ready for review`. Push the source and the compiled file together.

## Merge order

**#1 → #2 → #4 → #5**, rebasing each onto the previous. Each PR changes the previous lesson's
`advance`, so the order carries the links. Do not squash: the rung's routing lives in those diffs.
