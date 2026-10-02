---
name: init
description: "One-shot setup of a project's Claude Code context. Audits what already loads, then creates or repairs root and nested `CLAUDE.md`, path-scoped rules, and the decision-record archive with its index by running the owning tsh-core skills in order, and wires maintenance pointers into `CLAUDE.md` so future sessions keep it all current. Run /tsh-core:init inside the repository to set up."
disable-model-invocation: true
---

# Init

The one command that takes a repository from any starting state — nothing, a
partial setup, or a drifted one — to a complete, wired set of context primitives:
a root `CLAUDE.md` (nested ones where ownership demands), path-scoped rules in
`.claude/rules/`, a decision-record archive with its index, and a maintenance
section telling every future session which skill keeps each artifact true.

**The failure this skill exists to prevent is a half-initialized repository.** A
`CLAUDE.md` with no decision index, an ADR directory nothing references, a setup
done once with no note saying how it is maintained — each looks finished and
quietly stops paying off.

> **Scope boundary.** This skill owns the **sequence and the wiring** — which
> skill runs when, and the maintenance section in `CLAUDE.md`. Every rule about
> the artifacts themselves belongs to the owning skill:
> [`managing-claude-context`](../managing-claude-context/SKILL.md) for the memory
> layer, [`managing-decision-records`](../managing-decision-records/SKILL.md) for
> record format and lifecycle. This skill loads their rules; it never restates
> them.

## When to Use

- A user runs `/tsh-core:init` — this skill is user-invoked only and never loads
  by description match
- Setting up a repository for the first time, or re-running after a template or
  fork left context files describing the wrong project
- A repository whose setup is partial or drifted — running init again is repair,
  not a rewrite

## Applicability and Precedence

Everything `managing-claude-context` and `managing-decision-records` state about
precedence applies unchanged here: an existing `CLAUDE.md` is revised in place, an
existing ADR convention and location win over the defaults, and Claude Code's own
documentation outranks all of it. Init adds one thing — it is safe to run
repeatedly, and a second run must converge to "nothing to do", never re-create
what the first run built.

## Explicit Exclusions

This skill does not:

- restate, soften or override any rule owned by the skills it orchestrates — with
  one addition of its own, marked in the rules table: the decision index is always
  left in place
- write or edit product code, configuration logic, tests, or infrastructure
- invent a convention or a decision — it records what exists and asks about the
  rest
- write a decision record's body, or set a status — it proposes candidates and
  hands the writing to [`managing-decision-records`](../managing-decision-records/SKILL.md)
- install plugins, configure permissions, or write outside the repository

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Execute `managing-claude-context`'s procedure in full as Step 1, starting with its inventory. Init never writes before that audit has run. |
| NEVER | Overwrite an existing `CLAUDE.md` wholesale. Revise in place and report what changed. (Owned by `managing-claude-context`; restated because it blocks.) |
| MUST | Read the owning skill's `SKILL.md` before touching its artifact — never work its area from memory. |
| MUST | Leave the repository with a decision index — `docs/decisions/README.md`, or the existing archive location — even when no decision has been recorded yet. An empty indexed archive is the correct starting state. (Init's own rule, not the owner's: `managing-claude-context` wires an index only where records exist or are wanted; a bootstrap counts as wanting one.) |
| NEVER | Invent a decision record to fill an empty archive. Propose candidates in the report; a human confirms and `managing-decision-records` governs the writing. |
| MUST | Wire the maintenance section into root `CLAUDE.md` exactly per `./references/wiring-tsh-core-skills.md` — conditional phrasing, every path in backticks, never a leading `@`. |
| MUST | End with a report of what was created, what was repaired and what was left alone, and flag the result as a proposal for human review. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [managing-claude-context](../managing-claude-context/SKILL.md) | Step 1, before writing anything | The memory layer: inventory, bootstrap vs. drift audit, layer choice, `CLAUDE.md` and `.claude/rules/` rules, decision-index wiring |
| [managing-decision-records](../managing-decision-records/SKILL.md) | Step 2, when a record is proposed or the archive's shape is in question | Record format, numbering, status vocabulary and lifecycle |
| [Wiring tsh-core skills](./references/wiring-tsh-core-skills.md) | Step 3, before writing or repairing the maintenance section | The canonical maintenance block, why its phrasing is conditional, repairing a stale variant, adapting paths |

## Procedure

**Step 1 — Establish the memory layer.** Read
[`managing-claude-context`](../managing-claude-context/SKILL.md) and execute its
procedure in full. Its own first step inventories what loads and branches —
nothing found → bootstrap, something found → drift audit — and its Step 5 wires
the decision index. Run it through its self-check even when the repository looks
already set up: repair is this command's job as much as creation.

**Step 2 — Ensure the decision archive exists.** If Step 1 left the repository
without one, create the index — default `docs/decisions/README.md`; an existing
archive location wins — with the binding note and an empty four-column table, per
the indexing reference `managing-claude-context` loads. Do not backfill records:
when the codebase clearly embodies undocumented decisions, list them as
candidates in the final report and point at
[`managing-decision-records`](../managing-decision-records/SKILL.md) instead of
writing them.

**Step 3 — Wire the maintenance section.** Read
[`wiring-tsh-core-skills.md`](./references/wiring-tsh-core-skills.md), then add
the section to root `CLAUDE.md` — or repair the existing variant in place. It
counts against the 200-line budget like every other line.

**Step 4 — Verify and report.** Run `/context` and confirm everything written or
repaired loads, or is scoped to load on read. Report three lists — created,
repaired, left alone — plus any decision candidates from Step 2, and close by
flagging the setup as a proposal for the team to review, not a finished artifact.

## Self-check Before Handoff

```text
- [ ] managing-claude-context's procedure ran in full, inventory first, self-check included
- [ ] No existing file was overwritten wholesale; every revision is reported
- [ ] Every artifact was written under its owning skill's rules, loaded not recalled
- [ ] A decision index exists, at the default or the repository's own location
- [ ] No decision record was invented; candidates are listed for a human
- [ ] The maintenance section is in root CLAUDE.md — conditional, backticked, no bare @
- [ ] /context confirms the result loads
- [ ] The report lists created / repaired / left alone and calls the result a proposal
```
