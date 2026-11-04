---
title: Writing Project Knowledge
sidebar_label: Writing Project Knowledge
sidebar_position: 22
description: Adds or updates a document in a project's knowledge base on its own branch, in the owning workspace, with the index updated and the reviewing owner named.
sources:
  - plugins/tsh-product-management/skills/writing-project-knowledge/
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/shared/locate_project_context.py
  - plugins/tsh-product-management/shared/sync_project_context.py
  - plugins/tsh-product-management/shared/write_worktree.py
sources_hash: "1533348283b1a4ccf59dd3a6768e2e07572ad0030de832d6b14d31305544751a"
---

# Writing Project Knowledge

**Plugin:** [TSH Product Management](/docs/plugins/tsh-product-management/)  
**Invoke:** `/tsh-product-management:writing-project-knowledge` (also model-invocable: it routes on "write this down", "document this", "update the doc on X" in a project with a `*-context` repository)  
**Used by:** [Navigating Project Context](/docs/plugins/tsh-product-management/skills/navigating-project-context) names it as the only route for changing the knowledge base from work in a code repository. No agent loads it.

Writes into the project's knowledge base under the rules of the workspace that owns the topic. The failure it prevents is a second document saying something different: knowledge added beside the existing document instead of into it.

## When it applies

- Recording a requirement, constraint, integration detail or process change.
- Correcting a document that no longer matches reality.
- A workshop or call that produced knowledge worth keeping.

## What it covers

| Area                  | Coverage                                                                                                                                                                                                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Isolated write**    | Every change is made in a separate worktree on a new branch `docs/<topic>`, beside the person's clone. The person's clone is never edited, whatever branch it is on, except for a knowledge base with no remote yet (see The branch flow)                                                   |
| **Owning workspace**  | Reads `docs/README.md`, picks the one workspace whose scope covers the topic, then reads that workspace's `CLAUDE.md` for its owner and rules. When two fit, it chooses the one that owns the outcome and says which it rejected                                                            |
| **Update, don't add** | Reads the workspace `README.md` and the documents it names first. Updating a document in place beats adding another; a file is created only when nothing covers the topic                                                                                                                   |
| **State of today**    | Present tense, current state, no history; history lives in version control. A document the change makes wrong is fixed in the same change, deleted, or given a `DEPRECATED` banner with a pointer to the successor                                                                          |
| **Index**             | The entry in the workspace `README.md` is added or adjusted in the same change; a document nothing links to will not be found                                                                                                                                                               |
| **Checks**            | `scripts/check_links.py` and `scripts/check_tables.py` run from the worktree until clean                                                                                                                                                                                                    |
| **Review**            | The report names the workspace, the files, the branch, and the owner from that workspace's `CLAUDE.md` who reviews it. The change reaches everyone only after the pull request is merged                                                                                                    |
| **Decisions**         | Never recorded here. A choice with alternatives goes to [Managing Decision Records](/docs/plugins/tsh-core/skills/managing-decision-records) with the worktree's `docs/decisions/` as the archive, never a code repository's own folder. This skill never sets or changes a record's status |

The deprecation banner, placed under the document's title:

```markdown
> **DEPRECATED (YYYY-MM-DD).** <Why this no longer describes the current state.>
> Current state: [<successor>](path).
```

## How it works

1. **Locate the knowledge base and open a branch.** Resolve and sync KB through the shared guide, propose the branch with `write_worktree.py start`, and create it only after the person answers `Create`. The worktree is called W; everything is read and written under W.
2. **Find the owning workspace** in `W/docs/README.md`, then read its `CLAUDE.md`. Its rules outrank this skill.
3. **Look for the document that already exists.**
4. **Write it**, in kebab-case filenames, linking only to files that exist in the repository. Fix or banner anything the change contradicts.
5. **Update the index** in the workspace `README.md`.
6. **Verify, then commit and push only on a yes**: both checkers, then the `Commit` and `Push` questions.

The skill never invents a fact to fill a gap: it writes what is known and names the gap as a gap.

## The branch flow

Shared by [Adding a Project-Context Workspace](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace) and [Repairing Project-Context Links](/docs/plugins/tsh-product-management/skills/repairing-project-context-links). Each git step runs only after its own yes; one yes never covers another step. Every question names where the change lands and whether it stays on this machine.

| Step            | Script call                                 | Question and effect                                                                                                                                                                                                   |
| --------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Propose         | `write_worktree.py start <KB> docs/<topic>` | Changes nothing; prints the proposed worktree, branch, base, base commit and remote                                                                                                                                   |
| Create          | `start <KB> <branch> --yes --at <sha>`      | `Create` / `Cancel`. Creates the worktree at the confirmed commit. The person's own copy stays untouched; nothing is sent                                                                                             |
| Write and check | none                                        | In W, as the skill says                                                                                                                                                                                               |
| Commit          | `commit <W> --message <text> --yes`         | `Commit` / `Change something` / `Cancel`. Commits in W; stays on this machine                                                                                                                                         |
| Push            | `push <W> --yes`                            | `Push` / `Keep local`. Sends the branch for review; the base branch changes only when someone merges the pull request. On Bitbucket and GitHub the push output carries the pull-request link, and the person opens it |

The worktree is placed at `<KB parent>/<KB name>-worktrees/<branch>`, with each `/` in the branch name replaced by `-` (for example `...-worktrees/docs-payments`). `push` refuses the default branch, a detached HEAD and uncommitted changes, and never forces. On `Cancel` or `Keep local` the skill stops and says where the work is; the worktree and branch stay on this machine and are never deleted by the skill.

- **No remote yet.** For a knowledge base that exists only on this machine (a lead starting alone) there is nothing to branch from. Only if KB has no uncommitted changes, the skill asks `Write` and, on yes, writes directly in KB and commits there. The change exists only on this machine until the project gets its URL.
- **Refusals.** `start` exiting 1 means the remote could not be asked (offline, no access): the skill stops and never falls back to writing in KB. A name that is taken gets `docs/<topic>-2` proposed. `commit` or `push` failing shows the message and stops; it never retries differently, forces, or runs git by hand.

## Rules

| Severity | Rule                                                                                                                                                                                                             |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MUST     | Read the target workspace's `CLAUDE.md` before writing                                                                                                                                                           |
| NEVER    | Add a document that contradicts a live one                                                                                                                                                                       |
| NEVER    | Record a decision, or set or change a record's status                                                                                                                                                            |
| MUST     | Update the workspace `README.md` index in the same change; leave both checkers passing; name the reviewing owner                                                                                                 |
| NEVER    | Create the branch, commit or push without that step's own yes; write in the person's clone (except for a knowledge base with no remote yet); push to the default branch; open, merge or approve the pull request |
| NEVER    | Invent a fact to fill a gap                                                                                                                                                                                      |

## Related skills

- [Navigating Project Context](/docs/plugins/tsh-product-management/skills/navigating-project-context): reads the knowledge base; this skill writes to it.
- [Adding a Project-Context Workspace](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace): when the topic needs a workspace that does not exist yet.
- [Repairing Project-Context Links](/docs/plugins/tsh-product-management/skills/repairing-project-context-links): when the checkers report violations.
- [Managing Decision Records](/docs/plugins/tsh-core/skills/managing-decision-records): where a decision goes.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/writing-project-knowledge/SKILL.md)
- Shared: [`locating-project-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locating-project-context.md), [`locate_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locate_project_context.py), [`sync_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/sync_project_context.py), [`write_worktree.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/write_worktree.py)
