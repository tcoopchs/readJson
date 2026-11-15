# For automated contributors

If you are an agent asked to add or fix a lesson in this repository, do this in order:

1. **Read `CONTRIBUTING.md`.** The first section is a licence rule: the text must be public domain,
   CC0 or CC BY, with the exact source URL recorded. If you cannot name a free source, stop and say so
   rather than writing a passage from memory.
2. **Read `DESIGN_RULES.md`** for passages, questions, keys and routes. `README.md` is the contract for
   filenames and placement.
3. **Get the compiler.** It is public and needs no virtualenv:

   ```bash
   git clone https://github.com/ctroy978/readingHarness ../readingHarness
   ```

4. **Write the source** at `lessons/src/<category>_band_<grade>_<stage>_<sequence>.source.json`. Do not
   hand-edit anything in `lessons/` except by running the compiler.
5. **Run the gate and fix what it reports:**

   ```bash
   python3 tools/check.py --harness ../readingHarness lessons/src/<your>.source.json
   ```

   It must print `PASS - ready for review`.
6. **Compile and commit both files**, on a branch named `lesson/<lesson_id>`:

   ```bash
   python3 tools/compile.py --harness ../readingHarness
   git add lessons/src/<your>.source.json lessons/<your>.json
   ```

7. **Open one pull request per lesson** and say, in the description, the source URL, its licence, and
   the reading band you targeted.

What happens after you open it, which the machines cannot do for you: a key probe over the five items,
a read of the passage for quality and band fit, and a check of the licence record. A passing
`check.py` is the floor, not the bar.
