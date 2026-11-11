#!/usr/bin/env python3
"""Independent fidelity gate for an authored rung.

Checks each lesson against the human-written excerpt it names in plan.json:
control characters, invented questions, hype words, names and numbers not in the
source, and per-part 4-gram overlap. Exits 1 on any failure.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

BOT = pathlib.Path(__file__).resolve().parent
ROOT = BOT.parents[1]
SRC = ROOT / "lessons" / "src"
SKILL = pathlib.Path.home() / ".hermes/skills/productivity/readjson-lessons"

spec = importlib.util.spec_from_file_location("mp", SKILL / "scripts/measure_passage.py")
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

HYPE = re.compile(r"\b(have you ever|how cool|isn[’']t|amazing|wonder(?:ful)?|secret|"
                  r"beautiful|you wouldn[’']t want|right\?)\b", re.I)
CTRL = re.compile(r"[\x00-\x1f]")


def grams(text: str, n: int = 4) -> set:
    w = re.findall(r"[a-z']+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def caps(text: str) -> set:
    out = set()
    for s in re.split(r"(?<=[.!?])\s+", text):
        body = s.split(" ", 1)[1] if " " in s else ""
        out |= set(re.findall(r"\b[A-Z][a-z]{2,}\b", body))
    return out


def check(lesson: dict, src_text: str) -> list[str]:
    problems = []
    seq = lesson["sequence"]
    lid = f"authors_craft_band_4_1_{seq:04d}"
    path = SRC / f"{lid}.source.json"
    if not path.exists():
        return [f"{lid}: missing source"]
    d = json.loads(path.read_text())
    whole = " ".join(d["passage"].values())
    if CTRL.search(whole):
        problems.append(f"{lid}: control character in passage")
    if whole.count("?") > src_text.count("?"):
        problems.append(f"{lid}: {whole.count('?')} question marks; source has {src_text.count('?')}")
    hit = HYPE.search(whole)
    if hit:
        problems.append(f"{lid}: hype/tag phrase {hit.group(0)!r}")
    extra_nums = set(re.findall(r"\d+", whole)) - set(re.findall(r"\d+", src_text))
    if extra_nums:
        problems.append(f"{lid}: numbers not in source {sorted(extra_nums)}")
    extra_caps = caps(whole) - caps(src_text)
    if extra_caps:
        problems.append(f"{lid}: names not in source {sorted(extra_caps)}")
    src_g = grams(src_text)
    for part, text in d["passage"].items():
        shared = len(grams(text) & src_g)
        if mp.words(text) >= 60 and shared < 2:
            problems.append(f"{lid} {part}: only {shared} shared 4-grams with the source")
    return problems


def main() -> int:
    plan = json.loads((BOT / "plan.json").read_text())
    failures = []
    for lesson in plan["lessons"]:
        src = (BOT / "sources" / lesson["source_file"]).read_text()
        failures += check(lesson, src)
    if failures:
        print("\n".join(failures))
        print(f"\nFIDELITY FAIL: {len(failures)} problem(s)")
        return 1
    print("FIDELITY PASS: no invented questions, hype, names, numbers, or control characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
