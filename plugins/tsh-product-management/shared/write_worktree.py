#!/usr/bin/env python3
"""Give a knowledge-base change its own checkout, so writing never touches the
person's clone — whatever branch it is on, whatever is uncommitted in it.

    write_worktree.py start <KB> <branch>       new branch from origin/<default>,
                                                in <KB parent>/<KB name>-worktrees/<branch>
    write_worktree.py push <worktree> --yes     push that branch to origin, nothing else

`start` fetches the default branch (capped, never prompts), refuses a branch name
that already exists locally or on origin, and prints:

    WORKTREE=/abs/path
    BRANCH=<branch>
    BASE=origin/<default>@<sha>

`push` runs only with --yes — the caller passes it after the person said yes to
"Push branch <name> to <remote>?". It refuses the default branch, a detached HEAD,
a branch with uncommitted changes, and never forces. It prints the remote's own
output, which on Bitbucket and GitHub carries the link to open a pull request.

Exit 0 on success, 2 on bad input, 3 when the KB has no remote (the caller falls
back to the rule in locating-project-context.md), 1 on a git failure.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

TIMEOUT = int(os.environ.get("TSH_CONTEXT_FETCH_TIMEOUT", "5"))
BRANCH_RE = re.compile(r"[a-z0-9][a-z0-9._/-]{0,80}")


def git(cwd, *args, timeout=30, env=None):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                           timeout=timeout, env=env)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s"


def net_env(cwd):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    if "GIT_SSH_COMMAND" not in env and not git(cwd, "config", "--get", "core.sshCommand")[1]:
        env["GIT_SSH_COMMAND"] = f"ssh -o BatchMode=yes -o ConnectTimeout={TIMEOUT}"
    return env


def fail(code, msg):
    print(msg, file=sys.stderr)
    return code


def default_branch(kb, env):
    code, out, _ = git(kb, "ls-remote", "--symref", "origin", "HEAD", timeout=TIMEOUT, env=env)
    m = re.search(r"ref: refs/heads/(\S+)\s+HEAD", out) if code == 0 else None
    if m:
        return m.group(1)
    code, out, _ = git(kb, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    return out[len("origin/"):] if code == 0 and out.startswith("origin/") else None


def start(kb, branch):
    kb = Path(kb).resolve()
    if not BRANCH_RE.fullmatch(branch) or ".." in branch or branch.endswith((".lock", "/")):
        return fail(2, f"'{branch}' is not a usable branch name: lowercase, digits, '-', '/', '.'.")
    if not git(kb, "remote", "get-url", "origin")[1]:
        return fail(3, "The knowledge base has no remote: there is no approved version to branch from.")
    env = net_env(kb)
    base = default_branch(kb, env)
    if not base:
        return fail(1, "Could not tell the remote's default branch (offline or no access).")
    if branch == base:
        return fail(2, f"'{branch}' is the default branch; a change needs its own branch.")
    code, _, err = git(kb, "fetch", "--quiet", "origin",
                       f"+refs/heads/{base}:refs/remotes/origin/{base}", timeout=TIMEOUT, env=env)
    if code != 0:
        return fail(1, f"Could not fetch origin/{base}: {err[-200:]}")
    if git(kb, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")[0] == 0:
        return fail(2, f"Branch '{branch}' already exists in this clone; pick another name.")
    code, _, _ = git(kb, "ls-remote", "--exit-code", "--heads", "origin", branch, timeout=TIMEOUT, env=env)
    if code != 2:
        return fail(2, f"Branch '{branch}' already exists on origin, or origin could not be asked; "
                       "pick another name.")
    path = kb.parent / f"{kb.name}-worktrees" / branch.replace("/", "-")
    if path.exists():
        return fail(2, f"{path} already exists.")
    code, _, err = git(kb, "worktree", "add", "--quiet", "--no-track", "-b", branch, str(path), f"origin/{base}")
    if code != 0:
        return fail(1, f"git worktree add failed: {err[-200:]}")
    sha = git(path, "rev-parse", "--short", "HEAD")[1]
    print(f"WORKTREE={path}\nBRANCH={branch}\nBASE=origin/{base}@{sha}")
    return 0


def push(worktree, confirmed):
    wt = Path(worktree).resolve()
    if not confirmed:
        return fail(2, "Refusing to push without --yes: ask the person first.")
    code, gitdir, _ = git(wt, "rev-parse", "--absolute-git-dir")
    _, common, _ = git(wt, "rev-parse", "--git-common-dir")
    common_abs = (wt / common).resolve() if common and not Path(common).is_absolute() else Path(common or ".")
    if code != 0 or Path(gitdir).resolve() == common_abs.resolve() or not wt.parent.name.endswith("-worktrees"):
        return fail(2, "Only a write worktree made by `start` is pushed — never the person's own clone. "
                       "Nothing was pushed.")
    branch = git(wt, "symbolic-ref", "--quiet", "--short", "HEAD")[1]
    if not branch:
        return fail(2, "Detached HEAD: nothing to push.")
    env = net_env(wt)
    base = default_branch(wt, env)
    if branch == base or branch in ("main", "master", "develop", "trunk"):
        return fail(2, f"Refusing to push '{branch}': the default branch changes only through a pull request.")
    if git(wt, "status", "--porcelain")[1]:
        return fail(2, "Uncommitted changes in the worktree: commit them first, or say what to leave out.")
    code, out, err = git(wt, "push", "--set-upstream", "origin", f"refs/heads/{branch}:refs/heads/{branch}",
                         timeout=max(30, TIMEOUT), env=env)
    print((out + "\n" + err).strip())
    return 0 if code == 0 else 1


def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "start":
        return start(a[1], a[2])
    if len(a) >= 2 and a[0] == "push":
        return push(a[1], "--yes" in a[2:])
    return fail(2, __doc__)


if __name__ == "__main__":
    sys.exit(main())
