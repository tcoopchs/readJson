#!/usr/bin/env python3
"""Key probe over an explicit list of Band 4 items, after the triage edits.

For each item: a cheap student model writes 8 answers from the passage and prompt only (never the
key); an independent labeller (different model family, no key) labels each one under DECISIONS.md;
the three tutor models score each one under the live compiled protocol. Reports agreement, false
rejects, false accepts, and lists every case where a tutor and the labeller disagree.

Usage: python3 probe_band4.py list.json [--limit N] [--out probe.json]
"""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
import grade as G
import gen_answers as A

B = Path(__file__).parent
LESSONS = Path("/home/tcoop/Work/readJson/lessons")
LABELLER = "openai/gpt-5.6-terra"
CAP = 3.50
DECISIONS = (B / "DECISIONS.md").read_text()

LAB_SYSTEM = ("You are an experienced reading teacher labelling a student's answer to a reading question. "
              "You have no answer key: judge from the passage and the question alone, under the scoring decisions."
              ' Reply with JSON only: {"label": "CORRECT" | "UNCLEAR" | "MISS", "why": "<=20 words"}')
LAB_USER = """SCORING DECISIONS
{decisions}

Labels: CORRECT = Correct., UNCLEAR = Not clear yet., MISS = Not quite.

PASSAGE
{passage}

QUESTION
{prompt}

STUDENT ANSWER
{answer}

JSON only."""


def call(model, system, user, key, max_tokens=2500):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(G.ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=180)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {}).get("cost", 0) or 0
        except Exception as e:
            if attempt == 2:
                return f"ERROR {e}", 0
            time.sleep(3)
    return "", 0


def verdict(t):
    m = re.search(r"(CORRECT|UNCLEAR|MISS)", (t or "").upper())
    return m.group(1) if m else None


def main():
    lst = json.loads(Path(sys.argv[1]).read_text())
    if "--limit" in sys.argv:
        lst = lst[: int(sys.argv[sys.argv.index("--limit") + 1])]
    key = G.api_key()
    spent = 0.0
    rows = []
    for n, (lid, iid) in enumerate(lst, 1):
        src = json.loads((LESSONS / "src" / f"{lid}.source.json").read_text())
        it = next(x for x in src["items"] if str(x["id"]) == str(iid))
        passage = A.passage_of(src, it)
        raw, c = call(A.STUDENT, A.SYSTEM, A.PROMPT.format(passage=passage, prompt=it["prompt"]), key)
        spent += c
        try:
            answers = A.json_block(raw)
        except Exception:
            print("skip", lid, iid); continue
        compiled = json.loads((LESSONS / f"{lid}.json").read_text())
        citem = next(x for x in compiled["items"] if str(x["id"]) == str(iid))
        user = G.USER.format(rules=G.RULES, passage=passage, prompt=citem["prompt"],
                             tutor_only=json.dumps(citem["tutor_only"], indent=1), answer="{ans}")
        tasks = [(("lab", k2, v)) for k2, v in answers.items()]
        for k2, v in answers.items():
            tasks.append(("lab", k2, v))
            for m in G.MODELS:
                tasks.append(("tutor", f"{m}|{k2}", v))

        def run(t):
            kind, tag, ans = t
            if kind == "lab":
                txt, cost = call(LABELLER, LAB_SYSTEM, LAB_USER.format(decisions=DECISIONS, passage=passage,
                                                                       prompt=it["prompt"], answer=ans), key)
                return {"kind": "lab", "type": tag, "v": verdict(txt), "cost": cost}
            model, typ = tag.split("|")
            txt, cost = call(model, G.SYSTEM, user.replace("{ans}", ans), key)
            return {"kind": "tutor", "model": model, "type": typ, "v": verdict(txt), "cost": cost}

        with ThreadPoolExecutor(max_workers=8) as pool:
            res = list(pool.map(run, tasks))
        spent += sum(r["cost"] for r in res)
        rows.append({"lesson": lid, "item": iid, "answers": answers, "res": res})
        outpath = Path(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else B / "probe_band4.json")
        outpath.write_text(json.dumps(rows, indent=1))
        if spent > CAP:
            print("cap reached at", n); break
        if n % 5 == 0:
            print(f"{n}/{len(lst)} items, ${spent:.3f}", flush=True)
    Path(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else B / "probe_band4.json").write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} items, cost ${spent:.4f}")


if __name__ == "__main__":
    main()
