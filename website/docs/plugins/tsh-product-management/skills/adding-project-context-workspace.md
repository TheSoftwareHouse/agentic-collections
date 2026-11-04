---
title: Adding a Project-Context Workspace
sidebar_label: Adding a Project-Context Workspace
sidebar_position: 23
description: Creates a new workspace in a project's knowledge base (the folder, its README index, its CLAUDE.md with exactly one named owner, and its row in the area map) in one change.
sources:
  - plugins/tsh-product-management/skills/adding-project-context-workspace/
  - plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/conventions/ownership.md.tmpl
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/shared/locate_project_context.py
  - plugins/tsh-product-management/shared/sync_project_context.py
  - plugins/tsh-product-management/shared/write_worktree.py
sources_hash: "0a2667af4d9a72f853b6d07b846e5307ee91738842ef694a77776d95f5d30c5c"
---

# Adding a Project-Context Workspace

**Plugin:** [TSH Product Management](/docs/plugins/tsh-product-management/)  
**Invoke:** `/tsh-product-management:adding-project-context-workspace` (also model-invocable: it routes on "add a workspace for X", a new layer such as mobile or platform joining the project, or a topic outgrowing the workspace it sits in)  
**Used by:** no skill or agent loads it. The knowledge base that [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context) scaffolds points to it from its root `CLAUDE.md`, its area map and `conventions/ownership.md`.

A workspace exists when a named person keeps an area current. The failure this skill prevents is a folder nobody owns: it fills up, goes stale, and becomes something readers cannot trust and will not delete.

## What it covers

| Area                  | Coverage                                                                                                                                                                                                                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Is it really new?** | Reads `docs/README.md`. If an existing workspace's scope covers the topic, even under another name (`qa` for `quality`, `infra` for `platform`), the answer is a document there, not a new folder, and the skill stops. A workspace is warranted when the area has its own standing content and its own owner |
| **Exactly one owner** | Full name and e-mail. The skill asks if it is not given and never infers it from git history or from who is talking. One person may own several workspaces. If nobody can be named yet, it stops: the workspace is created when somebody can be                                                               |
| **The folder**        | `docs/<name>/`, kebab-case, with two files in the shape `conventions/ownership.md` defines and the wording of neighbouring workspaces                                                                                                                                                                         |
| **`README.md`**       | What the space holds, and what it does not, with a pointer to where that lives instead                                                                                                                                                                                                                        |
| **`CLAUDE.md`**       | The owner as default reviewer, scope, the rules a newcomer would get wrong, and where to start. It does not restate the root `CLAUDE.md` and holds no directory listing, because the `README.md` is the index                                                                                                 |
| **Area-map row**      | Added to `docs/README.md` in the right table, project workspaces or layer workspaces. This is the step that gets forgotten, and a workspace missing from the map is invisible                                                                                                                                 |
| **Decisions**         | No `decisions/` folder inside the workspace. Records live in `docs/decisions/` of the knowledge base and carry the workspace's name in their `Scope`                                                                                                                                                          |
| **Splitting out**     | When the workspace is split out of another, existing documents move in the same change and every link that pointed at them is fixed                                                                                                                                                                           |
| **Precedence**        | `conventions/ownership.md` of the knowledge base owns these rules and wins on any conflict                                                                                                                                                                                                                    |

## How it works

1. **Locate the knowledge base.** Resolve and sync KB through the shared guide and read `KB/conventions/ownership.md`. The branch is opened only once steps 2 and 3 say the workspace is warranted.
2. **Check it is really a new workspace.**
3. **Get the owner.**
4. **Open the branch and create the folder.** Propose `docs/workspace-<name>` with `write_worktree.py start`, create it only after the person answers `Create`, and make every change under the worktree W, never in KB itself. Then create `docs/<name>/README.md` and `CLAUDE.md`.
5. **Add the row to the area map** in `W/docs/README.md`.
6. **Verify, then commit and push only on a yes.** Run both checker scripts from W until clean, then the `Commit` question (message `docs: add the <name> workspace`) and the `Push` question. The report lists the files created, the row added, the owner and the branch, and says the person opens the pull request from the link the push printed.

The branch, commit and push questions are the same as in [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge#the-branch-flow): each git step runs only after its own yes, and the person's clone is never edited.

## Rules

| Severity | Rule                                                                                                                              |
| -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| MUST     | Exactly one owner, named with full name and e-mail. Never two, never inferred                                                     |
| NEVER    | Create the folder without both `README.md` and `CLAUDE.md`                                                                        |
| MUST     | Add the area-map row in the same change as the folder                                                                             |
| NEVER    | Create a `decisions/` folder inside the workspace                                                                                 |
| NEVER    | Restate the root `CLAUDE.md` in the workspace file, or put a directory listing there                                              |
| MUST     | Move existing documents into the new workspace in the same change when splitting one out, and fix every link that pointed at them |

## Related skills

- [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge): the branch flow, and the right tool when a document, not a workspace, is what is missing.
- [Repairing Project-Context Links](/docs/plugins/tsh-product-management/skills/repairing-project-context-links): when moved documents leave broken links.
- [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context): creates the initial workspaces and the optional layers.
- [Managing Decision Records](/docs/plugins/tsh-core/skills/managing-decision-records): where a workspace's decisions are recorded.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/adding-project-context-workspace/SKILL.md)
- Ownership standard: [`ownership.md.tmpl`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/conventions/ownership.md.tmpl)
- Shared: [`locating-project-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locating-project-context.md), [`locate_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locate_project_context.py), [`sync_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/sync_project_context.py), [`write_worktree.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/write_worktree.py)
