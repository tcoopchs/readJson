# Grading baseline — your review (S1)

Twelve Band 4 items, 96 student answers written by `gpt-4o-mini`. I labelled them all, then three tutor models scored them under the live protocol rules. Your part is two lists: **policy calls** (rules that aren't written yet) and **spot-checks** of my labels. Reply with the decision letter and any labels you'd change, e.g. `D1 a, D2 b, … ; spot: 7 MISS`.

Passages and keys are in `items.json`, and every row is in `labels_agent.json` and `grades.json`, all in this folder.

## Part 1 — policy calls (5 decisions, 17 answers)

### D1. A yes/no prompt answered with the verdict only.

Options: a) Correct: the prompt asked only yes/no  b) Not clear yet: ask for the reason  c) Rewrite the prompts to ask "…and why?" (then a bare verdict is half an answer, see D2)

| ID | Question | Student answer | My label | 3 models | Why |
|---|---|---|---|---|---|
| A002 | A reader says every person in town was asked. Does the notice support that? | No, not everyone was asked. | CORRECT | ds CORRECT, gpt CORRECT, qw CORRECT | bare verdict: the prompt asks only 'does it support that', no reason requested |
| A004 | A reader says every person in town was asked. Does the notice support that? | It doesn't really include everyone. | UNCLEAR | ds CORRECT, gpt UNCLEAR, qw CORRECT | hedged bare verdict ('doesn't really') |

### D2. Half of a two-part answer, or the 'what' of a 'what and why' prompt.

Options: a) Not quite → tell  b) Not clear yet once, asking for the missing part  c) Correct when the half given is the part the prompt stresses

| ID | Question | Student answer | My label | 3 models | Why |
|---|---|---|---|---|---|
| A011 | What do a corn stalk and a bean stalk show about the two kinds of wood? | Corn stalks are one type. | UNCLEAR | ds MISS, gpt MISS, qw UNCLEAR | half of a two-part answer (one plant only) |
| A019 | The paint wore off the loop. Why does that matter? | it causes the metal to swell. | CORRECT | ds MISS, gpt MISS, qw CORRECT | skips the rust step of the chain, states only the end effect |
| A067 | The crew adds a boxer to the lane that fills fastest. What should they expect next, and why? | The pile will move. | UNCLEAR | ds CORRECT, gpt MISS, qw UNCLEAR | two-question prompt (what + why): the 'what' alone |
| A070 | The crew adds a boxer to the lane that fills fastest. What should they expect next, and why? | The pile shifted again, this time to the boxers. | UNCLEAR | ds CORRECT, gpt MISS, qw CORRECT | passage sentence states the 'what' with no 'why' (same two-question issue) |
| A083 | Why did the man keep cutting twenty-five pounds when the foreman wanted thinner blocks? | the trips were longer now. | CORRECT | ds CORRECT, gpt CORRECT, qw CORRECT | half: the cause without the link to the ice lasting; the key lists it as accepted |
| A093 | Why does clover help the next crop? | Clover pulls nitrogen from the air. | CORRECT | ds MISS, gpt CORRECT, qw MISS | passage fact without the link to the next crop |

### D3. An answer that's true at a shallower level than the prompt intends.

Options: a) Correct, and rewrite the prompt so the shallow answer no longer fits (3.1.6)  b) Not quite → tell

| ID | Question | Student answer | My label | 3 models | Why |
|---|---|---|---|---|---|
| A025 | A calf that carries the mark shows the same small gap. Where does the gap come from? | the gap comes from the branding iron. | CORRECT | ds MISS, gpt MISS, qw MISS | defensible: the gap is in the iron; key wants who cut it (prompt admits the shallower answer) |
| A026 | A calf that carries the mark shows the same small gap. Where does the gap come from? | from the branding iron. | CORRECT | ds MISS, gpt MISS, qw MISS | same as A025 |
| A027 | A calf that carries the mark shows the same small gap. Where does the gap come from? | the branding iron made it. | CORRECT | ds MISS, gpt MISS, qw MISS | same as A025 |
| A073 | What change in approach does the sentence about shaping loaves and filling pans show? | It shows the next step in making bread. | UNCLEAR | ds CORRECT, gpt MISS, qw MISS | prompt is vague ('change in approach'); answer names steps but not the change |

### D4. An answer the passage supports that the key doesn't list, or contradicts.

Options: a) Correct, and fix the key  b) Not quite: the key decides

