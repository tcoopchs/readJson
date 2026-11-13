#!/usr/bin/env python3
"""Sweep every Band 4 item with two generated answers and three tutors.

For each short-answer item a cheap model writes, from the passage and prompt only (never the key):
  likely_right  the answer a student who understood would type   -> expected CORRECT
  wrong         a plausible misreading                            -> expected MISS
Three tutor models score both under the live compiled protocol. A row is flagged when the expectation
is not met by at least two tutors, so a single model's flake does not fill the report.

Writes sweep_band4.json incrementally. Usage: python3 sweep_band4.py [--limit N] [--only CATEGORY]
"""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
import grade as G
import gen_answers as A

B = Path(__file__).parent
SRC = Path("/home/tcoop/Work/readJson/lessons/src")
LESSONS = Path("/home/tcoop/Work/readJson/lessons")
STUDENT = "openai/gpt-4o-mini"
CAP = 4.00

SYS = ("You are a student in a reading lesson. You answer in your own casual words, never in a "
       "teacher's wording. Reply with JSON only.")
PROMPT = """PASSAGE
{passage}

QUESTION
{prompt}

Write two answers:
- "likely_right": the answer a student who understood the passage would type, in one short sentence.
- "wrong": an answer a real student might give from a misreading of the passage.

JSON only: {{"likely_right": "...", "wrong": "..."}}"""


def call(model, system, user, key, max_tokens=1500):
    body = {"model": model, "temperature": 0.3, "max_tokens": max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(G.ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {}).get("cost", 0) or 0
        except Exception as e:
            if attempt == 2:
                return f"ERROR {e}", 0
            time.sleep(2)
    return "", 0


def verdict(t):
    m = re.search(r"(CORRECT|UNCLEAR|MISS)", (t or "").upper())
    return m.group(1) if m else None


def main():
    key = G.api_key()
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 9999
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    items = []
    for p in sorted(SRC.glob("*_band_4_*.source.json")):
        d = json.loads(p.read_text())
        if only and not d["lesson_id"].startswith(only):
            continue
        for it in d["items"]:
            if it.get("type") == "short_answer":
                items.append((d["lesson_id"], it))
    items = items[:limit]
    rows, spent = [], 0.0
    for n, (lid, it) in enumerate(items, 1):
        src = json.loads((SRC / f"{lid}.source.json").read_text())
        sp = it.get("show_part")
        passage = "\n\n".join(src["passage"].values()) if sp in (None, "all") else src["passage"][sp]
        raw, c = call(STUDENT, SYS, PROMPT.format(passage=passage, prompt=it["prompt"]), key)
        spent += c
        try:
            pair = A.json_block(raw)
        except Exception:
            continue
        comp = json.loads((LESSONS / f"{lid}.json").read_text())
        ci = next(x for x in comp["items"] if str(x["id"]) == str(it["id"]))
        out = {"lesson": lid, "item": it["id"], "difficulty": it.get("difficulty"), "prompt": it["prompt"],
               "core": ci["tutor_only"].get("core_idea"), "flag": ci["tutor_only"].get("one_idea_is_enough"),
               "answers": pair, "res": {}}
        for kind, exp in (("likely_right", "CORRECT"), ("wrong", "MISS")):
            for m in G.MODELS:
                user = G.USER.format(rules=G.RULES, passage=passage, prompt=ci["prompt"],
                                     tutor_only=json.dumps(ci["tutor_only"], indent=1), answer=pair.get(kind, ""))
                txt, cost = call(m, G.SYSTEM, user, key, max_tokens=2000)
                spent += cost
                out["res"][f"{kind}|{m}"] = verdict(txt)
        rows.append(out)
        (B / "sweep_band4.json").write_text(json.dumps(rows, indent=1))
        if n % 25 == 0:
            print(f"{n}/{len(items)} ${spent:.3f}", flush=True)
        if spent > CAP:
            print("cap reached"); break
    print(f"{len(rows)} items, ${spent:.3f}")


if __name__ == "__main__":
    main()
