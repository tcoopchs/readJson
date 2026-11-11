#!/usr/bin/env python3
"""LessonBot: one process, one rung, then exit.

The bot never invents a source. Every passage is adapted from a human-written work
listed in plan.json, under DESIGN_RULES 2.5, with the license recorded. It drafts
the six lessons of one rung, compiles them, runs the publish gates, and stops.

    python3 bot.py preflight          # plan, domain spread, sources, budget
    python3 bot.py run                # author the rung; hard-stop on a gate failure
    python3 bot.py status             # spend and phase
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import random
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

BOT = pathlib.Path(__file__).resolve().parent
ROOT = BOT.parents[1]
SRC = ROOT / "lessons" / "src"
LESSONS = ROOT / "lessons"
HARNESS = pathlib.Path("/home/tcoop/Work/readingHarness")
SKILL = pathlib.Path.home() / ".hermes/skills/productivity/readjson-lessons"
STATE = BOT / "state.json"
LEDGER = BOT / "ledger.jsonl"
BAND = {"fk_low": 4.6, "fk_high": 7.7, "words_low": 100, "words_high": 150,
        "mean_low": 12, "mean_high": 22}
MAX_REPAIRS = 2


# ---------------------------------------------------------------- measurement
def _load_measure():
    spec = importlib.util.spec_from_file_location("mp", SKILL / "scripts/measure_passage.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MP = _load_measure()


def sentence_stats(text: str) -> tuple[int, float]:
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if len(re.findall(r"[A-Za-z']+", s)) >= 3]
    words = MP.words(text)
    return len(sents), (words / len(sents) if sents else 0.0)


def measure(parts: dict) -> dict:
    out = {}
    for key, text in parts.items():
        n = MP.words(text)
        out[key] = {"words": n, "fk": MP.fk(text), "sents": sentence_stats(text)[0],
                    "mean": round(sentence_stats(text)[1], 1)}
    return out


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(re.findall(r"[A-Za-z']+", s)) >= 3]


def nudge_to_band(parts: dict) -> dict:
    """Deterministic first aid. Trim overlong parts, split a sentence when the score is
    too high, join a pair when it is too low. No facts are added or removed."""
    out = {}
    for key, text in parts.items():
        sents = _sentences(text)
        while len(sents) > 2 and MP.words(" ".join(sents)) > BAND["words_high"]:
            sents.pop()
        # split the longest joinable sentence while the score is too high
        while len(sents) < 14:
            score = MP.fk(" ".join(sents))
            if score is None or score <= BAND["fk_high"]:
                break
            picked = None
            for i, s in enumerate(sents):
                for mark in (", and ", "; "):
                    if mark in s:
                        left, right = s.split(mark, 1)
                        if MP.words(left) >= 7 and MP.words(right) >= 7:
                            picked = (i, left + ".", right)
                            break
                if picked:
                    break
            if not picked:
                break
            i, left, right = picked
            sents[i:i + 1] = [left, right[0].upper() + right[1:]]
        # join a pair while the mean is low or the score is too easy
        while len(sents) > 2:
            joined = " ".join(sents)
            mean = MP.words(joined) / len(sents)
            score = MP.fk(joined)
            if mean >= BAND["mean_low"] and (score is None or score >= BAND["fk_low"]):
                break
            if mean >= 20:
                break
            cands = [(abs(MP.words(sents[i]) + MP.words(sents[i + 1]) - 32), i)
                     for i in range(len(sents) - 1)
                     if MP.words(sents[i]) + MP.words(sents[i + 1]) <= 34]
            if not cands:
                break
            _, i = min(cands)
            nxt = sents[i + 1]
            if not re.match(r"^(I\b|I'm|I've|I'll|I'd)", nxt):
                nxt = nxt[0].lower() + nxt[1:]
            sents[i:i + 2] = [sents[i].rstrip(".!?") + "; " + nxt]
        out[key] = " ".join(sents)
    return out


def repair_part(state: dict, plan: dict, key: str, text: str, want: str) -> str:
    """One targeted rewrite of a single part, aimed at the measured problem."""
    if want == "simpler":
        instruction = ("Rewrite this part at Flesch-Kincaid 5.0-6.5. Use only common one- and "
                       "two-syllable words except names, and split any sentence over 22 words. "
                       "Keep every fact and the author's voice.")
    elif want == "harder":
        instruction = ("Rewrite this part at Flesch-Kincaid 5.0-6.5. Use more exact words and "
                       "join two short sentences. Keep every fact and the author's voice.")
    elif want == "longer":
        instruction = ("Rewrite this part 20-30 words longer, adding only detail that is already "
                       "in the source. Keep the same reading level and voice.")
    else:
        instruction = ("Rewrite this part 20-30 words shorter, dropping the least important "
                       "detail. Keep every fact an item depends on and keep the voice.")
    content = (instruction + "\n\nPART (" + key + "):\n" + text + "\n\n"
               'Return JSON {"part": "..."}.')
    obj, _ = call(state, plan, [{"role": "user", "content": content}],
                  temperature=0.3, max_tokens=900)
    return re.sub(r"\s+", " ", str(obj.get("part", ""))).strip() or text


def out_of_band(m: dict) -> list[str]:
    bad = []
    for key, v in m.items():
        if not BAND["words_low"] <= v["words"] <= BAND["words_high"]:
            bad.append(f"{key}: {v['words']} words (need {BAND['words_low']}-{BAND['words_high']})")
        if v["fk"] is None or not BAND["fk_low"] <= v["fk"] <= BAND["fk_high"]:
            bad.append(f"{key}: FK {v['fk']} (need {BAND['fk_low']}-{BAND['fk_high']})")
        if not BAND["mean_low"] <= v["mean"] <= BAND["mean_high"]:
            bad.append(f"{key}: mean sentence {v['mean']} (need {BAND['mean_low']}-{BAND['mean_high']})")
    return bad


# ---------------------------------------------------------------- state / spend
def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"status": "new", "spend_usd": 0.0, "calls": 0, "phase": "preflight",
            "lessons": {}, "failures": []}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def log(record: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **record}) + "\n")


def die(state: dict, reason: str) -> None:
    state["status"] = "failed"
    state["failures"].append(reason)
    save_state(state)
    log({"event": "terminate", "reason": reason})
    print(f"\nTERMINATED: {reason}", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- model call
def api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env = pathlib.Path.home() / ".hermes/.env"
    for line in env.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY not set")


def call(state: dict, plan: dict, messages: list, *, temperature=0.7,
         max_tokens=2400, json_mode=True, model=None) -> tuple[dict, float]:
    cap = plan["budget_cap_usd"]
    if state["spend_usd"] >= cap:
        die(state, f"budget cap reached ({state['spend_usd']:.4f} >= {cap})")
    body = {
        "model": model or plan["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "usage": {"include": True},
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:400]
        die(state, f"model call failed HTTP {exc.code}: {detail}")
    cost = float(data.get("usage", {}).get("cost") or 0.0)
    state["spend_usd"] = round(state["spend_usd"] + cost, 6)
    state["calls"] += 1
    save_state(state)
    log({"event": "call", "model": model or plan["model"], "cost": cost,
         "spend": state["spend_usd"], "phase": state["phase"]})
    if state["spend_usd"] > cap:
        die(state, f"budget cap exceeded after call ({state['spend_usd']:.4f} > {cap})")
    text = data["choices"][0]["message"]["content"] or ""
    if not json_mode:
        return text, cost
    try:
        return json.loads(text), cost
    except json.JSONDecodeError:
        log({"event": "bad_json", "phase": state["phase"], "finish_reason":
             data["choices"][0].get("finish_reason"), "usage": data.get("usage"),
             "text": text[:3000]})
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise ValueError("model returned no JSON object")
        return json.loads(m.group(0)), cost


# ---------------------------------------------------------------- phases
def preflight(plan: dict, state: dict) -> None:
    domains = [l["domain"] for l in plan["lessons"]]
    if len(plan["lessons"]) != 6:
        die(state, f"rung must hold 6 lessons, plan holds {len(plan['lessons'])}")
    if any(a == b for a, b in zip(domains, domains[1:])):
        die(state, f"topic-domain breach: adjacent lessons share a domain {domains}")
    if len(set(domains)) < 4:
        die(state, f"topic-domain breach: only {len(set(domains))} domains across the rung")
    for l in plan["lessons"]:
        src = BOT / "sources" / l["source_file"]
        if not src.exists():
            die(state, f"missing source {src}")
        if MP.words(src.read_text()) < 350:
            die(state, f"source {src.name} under 350 words")
        for k in ("basis", "attribution", "text_status", "adaptation"):
            if not l["source"].get(k):
                die(state, f"lesson {l['sequence']} source metadata missing {k}")
    if state["spend_usd"] >= plan["budget_cap_usd"]:
        die(state, "budget already exhausted")
    print(f"preflight ok: 6 lessons, domains {domains}, spend ${state['spend_usd']:.4f}")


ADAPT_SYSTEM = """You are a careful editor, not a writer. You are given numbered source sentences for one part of a lesson. Return exactly one line for every sentence, in order, and nothing else:

