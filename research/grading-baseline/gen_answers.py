#!/usr/bin/env python3
"""S1 step 1-2: pick 12 landed Band 4 items and have a cheap model write 8 student answers each.

The student model sees only the passage and the prompt, never the key.
Output: items.json (selected items with keys) and answers.json (8 answers per item).
"""
import json, random, re, subprocess, sys, time
from pathlib import Path
import requests

ROOT = Path("/home/tcoop/Work/readJson")
OUT = ROOT / "research/grading-baseline"
STUDENT = "openai/gpt-4o-mini"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def api_key():
    for line in (Path.home() / ".hermes/.env").read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("no key")


def call(model, system, user, key, max_tokens=900):
    body = {"model": model, "temperature": 0.7, "max_tokens": max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    for attempt in range(3):
        try:
            r = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"], d.get("usage", {}).get("cost", 0) or 0
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2)


def json_block(t):
    t = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip()
    return json.loads(t[t.find("{"): t.rfind("}") + 1])


def passage_of(lesson, item):
    p = item.get("show_part")
    if p in (None, "all"):
        return "\n\n".join(lesson["passage"].values())
    return lesson["passage"][p]


SYSTEM = ("You simulate real students aged 12-18 and adults reading below grade level, answering a reading "
          "question in a chat. Students write short, casual, sometimes sloppy answers with minor spelling "
          "errors. Never use teacher or textbook wording. Reply with JSON only.")

PROMPT = """PASSAGE
{passage}

QUESTION
{prompt}

Write eight different student answers, one per type below. Each is what a real student would type: usually
one short sentence or a fragment. Do not label or explain them.

- "likely_right": the answer most students who understood would actually type.
- "short_right": a correct answer in 2-6 words.
- "half": an answer that gets only part of what the question needs (if the full answer has two pieces, give one).
- "vague": an answer pointing in the right direction but too vague to tell what the student means (e.g. uses "it" or "that" with no clear referent, or a general word).
- "echo": an answer that mostly repeats the question's own words or a passage sentence without answering what is asked.
- "literal": an answer that reports what happens in the passage when the question asks why, what it shows, or what it does.
- "plausible_wrong": a wrong answer a real student might give from a misreading of the passage.
- "alternative": a different answer from the one a teacher expects, which a careful reader could still defend from the passage. If none is defensible, give the most defensible different answer you can.

JSON only: {{"likely_right": "...", "short_right": "...", "half": "...", "vague": "...", "echo": "...", "literal": "...", "plausible_wrong": "...", "alternative": "..."}}"""


def select():
    tracked = subprocess.run(["git", "ls-files", "lessons/src"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    pool = {}
    for rel in tracked:
        if "_band_4_" not in rel:
            continue
        lesson = json.loads((ROOT / rel).read_text())
        cat = lesson["lesson_id"].split("_band_")[0]
        for it in lesson["items"]:
            if it.get("type") == "short_answer" and (it.get("difficulty") or 0) >= 2:
                pool.setdefault(cat, []).append((lesson, it))
    rng = random.Random(20261112)
    chosen, used_lessons = [], set()
    cats = sorted(pool)
    def pick(cat, min_d):
        cands = [(l, i) for l, i in pool[cat] if (i.get("difficulty") or 0) >= min_d and l["lesson_id"] not in used_lessons]
        l, i = rng.choice(cands)
        used_lessons.add(l["lesson_id"])
        chosen.append((l, i))
    for c in cats:
        pick(c, 2)
    for c in rng.sample(cats, 4):
        pick(c, 3)
    return chosen


def main():
    key = api_key()
    chosen = select()
    items, answers, cost = [], [], 0.0
    for n, (lesson, it) in enumerate(chosen, 1):
        passage = passage_of(lesson, it)
        t = it["tutor_only"]
        iid = f"S{n:02d}"
        items.append({"sid": iid, "lesson": lesson["lesson_id"], "item": it["id"], "difficulty": it.get("difficulty"),
                      "show_part": it.get("show_part"), "passage": passage, "prompt": it["prompt"],
                      "key": {k: t.get(k) for k in ("core_idea", "accept_ideas", "not_required", "confirm", "tell",
                                                     "partial", "if_they_say", "normalize")}})
        raw, c = call(STUDENT, SYSTEM, PROMPT.format(passage=passage, prompt=it["prompt"]), key)
        cost += c
        a = json_block(raw)
        for typ, text in a.items():
            answers.append({"sid": iid, "type": typ, "answer": text})
        print(iid, lesson["lesson_id"], it["id"], f"d{it.get('difficulty')}", len(a))
    (OUT / "items.json").write_text(json.dumps(items, indent=1))
    rng = random.Random(7)
    for i, a in enumerate(answers):
        a["aid"] = f"A{i+1:03d}"
    (OUT / "answers.json").write_text(json.dumps(answers, indent=1))
    print(f"{len(items)} items, {len(answers)} answers, cost ${cost:.4f}")


if __name__ == "__main__":
    main()
