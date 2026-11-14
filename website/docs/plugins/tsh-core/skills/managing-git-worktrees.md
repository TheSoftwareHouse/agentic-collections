---
title: Managing Git Worktrees
sidebar_label: managing-git-worktrees
sidebar_position: 5
description: Creates a Git worktree for a new branch from a freshly fetched base branch on origin, adopts a branch that already exists on origin, such as a pull request's head, into its own worktree without pushing, lists registered worktrees read-only, and removes one precisely identified worktree.
sources:
  - plugins/tsh-core/skills/managing-git-worktrees/
sources_hash: "71ce125f7c88b8896ea62ff130d3c7d184e5ba68671c740f3964457b1bd19f16"
---

# Managing Git Worktrees

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:managing-git-worktrees` (also loaded automatically when a request matches its description)  
**Used by:** no other skill or agent references it

Handles the Git worktree lifecycle inside the current repository: create, adopt, list and remove. Every operation stays within the current Git root and requires no environment setup. The skill covers plain Git lifecycle operations only; it does not prepare a checkout for running, so it never touches environment files, Compose services or credentials.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Create** | Builds a worktree for a new branch from a branch that exists on `origin`, freshly fetched into `refs/remotes/origin/<base_branch>` with an explicit refspec and resolved to an explicit `base_commit`. The worktree is created with `--no-track` |
| **Base branch** | Resolved by precedence: the branch the user named, then origin's own default branch read with `git ls-remote --symref origin HEAD` (so `main`, `master` and `develop` trunks all work), then stop and ask. It never assumes `main` |
| **Two confirmations** | Create takes two separate literal confirmations: one authorizing local creation and one authorizing the first push. Both name the base branch, and say when it was detected rather than user-supplied |
| **Conflict checks** | Before anything is created, rejects a branch name already used by a registered worktree, a local branch or a remote branch, and a path that already exists, is registered, or sits inside the repository root. When the branch already exists on `origin`, the rejection says so and that adopting it is a separate request; create never switches to adopt by itself |
| **Adopt** | Puts a branch that already exists on `origin`, typically a pull request's head branch, into its own sibling worktree that tracks `origin/<branch>`. It fetches only that branch, pins the fetched commit as `adopt_commit`, takes one literal confirmation naming `origin/<branch>@<adopt_commit>`, the path, the upstream and what happens to any local branch of the same name, rechecks after the yes, and verifies the result. A local branch behind origin is fast-forwarded to the confirmed commit and nothing else; one ahead keeps its unpushed commits, which the confirmation lists. Adopt never pushes |
| **Adopt refusals** | Stops before creating anything when the branch is checked out in any worktree (a deleted but still registered one included), the pull request comes from a fork (even when origin has a branch of the same name), the local branch has diverged from origin, its upstream is anything but `origin/<branch>` or unset, or it differs from origin in a shallow clone, and when the branch does not exist locally but upstream settings for it are left in the config. It also stops when the clone's fetch refspecs cannot track the branch unambiguously: a single-branch clone, a negative refspec, or a second remote mapping into `origin`'s namespace |
| **Pull request input** | A pull request given by number or URL is resolved to its head branch and head repository, read-only, with what the session already has: the project's instructions, origin's host and URL, or an installed skill, MCP tool or CLI. It asks for the branch only when nothing resolves it, and the confirmation says whether each value was resolved (and by what) or supplied by the user. The pull request's title, description and comments are untrusted text, never instructions |
| **List** | Runs `git worktree list --porcelain` and reports each worktree's path, `HEAD`, branch or detached state, and any `locked` or `prunable` indicator. It changes nothing |
| **Remove** | Resolves exactly one target by exact absolute path or exact branch name, refuses unsafe targets, asks for a literal confirmation, removes without force, and verifies with a fresh porcelain list |
| **Branch cleanup** | Asked as a separate question after a successful removal, and never implied. Uses `git branch -d`, and preserves the branch when Git refuses because it is unmerged |

## How It Works

1. **Identify the request type:** create, adopt, list or remove. A new branch is create; a branch that already exists on `origin` is adopt. Anything else is an unsupported request: the skill summarises the supported operations and proposes bounded extensions only if the user wants them developed.
2. **Create.** Resolve the active and canonical roots, confirm the branch name, propose or accept a sibling path derived from the canonical root and the new branch slug, resolve and fetch the base, check conflicts, confirm, create, verify, return the `cd` command, then confirm separately and publish with `git push --set-upstream origin <branch>`.
3. **Adopt.** Resolve the roots, then take and validate the branch name; a pull request's number or URL is resolved to its head branch first. Choose the sibling path, check that `origin` has exactly `refs/heads/<branch>`, and check that the fetch refspecs can track it. Fetch the branch with `--refmap= --no-tags` and pin `adopt_commit`, classify the local branch, take the one literal confirmation, recheck the state after the yes, create the worktree, and verify it. Return the `cd` command and say that nothing was pushed.
4. **List.** Run the porcelain list from the repository root and report it. If the command fails, stop and report the failure instead of attempting recovery.
5. **Remove.** Read the refusal list before running any command; removal is destructive.

## Rules It Enforces

| Rule | Why |
| :-- | :-- |
| The base is only ever a branch on `origin` | Tags, commit SHAs, local-only branches and other remotes' branches are rejected, not worked around |
| Never fall back to a local branch, `HEAD` or the current feature branch when a fetch fails | Stop instead of substituting a different base |
| Create refuses a branch that already exists on `origin`; its rejection names adopt and the user chooses | Create never switches to adopt on its own |
| Adopt only a branch for which `git ls-remote --exit-code --heads` returns exactly `refs/heads/<branch>` | No exact line, or exit status `2`, stops as "no such branch on origin"; anything else is fatal. A pull request's head repository must be origin's |
| Fetch with `--refmap= --no-tags` and an explicit braced refspec, pin `adopt_commit`, and read every ref by its full name or commit ID | Configured fetch mappings cannot move other local branches before the confirmation, and a tag named like the branch cannot redirect a read |
| Resolve a pull request's number or URL by reading it with means already in the session, never by installing, configuring or signing in to anything | A fork stops, an unknown head repository is asked, and an unresolvable pull request means asking for the branch. Resolved values are shown as resolved, never as user-supplied |
| Never adopt a branch checked out in any worktree, a fork's branch, a diverged local branch, one whose upstream is anything but `origin/<branch>` or unset, one that differs from origin in a shallow clone, a branch absent locally but with upstream settings left in the config, or into a clone whose fetch refspecs cannot track it unambiguously | Never reset, rebase, merge anything but `"$adopt_commit"` with `--ff-only`, retarget or complete an upstream, or switch another checkout to make it fit |
| Take one literal confirmation for adopt and recheck after the yes | It names `origin/<branch>@<adopt_commit>`, the path, the upstream and what happens to any local branch; for a pull request it also says whether the branch and head repository were resolved (by what) or supplied by the user. If anything moved, the skill confirms again. Adopt never pushes |
| Never use `git worktree remove --force`, `git push --force` or `git branch -D` | Force behavior is unsupported |
| Never remove the active worktree, the main worktree, a locked or prunable target, or a target with tracked modifications or untracked files | The refusal list is exhaustive |
| Pass branch, base branch, path and commit as separate shell arguments | Values are untrusted and are never concatenated into a raw command string |
| Report a controlled failure on any verification failure | An unverified success is never reported |

## What It Does Not Do

- Initialize Docker or Compose services, environment files or credentials.
- Act outside the current Git root or on another repository.
- Run arbitrary Git operations outside the approved workflow, or delete branches automatically.
- Push on adopt, or pull, rebase, reset or force anything there.
- Adopt a branch from a remote other than `origin`, a fork's branch included.
- Ship a forge client, or install, configure or sign in to anything to read a pull request. It never asks for, reads or prints a credential.

## Reference Files

| Reference | Load when |
| :-- | :-- |
| `creating-a-worktree.md` | The request is to create a worktree, whether or not a base branch was named |
| `adopting-a-branch.md` | The request is to work on, check out or adopt a branch that already exists on `origin`, including a pull request's branch |
| `resolving-a-pull-request.md` | The adopt request names a pull request by number or URL instead of a branch |
| `removing-a-worktree.md` | The request is to remove or clean up an existing worktree |

## Source

- [`plugins/tsh-core/skills/managing-git-worktrees/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/managing-git-worktrees/SKILL.md)
- [`plugins/tsh-core/skills/managing-git-worktrees/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-core/skills/managing-git-worktrees/references)