<id>|keep
<id>|drop
<id>|simplify|<the simplified sentence>

Keep means use the sentence unchanged. Simplify means rewrite it in simpler words with the same meaning: shorter sentences, common words, split clauses, removed asides. You may not add a fact, a name, a number, a question, a metaphor, an example, or an opinion that is not in that sentence. Keep any repeated word or phrase that carries the craft.

This part must end at 100-150 words, so keep enough sentences. Drop the least important ones."""

HYPE = re.compile(r"\b(have you ever|how cool|isn[’']t|amazing|wonder(?:ful)?|secret|"
                  r"beautiful|you wouldn[’']t want|right\?)\b", re.I)
STOP = set("a an the and or but of to in on at for with from by as is are was were be been "
           "being it its this that these those he she they them his her their you your i we "
           "our not no so if then than there here what which who whom whose how why when "
           "where do does did have has had can could would should will shall may might must".split())


def content_words(text: str) -> set:
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOP and len(w) > 2}


def check_row(text: str, mapped: str) -> tuple[list[str], bool]:
    """Every output sentence must be a simplification of the source sentences it names.
    Returns (problems, needs_semantic_check); a full synonym swap is checked by a second call."""
    probs = []
    cw, mw = content_words(text), content_words(mapped)
    needs = not (cw & mw)
    if set(re.findall(r"\d+", text)) - set(re.findall(r"\d+", mapped)):
        probs.append("adds a number the source does not give")
    if "?" in text and "?" not in mapped:
        probs.append("adds a question the source does not ask")
    hit = HYPE.search(text)
    if hit:
        probs.append(f"adds hype or a tag question ({hit.group(0)!r})")
    if re.search(r"[\x00-\x1f]", text):
        probs.append("contains a control character")
    caps = set()
    for s in re.split(r"(?<=[.!?])\s+", text):
        body = s.split(" ", 1)[1] if " " in s else ""
        caps |= set(re.findall(r"\b[A-Z][a-z]{2,}\b", body))
    mcaps = {w for w in re.findall(r"\b[A-Z][a-z]{2,}\b", mapped)}
    if caps - mcaps:
        probs.append("adds a name the source does not give: " + ", ".join(sorted(caps - mcaps)))
    return probs, needs


def verify_grounding(state: dict, plan: dict, text: str, src: str) -> bool:
    try:
        obj, _ = call(state, plan, [
        {"role": "system", "content": (
            "You check whether a simplified sentence preserves the meaning of the source "
            "sentence without adding a fact, name, number, question, or opinion. Return JSON "
            "{\"grounded\": true|false, \"reason\": \"...\"}.")},
        {"role": "user", "content": f"SOURCE: {src}\nSIMPLIFIED: {text}"},
    ], temperature=0.0, max_tokens=600)
        return bool(obj.get("grounded"))
    except Exception:
        return False


def pack_parts(out_sents: list[str]) -> dict | None:
    total = sum(MP.words(s) for s in out_sents)
    if total < 300 or total > 450:
        return None
    best, best_cost = None, None
    for i in range(len(out_sents) - 2):
        for j in range(i + 1, len(out_sents) - 1):
            parts = {"part_1": " ".join(out_sents[:i + 1]),
                     "part_2": " ".join(out_sents[i + 1:j + 1]),
                     "part_3": " ".join(out_sents[j + 1:])}
            ws = [MP.words(v) for v in parts.values()]
            if any(not BAND["words_low"] <= w <= BAND["words_high"] for w in ws):
                continue
            cost = abs(ws[0] - total / 3) + abs(ws[1] - total / 3) + abs(ws[2] - total / 3)
            if best_cost is None or cost < best_cost:
                best, best_cost = parts, cost
    return best


def split_three(sents: list[str]) -> list[list[str]]:
    total = sum(MP.words(s) for s in sents)
    cum, groups, g = 0, [[], [], []], 0
    for s in sents:
        if g < 2 and cum >= total * (g + 1) / 3:
            g += 1
        groups[g].append(s)
        cum += MP.words(s)
    return groups


def adapt_group(state: dict, plan: dict, lesson: dict, group: list[str], part: int) -> tuple[str, dict]:
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(group, 1))
    messages = [
        {"role": "system", "content": ADAPT_SYSTEM},
        {"role": "user", "content": (
            f"Craft focus to preserve: {lesson['craft_focus']}.\n\n"
            f"SOURCE SENTENCES for part {part} (human-written, public domain):\n{numbered}\n\n"
            "Return one line per sentence, in order."
        )},
    ]
    last = []
    for round_no in range(1, 7):
        raw, _ = call(state, plan, messages, temperature=0.3, max_tokens=2600,
                      json_mode=False)
        lines = [ln.strip() for ln in str(raw).splitlines() if re.match(r"^\d+\|", ln.strip())]
        log({"event": "adapt_lines", "lesson": lesson["sequence"], "part": part,
             "round": round_no, "lines": lines})
        problems, out = [], []
        if len(lines) != len(group):
            problems = [f"need one line per source sentence ({len(group)}), got {len(lines)}"]
        else:
            for i, (line, src) in enumerate(zip(lines, group), 1):
                bits = line.split("|", 2)
                try:
                    eid = int(bits[0])
                except ValueError:
                    problems.append(f"line {i}: id must be a number")
                    continue
                if eid != i:
                    problems.append(f"line {i}: id must be {i}")
                    continue
                action = bits[1].strip().lower() if len(bits) > 1 else ""
                if action == "keep":
                    out.append(src)
                elif action == "drop":
                    pass
                elif action == "simplify" and len(bits) == 3:
                    text = re.sub(r"\s+", " ", bits[2]).strip()
                    if not text:
                        problems.append(f"line {i}: simplify needs text")
                    else:
                        probs, needs = check_row(text, src)
                        if needs and not probs and not verify_grounding(state, plan, text, src):
                            probs = ["not a faithful simplification of the source sentence"]
                        problems += [f"line {i}: {p}" for p in probs]
                        out.append(text)
                else:
                    problems.append(f"line {i}: action must be keep, drop, or simplify|text")
        if not problems:
            text = nudge_to_band({"part": " ".join(out)})["part"]
            m = measure({"part": text})["part"]
            if not BAND["words_low"] <= m["words"] <= BAND["words_high"]:
                need = "keep more" if m["words"] < BAND["words_low"] else "drop"
                problems = [f"part {part} is {m['words']} words; {need} sentences to reach 100-150"]
            elif not BAND["fk_low"] <= (m["fk"] or 0) <= BAND["fk_high"]:
                if (m["fk"] or 0) > BAND["fk_high"]:
                    long_words = sorted({w for w in re.findall(r"[A-Za-z]{7,}", text)},
                                        key=len, reverse=True)[:10]
                    problems = [f"part {part} measures FK {m['fk']:.1f}; replace these long words "
                                "with common ones: " + ", ".join(long_words)]
                else:
                    problems = [f"part {part} measures FK {m['fk']:.1f}; use more exact words"]
            else:
                return text, m
        last = problems
        print(f"  part {part} round {round_no}: {len(problems)} flags -> revising")
        messages += [
            {"role": "assistant", "content": "\n".join(lines)},
            {"role": "user", "content": (
                "Revise the lines. Problems:\n- " + "\n- ".join(problems)
                + "\nReturn one line per source sentence, in order: <id>|keep, <id>|drop, or "
                  "<id>|simplify|<text>. Never add a fact, question, name, or number."
            )},
        ]
    die(state, f"lesson {lesson['sequence']} part {part} failed grounded adaptation: {last}")


def adapt(state: dict, plan: dict, lesson: dict) -> tuple[dict, dict]:
    state["phase"] = f"adapt {lesson['sequence']}"
    save_state(state)
    source = re.sub(r"\s+", " ", (BOT / "sources" / lesson["source_file"]).read_text()).strip()
    groups = split_three(_sentences(source))
    parts, metrics = {}, {}
    for n, group in enumerate(groups, 1):
        text, m = adapt_group(state, plan, lesson, group, n)
        parts[f"part_{n}"] = text
        metrics[f"part_{n}"] = m
    return parts, metrics


ITEM_SYSTEM = """You write one scored short_answer item for a grade-4 authors_craft lesson. \
The passage is fixed and must not be rewritten. Every answer must be derivable from the passage \
shown by show_part. Match the writer's choices, not outside knowledge.

