---
title: Project context
sidebar_label: Project context
sidebar_position: 6
description: How a repository's own Claude Code context is set up and kept true, and how a project's shared knowledge base — the `<slug>-context` repository — is created, connected to code repositories, read with citations and written through reviewed branches.
sources:
  - plugins/tsh-core/skills/init/
  - plugins/tsh-core/skills/managing-claude-context/
  - plugins/tsh-core/skills/managing-decision-records/
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/skills/initializing-project-context/SKILL.md
  - plugins/tsh-product-management/skills/initializing-project-context/references/
  - plugins/tsh-product-management/skills/initializing-project-context/templates/catalog/__SLUG__-context/docs/README.md.tmpl
  - plugins/tsh-product-management/skills/navigating-project-context/SKILL.md
  - plugins/tsh-product-management/skills/writing-project-knowledge/SKILL.md
  - plugins/tsh-product-management/skills/adding-project-context-workspace/SKILL.md
  - plugins/tsh-product-management/skills/repairing-project-context-links/SKILL.md
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/hooks/hooks.json
  - plugins/tsh-product-management/hooks/guard-project-context-block.mjs
  - .claude/rules/project-context-contract.md
sources_hash: "fd3586612e9c285b5835ef9e43939f4d44f269067c91ff3efc84d634caad9bbf"
---

# Project context

Two related jobs share this page. **Repository context** is what Claude Code loads in one repository — `CLAUDE.md`, path-scoped rules, the decision index — and lives in `tsh-core`. The **project knowledge base** is the project's shared `<slug>-context` repository — scope, decisions, vocabulary, owners — read and written from any code repository of the project, and lives in `tsh-product-management`.

## Repository context

**Plugin:** [`tsh-core`](/docs/plugins/tsh-core/) · **Start with:** `/tsh-core:init`, run inside the repository.

| Component | Owns |
| :-- | :-- |
| [`init`](/docs/plugins/tsh-core/skills/init) | The sequence and the wiring: runs the two skills below in order and adds a maintenance section to root `CLAUDE.md`. A command only — it never loads by description match |
| [`managing-claude-context`](/docs/plugins/tsh-core/skills/managing-claude-context) | The memory layer: root and nested `CLAUDE.md`, `.claude/rules/` with `paths:` globs, and the decision index |
| [`managing-decision-records`](/docs/plugins/tsh-core/skills/managing-decision-records) | What a decision record is: the four sections, the status vocabulary, numbering, superseding, and the index row |

None of the three names a subagent: the session that runs them does the work. `init` is safe to re-run: a second run converges to "nothing to do", and a partial or drifted setup is repaired, not rewritten.

### What `/tsh-core:init` does

1. **Establishes the memory layer** by running `managing-claude-context` in full. It starts with `/context` and an inventory of what loads — nested `CLAUDE.md` files, `.claude/rules/`, `AGENTS.md`, `.github/copilot-instructions.md`, `.cursor/rules/` — and branches: nothing found means a bootstrap, something found means a drift audit. Each fact goes to exactly one layer: root `CLAUDE.md` orients and points downward, conventions go to path-scoped rules, area-owned conventions go to a nested `CLAUDE.md`, and multi-step procedures go to skills. Every `CLAUDE.md` stays under 200 lines, and every command, path and version is verified before it is written.
2. **Ensures the decision archive exists.** If none was left behind, it creates the index — default `docs/decisions/README.md`; an existing archive location wins — with an empty four-column table: path, tags, description, status. It invents no record: decisions the codebase clearly embodies are listed as candidates in the report, for `managing-decision-records` to write once a person confirms them.
3. **Wires the maintenance section** into root `CLAUDE.md`: when structure, conventions, commands or tooling change, update the memory files in the same change; when an important decision is made, propose recording it. Each bullet names the `tsh-core` skill, and says what to do by hand without it — `tsh-core` installs per person, so a teammate without it still gets a working instruction.
4. **Verifies and reports.** `/context` confirms everything written loads, or is scoped to load on read. The report lists what was created, repaired and left alone, plus decision candidates, and calls the result a proposal for the team to review.

