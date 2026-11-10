---
title: Init
sidebar_label: init
sidebar_position: 2
description: One-shot setup of a repository's Claude Code context that runs the owning tsh-core skills in order and wires maintenance pointers into CLAUDE.md.
sources:
  - plugins/tsh-core/skills/init/
sources_hash: "7eb8ea486a7e8e1b7aa55575ad392a6601b4aa8871dd1760eeefb4bfa0876c2f"
---

# Init

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:init` (runs only when you invoke it; Claude never loads it from a prose request)  
**Used by:** no other skill or agent references it; it is a command you type once per repository

Takes a repository from any starting state (nothing, a partial setup, or a drifted one) to a complete, wired set of context files: a root `CLAUDE.md` (nested ones where ownership demands), path-scoped rules in `.claude/rules/`, a decision-record archive with its index, and a maintenance section that tells every future session which skill keeps each artifact true. It is safe to re-run: the second pass is a repair, and a second run must converge to "nothing to do".

`init` owns only the sequence and the maintenance pointers. Every rule about the artifacts themselves stays with the skill that owns them: [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context) for the memory layer and [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records) for record format and lifecycle.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Memory layer** | Runs the full `managing-claude-context` procedure first, starting with its inventory of what already loads. Nothing is written before that audit has run |
| **Decision archive** | Leaves the repository with a decision index (`docs/decisions/README.md`, or the repository's existing archive location) even when no decision has been recorded. An empty indexed archive is the correct starting state |
| **Maintenance section** | Adds a "Keeping context and decisions current" section to the root `CLAUDE.md`: update the memory files in the same change as the project change, and propose recording important decisions |
| **Conditional phrasing** | The section names the `/tsh-core:` skills only as "with the `tsh-core` plugin installed", and gives a manual fallback, because `tsh-core` installs per teammate while `CLAUDE.md` is read by every contributor |
| **Domain dictionary** | A third bullet joins the section only where the repository already has a domain dictionary (`docs/domain-dictionary.md` or its chosen path) |
| **Project checks** | With `tsh-product-engineering` installed, invokes `/tsh-product-engineering:capturing-project-checks`, which writes the project's verification and security-invariant skills under its own rules; without it, the report says so and names the command. `init` never writes those skills itself |
| **Report** | Ends with three lists (created, repaired, left alone), any decision-record candidates, and a flag that the setup is a proposal for human review |

## How It Works

1. **Establish the memory layer.** Execute `managing-claude-context` in full, even when the repository looks set up: repair is as much this command's job as creation.
2. **Ensure the decision archive exists.** If step 1 left no index, create it with the binding note and an empty four-column table. Do not backfill records: undocumented decisions the codebase clearly embodies are listed as candidates in the report, and writing them is handed to `managing-decision-records`.
3. **Wire the maintenance section.** Add the section to root `CLAUDE.md`, or repair an existing variant in place. It counts against the 200-line budget like every other line.
4. **Capture the project's checks.** With `tsh-product-engineering` installed, invoke [`capturing-project-checks`](/docs/plugins/tsh-product-engineering/skills/capturing-project-checks); without it, say so and name the command. A repository with no CI yet gets a thin result, and the block that skill writes says when to re-run it.
5. **Verify and report.** Run `/context`, confirm everything written or repaired loads (or is scoped to load on read), and report created, repaired and left alone.

## Rules It Enforces

| Rule | Why |
| :-- | :-- |
| Never overwrite an existing `CLAUDE.md` wholesale | Revise in place and report what changed |
| Never invent a decision record | Candidates go in the report; a human confirms, and `managing-decision-records` governs the writing |
| Every path in the maintenance section is in backticks, never a leading `@` | A bare `@` path becomes an import and loads the file at launch |
| Read the owning skill's `SKILL.md` before touching its artifact | Never work an artifact's area from memory |

## What It Does Not Do

- Restate, soften or override any rule owned by the skills it orchestrates, with one addition of its own: it always leaves a decision index in place, where `managing-claude-context` wires one only when records exist or are wanted.
- Write or edit product code, configuration logic, tests or infrastructure.
- Invent a convention or a decision; it records what exists and asks about the rest.
- Write a decision record's body or set a status; it proposes candidates and hands the writing to `managing-decision-records`.
- Install plugins, configure permissions, or write outside the repository.

## Related Skills

- [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context): run as step 1 of `init`; owns the memory layer.
- [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records): owns record format and lifecycle; `init` hands decision candidates to it.

## Source

- [`plugins/tsh-core/skills/init/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/init/SKILL.md)
- [`plugins/tsh-core/skills/init/references/wiring-tsh-core-skills.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/init/references/wiring-tsh-core-skills.md)
