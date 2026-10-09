#!/usr/bin/env python3
"""Flag model-routed descriptions that read alike.

Collects the frontmatter `description` plus `when_to_use` of every
plugins/*/skills/*/SKILL.md and plugins/*/agents/*.md, then ranks pairs by
TF-IDF cosine similarity. Two near-identical descriptions make routing a coin
flip, so a pair above the fail line exits 1 unless it is listed in `allowed_pairs`.

Only the routing surface the model actually sees is compared:

- Skills with `disable-model-invocation: true` are excluded: their description is
  never preloaded (.claude/rules/authoring-skills.md, user-invoked entry points).
- A skill and an agent in the same plugin are never compared: an agent is chosen
  at delegation time, not by the Skill router.
- Pairs whose plugins sit in one `exclusive_groups` entry are never installed
  together (.claude/rules/stack-plugin-conventions.md: one runtime target and one
  cloud provider per repository), so both thresholds rise by `exclusive_bonus`.

`allowed_pairs` entries have the shape {"a": "<id>", "b": "<id>", "reason": "..."}.
An id is `tsh-<plugin>:<skill>` for a skill or `tsh-<plugin>:@<agent>` for an agent;
the order of a and b does not matter. An entry naming an id that no longer exists
is an error, so renames cannot leave stale entries behind. An allowed pair never
fails the run: at or below the fail line it is shown as `allowed` and emits no
annotation; above the fail line it is reported as WARN.

Standard library only. A component whose frontmatter cannot be parsed is reported
and fails the run: a skipped component is a missed collision.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path(__file__).resolve().parent / "description-lint.json"

STOP_WORDS = frozenset(
    """a an and are as at be by can for from has have how if in into is it its of on
    or that the their this to use used using when whenever with without you your not
    any all also than then them they these those which who will would should may
    must per via each every other more most such only own same so too very just""".split()
)
TOKEN = re.compile(r"[a-z][a-z0-9-]+")


class ParseError(Exception):
    pass


def parse_frontmatter(path):
    """Return ({key: scalar}, line of `description:`); raise ParseError on unsupported shapes."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ParseError("no frontmatter opening '---'")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ParseError("no frontmatter closing '---'")
    block = lines[1:end]
    data = {}
    desc_line = 1
    for i, line in enumerate(block):
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            continue
        key, raw = match.group(1), match.group(2).strip()
        if key in ("description", "when_to_use") and raw[:1] not in ("|", ">"):
            nxt = next((ln for ln in block[i + 1:] if ln.strip()), None)
            if nxt is not None and not re.match(r"^[A-Za-z_][\w-]*:", nxt):
                raise ParseError(f"multi-line value for '{key}'")
        if key == "description":
            desc_line = i + 2
        data[key] = parse_scalar(key, raw)
    return data, desc_line


def parse_scalar(key, raw):
    if raw[:1] in ("|", ">"):
        raise ParseError(f"block scalar for '{key}'")
    if raw[:1] == '"':
        if len(raw) < 2 or raw[-1] != '"':
            raise ParseError(f"unterminated double-quoted value for '{key}'")
        try:
            return json.loads(raw)
        except ValueError:
            return raw[1:-1].replace('\\"', '"')
    if raw[:1] == "'":
        if len(raw) < 2 or raw[-1] != "'":
            raise ParseError(f"unterminated single-quoted value for '{key}'")
        return raw[1:-1].replace("''", "'")
    return re.sub(r"\s+#.*$", "", raw)


def collect(root=ROOT):
    """Return (components, errors). A component is a dict with id, plugin, kind, path, text."""
    components, errors = [], []
    patterns = [("skill", "plugins/*/skills/*/SKILL.md"), ("agent", "plugins/*/agents/*.md")]
    for kind, pattern in patterns:
        for path in sorted(root.glob(pattern)):
            rel = path.relative_to(root).as_posix()
            plugin = path.relative_to(root / "plugins").parts[0]
            try:
                fm, desc_line = parse_frontmatter(path)
            except ParseError as exc:
                errors.append((rel, str(exc)))
                continue
            if kind == "skill" and fm.get("disable-model-invocation", "").lower() == "true":
                continue
            name = fm.get("name") or (path.parent.name if kind == "skill" else path.stem)
            text = f"{fm.get('description', '')} {fm.get('when_to_use', '')}".strip()
            if not text:
                errors.append((rel, "no description or when_to_use"))
                continue
            ident = f"{plugin}:{'@' if kind == 'agent' else ''}{name}"
            components.append(
                {"id": ident, "plugin": plugin, "kind": kind, "path": rel, "line": desc_line, "text": text}
            )
    return components, errors


