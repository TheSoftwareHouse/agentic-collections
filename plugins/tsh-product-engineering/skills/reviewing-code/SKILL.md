---
name: reviewing-code
description: "TSH's pre-merge review of a delivered change set: reads the plan and requirements first, compares the implementation against what was agreed, judges test coverage per layer, actually executes the project's tests, linters and build, then checks high-risk anti-patterns, security, and scalability. Use when a change set, task, or PR must be judged against its plan or acceptance criteria with its suites actually run, not read as a diff."
when_to_use: "Trigger on: 'review this code', 'review this PR', 'is this ready to merge', verifying an implementation against its *.plan.md or acceptance criteria, judging whether a change is adequately tested, or the review gate closing an implementation workflow. Executes the project's own suites as part of the review; reports findings and never fixes code."
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
| MUST | Ground every result in executed evidence: verbatim output from commands run in this review, or a `gate-runner` report embedded in the delegation. Never accept "tests pass" from the party that wrote the code. |
| MUST | Treat missing integration coverage as a substantive finding when correctness depends on a real database, transaction boundaries, SQL semantics, migrations, queues, or external services. Unit tests alone do not cover those. |
| MUST | Check every change for the high-risk anti-patterns listed below and report each hit unless the context documents a justified tradeoff. |
| MUST | Give every finding a severity, evidence (file and line), the consequence, and the minimum correction. No redesigns. |
| MUST | Run each suite, gate and build once. A failure is a finding, not a retry loop — record it verbatim and move on. |
| NEVER | Write to the working tree. Run formatters and autofixers in check mode only; a reviewer reports drift, it never fixes it. |
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
- [ ] 4. Establish gate evidence
- [ ] 5. Best practices and anti-patterns
- [ ] 6. Security
- [ ] 7. Scalability
- [ ] 8. Report findings
```

**Step 1 — Understand the task and the plan.** Read the research notes, the plan, and
the project's instructions (`CLAUDE.md`, rules, decision records) for the touched
area. Establish what was supposed to change and by what standard.

**Step 2 — Compare implementation to both.** Walk the diff of the delegated change
set against the plan's tasks and the task description, opening surrounding files only
where a finding needs their context — never re-read whole packages. Look beyond the
diff where the plan makes claims: verify that things it marked as `reuse` or "already
implemented" actually exist and behave as claimed.

**Step 3 — Judge test coverage.** Every critical path needs coverage from the right
layer — unit, integration, or e2e. Apply the integration-coverage rule from the
table.

**Step 4 — Establish gate evidence.** When the delegation embeds a `gate-runner`
report, that is the execution evidence: confirm its command list covers the scope —
static gates, the formatter in check mode, unit and integration suites, the build —
and run only what it missed. Otherwise run the gates yourself with the project's own
commands (the plan's Technical Context lists them), static gates first: a failed
build skips the suites, which can only fail for the same reason. Keep suite output
out of your context — prefer the quiet or CI reporter, or redirect to a file and read
back only the summary and failure blocks. Each command runs once: record failures
verbatim as findings rather than fixing and re-running. Scope comes from the caller:
a standalone review with no stated scope runs everything, e2e included; when the
delegation assigns functional and e2e verification to a parallel verifier, exclude
those suites and record the exclusion in the report.

This is the plan's one full pass. Earlier tiers ran deliberately narrow — tasks over
their own files, phases over their own package — so a gate you are running for the
first time here is the design working, not a coverage gap to report.

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

Ships in this plugin — if this skill loaded, it is installed.

- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  establishes the conventions the review judges against.
