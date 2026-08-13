---
name: managing-claude-context
description: "Sets up and maintains the project-context files Claude Code loads — root and nested `CLAUDE.md`, path-scoped rules in `.claude/rules/`, and a decision-record index — so a repository's conventions reach the model without bloating every session. Use when a repository has no `CLAUDE.md`, when Claude keeps ignoring a convention, or when the memory files have drifted from the code."
when_to_use: "Trigger on: setting up Claude Code in a new repository, a `CLAUDE.md` grown past 200 lines or gone stale, Claude repeatedly ignoring a convention, a monorepo needing nested `CLAUDE.md` files or path-scoped rules, indexing decision records, migrating instructions from GitHub Copilot or Cursor, or any request to audit what loads into Claude's context."
---

# Managing Claude Context

Puts a repository's conventions where Claude Code will actually load them, and
keeps them true as the code changes. The mechanics below are dictated by Claude
Code's own loading rules — what loads at launch, what loads on demand, and what
silently never loads at all — not by preference.

**The failure this skill exists to prevent is a context file nobody can trust.** A
`CLAUDE.md` that states a build command which no longer works is worse than no
file: the model follows it confidently and the reader stops checking.

## When to Use

- A repository has no `CLAUDE.md` and Claude keeps re-deriving the same conventions
- `CLAUDE.md` has grown past 200 lines, or covers areas the current task never touches
- Claude repeatedly ignores a convention the team considers settled
- A project has grown into a monorepo and one root file no longer fits
- Architecture decisions exist but Claude never finds them
- Instructions need migrating from GitHub Copilot, Cursor, or an `AGENTS.md`
- Conventions changed and nobody updated the memory files

## Applicability and Precedence

Read what already loads before writing anything. An existing `CLAUDE.md` is a
statement of team intent, not a draft to overwrite — revise it in place and report
what changed. Where a repository already has a documentation or ADR convention,
that convention wins over this skill's defaults.

`docs/decisions/` is this skill's **default** location for decision records, not a
requirement of Claude Code. A repository that already keeps ADRs elsewhere keeps
them there; only the index wiring described below is non-negotiable.

## Explicit Exclusions

This skill does not:

- write or edit product code, configuration logic, tests, or infrastructure
- decide what a convention *should be* — it records conventions the team already
  holds, and asks when a convention is ambiguous rather than inventing one
- author the prose inside a decision record; it defines the index and the wiring
  only, and hands the writing to
  [`writing-technical-documents`](../writing-technical-documents/SKILL.md)
- make an architectural decision, or mark an ADR accepted or superseded — that is a
  human call recorded after the fact
- configure permissions, hooks, or MCP servers
- write to `~/.claude/` or any path outside the repository without being asked

When a convention cannot be stated without a decision nobody has made, stop and name
the decision instead of writing a plausible rule.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Inventory what already loads before writing — run `/context` and read every file it lists under **Memory files**. |
| MUST | Verify every command, path, version and convention against the source before writing it into a memory file. |
| NEVER | Write a fact Claude can derive from the codebase — directory listings, dependency inventories, generated architecture overviews. |
| MUST | Keep every `CLAUDE.md` under 200 lines, root and nested alike. Adherence drops as the file grows. |
| MUST | Make each layer point downward to the next instead of inlining it. |
| MUST | Move any multi-step procedure out of `CLAUDE.md` into a skill. `CLAUDE.md` holds facts, not workflows. |
| MUST | Give every rule in `.claude/rules/` a `paths:` glob unless it genuinely applies to every session — a rule without one costs every session, forever. |
| MUST | Write the decision index reference in backticks as `` `docs/decisions/README.md` ``. Written bare with a leading `@` it becomes an import and loads the whole index at launch. |
| MUST | Give the decision index four columns — path, tags, one-line description, status. Tags carry the routing; an index without them is a list nothing can search. |
| NEVER | Use `@path` imports to reduce context. Imports load in full at launch; they organise, they never save. |
| MUST | Split downward into a nested `CLAUDE.md` once the root file grows per-package or per-subsystem sections. |
| NEVER | Overwrite an existing `CLAUDE.md` wholesale. Revise in place and report what changed and why. |
| MUST | Confirm what actually loaded with `/context` before reporting the work finished. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Choosing the layer](./references/choosing-the-layer.md) | Before writing or moving any instruction, every time | The four layers and the predicate for each; `CLAUDE.md` vs. rule vs. nested file vs. skill vs. hook vs. auto memory; the import and `/compact` traps |
| [Writing CLAUDE.md](./references/writing-claude-md.md) | Creating or trimming a root or nested `CLAUDE.md` | The content contract, the 200-line target, what to cut, section order, `AGENTS.md` interop |
| [Writing path-scoped rules](./references/writing-path-scoped-rules.md) | Recording a convention that applies to some files but not all | `.claude/rules/` mechanics, `paths:` globs, brace-expansion budget, the unescaped-`[` trap, sharing rules by symlink |
| [Monorepos and scale](./references/monorepos-and-scale.md) | The repo has packages or subsystems with different owners | Nested `CLAUDE.md` vs. path-scoped rules by ownership, the split trigger, start directory, `claudeMdExcludes`, per-directory skills |
| [Indexing decision records](./references/indexing-decision-records.md) | Wiring ADRs into context, or decisions exist but go unread | `docs/decisions/` layout, the index schema, statuses and superseding, the backtick-not-import wiring |
| [Bootstrapping a repository](./references/bootstrapping-a-repository.md) | Step 1 found no existing context files | The inspection order, `/init` and `/import`, migrating from Copilot or Cursor |
| [Auditing for drift](./references/auditing-for-drift.md) | Step 1 found existing context files | Verifying each claim against current code, pruning, `/doctor`, the `InstructionsLoaded` and `Stop` hooks |