Every pointer to the decision index is written in backticks, never as a bare `@` import, which would load the whole index at launch. Both the pointer and the index header state that only `Accepted` records bind.

### Keeping it current

- **`managing-claude-context`** loads on its own when Claude keeps ignoring a convention, a `CLAUDE.md` grows past 200 lines or goes stale, a monorepo needs nested files, or instructions need migrating from GitHub Copilot or Cursor. It revises existing files in place and never removes or edits a block fenced by `<!-- tsh:<name> START` … `END -->`.
- **`managing-decision-records`** first checks that the choice is a decision and not a convention that belongs in `CLAUDE.md`. It writes Decision, Context, Alternatives and Consequences in that order, adds the index row in the same change, never edits an accepted record's body — a changed decision gets a new record and a forward link — and never sets a status: it proposes one and names who decides.
- **A domain dictionary** from [business analysis](./business-analysis) is adopted by `managing-claude-context` as two tiers: about 15 lines in root `CLAUDE.md`, and the full file on demand at `docs/domain-dictionary.md` by default, referenced in backticks.

## The project knowledge base

**Plugin:** [`tsh-product-management`](/docs/plugins/tsh-product-management/) · **Start with:** `/tsh-product-management:initializing-project-context`, in the folder where the project should live or in a code repository to connect.

| Component | Does |
| :-- | :-- |
| [`initializing-project-context`](/docs/plugins/tsh-product-management/skills/initializing-project-context) | Creates the knowledge base, connects code repositories to it, and publishes it. A command only |
| [`navigating-project-context`](/docs/plugins/tsh-product-management/skills/navigating-project-context) | Reads it before work that depends on project facts, and cites file, last change and owner for each fact |
| [`writing-project-knowledge`](/docs/plugins/tsh-product-management/skills/writing-project-knowledge) | Adds or updates a document in the owning workspace, on its own branch, for the owner to review |
| [`adding-project-context-workspace`](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace) | Creates a workspace with exactly one named owner and its row in the area map |
| [`repairing-project-context-links`](/docs/plugins/tsh-product-management/skills/repairing-project-context-links) | Repairs what the knowledge base's checker scripts report: broken links, non-kebab-case filenames, misrendering tables |

None of the five names a subagent: the session that runs them asks the questions and runs the scripts. The four knowledge-base skills ship in the plugin and find the knowledge base on their own; nothing but the checker scripts is copied into it.

### Setting it up

`initializing-project-context` has three modes:

- **New project.** It probes the folder, asks the fixed questions (project name, owner, layout, extra layers), shows a dry-run file list and asks before writing. It scaffolds `<slug>-context/`: five project workspaces (baseline, architecture, product, delivery, quality), three layer workspaces (backend, frontend, design) plus any chosen extra layer, one `docs/decisions/` folder, a glossary, two conventions, four checker scripts, a Bitbucket pipeline, and a Claude Code marketplace with an empty `<slug>-shared` plugin for the project's own Markdown skills. The checker scripts and `claude plugin validate` must pass before the local first commit. It publishes only after a yes to `Push`, and only to an **empty** remote; otherwise it prints the commands.
- **Attach repository.** It connects a code repository to an existing project. For every repository it asks whether the team may commit there: **commit mode** writes `.claude/settings.json` and a `tsh:project-context` block in `CLAUDE.md`, for the person to commit in a pull request; **local mode**, for a client's repository, writes `.claude/settings.local.json` and the block in `CLAUDE.local.md`, kept out of git through `.git/info/exclude`. The settings enable the project's plugin and `tsh-product-management`, so every role in a connected repository gets the knowledge-base skills.
- **Add URL.** It gives a knowledge base started without a remote its URL and publishes it after asking; each connected repository is then re-attached so its settings point at the URL.

The closing report states that **the current session cannot see the new plugin** — a new session is needed — and lists what the person still has to do by hand: commit the commit-mode files, protect the default branch on the git host, enable Pipelines on Bitbucket, assign owners marked `TBD — assign an owner`.

### Reading it

