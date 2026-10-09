#!/usr/bin/env python3
"""Check routing eval cases for mistakes that would let them pass while proving nothing.

A `tool_used` grader with `max: 0` passes whenever its pattern matches nothing, so a
misspelled or renamed skill turns a must-not-fire assertion green forever. This
check reads every evals/routing/<case>/case.yaml and fails when:

- a grader names a skill that none of the case's plugins ships, or one with
  `disable-model-invocation: true`, which the model can never load;
- `name` differs from the directory name, or a plugin path does not resolve;
- the case breaks the routing shape in .claude/rules/plugin-evals.md: `runs: 1`,
  `max_turns: 1`, `allowed_tools: [Skill]`, no `scaffold_script`, `tool_used`
  graders on Skill only, and at least one must-not-fire grader;
- a case is tagged neither `routing` nor `known-failure`, or both;
- a `known-failure` case is missing from the Known failures table in
  evals/README.md, or that table lists a case that is not quarantined.

`--coverage` also lists model-invocable skills that no case asserts must fire.

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
SKILL_IN_PATTERN = re.compile(r"([a-z0-9][a-z0-9-]*)\"\s*$")
STATUS_TAGS = ("routing", "known-failure")


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
    if data.get("runs") != 1:
        err("runs must be 1; measure a suspect case with --runs 6 instead", "runs")
    if "scaffold_script" in data:
        err("routing cases must not declare scaffold_script", "scaffold_script")

    execution = data.get("execution")
    if not isinstance(execution, dict):
        err("execution must be a mapping", "execution")
        execution = {}
    if not str(execution.get("prompt", "")).strip():
        err("execution.prompt is empty", "execution")
    if execution.get("max_turns") != 1:
        err("execution.max_turns must be 1: only the first Skill call is a routing decision",
            "execution.max_turns")
    if execution.get("allowed_tools") != ["Skill"]:
        err("execution.allowed_tools must be [Skill]: a pull request supplies the case, so it may grant nothing more",
            "execution.allowed_tools")
    if "scaffold_script" in execution:
        err("routing cases must not declare scaffold_script", "execution.scaffold_script")

    skills = {}
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        err("plugins must be a non-empty list", "plugins")
        plugins = []
    for entry in plugins:
        plugin_dir = (case_dir / str(entry)).resolve()
        if not (plugin_dir / ".claude-plugin" / "plugin.json").exists():
            err(f"plugin path '{entry}' does not resolve to a plugin", "plugins")
            continue
        for skill_md in sorted(plugin_dir.glob("skills/*/SKILL.md")):
            skills.setdefault(skill_md.parent.name, []).append((plugin_dir.name, skill_md))

    graders = data.get("graders")
    if not isinstance(graders, list) or not graders:
        err("graders must be a non-empty list", "graders")
        graders = []
    negatives = 0
    for n, grader in enumerate(graders):
        key = f"graders.{n}"
        label = grader.get("name", f"#{n + 1}")
        if grader.get("type") != "tool_used" or grader.get("tool") != "Skill":
            err(f"grader '{label}' must be type tool_used on tool Skill", f"{key}.type")
            continue
        found = SKILL_IN_PATTERN.search(str(grader.get("input_match", "")))
        if not found:
            err(f"grader '{label}': cannot read a skill name from input_match; end the pattern "
                "with the skill name and its closing quote, as in .claude/rules/plugin-evals.md",
                f"{key}.input_match")
            continue
        skill = found.group(1)
        owners = skills.get(skill, [])
        if not owners:
            err(f"grader '{label}' names skill '{skill}', which none of the case's plugins ships",
                f"{key}.input_match")
            continue
        if any(frontmatter_flag(md, "disable-model-invocation") == "true" for _, md in owners):
            err(f"grader '{label}' names '{skill}', which has disable-model-invocation: true "
                "and can never be routed to", f"{key}.input_match")
        negative = grader.get("max") == 0
        negatives += negative
        if not negative:
            must_fire.update(f"{plugin}:{skill}" for plugin, _ in owners)
    if graders and not negatives:
        err("no must-not-fire grader (max: 0): assert that the nearest sibling did not fire",
            "graders")
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
    ap.add_argument("--coverage", action="store_true",
                    help="list model-invocable skills no case asserts must fire")
    ap.add_argument("--github", action="store_true", help="emit GitHub annotations")
    args = ap.parse_args(argv)
    root = args.root

    case_dirs = sorted(p for p in (root / "evals" / "routing").glob("*") if p.is_dir())
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

    for rel, line, msg in errors:
        print(f"ERROR {rel}:{line}: {msg}", file=sys.stderr)
        if args.github:
            print(f"::error file={rel},line={line}::{msg}")

    invocable = model_invocable_skills(root)
    uncovered = sorted(invocable - covered)
    print(f"{len(case_dirs)} routing cases, {len(quarantined)} quarantined; "
          f"{len(invocable) - len(uncovered)} of {len(invocable)} model-invocable skills "
          f"have a passing must-fire case")
    if args.coverage:
        for ident in uncovered:
            print(f"  no must-fire case: {ident}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
