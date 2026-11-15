#!/usr/bin/env python3
"""The contribution gate: compile check, validator, and the new-lesson key checks.

Run from the root of the readJson repo. The compiler lives in the readingHarness repo, so point at a
clone of it (it is public, and needs no virtualenv):

    git clone https://github.com/ctroy978/readingHarness ../readingHarness
    python3 tools/check.py --harness ../readingHarness

With no source arguments it checks the whole corpus (compiled output in step, strict validation).
Name the sources you touched to also run the new-lesson gate on them:

    python3 tools/check.py --harness ../readingHarness lessons/src/inference_band_5_1_0007.source.json

Exit code 0 means the contribution is ready for review. Exit 1 means it failed a machine check; the
output says which one.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
COMPILER = Path("scripts/build_lessons.py")
PROTOCOL = Path("server/config/protocol.json")


def run(cmd, label):
    print(f"\n== {label}\n   {' '.join(str(c) for c in cmd)}")
    result = subprocess.run([str(c) for c in cmd], cwd=ROOT, capture_output=True, text=True)
    out = (result.stdout + result.stderr).strip()
    if out:
        tail = "\n   ".join(out.splitlines()[-25:])
        print(f"   {tail}")
    return result.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", default="../readingHarness",
                    help="path to a clone of the readingHarness repo (public, no venv needed)")
    ap.add_argument("sources", nargs="*", help="source files you changed; adds the new-lesson key checks")
    args = ap.parse_args()

    harness = Path(args.harness).expanduser()
    if not (harness / COMPILER).is_file():
        print(f"cannot find the compiler at {harness / COMPILER}\n"
              f"clone it: git clone https://github.com/ctroy978/readingHarness {harness}")
        return 1

    ok = True
    ok &= run([sys.executable, harness / COMPILER, "--source-dir", "lessons/src", "--output-dir", "lessons",
               "--protocol", harness / PROTOCOL, "--check"], "compiled output matches the sources")
    ok &= run([sys.executable, HERE / "validate_lesson.py", "--strict", "--src-dir", "lessons/src",
               "--lessons-dir", "lessons", *sorted(str(p) for p in Path("lessons/src").glob("*.source.json"))],
              "validator, strict (the whole corpus)")
    if args.sources:
        ok &= run([sys.executable, HERE / "validate_lesson.py", "--strict", "--key-scope", "--src-dir",
                   "lessons/src", "--lessons-dir", "lessons", *args.sources],
                  "new-lesson key checks on the files you changed")
    else:
        print("\n== new-lesson key checks skipped (name your source files to run them)")

    print("\n" + ("PASS - ready for review" if ok else "FAIL - fix the check above before opening a PR"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
