---
title: Reviewing Code
sidebar_label: reviewing-code
sidebar_position: 6
description: TSH's evidence-based pre-merge review of a delivered change set, comparing it with the plan, running the project's checks and applying anti-pattern, security and scalability checks.
sources:
  - plugins/tsh-product-engineering/skills/reviewing-code/
sources_hash: "c316c76db2fa4654f111972443deee74b6701830dd697612d0a06f33ca4263dc"
---

# Reviewing Code

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:reviewing-code`  
**Used by:** the [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) agent preloads it. [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) applies it as the standard of the final review gate, and [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) names it as the judge of a finished fix.

A review here is evidence-based: run the checks, read the code, compare against what was agreed. The plan and requirements are comparison context and never review targets themselves. Findings are reported to the caller. The reviewer does not fix code and does not do plan bookkeeping, since checking Definition of Done boxes belongs to whoever orchestrates the fix loop.

Use it when a delivered change set (feature, fix or refactor) needs review before merge, when an implementation must be verified against its `*.plan.md` and acceptance criteria, or when the user asks whether a change is correctly and sufficiently tested. A pasted diff, a task or a PR are all valid inputs. Project-specific review checklists and conventions outrank the skill; it fills what they leave unstated.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Intent first** | The task context and plan (`*.plan.md`, ticket, research notes) are read before the diff, because a review without the intent is a style check |
| **Executed checks** | Relevant test suites, linters and the build are actually run. "Tests pass" from an implementation report is never accepted |
| **Test coverage by layer** | Every critical path needs coverage from the right layer. Missing integration coverage is a substantive finding when correctness depends on a real database, transactions, SQL semantics, migrations, queues or external services |
| **High-risk anti-patterns** | N+1 access patterns, in-memory data processing that should be pushed down to the database or upstream service, and missing integration tests for behavior that depends on a real database or external boundary |
| **Security baseline** | A universal, framework-agnostic checklist applied on every review (see below) |
| **Stack-specific checks** | When the change targets a framework whose stack skill is available in the session, that skill is loaded and its review checklist applied alongside. Whichever are present are loaded; none that is absent is named |
| **Finding contract** | Every finding has a severity, evidence (file and line), the consequence and the minimum correction. No redesigns |
| **Honest reporting** | No cosmetic or wording-only findings, no invented issues to pad a clean review, and no severity escalation because an issue repeats |
| **Leftover files** | A module the change moved or renamed must leave nothing behind. A file at the old path that only re-exports the new one is a finding, unless it is the public API of a package other code consumes and is marked deprecated, or the plan stages it as transitional |

## Security baseline

The reference `security-review-checklist.md` is loaded in step 6 of every review. It is a floor, not a ceiling: a project's own security rules outrank it and apply first, and the installed stack skill's security rows run on top. A full audit is a different task. The baseline maps to OWASP Top 10 classes and each row names what to look for in the diff, a typical severity and the minimum correction:

- broken access control, and object-level access control (IDOR)
- mass assignment and over-posting
- injection
- unsafe deserialization and dynamic evaluation
- SSRF
- open redirect
- sensitive data exposure
- hardcoded secrets
- cryptographic failures
- authentication weaknesses
- vulnerable dependencies
- security misconfiguration

Missing authorization on a new entry point and object-level authorization are called out as the highest-frequency, highest-severity misses. The checklist also states its limits: it reads a diff, and a clean pass means "no issues in these classes were found in this change", never "this change is secure".

## How it works

1. **Understand the task and the plan,** including the project's instructions for the touched area.
2. **Compare the implementation to both.** Walk the change set against the plan's tasks, and verify that things marked `reuse` or "already implemented" exist and behave as claimed.
3. **Judge test coverage** per layer.
4. **Run tests, linters and build** with the project's own commands, recording failures verbatim. A standalone review with no stated scope runs everything, E2E included. When the delegation assigns functional and E2E verification to a parallel verifier, those suites are excluded and the exclusion is recorded.
5. **Check best practices and anti-patterns,** loading the stack skill when one is available.
6. **Security,** with the baseline checklist.
7. **Scalability:** statefulness that blocks horizontal scaling, unbounded memory growth and needlessly high computational complexity on hot paths.
8. **Report** findings ordered by severity (blocker, major, minor), then what was executed and its results, then what passed. A clean review says so plainly.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| `security-review-checklist.md` | Step 6, every review |

## Related skills

- [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) establishes the conventions the review judges against.

## Source

[`plugins/tsh-product-engineering/skills/reviewing-code/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/reviewing-code/SKILL.md)
