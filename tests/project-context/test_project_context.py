#!/usr/bin/env python3
"""Is a project's knowledge base set up and found, in every layout people use?

    python3 tests/project-context/test_project_context.py -v

Structure only. Every folder is created under a temporary HOME; code repositories
are local `git init` folders, because the locator recognises "which repository am I
in" through git, exactly as on a real disk. There is no git server, no network, no
clone, fetch, pull or push, and no credentials: the test git config has a fake
identity and no credential helper, and the person's SSH agent is removed from the
environment. Where a URL must be reachable (wiring in commit mode checks it with
`ls-remote`), it is a local `--bare` folder.

Not covered here, by decision: the sync's pull, the write worktree's push and the
first push of a new knowledge base — checked by review and by hand on a real host.
Their refusals are covered, because each is decided before any network call.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "tsh-product-management"
LOCATE = PLUGIN / "shared" / "locate_project_context.py"
GUARD = PLUGIN / "hooks" / "guard-project-context-block.mjs"
WRITE = PLUGIN / "shared" / "write_worktree.py"
INIT = PLUGIN / "skills" / "initializing-project-context" / "scripts"
SCAFFOLD, WIRE, GITSTEPS = INIT / "scaffold.py", INIT / "wire_repos.py", INIT / "context_repo_git.py"
BLOCK = ("<!-- tsh:project-context START — DO NOT REMOVE. -->\nProject knowledge base: {url}.\n"
         "<!-- tsh:project-context END -->\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pctx-")).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()
        gitconfig = self.tmp / "gitconfig"
        gitconfig.write_text("[user]\n\tname = Test\n\temail = t@example.com\n[credential]\n\thelper =\n"
                             "[init]\n\tdefaultBranch = main\n[advice]\n\tdetachedHead = false\n")
        self.env = dict(os.environ, HOME=str(self.home), GIT_CONFIG_GLOBAL=str(gitconfig),
                        GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
                        TSH_CONTEXT_HOME=str(self.home / ".tsh" / "context"))
        for var in ("GIT_SSH_COMMAND", "SSH_AUTH_SOCK", "GIT_ASKPASS", "SSH_ASKPASS", "GIT_CONFIG_PARAMETERS"):
            self.env.pop(var, None)
        self.w = self.tmp / "work"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers ------------------------------------------------------------------

    def git(self, cwd, *args):
        r = subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {r.stderr}")
        return r.stdout.strip()

    def py(self, script, *args, cwd=None, env=None):
        r = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=cwd,
                           env=env or self.env, capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr

    def locate(self, *args, cwd, env=None):
        code, out, err = self.py(LOCATE, *args, cwd=cwd, env=env)
        kv, cands = {}, []
        for line in out.splitlines():
            k, _, v = line.partition("=")
            (cands.append(v) if k == "CANDIDATE" else kv.__setitem__(k, v))
        return code, kv, cands, err

    def context_repo(self, path, slug):
        """What a clone looks like on disk — files only, as `git clone` would leave them."""
        for d in ("docs/decisions", "conventions", ".claude-plugin"):
            (path / d).mkdir(parents=True, exist_ok=True)
        (path / "docs" / "README.md").write_text("# Area map\n")
        (path / "conventions" / "ownership.md").write_text("# Ownership\n")
        (path / ".claude-plugin" / "marketplace.json").write_text(json.dumps({"name": f"{slug}-context"}))
        return path

    @staticmethod
    def url(slug):
        return f"git@bitbucket.org:acme/{slug}-context.git"

    def code_repo(self, path, slug, url=None, mode="commit", block=True):
        """A code repository wired the way init leaves it, committed in commit mode."""
        url = url or self.url(slug)
        path.mkdir(parents=True)
        self.git(path, "init", "-q")
        (path / "README.md").write_text("code\n")
        settings = {"extraKnownMarketplaces": {f"{slug}-context": {"source": {"source": "git", "url": url}}},
                    "enabledPlugins": {f"{slug}-shared@{slug}-context": True}}
        (path / ".claude").mkdir()
        (path / ".claude" / ("settings.json" if mode == "commit" else "settings.local.json")).write_text(
            json.dumps(settings))
        if block:
            (path / ("CLAUDE.md" if mode == "commit" else "CLAUDE.local.md")).write_text(
                "# Repo\n\n" + BLOCK.format(url=url))
        self.git(path, "add", "README.md", *([".claude/settings.json"] if mode == "commit" else []),
                 *(["CLAUDE.md"] if mode == "commit" and block else []))
        self.git(path, "commit", "-qm", "code")
        return path


# --- the layouts ------------------------------------------------------------------

class Layouts(Base):
    def test_flat_layout_two_projects(self):
        """Adam: proj1-context, proj1-backend, proj2-context, proj2-backend side by side."""
        self.context_repo(self.w / "proj1-context", "proj1")
        self.context_repo(self.w / "proj2-context", "proj2")
        b1 = self.code_repo(self.w / "proj1-backend", "proj1")
        self.code_repo(self.w / "proj2-backend", "proj2")
        code, _, cands, _ = self.locate(cwd=b1)
        self.assertEqual((code, cands), (3, [str(self.w / "proj1-context")]), "only proj1's clone is offered")
        code, kv, _, _ = self.locate("--use", cands[0], cwd=b1)
        self.assertEqual((code, kv["KB"], kv["BLOCK"]), (0, cands[0], "ok"))
        (b1 / "src" / "deep").mkdir(parents=True)
        self.assertEqual(self.locate(cwd=b1 / "src" / "deep")[1]["KB"], cands[0], "from any subfolder")
        code, _, cands2, _ = self.locate(cwd=self.w / "proj2-backend")
        self.assertEqual((code, cands2), (3, [str(self.w / "proj2-context")]), "proj2 is its own choice")

    def test_an_unreadable_folder_nearby_is_skipped(self):
        """CI runners keep root-only folders in /tmp; a person may have one beside the code."""
        self.context_repo(self.w / "acme-context", "acme")
        locked = self.w / "locked"
        locked.mkdir()
        locked.chmod(0)
        self.addCleanup(locked.chmod, 0o755)
        repo = self.code_repo(self.w / "acme-api", "acme")
        code, _, cands, err = self.locate(cwd=repo)
        self.assertEqual((code, cands), (3, [str(self.w / "acme-context")]), err)

    def test_project_folder_with_other_files(self):
        """Jakub: project-main-dir/{context-repo, repo-1, other-dir, *.pdf}."""
        root = self.w / "project-main-dir"
        self.context_repo(root / "context-repo", "acme")
        (root / "other-dir").mkdir()
        (root / "brief.pdf").write_text("%PDF")
        repo = self.code_repo(root / "repo-1", "acme")
        code, _, cands, _ = self.locate(cwd=repo)
        self.assertEqual((code, cands), (3, [str(root / "context-repo")]), "found whatever the folder is called")
        self.assertEqual(self.locate("--use", cands[0], cwd=repo)[0], 0)

    def test_scattered_repos_share_one_clone(self):
        kb = self.context_repo(self.home / ".tsh" / "context" / "acme", "acme")
        a = self.code_repo(self.w / "x" / "y" / "backend", "acme")
        b = self.code_repo(self.tmp / "elsewhere" / "frontend", "acme")
        for repo in (a, b):
            code, kv, _, _ = self.locate(cwd=repo)
            self.assertEqual((code, kv["KB"], kv["SOURCE"]), (0, str(kb), "default"))

    def test_new_member_joins(self):
        """Nothing chosen yet: asked once, nothing written before the answer, remembered after."""
        repo = self.code_repo(self.w / "acme-api", "acme")
        code, kv, cands, _ = self.locate(cwd=repo)
        self.assertEqual((code, cands, kv["DEFAULT"]), (3, [], str(self.home / ".tsh" / "context" / "acme")))
        self.assertFalse((self.home / ".tsh").exists(), "nothing written before the person chooses")
        mine = self.context_repo(self.tmp / "my-docs" / "acme-knowledge", "acme")
        self.assertEqual(self.locate("--use", mine, cwd=repo)[0], 0)
        web = self.code_repo(self.w / "acme-web", "acme")
        code, kv, _, _ = self.locate(cwd=web)
        self.assertEqual((code, kv["KB"], kv["SOURCE"]), (0, str(mine), "registry"), "second repo: no question")

    def test_t3_worktree_outside_the_folder(self):
        self.context_repo(self.w / "acme-context", "acme")
        repo = self.code_repo(self.w / "acme-api", "acme")
        self.locate("--use", self.w / "acme-context", cwd=repo)
        wt = self.tmp / "t3-worktrees" / "feature-x"
        self.git(repo, "worktree", "add", "-q", "-b", "feature-x", str(wt))
        code, kv, _, _ = self.locate(cwd=wt)
        self.assertEqual((code, kv["KB"]), (0, str(self.w / "acme-context")))

    def test_worktree_on_branch_cut_before_wiring(self):
        """The wiring is read from origin/HEAD — simulated with local refs, no remote."""
        self.context_repo(self.w / "acme-context", "acme")
        repo = self.code_repo(self.w / "acme-api", "acme")
        self.locate("--use", self.w / "acme-context", cwd=repo)
        self.git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        self.git(repo, "checkout", "-q", "--orphan", "old")
        self.git(repo, "rm", "-rq", "--cached", ".")
        self.git(repo, "commit", "-q", "--allow-empty", "-m", "before wiring")
        self.git(repo, "checkout", "-q", "-f", "main")
        wt = self.tmp / "old-branch"
        self.git(repo, "worktree", "add", "-q", str(wt), "old")
        self.assertFalse((wt / ".claude").exists())
        code, kv, _, _ = self.locate(cwd=wt)
        self.assertEqual((code, kv["SLUG"], kv["BLOCK"]), (0, "acme", "n/a"))

    def test_client_repo_local_mode_and_its_worktree(self):
        self.context_repo(self.w / "acme-context", "acme")
        repo = self.code_repo(self.w / "client-api", "acme", mode="local")
        code, kv, _, _ = self.locate("--use", self.w / "acme-context", cwd=repo)
        self.assertEqual((code, kv["WIRING"], kv["BLOCK"]), (0, "local", "ok"))
        wt = self.tmp / "wt-client"
        self.git(repo, "worktree", "add", "-q", "-b", "f", str(wt))
        self.assertEqual(self.locate(cwd=wt)[1]["WIRING"], "local", "found through the main checkout")

    def test_identity_is_the_project_not_the_folder_or_url(self):
        other = self.context_repo(self.w / "whatever-name", "acme")
        repo = self.code_repo(self.w / "acme-api", "acme", url="https://bitbucket.org/acme/acme-context.git")
        self.assertEqual(self.locate(cwd=repo)[2], [str(other)])

    def test_another_projects_clone_is_refused(self):
        self.context_repo(self.w / "proj2-context", "proj2")
        repo = self.code_repo(self.w / "proj1-api", "proj1")
        code, _, _, err = self.locate("--use", self.w / "proj2-context", cwd=repo)
        self.assertEqual(code, 4)
        self.assertIn("not a clone of proj1-context", err)

    def test_remembered_clone_deleted(self):
        kb = self.context_repo(self.w / "acme-context", "acme")
        repo = self.code_repo(self.w / "acme-api", "acme")
        self.locate("--use", kb, cwd=repo)
        shutil.rmtree(kb)
        code, _, _, err = self.locate(cwd=repo)
        self.assertEqual(code, 3)
        self.assertIn("gone", err)

    def test_by_url_without_a_code_repository(self):
        kb = self.context_repo(self.home / ".tsh" / "context" / "acme", "acme")
        pm = self.tmp / "pm-desktop"
        pm.mkdir()
        code, kv, _, _ = self.locate("--url", self.url("acme"), cwd=pm)
        self.assertEqual((code, kv["KB"], kv["WIRING"]), (0, str(kb), "none"))

    def test_by_url_offers_the_clone_beside_the_repository(self):
        self.context_repo(self.w / "beta-context", "beta")
        repo = self.w / "client api"
        repo.mkdir(parents=True)
        self.git(repo, "init", "-q")
        code, _, cands, _ = self.locate("--url", self.url("beta"), cwd=repo)
        self.assertEqual((code, cands), (3, [str(self.w / "beta-context")]))

    def test_session_inside_the_context_repo(self):
        kb = self.context_repo(self.w / "acme-context", "acme")
        (kb / "docs" / "backend").mkdir()
        code, kv, _, _ = self.locate(cwd=kb / "docs" / "backend")
        self.assertEqual((code, kv["KB"], kv["SOURCE"]), (0, str(kb), "inside"))

    def test_old_sibling_layout_still_works(self):
        self.context_repo(self.w / "cat" / "acme-context", "acme")
        (self.w / "cat" / "api").mkdir()
        self.assertEqual(self.locate(cwd=self.w / "cat" / "api")[1]["SOURCE"], "legacy")
        self.context_repo(self.w / "cat" / "beta-context", "beta")
        self.assertEqual(self.locate(cwd=self.w / "cat" / "api")[0], 2, "two projects: ask, never pick")

    def test_not_wired_nothing_found(self):
        repo = self.w / "random"
        repo.mkdir(parents=True)
        self.git(repo, "init", "-q")
        self.assertEqual(self.locate(cwd=repo)[0], 1)


class BlockAndReadAccess(Base):
    def setUp(self):
        super().setUp()
        self.kb = self.context_repo(self.w / "acme-context", "acme")

    def wired(self, **kw):
        repo = self.code_repo(self.w / "acme-api", "acme", **kw)
        self.locate("--use", self.kb, cwd=repo)
        return repo

    def test_missing(self):
        self.assertEqual(self.locate(cwd=self.wired(block=False))[1]["BLOCK"], "missing")

    def test_drift(self):
        repo = self.wired()
        (repo / "CLAUDE.md").write_text(BLOCK.format(url="git@bitbucket.org:old/acme-context.git"))
        self.assertEqual(self.locate(cwd=repo)[1]["BLOCK"], "drift")

    def test_grant_read_stays_out_of_git(self):
        repo = self.wired()
        self.assertEqual(self.locate(cwd=repo)[1]["READ_ACCESS"], "missing")
        code, kv, _, _ = self.locate("--grant-read", cwd=repo)
        self.assertEqual((code, kv["READ_ACCESS"]), (0, "granted"))
        self.assertEqual(self.git(repo, "status", "--porcelain"), "", "git sees nothing new")


# --- init: scaffold and wiring, in both layouts --------------------------------------

class InitHelpers(Base):
    def scaffold(self, *placement, slug="acme"):
        code, out, err = self.py(SCAFFOLD, "--name", "Acme Shop", "--slug", slug, "--owner-tbd", *placement)
        self.assertEqual(code, 0, err)
        return Path(out.split("CONTEXT_DIR=")[1].splitlines()[0])

    def checkers_pass(self, kb):
        for script in ("check_links.py", "check_tables.py", "check_decisions.py", "check_plugin.py"):
            code, out, err = self.py(kb / "scripts" / script, cwd=kb)
            self.assertEqual(code, 0, f"{script}: {out}{err}")

    def remote_folder(self, slug):
        """A reachable URL with no server: a local bare folder."""
        bare = self.tmp / "remotes" / f"{slug}-context.git"
        bare.parent.mkdir(exist_ok=True)
        self.git(self.tmp, "init", "-q", "--bare", str(bare))
        return str(bare)

    def bare_repo(self, path):
        path.mkdir(parents=True)
        self.git(path, "init", "-q")
        return path


class Init(InitHelpers):
    def test_flat_layout_end_to_end(self):
        """Adam's layout: init in the folder, own repo committed, client repo local; found afterwards."""
        self.w.mkdir()
        api, client = self.bare_repo(self.w / "acme-backend"), self.bare_repo(self.w / "acme-client-app")
        kb = self.scaffold("--catalog-dir", self.w)
        self.assertEqual(kb, self.w / "acme-context")
        self.checkers_pass(kb)
        url = self.remote_folder("acme")
        code, out, err = self.py(WIRE, "--kb", kb, "--slug", "acme", "--url", url, "--self",
                                 "--commit", api, "--local", client)
        self.assertEqual(code, 0, out + err)
        settings = json.loads((api / ".claude" / "settings.json").read_text())
        self.assertEqual(settings["extraKnownMarketplaces"]["acme-context"]["source"]["url"], url)
        self.assertIn("tsh:project-context START", (api / "CLAUDE.md").read_text())
        self.assertEqual(self.git(client, "status", "--porcelain"), "", "client repository: git sees nothing")
        self.assertFalse((client / ".gitignore").exists(), "the client's .gitignore is never written")
        for repo in (api, client):
            code, kv, _, _ = self.locate(cwd=repo)
            self.assertEqual((code, kv["KB"], kv["BLOCK"], kv["READ_ACCESS"]), (0, str(kb), "ok", "granted"))

    def test_project_folder_end_to_end(self):
        """Jakub's layout: a new project folder, repo inside it, the PDFs beside."""
        self.w.mkdir()
        kb = self.scaffold("--parent", self.w)
        self.assertEqual(kb, self.w / "acme" / "acme-context")
        repo = self.bare_repo(self.w / "acme" / "repo-1")
        (self.w / "acme" / "brief.pdf").write_text("%PDF")
        self.checkers_pass(kb)
        self.assertEqual(self.py(WIRE, "--kb", kb, "--slug", "acme", "--url", self.remote_folder("acme"),
                                 "--commit", repo)[0], 0)
        code, kv, _, _ = self.locate(cwd=repo)
        self.assertEqual((code, kv["KB"]), (0, str(kb)))

    def test_lead_alone_no_repos_no_url_then_a_repo_then_the_url(self):
        self.w.mkdir()
        kb = self.scaffold("--parent", self.w)
        self.assertEqual(self.py(WIRE, "--kb", kb, "--slug", "acme", "--self")[0], 0, "no code repository")
        repo = self.bare_repo(self.w / "acme" / "acme-api")
        code, out, _ = self.py(WIRE, "--kb", kb, "--slug", "acme", "--commit", repo)
        self.assertIn("no URL yet", out)
        self.assertFalse((repo / ".claude" / "settings.json").exists(), "a local path is never committed")
        self.assertEqual(self.locate(cwd=repo)[1]["KB"], str(kb))
        url = self.remote_folder("acme")
        self.assertEqual(self.py(WIRE, "--kb", kb, "--slug", "acme", "--url", url, "--commit", repo)[0], 0)
        self.assertFalse((repo / "CLAUDE.local.md").exists(), "the local-path block is gone")
        local = json.loads((repo / ".claude" / "settings.local.json").read_text())
        self.assertNotIn("acme-context", local.get("extraKnownMarketplaces", {}))
        code, kv, _, _ = self.locate(cwd=repo)
        self.assertEqual((code, kv["WIRING"], kv["URL"]), (0, "commit", url))

    def test_teammate_joins_a_wired_repository(self):
        """The lead's wiring is committed; the teammate has their own HOME and a clone elsewhere."""
        self.w.mkdir()
        kb = self.scaffold("--catalog-dir", self.w)
        api = self.bare_repo(self.w / "acme-api")
        self.py(WIRE, "--kb", kb, "--slug", "acme", "--url", self.remote_folder("acme"), "--commit", api)
        mate_home = self.tmp / "mate"
        mate = dict(self.env, HOME=str(mate_home), TSH_CONTEXT_HOME=str(mate_home / ".tsh" / "context"))
        mate_api = mate_home / "code" / "api"
        shutil.copytree(api, mate_api)
        (mate_api / ".claude" / "settings.local.json").unlink()  # the lead's own, never committed
        code, _, cands, _ = self.locate(cwd=mate_api, env=mate)
        self.assertEqual((code, cands), (3, []), "asked once")
        theirs = shutil.copytree(kb, mate_home / ".tsh" / "context" / "acme")
        code, kv, _, _ = self.locate(cwd=mate_api, env=mate)
        self.assertEqual((code, kv["KB"]), (0, str(theirs)))

    def test_wrong_url_writes_nothing(self):
        self.w.mkdir()
        kb = self.scaffold("--catalog-dir", self.w)
        api = self.bare_repo(self.w / "acme-api")
        code, _, _ = self.py(WIRE, "--kb", kb, "--slug", "acme", "--url", str(self.tmp / "nope.git"), "--commit", api)
        self.assertEqual(code, 2)
        self.assertFalse((api / ".claude").exists())

    def test_knowledge_base_inside_a_client_repository_gets_its_own(self):
        client = self.bare_repo(self.w / "client-repo")
        (client / "secret.txt").write_text("client data\n")
        kb = client / "x-context"
        kb.mkdir()
        (kb / "a.md").write_text("# a\n")
        self.assertEqual(self.py(GITSTEPS, "remote", kb, self.remote_folder("x"))[0], 2)
        self.assertEqual(self.py(GITSTEPS, "first-push", kb, "--yes")[0], 2)
        self.assertEqual(self.py(GITSTEPS, "init", kb)[0], 0)
        self.assertEqual(subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=client, env=self.env,
                                        capture_output=True).returncode, 1, "no commit in the client repository")
        self.assertNotIn("secret.txt", self.git(kb, "ls-files"))


    def test_first_commit_carries_the_knowledge_bases_own_wiring(self):
        """The order N3 runs: --self before the first commit, so teammates get it and the
        lead's clone has no untracked file that would later block a pull."""
        self.w.mkdir()
        kb = self.scaffold("--catalog-dir", self.w)
        self.assertEqual(self.py(WIRE, "--kb", kb, "--slug", "acme", "--self")[0], 0)
        self.assertEqual(self.py(GITSTEPS, "init", kb)[0], 0)
        self.assertEqual(self.git(kb, "status", "--porcelain"), "", "nothing left outside the first commit")
        committed = json.loads(self.git(kb, "show", "HEAD:.claude/settings.json"))
        self.assertEqual(committed["extraKnownMarketplaces"]["acme-context"]["source"],
                         {"source": "directory", "path": "."}, "the same on every machine")
        self.py(WIRE, "--kb", kb, "--slug", "acme", "--self", "--commit", self.bare_repo(self.w / "acme-api"))
        self.assertEqual(self.git(kb, "status", "--porcelain"), "", "N5 re-wiring leaves the clone clean")


