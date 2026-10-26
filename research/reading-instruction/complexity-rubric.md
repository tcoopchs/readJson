# Text Complexity Rubric v1

Purpose: place a passage by what it demands, not by one readability number. Two passages can have
the same Lexile and different idea loads. The rubric produces a language score, an idea score, a
structure score, and a knowledge score; the band recommendation is the highest demand, never the
average.

## 1. Why Lexile alone fails

Quantitative formulas use word length and sentence length as proxies for meaning and syntax. They
miss levels of meaning, structure, language conventionality, and knowledge demands, which the CCSS
treat as qualitative dimensions judged by an attentive reader. [29, 30]

The standard example: Flesch-Kincaid and Lexile rate *The Grapes of Wrath* as appropriate for
grades 2-3. The formula is not wrong at counting; it is counting the wrong things. [32]

Cohesion is also not captured by Lexile. Low referential or causal cohesion forces the reader to
supply connections, which raises inference demand. High cohesion can still be hard when sentences
are long, especially for older adults with limited verbal ability. [33, 34]

## 2. Four dimensions, each scored 0-3

### A. Language load (L)

| Score | Descriptor |
| --- | --- |
| 0 | Short simple sentences; common concrete words; explicit connectives; high cohesion. |
| 1 | Mostly simple or compound sentences; common words; a few academic terms explained in text. |
| 2 | Varied or complex sentences; some abstract, figurative, or domain terms; some cohesion gaps. |
| 3 | Dense complex syntax; abstract, archaic, ironic, or specialized language; frequent cohesion gaps. |

### B. Idea load (I)

| Score | Descriptor |
| --- | --- |
| 0 | One entity, one step, one explicit idea. |
| 1 | Two or three entities; explicit sequence; one clear relation. |
| 2 | Several entities or steps; two or three relations; one abstraction; evidence one or two sentences apart. |
| 3 | Many entities or steps; nested dependencies; abstraction or competing interpretations; evidence across parts; a supplied background fact is needed. |

### C. Structure load (S)

| Score | Descriptor |
| --- | --- |
| 0 | Straightforward chronology or a single clear section. |
| 1 | Clear sections with headings or signal words. |
| 2 | Mixed structure, time or place shifts, or several embedded sections. |
| 3 | Nonchronological, embedded, unreliable, or genre-specific structure that must be inferred. |

### D. Knowledge load (K)

| Score | Descriptor |
| --- | --- |
| 0 | Everyday experience only. |
| 1 | Topic is introduced and explained in the passage. |
| 2 | Some domain knowledge is assumed but supported by context. |
| 3 | Specialized, cultural, literary, or allusive knowledge is assumed and not supplied. |

## 3. Placement rule

The Band code is a routing slot, not a grade. `reader.reading_level` remains the grade target.

Recommended band = the highest demand among L, I, S, and K, using this map:

| Highest demand | Recommended Band |
| --- | --- |
| L0-1, I0-1, S0-1, K0-1 | Band 3.1 |
| L2, I1-2, S1-2, K1-2 | Band 5.1 |
| L2, I2-3, S2, K2 | Band 7.1 |
| L2-3, I3, S2-3, K2-3 | Band 9.1 |
| L3, I3, S3, K3 | Band 12.1 |

Adjustments:

- If L and I disagree, use the higher one. Do not average down.
- Low cohesion raises I by one step.
- A passage with simple sentences and a genuinely complex idea belongs at the idea's band.
- A passage with hard sentences and simple ideas belongs at the language's band, because decoding
  load is real.
- Passage length is not a complexity score.

## 4. Worked examples

### Canal lock (existing `process_band_9_1_0001`)

- L1: common words, simple sentences, explicit sequence.
- I2: two gates, two water levels, three ordered steps, one dependency.
- S2: two parts, each a stage of the process.
- K1: all needed knowledge is in the passage.
- Highest demand: 2 -> Band 5.1. Grade target 9 is set by the intended reader, not the Band code.

### Wastewater treatment (`process_band_10_1_0001`)

- L1: short sentences, common words, terms explained in text.
- I3: screen, grit tank, aeration, clarifier, disinfect; each stage depends on the last; failure
  modes; flow timing.
- S2: three parts, each a stage block.
- K1: no outside knowledge required.
- Highest demand: 3 -> Band 7.1. This is the case the user identified: simple language, complex
  information.

### Diner cooler (`inference_band_5_1_0001`)

- L1: common words, short sentences.
- I1-2: one place, two times, one causal chain, evidence in adjacent sentences.
- S1: chronological.
- K0: everyday kitchen knowledge.
- Highest demand: 2 -> Band 5.1.

### Shakespeare at the top band

- L3: archaic syntax and vocabulary, inversion, figurative density.
- I3: motive, theme, and multiple meanings.
- S3: verse and scene structure, shifts in speaker and time.
- K3: genre and cultural knowledge assumed.
- Highest demand: 3 -> Band 12.1. Allowed under the old-text rule because it is the top grade.

## 5. Authoring checks

1. Score all four dimensions before writing items. Record the scores in
   `reader.why_this_level`.
2. Name the highest demand and why it sets the band.
3. If a passage is below the intended band on every dimension, rewrite or replace it. Do not
   relabel it.
4. If a passage is above the Band on one dimension, decide whether a scaffold can carry it. If
   not, rewrite that dimension, not the whole text.
5. Do not use a readability score as the sole justification. Give the measure and then explain
   what it misses.
6. Old text is allowed only at grades 11-12, and only when the L/I/S/K scores justify it.

## 6. What this rubric does not do

- It does not measure topic interest or reader motivation.
- It does not predict an individual reader's performance.
- It does not replace a cold-chat test. A passage can score correctly and still produce ambiguous
  items.
- It does not settle the band for a whole category. Band selection also depends on the skill and
  the route.

## 7. Open issues

- The 0-3 descriptors are author judgment, not an instrument with inter-rater reliability.
- The band map needs testing against the six existing sources.
- Cohesion is treated as a modifier, not a fifth dimension. If it proves decisive, split it out.
