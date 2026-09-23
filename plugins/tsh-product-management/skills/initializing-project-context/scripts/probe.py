#!/usr/bin/env python3
"""Probe the current directory and print the values the skill's fixed questions need.

Output is JSON on stdout, always with the same keys, so the AskUserQuestion call
the skill builds looks the same every run — only the option labels change:

  cwd, folder_name, parent_name, cwd_is_empty, cwd_is_git_repo,
  name_option_a       ("Demo Context"  — title-cased folder name)
  name_option_b       ("Ai Driven Development" — title-cased parent folder name)
  git_owner           ("Jane Doe (jane.doe@example.com)" or null when git config has no identity)
  siblings            (directories in cwd other than hidden ones — future code repositories)
  can_be_catalog      (true when cwd is not itself a git repository: the catalog may BE
                       this folder, whether it is empty or already holds code repositories)
  folder_name_is_slug (true when folder_name is already kebab-case; when false,
                       folder_slug is the slug to use and the folder keeps its name)
  folder_slug         (kebab-case of folder_name, e.g. "Swarmer_API" -> "swarmer-api")
  parent_is_git_repo  (true when the PARENT folder is a git repository — then the
                       catalog cannot be created there either)
  parent_writable     (true when the parent folder accepts new files)
  parent_siblings     (directories in the parent other than hidden ones, cwd included —
                       the code repositories a catalog in the parent would hold)
  parent_name_is_slug, parent_slug (same as the folder pair, for the parent)

Never writes anything. Never fails: missing git or an empty folder yields nulls.

Usage: python3 probe.py [directory]
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def title(name):
    return " ".join(w.capitalize() for w in re.split(r"[-_\s]+", name) if w)


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-")


def is_git_repo(path):
    try:
        r = subprocess.run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except FileNotFoundError:
        return False


def git_value(key):
    try:
        r = subprocess.run(["git", "config", "--get", key], capture_output=True, text=True)
        return r.stdout.strip() or None
    except FileNotFoundError:
        return None


def visible_dirs(path):
    if not path.is_dir():
        return []
    return sorted(p.name for p in path.iterdir() if p.is_dir() and not p.name.startswith("."))


def main():
    cwd = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    parent = cwd.parent
    entries = [p for p in cwd.iterdir() if not p.name.startswith(".")] if cwd.is_dir() else []
    name, email = git_value("user.name"), git_value("user.email")
    print(json.dumps({
        "cwd": str(cwd),
        "folder_name": cwd.name,
        "parent_name": parent.name,
        "cwd_is_empty": len(entries) == 0,
        "cwd_is_git_repo": is_git_repo(cwd),
        "can_be_catalog": not is_git_repo(cwd),
        "name_option_a": title(cwd.name),
        "name_option_b": title(parent.name),
        "git_owner": f"{name} ({email})" if name and email else None,
        "siblings": sorted(p.name for p in entries if p.is_dir()),
        "folder_name_is_slug": bool(KEBAB.fullmatch(cwd.name)),
        "folder_slug": slugify(cwd.name) or None,
        "parent_is_git_repo": is_git_repo(parent),
        "parent_writable": os.access(parent, os.W_OK),
        "parent_siblings": visible_dirs(parent),
        "parent_name_is_slug": bool(KEBAB.fullmatch(parent.name)),
        "parent_slug": slugify(parent.name) or None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
