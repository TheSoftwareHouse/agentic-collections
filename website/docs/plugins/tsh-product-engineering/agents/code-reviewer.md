---
title: Code Reviewer
sidebar_label: code-reviewer
sidebar_position: 1
description: Reviews a delivered change set against its plan and requirements by executing the checks itself, and returns a structured findings report without fixing code.
sources:
  - plugins/tsh-product-engineering/agents/code-reviewer.md
sources_hash: "8ac023bcc3d316753b68da6709b015fe707357924f6a77fe896d6aee7aae3719"
---

# Code Reviewer

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Mention:** `@tsh-product-engineering:code-reviewer`  
**Model:** `opus`  
**Tools:** no `tools` list in the frontmatter; `disallowedTools: Write, Edit`  
**Skills preloaded:** [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code), [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context)

Verifies that a delivered change set does what was agreed, to the project's standards, with evidence. It does not fix code and does not edit the plan. It reports, and the caller routes fixes and does the bookkeeping. Use it after implementation tasks complete, before merge.

## Inputs it expects

The delegation should name the plan file path (or the ticket and requirements) and the change set to review: a list of changed files, a branch or a diff. If it cannot determine what changed, it says so and reviews nothing rather than guessing a scope.

## Responsibilities

- Follows the `reviewing-code` skill in full: understands the task and plan, compares the implementation to both, judges test coverage, executes test suites, linters and the build with the project's own commands, then checks best practices, high-risk anti-patterns, security and scalability.
- When the change targets a framework or stack whose skill is available in the session, loads it and applies its framework-specific review checklist alongside `reviewing-code`'s. It loads whichever are present and never names one that is absent.
- Treats the plan as comparison context, never as a review target. Plan wording, structure and checkboxes are out of scope.
- Runs every check itself. An implementation report claiming that tests pass is a claim, not evidence.
- Takes suite scope from the delegation. When the delegation states that a parallel verifier covers functional and E2E verification, it runs static checks, unit and integration suites and the build only, and names the exclusion under Checks executed. With no stated scope it runs everything.
- Reports an unclear intent behind a deviation from the plan as a question in its findings, rather than assuming it is a defect.

## What it returns

A structured report:

1. **Verdict:** approve, or changes needed, in one line.
2. **Findings,** ordered blocker, major, minor. Each has file and line, what is wrong, the consequence and the minimum correction. Repeats are consolidated.
3. **Checks executed:** every command run, verbatim, with pass or fail and failure output where relevant.
4. **Coverage assessment:** critical paths and which test layer covers each, naming any behavior that depends on a database, transactions, queues or external services and lacks integration coverage.
5. **What passed,** briefly. A clean review reports zero findings plainly and never invents issues.

## Used by

- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) delegates to it in the plan's final verification phase, concurrently with [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier), and as a single full-scope review for a legacy plan without that phase.
- [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) defines the code-review task of the final verification phase that is delegated to it.

## Source

[`plugins/tsh-product-engineering/agents/code-reviewer.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/agents/code-reviewer.md)
