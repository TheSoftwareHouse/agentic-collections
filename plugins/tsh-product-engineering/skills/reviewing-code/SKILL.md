---
name: reviewing-code
description: "Runs TSH's structured code review of a delivered change set: implementation compared against its plan and requirements, test coverage judged and test suites executed, best practices and high-risk anti-patterns checked, then static analysis, security, and scalability. Use when reviewing implemented changes, a pull request, or a finished task against its plan."
when_to_use: "Trigger on: 'review this code', 'review this PR', verifying an implementation against its plan or acceptance criteria, a pre-merge quality check, or judging whether a change set is adequately tested."
---

# Reviewing Code

A review here is evidence-based: run the checks, read the code, compare against what
was agreed. The plan and requirements are comparison context — never review targets
themselves. Findings are reported to the caller; the reviewer does not fix code and
does not do plan bookkeeping (checking Definition of Done boxes belongs to whoever
orchestrates the fix loop).

## When to Use

- A delivered change set (feature, fix, refactor) needs review before merge.
- An implementation must be verified against its `*.plan.md` and acceptance criteria.
- The user asks whether a change is correctly and sufficiently tested.

## Applicability and Precedence

Project-specific review checklists and conventions outrank this skill — apply them
first and use this process to fill what they leave unstated.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Read the task context and plan (`*.plan.md`, ticket, research notes) before reading the diff. A review without the intent is a style check. |
| MUST | Actually execute the relevant test suites, linters, and build — never accept "tests pass" from the implementation report. |
| MUST | Treat missing integration coverage as a substantive finding when correctness depends on a real database, transaction boundaries, SQL semantics, migrations, queues, or external services. Unit tests alone do not cover those. |
| MUST | Check every change for the high-risk anti-patterns listed below and report each hit unless the context documents a justified tradeoff. |
| MUST | Give every finding a severity, evidence (file and line), the consequence, and the minimum correction. No redesigns. |
| NEVER | Report cosmetic or wording-only notes as findings, pad a clean review with invented issues, or escalate severity because an issue repeats — consolidate instead. |

## High-risk anti-patterns

Always checked, always substantive when found:

- **N+1 access patterns** — queries in loops, per-item lazy loading, repeated
  external fetches while iterating entities one by one.
- **In-memory data processing** — pagination, filtering, sorting, or aggregation done
  in application memory after loading large datasets, instead of pushed down to the
  database or upstream service.
- **Missing integration tests** for behavior that depends on a real database or an
  external service boundary.

## Review Procedure

Copy this checklist and track progress:

```text
Review progress:
- [ ] 1. Understand the task and the plan
- [ ] 2. Compare implementation to both
- [ ] 3. Judge test coverage
- [ ] 4. Run tests, linters, and build
- [ ] 5. Best practices and anti-patterns
- [ ] 6. Security
- [ ] 7. Scalability
- [ ] 8. Report findings
```

**Step 1 — Understand the task and the plan.** Read the research notes, the plan, and
the project's instructions (`CLAUDE.md`, rules, decision records) for the touched
area. Establish what was supposed to change and by what standard.

**Step 2 — Compare implementation to both.** Walk the change set against the plan's
tasks and the task description. Look beyond the diff: verify that things the plan
marked as `reuse` or "already implemented" actually exist and behave as claimed.

**Step 3 — Judge test coverage.** Every critical path needs coverage from the right
layer — unit, integration, or e2e. Apply the integration-coverage rule from the
table.

**Step 4 — Run tests, linters, and build.** Unit, integration, and e2e suites as they
exist in the project, then static analysis, formatting, and the build. Use the
project's own commands (the plan's Technical Context lists them). Record failures
verbatim.

**Step 5 — Best practices and anti-patterns.** Check against project standards first,
then general practice (SOLID, DRY, KISS, low cognitive complexity — and no
over-engineering: flag speculative abstraction as readily as duplication). Then the
high-risk anti-pattern list above.

**Step 6 — Security.** Check for OWASP Top 10 classes relevant to the change —
injection, broken auth/authz, sensitive-data exposure — and anything that would let
one user act as another.

**Step 7 — Scalability.** Statefulness that blocks horizontal scaling, unbounded
memory growth, and needlessly high computational complexity on hot paths.

**Step 8 — Report.** Findings ordered by severity (blocker / major / minor), each
with evidence, consequence, and minimum correction; then what was executed and its
results; then what passed. A clean review says so plainly.

## Related Skills

Optional and may not be installed — treat each as a bonus, never a prerequisite.

- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  establishes the conventions the review judges against.
