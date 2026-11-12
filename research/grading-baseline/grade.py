#!/usr/bin/env python3
"""S1 step 3: score every generated answer with 3 tutor models, using the live protocol's scoring rules
verbatim and the compiled item's tutor_only block. Three outcomes: CORRECT / UNCLEAR / MISS."""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

B = Path(__file__).parent
LESSONS = Path("/home/tcoop/Work/readJson/lessons")
PROTOCOL = Path("/home/tcoop/Work/readingHarness/server/config/protocol.json")
import os
MODELS = os.environ.get("MODELS", "deepseek/deepseek-v4.1-flash-1017,qwen/qwen3.8-flash,google/gemini-3.8-flash").split(",")
OUTFILE = os.environ.get("OUTFILE", "grades.json")
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
CAP_USD = 2.00


def api_key():
    for line in (Path.home() / ".hermes/.env").read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')


proto = json.loads(PROTOCOL.read_text())
# the scoring instructions, verbatim, selected by content so a reorder does not break this
KEEP = ("Every answer gets an outcome word", "Use one question at a time", "Read past spelling",
        "Grade only the job written in the prompt", "evidence-not-wording test",
        "On short-answer items, a synonym", "If the answer matches an if_they_say",
        "A right answer before tell is unaided")
RULES = "\n".join(f"- {s}" for s in proto["instructions"] if any(k in s for k in KEEP))

SYSTEM = ("You are the tutor in a reading lesson, scoring one student answer. Apply the rules exactly. "
          'Reply with JSON only: {"outcome": "CORRECT" | "UNCLEAR" | "MISS", "why": "<=15 words"}')

USER = """RULES (from the lesson protocol)
{rules}

Map the outcome words: Correct. -> CORRECT, Not clear yet. -> UNCLEAR, Not quite. -> MISS.

PASSAGE ON SCREEN
{passage}

QUESTION
{prompt}

tutor_only (private key for this item)
{tutor_only}

STUDENT ANSWER (first attempt)
{answer}

JSON only."""


def call(model, user, key):
    body = {"model": model, "temperature": 0, "max_tokens": 2000, "usage": {"include": True},
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {}).get("cost", 0) or 0
        except Exception as e:
            if attempt == 2:
                return f"ERROR {e}", 0
            time.sleep(3)


def main():
    key = api_key()
    items = {i["sid"]: i for i in json.loads((B / "items.json").read_text())}
    answers = json.loads((B / "answers.json").read_text())
    tasks = []
    for a in answers:
        it = items[a["sid"]]
        compiled = json.loads((LESSONS / f"{it['lesson']}.json").read_text())
        citem = next(x for x in compiled["items"] if str(x["id"]) == str(it["item"]))
        user = USER.format(rules=RULES, passage=it["passage"], prompt=citem["prompt"],
                           tutor_only=json.dumps(citem["tutor_only"], indent=1), answer=a["answer"])
        for m in MODELS:
            tasks.append((a["aid"], m, user))
    spent = 0.0
    prev = json.loads((B / OUTFILE).read_text()) if (B / OUTFILE).exists() else []
    out = [r for r in prev if r["outcome"]]
    done = {(r["aid"], r["model"]) for r in out}
    tasks = [t for t in tasks if (t[0], t[1]) not in done]
    print(f"{len(tasks)} gradings to run")

    def run(t):
        aid, m, user = t
        text, cost = call(m, user, key)
        mm = re.search(r"(CORRECT|UNCLEAR|MISS)", text.upper())
        return {"aid": aid, "model": m, "outcome": mm.group(1) if mm else None, "raw": text[:300], "cost": cost}

    with ThreadPoolExecutor(max_workers=8) as pool:
        for res in pool.map(run, tasks):
            out.append(res)
            spent += res["cost"]
            if spent > CAP_USD:
                print("cap reached, stopping"); break
    (B / OUTFILE).write_text(json.dumps(out, indent=1))
    print(f"{len(out)} gradings, {sum(1 for r in out if r['outcome'] is None)} unparsed, cost ${spent:.4f}")


if __name__ == "__main__":
    main()
