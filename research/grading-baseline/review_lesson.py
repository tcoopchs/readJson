#!/usr/bin/env python3
"""Review sheet for one or more lessons before merge.

Runs the machine gates, then the key probe: a cheap student model writes eight answers per item from
the passage and prompt only (never the key), and three tutor models score them under the live compiled
protocol. Prints one sheet per lesson for a human to read: the passage, every prompt, its key, and any
item where a likely-right answer was rejected or a wrong answer accepted.

    python3 review_lesson.py authors_craft_band_5_1_0007 [more ids...]
    python3 review_lesson.py --sheet reviews/band5.md <ids>

Cost is about $0.15 per lesson. Exit code 0 means no flag; 1 means read the flags before merging.
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


def review(lid, key):
    src = json.loads((ROOT / "lessons/src" / f"{lid}.source.json").read_text())
    compiled = json.loads((ROOT / "lessons" / f"{lid}.json").read_text())
    out = {"lesson": lid, "title": src["meta"].get("title"), "genre": src["meta"].get("genre"),
           "status": src["meta"].get("status"), "source": src["meta"].get("source"), "items": [],
           "spend": 0.0}
    for item in src["items"]:
        ci = next(x for x in compiled["items"] if str(x["id"]) == str(item["id"]))
        passage = A.passage_of(src, item)
        raw, cost = call(STUDENT, A.SYSTEM, A.PROMPT.format(passage=passage, prompt=item["prompt"]), key)
        out["spend"] += cost
        try:
            answers = A.json_block(raw)
        except Exception:
            answers = {}
        tasks = [(typ, ans, m) for typ, ans in answers.items() for m in G.MODELS]
        def score(t):
            typ, ans, m = t
            user = G.USER.format(rules=G.RULES, passage=passage, prompt=ci["prompt"],
                                 tutor_only=json.dumps(ci["tutor_only"], indent=1), answer=ans)
            text, c = call(m, G.SYSTEM, user, key, max_tokens=1200)
            return typ, m.split("/")[-1][:10], verdict(text), c
        rows = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            for typ, mname, v, c in pool.map(score, tasks):
                out["spend"] += c
                rows.setdefault(typ, {"answer": answers[typ], "verdicts": {}})["verdicts"][mname] = v
        out["items"].append({"id": item["id"], "type": item.get("type"), "difficulty": item.get("difficulty"),
                             "show_part": item.get("show_part"), "prompt": item["prompt"],
                             "key": ci["tutor_only"].get("core_idea") or ci["tutor_only"].get("accept_words"),
                             "flag": ci["tutor_only"].get("one_idea_is_enough"),
                             "accepts": ci["tutor_only"].get("accept_ideas"), "rows": rows})
    return out


def flags_for(item):
    f = []
    lr = item["rows"].get("likely_right", {}).get("verdicts", {})
    wr = item["rows"].get("wrong", {}).get("verdicts", {})
    if sum(1 for v in lr.values() if v == "MISS") >= 2:
        f.append("likely-right answer rejected")
    if sum(1 for v in wr.values() if v == "CORRECT") >= 2:
        f.append("wrong answer accepted")
    return f


def sheet(res):
    lines = [f"# {res['lesson']} — {res['title']}", "",
             f"genre: {res['genre']} | status: {res['status']}",
             f"source basis: {res['source'].get('basis')}",
             f"attribution: {res['source'].get('attribution')}",
             f"text status: {res['source'].get('text_status')}", ""]
    total = sum(len(flags_for(i)) for i in res["items"])
    lines.append(f"**{total} flag(s)** across {len(res['items'])} items")
    for it in res["items"]:
        f = flags_for(it)
        lines += ["", f"## item {it['id']} (d{it['difficulty']}, {it['type']}, shows {it['show_part']})",
                  f"**Q:** {it['prompt']}", f"**Key:** {it['key']}", f"flag one_idea_is_enough: {it['flag']}"]
        if it["accepts"]:
            lines.append(f"**Accepts:** {'; '.join(it['accepts'])}")
        if f:
            lines.append(f"**FLAG:** {', '.join(f)}")
            for typ in ("likely_right", "wrong"):
                if typ in it["rows"]:
                    r = it["rows"][typ]
                    lines.append(f"- {typ}: \"{r['answer']}\" -> {r['verdicts']}")
        else:
            lines.append("no flag")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lessons", nargs="+")
    ap.add_argument("--sheet", help="write a markdown review sheet here")
    args = ap.parse_args()
    key = G.api_key()
    results, total = [], 0.0
    for lid in args.lessons:
        res = review(lid, key)
        results.append(res)
        total += res["spend"]
        print(sheet(res))
        print()
    flagged = sum(1 for r in results for i in r["items"] if flags_for(i))
    print(f"== {len(results)} lesson(s), {flagged} flagged item(s), ${total:.3f}")
    if args.sheet:
        Path(args.sheet).parent.mkdir(parents=True, exist_ok=True)
        Path(args.sheet).write_text("\n\n---\n\n".join(sheet(r) for r in results) + "\n")
        print(f"sheet written to {args.sheet}")
    return 0 if flagged == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