## Procedure

**Step 1 — Inventory what already loads, then branch.** Run `/context` and read
every file listed under **Memory files**. Then look for what `/context` cannot show
because it has not loaded yet: nested `CLAUDE.md` files, `.claude/rules/`,
`AGENTS.md`, `.github/copilot-instructions.md`, `.cursor/rules/`. Report the
inventory before changing anything.

- **Nothing found** → read
  [`bootstrapping-a-repository.md`](./references/bootstrapping-a-repository.md).
- **Something found** → read
  [`auditing-for-drift.md`](./references/auditing-for-drift.md). Do not treat an
  existing file as a blank page.

**Step 2 — Choose the layer for every fact.** Read
[`choosing-the-layer.md`](./references/choosing-the-layer.md) **before writing any
file**. Each candidate instruction goes to exactly one layer, and the wrong layer is
the most common and most expensive mistake here: a convention placed in the root
file taxes every session forever, and a procedure placed there is ignored anyway.

**Step 3 — Gather and verify.** Read the build files, CI configuration, test setup
and a representative slice of source. Run the commands you intend to document.
Confirm every path exists. A convention you inferred from one file is a guess —
check a second, or ask.

**Step 4 — Write the layers, thin, pointing downward.** Root `CLAUDE.md` orients and
points. Conventions go to `.claude/rules/` with `paths:`. Area-owned conventions go
to a nested `CLAUDE.md` in the directory that owns them. If the repository has
packages or subsystems, read
[`monorepos-and-scale.md`](./references/monorepos-and-scale.md) **before deciding
between a rule and a nested file** — the deciding question is ownership, not count.

**Step 5 — Wire the decision index.** If decision records exist or are wanted, read
[`indexing-decision-records.md`](./references/indexing-decision-records.md) and
create or update `docs/decisions/README.md`, then reference it from root `CLAUDE.md`
in backticks. Write the index rows only; individual ADRs are drafted with
[`writing-technical-documents`](../writing-technical-documents/SKILL.md) and their
status is a human decision.

**Step 6 — Verify what actually loads.** Start a session and run `/context`. Confirm
the files you expect appear under **Memory files** and the ones you scoped are
absent until a matching file is read. A path-scoped rule that never triggers is
indistinguishable from one you never wrote.

## Self-check Before Handoff

Answer each line before reporting the work finished. Any "no" sends you back.

```text
- [ ] `/context` was run at the start and again at the end
- [ ] Every command, path and version was executed or checked against the source
- [ ] No root or nested CLAUDE.md exceeds 200 lines
- [ ] Nothing was written that Claude could derive from the codebase
- [ ] Every rule in .claude/rules/ has paths:, or justifies loading every session
- [ ] The decision index is referenced in backticks, with no bare @ import anywhere
- [ ] No multi-step procedure was left in a CLAUDE.md
- [ ] An existing CLAUDE.md was revised in place, and the changes were reported
- [ ] Every convention written down is one the team holds, not one I invented
```
