#!/usr/bin/env python3
"""S1b: (1) an independent labeller (different model family, no key) labels all 96 answers under the
decisions; (2) the three tutor models re-score with the decisions added to the rules and the four
defective keys patched in memory (lesson files untouched)."""
import json, re, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
import grade as G

B = Path(__file__).parent
LABELLER = "openai/gpt-5.6-terra"
CAP_USD = 2.00
DECISIONS = (B / "DECISIONS.md").read_text()

ADDED_RULES = """
- A key may need more than one part. If the answer gives only part of what the key needs, it is Not quite.
- Quoting a passage sentence is correct only when that sentence itself answers the question. A sentence that reports what happened, when the question asks why, what it shows, or what something did, is Not quite.
- Use Not clear yet only when the answer names something from the passage that could be the key idea but cannot be pinned down (an unclear "it", or a word with two readings). An answer with no passage content ("it comes from something", "it makes things better") is Not quite.
- A yes/no question answered with the correct verdict only is Correct when the question did not ask for a reason."""

# authoring-time key fixes the decisions call for (D3/D4); simulated, not written to lessons
KEY_PATCH = {
    "S04": {"accept_ideas_add": ["the branding iron", "the iron has the gap in it"]},
    "S06": {"core_idea": "With the sand in the holes, water went into the soil instead of running off, and the roots followed it down.",
            "accept_ideas_add": ["it let water in", "it helped drainage", "it helped the roots grow deeper"]},
    "S11": {"accept_ideas_add": ["a thick block saves money at sea", "a thin block costs more at sea"]},
    "S12": {"accept_ideas_add": ["it shades out weeds"], "drop_if": "covers the ground and blocks weeds"},
}

LAB_SYSTEM = ("You are an experienced reading teacher labelling a student's answer to a reading question. "
              "You have no answer key: judge from the passage and the question alone, under the scoring decisions "
              'given. Reply with JSON only: {"label": "CORRECT" | "UNCLEAR" | "MISS", "why": "<=20 words"}')
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


def call(model, system, user, key, max_tokens=3000):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(G.ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=180)
            r.raise_for_status()
            d = r.json()
            txt = d["choices"][0]["message"]["content"] or ""
            if not re.search(r"CORRECT|UNCLEAR|MISS", txt.upper()) and attempt < 2:
                continue
            return txt, d.get("usage", {}).get("cost", 0) or 0
        except Exception as e:
            if attempt == 2:
                return f"ERROR {e}", 0
            time.sleep(3)
    return "", 0


def outcome(t, words=("CORRECT", "UNCLEAR", "MISS")):
    m = re.search("(" + "|".join(words) + ")", t.upper())
    return m.group(1) if m else None


def main():
    key = G.api_key()
    items = {i["sid"]: i for i in json.loads((B / "items.json").read_text())}
    answers = json.loads((B / "answers.json").read_text())
    tasks = []
    for a in answers:
        it = items[a["sid"]]
        tasks.append(("label", a["aid"], LABELLER, LAB_SYSTEM,
                      LAB_USER.format(decisions=DECISIONS, passage=it["passage"], prompt=it["prompt"], answer=a["answer"])))
        compiled = json.loads((G.LESSONS / f"{it['lesson']}.json").read_text())
        to = json.loads(json.dumps(next(x for x in compiled["items"] if str(x["id"]) == str(it["item"]))["tutor_only"]))
        p = KEY_PATCH.get(a["sid"])
        if p:
            if "core_idea" in p:
                to["core_idea"] = p["core_idea"]
            to["accept_ideas"] = to.get("accept_ideas", []) + p.get("accept_ideas_add", [])
            if "drop_if" in p:
                to["if_they_say"] = [b for b in to.get("if_they_say", []) if p["drop_if"] not in b["when"]]
        user = G.USER.format(rules=G.RULES + ADDED_RULES, passage=it["passage"], prompt=it["prompt"],
                             tutor_only=json.dumps(to, indent=1), answer=a["answer"])
        for m in G.MODELS:
            tasks.append(("tutor", a["aid"], m, G.SYSTEM, user))
    spent, out = 0.0, []

    def run(t):
        kind, aid, m, sysm, user = t
        txt, cost = call(m, sysm, user, key)
        return {"kind": kind, "aid": aid, "model": m, "outcome": outcome(txt), "raw": txt[:300], "cost": cost}

    with ThreadPoolExecutor(max_workers=8) as pool:
        for res in pool.map(run, tasks):
            out.append(res)
            spent += res["cost"]
    (B / "round2.json").write_text(json.dumps(out, indent=1))
    print(f"{len(out)} calls, {sum(1 for r in out if r['outcome'] is None)} unparsed, cost ${spent:.4f}")
    if spent > CAP_USD:
        print("OVER CAP")


if __name__ == "__main__":
    main()
