#!/usr/bin/env python3
r"""Check routing eval cases for mistakes that would let them pass while proving nothing.

A `tool_used` grader with `max: 0` passes whenever its pattern matches nothing, so a
misspelled or renamed skill turns a must-not-fire assertion green forever. This check
reads every case.yaml under evals/ — the tree `claude plugin eval --eval-dir evals`
runs — and fails when:

- a grader's pattern is not the idiom in .claude/rules/plugin-evals.md: every `|`
  alternative must anchor on `"skill"` or `"subagent_type"` with an optional
  `(?:[\w-]+:)?` prefix, so a hard-coded prefix, a typo'd branch, or a bare name that
  the session init line always satisfies is caught rather than read for its last name;
- a grader names a skill that none of the case's plugins ships, or one with
  `disable-model-invocation: true`, which the model can never load;
- a `tool_used` grader sets `min: 0` without `max: 0` (asserts nothing), or a grader
  that is not a mapping, or a non-integer `min`/`max`;
- `name` differs from the directory name, or a plugin path does not resolve under
  plugins/;
- the case breaks the routing shape in .claude/rules/plugin-evals.md: `runs: 1`,
  `max_turns: 1` (the integer, not `true`), `allowed_tools: [Skill]`, no
  `scaffold_script`, graders that are either `tool_used` on Skill or `regex` over the
  trace naming a skill or agent, and at least one must-not-fire grader;
- a case is tagged neither `routing` nor `known-failure`, or both;
- a `known-failure` case is missing from the Known failures table in
  evals/README.md, or that table lists a case that is not quarantined;
- a model-invocable skill has no must-fire assertion in a non-quarantined case and is
  not listed in scripts/eval-coverage-baseline.json, or the baseline lists a skill that
  now has one or no longer exists. Only a grader naming one skill alone credits
  coverage. The baseline only shrinks, and `--base-baseline` fails any entry the base
  branch's baseline lacks.

`--coverage` also lists every model-invocable skill without a must-fire case.

Standard library only. case.yaml is read with a parser for the subset the cases
use — scalars, flow lists, `|` block scalars, one level of mapping or list of
mappings — and anything else is reported as an error rather than guessed at.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")
NAME_RX = r"([a-z0-9][a-z0-9-]*)"
STATUS_TAGS = ("routing", "known-failure")


def _idiom(template, key_rx=None):
    """Compile a fullmatch regex from a literal template with {name} and optional {key} markers.

    The template is the exact text a grader must contain, so every regex metacharacter in it is
    escaped and only {name} and {key} become capture groups. A grader that deviates from the
    idiom — a hard-coded plugin prefix, a bare alternative, a typo in one branch — then fails to
    match and is reported, instead of being read for its final name alone.
    """
    out = []
    for tok in re.split(r"(\{name\}|\{key\})", template):
        if tok == "{name}":
            out.append(NAME_RX)
        elif tok == "{key}":
            out.append(f"({key_rx})")
        else:
            out.append(re.escape(tok))
    return re.compile("".join(out))


# A tool_used input_match names one skill: "skill":"<optional plugin prefix><name>".
INPUT_MATCH_IDIOM = _idiom('"skill"\\s*:\\s*"(?:[\\w-]+:)?{name}"')
# A trace alternative anchors on "skill" or "subagent_type", each quote optionally backslash-escaped.
TRACE_IDIOM = _idiom('(?:\\\\?"{key}\\\\?"\\s*:\\s*\\\\?"(?:[\\w-]+:)?{name}\\\\?")',
                     key_rx="skill|subagent_type")


def _is_one(value):
    """True only for the integer 1 — not True, which equals 1 in Python."""
    return value == 1 and not isinstance(value, bool)


def _int_or_absent(value):
    return value is None or (isinstance(value, int) and not isinstance(value, bool))


def top_level_alts(pattern):
    """Split a regex on every | that is not inside (...) or [...], honouring backslash escapes."""
    alts, depth, start, i = [], 0, 0, 0
    while i < len(pattern):
        char = pattern[i]
        if char == "\\":
            i += 2
            continue
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        elif char == "|" and depth == 0:
            alts.append(pattern[start:i])
            start = i + 1
        i += 1
    alts.append(pattern[start:])
    return alts


def read_names(field, raw):
    """The (kind, name) pairs a grader asserts, or None if any alternative breaks the idiom.

    field is 'input_match' (a tool_used pattern, one skill per alternative) or 'pattern' (a trace
    regex, a skill or the agent that runs it). Every | alternative must match the idiom, so a
    hard-coded prefix, a typo'd branch, or a bare name that the session init line always satisfies
    is rejected rather than silently skipped.
    """
    names = []
    for alt in top_level_alts(raw.strip()):
        alt = alt.strip()
        if not alt:
            # An empty alternative — a leading, trailing or doubled | — matches anything, so the
            # grader asserts nothing; reject the whole pattern rather than skip the empty branch.
            return None
        if field == "input_match":
            match = INPUT_MATCH_IDIOM.fullmatch(alt)
            if not match:
                return None
            names.append(("skill", match.group(1)))
        else:
            match = TRACE_IDIOM.fullmatch(alt)
            if not match:
                return None
            key, name = match.group(1), match.group(2)
            names.append(("subagent_type" if key == "subagent_type" else "skill", name))
    return names


class ParseError(Exception):
    pass


def parse_scalar(raw):
    raw = raw.strip()
    if raw[:1] == '"':
        if len(raw) < 2 or raw[-1] != '"':
            raise ParseError(f"unterminated double-quoted value: {raw}")
        return json.loads(raw)
    if raw[:1] == "'":
        if len(raw) < 2 or raw[-1] != "'":
            raise ParseError(f"unterminated single-quoted value: {raw}")
        return raw[1:-1].replace("''", "'")
    if raw[:1] == "[":
        if raw[-1:] != "]":
            raise ParseError(f"unterminated flow list: {raw}")
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items = re.findall(r'"(?:[^"\\]|\\.)*"|\'(?:[^\']|\'\')*\'|[^,]+', inner)
        return [parse_scalar(item) for item in items if item.strip()]
    if raw[:1] in ("{", "&", "*", "!"):
        raise ParseError(f"unsupported YAML construct: {raw}")
    raw = re.sub(r"\s+#.*$", "", raw)
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return {"true": True, "false": False}.get(raw, raw)


def parse_case(text):
    """Return (data, lines): the parsed mapping and {dotted key: 1-based line}."""
    rows = text.splitlines()
    data, lines = {}, {}
    i = 0

    def block(start, parent_indent):
        out, j = [], start
        while j < len(rows) and (not rows[j].strip() or indent_of(rows[j]) > parent_indent):
            out.append(rows[j])
            j += 1
        body = out
        while body and not body[-1].strip():
            body.pop()
        cut = min((indent_of(r) for r in body if r.strip()), default=0)
        return "\n".join(r[cut:] for r in body) + "\n", j

    def value(raw, at, parent_indent):
        if raw in ("|", "|-", ">", ">-"):
            return block(at + 1, parent_indent)
        return parse_scalar(raw), at + 1

    while i < len(rows):
        row = rows[i]
        if not row.strip() or row.lstrip().startswith("#"):
            i += 1
            continue
        if indent_of(row) != 0:
            raise ParseError(f"line {i + 1}: unexpected indentation")
        match = KEY.match(row)
        if not match:
            raise ParseError(f"line {i + 1}: expected 'key: value'")
        key, raw = match.group(1), (match.group(2) or "").strip()
        lines[key] = i + 1
        if raw:
            data[key], i = value(raw, i, 0)
            continue
        i += 1
        container = None
        while i < len(rows) and (not rows[i].strip() or indent_of(rows[i]) > 0):
            row = rows[i]
            if not row.strip() or row.lstrip().startswith("#"):
                i += 1
                continue
            ind, body = indent_of(row), row.strip()
            if body.startswith("- "):
                if container is None:
                    container = []
                if not isinstance(container, list):
                    raise ParseError(f"line {i + 1}: list item inside a mapping")
                container.append({})
                body, ind = body[2:], ind + 2
            elif container is None:
                container = {}
            target = container[-1] if isinstance(container, list) else container
            match = KEY.match(body)
            if not match:
                raise ParseError(f"line {i + 1}: expected 'key: value'")
            sub, raw = match.group(1), (match.group(2) or "").strip()
            if not raw:
                raise ParseError(f"line {i + 1}: nesting deeper than one level under '{key}'")
            index = f"{len(container) - 1}." if isinstance(container, list) else ""
            lines[f"{key}.{index}{sub}"] = i + 1
            target[sub], i = value(raw, i, ind)
        data[key] = container
    return data, lines


def indent_of(row):
    return len(row) - len(row.lstrip(" "))


def frontmatter_flag(path, key):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return None
    flag = re.search(rf"^{re.escape(key)}:\s*(\S+)", match.group(1), re.M)
    return flag.group(1).strip("\"'").lower() if flag else None


def known_failure_rows(readme):
    """Case names in the first column of the Known failures table."""
    if not readme.exists():
        return set()
    section = re.split(r"^## Known failures\s*$", readme.read_text(encoding="utf-8"), flags=re.M)
    if len(section) < 2:
        return set()
    body = re.split(r"^## ", section[1], flags=re.M)[0]
    return set(re.findall(r"^\|\s*`([^`]+)`\s*\|", body, re.M))


def check_case(case_dir, root):
    """Return (errors, must_fire, tags).

    errors is [(rel path, line, message)]; must_fire is {plugin:skill} the case asserts fired.
    """
    path = case_dir / "case.yaml"
    rel = path.relative_to(root).as_posix()
    errors, must_fire = [], set()

    def err(msg, key=None):
        errors.append((rel, lines.get(key, 1) if key else 1, msg))

    lines = {}
    if not path.exists():
        return [(case_dir.relative_to(root).as_posix(), 1, "directory has no case.yaml")], must_fire, []
    try:
        data, lines = parse_case(path.read_text(encoding="utf-8"))
    except (ParseError, ValueError) as exc:
        return [(rel, 1, f"cannot parse: {exc}")], must_fire, []

    if data.get("name") != case_dir.name:
        err(f"name '{data.get('name')}' does not match directory '{case_dir.name}'", "name")
    tags = data.get("tags") or []
    if not isinstance(tags, list) or sum(t in STATUS_TAGS for t in tags) != 1:
        err("tags must include exactly one of 'routing' or 'known-failure'", "tags")
        tags = tags if isinstance(tags, list) else []
    if not _is_one(data.get("runs")):
        err("runs must be 1; measure a suspect case with --runs 6 instead", "runs")
    if "scaffold_script" in data:
        err("routing cases must not declare scaffold_script", "scaffold_script")

    execution = data.get("execution")
    if not isinstance(execution, dict):
        err("execution must be a mapping", "execution")
        execution = {}
    if not str(execution.get("prompt", "")).strip():
        err("execution.prompt is empty", "execution")
    if not _is_one(execution.get("max_turns")):
        err("execution.max_turns must be 1: only the first Skill call is a routing decision",
            "execution.max_turns")
    if execution.get("allowed_tools") != ["Skill"]:
        err("execution.allowed_tools must be [Skill]: a pull request supplies the case, so it may grant nothing more",
            "execution.allowed_tools")
    if "scaffold_script" in execution:
        err("routing cases must not declare scaffold_script", "execution.scaffold_script")

    skills, agents = {}, set()
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        err("plugins must be a non-empty list", "plugins")
        plugins = []
    plugins_root = (root / "plugins").resolve()
    for entry in plugins:
        plugin_dir = (case_dir / str(entry)).resolve()
        try:
            rel_parts = plugin_dir.relative_to(plugins_root).parts
        except ValueError:
            err(f"plugin path '{entry}' must resolve under plugins/, not elsewhere in the tree",
                "plugins")
            continue
        if len(rel_parts) != 1 or not (plugin_dir / ".claude-plugin" / "plugin.json").exists():
            err(f"plugin path '{entry}' does not resolve to a plugin", "plugins")
            continue
        for skill_md in sorted(plugin_dir.glob("skills/*/SKILL.md")):
            skills.setdefault(skill_md.parent.name, []).append((plugin_dir.name, skill_md))
        for agent_md in sorted(plugin_dir.glob("agents/*.md")):
            agents.add(agent_md.stem)

    graders = data.get("graders")
    if not isinstance(graders, list) or not graders:
        err("graders must be a non-empty list", "graders")
        graders = []
    negatives = 0
    for n, grader in enumerate(graders):
        key = f"graders.{n}"
        if not isinstance(grader, dict):
            err(f"grader #{n + 1} must be a mapping, not {type(grader).__name__}", "graders")
            continue
        label = grader.get("name", f"#{n + 1}")
        if grader.get("type") == "tool_used" and grader.get("tool") == "Skill":
            field = "input_match"
            low, high = grader.get("min"), grader.get("max")
            if not _int_or_absent(low) or not _int_or_absent(high):
                err(f"grader '{label}': min and max must be integers", f"{key}.{field}")
                continue
            negative = high == 0
            if not negative and low == 0:
                err(f"grader '{label}': min: 0 without max: 0 asserts nothing; a must-fire grader "
                    "needs min absent or >= 1", f"{key}.{field}")
                continue
            names = read_names(field, str(grader.get(field, "")))
        elif grader.get("type") == "regex" and grader.get("target") == "trace":
            if grader.get("match", "contains") not in ("contains", "not_contains"):
                err(f"grader '{label}': match must be contains or not_contains", f"{key}.match")
                continue
            field, negative = "pattern", grader.get("match") == "not_contains"
            names = read_names(field, str(grader.get(field, "")))
        else:
            err(f"grader '{label}' must be tool_used on tool Skill, or regex with target: trace",
                f"{key}.type")
            continue
        if names is None:
            err(f"grader '{label}': {field} is not the idiom in .claude/rules/plugin-evals.md; "
                'every alternative must anchor on "skill" or "subagent_type" with an optional '
                "(?:[\\w-]+:)? prefix", f"{key}.{field}")
            continue
        negatives += negative
        # Credit coverage only to a grader that names one skill alone: a "skill or the agent that
        # runs it" grader passes when the agent fires, so the skill's own description never has to win.
        single_skill = len(names) == 1 and names[0][0] == "skill"
        for kind, name in names:
            if kind == "subagent_type":
                if name not in agents:
                    err(f"grader '{label}' names agent '{name}', which none of the case's plugins ships",
                        f"{key}.{field}")
                continue
            owners = skills.get(name, [])
            if not owners:
                err(f"grader '{label}' names skill '{name}', which none of the case's plugins ships",
                    f"{key}.{field}")
                continue
            if any(frontmatter_flag(md, "disable-model-invocation") == "true" for _, md in owners):
                err(f"grader '{label}' names '{name}', which has disable-model-invocation: true "
                    "and can never be routed to", f"{key}.{field}")
            if not negative and single_skill:
                must_fire.update(f"{plugin}:{name}" for plugin, _ in owners)
    if graders and not negatives:
        err("no must-not-fire grader (max: 0 or match: not_contains): assert that the nearest "
            "sibling did not fire", "graders")
    return errors, must_fire, tags


def model_invocable_skills(root):
    result = set()
    for skill_md in sorted(root.glob("plugins/*/skills/*/SKILL.md")):
        if frontmatter_flag(skill_md, "disable-model-invocation") != "true":
            plugin = skill_md.relative_to(root / "plugins").parts[0]
            result.add(f"{plugin}:{skill_md.parent.name}")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this repository)")
    ap.add_argument("--baseline", type=Path,
                    help="skills allowed to lack a case (default: <root>/scripts/eval-coverage-baseline.json)")
    ap.add_argument("--coverage", action="store_true",
                    help="list model-invocable skills no case asserts must fire")
    ap.add_argument("--base-baseline", type=Path,
                    help="the base branch's eval-coverage-baseline.json; fail on any entry it lacks")
    ap.add_argument("--github", action="store_true", help="emit GitHub annotations")
    args = ap.parse_args(argv)
    root = args.root

    # Walk the whole tree the runner does (claude plugin eval --eval-dir evals), not just
    # evals/routing, so a routing case placed elsewhere cannot run in CI unchecked. A routing
    # subdirectory with no case.yaml is still a mistake, so keep checking those too.
    eval_root = root / "evals"
    with_case = {p.parent for p in eval_root.rglob("case.yaml")
                 if "results" not in p.relative_to(eval_root).parts} if eval_root.exists() else set()
    routing_dirs = {p for p in (eval_root / "routing").glob("*") if p.is_dir()}
    case_dirs = sorted(with_case | routing_dirs)
    errors, covered, quarantined = [], set(), set()
    for case_dir in case_dirs:
        case_errors, must_fire, tags = check_case(case_dir, root)
        errors += case_errors
        if "known-failure" in tags:
            quarantined.add(case_dir.name)
        else:
            covered |= must_fire

    listed = known_failure_rows(root / "evals" / "README.md")
    for name in sorted(quarantined - listed):
        errors.append((f"evals/routing/{name}/case.yaml", 1,
                       "tagged known-failure but missing from the Known failures table in evals/README.md"))
    for name in sorted(listed - quarantined):
        errors.append(("evals/README.md", 1,
                       f"Known failures lists '{name}', which is not a known-failure case"))

    invocable = model_invocable_skills(root)
    uncovered = sorted(invocable - covered)
    baseline_path = args.baseline or root / "scripts" / "eval-coverage-baseline.json"
    try:
        baseline_rel = baseline_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        baseline_rel = str(baseline_path)
    baseline = set()
    if baseline_path.exists():
        baseline = set(json.loads(baseline_path.read_text(encoding="utf-8")).get("uncovered", []))
    for ident in uncovered:
        if ident not in baseline:
            plugin, skill = ident.split(":")
            errors.append((f"plugins/{plugin}/skills/{skill}/SKILL.md", 1,
                           f"{ident} has no must-fire routing case; add a must-fire and a "
                           "must-not-fire case (.claude/rules/plugin-evals.md)"))
    for ident in sorted(baseline - set(uncovered)):
        reason = "now has a must-fire case" if ident in invocable else "is not a model-invocable skill"
        errors.append((baseline_rel, 1, f"{ident} {reason}; remove it from the baseline"))

    # The baseline only shrinks (evals/README.md). A PR cannot grandfather a new skill into it:
    # anything the base branch's baseline lacks must earn a routing case instead.
    if args.base_baseline and args.base_baseline.exists():
        base = set(json.loads(args.base_baseline.read_text(encoding="utf-8")).get("uncovered", []))
        for ident in sorted(baseline - base):
            errors.append((baseline_rel, 1, f"{ident} is new in the baseline, which only shrinks "
                           "(.claude/rules/plugin-evals.md); add a routing case rather than listing it"))

    for rel, line, msg in errors:
        print(f"ERROR {rel}:{line}: {msg}", file=sys.stderr)
        if args.github:
            print(f"::error file={rel},line={line}::{msg}")

    print(f"{len(case_dirs)} routing cases, {len(quarantined)} quarantined; "
          f"{len(invocable) - len(uncovered)} of {len(invocable)} model-invocable skills "
          f"have a passing must-fire case")
    if args.coverage:
        for ident in uncovered:
            print(f"  no must-fire case: {ident}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
