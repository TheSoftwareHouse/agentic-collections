---
name: navigating-project-context
description: "Reads a project's knowledge base — the `<project>-context` repository beside its code: scope, accepted decisions, vocabulary, who owns what — before work that depends on it, and cites the document behind every project fact. Use when a task in a repository of such a project needs project facts: what was decided, what a term means, who owns an area, where a document lives."
when_to_use: "Trigger on: questions about the project's scope, requirements, decisions or terminology in a repository that has a sibling `*-context` folder; starting a feature, review or plan there; 'what did we decide about', 'who owns', 'what does <term> mean here'; code and documentation disagreeing."
---

# Navigating project context

Never answer a project question from memory. Read the corpus, cite the document.

## Procedure

**Step 1 — Locate the knowledge base.** Read
`${CLAUDE_PLUGIN_ROOT}/shared/locating-project-context.md` and resolve **KB**. Stop
there if nothing resolves.

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

**Step 3 — Answer with sources.** Name the document behind every project fact, so the
reader can check it.

## Rules

| Severity | Rule |
| --- | --- |
| MUST | Treat only `Accepted` records as constraints; read a `Superseded` record with its successor. |
| MUST | Check for a `DEPRECATED` banner under a title before citing the document. |
| MUST | Use the glossary's canonical terms in identifiers, tickets and documents you write. |
| NEVER | Edit anything under KB as a side effect of work in a code repository. Use `/tsh-product-management:writing-project-knowledge`, which routes the change to the owner. |
| MUST | When knowledge and code disagree, report both sources and name the workspace owner who decides. Do not silently pick one. |
