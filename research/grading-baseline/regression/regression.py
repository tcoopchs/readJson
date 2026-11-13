#!/usr/bin/env python3
"""Protocol regression: run every case we have against the live compiled lessons.

Three case files in this directory:
  owner_answers.json  answers the owner labelled across four sample rounds
  saybacks.json       scripted say-backs (copy, paraphrase, passage quote, denial)
  cloze.json          cloze synonyms and category words from the sweep

Each case is scored by three tutor models against the real compiled lesson (its tutoring_instructions,
scripts and tutor_only), so the result reflects what a student would actually meet.

Usage:
  python3 regression.py                 # all cases, 3 models
  python3 regression.py --models 1      # only the production model
  python3 regression.py --only sayback  # one file
  python3 regression.py --baseline      # write results/baseline.json for later comparison
  python3 regression.py --compare results/baseline.json
"""
import argparse, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

HERE = Path(__file__).parent
ROOT = Path("/home/tcoop/Work/readJson")
LESSONS = ROOT / "lessons"
sys.path.insert(0, str(HERE.parent))
import grade as G  # noqa: E402

MODELS = ["deepseek/deepseek-v4.1-flash-1017", "qwen/qwen3.8-flash", "google/gemini-3.8-flash"]
FILES = {"answer": "owner_answers.json", "sayback": "saybacks.json", "cloze": "cloze.json", "yesno": "yesno.json"}

ANSWER_SYS = ("You are the tutor for this lesson. Follow its tutoring instructions exactly. The passage and "
              "the question have been shown and the student has answered for the first time. Decide the "
              'outcome. Reply with JSON only: {"outcome": "CORRECT"|"UNCLEAR"|"MISS", "why": "<=12 words"}')
SAYBACK_SYS = ("You are the tutor for this lesson. Follow its tutoring instructions exactly. The passage and "
               "the question have been shown, tutor_only.tell has been said, and the student has replied. "
               'Decide what you do next. Reply with JSON only: {"outcome": "mercy"|"open"|"near_copy_1", '
               '"say": "the exact line you would say"}')

USER = """TUTORING INSTRUCTIONS
{instr}

SCRIPTS
{scripts}

PASSAGE ON SCREEN
{passage}

QUESTION
{prompt}

tutor_only
{tutor_only}

{state}
{answer}

JSON only."""


def api_key():
    for line in (Path.home() / ".hermes/.env").read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("no key")


def call(model, system, user, key):
    body = {"model": model, "temperature": 0, "max_tokens": 1500, "usage": {"include": True},
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


SYNONYMS = {
    "sayback": [("near_copy_1", r"near[-_ ]?copy|my wording|is a copy|repeat(s|ing)? (my|the) tell"),
                ("mercy", r"\bmercy\b|in (their|his|her|your) own words|accept the say-back|mark (it )?correct"),
                ("open", r"\bopen\b|does not state|literal restatement|mark (it )?(a )?miss|incomplete")],
    "answer": [("CORRECT", r"\bcorrect\b|accept"),
               ("UNCLEAR", r"unclear|not clear|say more|ambiguou"),
               ("MISS", r"\bmiss\b|not quite|incorrect|reject")],
}


def verdict(text, kind):
    key = "sayback" if kind == "sayback" else "answer"
    for label, pattern in SYNONYMS[key]:
        if re.search(pattern, text or "", re.I):
            return label
    return None


def load(kind):
    return json.loads((HERE / FILES[kind]).read_text())["cases"]


def run_case(kind, case, model, key):
    lesson = json.loads((LESSONS / f"{case['lesson']}.json").read_text())
    item = next(x for x in lesson["items"] if str(x["id"]) == str(case["item"]))
    sp = item.get("show_part")
    passage = "\n\n".join(lesson["passage"].values()) if sp in (None, "all") else lesson["passage"][sp]
    state = ("You already said tutor_only.tell. The student's say-back:" if kind == "sayback"
             else "The student's first answer:")
    user = USER.format(instr="\n".join(f"- {s}" for s in lesson["tutoring_instructions"]),
                       scripts=json.dumps(lesson["script"], indent=1), passage=passage,
                       prompt=item["prompt"], tutor_only=json.dumps(item["tutor_only"], indent=1),
                       state=state, answer=case["answer"])
    system = SAYBACK_SYS if kind == "sayback" else ANSWER_SYS
    cost = 0.0
    for _ in range(3):  # a model that answers in prose is a harness flake, not a behaviour
        text, c = call(model, system, user, key)
        cost += c
        v = verdict(text, kind)
        if v:
            return v, cost
    return None, cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", type=int, default=3)
    ap.add_argument("--only", choices=list(FILES))
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--compare")
    args = ap.parse_args()
    key = api_key()
    models = MODELS[: args.models]
    kinds = [args.only] if args.only else list(FILES)
    jobs = [(kind, c) for kind in kinds for c in load(kind)]
    results, spent = {}, 0.0

    def work(job):
        kind, case = job
        out = {}
        for m in models:
            v, cost = run_case(kind, case, m, key)
            out[m] = v
            nonlocal spent
            spent += cost
        return case["id"], kind, out

    with ThreadPoolExecutor(max_workers=6) as pool:
        for cid, kind, out in pool.map(work, jobs):
            results[cid] = {"kind": kind, "expect": next(c["expect"] for c in load(kind) if c["id"] == cid),
                            "got": out}
    # majority of three: one model dissenting is provider nondeterminism, not a behaviour change
    def votes(r):
        vals = [v for v in r["got"].values()]
        return sum(1 for v in vals if v == r["expect"]), len(vals)
    passed = {cid: (votes(r)[0] * 2 > votes(r)[1]) for cid, r in results.items()}
    for cid, r in results.items():
        ok, n = votes(r)
        flag = "PASS" if passed[cid] else "FAIL"
        detail = " ".join(f"{m.split('/')[-1][:9]}={v}" for m, v in r["got"].items())
        print(f"{flag} {cid:4} {ok}/{n} expect {r['expect']:11} {detail}")
    print(f"\n{sum(passed.values())}/{len(passed)} cases pass by majority, cost ${spent:.3f}")
    outdir = HERE / "results"
    outdir.mkdir(exist_ok=True)
    if args.baseline:
        (outdir / "baseline.json").write_text(json.dumps(results, indent=1))
        print("baseline written")
    if args.compare:
        base = json.loads(Path(args.compare).read_text())
        regressed = [cid for cid in results if cid in base and passed.get(cid) is False]
        print(f"regressions vs {args.compare}: {regressed or 'none'}")
    return 0 if all(passed.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
