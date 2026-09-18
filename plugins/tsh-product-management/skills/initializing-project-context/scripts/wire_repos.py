#!/usr/bin/env python3
"""Make the project's shared plugin live, in the context repository and in the
code repositories of a catalog.

Targets, in this order:

  1. <catalog>/<slug>-context itself — ALWAYS. It is the marketplace root, so
     its own settings use the source path ".". This is what makes the plugin
     usable straight after the scaffold, even in a catalog with no code
     repositories yet, and it travels to anyone who clones the context
     repository.
  2. The catalog folder itself — ALWAYS, with "./<slug>-context". The person who
     ran the setup is standing there, so a session opened in the catalog finds
     the plugin without having to change directory first.
  3. Each directory named with --only (code repositories beside it), whose
     settings use "../<slug>-context".

For every target it merges into <target>/.claude/settings.json:

    extraKnownMarketplaces.<slug>-context = {source: directory, path: <as above>}
    enabledPlugins["<slug>-shared@<slug>-context"] = true

Existing keys are preserved; only these two entries are added or updated. A
settings file that is not valid JSON is left untouched and reported. Nothing is
written with --dry-run. The script never runs git.

With --register (the normal mode) it first runs, inside each target:

    claude plugin marketplace add <abs context dir> --scope project
    claude plugin install <slug>-shared@<slug>-context --scope project

so the plugin is live on this machine at once — no trust dialog, no restart —
and then rewrites the absolute path the CLI stores into the portable relative
one. Teammates reach the same state through the trust dialog on their first
interactive session.

Usage:
    python3 wire_repos.py --catalog /path/to/<slug> --slug <slug> \
        [--only repo-a repo-b] [--register] [--dry-run]

Exit 0 on success, 1 if any target was skipped or a CLI step failed.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def register(target, context_dir, plugin_id):
    """Register the marketplace and install the plugin at project scope, from inside target."""
    if not shutil.which("claude"):
        return "claude CLI not on PATH"
    for cmd in (["claude", "plugin", "marketplace", "add", str(context_dir), "--scope", "project"],
                ["claude", "plugin", "install", plugin_id, "--scope", "project"]):
        try:
            r = subprocess.run(cmd, cwd=target, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            return f"`{' '.join(cmd[2:])}` timed out"
        out = (r.stdout + r.stderr).strip()
        if r.returncode != 0 and "already" not in out.lower():
            return f"`{' '.join(cmd[2:])}` failed: {out[-300:]}"
    return None


def merge_settings(target, context_name, plugin_id, rel_path, dry_run):
    """Write the two keys into <target>/.claude/settings.json. Returns (state, error)."""
    settings_path = target / ".claude" / "settings.json"
    settings = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return None, f".claude/settings.json is not valid JSON ({e}); left untouched"
    before = json.dumps(settings, sort_keys=True)
    settings.setdefault("extraKnownMarketplaces", {})[context_name] = {
        "source": {"source": "directory", "path": rel_path}
    }
    settings.setdefault("enabledPlugins", {})[plugin_id] = True
    changed = json.dumps(settings, sort_keys=True) != before
    if changed and not dry_run:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return ("unchanged" if not changed else ("would update" if dry_run else "updated")), None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--only", nargs="*", help="code repository folder names to wire as well")
    ap.add_argument("--register", action="store_true",
                    help="also register the marketplace and install the plugin on this machine via the claude CLI")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    catalog = Path(args.catalog).resolve()
    context_name = f"{args.slug}-context"
    context_dir = catalog / context_name
    plugin_id = f"{args.slug}-shared@{context_name}"

    if not (context_dir / ".claude-plugin" / "marketplace.json").exists():
        print(f"error: no marketplace at {context_dir}/.claude-plugin/marketplace.json", file=sys.stderr)
        return 1

    # target -> relative marketplace path recorded in its settings
    targets = [(context_dir, "."), (catalog, f"./{context_name}")]
    for name in (args.only or []):
        repo = catalog / name
        if name == context_name:
            continue
        if not repo.is_dir():
            print(f"  ! {name}: no such directory in the catalog")
            continue
        targets.append((repo, f"../{context_name}"))

    failures = 0
    for target, rel_path in targets:
        if rel_path == ".":
            label = f"{target.name}  (the context repository itself)"
        elif target == catalog:
            label = f"{target.name}/  (the catalog folder)"
        else:
            label = target.name
        if args.register and not args.dry_run:
            err = register(target, context_dir, plugin_id)
            if err:
                print(f"  ! {label}: {err}")
                failures += 1
            else:
                print(f"  ✔ {label}: marketplace registered, plugin installed at project scope")
        state, err = merge_settings(target, context_name, plugin_id, rel_path, args.dry_run)
        if err:
            print(f"  ! {label}: {err}")
            failures += 1
            continue
        mark = "=" if state == "unchanged" else "+"
        print(f"  {mark} {target.name}/.claude/settings.json — {state} (source: {rel_path})")

    if len(targets) == 2:
        print("\nNo code repositories wired — the catalog holds none yet. Add one later and "
              "re-run this skill, or copy the settings block from the context repository's "
              "plugin README, changing the path to \"../%s\"." % context_name)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
