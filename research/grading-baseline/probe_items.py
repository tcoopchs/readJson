#!/usr/bin/env python3
"""Targeted key probe: grade a named list of items instead of whole lessons.

    python3 probe_items.py items.json --out probe_out.json

items.json is a list of {"lesson": "<lesson_id>", "item": "<item id>"}. For each item a cheap
student model writes eight answers from the passage and prompt only (never the key), and three
tutor models grade them under the live compiled protocol. Rows are appended as they finish, so an
interrupted run keeps its work.

A flag means read it: a likely-right answer rejected by two or more models, or a wrong answer
accepted by two or more.
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/tcoop/Work/readJson")
sys.path.insert(0, str(HERE))
import grade as G  # noqa: E402
import gen_answers as A  # noqa: E402

STUDENT = "openai/gpt-4o-mini"


def call(model, system, user, key, max_tokens=1500):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(G.ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {}).get("cost", 0) or 0
        except Exception:
            if attempt == 2:
                return "", 0
            time.sleep(2)
    return "", 0


def verdict(t):
    m = re.search(r"(CORRECT|UNCLEAR|MISS)", (t or "").upper())
    return m.group(1) if m else None


def probe_one(spec, key):
    lid, iid = spec["lesson"], str(spec["item"])
    src = json.loads((ROOT / "lessons/src" / f"{lid}.source.json").read_text())
    comp = json.loads((ROOT / "lessons" / f"{lid}.json").read_text())
    src_it = next(x for x in src["items"] if str(x["id"]) == iid)
    comp_it = next(x for x in comp["items"] if str(x["id"]) == iid)
    passage = A.passage_of(src, src_it)
    raw, cost = call(STUDENT, A.SYSTEM, A.PROMPT.format(passage=passage, prompt=src_it["prompt"]), key)
    try:
        answers = A.json_block(raw)
    except Exception:
        answers = {}
    rows, spend = {}, cost

    def score(t):
        typ, ans, m = t
        user = G.USER.format(rules=G.RULES, passage=passage, prompt=comp_it["prompt"],
                             tutor_only=json.dumps(comp_it["tutor_only"], indent=1), answer=ans)
        text, c = call(m, G.SYSTEM, user, key, max_tokens=1200)
        return typ, m.split("/")[-1][:10], verdict(text), c

    tasks = [(typ, ans, m) for typ, ans in answers.items() for m in G.MODELS]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for typ, mname, v, c in pool.map(score, tasks):
            spend += c
            rows.setdefault(typ, {"answer": answers[typ], "verdicts": {}})["verdicts"][mname] = v

    lr = rows.get("likely_right", {}).get("verdicts", {})
    wr = rows.get("wrong", {}).get("verdicts", {})
    flags = []
    if sum(1 for v in lr.values() if v == "MISS") >= 2:
        flags.append("likely-right answer rejected")
    if sum(1 for v in wr.values() if v == "CORRECT") >= 2:
        flags.append("wrong answer accepted")
    return {"lesson": lid, "item": iid, "prompt": comp_it["prompt"],
            "key": comp_it["tutor_only"].get("core_idea") or comp_it["tutor_only"].get("accept_words"),
            "one_idea_is_enough": comp_it["tutor_only"].get("one_idea_is_enough"),
            "accepts": comp_it["tutor_only"].get("accept_ideas"),
            "rows": rows, "flags": flags, "cost": round(spend, 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    specs = json.loads(Path(args.items).read_text())
    if args.limit:
        specs = specs[: args.limit]
    key = G.api_key()
    out = Path(args.out)
    out.write_text("")
    total, flagged = 0.0, 0
    with open(out, "a") as fh:
        with ThreadPoolExecutor(max_workers=6) as pool:
            for n, res in enumerate(pool.map(lambda s: probe_one(s, key), specs), 1):
                fh.write(json.dumps(res) + "\n")
                fh.flush()
                total += res["cost"]
                if res["flags"]:
                    flagged += 1
                    print(f"FLAG {res['lesson']} i{res['item']} :: {res['flags']}")
                if n % 10 == 0:
                    print(f"  {n}/{len(specs)} items, ${total:.2f}")
    print(f"\n{len(specs)} items, {flagged} flagged, ${total:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
