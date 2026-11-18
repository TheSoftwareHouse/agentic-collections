#!/usr/bin/env python3
"""PreToolUse hook: block `gh pr create` until the change-reviewer agent has
reviewed the current branch.

The agent writes the marker `<git dir>/change-review/<branch>` as its last step,
with `/` in the branch name written as `%2F`. The marker records that a review
ran on this branch, not that it passed, and survives later commits, so fixing the
findings needs no second review. Exit code 2 blocks the tool call and shows
stderr to Claude.

Only a branch whose commits since `origin/main` touch `plugins/`, `evals/` or
`.claude/` needs the review; documentation-only changes pass. When the merge base
with `origin/main` cannot be found, the review is required.

It is a reminder, not a lock: a command hidden in `bash -c`, backticks or a
script is not seen, and `--head <other branch>` is checked against the current
branch.
"""
import json
import os
import re
import shlex
import subprocess
import sys

OPERATORS = set(";&|()\n")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
REPO_FLAGS = {"-R", "--repo"}
REVIEWED_PATHS = ("plugins/", "evals/", ".claude/")


def segments(command):
    """Yield the argv of each simple command, splitting on shell operators and
    respecting quotes, so text inside a quoted argument is never a command."""
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    current = []
    try:
        for token in lexer:
            if token and set(token) <= OPERATORS:
                yield current
                current = []
            else:
                current.append(token)
    except ValueError:  # unbalanced quotes: judge what was read so far
        pass
    yield current


def opens_pull_request(argv):
    while argv and ASSIGNMENT.match(argv[0]):
        argv = argv[1:]
    if not argv or os.path.basename(argv[0]) != "gh":
        return False
    rest = argv[1:]
    while rest and (rest[0] in REPO_FLAGS or rest[0].startswith("--repo=")):
        rest = rest[1:] if rest[0].startswith("--repo=") else rest[2:]
    if len(rest) < 2 or rest[0] != "pr" or rest[1] not in ("create", "new"):
        return False
    return not any(arg in ("--help", "-h") for arg in rest[2:])


def git(cwd, *args):
    try:
        out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    except OSError:
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def needs_review(cwd):
    base = git(cwd, "merge-base", "HEAD", "origin/main")
    if not base:
        return True
    changed = git(cwd, "diff", "--name-only", base, "HEAD").splitlines()
    return any(path.startswith(REVIEWED_PATHS) for path in changed)


def main():
    try:
        event = json.load(sys.stdin)
        command = event["tool_input"]["command"]
    except (ValueError, KeyError, TypeError):
        return 0
    if not isinstance(command, str) or not any(opens_pull_request(argv) for argv in segments(command)):
        return 0
    cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else None
    if cwd and not os.path.isdir(cwd):
        cwd = None
    branch = git(cwd, "branch", "--show-current")
    marker_dir = git(cwd, "rev-parse", "--path-format=absolute", "--git-path", "change-review")
    if not branch or not marker_dir:
        return 0
    marker = os.path.join(marker_dir, branch.replace("/", "%2F"))
    if os.path.isfile(marker) or not needs_review(cwd):
        return 0
    print(
        f"No change review recorded for branch '{branch}'. Run the change-reviewer "
        "agent on this branch and address its findings before opening the pull "
        "request. If the user explicitly waives the review, they create the marker "
        f"themselves: mkdir -p '{marker_dir}' && git rev-parse HEAD > '{marker}'",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