class WriteWorktree(InitHelpers):
    """Every git step of a write needs its own --yes, and each refusal below is decided
    before any network call — no test here fetches or pushes."""

    def setUp(self):
        super().setUp()
        self.w.mkdir()
        self.kb = self.scaffold("--catalog-dir", self.w)
        self.py(WIRE, "--kb", self.kb, "--slug", "acme", "--self")
        self.py(GITSTEPS, "init", self.kb)

    def worktree(self, branch, repo=None):
        """What `start --yes` leaves, made with plain git so no fetch is needed."""
        repo = repo or self.kb
        path = repo.parent / f"{repo.name}-worktrees" / branch.replace("/", "-")
        self.git(repo, "worktree", "add", "-q", "-b", branch, str(path))
        self.git(repo, "config", f"branch.{branch}.tshContextWrite", "true")
        return path

    def test_start_refuses_without_a_confirmed_proposal(self):
        self.assertEqual(self.py(WRITE, "start", self.kb, "Bad Name")[0], 2)
        self.assertEqual(self.py(WRITE, "start", self.kb, "docs/x", "--yes")[0], 2, "--yes needs --at")
        self.assertEqual(self.py(WRITE, "start", self.kb, "docs/x")[0], 3, "no remote: the exception")
        self.assertEqual(self.py(WRITE, "start", self.kb / "docs", "docs/x")[0], 2, "a subfolder of the clone")
        api = self.bare_repo(self.w / "acme-api")
        self.assertEqual(self.py(WRITE, "start", api, "docs/x")[0], 2, "a code repository")
        self.assertFalse((self.w / "acme-context-worktrees").exists())
        self.assertFalse((self.w / "acme-api-worktrees").exists())

    def test_commit_needs_a_yes_and_never_lands_in_a_published_clone(self):
        (self.kb / "docs" / "note.md").write_text("# Note\n")
        self.assertEqual(self.py(WRITE, "commit", self.kb, "--message", "docs: note")[0], 2, "no yes")
        self.assertEqual(self.py(WRITE, "commit", self.kb, "--message", "docs: note", "--yes")[0], 0,
                         "no remote yet: the knowledge base itself, after a yes")
        self.assertEqual(self.py(WRITE, "commit", self.kb, "--message", "again", "--yes")[0], 2, "nothing to commit")
        self.git(self.kb, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
        (self.kb / "docs" / "other.md").write_text("# Other\n")
        self.assertEqual(self.py(WRITE, "commit", self.kb, "--message", "docs: other", "--yes")[0], 2,
                         "a clone with a remote is the person's own: never committed to")

    def test_write_worktree_commits_and_push_refusals(self):
        w = self.worktree("docs/release-day")
        (w / "docs" / "release.md").write_text("# Release\n")
        code, out, _ = self.py(WRITE, "commit", w, "--message", "docs: release day", "--yes")
        self.assertEqual(code, 0)
        self.assertIn("docs: release day", out)
        self.assertEqual(self.py(WRITE, "push", w)[0], 2, "no yes")
        self.assertEqual(self.py(WRITE, "push", self.kb, "--yes")[0], 2, "the person's clone")
        (w / "docs" / "draft.md").write_text("# Draft\n")
        self.assertEqual(self.py(WRITE, "push", w, "--yes")[0], 2, "uncommitted changes")
        self.assertEqual(self.py(WRITE, "push", self.worktree("develop"), "--yes")[0], 2, "a default branch")
        stray = self.kb.parent / "elsewhere"
        self.git(self.kb, "worktree", "add", "-q", "-b", "docs/stray", str(stray))
        self.assertEqual(self.py(WRITE, "push", stray, "--yes")[0], 2, "not a write worktree")

    def test_a_worktree_of_another_repository_is_never_committed_or_pushed(self):
        api = self.bare_repo(self.w / "acme-api")
        (api / "README.md").write_text("code\n")
        self.git(api, "add", "README.md")
        self.git(api, "commit", "-qm", "code")
        theirs = self.worktree("feature/x", repo=api)
        (theirs / "secret.env").write_text("TOKEN=1\n")
        self.assertEqual(self.py(WRITE, "commit", theirs, "--message", "oops", "--yes")[0], 2)
        self.assertEqual(self.py(WRITE, "push", theirs, "--yes")[0], 2)
        unmarked = self.kb.parent / f"{self.kb.name}-worktrees" / "docs-unmarked"
        self.git(self.kb, "worktree", "add", "-q", "-b", "docs/unmarked", str(unmarked))
        (unmarked / "docs" / "x.md").write_text("# X\n")
        self.assertEqual(self.py(WRITE, "commit", unmarked, "--message", "x", "--yes")[0], 2,
                         "a worktree `start` did not make")

    def test_a_missing_message_never_swallows_the_yes(self):
        w = self.worktree("docs/msg")
        (w / "docs" / "m.md").write_text("# M\n")
        self.assertEqual(self.py(WRITE, "commit", w, "--message", "--yes")[0], 2)
        self.assertEqual(self.py(WRITE, "commit", w, "--yes", "--message")[0], 2)
        self.assertEqual(self.git(w, "rev-parse", "HEAD"), self.git(self.kb, "rev-parse", "HEAD"), "nothing committed")


class SyncMessages(unittest.TestCase):
    def test_a_failed_pull_names_its_cause(self):
        sys.path.insert(0, str(PLUGIN / "shared"))
        from sync_project_context import pull_warning
        code, message = pull_warning("error: The following untracked working tree files would be overwritten "
                                     "by merge:\n\t.claude/settings.json\nAborting")
        self.assertEqual(code, "blocked")
        self.assertIn(".claude/settings.json", message)
        self.assertEqual(pull_warning("fatal: Not possible to fast-forward, aborting.")[0], "diverged")
        self.assertEqual(pull_warning("ssh: connect to host bitbucket.org: timed out")[0], "offline")


class Checkers(InitHelpers):
    def setUp(self):
        super().setUp()
        self.w.mkdir()
        self.kb = self.scaffold("--catalog-dir", self.w)

    def run_check(self, script):
        return self.py(self.kb / "scripts" / script, cwd=self.kb)

    def test_two_people_take_the_same_decision_number(self):
        (self.kb / "docs" / "decisions" / "0001-use-postgres.md").write_text("# 0001: Use Postgres\n")
        self.assertEqual(self.run_check("check_decisions.py")[0], 0)
        (self.kb / "docs" / "decisions" / "0001-use-redis.md").write_text("# 0001: Use Redis\n")
        code, out, _ = self.run_check("check_decisions.py")
        self.assertEqual(code, 1)
        self.assertIn("DUPLICATE NUMBER 0001", out)

    def test_plugin_stays_markdown_only(self):
        plugin = self.kb / "plugins" / "acme-shared"
        (plugin / "skills" / "acme-release").mkdir(parents=True)
        skill = plugin / "skills" / "acme-release" / "SKILL.md"
        skill.write_text("---\nname: acme-release\ndescription: Release checklist.\n---\nSteps\n")
        self.assertEqual(self.run_check("check_plugin.py")[0], 0)
        skill.write_text("---\nname: acme-release\nallowed-tools: Bash(git *)\n---\n")
        self.assertIn("SHELL ACCESS", self.run_check("check_plugin.py")[1])
        skill.write_text("---\nname: acme-release\n---\n")
        (plugin / "hooks").mkdir()
        (plugin / "hooks" / "hooks.json").write_text("{}")
        self.assertIn("EXECUTABLE", self.run_check("check_plugin.py")[1])


# --- the guard on the CLAUDE.md block -------------------------------------------------

@unittest.skipUnless(shutil.which("node"), "node not installed")
class Hook(Base):
    """The guard script on its own; Claude Code's `if` filter is checked by hand."""

    def setUp(self):
        super().setUp()
        self.w.mkdir()
        self.md = self.w / "CLAUDE.md"
        self.block = BLOCK.format(url=self.url("acme"))
        self.md.write_text("# Repo\nfoo\n\n" + self.block + "\nbar\n")

    def guard(self, tool, path, **tool_input):
        payload = json.dumps({"tool_name": tool, "tool_input": dict(file_path=str(path), **tool_input)})
        r = subprocess.run(["node", str(GUARD)], input=payload, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return "deny" if '"deny"' in r.stdout else "allow"

    def test_edit_outside_block_allowed(self):
        self.assertEqual(self.guard("Edit", self.md, old_string="foo", new_string="baz"), "allow")

    def test_removing_or_editing_the_block_denied(self):
        self.assertEqual(self.guard("Edit", self.md, old_string=self.block, new_string=""), "deny")
        self.assertEqual(self.guard("Edit", self.md, old_string="Project knowledge", new_string="Knowledge"), "deny")
        self.assertEqual(self.guard("Write", self.md, content="# Repo\n"), "deny")

    def test_rewrite_that_keeps_the_block_allowed(self):
        self.assertEqual(self.guard("Write", self.md, content="# Short\n\n" + self.block), "allow")

    def test_local_file(self):
        local = self.w / "CLAUDE.local.md"
        local.write_text(self.block)
        self.assertEqual(self.guard("Edit", local, old_string="START", new_string="S"), "deny")

    def test_files_without_the_block_allowed(self):
        (self.w / "sub").mkdir()
        (self.w / "sub" / "CLAUDE.md").write_text("# Sub\n")
        self.assertEqual(self.guard("Write", self.w / "sub" / "CLAUDE.md", content=""), "allow")
        self.assertEqual(self.guard("Write", self.w / "notes.md", content=""), "allow")


if __name__ == "__main__":
    unittest.main()