def tokenize(text):
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP_WORDS]


def vectors(components):
    docs = [Counter(tokenize(c["text"])) for c in components]
    n = len(docs)
    df = Counter(term for doc in docs for term in doc)
    result = []
    for doc in docs:
        vec = {t: tf * math.log(n / df[t]) for t, tf in doc.items()}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        result.append({t: v / norm for t, v in vec.items()} if norm else {})
    return result


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(t, 0.0) for t, v in a.items())


def exclusive(plugin_a, plugin_b, groups):
    return plugin_a != plugin_b and any(
        plugin_a in g["plugins"] and plugin_b in g["plugins"] for g in groups
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this repository)")
    ap.add_argument("--warn-above", type=float)
    ap.add_argument("--fail-above", type=float)
    ap.add_argument("--top", type=int, default=10, help="rows to print (default 10)")
    ap.add_argument("--github", action="store_true", help="emit GitHub annotations")
    args = ap.parse_args(argv)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    warn = args.warn_above if args.warn_above is not None else config["warn_above"]
    fail = args.fail_above if args.fail_above is not None else config["fail_above"]
    bonus = config.get("exclusive_bonus", 0.0)
    groups = config.get("exclusive_groups", [])
    allowed = {frozenset((p["a"], p["b"])) for p in config.get("allowed_pairs", [])}

    components, errors = collect(args.root)
    for rel, msg in errors:
        print(f"ERROR {rel}: cannot parse frontmatter ({msg})", file=sys.stderr)
        if args.github:
            print(f"::error file={rel}::cannot parse frontmatter ({msg})")

    ids = {c["id"] for c in components}
    for p in config.get("allowed_pairs", []):
        for side in (p["a"], p["b"]):
            if side not in ids:
                msg = f"allowed_pairs entry {p['a']} / {p['b']}: unknown component {side}"
                print(f"ERROR {msg}", file=sys.stderr)
                if args.github:
                    print(f"::error file=scripts/description-lint.json::{msg}")
                errors.append((str(args.config), msg))

    vecs = vectors(components)
    rows = []
    for i, j in combinations(range(len(components)), 2):
        a, b = components[i], components[j]
        if a["plugin"] == b["plugin"] and a["kind"] != b["kind"]:
            continue
        extra = bonus if exclusive(a["plugin"], b["plugin"], groups) else 0.0
        score = cosine(vecs[i], vecs[j])
        pair_allowed = frozenset((a["id"], b["id"])) in allowed
        if score > fail + extra and not pair_allowed:
            level = "FAIL"
        elif score > fail + extra:
            level = "WARN"
        elif score > warn + extra:
            level = "allowed" if pair_allowed else "WARN"
        else:
            level = "ok"
        rows.append((score, level, extra, pair_allowed, a, b))
    rows.sort(key=lambda r: -r[0])

    print(f"{len(components)} components; warn > {warn:.2f}, fail > {fail:.2f} "
          f"(+{bonus:.2f} for mutually exclusive plugins)")
    print(f"{'score':>5}  {'level':<7}  pair")
    for score, level, extra, pair_allowed, a, b in rows[: args.top]:
        note = " [exclusive]" if extra else ""
        note += " [allowed]" if pair_allowed else ""
        print(f"{score:5.2f}  {level:<7}  {a['id']} / {b['id']}{note}")

    failed = bool(errors)
    for score, level, _, _, a, b in rows:
        if level in ("ok", "allowed"):
            continue
        if level == "FAIL":
            failed = True
        if args.github:
            kind = "error" if level == "FAIL" else "warning"
            hint = ('add a "X is <other skill>" disambiguation to the description or '
                    "when_to_use, or add an allowed_pairs entry with a reason")
            for side in (a, b):
                print(f"::{kind} file={side['path']},line={side['line']},"
                      f"title=Description similarity {score:.2f}::"
                      f"{a['id']} vs {b['id']} - {hint}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if args.github and summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("### Description similarity\n\n| score | level | pair |\n| --: | :-- | :-- |\n")
            for score, level, extra, pair_allowed, a, b in rows:
                if level != "ok":
                    note = " (exclusive)" if extra else ""
                    fh.write(f"| {score:.2f} | {level} | `{a['id']}` / `{b['id']}`{note} |\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
