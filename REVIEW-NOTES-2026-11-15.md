# Review notes for the inference 5.1 stack (PRs #1, #2, #4, #5)

**Temporary file.** Delete it once the four pull requests are merged. It exists because the bot that
wrote these lessons cannot read GitHub review comments where it runs, so the notes live in the repo
instead.

Four lessons, 0003 through 0006, one per PR, each branched off the last. The lessons are good work:
licences verified (NASA and NPS, all public domain, text matching the source pages verbatim), reading
levels honest (FK 5.0–6.7 inside the grade 4–5 window), five items ascending in each.

---

## CORRECTION to the first version of these notes

The first version said to point `advance` at the next lesson in the rung. **That was my error**, and it
came from copying `inference_band_5_1_0001` and `_0002` instead of reading the rule — those two lessons
are themselves the broken ones. What the design actually says:

**`DESIGN_RULES.md` 7.4**, the worked example:

```json
"advance": { "next_file": "inference_band_5_2_0001", "next_means": "The first lesson in the next inference stage." }
"retry":   { "next_file": "inference_band_5_1_0002", "next_means": "Another inference lesson in the same stage." }
```

and all eight lessons of rung 4.1 behave that way: every `advance` names `inference_band_5_1_0001`,
every `retry` names the next sequence, and the last sequence retries itself.

The three destinations are three different moves:

| field | the move it names | destination |
| --- | --- | --- |
| `advance` | **up** — leave this rung | the next **rung** that exists |
| `retry` | **stay** — another attempt in this rung | the next sequence in this rung |
| `stopped` | the reader stopped early | this lesson |

`7.3.1` is explicit: "Sequences are the road inside a rung, not a second progression." Taking the next
sequence is a *stay*, so it belongs in `retry`. When `advance` points at the next sequence, a reader
who earned a move up is held where they are.

---

## Routes to write

The next inference rung above 5.1 is `inference_band_6_1_0001` — stage 5.2 is not authored, so that is
the next existing rung and the correct `advance` for every lesson in this set.

| lesson | `advance` | `retry` | `stopped` |
| --- | --- | --- | --- |
| 0003 | `inference_band_6_1_0001` | `inference_band_5_1_0004` | itself |
| 0004 | `inference_band_6_1_0001` | `inference_band_5_1_0005` | itself |
| 0005 | `inference_band_6_1_0001` | `inference_band_5_1_0006` | itself |
| 0006 | `inference_band_6_1_0001` | itself — the last sequence, as `_0008` does in rung 4.1 | itself |

**Same defect, pre-existing:** `inference_band_5_1_0001` has `advance: inference_band_5_1_0002`. Point
it at `inference_band_6_1_0001` in whichever PR is open when it is convenient. `_0002` already does.

---

## Verified fixed at `27df8b2`

Everything from the first review except those three `advance` fields (0003, 0004, 0005) — 0006's routes
are already right.

- **The backwards `advance` is gone** from all four lessons; nothing points back into the rung.
- **PR #2 — the lock passage is clean.** "drop **of** 8 feet", "**navigate**", "**possible**", and the
  comma splice from the flattened bullets are corrected, and the edit is recorded honestly:
  `text_status: "Adapted, reading load reduced and typographical errors corrected."`, plus an
  `adaptation` line naming each fix. That is exactly the right response to a public-domain source with
  typos in it — correct, then say you did.
- **PR #1 — q5 now carries its own anchor.** "The passage says a round shape meets less drag than a
  flat one" replaces the ordinal the reader had to guess at.
- **PR #1 — q2 credits the short correct answer.** The accepts now include "Its wings. The shape makes
  lower pressure on top.", so a reader who names the wing is not marked wrong for not naming the
  pressure first.
- **PR #5 — both Earth items ask one thing.** q4: "Name one group, other than scientists, that uses the
  satellite record." q5: "Why is that change not caused by people?" Each key answers the question the
  prompt asks, each accept list agrees with its key.
- **PR #5 — `curriculum.json`** flips inference 5.1 to `complete`, which is correct: six sequences now
  exist.

The machine gate passes at this revision: `PASS - ready for review`, 5 files, 0 errors, 0 warnings.
CI is green on all four heads.

---

## Still open

**Both earlier items are now closed at `f49fd2e`** — verify for yourself and move on.

- Routes: 0003, 0004 and 0005 advance to `inference_band_6_1_0001`; 0001 was repaired too; 0006 retries
  itself. All correct against 7.4 and rung 4.1.
- PR #5 q3: the accepts now include the probe's own sentences. Re-probed at `f49fd2e` — clean, 0 flags
  across 0003 and 0006.

### The one thing still blocking: PR #2's prose

The typos are fixed, but the passage is still not written English. From part 2 and part 3 as they stand:

> The second thing you need to know the Lift Lock doors also called Lock Gates, when they are closed
> they are pointed towards higher water aka the higher water pressure.

That sentence has no main clause: "the Lift Lock doors … when they are closed they are pointed" teaches
a reader nothing about grammar except by accident. Alongside it: "Now the back gates are close" (should
be *closed*), "Say we have a boat" and "Now that's a big question that requires some context" (spoken
register), and "aka" (not written prose). The NPS page is a transcript of an oral presentation, so this
is not a typo problem — it is the source's idiom.

A reading lesson is the model of written English the student is meant to imitate. A wrong key teaches
one thing badly; a broken passage teaches bad grammar silently, with no feedback loop to catch it. That
makes this a merge blocker, not a polish item.

**Fix:** rewrite parts 2 and 3 as full sentences, keeping every fact (two sets of gates, the pointed
gates and water pressure, the panels and the lock key, the fill-and-match sequence). Everything else in
the lesson — the items, the key, the provenance — stays. Record it:

```json
"text_status": "Adapted, rewritten from an oral transcript into continuous prose; typographical errors corrected."
```

If that rewrite is more than you can do faithfully, choose a different source: another NPS page on the
same locks, or the Historic American Buildings Survey description, which was written as prose.

The other three lessons are ready. 0003 and 0005 read cleanly as written; 0006 carries NASA's voice
(the "For example:" list flattened into separate sentences is acceptable — it reads as a list, not as
broken syntax).



---

## What to keep doing

**PR #2, q5** — "How do you know the water raises the boat, rather than a machine in the lock?" — is
the best item across the four lessons. It asks for a conclusion the passage never states and the
evidence for it. That shape is what an inference item is for, and it is worth copying deliberately
into the next lessons rather than arriving at by luck.

One habit the routes taught: **when you stub a destination, check the field against the move it
names.** `advance` up, `retry` sideways, `stopped` here. A backwards `advance` still passes the
validator, because the file exists and the grade matches — only the direction was wrong.

---

## Before you push

```bash
python3 tools/check.py --harness ../readingHarness lessons/src/<your>.source.json
python3 tools/compile.py --harness ../readingHarness
```

`check.py` must print `PASS - ready for review`. Push the source and the compiled file together.

## Merge order

**#1 → #2 → #4 → #5**, rebasing each onto the previous. Each PR changes the previous lesson's routes,
so the order carries the links. Do not squash: the rung's routing lives in those diffs.
