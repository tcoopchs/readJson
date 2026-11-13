#!/usr/bin/env python3
"""Classify a sweep's flags cheaply, so a human reads only the ones that matter.

Reads a sweep file (sweep_band4.py output) and keeps only the flags worth acting on:
  likely_right rejected by 3 of 3 tutors    the key probably lacks a valid answer
  wrong accepted by 2 or more tutors        the key is too loose
A 2-of-3 rejection is dropped: across 418 Band 4 items those were almost all noise.

Each kept flag goes to a cheap model with the prompt, the key and the answer only, and comes back as:
  GAP     a correct answer the key fails to list   -> widen the key
  MISS    wrong or insufficient under the key      -> the tutor was right
  UNSURE  needs a human

Usage:
  python3 triage_flags.py sweep_band4.json [--out triage.json] [--limit N] [--show GAP]
"""
import argparse, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import grade as G  # noqa: E402

BUS = "openai/gpt-4o-mini"
SYS = ("You compare a student's answer with a lesson's stored answer key. You do not see the passage; "
       "judge only whether the answer states the key's idea in different words. "
       'Reply with JSON only: {"verdict": "GAP"|"MISS"|"UNSURE", "why": "<=12 words"}')
USER = """QUESTION
{prompt}

STORED KEY
core_idea: {core}
one_idea_is_enough: {flag}
accept_ideas: {accepts}

STUDENT ANSWER
{answer}

GAP means: this answer states the core idea, in different words, and the key simply does not list it.
MISS means: it states a different idea, only part of the idea when the key needs all of it, or something the key does not credit.
UNSURE means: you cannot tell from this much.

JSON only."""


def call(model, user, key):
    body = {"model": model, "temperature": 0, "max_tokens": 200, "usage": {"include": True},
            "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(G.ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=90)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {}).get("cost", 0) or 0
        except Exception:
            if attempt == 2:
                return "", 0
            time.sleep(2)
    return "", 0


def parse(text):
    m = re.search(r"\b(GAP|MISS|UNSURE)\b", (text or "").upper())
    why = re.search(r'"why"\s*:\s*"([^"]{0,80})', text or "")
    return (m.group(1) if m else "UNSURE"), (why.group(1) if why else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=9999)
    args = ap.parse_args()
    key = G.api_key()
    rows = json.loads(Path(args.sweep).read_text())
    flags = []
    for r in rows:
        lr = [v for k, v in r["res"].items() if k.startswith("likely_right|")]
        wr = [v for k, v in r["res"].items() if k.startswith("wrong|")]
        if sum(1 for v in lr if v == "MISS") == 3:
            flags.append((r["lesson"], r["item"], "likely_right", r["answers"].get("likely_right", ""), r))
        elif sum(1 for v in wr if v == "CORRECT") >= 2:
            flags.append((r["lesson"], r["item"], "wrong_accepted", r["answers"].get("wrong", ""), r))
    flags = flags[: args.limit]
    print(f"{len(rows)} rows -> {len(flags)} flags kept (3-of-3 rejections and wrong answers accepted)")

    def work(f):
        lid, iid, kind, answer, r = f
        core = (r.get("core") or "")[:300]
        accepts = r.get("accepts") or []
        if not accepts:
            src = json.loads((HERE.parent.parent / "lessons/src" / f"{lid}.source.json").read_text())
            item = next(x for x in src["items"] if str(x["id"]) == str(iid))
            accepts = (item.get("tutor_only") or {}).get("accept_ideas") or []
        user = USER.format(prompt=r["prompt"][:400], core=core, flag=r.get("flag"), accepts=json.dumps(accepts)[:600], answer=answer)
        text, cost = call(BUS, user, key)
        verdict, why = parse(text)
        return {"lesson": lid, "item": iid, "kind": kind, "answer": answer, "prompt": r["prompt"],
                "core": core, "verdict": verdict, "why": why, "cost": cost}

    with ThreadPoolExecutor(max_workers=6) as pool:
        out = list(pool.map(work, flags))
    counts = {}
    for o in out:
        counts[o["verdict"]] = counts.get(o["verdict"], 0) + 1
    print("classification:", counts, f"cost ${sum(o['cost'] for o in out):.4f}")
    for verdict in ("GAP", "UNSURE"):
        sel = [o for o in out if o["verdict"] == verdict]
        if not sel:
            continue
        print(f"\n== {verdict} ({len(sel)})")
        for o in sel:
            print(f"  {o['lesson'][:28]}.{o['item']} [{o['kind']}] {o['why']}")
            print(f"     Q: {o['prompt'][:90]}")
            print(f"     A: {o['answer'][:100]}")
            print(f"     K: {o['core'][:100]}")
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=1))
        print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
