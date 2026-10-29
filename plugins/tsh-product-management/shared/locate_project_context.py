#!/usr/bin/env python3
"""Find the project-context repository (KB) a session belongs to.

A context repository is a folder holding `docs/README.md` (the area map),
`conventions/ownership.md` and, for wired projects, `.claude-plugin/marketplace.json`
whose `name` is `<slug>-context`. The slug is the project's identity: two clones of
the same project, reached by SSH or HTTPS, are the same project.

Resolution order:

  1. The start directory is inside a context repository  -> that repository.
  2. The code repository is wired: a `<slug>-context` marketplace in
     `.claude/settings.local.json` or `.claude/settings.json` of the repository —
     its working tree, the main checkout when this is a git worktree, then
     `origin/HEAD:.claude/settings.json` for a branch cut before the wiring.
     Then: the clone this person chose earlier (the registry), a `directory`
     source, or a clone already at the default location. Otherwise exit 3 and
     list the existing clones found in the folders above, so the caller asks.
  3. `--url URL` with no code repository: same as 2, slug from the URL.
  4. Nothing wired: the legacy search — each ancestor D, then D/*-context.

Prints on success (exit 0), one KEY=VALUE per line:

    KB=/abs/path          the clone to read
    SLUG=<slug>
    URL=<git url, or empty when the project has no remote yet>
    SOURCE=inside | registry | directory | default | legacy
    REPO=<code repository root, or empty>
    WIRING=commit | local | none
    BLOCK=ok | missing | drift | n/a       the tsh:project-context block in
                                           CLAUDE.md (commit) / CLAUDE.local.md (local)
    READ_ACCESS=granted | missing | n/a    KB in permissions.additionalDirectories
                                           of the repository's settings.local.json

Exit codes:
  0  found
  1  nothing wired and nothing found
  2  legacy search: several context repositories in one folder (candidates on stderr)
  3  wired, but this person has not chosen a clone yet. Prints SLUG, URL, DEFAULT
     and one CANDIDATE=<path> per existing clone found above the repository. The
     caller asks, then re-runs with --use PATH or --clone PATH.
  4  --use / --clone refused (not a clone of this project, clone failed)
  5  the name is taken: on this machine `<slug>-context` already names a project with
     another URL — in the registry, at the default location, or in Claude Code's own
     marketplace list. Prints SLUG, URL and one CONFLICT=<where> per place. Nothing is
     read: the project plugin in this repository may be the other project's too.

Actions (each only after the user said yes):
  --use PATH      remember an existing clone for this project
  --clone PATH    git clone URL into PATH, then remember it
  --grant-read    add KB to permissions.additionalDirectories in the repository's
                  .claude/settings.local.json and keep that file out of git

Writes nothing without an action flag. Never runs a git command that changes a
repository, except `git clone` under --clone and a line in .git/info/exclude under
--grant-read. The registry lives in $TSH_CONTEXT_HOME (default ~/.tsh/context).
Claude Code's marketplace list is read with `claude plugin marketplace list --json`
($TSH_CONTEXT_CLAUDE names the CLI; empty skips that check).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BLOCK_RE = re.compile(r"<!-- tsh:project-context START.*?<!-- tsh:project-context END -->", re.S)
CLONE_TIMEOUT = int(os.environ.get("TSH_CONTEXT_CLONE_TIMEOUT", "120"))
SEARCH_LEVELS = 3


def home():
    return Path(os.environ.get("TSH_CONTEXT_HOME") or Path.home() / ".tsh" / "context").expanduser()


def git_env():
    """No prompt may block a skill: fail fast instead of asking for a password."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    if "GIT_SSH_COMMAND" not in env and not git("config", "--get", "core.sshCommand")[1]:
        env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes -o ConnectTimeout=5"
    return env


def git(*args, cwd=None, timeout=10, env=None):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)


# --- identity -----------------------------------------------------------------

