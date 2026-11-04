---
title: Managing Claude Context
sidebar_label: managing-claude-context
sidebar_position: 3
description: Sets up and maintains the project-context files Claude Code loads (CLAUDE.md, path-scoped rules and the decision-record index) and audits them for drift.
sources:
  - plugins/tsh-core/skills/managing-claude-context/
sources_hash: "75020d76309cb91b15e2845095e28bd35c75caca8d5154a1602d2e55ad11d295"
---

# Managing Claude Context

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:managing-claude-context` (also loaded automatically when a request matches its description)  
**Used by:** [init](/docs/plugins/tsh-core/skills/init) (step 1 of its procedure), [authoring-claude-extensions](/docs/plugins/tsh-core/skills/authoring-claude-extensions) and [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records) (both hand memory-file work to it), [managing-domain-dictionaries](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) and [domain-dictionary](/docs/plugins/tsh-product-management/skills/domain-dictionary) (both point at it for repository adoption of a dictionary), [configuring-serverless-service](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) (its project-structure reference points at it for `CLAUDE.md`), and [initializing-project-context](/docs/plugins/tsh-product-management/skills/initializing-project-context) (via its generated context-repository `CLAUDE.md` template, which names this skill as the owner)

Puts a repository's conventions where Claude Code will actually load them, and keeps them true as the code changes. The mechanics are dictated by Claude Code's own loading rules: what loads at launch, what loads on demand, and what never loads at all. The failure it exists to prevent is a context file nobody can trust, such as a `CLAUDE.md` that states a build command which no longer works.

It owns the memory layer only: root and nested `CLAUDE.md`, `.claude/rules/`, and the decision-record index. If you are building a skill, subagent, hook or plugin, [authoring-claude-extensions](/docs/plugins/tsh-core/skills/authoring-claude-extensions) is the right skill.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Four layers** | Orientation (root `CLAUDE.md`, loads every session), conventions (`.claude/rules/*.md` with `paths:`, load when a matching file is read), locality (a nested `CLAUDE.md`, loads when a file in its subtree is read), decisions (`docs/decisions/` behind an index) |
| **Routing predicate** | Seven questions asked in order: multi-step procedure (skill), must hold regardless (hook), needed before the file exists (skill), only for existing files matching a pattern (path-scoped rule), owned by one directory (nested `CLAUDE.md`), a decision with a status (ADR), needed every session (root `CLAUDE.md`, the last resort) |
| **Root `CLAUDE.md`** | Under 200 lines, root and nested alike. It answers four questions (what the repo is; how to build, test and run it; what a newcomer would get wrong; where everything else is) and cuts anything Claude can derive from the codebase or a linter enforces |
| **Path-scoped rules** | Every rule gets a `paths:` glob unless it applies to every session; every glob must match at least one existing file today. Covers the brace-expansion budget and the unescaped `[` trap |
| **Timing trap** | A path-scoped rule fires when Claude reads a matching file, not when it writes one, so creation-time guidance belongs in a skill. The symptom: the convention is honoured on edits and ignored on creation |
| **Decision index** | Four columns (path, tags, one-line description, status), a binding note stating that only `Accepted` records bind, and a backticked pointer from root `CLAUDE.md`. Written bare with a leading `@`, the path becomes an import and loads at launch |
| **Monorepos** | Split downward into nested `CLAUDE.md` files when the root grows per-package sections; ownership, not file count, decides between a nested file and a path-scoped rule. Also covers start directory and `claudeMdExcludes` |
| **Domain dictionary** | A two-tier projection: a vocabulary block of about 15 lines in the root file, the full dictionary on demand at `docs/domain-dictionary.md`, and an edit-time rule that points at it. The dictionary is exempt from the "never write a derivable fact" rule |
| **Drift audit** | Verifies every command, path, version and "always"/"never" rule against current code, prunes derivable content, finds contradictions, and reports instead of silently rewriting |
| **Bootstrap and migration** | First-pass inspection order, `/init` and `/import`, and a mapping from GitHub Copilot instruction files (`.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, prompts) to their Claude Code equivalents |

## How It Works

1. **Inventory what already loads, then branch.** Run `/context`, read every file under Memory files, and look for what has not loaded yet (nested `CLAUDE.md`, `.claude/rules/`, `AGENTS.md`, `.github/copilot-instructions.md`, `.cursor/rules/`). Nothing found leads to the bootstrap reference; something found leads to the drift-audit reference.
2. **Choose the layer for every fact.** Each candidate instruction goes to exactly one layer, decided before any file is written.
3. **Gather and verify.** Read build files, CI configuration and test setup, run the commands being documented, and confirm every path exists. A convention seen in one file is a guess.
4. **Write the layers, thin, pointing downward.** Root orients and points; conventions go to scoped rules; area-owned conventions go to a nested `CLAUDE.md`.
5. **Wire the decision index, if decision records exist or are wanted.** Create or update `docs/decisions/README.md` and reference it from root `CLAUDE.md` in backticks, with the `Accepted`-only sentence in both places.
6. **Verify what actually loads.** Run `/context` again and confirm that the expected files appear under Memory files and the scoped ones are absent until a matching file is read.

## Rules It Enforces

| Rule | Why |
| :-- | :-- |
| Verify every command, path, version and convention before writing it | A wrong command teaches the model that the file is unreliable |
| Never use `@path` imports to save context | Imports load in full at launch; they organise, they never save |
| Move any multi-step procedure out of `CLAUDE.md` into a skill | `CLAUDE.md` holds facts, not workflows |
| Never overwrite an existing `CLAUDE.md` wholesale | It is a statement of team intent; revise in place and report what changed |
| Never remove, edit or summarise a block fenced by `<!-- tsh:<name> START` ... `<!-- tsh:<name> END -->` | A TSH tool owns it and rewrites it itself |
| Treat only `Accepted` decision records as binding | Other statuses are history, and a `Superseded` record is never read without its successor |

## What It Does Not Do

- Write or edit product code, configuration logic, tests or infrastructure.
- Decide what a convention should be; it records conventions the team already holds and asks when one is ambiguous.
- Author the prose inside a decision record, or mark a record accepted or superseded.
- Configure permissions, hooks or MCP servers, or write to `~/.claude/` without being asked.

## Reference Files

| Reference | Load when |
| :-- | :-- |
| `choosing-the-layer.md` | Before writing or moving any instruction, every time |
| `writing-claude-md.md` | Creating or trimming a root or nested `CLAUDE.md` |
| `writing-path-scoped-rules.md` | Recording a convention that applies to some files but not all |
| `monorepos-and-scale.md` | The repository has packages or subsystems with different owners |
| `indexing-decision-records.md` | Wiring ADRs into context, or decisions exist but go unread |
| `adopting-a-domain-dictionary.md` | A domain dictionary is being adopted, or the repository already has one |
| `bootstrapping-a-repository.md` | The inventory found no existing context files |
| `auditing-for-drift.md` | The inventory found existing context files |

## Related Skills

- [init](/docs/plugins/tsh-core/skills/init): the one command that runs this skill together with its neighbours and wires the maintenance pointers.
- [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records): owns record format, numbering and status lifecycle; this skill owns only the index and its wiring.
- [writing-technical-documents](/docs/plugins/tsh-core/skills/writing-technical-documents): owns the prose inside a decision record.
- [authoring-claude-extensions](/docs/plugins/tsh-core/skills/authoring-claude-extensions): owns skills, subagents, hooks and plugins.

## Source

- [`plugins/tsh-core/skills/managing-claude-context/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/managing-claude-context/SKILL.md)
- [`plugins/tsh-core/skills/managing-claude-context/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-core/skills/managing-claude-context/references)
