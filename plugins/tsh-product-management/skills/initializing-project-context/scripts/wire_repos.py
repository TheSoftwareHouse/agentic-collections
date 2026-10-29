#!/usr/bin/env python3
"""Connect code repositories to a project's knowledge base, and make the project
plugin live on this machine.

Per code repository, one of two modes:

  commit  (a repository the team may commit config to)
      .claude/settings.json   + the marketplace and both plugins
      CLAUDE.md               + the tsh:project-context block
      Written, never committed: the person reviews and commits them in a pull request.

  local   (a client's repository, or no URL yet)
      .claude/settings.local.json + the same keys
      CLAUDE.local.md             + the same block
      both listed in .git/info/exclude, so nothing ever reaches the repository.

Both modes add, to .claude/settings.local.json, the knowledge-base clone of the
person running this to permissions.additionalDirectories — the path is theirs, so it
is never committed.

The marketplace source is the git URL when the project has one
({"source": "git", "url": URL, "sparsePaths": [".claude-plugin", "plugins"]} —
the plugin never needs the documents), else the clone's absolute path, which is
only ever written in local mode: a committed path would be wrong on every other
machine.

With --self the knowledge base itself is wired too (source ".", the same on every
machine), so a session started in it has the project plugin. Run it before the
knowledge base's first commit, so the committed scaffold carries it.

With --register, the claude CLI registers the marketplace and installs the plugin,
so the person running this can use it at once, without the trust dialog and
restart: at the repository's scope in a code repository, after which the settings
are re-merged to replace the absolute path the CLI writes; and at local scope in the
knowledge base, so the committed settings.json is never touched.

The block is inserted, or replaced when its markers are already there; the rest of
the file is never touched. Moving a repository from local to commit mode removes the
local entry and block, which would otherwise outrank the committed ones. Existing
settings keys are preserved; a settings file that is not valid JSON is left alone and
reported. The person's clone is
remembered for this project (the registry in $TSH_CONTEXT_HOME). Git is only read:
`git ls-remote` against the URL, before anything is written, so a URL nobody can
reach is never wired, and `git remote get-url` of the clones this machine already
knows. A name this machine already uses for another project — another URL in the
registry or in Claude Code's marketplace list — is refused before anything is
written too: the two would share one plugin and one clone.

Usage:
    python3 wire_repos.py --kb <clone> --slug <slug> [--url <git url>]
        [--commit <repo>...] [--local <repo>...] [--self] [--register]

Exit 0 on success, 1 if any repository was skipped or a CLI step failed, 2 on bad
input (including an unreachable URL).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
import locate_project_context as locator  # noqa: E402  the same plugin's own module

COMPANY_MARKETPLACE = "tsh-agentic-collections"
COMPANY_SOURCE = {"source": "github", "repo": "TheSoftwareHouse/agentic-collections"}
KNOWLEDGE_PLUGIN = f"tsh-product-management@{COMPANY_MARKETPLACE}"
INIT = "/tsh-product-management:initializing-project-context"
NAVIGATE = "/tsh-product-management:navigating-project-context"
BLOCK_RE = re.compile(r"<!-- tsh:project-context START.*?<!-- tsh:project-context END -->", re.S)


def block(url, kb):
    where = url or f"{kb} (local only — no remote yet)"
    return (
        f"<!-- tsh:project-context START — DO NOT REMOVE. No agent ever removes or edits this block; "
        f"only {INIT} changes it. -->\n"
        f"Project knowledge base: {where}. For work that touches decisions, scope, glossary terms, the "
        f"data model or new dependencies, use {NAVIGATE}. If that skill is unavailable, say so plainly — "
        f"do not answer from memory and do not clone the repository yourself; the fix is to install "
        f"`{KNOWLEDGE_PLUGIN}` and run {INIT} (Attach repository).\n"
        f"<!-- tsh:project-context END -->"
    )


def git(*args, cwd=None, timeout=15):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=10")
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)


def read_json(path):
    if not path.exists():
        return {}, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except ValueError as e:
        return None, f"{path.name} is not valid JSON ({e}); left untouched"


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def merge_settings(path, slug, source, extra_dirs=()):
    data, err = read_json(path)
    if err:
        return None, err
    before = json.dumps(data, sort_keys=True)
    mkt, plugin = f"{slug}-context", f"{slug}-shared@{slug}-context"
    if source is not None:
        data.setdefault("extraKnownMarketplaces", {})[mkt] = {"source": source}
        data.setdefault("enabledPlugins", {})[plugin] = True
        data["extraKnownMarketplaces"].setdefault(COMPANY_MARKETPLACE, {"source": COMPANY_SOURCE})
        data["enabledPlugins"].setdefault(KNOWLEDGE_PLUGIN, True)
    for d in extra_dirs:
        dirs = data.setdefault("permissions", {}).setdefault("additionalDirectories", [])
        if d not in dirs:
            dirs.append(d)
    changed = json.dumps(data, sort_keys=True) != before
    if changed:
        write_text(path, json.dumps(data, indent=2) + "\n")
    return ("updated" if changed else "unchanged"), None


def put_block(path, text):
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if BLOCK_RE.search(current):
        new = BLOCK_RE.sub(lambda _: text, current, count=1)
    else:
        new = (current.rstrip("\n") + "\n\n" if current.strip() else "") + text + "\n"
    if new == current:
        return "unchanged"
    write_text(path, new)
    return "updated"


def drop_local_wiring(repo, slug):
    """Commit mode replaces an earlier local wiring: settings.local.json outranks
    settings.json, so a leftover entry there would keep the old source on this
    machine, and a leftover block in CLAUDE.local.md would point at a local path."""
    path = repo / ".claude" / "settings.local.json"
    data, err = read_json(path)
    if data and not err:
        before = json.dumps(data, sort_keys=True)
        (data.get("extraKnownMarketplaces") or {}).pop(f"{slug}-context", None)
        (data.get("enabledPlugins") or {}).pop(f"{slug}-shared@{slug}-context", None)
        for key in ("extraKnownMarketplaces", "enabledPlugins"):
            if key in data and not data[key]:
                del data[key]
        if json.dumps(data, sort_keys=True) != before:
            write_text(path, json.dumps(data, indent=2) + "\n")
    local_md = repo / "CLAUDE.local.md"
    if local_md.exists():
        text = local_md.read_text(encoding="utf-8")
        new = BLOCK_RE.sub("", text, count=1).strip()
        if new != text.strip():
            if new:
                local_md.write_text(new + "\n", encoding="utf-8")
            else:
                local_md.unlink()


def exclude(repo, patterns):
    code, common, _ = git("rev-parse", "--git-common-dir", cwd=repo)
    if code != 0 or not common:
        return
    common = Path(common) if Path(common).is_absolute() else repo / common
    f = common / "info" / "exclude"
    lines = f.read_text(encoding="utf-8").splitlines() if f.exists() else []
    new = [p for p in patterns if p not in lines]
    if new:
        write_text(f, "\n".join(lines + new) + "\n")


def register(repo, source_arg, plugin, scope):
    if not shutil.which("claude"):
        return "claude CLI not on PATH"
    for cmd in (["claude", "plugin", "marketplace", "add", source_arg, "--scope", scope],
                ["claude", "plugin", "install", plugin, "--scope", scope]):
        try:
            r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            return f"`{' '.join(cmd[1:4])}` timed out"
        out = (r.stdout + r.stderr).strip()
        if r.returncode != 0 and "already" not in out.lower():
            return f"`{' '.join(cmd[1:4])}` failed: {out[-300:]}"
    return None


def remember(slug, kb, url):
    home = Path(os.environ.get("TSH_CONTEXT_HOME") or Path.home() / ".tsh" / "context").expanduser()
    reg = home / "registry.json"
    data, _ = read_json(reg)
    data = data or {}
    data.setdefault("projects", {})[slug] = {"path": str(kb), "url": url or ""}
    write_text(reg, json.dumps(data, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kb", required=True, help="the knowledge-base clone of the person running this")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--url", default="", help="the context repository's git URL; omit while it has none")
    ap.add_argument("--commit", nargs="*", default=[], metavar="REPO", help="repositories in commit mode")
    ap.add_argument("--local", nargs="*", default=[], metavar="REPO", help="repositories in local mode")
    ap.add_argument("--self", action="store_true", help="wire the knowledge base itself (source '.')")
    ap.add_argument("--register", action="store_true", help="install on this machine via the claude CLI")
    a = ap.parse_args()

    kb = Path(a.kb).expanduser().resolve()
    mkt_file = kb / ".claude-plugin" / "marketplace.json"
    try:
        name = json.loads(mkt_file.read_text(encoding="utf-8")).get("name")
    except (OSError, ValueError):
        name = None
    if name != f"{a.slug}-context":
        print(f"error: {kb} is not the {a.slug}-context repository ({mkt_file} names {name!r})", file=sys.stderr)
        return 2
    if a.url:
        code, _, err = git("ls-remote", "--heads", a.url, timeout=30)
        if code != 0:
            print(f"error: cannot reach {a.url} ({err[-300:] or 'no detail'}). Nothing was written. "
                  "Check the URL and that your SSH key or credential helper works without a prompt.",
                  file=sys.stderr)
            return 2
        clash = locator.other_projects(a.slug, a.url)
        if clash:
            print(f"error: {locator.taken_message(a.slug)}\n  " + "\n  ".join(clash)
                  + "\nNothing was written.", file=sys.stderr)
            return 2
    if a.commit and not a.url:
        print("note: no URL yet — repositories asked for commit mode are wired in local mode until "
              "the project has one (a committed local path would be wrong on every other machine).")
        a.local, a.commit = a.local + a.commit, []

    plugin = f"{a.slug}-shared@{a.slug}-context"
    git_source = {"source": "git", "url": a.url, "sparsePaths": [".claude-plugin", "plugins"]} if a.url else None
    failures = 0

    if a.self:
        state, err = merge_settings(kb / ".claude" / "settings.json", a.slug, {"source": "directory", "path": "."})
        print(f"  {'!' if err else '+'} {kb.name} (the knowledge base itself): {err or state}")
        failures += bool(err)
        if a.register and not err:
            # Local scope: the CLI writes this machine's absolute path into the untracked
            # settings.local.json, never into the committed settings.json, which keeps ".".
            if Path(git("rev-parse", "--show-toplevel", cwd=kb)[1] or "/").resolve() == kb:
                exclude(kb, ["/.claude/settings.local.json"])  # never an enclosing repository
            e = register(kb, str(kb), plugin, "local")
            if e:
                print(f"  ! {kb.name}: {e}")
                failures += 1

    for mode, repos in (("commit", a.commit), ("local", a.local)):
        for r in repos:
            repo = Path(r).expanduser().resolve()
            if not repo.is_dir() or git("rev-parse", "--show-toplevel", cwd=repo)[0] != 0:
                print(f"  ! {r}: not a git repository; skipped")
                failures += 1
                continue
            source = git_source or {"source": "directory", "path": str(kb)}
            settings = repo / ".claude" / ("settings.json" if mode == "commit" else "settings.local.json")
            state, err = merge_settings(settings, a.slug, source)
            if err:
                print(f"  ! {repo.name}: {err}")
                failures += 1
                continue
            if mode == "commit":
                drop_local_wiring(repo, a.slug)
            local = repo / ".claude" / "settings.local.json"
            if not str(kb).startswith(str(repo) + os.sep):
                merge_settings(local, a.slug, None, extra_dirs=[str(kb)])
            memory = repo / ("CLAUDE.md" if mode == "commit" else "CLAUDE.local.md")
            bstate = put_block(memory, block(a.url, kb))
            exclude(repo, ["/.claude/settings.local.json"] + (["/CLAUDE.local.md"] if mode == "local" else []))
            print(f"  + {repo.name} [{mode}]: {settings.relative_to(repo)} {state}, {memory.name} block {bstate}")
            if a.register:
                e = register(repo, a.url or str(kb), plugin, "project" if mode == "commit" else "local")
                if e:
                    print(f"  ! {repo.name}: {e}")
                    failures += 1
                else:
                    merge_settings(settings, a.slug, source)
            if mode == "commit":
                print(f"    to commit in a pull request: .claude/settings.json, CLAUDE.md")

    remember(a.slug, kb, a.url)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
