#!/usr/bin/env python3
"""Bring a knowledge-base clone up to date before it is read, without ever
touching work in progress.

The only operation that changes the clone is `git pull --ff-only --no-rebase`,
and only when the clone is on the remote's default branch with no uncommitted
changes to tracked files. Everything else is read-only (`fetch`, `status`,
`rev-list`). Never merge, rebase, stash, reset, checkout, or push.

    python3 sync_project_context.py <KB> [--force]

Prints one JSON object:

    {"kb", "remote", "default_branch", "branch", "dirty", "behind", "ahead",
     "fetched", "pulled", "warnings": [{"code", "message"}]}

Warning codes, each a sentence the reader of the answer must see:

    not-git             the KB is plain files, not a git clone
    local-only          no remote yet: knowledge exists only on this machine
    index-lock          another git process holds the index; nothing was done
    busy                another sync of this KB is running; read as is
    offline             fetch failed or timed out (network, VPN, credentials)
    blocked             a local file the update would overwrite stopped the pull
    not-default-branch  the clone is on another branch: reading that branch
    dirty               uncommitted changes in the clone: reading them
    behind              the clone is behind the remote and was not updated
    unknown-default     the approved branch could not be determined; nothing pulled
    diverged            local and remote history differ (e.g. a force-push):
                        nothing was changed; a fresh clone is the fix

The network is used at most once per TTL (default 600 s, TSH_CONTEXT_TTL) unless
--force; each network call is capped (TSH_CONTEXT_FETCH_TIMEOUT, default 5 s)
and can never prompt for a password. Exit 0 always when KB exists — a stale read
with a warning beats no read; exit 1 when KB is not a directory.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

TTL = int(os.environ.get("TSH_CONTEXT_TTL", "600"))
TIMEOUT = int(os.environ.get("TSH_CONTEXT_FETCH_TIMEOUT", "5"))
LOCK_STALE = 120
STAMP, LOCK = "tsh-context-last-fetch", "tsh-context-sync.lock"


def git(kb, *args, timeout=10, env=None):
    try:
        r = subprocess.run(["git", "-C", str(kb), *args], capture_output=True, text=True,
                           timeout=timeout, env=env)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s"
    except OSError as e:
        return 1, "", str(e)


def net_env(kb):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    if "GIT_SSH_COMMAND" not in env and not git(kb, "config", "--get", "core.sshCommand")[1]:
        env["GIT_SSH_COMMAND"] = f"ssh -o BatchMode=yes -o ConnectTimeout={TIMEOUT}"
    return env


def pull_warning(err):
    """Name why a fast-forward pull failed. A local file in the way is not a network
    problem, and calling it 'offline' would hide the one thing the person must fix."""
    low = err.lower()
    if "would be overwritten" in low:
        files = [l.strip() for l in err.splitlines() if l.startswith(("\t", "        "))]
        return ("blocked", "A file in the knowledge-base clone blocks the update"
                + (f" ({', '.join(files[:5])})" if files else "")
                + ": the server has the same file. Nothing was changed; move that file away "
                  "or delete it, and the next read updates the clone.")
    if "fast-forward" in low or "diverg" in low:
        return ("diverged", "The knowledge base's history on the server differs from this "
                            "clone (for example after a force-push). Nothing was changed. "
                            "Reading the local copy; a fresh clone fixes it.")
    return ("offline", f"Could not update the clone ({err[-160:] or 'no detail'}): "
                       "reading the local copy, which may be out of date.")


def default_branch(kb, env=None):
    """origin/HEAD when the clone has it; otherwise ask the remote (only when the
    caller is online anyway). Never guessed from branch names: a repository whose
    default is `develop` may also have a `main`."""
    code, out, _ = git(kb, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if code == 0 and out.startswith("origin/"):
        return out[len("origin/"):]
    if env is not None:
        code, out, _ = git(kb, "ls-remote", "--symref", "origin", "HEAD", timeout=TIMEOUT, env=env)
        for line in out.splitlines() if code == 0 else []:
            if line.startswith("ref: refs/heads/") and line.endswith("\tHEAD"):
                return line[len("ref: refs/heads/"):-len("\tHEAD")]
    return None


def main():
    if len(sys.argv) < 2 or not Path(sys.argv[1]).is_dir():
        print("usage: sync_project_context.py <KB> [--force]", file=sys.stderr)
        return 1
    kb, force = Path(sys.argv[1]).resolve(), "--force" in sys.argv
    out = {"kb": str(kb), "remote": None, "default_branch": None, "branch": None, "dirty": False,
           "behind": 0, "ahead": 0, "fetched": False, "pulled": False, "warnings": []}

    def warn(code, message):
        out["warnings"].append({"code": code, "message": message})

    def done():
        print(json.dumps(out, indent=2))
        return 0

    code, gitdir, _ = git(kb, "rev-parse", "--absolute-git-dir")
    if code != 0:
        warn("not-git", "The knowledge base is plain files, not a git clone: reading them as they are.")
        return done()
    gitdir = Path(gitdir)
    out["branch"] = git(kb, "symbolic-ref", "--quiet", "--short", "HEAD")[1] or None
    out["dirty"] = bool(git(kb, "status", "--porcelain", "--untracked-files=no")[1])
    out["remote"] = git(kb, "remote", "get-url", "origin")[1] or None

    if not out["remote"]:
        warn("local-only", "This knowledge base has no remote yet: it exists only on this machine "
                           "and nobody else sees it. Add the URL with the init skill's 'add URL' mode.")
        if out["dirty"]:
            warn("dirty", "Uncommitted changes in the knowledge base: reading them as they are.")
        return done()

    if (gitdir / "index.lock").exists():
        warn("index-lock", "Another git process is working in the knowledge-base clone "
                           "(index.lock): nothing was updated, reading the files as they are.")
        return done()

    lock = gitdir / LOCK
    try:
        if lock.exists() and time.time() - lock.stat().st_mtime > LOCK_STALE:
            lock.unlink()
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        warn("busy", "Another session is updating the knowledge base right now: reading it as it is.")
        lock = None
    except OSError:
        lock = None

    try:
        out["default_branch"] = default_branch(kb)
        on_default = out["branch"] is not None and out["branch"] == out["default_branch"]
        stamp = gitdir / STAMP
        fresh = stamp.exists() and time.time() - stamp.stat().st_mtime < TTL
        if lock is not None and (force or not fresh):
            env = net_env(kb)
            # Fetch first, capped: the network is the part that can hang. The pull that
            # follows only runs when there is something to fast-forward, so it moves
            # already-fetched objects and needs no tight cap.
            code, _, err = git(kb, "fetch", "--quiet", "origin", timeout=TIMEOUT, env=env)
            out["fetched"] = code == 0
            if code != 0:
                warn("offline", f"Could not reach the server ({err[-160:] or 'no detail'}): "
                                "reading the local copy, which may be out of date.")
            else:
                if not out["default_branch"]:
                    out["default_branch"] = default_branch(kb, env)
                    on_default = out["branch"] is not None and out["branch"] == out["default_branch"]
                d = out["default_branch"]
                behind = d and git(kb, "rev-list", "--count", f"HEAD..origin/{d}")[1] not in ("", "0")
                if on_default and not out["dirty"] and behind:
                    code, _, err = git(kb, "pull", "--ff-only", "--no-rebase", "--quiet", "origin", d,
                                       timeout=max(30, TIMEOUT), env=env)
                    out["pulled"] = code == 0
                    if code != 0:
                        warn(*pull_warning(err))
                # A pull blocked by a local file does not count toward the TTL: once the
                # person moves the file, the next read updates instead of waiting.
                if not any(w["code"] == "blocked" for w in out["warnings"]):
                    stamp.touch()
    finally:
        if lock is not None:
            lock.unlink(missing_ok=True)

    d = out["default_branch"]
    if d:
        code, counts, _ = git(kb, "rev-list", "--left-right", "--count", f"HEAD...origin/{d}")
        if code == 0:
            out["ahead"], out["behind"] = (int(x) for x in counts.split())
    if not d:
        warn("unknown-default", "Could not tell which branch is the approved version (the clone has no "
                                "origin/HEAD and the server was not reached): reading the clone as it is.")
    elif out["branch"] != d:
        warn("not-default-branch", f"The knowledge-base clone is on '{out['branch'] or 'a detached HEAD'}', "
                                   f"not '{d}': reading that branch, which may hold unapproved changes.")
    if out["dirty"]:
        warn("dirty", "Uncommitted changes in the knowledge-base clone: reading them, they are not "
                      "approved knowledge.")
    if out["behind"] and not any(w["code"] in ("diverged", "blocked") for w in out["warnings"]):
        warn("behind", f"The clone is {out['behind']} commit(s) behind the server and was not updated "
                       "(only a clean default branch is updated automatically).")
    return done()


if __name__ == "__main__":
    sys.exit(main())