| ID | Question | Student answer | My label | 3 models | Why |
|---|---|---|---|---|---|
| A041 | What did the sand in the holes do? | The sand helped the roots grow deeper. | CORRECT | ds MISS, gpt MISS, qw CORRECT | defensible from the sequence; key's 'kept holes open' is not stated in the passage |
| A048 | What did the sand in the holes do? | The sand might have helped with drainage. | CORRECT | ds UNCLEAR, gpt MISS, qw MISS | drainage is defensible from the passage (water entered instead of running off) |
| A087 | Why did the man keep cutting twenty-five pounds when the foreman wanted thinner blocks? | he wanted to save money at sea. | CORRECT | ds MISS, gpt MISS, qw MISS | defensible: 'cheaper at the plant and dearer at sea' says thick blocks save money at sea |
| A096 | Why does clover help the next crop? | Clover helps by stopping weeds. | MISS | ds MISS, gpt MISS, qw MISS | 'The cover crop shades out weeds' may refer to clover; the key's branch treats this as a miss |

### D5. The student quotes the passage sentence that holds the answer, without saying how it answers.

Options: a) Correct: the evidence is the answer  b) Not clear yet: ask what it shows  c) Correct only when the sentence directly answers the prompt

| ID | Question | Student answer | My label | 3 models | Why |
|---|---|---|---|---|---|
| A046 | What did the sand in the holes do? | Water entered the holes, and the roots followed it down. | UNCLEAR | ds MISS, gpt MISS, qw CORRECT | passage sentence about what followed the sand; is that 'what the sand did'? |
| A070 | The crew adds a boxer to the lane that fills fastest. What should they expect next, and why? | The pile shifted again, this time to the boxers. | UNCLEAR | ds CORRECT, gpt MISS, qw CORRECT | passage sentence states the 'what' with no 'why' (same two-question issue) |

Two key defects surfaced along the way:
- `process_band_4_1_0004` item 4: the key says the sand "held the holes open", but the passage never says that.
- `authors_craft_band_4_2_0003` item 2: the key relies on "scattered threads" and "a ring", which aren't in the displayed passage.

## Part 2 — spot-check my labels (18 random, not policy)

Mark any you'd label differently. Labels: CORRECT, UNCLEAR (Not clear yet), MISS.

| # | ID | Question | Student answer | My label | Why |
|---|---|---|---|---|---|
| 1 | A003 | A reader says every person in town was asked. Does the notice support that? | Only bus passengers got cards. | CORRECT | implies no, gives the reason |
| 2 | A018 | The paint wore off the loop. Why does that matter? | rust makes it grip tighter. | CORRECT | rust implied; result stated |
| 3 | A030 | A calf that carries the mark shows the same small gap. Where does the gap come from? | Every calf that carried the mark carried the same small gap in it. | MISS |  |
| 4 | A034 | The passage says no area in view of the Skyline Drive is fully natural. Why does it say that? | The land was changed by people. | CORRECT |  |
| 5 | A037 | The passage says no area in view of the Skyline Drive is fully natural. Why does it say that? | No area in view of the Skyline Drive is fully natural. | MISS |  |
| 6 | A039 | The passage says no area in view of the Skyline Drive is fully natural. Why does it say that? | The trees were all cut down. | MISS |  |
| 7 | A042 | What did the sand in the holes do? | It let water in. | CORRECT |  |
| 8 | A056 | Splitting the check into two steps cleared the line. Why did that work when a second packer would not? | Maybe the owner wanted to save money. | MISS |  |
| 9 | A059 | What is a margin? | It's how much they earn. | UNCLEAR | earn could mean revenue or profit |
| 10 | A066 | The crew adds a boxer to the lane that fills fastest. What should they expect next, and why? | Less pile of apples. | MISS |  |
| 11 | A074 | What change in approach does the sentence about shaping loaves and filling pans show? | Starts shaping the dough. | MISS |  |
| 12 | A077 | What change in approach does the sentence about shaping loaves and filling pans show? | The sentence is about shaping loaves and filling pans. | MISS |  |
| 13 | A078 | What change in approach does the sentence about shaping loaves and filling pans show? | The dough is shaped into loaves and put in pans half filled. | MISS |  |
| 14 | A086 | Why did the man keep cutting twenty-five pounds when the foreman wanted thinner blocks? | the man kept cutting twenty-five pounds. | MISS |  |
| 15 | A090 | Why does clover help the next crop? | It adds nitrogen to soil. | CORRECT |  |
| 16 | A092 | Why does clover help the next crop? | It makes things better. | MISS |  |
| 17 | A094 | Why does clover help the next crop? | Clover and other legumes pull nitrogen from the air and store it in their roots. | CORRECT | passage sentence; the soil link is implied by 'store it in their roots' |
| 18 | A095 | Why does clover help the next crop? | Clover makes the ground harder. | MISS |  |