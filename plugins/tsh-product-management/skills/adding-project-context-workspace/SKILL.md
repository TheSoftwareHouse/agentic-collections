---
name: adding-project-context-workspace
description: "Creates a new workspace in a project's `<project>-context` knowledge base — the folder, its README index, its CLAUDE.md with exactly one named owner, and its row in the area map, all in one change. Use when a new layer or area of such a project needs its own place: a new delivery layer, a workstream, an integration package."
when_to_use: "Trigger on: 'add a workspace for X' in a project with a `*-context` repository; a new layer joining the project such as mobile or platform; a topic outgrowing the workspace it sits in; 'where should this live' answered with 'somewhere new'; retiring a workspace."
---

# Adding a project-context workspace

A workspace exists when a named person keeps an area current. The failure this
prevents is a folder nobody owns: it fills up, goes stale, and becomes something
readers cannot trust and will not delete.

## Procedure

**Step 1 — Locate the knowledge base.** Read
`${CLAUDE_PLUGIN_ROOT}/shared/locating-project-context.md`, resolve and sync **KB**,
and start the write worktree it describes (branch `docs/<topic>`); call it **W** and
make every change under W, never in KB itself, then
read `KB/conventions/ownership.md`. It owns the rules below and wins on any conflict.

**Step 2 — Check it is really a new workspace.** Read `W/docs/README.md`. If an
existing workspace's scope covers the topic — including under another name, `qa` for
`quality`, `infra` for `platform` — the answer is a document there, not a new folder:
say so and stop. A workspace is warranted when the area has its own standing content
**and** its own owner.

**Step 3 — Get the owner.** Exactly one person, full name and e-mail. **Ask if it is
not given; never infer it** from git history or from who is talking. One person may
own several workspaces. If nobody can be named yet, stop: create the workspace when
somebody can.

**Step 4 — Create the folder** under `W/docs/<name>/`, kebab-case, with two files
matching the shape in `ownership.md` and the wording of its neighbours:

- `README.md` — what the space holds, and what it does not with a pointer to where
  that lives instead.
- `CLAUDE.md` — the owner as default reviewer, scope, the rules a newcomer would get
  wrong, and where to start.

**Step 5 — Add the row to the area map** in `W/docs/README.md`, in the right table:
project workspaces or layer workspaces. **This is the step that gets forgotten, and a
workspace missing from the map is invisible.**

**Step 6 — Verify, commit, report.** Run both checker scripts from W. Then commit in W and ask with AskUserQuestion — header `Push`, question "Push branch
`<branch>` to `<remote>` for review?", options `Push` / `Keep local`; on `Push` run
`write_worktree.py push "<W>" --yes`. Never push without that answer. Report
the files created, the row added, the owner, the branch, and that the person opens the
pull request from the link the push printed.

## Rules

| Severity | Rule |
| --- | --- |
| MUST | Exactly one owner, named with full name and e-mail. Never two, never inferred. |
| NEVER | Create the folder without both `README.md` and `CLAUDE.md`. |
| MUST | Add the area-map row in the same change as the folder. |
| NEVER | Create a `decisions/` folder inside the workspace. Records live in `KB/docs/decisions/` and carry this workspace's name in their `Scope`. |
| NEVER | Restate the root `CLAUDE.md` in the workspace file, or put a directory listing there — the `README.md` is the index. |
| MUST | Move existing documents into the new workspace in the same change when it is being split out of another, and fix every link that pointed at them. |