Every knowledge-base skill starts by locating and syncing the clone, which may sit beside the code, in a project folder or in `~/.tsh/context/<slug>/`. A teammate who has no clone yet is asked once where it should live; the choice is remembered for every repository of the project. The sync's only possible change is a fast-forward of a clean clone on its default branch, and its warnings — reading a branch, uncommitted changes, an out-of-date copy — go at the top of every answer.

[`navigating-project-context`](/docs/plugins/tsh-product-management/skills/navigating-project-context) then reads only what the task needs: the knowledge base's `CLAUDE.md`, the area map in `docs/README.md`, the decision index filtered to `Accepted`, the owning workspace, and the glossary. Every project fact is followed by its source, last change and owner:

```text
(docs/decisions/0004-payments.md · changed 2026-09-12 · owner: Jane Doe)
```

When knowledge and code disagree, it reports both and names the workspace owner who decides. It never edits the knowledge base as a side effect of work in a code repository.

### Writing to it

[`writing-project-knowledge`](/docs/plugins/tsh-product-management/skills/writing-project-knowledge), [`adding-project-context-workspace`](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace) and [`repairing-project-context-links`](/docs/plugins/tsh-product-management/skills/repairing-project-context-links) share one write path, and the person's own clone is never edited:

1. **Propose** a branch — `docs/<topic>`, `docs/workspace-<name>` or `docs/fix-links`.
2. **`Create`** — on a yes, a new worktree for that branch; all changes happen there.
3. **Write and check** — the checker scripts run until clean.
4. **`Commit`** — the change is shown first; on a yes it is committed, and stays on this machine.
5. **`Push`** — on a yes the branch is sent to the remote. The person opens the pull request from the printed link; the change reaches everyone once the owner's review is merged.

Each git step runs only after its own yes; one yes never covers another step. A knowledge base with no remote yet is the one exception: with a `Write here` yes, the change is written and committed directly in it.

What each writer adds to the shared path:

- **`writing-project-knowledge`** picks the one workspace whose scope covers the topic, updates an existing document rather than adding a second one, writes the current state in present tense, banners an outdated document `DEPRECATED`, and updates the workspace index in the same change. A choice with alternatives is a decision record instead: it goes through `/tsh-core:managing-decision-records`, with the knowledge base's `docs/decisions/` as the archive.
- **`adding-project-context-workspace`** first checks that no existing workspace covers the topic, asks for exactly one owner — never inferred from git history — and creates the folder with its `README.md`, its `CLAUDE.md` and the area-map row in one change.
- **`repairing-project-context-links`** runs `check_links.py` and `check_tables.py`, diagnoses each broken link as moved, deleted on purpose or never existed, renames files to kebab-case with every referrer updated, and never creates a placeholder or deletes a document to make a link resolve.

### Decision records

Project decisions live in one place: the knowledge base's `docs/decisions/`, with one number sequence and one index, whichever folder the session started in. A record about one code repository's own internal conventions may stay in that repository. Only `Accepted` records bind; a `Superseded` record is read together with its successor.

## Guard rails

- **The `tsh:project-context` block is protected.** A `PreToolUse` hook denies any `Edit` or `Write` to `CLAUDE.md` or `CLAUDE.local.md` whose result no longer contains the block byte for byte. Only `initializing-project-context` rewrites it, through its own script. A shell command that rewrites the file is not covered; the locator reports a missing or drifted block on the next read and offers to restore it.
- **Git runs through the plugin's scripts.** No merge, rebase, stash, reset or branch switch in a person's clone; no commit, staging or `.gitignore` change in a code repository; no push to the default branch, no force-push, no branch or worktree deletion.
- **Nothing is invented.** No owners, decisions or terms are made up, and no client, employer or other project's details reach a generated file.

## Where people decide

| Point | What the user decides |
| :-- | :-- |
| New project | Name, owner, layout and layers; whether to create the files; which repositories to connect and which belong to the client; where the remote lives; whether to push |
| Attach repository | The project's URL; commit or local mode for each repository |
| First read | Where this person's clone lives; whether sessions may read it without asking each time |
| Every write | `Create` the branch, `Commit`, `Push` — three separate answers |
| New workspace | Who the one owner is |
| Ambiguous link repair | Which of two equally plausible targets is meant |
| Diverged clone | Whether to clone a fresh copy beside the old one |
