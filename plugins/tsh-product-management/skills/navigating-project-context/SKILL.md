---
name: navigating-project-context
description: "Reads a project's knowledge base — the `<project>-context` repository: scope, accepted decisions, vocabulary, who owns what — before work that depends on it, wherever the clone sits, and cites the file, its last change and its owner behind every project fact. Use when a task in a repository of such a project needs project facts: what was decided, what a term means, who owns an area, where a document lives."
when_to_use: "Trigger on: questions about the project's scope, requirements, decisions or terminology in a repository whose CLAUDE.md carries a `tsh:project-context` block or whose settings declare a `*-context` marketplace; starting a feature, review or plan there; 'what did we decide about', 'who owns', 'what does <term> mean here'; code and documentation disagreeing; a context-repository URL given to read from anywhere."
argument-hint: "[question] [context repository URL, when there is no code repository]"
---

# Navigating project context

Never answer a project question from memory. Read the corpus, cite the document.

Input: **$ARGUMENTS** — a question, optionally with the context repository's URL.

## Procedure

**Step 1 — Locate and sync the knowledge base.** Read
`${CLAUDE_PLUGIN_ROOT}/shared/locating-project-context.md` and follow it: locate
(with `--url` when `$ARGUMENTS` carries a git URL), then sync. Stop if nothing
resolves. Keep the sync's `warnings` for Step 4.

**Step 2 — Read only what the task needs**, in this order. The corpus is large by
design and the area map exists so you do not read all of it.

1. `KB/CLAUDE.md` — the binding rules of the corpus.
2. `KB/docs/README.md` — the area map: which workspace owns the topic, and who owns it.
3. `KB/docs/decisions/README.md` — what was decided, for the whole project in one
   index. Filter to `Accepted` first, then narrow by the `Scope` column to the layer
   the task touches. This is the only archive; do not look for records in a code
   repository, and do not write one there.
4. The owning workspace's `README.md` and `CLAUDE.md`, then what they point at.
5. `KB/docs/glossary.md` when a term is in question.

**Step 3 — Date every source you will cite.** One command per file:

```shell
git -C "<KB>" log -1 --format='%cs %an' -- "<path relative to KB>"
```

No output means the file is not committed yet — say "uncommitted" instead of a date.
The owner is the one named in the owning workspace's `CLAUDE.md`.

**Step 4 — Answer.** First the sync's warnings, one line each. Then the answer, with
every project fact followed by its source:

```text
(docs/decisions/0004-payments.md · changed 2026-09-12 · owner: Jane Doe)
```

A source older than the code it describes, or than a later document on the same
topic, is a finding: say so, and name the owner who decides.

## Rules

| Severity | Rule |
| --- | --- |
| MUST | Show every sync warning at the top of the answer. An answer read from a branch, from uncommitted changes or from an out-of-date copy must say so before anything else. |
| MUST | Cite file, last-change date and owner for every project fact. |
| MUST | Treat only `Accepted` records as constraints; read a `Superseded` record with its successor. |
| MUST | Check for a `DEPRECATED` banner under a title before citing the document. |
| MUST | Use the glossary's canonical terms in identifiers, tickets and documents you write. |
| NEVER | Edit anything under KB as a side effect of work in a code repository. Use `/tsh-product-management:writing-project-knowledge`, which writes on its own branch and routes the change to the owner. |
| NEVER | Run git in KB beyond the two scripts and `git log` above. Side effects allowed here: a fast-forward of a clean default branch (sync), a clone and a registry entry after the person chose a folder, a `settings.local.json` entry after they said yes. |
| MUST | When knowledge and code disagree, report both sources and name the workspace owner who decides. Do not silently pick one. |
