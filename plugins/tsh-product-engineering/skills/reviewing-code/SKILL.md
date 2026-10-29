---
name: reviewing-code
description: "TSH's pre-merge review of a delivered change set — a pasted diff, a task, or a PR: reads the plan and requirements first, compares the implementation against what was agreed, judges test coverage per layer, runs the project's tests, linters and build when they are available, then checks high-risk anti-patterns, security, and scalability. Use when a change must be judged for merge readiness, whether it arrives as a pasted diff or a branch, against its plan or acceptance criteria when those exist."
when_to_use: "Trigger on: 'review this code', 'review this PR', 'review this diff before we merge', 'is this ready to merge', verifying an implementation against its *.plan.md or acceptance criteria, judging whether a pasted change or change set is adequately tested, or the review gate closing an implementation workflow. Runs the project's own suites as part of the review when available; reports findings and never fixes code."
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
| MUST | Run the universal security baseline in [`references/security-review-checklist.md`](./references/security-review-checklist.md) on every review. It is a floor: a project's own security rules outrank it and apply first, and the installed stack skill's security rows run on top. Missing authorization on a new entry point and object-level authz (IDOR) are the highest-frequency, highest-severity misses — check them on every change that adds or reaches a data access path. |
| MUST | When the change targets a framework or stack that has its own skill available in this session — a NestJS, Terraform, frontend, Python or similar stack skill — load that skill and apply its framework-specific review checklist. This skill owns the review that is the same for every stack; the stack skill owns what is specific to one, and a review of a framework change that skips it is incomplete. Load whichever such skills are present; name none that is absent. |
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

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Security review checklist](./references/security-review-checklist.md) | Step 6, every review | The universal security baseline — framework-agnostic OWASP classes worth checking on any change, each with what to look for in the diff and the minimum correction, plus how project rules, stack skills and named standards layer on top |

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
verbatim. Run the suites within the scope the caller set: a standalone review with no
stated scope runs everything, e2e included; when the delegation assigns functional
and e2e verification to a parallel verifier, exclude those suites and record the
exclusion in the report.

**Step 5 — Best practices and anti-patterns.** Check against project standards first,
then general practice (SOLID, DRY, KISS, low cognitive complexity — and no
over-engineering: flag speculative abstraction as readily as duplication). Then the
high-risk anti-pattern list above. When the change targets a framework or stack whose
skill is available this session, load it now and run its review checklist alongside
this one — it carries the framework-specific risks (for a NestJS change: CQRS
boundaries, TypeORM transaction and persistence semantics, DTO validation,
testability) that a stack-agnostic review does not name.

**Step 6 — Security.** Load
[`./references/security-review-checklist.md`](./references/security-review-checklist.md)
and run its universal baseline against the change — broken access control and
object-level authz (the most common and highest-severity classes), injection, unsafe
deserialization, mass assignment, sensitive-data exposure, hardcoded secrets, crypto
and auth weaknesses, SSRF, vulnerable dependencies, and security misconfiguration. The
checklist is a floor: a project's own security rules outrank it and are applied first,
and when a stack skill is available this session its security rows run on top of the
baseline. A change that only needs the baseline still gets it; nothing here replaces a
dedicated audit when the task is to audit a whole service rather than review a change.

**Step 7 — Scalability.** Statefulness that blocks horizontal scaling, unbounded
memory growth, and needlessly high computational complexity on hot paths.

**Step 8 — Report.** Findings ordered by severity (blocker / major / minor), each
with evidence, consequence, and minimum correction; then what was executed and its
results; then what passed. A clean review says so plainly.

## Related Skills

Ships in this plugin — if this skill loaded, it is installed.

- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  establishes the conventions the review judges against.
