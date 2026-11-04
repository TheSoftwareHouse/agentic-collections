---
title: Managing Git Worktrees
sidebar_label: managing-git-worktrees
sidebar_position: 5
description: Creates a Git worktree from a freshly fetched base branch on origin, lists registered worktrees read-only, and removes one precisely identified worktree.
sources:
  - plugins/tsh-core/skills/managing-git-worktrees/
sources_hash: "40bc6673c10738813bb35b1b8c653e6fd32dcbdc2bc95d85a20d56a1c2d4a5fe"
---

# Managing Git Worktrees

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:managing-git-worktrees` (also loaded automatically when a request matches its description)  
**Used by:** no other skill or agent references it

Handles the Git worktree lifecycle inside the current repository: create, list and remove. Every operation stays within the current Git root and requires no environment setup. The skill covers plain Git lifecycle operations only; it does not prepare a checkout for running, so it never touches environment files, Compose services or credentials.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Create** | Builds a worktree from a branch that exists on `origin`, freshly fetched into `refs/remotes/origin/<base_branch>` with an explicit refspec and resolved to an explicit `base_commit`. The worktree is created with `--no-track` |
| **Base branch** | Resolved by precedence: the branch the user named, then origin's own default branch read with `git ls-remote --symref origin HEAD` (so `main`, `master` and `develop` trunks all work), then stop and ask. It never assumes `main` |
| **Two confirmations** | Create takes two separate literal confirmations: one authorizing local creation and one authorizing the first push. Both name the base branch, and say when it was detected rather than user-supplied |
| **Conflict checks** | Before anything is created, rejects a branch name already used by a registered worktree, a local branch or a remote branch, and a path that already exists, is registered, or sits inside the repository root |
| **List** | Runs `git worktree list --porcelain` and reports each worktree's path, `HEAD`, branch or detached state, and any `locked` or `prunable` indicator. It changes nothing |
| **Remove** | Resolves exactly one target by exact absolute path or exact branch name, refuses unsafe targets, asks for a literal confirmation, removes without force, and verifies with a fresh porcelain list |
| **Branch cleanup** | Asked as a separate question after a successful removal, and never implied. Uses `git branch -d`, and preserves the branch when Git refuses because it is unmerged |

## How It Works

1. **Identify the request type:** create, list or remove. Anything else is an unsupported request: the skill summarises the supported operations and proposes bounded extensions only if the user wants them developed.
2. **Create.** Resolve the active and canonical roots, confirm the branch name, propose or accept a sibling path derived from the canonical root and the new branch slug, resolve and fetch the base, check conflicts, confirm, create, verify, return the `cd` command, then confirm separately and publish with `git push --set-upstream origin <branch>`.
3. **List.** Run the porcelain list from the repository root and report it. If the command fails, stop and report the failure instead of attempting recovery.
4. **Remove.** Read the refusal list before running any command; removal is destructive.

## Rules It Enforces

| Rule | Why |
| :-- | :-- |
| The base is only ever a branch on `origin` | Tags, commit SHAs, local-only branches and other remotes' branches are rejected, not worked around |
| Never fall back to a local branch, `HEAD` or the current feature branch when a fetch fails | Stop instead of substituting a different base |
| Never use `git worktree remove --force`, `git push --force` or `git branch -D` | Force behavior is unsupported |
| Never remove the active worktree, the main worktree, a locked or prunable target, or a target with tracked modifications or untracked files | The refusal list is exhaustive |
| Pass branch, base branch, path and commit as separate shell arguments | Values are untrusted and are never concatenated into a raw command string |
| Report a controlled failure on any verification failure | An unverified success is never reported |

## What It Does Not Do

- Initialize Docker or Compose services, environment files or credentials.
- Act outside the current Git root or on another repository.
- Run arbitrary Git operations outside the approved workflow, or delete branches automatically.

## Reference Files

| Reference | Load when |
| :-- | :-- |
| `creating-a-worktree.md` | The request is to create a worktree, whether or not a base branch was named |
| `removing-a-worktree.md` | The request is to remove or clean up an existing worktree |

## Source

- [`plugins/tsh-core/skills/managing-git-worktrees/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/managing-git-worktrees/SKILL.md)
- [`plugins/tsh-core/skills/managing-git-worktrees/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-core/skills/managing-git-worktrees/references)