Return JSON {"item": {...}} with exactly these fields:
{"id":"1","type":"short_answer","skill":"authors_craft","difficulty":1,
 "show_part":"part_1","show_part_again":false,"prompt":"...",
 "tutor_only":{"confirm":"...","correct_reason":"...","tell":"...",
   "help":["...","..."],"say_back":"own_words","core_idea":"...",
   "accept_ideas":["...","..."],"one_idea_is_enough":true,
   "not_required":["..."],"normalize":"Ignore case, punctuation, and minor spelling. Accept a meaning-preserving paraphrase.",
   "if_they_say":[{"when":"...","ask":"..."}]}}

Rules: the prompt must be a question. Each prompt must be answerable by pointing at one sentence, and correct_reason must name \
that sentence. Each help line points at evidence or narrows, never gives the answer. tell is two \
short sentences, each 20 words or fewer. prompt, confirm, tell, help, and if_they_say.ask are \
student copy: 20 words or fewer per sentence, no praise, no exclamation marks, and never the \
words just, easy, simple, buddy, kiddo, awesome, great job, or proud. accept_ideas holds ideas, \
not instructions. Each if_they_say names one specific misreading."""

MOVES = [
    ("anchor", "part_1", 1,
     "a stated fact from part_1 that later items depend on"),
    ("join", "part_1", 2,
     "connect two stated facts from part_1 or part_2"),
    ("interpret", "part_2", 2,
     "the conclusion the facts support but the passage does not state"),
    ("craft", "part_2", 3,
     "quote the exact word or phrase the author repeats or chooses, and ask what that choice "
     "does for the reader"),
    ("whole", "all", 3,
     "how the author's plan or approach changes from part_1 to part_3; do not reuse the craft "
     "item's quoted choice; set show_part_again true"),
]


def make_items(state: dict, plan: dict, lesson: dict, parts: dict) -> list:
    state["phase"] = f"items {lesson['sequence']}"
    save_state(state)
    passage = "\n\n".join(f"[{k}]\n{v}" for k, v in parts.items())
    required = {"id", "type", "skill", "difficulty", "show_part", "show_part_again", "prompt",
                "tutor_only"}
    tutor = {"confirm", "correct_reason", "tell", "help", "say_back", "core_idea",
             "accept_ideas", "if_they_say"}
    items = []
    for n, (move, show, difficulty, description) in enumerate(MOVES, 1):
        messages = [
            {"role": "system", "content": ITEM_SYSTEM},
            {"role": "user", "content": (
                f"Craft focus: {lesson['craft_focus']}.\n\nPASSAGE:\n{passage}\n\n"
                f"Write item {n} of 5. Move: {description}. Use show_part \"{show}\" and "
                f"difficulty {difficulty}. Set id \"{n}\"."
            )},
        ]
        item = None
        for attempt in range(1, 4):
            try:
                obj, _ = call(state, plan, messages, temperature=0.4, max_tokens=6000)
                item = obj.get("item") if isinstance(obj, dict) else None
            except Exception as exc:  # parse or empty content
                item = None
                problem = str(exc)
            if isinstance(item, dict):
                missing = required - set(item)
                t = item.get("tutor_only") or {}
                tmiss = tutor - set(t)
                if not missing and not tmiss:
                    break
                problem = f"missing fields: {sorted(missing | tmiss)}"
            if attempt < 3:
                messages.append({"role": "user", "content":
                                 f"Return one valid JSON object with every field. {problem}"})
        if not isinstance(item, dict):
            die(state, f"lesson {lesson['sequence']} item {n} unparseable after 3 attempts")
        item["id"] = str(n)
        item["type"] = "short_answer"
        item["skill"] = "authors_craft"
        item["difficulty"] = int(difficulty)
        item["show_part"] = show
        item["show_part_again"] = (show == "all")
        t = item.setdefault("tutor_only", {})
        t["say_back"] = "own_words"
        t.setdefault("one_idea_is_enough", True)
        t.setdefault("not_required", [])
        t.setdefault("accept_ideas", [])
        t["accept_ideas"] = [
            re.sub(r"^(use|write|say|choose|find|look at|read|put|add|mix|take|select)\s+",
                   "", str(x).strip(), flags=re.I) for x in t["accept_ideas"]
        ]
        t.setdefault("if_they_say", [])
        t["help"] = list(t.get("help") or [])[:2] or ["The sentence about this says what happened."]
        items.append(item)
        print(f"  item {n}: {item['prompt'][:70]}")
    return items


def clean_doc(doc: dict) -> dict:
    """Normalize model output into the schema's exact enums and shapes."""
    for key, text in list(doc["passage"].items()):
        text = re.sub(r"!+", ".", text)
        text = re.sub(r"\.\.+", ".", text)
        doc["passage"][key] = re.sub(r"\s+", " ", text).strip()
    for it in doc["items"]:
        it["difficulty"] = int(it.get("difficulty", 1))
        if it.get("show_part") not in ("part_1", "part_2", "part_3", "all"):
            it["show_part"] = "part_1"
        t = it.setdefault("tutor_only", {})
        sb = str(t.get("say_back", "")).strip().lower().replace(" ", "_")
        t["say_back"] = sb if sb in ("own_words", "use_word") else "own_words"
        t.setdefault("one_idea_is_enough", True)
        t.setdefault("not_required", [])
        t.setdefault("accept_ideas", [])
        t["accept_ideas"] = [
            re.sub(r"^(use|write|say|choose|find|look at|read|put|add|mix|take|select)\s+",
                   "", str(x).strip(), flags=re.I) for x in t["accept_ideas"]
        ]
        t.setdefault("if_they_say", [])
        if not isinstance(t.get("help"), list) or not t["help"]:
            t["help"] = ["The sentence about this says what happened.", "Look for the words that carry the idea."]
        t["help"] = t["help"][:2]
    return doc


