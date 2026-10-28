---
paths:
  - "plugins/tsh-product-management/shared/**"
  - "plugins/tsh-product-management/hooks/guard-project-context-block.mjs"
  - "plugins/tsh-product-management/hooks/hooks.json"
  - "plugins/tsh-product-management/skills/initializing-project-context/**"
  - "plugins/tsh-product-management/skills/navigating-project-context/**"
  - "plugins/tsh-product-management/skills/writing-project-knowledge/**"
  - "plugins/tsh-product-management/skills/adding-project-context-workspace/**"
  - "plugins/tsh-product-management/skills/repairing-project-context-links/**"
  - "tests/project-context/**"
---

# Project-context: the contract and its tests

The project-context skills run git on other people's clones and write into client
repositories, so their scripts carry a contract that prose alone cannot keep. **After
any change to a file this rule covers, run both and show them passing before you report
the work done** — CI runs them too, in the `project-context-tests` job of
`.github/workflows/quality.yml`, on the latest Python 3:

```shell
python3 tests/project-context/test_project_context.py
python3 plugins/tsh-product-management/skills/initializing-project-context/tests/smoke_test.py --with-claude
```

They test **structure**: in both folder layouts — flat (`proj-context` beside
`proj-backend`) and a project folder (`project/context-repo` beside `project/repo-1`) —
for the lead's init, a teammate joining, a T3 worktree and a client repository, the
knowledge base is set up and found. They need only `git`, a current `python3` and `node`.
**They never talk to a git server**: code repositories are local `git init` folders, a
URL that must be reachable is a local `--bare` folder, the git config has a fake
identity and no credential helper, and the SSH agent is removed. Keep it that way — no
test clones, fetches, pulls or pushes, and none touches `~/.tsh`, `~/.claude` or a real
repository.

A red test is a broken contract until proven otherwise: fix the code, or — when the
behaviour is meant to change — change the test in the same change and say what moved.

## The contract

| Never | Only |
| --- | --- |
| merge, rebase, stash, reset or switch branch in a person's clone | `pull --ff-only` of a clean default branch, through `sync_project_context.py` |
| create a branch or worktree, commit, or push without that step's own yes | `write_worktree.py start --yes --at <sha>`, `commit --yes`, `push --yes`, each after its own answer; the first push of a new knowledge base after `--yes`, to an empty remote |
| push the default branch, force-push, delete a branch or a worktree | — |
| commit in a person's clone | only a write worktree; the knowledge base itself only while it has no remote |
| commit, stage, or touch `.gitignore` in a code repository | files written for the person to commit (commit mode), or kept out of git through `.git/info/exclude` (local mode) |
| act on a repository that encloses the knowledge base | the knowledge base's own repository |
| remove or edit the `tsh:project-context` block through an agent | `wire_repos.py` writes and replaces it |

The rows that move data over the network — the sync's pull, the write worktree's push,
the first push — are deliberately not tested automatically; their refusals are, because
each is decided before any network call. A change to
`sync_project_context.py`, `write_worktree.py` or `context_repo_git.py` needs a reviewer
who checks it against this table, line by line, and a manual run on a scratch repository.

## What the tests cannot see

Check these by hand when a change touches them, and say so in the pull request:

- The hook's `if` filter is evaluated by Claude Code, not by the tests: after changing
  `hooks.json`, run `claude -p` with `--plugin-dir plugins/tsh-product-management` in a
  scratch repository and confirm an edit that removes the block is denied and an edit of
  another file never starts the hook.
- `wire_repos.py --register` calls the `claude` CLI and is not exercised by the tests.
- Trust dialogs, `autoUpdate` and a real private host (SSH, HTTPS app password) need an
  interactive session.
