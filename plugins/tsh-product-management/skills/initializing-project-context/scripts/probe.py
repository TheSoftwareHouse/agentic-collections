#!/usr/bin/env python3
"""Probe the current directory and print the values the skill's fixed questions need.

Output is JSON on stdout, always with the same keys, so the AskUserQuestion call
the skill builds looks the same every run — only the option labels change:

  cwd, folder_name, parent_name, cwd_is_empty, cwd_is_git_repo,
  name_option_a   ("Demo Context"  — title-cased folder name)
  name_option_b   ("Ai Driven Development" — title-cased parent folder name)
  git_owner       ("Jane Doe (jane.doe@example.com)" or null when git config has no identity)
  siblings        (directories in cwd other than hidden ones — future code repositories)
  can_be_catalog  (true when cwd is not itself a git repository: the catalog may BE
                   this folder, whether it is empty or already holds code repositories)

Never writes anything. Never fails: missing git or an empty folder yields nulls.

Usage: python3 probe.py [directory]
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def title(name):
    return " ".join(w.capitalize() for w in re.split(r"[-_\s]+", name) if w)


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


def main():
    cwd = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    entries = [p for p in cwd.iterdir() if not p.name.startswith(".")] if cwd.is_dir() else []
    name, email = git_value("user.name"), git_value("user.email")
    print(json.dumps({
        "cwd": str(cwd),
        "folder_name": cwd.name,
        "parent_name": cwd.parent.name,
        "cwd_is_empty": len(entries) == 0,
        "cwd_is_git_repo": is_git_repo(cwd),
        "can_be_catalog": not is_git_repo(cwd),
        "name_option_a": title(cwd.name),
        "name_option_b": title(cwd.parent.name),
        "git_owner": f"{name} ({email})" if name and email else None,
        "siblings": sorted(p.name for p in entries if p.is_dir()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