def assemble(plan: dict, lesson: dict, parts: dict, metrics: dict, items: list) -> dict:
    cell = plan["cell"]
    seq = lesson["sequence"]
    lid = f"{cell['skill']}_band_{cell['grade']}_{cell['stage']}_{seq:04d}"
    nxt = f"{cell['skill']}_band_{cell['grade']}_{cell['stage']}_{seq + 1:04d}"
    if seq == 6:
        nxt = lid
    span = ", ".join(f"{k} {v['words']}w at FK {v['fk']:.1f}" for k, v in metrics.items())
    why = (f"Measured {span}. The load is {lesson['craft_focus']}.")
    doc = {
        "schema_version": 3,
        "document_type": "lesson_source",
        "lesson_id": lid,
        "meta": {
            "status": "published",
            "title": lesson["title"],
            "skill": cell["skill"],
            "irl_grade": cell["grade"],
            "stage": cell["stage"],
            "sequence": seq,
            "genre": "nonfiction",
            "topic_domain": lesson["domain"],
            "skill_frame": f"Author's craft: read how the writer uses {lesson['craft_focus'].split(',')[0]}.",
            "reader": {
                "who": "Older students who read at about a fourth-grade level.",
                "reading_level": cell["grade"],
                "why_this_level": why,
                "tone": "Adult subject. Plain sentences. The lesson must not make the reader feel small.",
            },
            "source": lesson["source"],
            "session": {"scope": "bank", "item_target": 5, "time_target_minutes": 12,
                        "difficulty_basis": lesson["craft_focus"]},
            "authoring_exceptions": [],
        },
        "script_overrides": {"near_copy_2": "Say it in your own words. One sentence is enough."},
        "passage": parts,
        "items": items,
        "advance": {"next_file": f"{cell['skill']}_band_{cell['grade']}_{cell['stage']}_0001",
                    "next_irl": cell["grade"],
                    "next_means": "This band has no higher rung yet.",
                    "student_line": "You have the move. The next reading is another craft lesson."},
        "retry": {"next_file": nxt, "next_irl": cell["grade"],
                  "next_means": "Another lesson in this band.",
                  "student_line": "The next reading is another craft lesson in this band."},
        "stopped": {"next_file": lid, "next_irl": cell["grade"],
                    "next_means": "This same lesson, so it can be finished."},
    }
    return clean_doc(doc)


