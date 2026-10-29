#!/usr/bin/env python3
"""Give a knowledge-base change its own checkout, so writing never touches the
person's clone — whatever branch it is on, whatever is uncommitted in it. Every
step that changes git state runs only with --yes, which the caller passes after
the person said yes to that step; nothing here substitutes one yes for another.

    write_worktree.py start <KB> <branch>                    propose: check, change nothing
    write_worktree.py start <KB> <branch> --yes --at <sha>   create the confirmed worktree
    write_worktree.py commit <W> --message <text> --yes      commit everything in W
    write_worktree.py push <W> --yes                         push W's branch, nothing else

`start` without --yes asks the remote for its default branch (never guessed from
local state), fetches only that branch, refuses a branch name that already exists
locally or on origin, and prints the proposal to confirm:

    WORKTREE=/abs/path            <KB parent>/<KB name>-worktrees/<branch>
    BRANCH=<branch>
    BASE=origin/<default>
    BASE_COMMIT=<sha>
    UPSTREAM=origin/<branch>
    REMOTE=<origin's URL>         where a push would send the branch

`start --yes --at <sha>` repeats the checks and creates exactly that: a new branch
at the confirmed commit, which must still be on origin/<default>, with no tracking,
marked in git config as a write branch. <KB> must be the main checkout of a
context repository — never a subfolder, a worktree, or a code repository.

`commit` works only in a write worktree made by `start` — or, when the knowledge
base has no remote yet, in the knowledge base itself — never on a default branch,
and refuses when there is nothing to commit. `push` works only in a write worktree;
it refuses the default branch, a detached HEAD and uncommitted changes, and never
forces. It prints the remote's own output, which on Bitbucket and GitHub carries the
pull-request link.

Exit 0 on success; 2 when refused or on bad input; 4 when `start --yes` finds the
confirmed proposal no longer holds (propose again and ask again); 3 when the KB has
no remote (the caller falls back to the rule in locating-project-context.md); 1 on a
git failure, including no network.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

TIMEOUT = int(os.environ.get("TSH_CONTEXT_FETCH_TIMEOUT", "5"))
BRANCH_RE = re.compile(r"[a-z0-9][a-z0-9._/-]{0,80}")
SHA_RE = re.compile(r"[0-9a-f]{7,40}")
PROTECTED = ("main", "master", "develop", "trunk")


def git(cwd, *args, timeout=30, env=None):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                           timeout=timeout, env=env)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s"
    except OSError as e:
        return 1, "", str(e)


def net_env(cwd):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    if "GIT_SSH_COMMAND" not in env and not git(cwd, "config", "--get", "core.sshCommand")[1]:
        env["GIT_SSH_COMMAND"] = f"ssh -o BatchMode=yes -o ConnectTimeout={TIMEOUT}"
    return env


def fail(code, msg):
    print(msg, file=sys.stderr)
    return code


def default_branch(kb, env):
    """The remote's own answer first: a stale local origin/HEAD must not pick the base."""
    code, out, _ = git(kb, "ls-remote", "--symref", "origin", "HEAD", timeout=TIMEOUT, env=env)
    m = re.search(r"ref: refs/heads/(\S+)\s+HEAD", out) if code == 0 else None
    if m:
        return m.group(1)
    code, out, _ = git(kb, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    return out[len("origin/"):] if code == 0 and out.startswith("origin/") else None


def is_context_repo(path):
    try:
        name = json.loads((path / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")).get("name")
    except (OSError, ValueError):
        return False
    return isinstance(name, str) and name.endswith("-context")


def checkout(path):
    """(top, gitdir, common dir) of the checkout at path, all absolute; None outside git."""
    code, top, _ = git(path, "rev-parse", "--show-toplevel")
    _, gitdir, _ = git(path, "rev-parse", "--absolute-git-dir")
    _, common, _ = git(path, "rev-parse", "--git-common-dir")
    if code != 0 or not gitdir or not common:
        return None
    common = Path(common) if Path(common).is_absolute() else path / common
    return Path(top).resolve(), Path(gitdir).resolve(), common.resolve()


def is_kb_main(path):
    """The main checkout of a context repository, at its top — not a subfolder, not a worktree."""
    c = checkout(path)
    return bool(c) and c[0] == path and c[1] == c[2] and is_context_repo(path)


def is_write_worktree(wt):
    """A linked worktree that `start` made, beside its context repository's main checkout,
    on a branch `start` marked — never the person's clone, never another repository."""
    c = checkout(wt)
    if not c or c[0] != wt or c[1] == c[2]:
        return False
    main = c[2].parent
    branch = git(wt, "symbolic-ref", "--quiet", "--short", "HEAD")[1]
    return (is_context_repo(main) and wt.parent == main.parent / f"{main.name}-worktrees" and bool(branch)
            and git(wt, "config", "--get", f"branch.{branch}.tshContextWrite")[1] == "true")


def is_unpublished_kb(path):
    """The knowledge base itself, while it has never had a remote."""
    return (is_kb_main(path) and not git(path, "remote")[1]
            and not git(path, "for-each-ref", "--count=1", "refs/remotes")[1])


def start(kb, branch, confirmed, at):
    kb = Path(kb).resolve()
    if not BRANCH_RE.fullmatch(branch) or ".." in branch or branch.endswith((".lock", "/")):
        return fail(2, f"'{branch}' is not a usable branch name: lowercase, digits, '-', '/', '.'.")
    if confirmed and not (at and SHA_RE.fullmatch(at)):
        return fail(2, "--yes needs --at <BASE_COMMIT> from the proposal the person confirmed. Nothing created.")
    if not is_kb_main(kb):
        return fail(2, f"{kb} is not the main checkout of a context repository. Nothing created.")
    # Once confirmed, a check that no longer passes means the proposal changed under the
    # person: say so with its own code, so the caller proposes again instead of renaming.
    refused = 4 if confirmed else 2
    remote = git(kb, "remote", "get-url", "origin")[1]
    if not remote:
        return fail(3, "The knowledge base has no remote: there is no approved version to branch from.")
    env = net_env(kb)
    base = default_branch(kb, env)
    if not base:
        return fail(1, "Could not ask the remote for its default branch (offline or no access). Nothing created.")
    if branch == base or branch in PROTECTED:
        return fail(refused, f"'{branch}' is a default branch; a change needs its own branch.")
    code, _, err = git(kb, "fetch", "--quiet", "origin",
                       f"+refs/heads/{base}:refs/remotes/origin/{base}", timeout=TIMEOUT, env=env)
    if code != 0:
        return fail(1, f"Could not fetch origin/{base}: {err[-200:]} Nothing created.")
    if git(kb, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")[0] == 0:
        return fail(refused, f"Branch '{branch}' already exists in this clone; propose another name.")
    code, _, _ = git(kb, "ls-remote", "--exit-code", "--heads", "origin", branch, timeout=TIMEOUT, env=env)
    if code != 2:
        return fail(refused, f"Branch '{branch}' already exists on origin, or origin could not be asked; "
                             "propose another name.")
    path = kb.parent / f"{kb.name}-worktrees" / branch.replace("/", "-")
    if path.exists():
        return fail(refused, f"{path} already exists; propose another name.")
    tip = git(kb, "rev-parse", f"refs/remotes/origin/{base}")[1]

    if not confirmed:
        print(f"WORKTREE={path}\nBRANCH={branch}\nBASE=origin/{base}\nBASE_COMMIT={tip[:12]}\n"
              f"UPSTREAM=origin/{branch}\nREMOTE={remote}")
        return 0

    code, sha, _ = git(kb, "rev-parse", "--verify", "--quiet", f"{at}^{{commit}}")
    if code != 0 or git(kb, "merge-base", "--is-ancestor", sha, f"refs/remotes/origin/{base}")[0] != 0:
        return fail(4, f"{at} is not on origin/{base}: propose again and confirm the new proposal. "
                       "Nothing created.")
    code, _, err = git(kb, "worktree", "add", "--quiet", "--no-track", "-b", branch, str(path), sha)
    if code != 0:
        return fail(1, f"git worktree add failed: {err[-200:]}")
    git(kb, "config", f"branch.{branch}.tshContextWrite", "true")
    head = git(path, "rev-parse", "HEAD")[1]
    if head != sha or git(path, "rev-parse", "--abbrev-ref", "@{u}")[0] == 0:
        return fail(1, f"Created {path}, but it is not at {sha[:12]} without an upstream: check it by hand.")
    behind = git(kb, "rev-list", "--count", f"{sha}..refs/remotes/origin/{base}")[1]
    print(f"WORKTREE={path}\nBRANCH={branch}\nBASE=origin/{base}\nBASE_COMMIT={head[:12]}\n"
          f"UPSTREAM=origin/{branch}\nREMOTE={remote}"
          + (f"\nBASE_BEHIND={behind}" if behind not in ("", "0") else ""))
    return 0


def commit(target, message, confirmed):
    w = Path(target).resolve()
    if not confirmed:
        return fail(2, "Refusing to commit without --yes: show the change and ask the person first.")
    if not message.strip():
        return fail(2, "A commit needs --message.")
    if not (is_write_worktree(w) or is_unpublished_kb(w)):
        return fail(2, "Only a write worktree made by `start` is committed to — or the knowledge base "
                       "itself while it has no remote. Nothing was committed.")
    branch = git(w, "symbolic-ref", "--quiet", "--short", "HEAD")[1]
    if not branch:
        return fail(2, "Detached HEAD: nothing was committed.")
    if branch in PROTECTED and not is_unpublished_kb(w):
        return fail(2, f"Refusing to commit on '{branch}': a change goes on its own branch.")
    code, _, err = git(w, "add", "-A")
    if code != 0:
        return fail(1, f"git add failed: {err[-200:]}")
    if not git(w, "diff", "--cached", "--name-only")[1]:
        return fail(2, "Nothing to commit.")
    code, _, err = git(w, "commit", "--quiet", "-m", message)
    if code != 0:
        return fail(1, f"git commit failed (is user.name / user.email set?): {err[-200:]}")
    print(git(w, "show", "--stat", "--format=COMMIT=%h %s", "HEAD")[1])
    return 0


def push(worktree, confirmed):
    wt = Path(worktree).resolve()
    if not confirmed:
        return fail(2, "Refusing to push without --yes: ask the person first.")
    if not is_write_worktree(wt):
        return fail(2, "Only a write worktree made by `start` is pushed — never the person's own clone. "
                       "Nothing was pushed.")
    branch = git(wt, "symbolic-ref", "--quiet", "--short", "HEAD")[1]
    if not branch:
        return fail(2, "Detached HEAD: nothing to push.")
    if branch in PROTECTED:
        return fail(2, f"Refusing to push '{branch}': the default branch changes only through a pull request.")
    if git(wt, "status", "--porcelain")[1]:
        return fail(2, "Uncommitted changes in the worktree: commit them first, or say what to leave out.")
    env = net_env(wt)
    if branch == default_branch(wt, env):
        return fail(2, f"Refusing to push '{branch}': the default branch changes only through a pull request.")
    code, out, err = git(wt, "push", "--set-upstream", "origin", f"refs/heads/{branch}:refs/heads/{branch}",
                         timeout=max(30, TIMEOUT), env=env)
    print((out + "\n" + err).strip())
    if code != 0:
        return 1
    upstream = git(wt, "rev-parse", "--abbrev-ref", "@{u}")[1]
    if upstream != f"origin/{branch}":
        return fail(1, f"Pushed, but the upstream is '{upstream}', not 'origin/{branch}': check it by hand.")
    return 0


def parse(args, valued):
    """Flags and `--name value` pairs. A value is never another option, so a missing
    value cannot swallow the `--yes` that follows it and count it twice."""
    flags, values, i = set(), {}, 0
    while i < len(args):
        if args[i] in valued:
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                return None
            values[args[i]] = args[i + 1]
            i += 2
        elif args[i] == "--yes":
            flags.add("--yes")
            i += 1
        else:
            return None
    return flags, values


def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "start" and (p := parse(a[3:], {"--at"})):
        return start(a[1], a[2], "--yes" in p[0], p[1].get("--at", ""))
    if len(a) >= 2 and a[0] == "commit" and (p := parse(a[2:], {"--message"})):
        return commit(a[1], p[1].get("--message", ""), "--yes" in p[0])
    if len(a) >= 2 and a[0] == "push" and (p := parse(a[2:], set())):
        return push(a[1], "--yes" in p[0])
    return fail(2, __doc__)


if __name__ == "__main__":
    sys.exit(main())
