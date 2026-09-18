#!/usr/bin/env python3
"""Scaffold a project catalog with its project-context repository.

Creates, under --parent (default: the current directory):

    <slug>/                      the project catalog
    <slug>/CLAUDE.md             pointer loaded in every session below
    <slug>/<slug>-context/       knowledge base + Claude Code marketplace

from the templates in ../templates. Every template path and file body has
{{PROJECT_NAME}}, {{PROJECT_SLUG}}, {{OWNER}}, {{OWNER_NAME}}, {{OWNER_EMAIL}}
and {{DATE}} substituted; the `__SLUG__` token in a path becomes the slug and
the `.tmpl` suffix is stripped.

Workspaces always created: the five project workspaces (baseline, architecture,
product, delivery, quality) and the three layer workspaces every project has
(backend, frontend, design). Anything in --layers is added from
../templates/layers and gets its row in the area map.

The script never overwrites: an existing file is left alone and reported, so a
second run converges to "nothing to do". It never runs git.

Usage:
    python3 scaffold.py --name "Acme Portal" --owner-name "Jane Doe" \
        --owner-email jane.doe@example.com [--slug acme] [--parent /path] \
        [--layers mobile platform] [--dry-run]
    python3 scaffold.py --name "Acme Portal" --owner-tbd    # owner assigned later

Prints a report: created / skipped (already existed), then CONTEXT_DIR and SLUG.
Exit 0 on success, 2 on bad arguments.
"""

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
CATALOG_TEMPLATES = TEMPLATES / "catalog"
LAYER_TEMPLATES = TEMPLATES / "layers"
EXECUTABLE_SUFFIXES = {".py", ".sh"}

# Optional layer workspaces, with the row each adds to the area map.
OPTIONAL_LAYERS = {
    "mobile": "Mobile applications: platform targets, release and store process, "
              "device constraints, offline behaviour.",
    "platform": "Infrastructure and delivery pipelines: environments, provisioning, "
                "CI/CD, observability, secrets, cost.",
}


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-")


def render(text, vars_):
    for key, value in vars_.items():
        if value == "":
            # Drop the whole line for an empty block placeholder, so no blank line
            # is left inside a markdown table.
            text = text.replace("{{" + key + "}}\n", "")
        text = text.replace("{{" + key + "}}", value)
    return text


def write(src, dest, vars_, dry_run, created, skipped, rel):
    if dest.exists():
        skipped.append(rel)
        return
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(src.read_text(encoding="utf-8"), vars_), encoding="utf-8")
        if dest.suffix in EXECUTABLE_SUFFIXES:
            dest.chmod(dest.stat().st_mode | 0o111)
    created.append(rel)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="human project name, e.g. 'Acme Portal'")
    ap.add_argument("--slug", help="kebab-case identifier; derived from --name if omitted")
    ap.add_argument("--owner-name", help="repository owner's full name")
    ap.add_argument("--owner-email", help="repository owner's e-mail")
    ap.add_argument("--owner-tbd", action="store_true",
                    help="no owner yet: every owner field reads 'TBD — assign an owner'")
    ap.add_argument("--layers", nargs="*", default=[],
                    choices=sorted(OPTIONAL_LAYERS), metavar="LAYER",
                    help="optional layer workspaces to add: " + ", ".join(sorted(OPTIONAL_LAYERS)))
    ap.add_argument("--parent", default=os.getcwd(),
                    help="where to create the catalog (default: cwd)")
    ap.add_argument("--date", default=dt.date.today().isoformat(),
                    help="ISO date stamped into generated files")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be created, write nothing")
    args = ap.parse_args()

    slug = args.slug or slugify(args.name)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        print(f"error: slug '{slug}' is not kebab-case", file=sys.stderr)
        return 2
    if not CATALOG_TEMPLATES.is_dir():
        print(f"error: templates not found at {CATALOG_TEMPLATES}", file=sys.stderr)
        return 2

    if args.owner_tbd:
        owner_name, owner_email, owner = "TBD", "", "TBD — assign an owner"
    elif args.owner_name and args.owner_email:
        owner_name, owner_email = args.owner_name.strip(), args.owner_email.strip()
        owner = f"{owner_name} ({owner_email})"
    else:
        print("error: give --owner-name and --owner-email, or --owner-tbd", file=sys.stderr)
        return 2

    layers = sorted(set(args.layers))
    rows = "\n".join(
        f"| [{layer.capitalize()}]({layer}/README.md) | {OPTIONAL_LAYERS[layer]} | {owner_name} |"
        for layer in layers)

    vars_ = {
        "PROJECT_NAME": args.name.strip(),
        "PROJECT_SLUG": slug,
        "OWNER_NAME": owner_name,
        "OWNER_EMAIL": owner_email,
        "OWNER": owner,
        "DATE": args.date,
        "OPTIONAL_LAYER_ROWS": rows,
    }
    catalog = Path(args.parent).resolve() / slug
    context = catalog / f"{slug}-context"

    created, skipped = [], []
    for src in sorted(CATALOG_TEMPLATES.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(CATALOG_TEMPLATES).as_posix().replace("__SLUG__", slug)
        if rel.endswith(".tmpl"):
            rel = rel[: -len(".tmpl")]
        write(src, catalog / rel, vars_, args.dry_run, created, skipped, rel)

    for layer in layers:
        layer_dir = LAYER_TEMPLATES / layer
        if not layer_dir.is_dir():
            print(f"  ! no template for layer '{layer}'; skipped")
            continue
        for src in sorted(layer_dir.rglob("*")):
            if not src.is_file():
                continue
            name = src.relative_to(layer_dir).as_posix()
            if name.endswith(".tmpl"):
                name = name[: -len(".tmpl")]
            rel = f"{slug}-context/docs/{layer}/{name}"
            write(src, catalog / rel, vars_, args.dry_run, created, skipped, rel)

    verb = "Would create" if args.dry_run else "Created"
    print(f"Catalog: {catalog}")
    if layers:
        print(f"Optional layers: {', '.join(layers)}")
    print(f"\n{verb} ({len(created)}):")
    for rel in created:
        print(f"  + {rel}")
    if skipped:
        print(f"\nSkipped, already existed ({len(skipped)}):")
        for rel in skipped:
            print(f"  = {rel}")
    print(f"\nCONTEXT_DIR={context}")
    print(f"SLUG={slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
