#!/usr/bin/env python3
"""Assemble a lesson source from a writer draft plus the placement metadata.

    python3 assemble.py plan.json --out lessons/src/<id>.source.json

The plan holds one entry per lesson: id, title, domain, source block, and the draft path. Item
fields the writer does not produce (skill, help, say_back, correct_reason, full_idea, show_part_again)
are filled here. Routes are computed from the ladder: advance goes to the next authored rung, retry
to the next sequence in this rung, stopped to this lesson.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path("/home/tcoop/Work/readJson")
SCHEMA_VERSION = 3


def syl(x):
    x = re.sub(r"[^a-z]", "", x.lower())
    if not x:
        return 0
    n = len(re.findall(r"[aeiouy]+", x))
    return max(1, n - 1 if x.endswith("e") and n > 1 else n)


def fk(text):
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    return round(0.39 * len(words) / len(sentences)
                 + 11.8 * sum(syl(w) for w in words) / len(words) - 15.59, 1)


def _show_part(v):
    v = str(v or "").strip().lower().replace("-", "_").replace(" ", "_")
    if v in {"all", "all_parts", "all_three_parts", "all_3_parts", "parts_1_2_3", "three_parts"}:
        return "all"
    if v in {"part_1", "part_2", "part_3"}:
        return v
    if v in {"1", "2", "3"}:
        return f"part_{v}"
    return "part_1"


def item(e, seq_index, skill):
    """Normalise one drafted item into the source schema."""
    branch = e.get("if_they_say") or []
    if isinstance(branch, dict):
        branch = [branch]
    out_branches = []
    for b in branch[:2]:
        if isinstance(b, str):
            b = {"when": b, "ask": "Say what the passage states, in your own words."}
        when = b.get("when") or b.get("condition") or "the student says something off the point"
        ask = b.get("ask") or b.get("say") or b.get("reply") or ""
        if ask:
            out_branches.append({"when": when.strip(), "ask": ask.strip()})
    return {
        "id": str(seq_index + 1),
        "type": e.get("type", "short_answer"),
        "skill": skill,
        "difficulty": int(e.get("difficulty", 2)),
        "show_part": _show_part(e.get("show_part", "part_1")),
        "show_part_again": False,
        "prompt": e["prompt"].strip(),
        "tutor_only": {
            "confirm": (e.get("confirm") or "").strip(),
            "correct_reason": (e.get("correct_reason") or e.get("tell") or "").strip(),
            "tell": (e.get("tell") or "").strip(),
            "help": [f"Look again at {e.get('show_part', 'part_1').replace('_', ' ')}.",
                     "Say what the passage states in your own words."],
            "say_back": "own_words",
            "core_idea": (e.get("core_idea") or "").strip(),
            "accept_ideas": [a.strip() for a in (e.get("accept_ideas") or []) if a and a.strip()],
            "one_idea_is_enough": bool(e.get("one_idea_is_enough", True)),
            "not_required": [n.strip() for n in (e.get("not_required") or []) if n and n.strip()],
            "if_they_say": out_branches,
            "full_idea": (e.get("full_idea") or e.get("core_idea") or "").strip(),
        },
    }


def build(entry, ladder):
    draft = json.loads(Path(entry["draft"]).read_text())
    passage = draft["passage"]
    lid = entry["id"]
    skill, grade, stage, seq = re.match(r"(.+)_band_(\d+)_(\d+)_(\d+)", lid).groups()
    grade, stage, seq = int(grade), int(stage), int(seq)
    full = " ".join(passage[k] for k in ("part_1", "part_2", "part_3"))
    measured = fk(full)

    higher = [x for x in ladder.get(skill, []) if x > (grade, stage)]
    if higher:
        adv = (f"{skill}_band_{higher[0][0]}_{higher[0][1]}_0001", higher[0][0],
               f"The first {skill.replace('_', ' ')} lesson in Band {higher[0][0]}.{higher[0][1]}.")
    else:
        adv = (lid, grade, f"No higher {skill.replace('_', ' ')} rung is authored yet; hold in this lesson.")
    retry = lid if seq >= 6 else f"{skill}_band_{grade}_{stage}_{seq + 1:04d}"

    return {
        "schema_version": SCHEMA_VERSION,
        "document_type": "lesson_source",
        "lesson_id": lid,
        "meta": {
            "status": "published",
            "title": entry["title"],
            "skill": skill,
            "irl_grade": grade,
            "stage": stage,
            "sequence": seq,
            "genre": "nonfiction",
            "topic_domain": entry["domain"],
            "skill_frame": entry["skill_frame"],
            "reader": {
                "who": "Older students who read at about a fifth-grade level.",
                "reading_level": grade,
                "why_this_level": entry["why_this_level"].replace("{fk}", str(measured)),
                "tone": "Adult subject. Plain sentences. The lesson must not make the reader feel small.",
            },
            "source": entry["source"],
            "session": {"scope": "build-band", "item_target": 5, "time_target_minutes": 14,
                        "difficulty_basis": "How far the stated idea sits from the words the passage uses."},
            "authoring_exceptions": [],
        },
        "script_overrides": {"near_copy_2": "Say it in your own words. One sentence is enough."},
        "passage": {k: passage[k].strip() for k in ("part_1", "part_2", "part_3")},
        "items": [item(e, i, skill) for i, e in enumerate(draft["items"])],
        "advance": {"next_file": adv[0], "next_irl": adv[1], "next_means": adv[2],
                    "student_line": f"You found the idea across the whole passage. The next reading is another {skill.replace('_', ' ')} lesson."},
        "retry": {"next_file": retry, "next_irl": grade,
                  "next_means": "Another lesson in this stage." if retry != lid else "This same lesson, so it can be read again.",
                  "student_line": "You have most of the move. The next reading is another main-idea lesson."},
        "stopped": {"next_file": lid, "next_irl": grade, "next_means": "This same lesson, so it can be finished."},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--outdir", default=str(ROOT / "lessons/src"))
    args = ap.parse_args()
    plan = json.loads(Path(args.plan).read_text())
    ladder = {}
    for p in (ROOT / "lessons/src").glob("*.source.json"):
        m = re.match(r"(.+)_band_(\d+)_(\d+)_(\d+)", p.name.replace(".source.json", ""))
        if m:
            ladder.setdefault(m.group(1), set()).add((int(m.group(2)), int(m.group(3))))
    ladder = {k: sorted(v) for k, v in ladder.items()}
    made = []
    for entry in plan["lessons"]:
        src = build(entry, ladder)
        out = Path(args.outdir) / f"{entry['id']}.source.json"
        out.write_text(json.dumps(src, indent=2, ensure_ascii=False) + "\n")
        sk = src["meta"]["skill"]
        rung = (src["meta"]["irl_grade"], src["meta"]["stage"])
        ladder[sk] = sorted(set(ladder.get(sk, [])) | {rung})
        made.append((entry["id"], len(src["items"]), fk(" ".join(src["passage"].values()))))
    for m in made:
        print(f"wrote {m[0]}: {m[1]} items, FK {m[2]}")


if __name__ == "__main__":
    main()
