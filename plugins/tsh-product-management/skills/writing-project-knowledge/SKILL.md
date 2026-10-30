---
name: writing-project-knowledge
description: "Adds or updates a document in a project's knowledge base — the `<project>-context` repository — picking the owning workspace, applying the state-of-today rule, updating the workspace index, and naming the owner who reviews it. Use when something learned or changed on such a project should be written down."
when_to_use: "Trigger on: 'write this down', 'document this', 'update the doc on X' in a project with a `*-context` repository; recording a requirement, constraint, integration detail or process change; correcting a document that no longer matches reality; a workshop or call that produced knowledge worth keeping."
---

# Writing project knowledge

Writes into the knowledge base, under the rules of the workspace that owns the topic.
The failure this prevents is a second document saying something different: knowledge
added beside the existing document instead of into it.

## Procedure

**Step 1 — Locate the knowledge base and open a branch for the change.** Read
`${CLAUDE_PLUGIN_ROOT}/shared/locating-project-context.md`, resolve and sync **KB**,
then follow its §3 steps 1–2: propose the branch `docs/<topic>` with
`python3 ${CLAUDE_PLUGIN_ROOT}/shared/write_worktree.py start "<KB>" docs/<topic>` and
create it only after the person answers `Create`. Call the worktree **W**. Read and
write under W: it holds the approved version the change is reviewed against, and **the
person's clone is never edited**, whatever branch it is on.

**Step 2 — Find the owning workspace.** Read `W/docs/README.md`. Pick the one
workspace whose scope covers the topic, then read its `CLAUDE.md` — it carries the
owner and the rules specific to that space. When two workspaces both fit, choose the
one that owns the **outcome**, and say which you rejected.

**Step 3 — Look for the document that already exists.** Read the workspace's
`README.md` and the documents it names. Updating one in place beats adding another,
every time. Only create a file when nothing there covers the topic.

**Step 4 — Write it.** Present tense, current state, no history — history lives in
version control. If the change makes an existing document wrong, fix that document in
the same change, or delete it; if it must be kept, add the banner:

```markdown
> **DEPRECATED (YYYY-MM-DD).** <Why this no longer describes the current state.>
> Current state: [<successor>](path).
```

Filenames are kebab-case. Link only to files that exist in the repository.

**Step 5 — Update the index.** Add or adjust the entry in the workspace's `README.md`
in this same change. A document nothing links to will not be found.

**Step 6 — Verify, then commit and push only on a yes.** From W, run
`python3 scripts/check_links.py && python3 scripts/check_tables.py` until clean. Then
§3 steps 4–5 of the shared guide: show the change, ask `Commit`, and on yes run
`python3 ${CLAUDE_PLUGIN_ROOT}/shared/write_worktree.py commit "<W>" --message
"docs(<workspace>): <what changed>" --yes`; then ask `Push`, and on yes run
`python3 ${CLAUDE_PLUGIN_ROOT}/shared/write_worktree.py push "<W>" --yes`.

Report: which workspace, which files changed, the branch and where it lives, the owner
from that workspace's `CLAUDE.md` who reviews it, and the next step for the person —
open the pull request from the link the push printed. The change reaches everyone only
after that review is merged.

## Rules

| Severity | Rule |
| --- | --- |
| MUST | Read the target workspace's `CLAUDE.md` before writing. Its rules outrank this skill. |
| NEVER | Add a document that contradicts a live one. Update the live one, or banner it. |
| NEVER | Record a decision here. A choice with alternatives is a decision record: invoke `/tsh-core:managing-decision-records` with **`W/docs/decisions/`** as the archive — never a code repository's own folder, and never this skill. |
| NEVER | Set or change a decision record's status. |
| MUST | Update the workspace `README.md` index in the same change as the document. |
| MUST | Leave both checker scripts passing, and name the owner who reviews the change. |
| NEVER | Create the branch, commit or push without that step's own yes; write in the person's clone (the one exception — a knowledge base with no remote yet — is in `locating-project-context.md`); push to the default branch; or open, merge or approve the pull request. |
| NEVER | Invent a fact to fill a gap. Write what is known and name the gap as a gap. |
