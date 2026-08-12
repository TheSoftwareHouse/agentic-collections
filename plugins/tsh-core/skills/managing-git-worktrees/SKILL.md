---
name: managing-git-worktrees
description: "Manages Git worktree lifecycle requests by creating a worktree from a freshly fetched base branch on origin — any branch, defaulting to origin's own default branch — listing registered worktrees, and removing a precisely identified worktree. Use when the user asks for worktree creation, listing, removal, or safe Git worktree lifecycle guidance."
when_to_use: "Trigger on: creating a worktree for a new branch, spinning up a parallel checkout, `git worktree add`, basing a worktree on a specific branch such as `develop`, a release branch, or another feature branch, listing or inspecting existing worktrees, cleaning up or removing a worktree, deleting the branch left behind by a removed worktree, or any request to run a Git worktree operation safely."
---

# Managing Git Worktrees

Handles the Git worktree lifecycle inside the current repository without guessing
beyond the supported operations: create, list, and remove. Every operation stays
within the current Git root and requires no environment setup.

This skill covers **plain Git lifecycle operations only**. It does not prepare a
checkout for running.

## When to Use

- Creating a worktree so a new branch can be worked on in parallel with the current one
- Inspecting which worktrees exist, where they live, and what state they are in
- Removing a worktree that is finished with, and deciding separately about its branch
- Any request to run `git worktree` where getting it wrong would cost work

## Supported Scope

This skill supports exactly three operations:

1. Create a new worktree from a freshly fetched base branch on `origin`.
2. List existing worktrees in a read-only, inspectable format.
3. Remove one precisely identified worktree after explicit confirmation.

The base may be **any branch that exists on `origin`**, feature branches included.
Resolve it by precedence and stop at the first that succeeds:

1. The base branch the user named.
2. Origin's own default branch, read from the remote with
   `git ls-remote --symref origin HEAD` — so `main`, `master`, and `develop` trunks
   all work.
3. Neither resolved — stop and ask which branch to base on. Never assume `main`.

## Explicit Exclusions

This skill does not:

- initialize Docker/Compose services, environment files, or credentials
- perform environment initialization or post-create setup
- read or mutate state across unrelated checkouts or repositories
- run arbitrary Git operations outside the approved workflow
- use force deletion or automatic branch cleanup
- act outside the current Git root or on another repository
- perform arbitrary filesystem or Git workflows that belong elsewhere

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Create only from a branch that exists on `origin`, freshly fetched into `refs/remotes/origin/<base_branch>` with an explicit refspec and resolved to an explicit `base_commit`. |
| NEVER | Use anything but a branch on `origin` as the base — not a tag, a commit SHA, a local-only branch, or another remote's branch. |
| NEVER | Infer the default base from local state — `refs/remotes/origin/HEAD` may be stale or absent, and `init.defaultBranch` describes this machine, not this remote. Ask the remote with `git ls-remote --symref origin HEAD`. |
| NEVER | Fall back to a local branch, `HEAD`, or the current feature branch when the fetch or ref resolution fails, and never substitute a different base when the requested one is missing. Stop instead. |
| NEVER | Adopt an existing remote branch. `git ls-remote --exit-code --heads` exit status `2` is the only acceptable absence; `0` must cause rejection; anything else is fatal. |
| MUST | Take two separate literal confirmations for create — one authorizing local creation, one authorizing the first push. Neither substitutes for the other. |
| MUST | Name the base branch in both confirmations, never a bare commit, and disclose when it was detected rather than user-supplied. |
| NEVER | Use `git worktree remove --force`, `git push --force`, or `git branch -D`. Force behavior is unsupported here. |
| MUST | Resolve exactly one removal target by exact absolute path or exact branch name. Stop on zero matches, multiple matches, or any ambiguity. |
| NEVER | Remove the active worktree, the main worktree, a locked target, a prunable target, or a target with tracked modifications or untracked files. |
| NEVER | Act outside the current Git root, or on another repository. |
| MUST | Pass branch, base branch, path, and commit as separate shell arguments. Never concatenate them into a raw command string, and shell-quote them in any user-facing output. |
| MUST | Stop and report a controlled failure on any verification failure. Never report an unverified success. |
| NEVER | Touch environment files, Compose services, or credentials. That is outside this skill entirely. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Creating a worktree](./references/creating-a-worktree.md) | The request is to create, add, or set up a new worktree, whether or not a base branch was named | Root resolution, branch and path confirmation, base-branch resolution and fetching, conflict checks, `--no-track` creation, verification, and the separate publish step |
| [Removing a worktree](./references/removing-a-worktree.md) | The request is to remove, delete, or clean up an existing worktree | Target resolution, refused targets, cleanliness checks, confirmation, safe removal, verification, and the separate branch-deletion question |

## Procedure

**Step 1 — Identify the request type:** create, list, or remove. If it is none of
those three, go to [Unsupported Requests](#unsupported-requests). Do not guess.

**Step 2 — Create.** Read
[`creating-a-worktree.md`](./references/creating-a-worktree.md) **before running
any command** — the ordering of base resolution, fetch, conflict checks, and the
two confirmations is what makes this safe, and it is not reconstructible from the
rules table alone.

**Step 3 — List.** The full workflow, inline:

1. Run `git worktree list --porcelain` from the repository root. Treat the output
   as the authoritative, read-only source for the current state.
2. Parse each entry and report its absolute path, `HEAD`, branch name or detached
   state, and any `locked` or `prunable` indicator present.
3. Change nothing. Do not prune, clean, or remove. If the command fails, stop and
   report the failure instead of attempting recovery.

**Step 4 — Remove.** Read
[`removing-a-worktree.md`](./references/removing-a-worktree.md) **before running
any command**. Removal is destructive and the refused-target list is exhaustive
for a reason.

## Unsupported Requests

If the request is outside create, list, or remove, do not guess or emit an
arbitrary Git command. Respond with a concise summary of the supported operations
and propose bounded future extensions only if the user wants them developed.

Suggested future extensions are limited to:

- alternate base refs such as a tag or an explicit commit
- remotes other than `origin` as the base
- move, lock, or unlock operations for a specific worktree
- prune or stale metadata inspection
- status or divergence inspection for a worktree
- explicit force controls for removal or branch cleanup
- batch cleanup for multiple matching worktrees

Ask whether the user wants the unsupported capability developed. If they do, state
that any extension would need explicit scope, exact-target review, confirmations,
safe argument handling, and post-mutation verification. For force or batch
behavior, require stronger warnings and an extra confirmation step before
proceeding.
