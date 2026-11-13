#!/usr/bin/env python3
"""Sweep the Band 4 cloze items for the two errors the cloze rule can make.

For each cloze item, a cheap model reads the passage and the prompt (never the key) and writes two
answers: a synonym that fits the blank and keeps the meaning, and a plausible wrong word. Three tutor
models score both under the live compiled protocol.

  synonym rejected  -> the item is stricter than its own gloss (a defect under the open-cloze rule)
  wrong accepted    -> the item is too loose (the risk the open-cloze rule creates)

Writes sweep_cloze.json incrementally. Usage: python3 sweep_cloze.py [--limit N]
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
CAP = 2.00

SYS = ("You are a student in a reading lesson filling one blank. You answer from the passage only. "
       "Reply with JSON only.")
PROMPT = """PASSAGE
{passage}

SENTENCE WITH A BLANK
{prompt}

Write two single words or short phrases for the blank:
- "synonym": a word that fits the blank and keeps the sentence's meaning, but is NOT the word the passage uses.
- "wrong": a word that fits the grammar of the blank but gives the sentence a different or opposite meaning.

JSON only: {{"synonym": "...", "wrong": "..."}}"""


def call(model, system, user, key, max_tokens=1200):
    body = {"model": model, "temperature": 0.4, "max_tokens": max_tokens, "usage": {"include": True},
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
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 999
    items = []
    for p in sorted(SRC.glob("*_band_4_*.source.json")):
        d = json.loads(p.read_text())
        for it in d["items"]:
            if it.get("type") == "cloze":
                items.append((d["lesson_id"], it))
    items = items[:limit]
    rows, spent = [], 0.0
    for n, (lid, it) in enumerate(items, 1):
        sp = it.get("show_part")
        src = json.loads((SRC / f"{lid}.source.json").read_text())
        passage = "\n\n".join(src["passage"].values()) if sp in (None, "all") else src["passage"][sp]
        raw, c = call(STUDENT, SYS, PROMPT.format(passage=passage, prompt=it["prompt"]), key)
        spent += c
        try:
            pair = A.json_block(raw)
        except Exception:
            print("skip", lid, it["id"]); continue
        comp = json.loads((LESSONS / f"{lid}.json").read_text())
        ci = next(x for x in comp["items"] if str(x["id"]) == str(it["id"]))
        out = {"lesson": lid, "item": it["id"], "difficulty": it.get("difficulty"),
               "prompt": it["prompt"], "accept_words": ci["tutor_only"].get("accept_words"),
               "synonym": pair.get("synonym", ""), "wrong": pair.get("wrong", ""), "res": {}}
        for kind in ("synonym", "wrong"):
            for m in G.MODELS:
                user = G.USER.format(rules=G.RULES, passage=passage, prompt=ci["prompt"],
                                     tutor_only=json.dumps(ci["tutor_only"], indent=1), answer=pair.get(kind, ""))
                txt, cost = call(m, G.SYSTEM, user, key, max_tokens=2000)
                spent += cost
                out["res"][f"{kind}|{m}"] = verdict(txt)
        rows.append(out)
        (B / "sweep_cloze.json").write_text(json.dumps(rows, indent=1))
        if n % 6 == 0:
            print(f"{n}/{len(items)} ${spent:.3f}", flush=True)
        if spent > CAP:
            print("cap"); break
    print(f"{len(rows)} items, ${spent:.3f}")


if __name__ == "__main__":
    main()
