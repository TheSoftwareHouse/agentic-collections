---
name: discovering-technical-context
description: "Establishes a project's conventions, patterns, and standards before code is written, in a fixed priority order: context already persisted in the plan, then project instructions, then existing codebase patterns, then external documentation. Use before implementing in an unfamiliar codebase or when deciding which convention a change should follow."
when_to_use: "Trigger on: onboarding to a new area of a codebase, starting implementation or test-writing in an unfamiliar project, conflicting conventions in the same repository, 'how does this project do X', or populating a plan's Technical Context section."
---

# Discovering Technical Context

A systematic way to learn how a project does things before changing it, so new code
is consistent with what exists and conventions are followed rather than reinvented.
The output is often persisted into a plan's Technical Context section, where it saves
every later agent from rediscovering the same facts.

## When to Use

- Before implementing any feature or fix in code you have not worked in recently.
- Before writing tests — unit, integration, or e2e — in an unfamiliar project.
- When two parts of the repository disagree and you must pick a convention.
- When filling the Technical Context section of an implementation plan.

## Applicability and Precedence

This skill is itself a precedence rule: project instructions outrank existing
patterns, which outrank industry best practice. Nothing here overrides an explicit
instruction from the user.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Check the plan's Technical Context first. If it is populated, use it as-is and re-discover only what it does not cover. |
| MUST | Treat project instructions (`CLAUDE.md`, path-scoped rules, decision records) as the primary source of truth when they exist. |
| MUST | Mirror existing codebase patterns when instructions are silent — consistency with the code beats theoretical best practice. |
| MUST | Check the exact dependency versions in the project's manifest before consulting external documentation. |
| NEVER | Introduce a new pattern unless the user or the plan explicitly asks for one. |

## Discovery Procedure

Copy this checklist and track progress:

```text
Discovery progress:
- [ ] 0. Persisted context in the plan
- [ ] 1. Project instructions
- [ ] 2. Existing codebase patterns
- [ ] 3. External documentation (only if needed)
- [ ] 4. Apply the decision hierarchy
```

**Step 0 — Persisted context.** If a `*.plan.md` exists for the task and its
Technical Context section is populated, use it and skip to Step 4. Run Steps 1–2 only
for aspects it does not cover.

**Step 1 — Project instructions.** Read, where present: the root `CLAUDE.md` and any
nested ones near the touched files; path-scoped rules under `.claude/rules/`;
decision records (`docs/decisions/` or similar); `CONTRIBUTING.md` or equivalent.
These are the primary source for coding standards, architecture and layering,
stack versions, testing strategy, and naming.

**Step 2 — Existing codebase patterns.** For whatever the instructions leave
unstated, find the nearest similar implementation and replicate its approach:

- **Architecture** — folder structure, layering, module organization.
- **Style and idiom** — naming, formatting, import conventions.
- **Error handling and validation** — how failures are caught, logged, surfaced.
- **Testing** — structure, mocking strategy, assertions, fixtures, test data.
- **Persistence** — migrations, entities, query patterns.
- **API surface** — response shapes, status codes, documentation style.
- **Configuration** — env vars, feature flags, secrets handling.

**Step 3 — External documentation.** Only when neither instructions nor codebase
answer (greenfield project, first use of a pattern): read the official docs for the
exact versions the manifest pins, apply industry standards (OWASP for security,
SOLID and established design patterns where they fit), and document the decisions you
make so they become the project's pattern.

**Step 4 — Apply the decision hierarchy.**

| Context available | Action |
| --- | --- |
| Project instructions cover it | Follow them strictly — they outrank general best practice. |
| Instructions silent, codebase has a pattern | Mirror the existing pattern exactly. |
| Neither exists | Apply documented best practice and record the decision for the next person. |

## Related Skills

Optional and may not be installed — treat each as a bonus, never a prerequisite.

- [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md) —
  persists what this skill discovers into the plan's Technical Context.
