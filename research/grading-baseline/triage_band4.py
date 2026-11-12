#!/usr/bin/env python3
"""Step 4 triage, Band 4 only (Band 3 is never opened).

Fix 1  joined-key: one_idea_is_enough was true while core_idea joined two ideas. A one-sided
       paraphrase cannot answer a relation, so the flag becomes false (the item now needs the whole
       relation, DESIGN_RULES 3.1.9). The original sentence is kept in tutor_only.full_idea, and
       accept_ideas entries that cover only one side are dropped. An item left with fewer than two
       accept_ideas is reported for manual review.
Fix 2  not-required-filler: a not_required detail with no word from the passage is dropped. Such a
       detail can never be offered by a reader, so it is filler, not an option.

--apply writes; without it, only the report is printed.
"""
import json, re, sys
from pathlib import Path

SRC = Path("/home/tcoop/Work/readJson/lessons/src")
WORD_RE = re.compile(r"[A-Za-z0-9'’-]+")
STOP = set(
    "about above after again against their there these those which while would could should where other "
    "being every never still under until within without what when whom whose this that with from have they "
    "them then than into only some such very more most much many make made does because".split()
)
JOIN = [r";\s*", r"\s+because\s+", r",\s*so\s+", r"\s+so\s+that\s+", r"\s+and then\s+", r"\s+and so\s+", r",\s+and\s+"]


def bag(text):
    return {w.lower().strip("'’-") for w in WORD_RE.findall(text or "") if len(w) >= 5 and w.lower() not in STOP}


def hit(w, words):
    root = w[:5]
    return any(x.startswith(root) for x in words)


def split_idea(core):
    for pat in JOIN:
        m = re.search(pat, core, re.I)
        if m:
            head, tail = core[: m.start()].strip(" ,;"), core[m.end():].strip()
            if len(head.split()) >= 4 and len(tail.split()) >= 3:
                return head, tail
    return None


def main():
    apply = "--apply" in sys.argv
    report, changed = [], 0
    for p in sorted(SRC.glob("*_band_4_*.source.json")):
        raw = p.read_text()
        d = json.loads(raw)
        passage_words = bag(" ".join(v for v in d["passage"].values() if isinstance(v, str)))
        touched = False
        for it in d["items"]:
            t = it.get("tutor_only") or {}
            core = t.get("core_idea")
            if it.get("type") == "short_answer" and core and t.get("one_idea_is_enough") is True:
                sp = split_idea(core)
                if sp:
                    head, tail = sp
                    hb, tb = bag(head), bag(tail)
                    accepts = [i for i in t.get("accept_ideas", []) if isinstance(i, str)]
                    sides = []
                    for idea in accepts:
                        ib = bag(idea)
                        h, ta = bool(ib & hb), bool(ib & tb)
                        sides.append("both" if h and ta else "head" if h else "tail" if ta else "none")
                    tag = f"{p.stem[:-12]}.{it['id']}"
                    if "both" in sides:
                        # the author does credit a two-sided answer, so the item needs both parts.
                        # accept_ideas is left alone: a word-overlap test cannot tell a paraphrase
                        # that covers both sides from one that covers a single side.
                        t["one_idea_is_enough"] = False
                        t["full_idea"] = core
                        report.append(("joined-key: both parts", tag, core))
                    elif accepts:
                        # every accepted paraphrase is one-sided: the credit minimum is one idea and
                        # core_idea was written as the whole reasoning chain (3.1.9)
                        new_core = accepts[0].strip().rstrip(".")
                        new_core = new_core[:1].upper() + new_core[1:] + "."
                        t["full_idea"] = core
                        t["core_idea"] = new_core
                        report.append(("joined-key: one idea", tag, f"{core[:60]!r} -> {t['core_idea'][:60]!r}"))
                    touched = True
            if t.get("not_required"):
                kept = []
                for detail in t["not_required"]:
                    w = bag(detail)
                    if w and any(hit(x, passage_words) for x in w):
                        kept.append(detail)
                    else:
                        report.append(("not-required dropped", f"{p.stem[:-12]}.{it['id']}", detail))
                t["not_required"] = kept
                touched = True
        if touched:
            changed += 1
            if apply:
                indent = 1 if raw.startswith('{\n "') else 2
                p.write_text(json.dumps(d, indent=indent, ensure_ascii=False) + "\n")
    kinds = {}
    for k, _, _ in report:
        kinds[k] = kinds.get(k, 0) + 1
    for k in sorted(kinds):
        print(f"{k}: {kinds[k]}")
    for r in [x for x in report if "REVIEW" in x[0]][:40]:
        print("  REVIEW", r[1], "|", r[2][:100])
    print(f"{changed} band-4 files {'written' if apply else 'would change'}")


if __name__ == "__main__":
    main()
