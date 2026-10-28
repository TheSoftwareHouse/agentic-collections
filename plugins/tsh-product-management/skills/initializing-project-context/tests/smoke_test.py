#!/usr/bin/env python3
"""Smoke test for initializing-project-context: the edge cases a first run in an
empty folder never meets, each found once by running the scaffold by hand.

    python3 tests/smoke_test.py                 # files only, ~5 s
    python3 tests/smoke_test.py --with-claude   # also `claude plugin validate`

Everything happens in a temporary directory that is deleted afterwards. The
fixtures `git init` throwaway folders there to stand in for code repositories —
the scaffold itself never runs git. Nothing is registered with Claude Code:
wire_repos.py runs without --register, so the settings merge is tested and the
user's plugin state is left alone.

Exit 0 when every check passes, 1 otherwise.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
LOCATOR = SKILL.parents[1] / "shared" / "locate_project_context.py"

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'✔' if ok else '✘'} {name}" + (f" — {detail}" if detail and not ok else ""))


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def py(script, *args, cwd=None):
    return run([sys.executable, str(script), *map(str, args)], cwd=cwd)


def scaffold(*args, cwd=None):
    return py(SCRIPTS / "scaffold.py", "--name", "Acme Portal", "--owner-tbd", *args, cwd=cwd)


def probe(path):
    code, out = py(SCRIPTS / "probe.py", path)
    return json.loads(out) if code == 0 else {}


def git_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q"], cwd=path)
    return path


def gates(context):
    if not (context / "scripts").is_dir():
        missing = (1, f"{context} was not created")
        return missing, missing
    links = py(context / "scripts" / "check_links.py", cwd=context)
    tables = py(context / "scripts" / "check_tables.py", cwd=context)
    return links, tables


def knowledge_plugin():
    spec = importlib.util.spec_from_file_location("wire_repos", SCRIPTS / "wire_repos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.KNOWLEDGE_PLUGIN


def generated_leftovers(root):
    bad = []
    for f in root.rglob("*"):
        if "__SLUG__" in f.name or f.suffix == ".tmpl":
            bad.append(f.name)
        elif f.is_file() and f.suffix in {".md", ".json", ".py"} and "{{" in f.read_text(encoding="utf-8"):
            bad.append(f.relative_to(root).as_posix())
    return bad


def main():
    with_claude = "--with-claude" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="pctx-smoke-")).resolve()
    try:
        print("1. Empty folder, new catalog")
        code, out = scaffold("--slug", "acme", "--parent", tmp / "empty", cwd=tmp)
        ctx = tmp / "empty" / "acme" / "acme-context"
        check("scaffold exits 0", code == 0, out[-300:])
        check("context repository created", (ctx / "docs" / "README.md").is_file())
        check("no placeholder, __SLUG__ or .tmpl left", not generated_leftovers(ctx.parent),
              ", ".join(generated_leftovers(ctx.parent))[:300])
        plugin = ctx / "plugins" / "acme-shared"
        check("generated plugin ships no skill", not (plugin / "skills").exists()
              and not (plugin / "shared").exists())
        links, tables = gates(ctx)
        check("check_links.py passes", links[0] == 0, links[1][-300:])
        check("check_tables.py passes", tables[0] == 0, tables[1][-300:])
        check("checker scripts are executable",
              all((ctx / "scripts" / s).stat().st_mode & 0o111 for s in ("check_links.py", "check_tables.py")))
        code, out = scaffold("--slug", "acme", "--parent", tmp / "empty", cwd=tmp)
        check("second run creates nothing", code == 0 and "Created (0)" in out, out[-200:])
        if with_claude:
            for target in (ctx, plugin):
                code, out = run(["claude", "plugin", "validate", str(target)])
                check(f"claude plugin validate {target.name}", code == 0, out[-300:])

        print("2. Existing folder with code repositories is the catalog")
        cat = tmp / "brownfield"
        git_repo(cat / "api")
        git_repo(cat / "web")
        (cat / "web" / ".claude").mkdir()
        (cat / "web" / ".claude" / "settings.json").write_text(json.dumps(
            {"model": "keep-me", "enabledPlugins": {knowledge_plugin(): False}}))
        p = probe(cat)
        check("probe: can_be_catalog", p.get("can_be_catalog") is True)
        check("probe: siblings are the code repositories", p.get("siblings") == ["api", "web"], str(p.get("siblings")))
        code, out = scaffold("--slug", "acme", "--catalog-dir", cat, cwd=cat)
        check("scaffold exits 0", code == 0, out[-300:])
        check("context repository beside the code repositories", (cat / "acme-context" / "docs").is_dir())
        code, out = py(SCRIPTS / "wire_repos.py", "--catalog", cat, "--slug", "acme", "--only", "api", "web")
        check("wire_repos exits 0", code == 0, out[-300:])
        api = json.loads((cat / "api" / ".claude" / "settings.json").read_text())
        check("code repository: relative marketplace path",
              api["extraKnownMarketplaces"]["acme-context"]["source"]["path"] == "../acme-context")
        check("code repository: both plugins enabled",
              api["enabledPlugins"].get("acme-shared@acme-context") is True
              and api["enabledPlugins"].get(knowledge_plugin()) is True)
        self_ = json.loads((cat / "acme-context" / ".claude" / "settings.json").read_text())
        check("context repository refers to itself with '.'",
              self_["extraKnownMarketplaces"]["acme-context"]["source"]["path"] == ".")
        web = json.loads((cat / "web" / ".claude" / "settings.json").read_text())
        check("existing settings key preserved", web.get("model") == "keep-me")
        check("an existing `false` for the knowledge plugin is not flipped",
              web["enabledPlugins"][knowledge_plugin()] is False)

        print("3. Started inside a code repository")
        repo = git_repo(tmp / "projects-x" / "service")
        p = probe(repo)
        check("probe: cannot be the catalog", p.get("can_be_catalog") is False)
        check("probe: parent is usable", p.get("parent_is_git_repo") is False and p.get("parent_writable") is True)
        check("probe: parent_siblings include this repository", "service" in (p.get("parent_siblings") or []))

        print("4. Folder name that is not kebab-case")
        odd = tmp / "My_Project"
        odd.mkdir()
        p = probe(odd)
        check("probe: folder_name_is_slug is false", p.get("folder_name_is_slug") is False)
        check("probe: folder_slug is my-project", p.get("folder_slug") == "my-project", str(p.get("folder_slug")))
        code, out = scaffold("--slug", "my-project", "--catalog-dir", odd, cwd=odd)
        check("scaffold exits 0 and the folder keeps its name",
              code == 0 and (odd / "my-project-context" / "docs").is_dir(), out[-300:])
        code, _ = scaffold("--slug", "My Project", "--parent", tmp / "bad-slug", cwd=tmp)
        check("a non-kebab --slug is rejected with exit 2", code == 2)

        print("5. Layers typed in through Other")
        code, out = scaffold("--slug", "lay", "--parent", tmp / "layers",
                             "--layers", "data-pipelines", "qa", "quality", "mobile", cwd=tmp)
        lctx = tmp / "layers" / "lay" / "lay-context"
        amap = (lctx / "docs" / "README.md").read_text() if lctx.exists() else ""
        check("scaffold exits 0", code == 0, out[-300:])
        check("custom layer gets a workspace", (lctx / "docs" / "data-pipelines" / "CLAUDE.md").is_file())
        check("custom layer gets an area-map row", "(data-pipelines/README.md)" in amap)
        check("optional layer from its own template", (lctx / "docs" / "mobile" / "README.md").is_file())
        check("exact name of an always-created workspace: one row, not two",
              amap.count("(quality/README.md)") == 1)
        check("synonym is reported", "'qa' overlaps 'quality'" in out)
        links, tables = gates(lctx)
        check("gates pass with custom layers", links[0] == 0 and tables[0] == 0, (links[1] + tables[1])[-300:])
        code, _ = scaffold("--slug", "lay2", "--parent", tmp / "layers2", "--layers", "Bad_Layer", cwd=tmp)
        check("a non-kebab layer is rejected with exit 2", code == 2)

        print("6. The quality gate on an empty corpus")
        empty = git_repo(tmp / "empty-gate")
        (empty / "scripts").mkdir()
        for s in ("check_links.py", "check_tables.py"):
            shutil.copy(ctx / "scripts" / s, empty / "scripts" / s)
        for s in ("check_links.py", "check_tables.py"):
            code, out = py(empty / "scripts" / s, cwd=empty)
            check(f"{s} fails with nothing to check", code == 1 and "nothing to check" in out, out[-200:])
        fresh = tmp / "fresh-git"
        shutil.copytree(ctx, fresh)
        run(["git", "init", "-q"], cwd=fresh)
        code, out = py(fresh / "scripts" / "check_links.py", cwd=fresh)
        check("after git init with nothing committed: warns, walks the tree, passes",
              code == 0 and "no tracked files yet" in out, out[-300:])

        print("7. Locating the knowledge base")
        (cat / "api" / "src" / "deep").mkdir(parents=True)
        for where in (cat, cat / "acme-context", cat / "acme-context" / "docs" / "backend",
                      cat / "api", cat / "api" / "src" / "deep"):
            code, out = py(LOCATOR, where)
            check(f"from {where.relative_to(tmp)}",
                  code == 0 and f"KB={cat / 'acme-context'}" in out and "SLUG=acme" in out, out[-200:])
        code, _ = py(LOCATOR, tmp / "projects-x")
        check("nothing found: exit 1", code == 1)
        two = tmp / "two"
        for n in ("a-context", "b-context"):
            shutil.copytree(ctx, two / n)
        code, out = py(LOCATOR, two)
        check("two candidates: exit 2, both listed", code == 2 and "a-context" in out and "b-context" in out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} passed" + (f", {failed} FAILED" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