# ---------------------------------------------------------------- gates
def run(cmd: list, cwd: pathlib.Path, state: dict, label: str) -> subprocess.CompletedProcess:
    print(f"  gate: {label}")
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    log({"event": "gate", "label": label, "returncode": proc.returncode,
         "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]})
    if proc.returncode != 0:
        die(state, f"gate failed: {label}\n{proc.stdout[-3000:]}\n{proc.stderr[-2000:]}")
    return proc


def ensure_curriculum(state: dict) -> None:
    path = LESSONS / "curriculum.json"
    data = json.loads(path.read_text())
    row = {"skill": "authors_craft", "grade": 4, "stage": 1,
           "expected_sequences": [1, 2, 3, 4, 5, 6], "status": "complete"}
    data["sets"] = [s for s in data["sets"]
                    if not (s["skill"] == "authors_craft" and s["grade"] == 4 and s["stage"] == 1)]
    data["sets"].append(row)
    path.write_text(json.dumps(data, indent=2) + "\n")
    log({"event": "curriculum", "action": "added authors_craft 4.1 complete"})


def gate_rung(state: dict, plan: dict, ids: list[str]) -> None:
    state["phase"] = "gates"
    save_state(state)
    ensure_curriculum(state)
    run(["uv", "run", "python", "scripts/build_lessons.py",
         "--source-dir", str(SRC), "--output-dir", str(LESSONS)],
        HARNESS, state, "compile")
    run([sys.executable, str(SKILL / "scripts/validate_lesson.py"), "--strict",
         "--src-dir", str(SRC), "--lessons-dir", str(LESSONS)]
        + [str(SRC / f"{i}.source.json") for i in ids],
        ROOT, state, "strict validate")
    audit = subprocess.run(
        [sys.executable, str(SKILL / "scripts/audit_lessons.py"),
         "--src-dir", str(SRC), "--lessons-dir", str(LESSONS)],
        cwd=ROOT, capture_output=True, text=True)
    rung_hits = [ln for ln in (audit.stdout + audit.stderr).splitlines()
                 if any(i in ln for i in ids)]
    log({"event": "gate", "label": "guideline audit", "returncode": audit.returncode,
         "rung_hits": rung_hits})
    if rung_hits:
        die(state, "guideline audit: findings in this rung\n" + "\n".join(rung_hits))
    print(f"  gate: guideline audit (rung clean; corpus has pre-existing findings)")
    # corpus pass: all sources, non-strict, then hunt our ids and reuse findings
    proc = subprocess.run(
        [sys.executable, str(SKILL / "scripts/validate_lesson.py"),
         "--src-dir", str(SRC), "--lessons-dir", str(LESSONS)]
        + [str(p) for p in sorted(SRC.glob("*.source.json"))],
        cwd=ROOT, capture_output=True, text=True)
    hits = [ln for ln in (proc.stdout + proc.stderr).splitlines()
            if ("source.passage-repeat" in ln or "source.work-cross-cell" in ln)
            and any(i in ln for i in ids)]
    if hits:
        die(state, "corpus pass: duplicate passage or cross-cell work\n" + "\n".join(hits))
    log({"event": "gate", "label": "corpus reuse", "returncode": proc.returncode})
    run(["uv", "run", "python", "scripts/build_lessons.py",
         "--source-dir", str(SRC), "--output-dir", str(LESSONS), "--check"],
        HARNESS, state, "compile check")


def review_sample(state: dict, plan: dict, lessons: list[dict], ids: list[str]) -> dict:
    """A second, fresh-context model reads a random sample against the rules."""
    sample = random.Random(41).sample(lessons, 2)
    verdicts = []
    for lesson in sample:
        lid = f"{plan['cell']['skill']}_band_{plan['cell']['grade']}_{plan['cell']['stage']}_{lesson['sequence']:04d}"
        src = json.loads((SRC / f"{lid}.source.json").read_text())
        source_text = (BOT / "sources" / lesson["source_file"]).read_text()[:5000]
        review_prompt = (
            "You are a strict reviewer of grade-4 reading lessons. Check only these rules and "
            "answer from the file and the source. Return JSON {\"pass\": true|false, "
            "\"problems\": [\"...\"]}.\n"
            "1. Every item is answerable from the passage shown by show_part.\n"
            "2. The answer key scores the minimum the prompt asks, not extra detail.\n"
            "3. Help lines may paraphrase the passage. Flag one only if it points at text "
            "that is absent or states the answer.\n"
            "4. Every if_they_say names a real misreading.\n"
            "5. Student copy has no praise, no exclamation marks, no 'just', 'easy', or 'simple'.\n"
            "6. The passage must not add a fact, name, number, question, or evaluative claim "
            "the source lacks. Common-word synonyms and simpler phrasing are allowed "
            "(quadrupeds -> four-legged animals, suspended -> paused). Omitting detail is "
            "allowed. Flag only a change in meaning or an added claim. show_part 'all' displays "
            "the whole passage, so an item comparing parts is answerable.\n\n"
            f"SOURCE (human-written, public domain):\n{source_text}\n\n"
            f"LESSON FILE:\n{json.dumps(src, indent=1)}"
        )
        obj = {"pass": None, "error": "not run"}
        for attempt in range(2):
            try:
                obj, _ = call(state, plan, [{"role": "user", "content": review_prompt}],
                              temperature=0.2, max_tokens=4000,
                              model=plan.get("reviewer_model"))
                break
            except Exception as exc:
                obj = {"pass": None, "error": str(exc)}
        verdicts.append({"lesson": lid, "verdict": obj})
        print(f"  review {lid}: {'pass' if obj.get('pass') else 'FAIL'}")
    return {"sampled": [v["lesson"] for v in verdicts], "verdicts": verdicts}


# ---------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["preflight", "run", "status", "gates"])
    ap.add_argument("--only", type=int, default=None, help="author one sequence only (tuning)")
    ap.add_argument("--start", type=int, default=1, help="first sequence to author")
    ap.add_argument("--no-gates", action="store_true", help="skip gates (tuning only)")
    args = ap.parse_args(argv)
    plan = json.loads((BOT / "plan.json").read_text())
    state = load_state()

    if args.command == "status":
        print(json.dumps(state, indent=2))
        return 0
    if args.command == "preflight":
        preflight(plan, state)
        return 0
    if args.command == "gates":
        preflight(plan, state)
        all_ids = [f"{plan['cell']['skill']}_band_{plan['cell']['grade']}_{plan['cell']['stage']}_{l['sequence']:04d}"
                   for l in plan["lessons"]]
        for lid in all_ids:
            path = SRC / f"{lid}.source.json"
            if path.exists():
                path.write_text(json.dumps(clean_doc(json.loads(path.read_text())), indent=2, ensure_ascii=False) + "\n")
        gate_rung(state, plan, all_ids)
        review = review_sample(state, plan, plan["lessons"], all_ids)
        state["review"] = review
        state["status"] = "passed" if all(v["verdict"].get("pass") for v in review["verdicts"]) else "review-failed"
        save_state(state)
        print(f"\n{state['status']}: spend ${state['spend_usd']:.4f}")
        return 0 if state["status"] == "passed" else 3

    preflight(plan, state)
    state.update(status="running", phase="adapt", failures=[])
    save_state(state)
    lessons, ids = [], []
    selected = [l for l in plan["lessons"] if (args.only is None and l["sequence"] >= args.start) or l["sequence"] == args.only]
    for lesson in selected:
        print(f"lesson {lesson['sequence']}: {lesson['title']} [{lesson['domain']}]")
        parts, metrics = adapt(state, plan, lesson)
        items = make_items(state, plan, lesson, parts)
        doc = assemble(plan, lesson, parts, metrics, items)
        path = SRC / f"{doc['lesson_id']}.source.json"
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        lessons.append(lesson)
        ids.append(doc["lesson_id"])
        state["lessons"][doc["lesson_id"]] = {
            "words": {k: v["words"] for k, v in metrics.items()},
            "fk": {k: v["fk"] for k, v in metrics.items()},
            "status": "written",
        }
        save_state(state)
        log({"event": "lesson", "id": doc["lesson_id"], "spend": state["spend_usd"]})
    if args.no_gates:
        print(f"\ntuning run: {len(ids)} lesson(s), spend ${state['spend_usd']:.4f}")
        return 0
    all_ids = [f"{plan['cell']['skill']}_band_{plan['cell']['grade']}_{plan['cell']['stage']}_{l['sequence']:04d}"
               for l in plan["lessons"]]
    missing = [i for i in all_ids if not (SRC / f"{i}.source.json").exists()]
    if missing:
        die(state, f"gates need all six sources; missing {missing}")
    ids = all_ids
    gate_rung(state, plan, ids)
    review = review_sample(state, plan, lessons, ids)
    state["review"] = review
    state["phase"] = "done"
    state["status"] = "passed" if all(v["verdict"].get("pass") for v in review["verdicts"]) else "review-failed"
    save_state(state)
    print(f"\n{state['status']}: {len(ids)} lessons, spend ${state['spend_usd']:.4f}")
    if state["status"] != "passed":
        print(json.dumps(review, indent=2), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
