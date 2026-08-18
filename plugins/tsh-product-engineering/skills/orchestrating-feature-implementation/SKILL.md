---
name: orchestrating-feature-implementation
description: "Drives feature implementation end to end from the main conversation: ensures an implementation plan exists, delegates its tasks to implementer subagents — in parallel where the plan allows — verifies every task, and closes with a delegated code review. Use when implementing a feature or executing an implementation plan."
when_to_use: "Trigger on: 'implement this feature', executing or resuming a *.plan.md, coordinating implementation across multiple tasks or subagents, or continuing implementation work started in an earlier session."
---

# Orchestrating Feature Implementation

In this workflow the main conversation is the orchestrator: it owns the plan, the
todo list, the delegation, and the gates. Implementation work runs in subagents so
their file reads, tool output, and MCP traffic stay out of this context. The plan
file is the contract — every delegate works from it, because subagents never see this
conversation.

## When to Use

- A feature, fix, or task is ready to be implemented.
- A `*.plan.md` exists (possibly from a previous session) and should be executed.
- Implementation spans several tasks that benefit from parallel delegation.

## Applicability and Precedence

Local repository rules outrank this skill. If the project defines its own delivery
workflow (branching, review, CI gates), run this workflow inside it, not instead
of it.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Have a plan file the user has read before non-trivial implementation starts. No plan → create one first via `creating-implementation-plans`. Only a genuinely trivial change (single file, no design decision) may proceed planless. |
| MUST | Make every delegation self-contained: exact plan path, task ID(s), the instruction to read the plan's Technical Context first, and any pinned inputs (dev server URL, design URLs). Subagents have no conversation history. |
| MUST | Run tasks in parallel only when the plan marks them as one parallel group and their `**Files:**` lists are disjoint. Launch the group's subagents in a single message; run everything else in plan order. |
| MUST | Verify after every task: confirm the delegate ran the task's Definition of Done commands, and spot-check the result. A failed verification stops the flow — fix before proceeding. |
| MUST | Mirror plan tasks in the todo list and update both after each completed task. |
| MUST | Stop on any material deviation from the plan: update the plan file, tell the user what changed and why, and let them re-read before continuing. |
| MUST | Close with a `code-reviewer` delegation whenever the delivered change set contains product code, tests, or configuration — and route its findings back to the owning implementer. |
| NEVER | Treat "it compiles" or "tests pass" as a substitute for the final review, or a clean build as a substitute for UI verification against the design. |

## Task Routing

| Work | Route to |
| --- | --- |
| UI task backed by a design (Figma URL or design reference in the plan) | `ui-engineer` subagent |
| Any other implementation task — backend, logic, tests, config | `software-engineer` subagent |
| Trivial single-file change with no design decision | Inline, in this conversation |
| Final review of the delivered change set | `code-reviewer` subagent |
| E2E test suites, infrastructure/CI, discovery or analysis work | Out of scope here — name the gap to the user instead of improvising |

## Procedure

1. **Establish the state.** Locate the plan (default
   `specifications/<task-id>/<task-name>.plan.md`). Check it is actionable: tasks
   name files and Definitions of Done, no material open questions. Missing or stale →
   follow [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md)
   and iterate with the user until they are happy with it.
2. **Confirm the go-ahead.** For a plan created or changed in this session, ask the
   user to read it before execution. Their word is the gate — there are no approval
   fields to fill.
3. **Create todos.** One per plan task plus one for the final review, in plan order,
   parallel groups noted.
4. **Collect pinned inputs up front.** If any task is UI work: the dev server URL and
   every design URL, before the first delegation. Ask the user for whatever is
   missing; forward these unchanged to every delegate that needs them.
5. **Execute.** Walk the plan in order. For a parallel group, launch all its
   subagents in one message; otherwise one task at a time. Each delegation states the
   plan path, the task ID, the expected result shape (files changed, verification
   output, deviations), and the pinned inputs.
6. **Verify and record.** After each task: confirm the Definition of Done commands
   ran and passed, check the task's boxes in the plan, update the todo. A blocked or
   failed task stops the line — resolve it (with the user if needed) before the next
   delegation.
7. **Review.** When all tasks are done and any change set contains product code,
   tests, or config, delegate to `code-reviewer` with the plan path and the full list
   of changed files.
8. **Route the findings.** Send each actionable finding back to the implementer that
   owns it (`ui-engineer` for UI, `software-engineer` otherwise) as a scoped
   follow-up task; re-run the affected checks. A finding that invalidates part of the
   plan is a material deviation — rule above applies.
9. **Close.** Report to the user: what shipped, verification results, review outcome,
   and anything recorded in the plan as deviation or follow-up.

## Related Skills

Optional and may not be installed — treat each as a bonus, never a prerequisite.

- [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md) —
  authors the plan this workflow executes.
- [`reviewing-code`](../reviewing-code/SKILL.md) — the standard the final review
  gate applies.
