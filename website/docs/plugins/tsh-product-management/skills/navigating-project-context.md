---
title: Navigating Project Context
sidebar_label: Navigating Project Context
sidebar_position: 21
description: Reads a project's knowledge base before work that depends on it, wherever the clone sits, and cites the file, its last change and its owner behind every project fact.
sources:
  - plugins/tsh-product-management/skills/navigating-project-context/
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/shared/locate_project_context.py
  - plugins/tsh-product-management/shared/sync_project_context.py
sources_hash: "960bb1f31e977698cd0257696be53f491fa8009ff31e95e0e8a9acb815fb1377"
---

# Navigating Project Context

**Plugin:** [TSH Product Management](/docs/plugins/tsh-product-management/)  
**Invoke:** `/tsh-product-management:navigating-project-context [question] [context repository URL]` (also model-invocable: it routes on questions about a project's scope, decisions, terms and owners)  
**Used by:** the `tsh:project-context` block that [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context) writes into a connected repository's `CLAUDE.md` (or `CLAUDE.local.md`). The block directs sessions to this skill for work that touches decisions, scope, glossary terms, the data model or new dependencies. No other skill or agent loads it.

Reads a project's knowledge base, the `<project>-context` repository, before work that depends on it. It never answers a project question from memory: it reads the corpus and cites the document.

## When it applies

- Questions about the project's scope, requirements, decisions or terminology in a repository whose `CLAUDE.md` carries a `tsh:project-context` block, or whose settings declare a `*-context` marketplace.
- Starting a feature, review or plan in such a repository.
- "What did we decide about", "who owns", "what does a term mean here".
- Code and documentation disagreeing.
- A context-repository URL given to read from anywhere, with no code repository.

## What it covers

| Area              | Coverage                                                                                                                                                                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Locate**        | Finds the knowledge base (KB) wherever the clone sits: beside the code, in a project folder, or in `~/.tsh/context/<slug>/`. With a git URL in the arguments it resolves by URL                                                                          |
| **Sync**          | Brings the clone up to date before reading. The only change it can make is a fast-forward of a clean clone on the default branch                                                                                                                         |
| **Reading order** | `KB/CLAUDE.md`, then `KB/docs/README.md` (the area map), then `KB/docs/decisions/README.md`, then the owning workspace's `README.md` and `CLAUDE.md`, then `KB/docs/glossary.md` when a term is in question                                              |
| **Decisions**     | Filters the index to `Accepted` first, then narrows by the `Scope` column. Only `Accepted` records are constraints; a `Superseded` record is read with its successor. This is the only archive: no records are looked up or written in a code repository |
| **Citations**     | Every project fact is followed by its source: file, last-change date and owner, for example `(docs/decisions/0004-payments.md · changed 2026-09-12 · owner: Jane Doe)`. A file with no output from `git log` is reported as "uncommitted"                |
| **Warnings**      | Every sync warning goes at the top of the answer, one line each, before anything else                                                                                                                                                                    |
| **Conflicts**     | A source older than the code it describes, or than a later document on the same topic, is a finding. When knowledge and code disagree, both sources are reported and the workspace owner who decides is named                                            |
| **Deprecation**   | A `DEPRECATED` banner under a title is checked before citing the document; such a document is history, not current state                                                                                                                                 |
| **Vocabulary**    | Uses the glossary's canonical terms in identifiers, tickets and documents it writes                                                                                                                                                                      |

## How it works

1. **Locate and sync.** Follow the shared locating guide: run `locate_project_context.py` (with `--url` when the arguments carry a git URL), then `sync_project_context.py`. Stop if nothing resolves; keep the sync's warnings for the answer.
2. **Read only what the task needs**, in the order above. The corpus is large by design and the area map exists so the skill does not read all of it.
3. **Date every source** it will cite, one `git log -1 --format='%cs %an'` per file. The owner is the one named in the owning workspace's `CLAUDE.md`.
4. **Answer.** Warnings first, then the answer, each project fact followed by its source.

### Locator outcomes

| Exit | Means                                                                             | What the skill does                                                                                                                                                                                    |
| ---- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0    | Found                                                                             | Continues, then checks `BLOCK` and `READ_ACCESS`                                                                                                                                                       |
| 1    | Not wired, nothing found                                                          | Stops and says the repository is not connected; points to [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context) (_Attach repository_) or to `--url` |
| 2    | Several knowledge bases in one folder (old layout)                                | Asks which project the task belongs to; never picks one                                                                                                                                                |
| 3    | Wired, but this person has not chosen a clone yet                                 | Asks once where the knowledge base should live on this machine, offering existing clones, a default clone location or another folder; the choice is remembered for every repository of the project     |
| 4    | `--use` or `--clone` refused                                                      | Shows the message; another project's clone is never used                                                                                                                                               |
| 5    | The name is taken: `<slug>-context` already names another project on this machine | Stops; one of the two projects must be renamed by its lead. Neither clone is read and the registry is never edited                                                                                     |

- `BLOCK=missing` or `BLOCK=drift`: the pointer block is gone or points at another URL. The skill says so in one line and offers to restore it through _Attach repository_; it never restores or edits it itself.
- `READ_ACCESS=missing`: reads outside the session's folder will prompt each time. The skill offers once to add one line to the repository's `.claude/settings.local.json`, which git never sees (`--grant-read`).

### Sync behaviour

`sync_project_context.py` prints JSON and always exits 0 when the knowledge base exists: a stale read with a warning beats no read. It fetches at most once per TTL (default 600 s, `TSH_CONTEXT_TTL`), caps the fetch (default 5 s, `TSH_CONTEXT_FETCH_TIMEOUT`; the fast-forward pull that may follow is capped at no less than 30 s) and can never prompt for a password. It never merges, rebases, stashes, resets, checks out or pushes.

| Warning code         | Means                                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `not-git`            | The knowledge base is plain files, not a git clone                                                                 |
| `local-only`         | No remote yet: the knowledge exists only on this machine                                                           |
| `index-lock`         | Another git process holds the index; nothing was done                                                              |
| `busy`               | Another sync of this knowledge base is running; read as is                                                         |
| `offline`            | Fetch failed or timed out (network, VPN, credentials)                                                              |
| `blocked`            | A local file the update would overwrite stopped the pull                                                           |
| `not-default-branch` | The clone is on another branch; that branch is what is read                                                        |
| `dirty`              | Uncommitted changes in the clone; they are what is read                                                            |
| `behind`             | The clone is behind the remote and was not updated                                                                 |
| `unknown-default`    | The approved branch could not be determined; nothing was pulled                                                    |
| `diverged`           | Local and remote history differ (for example after a force-push); nothing was changed and a fresh clone is the fix |

On `diverged` the skill offers to clone the remote again into `<KB>-fresh`; the old copy stays and is never deleted. On no, it keeps reading the old copy with the warning.

## Boundaries

- It never edits anything under KB as a side effect of work in a code repository. Changes go through [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge), which writes on its own branch and routes the change to the owner.
- Git in KB is limited to the two scripts and `git log`. The side effects allowed are a fast-forward of a clean default branch, a clone and a registry entry after the person chose a folder, and a `settings.local.json` entry after they said yes.

## Related skills

- [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge): where a change to the knowledge base goes.
- [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context): connects a repository so this skill can find the knowledge base.
- [Managing Decision Records](/docs/plugins/tsh-core/skills/managing-decision-records): owns the record format that the decision index follows.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/navigating-project-context/SKILL.md)
- Shared: [`locating-project-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locating-project-context.md), [`locate_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locate_project_context.py), [`sync_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/sync_project_context.py)
