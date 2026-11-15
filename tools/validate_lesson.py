#!/usr/bin/env python3
"""Validate readJson schema-v3 lesson sources.

Checks the normative rules in readJson/README.md, readJson/DESIGN_RULES.md, and
readingHarness/server/lessons.py. It validates the *source*, not the generated runtime
file. Run the compiler's `--check` mode as the second gate.

When given more than one source, it also runs a corpus-wide sourcing check against DESIGN_RULES
2.2: no displayed passage repeats, and a work never serves two (category, grade, stage) cells.
Several works in one cell is legitimate and only reported as a note. The check needs every source;
validating one file at a time cannot see reuse. It reads `meta.source.attribution` and the URL in
`meta.source.basis`, so give external works their exact URL.

Exit codes: 0 = no errors (warnings allowed), 1 = errors, 2 = bad usage.

Usage:
    validate_lesson.py lessons/src/inference_band_5_1_0002.source.json
    validate_lesson.py --draft --src-dir lessons/src file.source.json
    validate_lesson.py --strict --src-dir lessons/src --lessons-dir lessons lessons/src/*.source.json
    validate_lesson.py --json lessons/src/*.source.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CATEGORIES = {
    "vocab",
    "main_idea",
    "inference",
    "process",
    "text_structure",
    "literary_text",
    "authors_craft",
    "argument_evidence",
}
GRADES = range(1, 13)
STAGES = range(1, 9)
NAME_RE = re.compile(
    r"^(?P<cat>[a-z][a-z0-9_-]*)_band_(?P<grade>\d{1,2})_(?P<stage>[1-8])_"
    r"(?P<seq>\d{4})\.source\.json$"
)
ID_RE = re.compile(
    r"^(?P<cat>[a-z][a-z0-9_-]*)_band_(?P<grade>\d{1,2})_(?P<stage>[1-8])_"
    r"(?P<seq>\d{4})$"
)
ITEM_TYPES = {"short_answer", "cloze", "multiple_choice", "rubric"}
SAY_BACK = {"own_words", "use_word"}
ALLOWED_TOP = {
    "schema_version",
    "document_type",
    "lesson_id",
    "meta",
    "passage",
    "items",
    "script_overrides",
    "instruction_additions",
    "advance",
    "retry",
    "stopped",
}
FORBIDDEN_TOP = {"script", "tutoring_instructions", "rules", "tokens"}
ALLOWED_OVERRIDES = {"near_copy_2"}
STATUSES = {"draft", "reviewed", "published"}

BANNED_WORDS = [
    "easy", "easily", "simple", "simply", "buddy", "kiddo",
    "awesome", "proud", "great job", "good job", "nice work", "superstar",
    "you got this", "champ", "sport",
]
BANNED_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b", re.I)

# DESIGN_RULES 3.1.7: a scored key states a claim about what the wording does. A key that
# asserts what the reader feels, sees, pictures, or imagines cannot be graded, because the
# next reader's image is different and honest. The prompt may quote the passage's own
# "picture" (a passage can invite one); it may not ask the student for their sensation.
SENSATION_PROMPT_RE = re.compile(
    r"\bwhat (?:does|do) (?:this|that|these|those|it|the \w+)\b[^.?!]*\bmake (?:you|the reader) "
    r"(?:feel|see|picture|imagine)|\bwhat do you (?:feel|picture)\b|\bhelp you (?:feel|picture)\b",
    re.I,
)
SENSATION_KEY_RE = re.compile(
    r"\bthe reader (?:feels?|sees?|pictures?|imagines?)\b|"
    r"\bmakes? (?:you|the reader) (?:feel|see|picture|imagine)\b",
    re.I,
)
JUST_RE = re.compile(r"\bjust\b", re.I)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z0-9'’\-]+")


class Report:
    def __init__(self, path: Path):
        self.path = path
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.notes: list[tuple[str, str]] = []

    def err(self, code: str, msg: str) -> None:
        self.errors.append((code, msg))

    def warn(self, code: str, msg: str) -> None:
        self.warnings.append((code, msg))

    def note(self, code: str, msg: str) -> None:
        self.notes.append((code, msg))

    @property
    def ok(self) -> bool:
        return not self.errors


def words(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def get(d, *keys, default=None):
    for key in keys:
        if not isinstance(d, dict) or key not in d:
            return default
        d = d[key]
    return d


def student_copy_strings(data: dict):
    skill_frame = get(data, "meta", "skill_frame")
    if isinstance(skill_frame, str):
        yield "meta.skill_frame", skill_frame
    for key, value in (data.get("script_overrides") or {}).items():
        if isinstance(value, str):
            yield f"script_overrides.{key}", value
    for idx, item in enumerate(data.get("items") or [], 1):
        if not isinstance(item, dict):
            continue
        iid = item.get("id", f"item{idx}")
        if isinstance(item.get("prompt"), str):
            yield f"{iid}.prompt", item["prompt"]
        tutor = item.get("tutor_only") or {}
        for key in ("confirm", "tell"):
            if isinstance(tutor.get(key), str):
                yield f"{iid}.{key}", tutor[key]
        for j, help_line in enumerate(tutor.get("help") or []):
            if isinstance(help_line, str):
                yield f"{iid}.help[{j}]", help_line
        for branch in (tutor.get("if_they_say") or []) + (tutor.get("partial") or []):
            if isinstance(branch, dict) and isinstance(branch.get("ask"), str):
                yield f"{iid}.ask", branch["ask"]


def lint_copy(rep: Report, data: dict) -> None:
    for label, text in student_copy_strings(data):
        flat = " ".join(text.split())
        if "!" in flat:
            rep.warn("copy.exclamation", f"{label}: exclamation point in student copy")
        match = BANNED_RE.search(flat)
        if match:
            rep.warn("copy.banned-word", f"{label}: condescending word {match.group(0)!r}")
        if JUST_RE.search(flat):
            rep.note("copy.style-word", f"{label}: uses 'just' (allowed only in its temporal sense)")
        long_sentences = []
        for sentence in SENTENCE_SPLIT.split(flat):
            n = words(sentence)
            if n > 15:
                long_sentences.append((n, sentence[:90]))
        if long_sentences:
            n, sentence = max(long_sentences)
            more = f" (+{len(long_sentences) - 1} more)" if len(long_sentences) > 1 else ""
            # 4.2 says "aim for 15 words or fewer", so 16-20 is a note, not a bar to publish.
            # Past 20 the sentence is doing two jobs and is worth splitting before shipping.
            emit = rep.warn if n > 20 else rep.note
            emit("copy.long-sentence", f"{label}: {n}-word sentence{more}: {sentence!r}")


def lint_passage(rep: Report, passage: object, exceptions: list | None = None) -> dict:
    exceptions = exceptions or []
    documented = any(
        isinstance(line, str) and re.search(r"word|length|short passage", line, re.I)
        for line in exceptions
    )
    if not isinstance(passage, dict) or not passage:
        rep.err("passage.missing", "passage must be a non-empty object")
        return {}
    for key, text in passage.items():
        if not isinstance(text, str) or not text.strip():
            rep.err("passage.type", f"passage.{key} must be a non-empty string")
            continue
        n = words(text)
        if n > 200:
            # 2.1 asks for 100-200; only length beyond the ceiling is a publish bar.
            msg = f"passage.{key}: {n} words (target 100-200)"
            if documented:
                rep.note("passage.length", msg + " [documented exception]")
            else:
                rep.warn("passage.length", msg)
        elif n < 100:
            # 2.1 calls a shorter passage acceptable, and band 3-4 lessons run 55-95 words.
            msg = f"passage.{key}: {n} words (target 100-200)"
            rep.note("passage.length", msg + (" [documented exception]" if documented else ""))
        if "!" in text:
            rep.warn("passage.exclamation", f"passage.{key}: exclamation point")
    if len(passage) < 2:
        rep.warn("passage.parts", f"{len(passage)} passage part(s); DESIGN_RULES 2.1 asks for 3-4")
    return passage


# Key-scope checks (DESIGN_RULES 3.1.8-3.1.10). Heuristic review prompts, not verdicts: by default
# they are notes, so the existing corpus can be triaged without breaking the strict gate; with
# --key-scope they become warnings (required for new lessons).
KEY_SCOPE_AS_WARNING = False
YESNO_RE = re.compile(
    r"^(?:is|are|was|were|does|do|did|can|could|would|will|should|has|have|had)\b", re.I
)
REASON_ASK_RE = re.compile(
    r"\b(?:why|how do you know|what in the passage|which (?:words|sentence|fact)|explain|what shows|tells you)\b",
    re.I,
)
JOINED_KEY_RE = re.compile(r";|,\s*(?:and|so)\b|\bbecause\b|\bso that\b|\s(?:and then|and so)\s", re.I)
QUANTITY_RE = re.compile(r"\b(one|two|three|four|both|each|all|list|name|every|any one)\b", re.I)
STOP = set(
    "about above after again against their there these those which while would could should where "
    "other being every never still under until within without what when whom whose this that with "
    "from have they them then than into only some such very more most much many make made does because".split()
)


def content_words(text: str) -> set[str]:
    return {w.lower().strip("'’-") for w in WORD_RE.findall(text or "") if len(w) >= 5 and w.lower() not in STOP}


def stem_hit(word: str, bag: set[str]) -> bool:
    root = word[:5]
    return any(b.startswith(root) for b in bag)


def scope(rep: Report, code: str, msg: str) -> None:
    (rep.warn if KEY_SCOPE_AS_WARNING else rep.note)(code, msg)


def check_key_scope(rep: Report, item: dict, iid: str, prompt: str, tutor: dict, passage: dict, branches: list) -> None:
    last_q = [s for s in SENTENCE_SPLIT.split(prompt.strip()) if s.strip()]
    last_q = last_q[-1] if last_q else ""
    if YESNO_RE.match(last_q) and not REASON_ASK_RE.search(prompt):
        scope(rep, "item.yes-no", f"{iid}: yes/no prompt with no request for the reason (3.1.8): {last_q[:70]!r}")
    core = str(tutor.get("core_idea") or "")
    if tutor.get("one_idea_is_enough") is True and JOINED_KEY_RE.search(core):
        # the contradiction is a compound core whose accept list also credits only one side; a
        # compound core with a two-sided accept is coherent (the relation is the one idea)
        head, tail = core, ""
        m = JOINED_KEY_RE.search(core)
        if m:
            head, tail = core[: m.start()], core[m.end() :]
        hb, tb = content_words(head), content_words(tail)
        two_sided = any(
            isinstance(i, str) and content_words(i) & hb and content_words(i) & tb
            for i in tutor.get("accept_ideas") or []
        )
        if not two_sided and hb and tb:
            rep.note(
                "item.joined-key",
                f"{iid}: core_idea joins two ideas and no accept credits both, but one_idea_is_enough is true; trim the key or set it false (3.1.9): {core[:80]!r}",
            )
    shown = passage.get(item.get("show_part")) if item.get("show_part") not in (None, "all") else None
    full = " ".join(v for v in passage.values() if isinstance(v, str))
    full_bag = content_words(full + " " + prompt)
    for detail in tutor.get("not_required") or []:
        words_ = content_words(detail)
        if words_ and not any(stem_hit(w, full_bag) for w in words_):
            scope(rep, "item.not-required-filler", f"{iid}: not_required detail is not in the passage: {detail[:60]!r} (3.1.9)")
    if isinstance(shown, str):
        shown_bag = content_words(shown + " " + prompt)
        key_words = content_words(core)
        missing = [w for w in key_words if not stem_hit(w, shown_bag) and stem_hit(w, full_bag)]
        if key_words and len(missing) >= 2 and len(missing) / len(key_words) >= 0.4:
            scope(
                rep,
                "item.key-off-screen",
                f"{iid}: core_idea leans on words from a part not displayed ({', '.join(sorted(missing)[:4])}); check show_part (2.3)",
            )
    if (item.get("difficulty") or 0) >= 4 and len(branches) < 2:
        # a note, not a gate: one named misreading is enough to score the item, and a second one only
        # sharpens the tell. Requiring two on every item would be 200+ authoring passes for little gain.
        rep.note("item.branches", f"{iid}: difficulty {item.get('difficulty')} item has {len(branches)} misreading branch; a second near-miss would sharpen the tell (3.1.10)")
    # 3.1.11: a key that credits any one of several different answers needs a prompt that says "one"
    accepts = [i for i in tutor.get("accept_ideas") or [] if isinstance(i, str)]
    if tutor.get("one_idea_is_enough") is True and len(accepts) >= 4:
        bags = [content_words(a) for a in accepts]
        disjoint = sum(
            1
            for x in range(len(bags))
            for y in range(x + 1, len(bags))
            if bags[x] and bags[y] and not (bags[x] & bags[y])
        )
        pairs = len(bags) * (len(bags) - 1) / 2
        if pairs and disjoint == pairs and not QUANTITY_RE.search(prompt) and not re.search(r"\bwhy\b", prompt, re.I):
            # a note only: a word-overlap test cannot tell a paraphrase set from a set of different
            # answers, so this flags a prompt to re-read, never a failure
            rep.note(
                "item.quantity",
                f"{iid}: accept list credits several different answers but the prompt does not say how many (3.1.11): {prompt[:70]!r}",
            )


def check_item(
    rep: Report, item: object, idx: int, passage: dict, exceptions: list | None = None
) -> None:
    where = f"items[{idx}]"
    if not isinstance(item, dict):
        rep.err("item.type", f"{where} is not an object")
        return
    iid = item.get("id")
    if not isinstance(iid, str) or not iid.strip():
        rep.err("item.id", f"{where} has no string id")
        iid = where

    typ = item.get("type")
    if typ not in ITEM_TYPES:
        rep.err("item.type", f"{iid}: unsupported type {typ!r} (allowed: {sorted(ITEM_TYPES)})")

    show_part = item.get("show_part", "<missing>")
    if show_part is None:
        pass
    elif not isinstance(show_part, str):
        rep.err("item.show_part", f"{iid}: show_part must be a string or null")
    elif show_part != "all" and show_part not in passage:
        rep.err("item.show_part", f"{iid}: show_part {show_part!r} is not a passage key or 'all'")
    if item.get("show_part_again") and not show_part:
        rep.err("item.show_part_again", f"{iid}: show_part_again requires a non-null show_part")

    if not isinstance(item.get("skill"), str) or not item["skill"].strip():
        rep.err("item.skill", f"{iid}: missing skill tag")
    if not isinstance(item.get("difficulty"), int):
        rep.err("item.difficulty", f"{iid}: difficulty must be an integer")

    prompt = item.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        rep.err("item.prompt", f"{iid}: missing prompt")
        prompt = ""
    waived = any(
        isinstance(line, str) and "key shape" in line.lower() and str(iid) in line
        for line in (exceptions or [])
    )
    if prompt and SENSATION_PROMPT_RE.search(prompt):
        msg = f"{iid}: prompt asks for a reader's feeling or image; ask what the wording does (3.1.7)"
        rep.note("item.key-shape", msg + " [documented exception]") if waived else rep.warn("item.key-shape", msg)
    unquoted = re.sub(r"[\"'][^\"']*[\"']", "", prompt)
    if unquoted.count("?") > 1:
        msg = f"{iid}: prompt asks more than one question; a scored item has one job (3.1.7)"
        rep.note("item.key-shape", msg + " [documented exception]") if waived else rep.warn("item.key-shape", msg)

    tutor = item.get("tutor_only")
    if not isinstance(tutor, dict):
        rep.err("item.tutor_only", f"{iid}: missing tutor_only block")
        return

    for key in ("confirm", "correct_reason", "tell"):
        if not isinstance(tutor.get(key), str) or not tutor[key].strip():
            rep.err("item.key", f"{iid}: missing tutor_only.{key}")

    for field in ("confirm", "tell", "core_idea"):
        value = tutor.get(field)
        if isinstance(value, str) and SENSATION_KEY_RE.search(value):
            msg = (
                f"{iid}: tutor_only.{field} asserts a reader sensation; state what the words do "
                f"to the meaning instead (3.1.7)"
            )
            rep.note("item.key-shape", msg + " [documented exception]") if waived else rep.warn(
                "item.key-shape", msg
            )

    helps = tutor.get("help")
    if not isinstance(helps, list) or not helps:
        rep.err("item.help", f"{iid}: at least one help line is required")
    elif len(helps) > 2:
        rep.warn("item.help", f"{iid}: {len(helps)} help lines; the ladder is two, then tell")
    if isinstance(helps, list):
        for j, line in enumerate(helps):
            if isinstance(line, str) and tutor.get("tell") and line.strip().lower() == str(tutor["tell"]).strip().lower():
                rep.err("item.help", f"{iid}: help[{j}] is identical to tell")

    say_back = tutor.get("say_back")
    if say_back not in SAY_BACK:
        rep.err("item.say_back", f"{iid}: say_back must be one of {sorted(SAY_BACK)}")
    if say_back == "use_word" and not isinstance(tutor.get("word"), str):
        rep.err("item.word", f"{iid}: say_back use_word requires tutor_only.word")

    branches = (tutor.get("if_they_say") or []) + (tutor.get("partial") or [])
    for branch in branches:
        if not isinstance(branch, dict):
            rep.err("item.branch", f"{iid}: branch is not an object")
            continue
        if not isinstance(branch.get("when"), str) or not isinstance(branch.get("ask"), str):
            rep.err("item.branch", f"{iid}: each branch needs 'when' and 'ask'")
            continue
        if re.search(
            r"\b(?:any (?:wrong|other|answer)|all other|every (?:wrong|other)|otherwise|whatever they say)\b",
            branch["when"],
            re.I,
        ):
            rep.warn("item.branch", f"{iid}: branch looks generic: {branch['when'][:70]!r}")

    if typ == "short_answer":
        core = tutor.get("core_idea")
        if not isinstance(core, str) or not core.strip():
            rep.err("item.core_idea", f"{iid}: short_answer needs tutor_only.core_idea")
        not_required = tutor.get("not_required")
        if not_required is not None:
            if not isinstance(not_required, list) or not all(
                isinstance(x, str) and x.strip() for x in not_required
            ):
                rep.err("item.not_required", f"{iid}: not_required must be non-empty strings")
        ideas = tutor.get("accept_ideas")
        if not isinstance(ideas, list) or not ideas:
            rep.err("item.accept_ideas", f"{iid}: short_answer needs accept_ideas")
        else:
            if not isinstance(tutor.get("one_idea_is_enough"), bool):
                rep.warn("item.one_idea", f"{iid}: set one_idea_is_enough explicitly")
            for idea in ideas:
                if isinstance(idea, str) and re.match(r"^(say|write|use|tell|ask)\b", idea.strip(), re.I):
                    rep.warn("item.accept_ideas", f"{iid}: accept_ideas holds an instruction: {idea[:60]!r}")
        if not branches:
            rep.warn("item.misconception", f"{iid}: no if_they_say/partial branch (DESIGN_RULES 3.1.2)")
        check_key_scope(rep, item, iid, prompt, tutor, passage, branches)

    elif typ == "cloze":
        if "____" not in prompt:
            rep.err("item.cloze", f"{iid}: cloze prompt must contain '____'")
        if not isinstance(tutor.get("accept_words"), list) or not tutor["accept_words"]:
            rep.err("item.cloze", f"{iid}: cloze needs accept_words")
        if not isinstance(tutor.get("normalize"), str) or not tutor["normalize"].strip():
            rep.err("item.cloze", f"{iid}: cloze needs a normalize rule")
        covered = " ".join(b.get("when", "") for b in branches if isinstance(b, dict)).lower()
        for word in tutor.get("reject_words") or []:
            if isinstance(word, str) and word.lower() not in covered:
                rep.err("item.reject_words", f"{iid}: reject word {word!r} has no authored branch")

    elif typ == "multiple_choice":
        if not isinstance(tutor.get("correct_option"), str):
            rep.err("item.mc", f"{iid}: multiple_choice needs correct_option")
        distractors = tutor.get("distractors") or {}
        if not isinstance(distractors, dict) or not distractors:
            rep.err("item.mc", f"{iid}: multiple_choice needs distractors")
        else:
            for letter, distractor in distractors.items():
                if not isinstance(distractor, dict) or not isinstance(distractor.get("misreading"), str):
                    rep.err("item.mc", f"{iid}: distractor {letter} needs a misreading")

    elif typ == "rubric":
        key_points = tutor.get("key_points")
        if not isinstance(key_points, list) or not key_points:
            rep.err("item.rubric", f"{iid}: rubric needs key_points")
        else:
            ids = [p.get("id") for p in key_points if isinstance(p, dict)]
            if any(not isinstance(x, str) for x in ids):
                rep.err("item.rubric", f"{iid}: every key point needs an id")
            min_coverage = tutor.get("min_coverage")
            if not isinstance(min_coverage, int) or not (1 <= min_coverage <= len(key_points)):
                rep.err("item.rubric", f"{iid}: min_coverage must be 1..{len(key_points)}")
            required_order = tutor.get("required_order") or []
            for rid in required_order:
                if rid not in ids:
                    rep.err("item.rubric", f"{iid}: required_order references unknown key point {rid!r}")
            if tutor.get("order_matters") and not required_order:
                rep.err("item.rubric", f"{iid}: order_matters is true but required_order is empty")


def parse_lesson_id(value: str) -> tuple[str, int, int, int] | None:
    match = ID_RE.fullmatch(value)
    if not match:
        return None
    return match["cat"], int(match["grade"]), int(match["stage"]), int(match["seq"])


def check_route(
    rep: Report,
    key: str,
    value: object,
    lesson_id: str,
    grade: int,
    src_dir: Path | None,
    lessons_dir: Path | None,
    allow_dangling: bool = False,
) -> None:
    if not isinstance(value, dict):
        rep.err(f"route.{key}", f"source needs a {key!r} route object")
        return
    next_file = value.get("next_file")
    next_irl = value.get("next_irl")
    next_means = value.get("next_means")
    student_line = value.get("student_line")

    if not isinstance(next_file, str) or not next_file.strip():
        rep.err(f"route.{key}", f"{key}.next_file must be a non-empty lesson id")
        return
    if next_file.endswith(".json") or next_file.endswith(".source"):
        rep.err(f"route.{key}", f"{key}.next_file must omit extensions ({next_file!r})")
        next_file = next_file.replace(".source.json", "").replace(".json", "")
    if not isinstance(next_irl, int) or next_irl < 1:
        rep.err(f"route.{key}", f"{key}.next_irl must be a positive integer")
    if not isinstance(next_means, str) or not next_means.strip():
        rep.err(f"route.{key}", f"{key}.next_means must explain the destination")
    if key == "stopped":
        if student_line is not None and not isinstance(student_line, str):
            rep.err(f"route.{key}", "stopped.student_line must be a string when present")
    elif not isinstance(student_line, str) or not student_line.strip():
        rep.err(f"route.{key}", f"{key} needs a student_line")

    parsed = parse_lesson_id(next_file)
    if parsed is None:
        rep.err(f"route.{key}", f"{key}.next_file {next_file!r} is not a valid lesson id")
        return
    _, dest_grade, _, _ = parsed
    if dest_grade not in GRADES:
        rep.err(f"route.{key}", f"{key}.next_file uses an invalid IRL grade {dest_grade}")
    if isinstance(next_irl, int) and next_irl != dest_grade:
        rep.err(f"route.{key}", f"{key}.next_irl {next_irl} does not match {next_file}")

    if key == "stopped" and next_file != lesson_id:
        rep.err("route.stopped", f"stopped.next_file must be {lesson_id!r}, got {next_file!r}")
    if key == "stopped" and isinstance(next_irl, int) and next_irl != grade:
        rep.err("route.stopped", "stopped.next_irl must equal the lesson grade")

    if next_file == lesson_id and key != "stopped":
        rep.note(f"route.{key}", f"{key} points back to this lesson; confirm that is deliberate")

    if src_dir is not None:
        target = src_dir / f"{next_file}.source.json"
        if not target.exists():
            message = f"{key}.next_file has no source file: {target.name}"
            if allow_dangling:
                rep.warn("route.target", message + " [staging only]")
            else:
                rep.err("route.target", message)
        else:
            try:
                target_data = json.loads(target.read_text(encoding="utf-8"))
                if not target_data.get("items") or not target_data.get("passage"):
                    rep.warn(
                        "route.placeholder",
                        f"{key}.next_file {next_file} is still a placeholder with no items/passage",
                    )
            except (OSError, json.JSONDecodeError):
                rep.warn("route.target", f"cannot inspect route target {target.name}")

    if lessons_dir is not None:
        compiled = lessons_dir / f"{next_file}.json"
        if not compiled.exists():
            message = f"{key}.next_file is not compiled: {compiled.name} (run build_lessons.py)"
            if allow_dangling:
                rep.warn("route.compiled", message + " [staging only]")
            else:
                rep.err("route.compiled", message)


def check_curriculum(
    rep: Report,
    lessons_dir: Path,
    category: str,
    grade: int,
    stage: int,
    sequence: int,
) -> None:
    """The server requires every lesson to belong to a declared curriculum set."""
    path = lessons_dir / "curriculum.json"
    if not path.is_file():
        rep.err("curriculum.missing", f"{path} is required by the server")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        rep.err("curriculum.invalid", f"{path.name} is not valid JSON")
        return
    rows = [row for row in data.get("sets", []) if isinstance(row, dict)]
    row = next(
        (
            item
            for item in rows
            if item.get("skill") == category
            and item.get("grade") == grade
            and item.get("stage") == stage
        ),
        None,
    )
    if row is None:
        rep.err(
            "curriculum.set",
            f"no curriculum set for {category} Band {grade}.{stage}; add a row in "
            f"{path.name}",
        )
        return
    expected = row.get("expected_sequences")
    if not isinstance(expected, list) or sequence not in expected:
        rep.err(
            "curriculum.sequence",
            f"sequence {sequence} is not in expected_sequences {expected!r}",
        )
    status = row.get("status")
    if status not in {"complete", "incomplete"}:
        rep.err("curriculum.status", f"set status must be complete or incomplete, got {status!r}")
    elif status == "complete":
        missing = [
            value
            for value in expected or []
            if not (lessons_dir / f"{category}_band_{grade}_{stage}_{value:04d}.json").exists()
        ]
        if missing:
            rep.err(
                "curriculum.complete",
                f"set is marked complete but missing sequences {missing}",
            )


# --- Corpus-wide sourcing check (DESIGN_RULES 2.2) -------------------------
#
# 2.2 requires one work per (category, grade, stage) cell, a different work for the next cell, and
# no displayed passage repeated in two lessons. Nothing per-file can see that, so this pass needs
# every source at once. It is a gate, not a proof of uniqueness: it cannot detect a republished copy
# under a new URL, and it cannot detect paraphrase (2.5 forbids paraphrase as a drafting move).

SHINGLE_N = 8
RUN_ERROR_WORDS = 12
RUN_NOTE_WORDS = 8
OVERLAP_ERROR_RATIO = 0.10
URL_RE = re.compile(r"https?://[^\s)\]}>\"']+", re.I)
TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


def normalize_url(url: str) -> str:
    cleaned = re.sub(r"^https?://", "", url.lower())
    cleaned = re.sub(r"^www\.", "", cleaned)
    cleaned = cleaned.split("#")[0].split("?")[0].rstrip("/")
    return cleaned


def work_key(data: dict) -> str | None:
    """Identity of the source work, or None when the passage is original to the lesson.

    A URL is preferred because it is the only field that reliably distinguishes two articles from
    the same publisher. Attribution is the fallback. Original writing written for the lesson has no
    shared work, so it is excluded from the one-work-per-cell comparison.
    """
    source = get(data, "meta", "source")
    if not isinstance(source, dict):
        return None
    blob = " ".join(str(source.get(key) or "") for key in ("attribution", "basis", "survey"))
    match = URL_RE.search(blob)
    if match:
        return "url:" + normalize_url(match.group(0))
    attribution = str(source.get("attribution") or "").strip()
    if attribution:
        normalized = re.sub(r"[^a-z0-9]+", " ", attribution.lower()).strip()
        return "attribution:" + normalized if normalized else None
    return None


def load_source_entry(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    stem = path.name[: -len(".source.json")] if path.name.endswith(".source.json") else path.stem
    match = ID_RE.fullmatch(stem)
    if not match:
        return None
    passage = data.get("passage") if isinstance(data.get("passage"), dict) else {}
    text = " ".join(str(part) for _, part in sorted(passage.items()))
    return {
        "id": stem,
        "cell": (match["cat"], int(match["grade"]), int(match["stage"])),
        "work": work_key(data),
        "tokens": [token.lower() for token in TOKEN_RE.findall(text)],
    }


def shingle_index(tokens: list[str]) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for pos in range(max(0, len(tokens) - SHINGLE_N + 1)):
        index.setdefault(" ".join(tokens[pos : pos + SHINGLE_N]), []).append(pos)
    return index


def longest_run(left: list[str], right: list[str], left_index, right_index) -> tuple[int, str]:
    """Longest verbatim run between two passages, in words, with its text."""
    best, phrase, budget = 0, "", 0
    for shingle in left_index.keys() & right_index.keys():
        for pa in left_index[shingle][:3]:
            for pb in right_index[shingle][:3]:
                end = SHINGLE_N
                while pa + end < len(left) and pb + end < len(right) and left[pa + end] == right[pb + end]:
                    end += 1
                if end > best:
                    best, phrase = end, " ".join(left[pa : pa + end])
                budget += 1
                if budget > 4000:
                    return best, phrase
    return best, phrase


def check_reuse(files: list[Path], allow_draft: bool, strict: bool = False) -> Report:
    rep = Report(Path("<corpus>"))
    severity = rep.warn if allow_draft else rep.err
    entries = [entry for entry in (load_source_entry(f) for f in files) if entry]

    by_work: dict[str, dict[tuple[str, int, int], list[str]]] = {}
    by_cell: dict[tuple[str, int, int], dict[str, list[str]]] = {}
    for entry in entries:
        if not entry["work"]:
            continue
        by_work.setdefault(entry["work"], {}).setdefault(entry["cell"], []).append(entry["id"])
        by_cell.setdefault(entry["cell"], {}).setdefault(entry["work"], []).append(entry["id"])

    for work, cells in sorted(by_work.items()):
        if len(cells) > 1:
            where = ", ".join(
                f"{cat} {grade}.{stage} ({', '.join(ids)})"
                for (cat, grade, stage), ids in sorted(cells.items())
            )
            severity(
                "source.work-cross-cell",
                f"one work serves {len(cells)} cells: {where}. A work serves one cell; the next band "
                f"gets fresh material. Work: {work}",
            )

    # More than one work in a cell is allowed: milking a good work is a convenience, not a duty.
    # Report it so the author can see the shape of the cell, never as a failure.
    for (cat, grade, stage), works in sorted(by_cell.items()):
        if len(works) > 1:
            listed = ", ".join(f"{work} ({', '.join(ids)})" for work, ids in sorted(works.items()))
            rep.note(
                "source.cell-works",
                f"{cat} Band {grade}.{stage} draws on {len(works)} works: {listed}",
            )

    indexes = [shingle_index(entry["tokens"]) for entry in entries]
    for i, left in enumerate(entries):
        for j in range(i + 1, len(entries)):
            right = entries[j]
            shared = indexes[i].keys() & indexes[j].keys()
            if not shared:
                continue
            run, phrase = longest_run(left["tokens"], right["tokens"], indexes[i], indexes[j])
            smaller = max(1, min(len(indexes[i]), len(indexes[j])))
            ratio = len(shared) / smaller
            message = (
                f"{left['id']} and {right['id']} share a {run}-word passage run "
                f"({len(shared)} matching {SHINGLE_N}-word window(s), {ratio:.0%} of the shorter "
                f"passage): {phrase[:90]!r}"
            )
            if run >= RUN_ERROR_WORDS or (len(shared) >= 4 and ratio >= OVERLAP_ERROR_RATIO):
                severity("source.passage-repeat", message)
            elif run >= RUN_NOTE_WORDS:
                rep.note("source.passage-overlap", message + " [short overlap; check by hand]")

    if len(entries) < 2:
        rep.note("source.reuse-skipped", "fewer than two parseable sources; nothing to compare")

    if strict:
        for code, msg in rep.warnings:
            rep.err(code, msg)
        rep.warnings = []
    return rep


def validate(
    path: Path,
    src_dir: Path | None,
    lessons_dir: Path | None,
    allow_draft: bool,
    strict: bool,
    allow_dangling: bool = False,
) -> Report:
    rep = Report(path)
    if not path.exists():
        rep.err("file", "file does not exist")
        return rep
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        rep.err("json", f"invalid JSON: {exc}")
        return rep
    if not isinstance(data, dict):
        rep.err("json", "top level must be an object")
        return rep

    match = NAME_RE.match(path.name)
    if not match:
        rep.err(
            "name",
            f"{path.name} does not match <category>_band_<grade>_<stage>_<sequence>.source.json",
        )
        return rep
    category = match["cat"]
    grade, stage, sequence = int(match["grade"]), int(match["stage"]), int(match["seq"])
    lesson_id = path.name[: -len(".source.json")]

    if category not in CATEGORIES:
        rep.err("name.category", f"unknown category {category!r}; use one of {sorted(CATEGORIES)}")
    if grade not in GRADES:
        rep.err("name.grade", f"grade {grade} must be 1-12 (whole-number Star IRL)")
    if stage not in STAGES:
        rep.err("name.stage", f"stage {stage} must be 1-8")
    if not 1 <= sequence <= 8:
        rep.err("name.sequence", f"sequence {sequence} must be 0001-0008")

    for key in sorted(set(data) & FORBIDDEN_TOP):
        rep.err(
            "source.shared-key",
            f"{key!r} belongs in readingHarness/server/config/protocol.json, not in a lesson source",
        )
    for key in sorted(set(data) - ALLOWED_TOP):
        rep.warn("source.unknown-key", f"unknown top-level key {key!r}; the compiler ignores it")

    if data.get("schema_version") != 3:
        rep.err("schema_version", f"schema_version must be 3, got {data.get('schema_version')!r}")
    if data.get("document_type") != "lesson_source":
        rep.err("document_type", "document_type must be 'lesson_source'")
    if data.get("lesson_id") != lesson_id:
        rep.err("lesson_id", f"lesson_id {data.get('lesson_id')!r} != filename id {lesson_id!r}")

    meta = data.get("meta")
    if not isinstance(meta, dict):
        rep.err("meta.missing", "missing meta object")
        meta = {}
    status = meta.get("status")
    if status is None:
        rep.err("meta.status", "meta.status is required")
    elif status not in STATUSES:
        rep.err("meta.status", f"unknown status {status!r}; use one of {sorted(STATUSES)}")
    elif status == "draft" and not allow_draft:
        rep.err("meta.status", "draft sources must not be published (server rejects the catalog)")
    if meta.get("skill") != category:
        rep.err("meta.skill", f"meta.skill {meta.get('skill')!r} != filename category {category!r}")
    if meta.get("irl_grade") != grade:
        rep.err("meta.irl_grade", f"meta.irl_grade {meta.get('irl_grade')!r} != filename grade {grade}")
    if meta.get("stage") != stage:
        rep.err("meta.stage", f"meta.stage {meta.get('stage')!r} != filename stage {stage}")
    if meta.get("sequence") != sequence:
        rep.err("meta.sequence", f"meta.sequence {meta.get('sequence')!r} != filename sequence {sequence}")

    reader = meta.get("reader")
    if not isinstance(reader, dict) or not reader:
        rep.err("reader.missing", "meta.reader is required")
    else:
        reading_level = reader.get("reading_level")
        if not isinstance(reading_level, int) or not 1 <= reading_level <= 13:
            rep.err(
                "reader.level",
                f"reader.reading_level must equal the filename grade ({grade})",
            )
        elif reading_level != grade:
            rep.err(
                "reader.level",
                f"reader.reading_level {reading_level} != filename grade {grade}",
            )
        why = reader.get("why_this_level")
        if not isinstance(why, str) or len(why) < 40:
            rep.err("reader.why", "reader.why_this_level must justify readability and cognitive load")
        elif not re.search(r"load|step|entit|clue|track|memory|schema|gate|place|times", why, re.I):
            rep.warn("reader.why", "why_this_level does not describe the cognitive load")
        if not isinstance(reader.get("tone"), str):
            rep.warn("reader.tone", "reader.tone is missing")

    source = meta.get("source")
    if not isinstance(source, dict) or not source.get("text_status"):
        rep.warn("source.missing", "meta.source.text_status is not recorded")

    overrides = data.get("script_overrides")
    if overrides is not None:
        if not isinstance(overrides, dict):
            rep.err("script_overrides", "script_overrides must be an object")
        else:
            for key, value in overrides.items():
                if key not in ALLOWED_OVERRIDES:
                    rep.err(
                        "script_overrides",
                        f"{key!r} is shared protocol copy; only {sorted(ALLOWED_OVERRIDES)} may be overridden",
                    )
                if not isinstance(value, str) or not value.strip():
                    rep.err("script_overrides", f"{key!r} must be a non-empty string")

    additions = data.get("instruction_additions")
    if additions is not None:
        if not isinstance(additions, list) or not all(isinstance(x, str) and x for x in additions):
            rep.err("instruction_additions", "instruction_additions must be non-empty strings")

    passage = lint_passage(rep, data.get("passage"), meta.get("authoring_exceptions") or [])

    items = data.get("items")
    if not isinstance(items, list) or not items:
        rep.err("items.missing", "items must be a non-empty list")
        items = []
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if len(ids) != len(items):
        rep.err("items.ids", "every item must be an object with an id")
    if len(ids) != len(set(ids)):
        rep.err("items.ids", f"duplicate item ids: {ids}")
    if items and len(items) < 3:
        rep.warn("items.count", f"{len(items)} items; a lesson needs at least 3 to be a lesson")
    if len(items) > 15:
        rep.warn("items.count", f"{len(items)} items exceeds the bank target of 10-15")
    skills = {item.get("skill") for item in items if isinstance(item, dict)} - {None}
    if len(skills) > 2:
        rep.warn("items.skills", f"{len(skills)} skill tags; target one primary plus at most one secondary")
    for idx, item in enumerate(items):
        check_item(rep, item, idx, passage, meta.get("authoring_exceptions") or [])

    for key in ("advance", "retry", "stopped"):
        check_route(
            rep, key, data.get(key), lesson_id, grade, src_dir, lessons_dir, allow_dangling
        )
    if lessons_dir is not None:
        check_curriculum(rep, lessons_dir, category, grade, stage, sequence)

    lint_copy(rep, data)

    placeholders = raw.count("TODO")
    if placeholders:
        if allow_draft:
            rep.note("authoring.placeholder", f"{placeholders} TODO placeholder(s) left (ok in a draft)")
        else:
            rep.err("authoring.placeholder", f"{placeholders} TODO placeholder(s) left; not publishable")

    if strict:
        for code, msg in rep.warnings:
            rep.err(code, msg)
        rep.warnings = []

    return rep


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--src-dir", type=Path, default=None, help="source directory for route targets")
    parser.add_argument("--lessons-dir", type=Path, default=None, help="compiled output directory for route targets")
    parser.add_argument("--draft", action="store_true", help="allow meta.status == draft (staging only)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument(
        "--allow-dangling",
        action="store_true",
        help="staging only: downgrade missing route targets to warnings",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--key-scope",
        action="store_true",
        help="promote key-scope notes (DESIGN_RULES 3.1.8-3.1.10) to warnings; required for new lessons",
    )
    args = parser.parse_args(argv)
    global KEY_SCOPE_AS_WARNING
    KEY_SCOPE_AS_WARNING = args.key_scope

    reports = []
    for file in args.files:
        reports.append(
            validate(
                file,
                args.src_dir or file.parent,
                args.lessons_dir,
                args.draft,
                args.strict,
                args.allow_dangling,
            )
        )

    # DESIGN_RULES 2.2 is a property of the corpus, not of one file.
    if len(args.files) > 1:
        reports.append(check_reuse(args.files, args.draft, args.strict))

    if args.json:
        print(json.dumps([
            {
                "file": str(r.path),
                "ok": r.ok,
                "errors": [{"code": c, "message": m} for c, m in r.errors],
                "warnings": [{"code": c, "message": m} for c, m in r.warnings],
                "notes": [{"code": c, "message": m} for c, m in r.notes],
            }
            for r in reports
        ], indent=2))
    else:
        for report in reports:
            print(
                f"\n{report.path.name}: {'PASS' if report.ok else 'FAIL'} "
                f"({len(report.errors)} errors, {len(report.warnings)} warnings)"
            )
            for code, message in report.errors:
                print(f"  ERROR {code}: {message}")
            for code, message in report.warnings:
                print(f"  warn  {code}: {message}")
            for code, message in report.notes:
                print(f"  note  {code}: {message}")
        total_e = sum(len(r.errors) for r in reports)
        total_w = sum(len(r.warnings) for r in reports)
        print(f"\n{len(reports)} file(s): {total_e} error(s), {total_w} warning(s)")

    return 0 if all(r.ok for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
