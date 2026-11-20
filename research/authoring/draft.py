#!/usr/bin/env python3
"""Draft one lesson with the cheap writer model. Output is a draft, never a finished lesson.

    python3 draft.py spec.json --out draft.json

The spec carries the source text and the placement. Two calls: one adapts the passage to the band,
one drafts the five items. The fact guard is the important part of the prompt: models will happily
explain a "why" the source never gives, and at band 5 an invented explanation breaks 2.6.

Everything this returns is reviewed before it goes near lessons/src. The key fields are rewritten by
hand, because that is where a draft fails.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "grading-baseline"))
import grade as G  # noqa: E402

WRITER = "deepseek/deepseek-v4.1-flash-1017"

PASSAGE_SYSTEM = ("You adapt public-domain source text into reading passages for a lesson. "
                  "You reply with one JSON object and nothing else.")

PASSAGE_USER = """Adapt the SOURCE into three parts for a grade-5 reading lesson.

Rules:
- Use only what the source states. If the source does not explain why something happens, do not
  explain it, and do not add a cause the source leaves out.
- Flesch-Kincaid grade 5.5 to 6.5. Average 12 to 17 words per sentence; very short sentences put you
  below the target.
- 100 to 125 words per part. Do not write word counts, notes, or headings into the text.
- No exclamation marks, no praise, no questions to the reader.
- Part 1 introduces the subject, part 2 develops it, part 3 closes it.

Return only: {{"part_1": "...", "part_2": "...", "part_3": "..."}}

SOURCE:
{source}"""

ITEM_SYSTEM = ("You write items for a reading lesson. You never invent content that is not in the "
               "passage. You reply with one JSON array and nothing else.")

ITEM_USER = """Write five items for this lesson. The construct is central idea: what the passage says
as a whole, not one detail. Item order, in this order:

1. anchor - a stated detail that shows the reader has the text (difficulty 1)
2. join - connects two sentences the passage keeps apart (difficulty 2)
3. interpret - what the writer means by something stated (difficulty 2 or 3)
4. craft - why the passage is built or worded this way (difficulty 3)
5. synthesis - the central idea across all three parts (difficulty 3 or 4)

Rules:
- Each prompt asks exactly one thing. Never "what and why".
- show_part is the part that answers it; item 5 shows all three parts.
- One defensible answer. If two answers are defensible, change the prompt.
- core_idea: one sentence, the smallest true answer.
- one_idea_is_enough: true unless the prompt genuinely needs two parts joined.
- accept_ideas: 3 to 5 phrasings a student would actually write, in their words, not the passage's.
- tell: one or two sentences stating the answer plainly.
- confirm: one short sentence, no praise.
- if_they_say: one branch naming a real misreading and a one-sentence reply.

Return a JSON array of five objects, each with: prompt, show_part, difficulty, core_idea,
one_idea_is_enough, accept_ideas, tell, confirm, not_required, if_they_say.

PASSAGE:
part_1: {p1}
part_2: {p2}
part_3: {p3}"""


def ask(model, system, user, key, max_tokens=6000, tries=4):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    spent = 0.0
    for attempt in range(tries):
        r = requests.post(G.ENDPOINT, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=180)
        if r.status_code != 200:
            time.sleep(4 * (attempt + 1))
            continue
        d = r.json()
        spent += d.get("usage", {}).get("cost", 0) or 0
        text = d["choices"][0]["message"].get("content") or ""
        if text.strip():
            return text, spent
        time.sleep(5 * (attempt + 1))
    return "", spent


def block(text, opener):
    m = re.search(rf"(\{opener}.*\])" if opener == "[" else r"(\{.*\})", text, re.S)
    if not m:
        raise ValueError(f"no JSON in reply: {text[:200]!r}")
    return json.loads(m.group(1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--writer", default=WRITER)  # module-level default, overridden below
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    key = G.api_key()
    model = args.writer
    spend = 0.0

    raw, c = ask(model, PASSAGE_SYSTEM, PASSAGE_USER.format(source=spec["source"]), key)
    passage = block(raw, "{")
    spend += c
    repairs = 0
    while repairs < 2 and any(len(passage[k].split()) < 95 or len(passage[k].split()) > 130
                              for k in ("part_1", "part_2", "part_3")):
        repairs += 1
        ask2 = ("This draft is outside the word target. Rewrite each part to 100 to 125 words. "
                "Use only facts the source states. Do not add a cause or explanation the source "
                "leaves out. Do not write word counts into the text. Return only "
                '{"part_1": "...", "part_2": "...", "part_3": "..."}'
                "\n\nSOURCE:\n" + spec["source"] + "\n\nDRAFT:\n" +
                "\n\n".join(f"{k}: {passage[k]}" for k in ("part_1", "part_2", "part_3")))
        raw2, c2 = ask(model, PASSAGE_SYSTEM, ask2, key)
        spend += c2
        try:
            passage = block(raw2, "{")
        except Exception:
            pass
    def _fk(text):
        ss = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]
        ww = re.findall(r"[A-Za-z']+", text)
        def _syl(x):
            x = re.sub(r"[^a-z]", "", x.lower())
            if not x:
                return 0
            n = len(re.findall(r"[aeiouy]+", x))
            return max(1, n - 1 if x.endswith("e") and n > 1 else n)
        return 0.39 * len(ww) / len(ss) + 11.8 * sum(_syl(w) for w in ww) / len(ww) - 15.59

    joined = " ".join(passage[k] for k in ("part_1", "part_2", "part_3"))
    if _fk(joined) > 6.9:
        ask3 = ("This draft reads above the target reading level. Rewrite it at Flesch-Kincaid grade "
                "5.5 to 6.5: split long sentences, use common words, keep every fact, keep 100 to 125 "
                "words per part, and add nothing the source does not state. Return only "
                '{"part_1": "...", "part_2": "...", "part_3": "..."}'
                "\n\nSOURCE:\n" + spec["source"] + "\n\nDRAFT:\n" + joined)
        raw3, c3 = ask(model, PASSAGE_SYSTEM, ask3, key)
        spend += c3
        try:
            simpler = block(raw3, "{")
            if all(len(simpler[k].split()) >= 80 for k in ("part_1", "part_2", "part_3")):
                passage = simpler
                repairs += 1
        except Exception:
            pass

    raw2, c = ask(model, ITEM_SYSTEM, ITEM_USER.format(p1=passage["part_1"], p2=passage["part_2"],
                                                        p3=passage["part_3"]), key, max_tokens=6000)
    items = block(raw2, "[")
    spend += c

    out = {"lesson": spec["lesson"], "passage": passage, "items": items,
           "writer": model, "length_repairs": repairs, "cost": round(spend, 5)}
    Path(args.out).write_text(json.dumps(out, indent=1))
    words = {k: len(passage[k].split()) for k in ("part_1", "part_2", "part_3")}
    print(f"{spec['lesson']}: parts {words}, {len(items)} items, ${spend:.4f}")


if __name__ == "__main__":
    main()
