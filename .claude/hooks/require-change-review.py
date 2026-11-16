#!/usr/bin/env python3
"""PreToolUse hook: block `gh pr create` until the change-reviewer agent has
reviewed the current branch.

The agent writes the marker `<git dir>/change-review/<branch>` as its last step.
The marker records that a review ran on this branch, not that it passed, and
survives later commits on the branch, so fixing the findings needs no second
review. Exit code 2 blocks the tool call and shows stderr to Claude.
"""
import json
import re
import subprocess
import sys

PR_CREATE = re.compile(r"(?:^|[\s;&|(])gh\s+pr\s+create\b")


def git(*args):
    out = subprocess.run(["git", *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    if not PR_CREATE.search(command):
        return 0
    branch = git("branch", "--show-current")
    marker_dir = git("rev-parse", "--git-path", "change-review")
    if not branch or not marker_dir:
        return 0
    marker = f"{marker_dir}/{branch.replace('/', '-')}"
    try:
        with open(marker, encoding="utf-8"):
            return 0
    except OSError:
        pass
    print(
        f"No change review recorded for branch '{branch}'. Run the change-reviewer "
        "agent on this branch and address its findings before opening the pull "
        "request. If the user explicitly waives the review, they create the marker "
        f"themselves: mkdir -p {marker_dir} && git rev-parse HEAD > {marker}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
