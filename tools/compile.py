#!/usr/bin/env python3
"""Compile one source (or all) into lessons/ using a clone of the readingHarness repo.

    python3 tools/compile.py --harness ../readingHarness                          # all sources
    python3 tools/compile.py --harness ../readingHarness lessons/src/<name>.source.json

Run tools/check.py afterwards; it proves the compiled output matches the sources.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = Path("scripts/build_lessons.py")
PROTOCOL = Path("server/config/protocol.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", default="../readingHarness")
    ap.add_argument("--protocol", default=None, help="override the protocol file")
    args = ap.parse_args()
    harness = Path(args.harness).expanduser()
    if not (harness / COMPILER).is_file():
        print(f"cannot find the compiler at {harness / COMPILER}\n"
              f"clone it: git clone https://github.com/ctroy978/readingHarness {harness}")
        return 1
    protocol = Path(args.protocol) if args.protocol else harness / PROTOCOL
    cmd = [sys.executable, str(harness / COMPILER), "--source-dir", "lessons/src", "--output-dir",
           "lessons", "--protocol", str(protocol)]
    print(" ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
