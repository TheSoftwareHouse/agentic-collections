---
title: Creating Implementation Plans
sidebar_label: creating-implementation-plans
sidebar_position: 2
description: Writes TSH's implementation plan as a committed file with phased tasks that each name their files and a verifiable Definition of Done, plus a verification document for the final phase.
sources:
  - plugins/tsh-product-engineering/skills/creating-implementation-plans/
sources_hash: "0ce3b6a21895e91b7be8ea33842db326917ab9fe460125f497b4c6154b1156cb"
---

# Creating Implementation Plans

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:creating-implementation-plans`  
**Used by:** [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) requires it when a task has no plan file, and [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) hands an established root cause to it when a fix outgrows a minimal change. [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) names it as the consumer of the context it discovers. No agent preloads it.

Turns a designed solution into a plan document that a human can review in minutes and an implementer subagent can execute without seeing the conversation. The plan is a file, not a chat message: it survives the session, travels in a commit, and is the single handoff artifact for delegated implementation. The default location is `specifications/<task-id>/<task-name>.plan.md`.

Use it when a plan, spec or task breakdown is asked for, when an existing `*.plan.md` needs revision, or when work will be delegated to implementer subagents, possibly several in parallel. It writes the plan only; executing it is `orchestrating-feature-implementation`. If the project has its own planning convention, that convention outranks this skill.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Plan as a file** | Saved at `specifications/<task-id>/<task-name>.plan.md`, where the task ID is the ticket ID or a short kebab-case name |
| **Deliberate sections** | Sections are chosen from a menu of building blocks, so depth matches task risk: a config tweak gets a goal and two tasks, a schema migration gets the full treatment |
| **No implementation code** | Type definitions, function signatures, DTOs and API shapes may pin a contract. Pseudo-code is allowed only for genuinely complicated algorithms |
| **Files per task** | Every task names each file it touches in a `**Files:**` field, labeled `create`, `modify` or `reuse` |
| **Checkboxes** | Every task and every Definition of Done item is a `- [ ]` checkbox, because implementer agents tick their own scope and a plan without checkboxes silently loses progress tracking |
| **Definition of Done** | At least one objectively verifiable check per task, with commands taken verbatim from the plan's Technical Context and scoped to the task's own files. Never directory- or project-wide suites |
| **Parallel groups** | Tasks qualify for a group only when neither depends on the other's output and their `**Files:**` lists are disjoint. When unsure, they are not independent |
| **Final verification phase** | Every non-trivial plan ends with a code-review task and a functional-verification task that can run in parallel |
| **Scope** | Only the current task is planned. Prerequisites and follow-ups go under Improvements (Out of Scope), not into extra phases |
| **No bookkeeping** | No approval tables, revision predicates or status bookkeeping. The user approves by reading the plan and saying so |

## Building blocks

The reference `plan-building-blocks.md` explains when each section earns its place: Task Details, Goal (always included, with a Success Measure and a Do NOT touch list), Proposed Solution, Current Implementation Analysis, Open Questions, Technical Context, Phases and Tasks, Parallel groups, Final Verification Phase, Security Considerations, Acceptance Criteria, Improvements (Out of Scope) and Changelog.

Technical Context is persisted so implementer subagents, which start with no conversation history, never rediscover the stack, conventions, test patterns and verification commands. When the plan takes over a bug from `debugging-code`, it also holds the established root cause: the causal chain with its evidence, and the measured reach of the fix.

Each phase carries a `**Verification:**` line: one integration-level check of what the phase's tasks created plus one typecheck or build, never a repeat of the task Definitions of Done and never a full suite.

## The final verification phase

The last phase of every non-trivial plan holds exactly two tasks that run in parallel:

- **Code review**, delegated to `code-reviewer` with the plan path and the changed-file list. It runs static checks, unit and integration suites and the build itself, and the delegation states that functional and E2E verification runs in the parallel verifier.
- **Functional verification**, delegated to `feature-verifier` with the path to the verification document. It executes the document's scenarios against the running app.

The verification document lives at `specifications/<task-id>/<task-name>.verification.md`. It is drafted at planning time, with the user, who decides which functional checks it includes before implementation starts. Its building blocks are a header, an Environment section, optional Seeding, numbered Scenarios, pass criteria with the report shape, and Boundaries. Scenarios carry one of five tags:

| Tag | Evidence required |
| :-- | :-- |
| `[E2E]` | The suite command's pass or fail output. A committed E2E suite is scenario zero |
| `[BROWSER]` | A screenshot per step that is examined. Accessibility snapshots and click-throughs are navigation, not verification |
| `[API]` | A real request's recorded status and the response fields that prove the behavior |
| `[DB]` | The rows returned by the stated query, compared to the expected state |
| `[LOGS]` | The matching log lines |

Credential values never appear in the document, the plan or a report.

## How it works

1. **Confirm the inputs:** goal, constraints and acceptance expectations. Ambiguity is resolved with the user before drafting.
2. **Establish technical context** by following `discovering-technical-context`.
3. **Pick the building blocks** from the reference, and tell the user in one line which were dropped and why.
4. **Analyze the current implementation:** what exists to reuse, what must change and what is new, with file paths.
5. **Break the work into phases and tasks** with files, a scoped Definition of Done and optionally a Stop Rule and Clues.
6. **Mark parallel groups** explicitly, for example `Parallel group A: Tasks 2.1–2.3`.
7. **Persist the Technical Context** into the plan.
8. **Draft the verification document**, proposing candidate checks and asking which to include.
9. **Hand both to the user** to read and iterate until they are satisfied. The plan file is the agreement; there is nothing to sign.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| `plan-building-blocks.md` | Assembling or revising a plan's structure, every time before drafting |
| `plan-example.md` | Unsure how a finished plan reads, or calibrating depth for a mid-size task |
| `verification-doc.md` | Drafting the final verification phase's document, for every non-trivial plan |

## Related skills

- [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context): populates the plan's Technical Context section. Required by step 2.
- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation): executes the finished plan.

## Source

[`plugins/tsh-product-engineering/skills/creating-implementation-plans/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/creating-implementation-plans/SKILL.md)
