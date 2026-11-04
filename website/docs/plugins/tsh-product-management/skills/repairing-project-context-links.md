---
title: Repairing Project-Context Links
sidebar_label: Repairing Project-Context Links
sidebar_position: 24
description: Finds and repairs broken relative links, non-kebab-case filenames and misrendering tables in a project's knowledge base, using the repository's own checker scripts.
sources:
  - plugins/tsh-product-management/skills/repairing-project-context-links/
  - plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/scripts/check_links.py.tmpl
  - plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/scripts/check_tables.py.tmpl
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/shared/locate_project_context.py
  - plugins/tsh-product-management/shared/sync_project_context.py
  - plugins/tsh-product-management/shared/write_worktree.py
sources_hash: "6fc95e6b4c2557ad0fdfce0cdd639587c679d7627d6172ce9cfe105659f23493"
---

# Repairing Project-Context Links

**Plugin:** [TSH Product Management](/docs/plugins/tsh-product-management/)  
**Invoke:** `/tsh-product-management:repairing-project-context-links` (also model-invocable: it routes on "check the links" or "fix the docs" in a `*-context` repository, on `check_links.py` or `check_tables.py` failures, on a pull request blocked on the quality gate, and after renaming or deleting documents)  
**Used by:** no skill or agent loads it. The knowledge base that [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context) scaffolds points to it from the quality-gate section of its root `CLAUDE.md`.

Detection is deterministic and belongs to the scripts the context repository ships. Repair needs judgment, and that is this skill's job.

## What it covers

| Area             | Coverage                                                                                                                                                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Detection**    | Runs `scripts/check_links.py` and `scripts/check_tables.py` from the worktree. Each output line is `file:line: problem`. Nothing is fixed before the whole list is in front of the skill, because one rename usually explains several failures |
| **Broken links** | Diagnosed in a fixed order: moved or renamed, deleted on purpose, never existed (see below)                                                                                                                                                    |
| **Naming**       | A filename that is not kebab-case is renamed, and every file that referred to the old name is updated in the same change                                                                                                                       |
| **Tables**       | Pads a short row to the header's cell count, removes a blank line inside the table, adds the missing blank line after it, or escapes a content pipe with a backslash. A ragged row is never fixed by deleting a column from the header         |
| **Empty corpus** | `FAIL: nothing to check` means the corpus is empty or unreadable, not clean: the skill reports it and stops                                                                                                                                    |
| **Ambiguity**    | When two candidate targets are equally plausible, it asks rather than guessing                                                                                                                                                                 |
| **Meaning**      | Never changes a document's meaning while fixing its references; never creates an empty placeholder file or deletes a document just to make a link resolve                                                                                      |

## What the checkers look for

The two scripts are copied into every knowledge base by [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context).

| Script            | Checks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `check_links.py`  | Every relative markdown link points at a file or folder that is part of the corpus. Inside a git repository the corpus is the set of **tracked** files, because a link that resolves on one disk but was never committed is already broken for everyone else. External links, bare `#anchor` links and links that resolve outside the repository (citations) are skipped. Every markdown filename must be kebab-case, with a few allowed forms: dotted suffixes, a structural underscore prefix, zero-padded decision records, and the uppercase files README, CLAUDE, SKILL, GUIDE and CHANGELOG |
| `check_tables.py` | A ragged row (cell count differs from the header), a header and separator with different cell counts, a split table (a blank line between two body rows), and a glued trailer (text on the line directly after the last row)                                                                                                                                                                                                                                                                                                                                                                      |

## How it works

1. **Locate the knowledge base and open a branch.** Resolve and sync KB through the shared guide, propose `docs/fix-links` with `write_worktree.py start`, and create it only after the person answers `Create`. Every change is made under the worktree W, never in KB itself.
2. **Detect.** Run both scripts from W and collect the full list.
3. **Diagnose each broken link, in this order:**
   1. **Moved or renamed.** Search the corpus for the basename. One plausible candidate means re-point the link; several means read the surrounding sentence to choose, and ask if it is still ambiguous.
   2. **Deleted on purpose.** Nothing matches and version control shows a deletion. Remove the link, keeping the sentence readable, or point it at the successor the deletion names.
   3. **Never existed.** No match anywhere. If it is a list entry, drop it. If the document is genuinely planned, leave plain text without a link.
4. **Fix naming violations**, then **fix tables**.
5. **Verify, then commit and push only on a yes.** Re-run both scripts from W until clean, then the `Commit` question (message `docs: repair links and tables`) and the `Push` question. The report gives, per finding, what was broken, which of the three cases it was and what was done; it lists anything left unresolved and why, and names the branch.

The branch, commit and push questions are described under [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge#the-branch-flow): each git step runs only after its own yes, and the person's clone is never edited.

## Rules

| Severity | Rule                                                                                |
| -------- | ----------------------------------------------------------------------------------- |
| NEVER    | Create an empty placeholder file, or delete a document, just to make a link resolve |
| NEVER    | Change a document's meaning while fixing its references                             |
| MUST     | Update every referrer when renaming a file, in the same change                      |
| MUST     | Re-run both scripts and show them clean before reporting                            |
| MUST     | Ask when two candidate targets are equally plausible, rather than guessing          |

## Related skills

- [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge): the branch flow, and the skill that adds or updates documents.
- [Adding a Project-Context Workspace](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace): moving documents into a new workspace is a common cause of broken links.
- [Initializing Project Context](/docs/plugins/tsh-product-management/skills/initializing-project-context): ships the checker scripts into the knowledge base.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/repairing-project-context-links/SKILL.md)
- Checkers: [`check_links.py.tmpl`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/scripts/check_links.py.tmpl), [`check_tables.py.tmpl`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/scripts/check_tables.py.tmpl)
- Shared: [`locating-project-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locating-project-context.md), [`locate_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locate_project_context.py), [`sync_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/sync_project_context.py), [`write_worktree.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/write_worktree.py)
