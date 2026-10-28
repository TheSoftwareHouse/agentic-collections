#!/usr/bin/env python3
"""The three git steps of a new knowledge base, each a separate command so the
skill can ask between them.

    context_repo_git.py init <KB>                 git init + first commit, local only
    context_repo_git.py remote <KB> <URL>         check the URL, set it as origin
    context_repo_git.py first-push <KB> --yes     push the default branch to an EMPTY remote

Every command acts only on KB's own repository: a KB folder inside another
repository gets its own `git init`, and `remote` / `first-push` refuse a folder that
is not the top of its own repository. `init` is idempotent: KB's own repository with
commits is left as it is.

`remote` refuses a URL it cannot reach without a prompt, and a remote that already
has branches — someone has pushed there, so this knowledge base would overwrite or
fork theirs; clone that one instead. An existing `origin` with another URL is
refused too; the same URL is a no-op.

`first-push` runs only with --yes, which the caller passes after the person said
yes, and only while the remote is still empty. It never forces. Afterwards every
change goes through a branch and a pull request.

Prints what it did. Exit 0 on success, 2 when refused, 1 on a git failure.
"""

import os
import subprocess
import sys
from pathlib import Path


def git(kb, *args, timeout=60):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=10")
    try:
        r = subprocess.run(["git", "-C", str(kb), *args], capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s"
    except OSError as e:
        return 1, "", str(e)


def fail(code, msg):
    print(msg, file=sys.stderr)
    return code


def own_repo(kb):
    """True only when KB is the top level of its own repository — never a folder
    inside someone else's (a client's code repository, a home-directory repo)."""
    code, top, _ = git(kb, "rev-parse", "--show-toplevel")
    return code == 0 and Path(top).resolve() == kb


def init(kb):
    if own_repo(kb) and git(kb, "rev-parse", "--verify", "--quiet", "HEAD")[0] == 0:
        print(f"{kb} is already a git repository with commits; left as it is.")
        return 0
    if not own_repo(kb):
        # Also when KB sits inside another repository: it gets its own, so nothing
        # here is ever committed to the enclosing one.
        code, _, err = git(kb, "init", "--quiet", "--initial-branch=main")
        if code != 0:
            return fail(1, f"git init failed: {err}")
    git(kb, "add", "-A")
    code, _, err = git(kb, "commit", "--quiet", "-m", "Initial project context")
    if code != 0:
        return fail(1, f"git commit failed (is user.name / user.email set?): {err}")
    print(f"Committed the scaffold locally on 'main' in {kb}. Nothing was pushed.")
    return 0


def remote(kb, url):
    if not own_repo(kb):
        return fail(2, f"{kb} is not the top of its own git repository; run `init` first. Nothing changed.")
    current = git(kb, "remote", "get-url", "origin")[1]
    if current and current != url:
        return fail(2, f"origin is already {current}; not changing it to {url}.")
    code, heads, err = git(kb, "ls-remote", "--heads", url, timeout=30)
    if code != 0:
        return fail(2, f"Cannot reach {url} ({err[-300:] or 'no detail'}). Check the URL, that the repository "
                       "exists on the host, and that your SSH key or credential helper works without a prompt.")
    if heads:
        return fail(2, f"{url} already has branches: someone has pushed a knowledge base there. "
                       "Clone that one instead of pushing this one.")
    if not current:
        code, _, err = git(kb, "remote", "add", "origin", url)
        if code != 0:
            return fail(1, f"git remote add failed: {err}")
    print(f"origin = {url} (empty, reachable). Nothing was pushed.")
    return 0


def first_push(kb, confirmed):
    if not confirmed:
        return fail(2, "Refusing to push without --yes: ask the person first.")
    if not own_repo(kb):
        return fail(2, f"{kb} is not the top of its own git repository. Nothing was pushed.")
    url = git(kb, "remote", "get-url", "origin")[1]
    if not url:
        return fail(2, "No origin: run `remote` first.")
    code, heads, err = git(kb, "ls-remote", "--heads", "origin", timeout=30)
    if code != 0 or heads:
        return fail(2, "The remote is not empty (or unreachable): the first push is only for an empty "
                       "repository. Nothing was pushed.")
    branch = git(kb, "symbolic-ref", "--short", "HEAD")[1] or "main"
    code, out, err = git(kb, "push", "--set-upstream", "origin", f"refs/heads/{branch}:refs/heads/{branch}")
    if code != 0:
        return fail(1, f"git push failed: {err[-300:]}")
    git(kb, "remote", "set-head", "origin", branch)
    print(f"Pushed '{branch}' to {url}. From now on changes go through branches and pull requests.")
    return 0


def main():
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "init":
        return init(Path(a[1]).resolve())
    if len(a) == 3 and a[0] == "remote":
        return remote(Path(a[1]).resolve(), a[2])
    if len(a) >= 2 and a[0] == "first-push":
        return first_push(Path(a[1]).resolve(), "--yes" in a[2:])
    return fail(2, __doc__)


if __name__ == "__main__":
    sys.exit(main())