def marketplace_name(path):
    try:
        return json.loads((path / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")).get("name", "")
    except (OSError, ValueError):
        return ""


def is_context_repo(path):
    # os.path never raises: a folder nobody may read (/tmp/systemd-private-*) is just not one.
    return os.path.isfile(path / "docs" / "README.md") and os.path.isfile(path / "conventions" / "ownership.md")


def slug_of(kb):
    name = marketplace_name(kb) or kb.name
    return name[: -len("-context")] if name.endswith("-context") else name


def is_clone_of(path, slug):
    return os.path.isdir(path) and is_context_repo(path) and marketplace_name(path) == f"{slug}-context"


def slug_from_url(url):
    base = url.rstrip("/").rsplit("/", 1)[-1].rsplit(":", 1)[-1]
    base = base[:-4] if base.endswith(".git") else base
    return base[: -len("-context")] if base.endswith("-context") else base


# --- wiring in a code repository --------------------------------------------------

def common_dir(path):
    """The repository's shared .git directory, absolute — without --path-format,
    which git before 2.31 does not know."""
    code, common, _ = git("rev-parse", "--git-common-dir", cwd=path)
    if code != 0 or not common:
        return None
    p = Path(common)
    return (p if p.is_absolute() else Path(path) / p).resolve()


def repo_roots(start):
    """(this checkout's root, main checkout's root) — equal outside a git worktree."""
    code, top, _ = git("rev-parse", "--show-toplevel", cwd=start)
    if code != 0:
        return None, None
    common = common_dir(start)
    main = common.parent if common and common.name == ".git" else Path(top)
    return Path(top).resolve(), main.resolve()


def wiring_in(settings):
    for name, entry in (settings.get("extraKnownMarketplaces") or {}).items():
        if name.endswith("-context") and isinstance(entry, dict):
            return name[: -len("-context")], entry.get("source") or {}
    return None


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def find_wiring(start):
    """Returns (slug, source, mode, repo_root, wiring_root) or None. wiring_root is
    this checkout when its own files carry the wiring, else None (found in the main
    checkout of a worktree, or in origin/HEAD)."""
    top, main = repo_roots(start)
    if top is None:
        return None
    candidates = [(top, ".claude/settings.local.json", "local"), (top, ".claude/settings.json", "commit")]
    if main != top:
        candidates += [(main, ".claude/settings.local.json", "local"), (main, ".claude/settings.json", "commit")]
    for root, rel, mode in candidates:
        data = read_json(root / rel)
        hit = data and wiring_in(data)
        if hit:
            # Files in the main checkout do not load in a worktree's sessions, so there
            # is nothing to check or repair from here.
            return hit[0], hit[1], mode, top, (root if root == top else None)
    code, out, _ = git("show", "origin/HEAD:.claude/settings.json", cwd=top)
    if code == 0:
        try:
            hit = wiring_in(json.loads(out))
        except ValueError:
            hit = None
        if hit:
            return hit[0], hit[1], "commit", top, None
    return None


def block_state(repo, mode, url):
    f = repo / ("CLAUDE.local.md" if mode == "local" else "CLAUDE.md")
    try:
        m = BLOCK_RE.search(f.read_text(encoding="utf-8"))
    except OSError:
        m = None
    if not m:
        return "missing"
    return "drift" if url and url not in m.group(0) else "ok"


def read_access(repo, kb):
    data = read_json(repo / ".claude" / "settings.local.json") or {}
    dirs = (data.get("permissions") or {}).get("additionalDirectories") or []
    return "granted" if any(Path(d).expanduser().resolve() == kb for d in dirs) else "missing"


# --- the per-person registry --------------------------------------------------------

def registry_path():
    return home() / "registry.json"


def registry():
    return (read_json(registry_path()) or {}).get("projects", {})


def remember(slug, path, url):
    data = read_json(registry_path()) or {}
    data.setdefault("projects", {})[slug] = {"path": str(path), "url": url or ""}
    registry_path().parent.mkdir(parents=True, exist_ok=True)
    registry_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def candidates_above(repo, slug, url=""):
    """Existing clones of this project in the folders above the repository:
    the flat layout (proj-context beside proj-backend) and the project folder
    (project/context-repo beside project/repo-1), whatever the clone is called.
    With a URL, a clone whose origin is another URL is another project's."""
    found, stop = [], Path.home().resolve()
    d = repo
    for _ in range(SEARCH_LEVELS):
        d = d.parent
        try:
            children = sorted(p for p in d.iterdir() if os.path.isdir(p) and not p.name.startswith("."))
        except OSError:
            children = []
        found += [c.resolve() for c in children if c != repo and is_clone_of(c, slug)
                  and not other_origin(c, url)]
        if d == stop or d == d.parent:
            break
    return list(dict.fromkeys(found))


# --- one name, one project ------------------------------------------------------------
# Claude Code keeps one marketplace per name on a machine, and the registry one clone
# per slug: two projects called `portal` would share both, and one of them would read
# the other's knowledge and load the other's skills. The URL tells them apart.

def norm_url(url):
    """One repository however it is written: SSH or HTTPS, with or without a user, a
    port, Bitbucket Server's `/scm/`, or `.git`."""
    u = url.strip().rstrip("/").lower()
    u = re.sub(r"^[a-z][a-z0-9+.-]*://", "", u)
    u = re.sub(r"^[^@/]+@", "", u)
    u = re.sub(r"^([^/:]+):\d+/", r"\1/", u)
    if not u.startswith("/"):
        u = u.replace(":", "/", 1)
    u = re.sub(r"^([^/]+)/scm/", r"\1/", u)
    return u[: -len(".git")] if u.endswith(".git") else u


def same_url(a, b):
    return bool(a) and bool(b) and norm_url(a) == norm_url(b)


def origin_of(path):
    return git("remote", "get-url", "origin", cwd=path)[1] if path and os.path.isdir(path) else ""


def other_origin(path, url):
    """PATH is a clone of another repository than URL. A folder with no origin proves
    nothing either way, and the person is asked about it anyway."""
    theirs = origin_of(path)
    return bool(url and theirs and not same_url(theirs, url))


def known_marketplace(name):
    """(source, where) of Claude Code's marketplace NAME on this machine, else None.
    Best effort: no CLI, or no answer, is None."""
    cli = os.environ.get("TSH_CONTEXT_CLAUDE", "claude")
    if not cli or not shutil.which(cli):
        return None
    try:
        r = subprocess.run([cli, "plugin", "marketplace", "list", "--json"],
                           capture_output=True, text=True, timeout=15)
        entries = json.loads(r.stdout) if r.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None
    for m in entries if isinstance(entries, list) else []:
        if isinstance(m, dict) and m.get("name") == name:
            where = m.get("url") or (f"https://github.com/{m['repo']}" if m.get("repo") else "") or m.get("path", "")
            return m.get("source", ""), where
    return None


def other_projects(slug, url):
    """Where on this machine `<slug>-context` already names a project other than the
    one at URL, one line each: a place that knows another URL. A place with no URL
    (a project with no remote yet) proves nothing, and neither does a repository
    wired without one."""
    if not url:
        return []
    found = []
    entry = registry().get(slug)
    if entry and entry.get("path"):
        path = entry["path"]
        urls = [u for u in (entry.get("url"), origin_of(path)) if u]
        if urls and not any(same_url(u, url) for u in urls):
            found.append(f"registry: {path} ({urls[0]})")
    default = home() / slug
    if is_clone_of(default, slug) and other_origin(default, url):
        found.append(f"default location: {default} ({origin_of(default)})")
    known = known_marketplace(f"{slug}-context")
    if known and known[1]:
        kind, where = known
        theirs = origin_of(where) if kind == "directory" else where
        if theirs and not same_url(theirs, url):
            found.append(f"Claude Code marketplace {slug}-context: {where} ({theirs})")
    return found


def names_in_use(slug, target):
    """For a NEW project at TARGET: where on this machine `<slug>-context` already
    names something else, with or without a URL. TARGET itself, or a clone with
    TARGET's own URL, is not a conflict — that is a re-run."""
    target = Path(target).resolve()
    mine = origin_of(target) if target.is_dir() else ""

    def elsewhere(path=None, url=""):
        if path and Path(path).expanduser().resolve() == target:
            return False
        return not same_url(url, mine)

    found = []
    entry = registry().get(slug)
    if entry and entry.get("path"):
        path = entry["path"]
        url = entry.get("url") or origin_of(path)
        if (url or is_clone_of(Path(path), slug)) and elsewhere(path, url):
            found.append(f"registry: {path} ({url or 'no remote'})")
    default = home() / slug
    if is_clone_of(default, slug) and elsewhere(default, origin_of(default)):
        found.append(f"default location: {default}")
    known = known_marketplace(f"{slug}-context")
    if known and known[1]:
        kind, where = known
        if (elsewhere(url=where) if kind != "directory"
                else os.path.isdir(where) and elsewhere(where, origin_of(where))):
            found.append(f"Claude Code marketplace {slug}-context: {where}")
    return found


def taken_message(slug):
    return (f"On this machine {slug}-context already names another project. Two projects cannot "
            f"share a name: its knowledge is not read here, and the {slug}-shared skills in this "
            f"repository may be that project's. One of the two must be renamed — the project lead "
            f"decides. If the other project is no longer used on this machine, remove `{slug}` "
            f"from {registry_path()} and run `claude plugin marketplace remove {slug}-context`.")


# --- main -------------------------------------------------------------------------

def emit(**kv):
    for k, v in kv.items():
        print(f"{k}={'' if v is None else v}")


def legacy(start):
    for d in (start, *start.parents):
        hits = [d] if is_context_repo(d) else sorted(
            p for p in d.glob("*-context") if os.path.isdir(p) and is_context_repo(p))
        if len(hits) == 1:
            emit(KB=hits[0], SLUG=slug_of(hits[0]), URL="", SOURCE="legacy", REPO="",
                 WIRING="none", BLOCK="n/a", READ_ACCESS="n/a")
            return 0
        if len(hits) > 1:
            print(f"Several context repositories under {d}:", file=sys.stderr)
            for h in hits:
                print(f"  {h}", file=sys.stderr)
            return 2
    print(f"No context repository found from {start} upward, and this repository is not wired.",
          file=sys.stderr)
    return 1


def grant_read(repo, kb):
    path = repo / ".claude" / "settings.local.json"
    data = read_json(path) if path.exists() else {}
    if data is None:
        print(f"{path} is not valid JSON; left untouched", file=sys.stderr)
        return 4
    dirs = data.setdefault("permissions", {}).setdefault("additionalDirectories", [])
    if str(kb) not in dirs:
        dirs.append(str(kb))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    exclude_from_git(repo, ".claude/settings.local.json")
    return 0


def exclude_from_git(repo, pattern):
    gitdir = common_dir(repo)
    if gitdir is None:
        return
    exclude = gitdir / "info" / "exclude"
    lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
    if pattern not in lines and f"/{pattern}" not in lines:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("\n".join(lines + [f"/{pattern}"]) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("start", nargs="?", default=".")
    ap.add_argument("--url", help="locate by the context repository's URL, from any folder")
    act = ap.add_mutually_exclusive_group()
    act.add_argument("--use", metavar="PATH", help="remember an existing clone for this project")
    act.add_argument("--clone", metavar="PATH", help="clone URL into PATH and remember it")
    act.add_argument("--grant-read", action="store_true", help="let sessions in this repository read KB")
    args = ap.parse_args()
    start = Path(args.start).resolve()

    for d in (start, *start.parents):
        if is_context_repo(d) and not args.url:
            emit(KB=d, SLUG=slug_of(d), URL=git("remote", "get-url", "origin", cwd=d)[1],
                 SOURCE="inside", REPO="", WIRING="none", BLOCK="n/a", READ_ACCESS="n/a")
            return 0

    if args.url:
        # The URL's name is only a guess at the project: a registry entry with this
        # URL, or the clone's own marketplace.json, says which project it really is.
        slug = next((k for k, v in registry().items() if v.get("url") == args.url), slug_from_url(args.url))
        source, mode, repo, wroot = {"source": "git", "url": args.url}, "none", None, None
        search_from = repo_roots(start)[0]
    else:
        wired = find_wiring(start)
        if not wired:
            return legacy(start)
        slug, source, mode, repo, wroot = wired
        search_from = repo
    url = source.get("url", "") if source.get("source") == "git" else ""

    clash = other_projects(slug, url)
    if clash:
        emit(SLUG=slug, URL=url)
        for c in clash:
            emit(CONFLICT=c)
        print(taken_message(slug), file=sys.stderr)
        return 5

    if args.use or args.clone:
        target = Path(args.use or args.clone).expanduser().resolve()
        if args.clone:
            if not url:
                print("No git URL for this project: nothing to clone. Use --use with the local clone.",
                      file=sys.stderr)
                return 4
            if target.exists() and any(target.iterdir()):
                print(f"{target} exists and is not empty; clone refused.", file=sys.stderr)
                return 4
            target.parent.mkdir(parents=True, exist_ok=True)
            code, _, err = git("clone", url, str(target), timeout=CLONE_TIMEOUT, env=git_env())
            if code != 0:
                print(f"git clone failed: {err[-400:]}", file=sys.stderr)
                return 4
        # By URL, a clone is this project when we just cloned it from that URL, or its
        # own origin is that URL; then its marketplace.json names the project.
        if args.url and is_context_repo(target) and (
                args.clone or git("remote", "get-url", "origin", cwd=target)[1] == args.url):
            slug = slug_of(target)
        if not is_clone_of(target, slug):
            print(f"{target} is not a clone of {slug}-context (its marketplace name differs, or it is "
                  "not a context repository).", file=sys.stderr)
            return 4
        if other_origin(target, url):
            print(f"{target} is a clone of another project called {slug} "
                  f"({origin_of(target)}), not of {url}.", file=sys.stderr)
            return 4
        remember(slug, target, url)

    kb, how = None, None
    entry = registry().get(slug)
    if entry and is_clone_of(Path(entry["path"]), slug):
        kb, how = Path(entry["path"]).resolve(), "registry"
    elif source.get("source") == "directory":
        p = Path(source.get("path", "")).expanduser()
        p = (repo / p if repo and not p.is_absolute() else p).resolve()
        if is_clone_of(p, slug):
            kb, how = p, "directory"
    if kb is None and is_clone_of(home() / slug, slug):
        kb, how = (home() / slug).resolve(), "default"

    if kb is None:
        emit(SLUG=slug, URL=url, DEFAULT=home() / slug)
        for c in (candidates_above(search_from, slug, url) if search_from else []):
            emit(CANDIDATE=c)
        if entry:
            print(f"The remembered clone {entry['path']} is gone or no longer this project.", file=sys.stderr)
        return 3

    if args.grant_read:
        if not repo:
            print("No code repository here: nothing to grant.", file=sys.stderr)
            return 4
        code = grant_read(wroot or repo, kb)
        wroot = wroot or repo
        if code:
            return code

    # Block and read access live in the checkout that carries the wiring; a branch cut
    # before the wiring has neither, which is not something to repair.
    emit(KB=kb, SLUG=slug, URL=url, SOURCE=how, REPO=repo or "", WIRING=mode,
         BLOCK=block_state(wroot, mode, url) if wroot else "n/a",
         READ_ACCESS=("granted" if kb.is_relative_to(wroot) else read_access(wroot, kb)) if wroot else "n/a")
    return 0


if __name__ == "__main__":
    sys.exit(main())
