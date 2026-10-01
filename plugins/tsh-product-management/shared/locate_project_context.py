#!/usr/bin/env python3
"""Find the project-context repository a session belongs to.

A context repository is any folder holding both `docs/README.md` (the area map)
and `conventions/ownership.md`. From the start directory (default: cwd) upward,
each ancestor D is checked as D itself, then as D/*-context. The first ancestor
that yields a match wins, so the search works from the context repository, from
any folder inside it, from the project catalog, and from anywhere inside a code
repository that sits beside the context repository.

Prints on success (exit 0):

    KB=/abs/path/to/<slug>-context
    SLUG=<slug>

Exit 1 when nothing matches. Exit 2 when one ancestor yields several context
repositories; the candidates are printed and the caller asks which one.
Never writes anything.
"""

import json
import sys
from pathlib import Path


def is_context_repo(path):
    return (path / "docs" / "README.md").is_file() and (path / "conventions" / "ownership.md").is_file()


def slug_of(kb):
    manifest = kb / ".claude-plugin" / "marketplace.json"
    try:
        name = json.loads(manifest.read_text(encoding="utf-8")).get("name", "")
    except (OSError, ValueError):
        name = ""
    name = name or kb.name
    return name[: -len("-context")] if name.endswith("-context") else name


def main():
    start = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    for d in (start, *start.parents):
        if is_context_repo(d):
            hits = [d]
        else:
            hits = sorted(p for p in d.glob("*-context") if p.is_dir() and is_context_repo(p))
        if len(hits) == 1:
            print(f"KB={hits[0]}")
            print(f"SLUG={slug_of(hits[0])}")
            return 0
        if len(hits) > 1:
            print(f"Several context repositories under {d}:", file=sys.stderr)
            for h in hits:
                print(f"  {h}", file=sys.stderr)
            return 2
    print(f"No context repository found from {start} upward.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
