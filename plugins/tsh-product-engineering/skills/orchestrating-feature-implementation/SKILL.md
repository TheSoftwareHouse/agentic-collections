---
name: orchestrating-feature-implementation
description: "Implements a feature, ticket, or plan end to end from the main conversation: confirms a plan file exists, delegates each task to implementer subagents — in parallel where the plan allows — gates on their reports, then closes with the plan's final verification phase: code review and functional verification in parallel. Use for any feature request or multi-file change, before the first file is edited."
when_to_use: "Trigger on: 'implement this', 'build this feature', 'do this ticket', executing or resuming a *.plan.md, work spanning more than one file or task, delegating implementation to subagents or running tasks in parallel, or a change that looks obvious enough to just start editing. Writing the plan is creating-implementation-plans; judging finished work is reviewing-code; fixing a bug whose cause is not yet known is debugging-code."
---

# Orchestrating Feature Implementation

In this workflow the main conversation is the orchestrator: it owns the plan, the
todo list, the delegation, and the gates. Implementation work runs in subagents so
their file reads, tool output, and MCP traffic stay out of this context. The plan
file is the contract — every delegate works from it, because subagents never see this
conversation.

Verification follows a pyramid: each task runs only its own scoped checks and is
trusted from its report, each phase closes with one integration checkpoint, and the
plan's final verification phase is the single full, evidence-based pass. No check
runs twice.

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
| MUST | Have a plan file the user has read before non-trivial implementation starts. No plan → create one first via `creating-implementation-plans`, which ships in this plugin and is always available. Only a genuinely trivial change (single file, no design decision) may proceed planless. |
| MUST | Make every delegation self-contained: exact plan path, task ID(s), the instruction to read the plan's Technical Context first, and any pinned inputs (dev server URL, design URLs). Subagents have no conversation history. |
| MUST | Run tasks in parallel only when the plan marks them as one parallel group and their `**Files:**` lists are disjoint. Launch the group's subagents in a single message; run everything else in plan order. |
| MUST | Gate on every task report: confirm it names each Definition of Done command with a passing result, and read the files-changed and deviations sections critically — they are gate inputs, not decoration. Re-run nothing at this tier; the final verification phase re-establishes evidence. A failed, blocked, or command-less report stops the flow. |
| MUST | Run each phase's `Verification:` line exactly once, when its last task completes — an integration-scoped check of what the phase's tasks created plus one typecheck or build. Never a re-run of task Definitions of Done, never a full suite. |
| MUST | Mirror plan tasks in the todo list and update both after each completed task. |
| MUST | Stop on any material deviation from the plan: update the plan file, tell the user what changed and why, and let them re-read before continuing. |
| MUST | Close every Figma-backed UI task through the UI verification gate — fresh `ui-capture-worker` artifacts judged by `ui-reviewer`, iterated up to 5 times per item. Read [`./references/ui-verification-gate.md`](./references/ui-verification-gate.md) before the first UI delegation. The final verification phase starts only when every UI item is individually PASSED or user-acknowledged ESCALATED. |
| MUST | Close by executing the plan's final verification phase exactly once: delegate `code-reviewer` and `feature-verifier` concurrently — in a single message, or as immediately consecutive background delegations — stating verbatim in the reviewer's delegation that functional and E2E verification runs in the parallel verifier. A legacy plan without that phase gets a single full-scope `code-reviewer` delegation instead. |
| NEVER | Re-run full suites between tasks, or add any review or verification pass after the final verification phase has passed. Findings route back as scoped fixes with scoped re-checks — never a second full pass. |
| NEVER | Treat task-tier trust as the final word — it holds only because the final phase re-runs everything once — or a clean build as a substitute for UI verification against the design. |

## Task Routing

| Work | Route to |
| --- | --- |
| UI task backed by a design (Figma URL or design reference in the plan) | `ui-engineer` subagent |
| UI verification capture — ACTUAL evidence from the running app, per gate iteration | `ui-capture-worker` subagent |
| UI verification verdict — Figma comparison on captured artifacts, per gate iteration | `ui-reviewer` subagent |
| Any other implementation task — backend, logic, tests, config | `software-engineer` subagent |
| Trivial single-file change with no design decision | Inline, in this conversation |
| A bug whose cause is not yet established | `debugging-code`, in this conversation — a fix that outgrows a minimal change comes back here as a plan carrying the established root cause |
| Code review, in the final verification phase | `code-reviewer` subagent |
| Functional verification of the delivered feature, in the final verification phase | `feature-verifier` subagent |
| Authoring E2E test suites, infrastructure/CI, discovery or analysis work | Out of scope here — name the gap to the user instead of improvising |

## Procedure

1. **Establish the state.** Locate the plan (default
   `specifications/<task-id>/<task-name>.plan.md`). Check it is actionable: tasks
   name files and Definitions of Done, no material open questions, and — for a
   non-trivial plan — a final verification phase whose verification document
   (`specifications/<task-id>/<task-name>.verification.md`) exists. Missing or
   stale → follow
   [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md)
   and iterate with the user until they are happy with it.
2. **Confirm the go-ahead.** For a plan created or changed in this session, ask the
   user to read it before execution. Their word is the gate — there are no approval
   fields to fill. Ask through the AskUserQuestion tool (options like "Execute the
   plan" / "Wait — I want changes"), never as a prose question at the end of a turn:
   plain text blocks nothing and is easy to scroll past, so the flow silently stalls
   while both sides think they are waiting for the other.
3. **Create todos.** One per plan task, including the final verification phase's
   tasks, in plan order, parallel groups noted.
4. **Collect pinned inputs up front.** If any task is UI work, or the verification
   document names a browser or API scenario: the exact full dev server URL,
   user-confirmed — never inferred from config, processes, or port scans — and every
   design URL, before the first delegation. A Figma-backed UI task without a design
   URL: get it from the user and record it in the plan first. Forward these
   unchanged to every delegate that needs them, the verifier included.
5. **Execute.** Walk the plan in order. For a parallel group, launch all its
   subagents in one message; otherwise one task at a time. Each delegation states the
   plan path, the task ID, the expected result shape (files changed, verification
   output, deviations), and the pinned inputs.
6. **Record and gate.** After each task: read the report, confirm the Definition of
   Done commands ran and passed as reported, check the task's boxes in the plan,
   update the todo — and re-run nothing. When a phase's last task completes, run the
   phase's `Verification:` line once. A failed report or phase check stops the line —
   resolve it (with the user if needed) before the next delegation.
7. **Run the UI verification gate.** After each Figma-backed UI task's report, run
   the per-item verify-fix loop from
   [`./references/ui-verification-gate.md`](./references/ui-verification-gate.md):
   fresh `ui-capture-worker` capture, `ui-reviewer` verdict, fixes back to
   `ui-engineer`, up to 5 iterations, then the structured escalation gate. Every
   item ends PASSED or user-acknowledged ESCALATED before the next step, and the UI
   Verification Summary is reported separately from code review.
8. **Execute the final verification phase.** When all implementation tasks are done
   and the UI gate is closed, launch both delegates concurrently (one message, or
   immediately consecutive background delegations): `code-reviewer` with the plan path, the full
   list of changed files, and the sentence assigning functional and E2E verification
   to the parallel verifier; `feature-verifier` with the verification document path
   and the pinned inputs. For a legacy plan without this phase, delegate a single
   full-scope `code-reviewer` instead.
9. **Route the findings.** Send each actionable finding back to the implementer that
   owns it (`ui-engineer` for UI, `software-engineer` otherwise) as a scoped
   follow-up task; re-run only the checks scoped to each fix — never a second full
   review or verification pass. A fix that changes rendered UI on a Figma-backed
   screen reopens that item's UI verification gate. A finding that invalidates part
   of the plan is a material deviation — rule above applies.
10. **Close.** Report to the user: what shipped, the UI Verification Summary,
    verification results, review outcome, and anything recorded in the plan as
    deviation or follow-up.

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [UI verification gate](./references/ui-verification-gate.md) | The plan contains a Figma-backed UI task, before the first UI delegation — and again before closing any UI item | The per-item verify-fix loop, iteration budget, blocker handling, the structured escalation gate, the UI Verification Summary |

## Related Skills

All of these ship in this plugin — if this skill loaded, they are installed. The plan
rule above depends on the first: it is a prerequisite, not a bonus. So do the
`feature-verifier`, `ui-capture-worker`, and `ui-reviewer` agents. Every
browser-driving delegate in this plugin runs on the Playwright CLI, and the UI
verification gate judges through the Figma MCP, exclusively.

- [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md) —
  authors the plan and the verification document this workflow executes.
- [`reviewing-code`](../reviewing-code/SKILL.md) — the standard the final review
  gate applies; the `code-reviewer` agent loads it automatically.
- [`reviewing-ui`](../reviewing-ui/SKILL.md) — the single verification pass the UI
  gate repeats; also user-invocable standalone.
- [`verifying-ui`](../verifying-ui/SKILL.md) and
  [`capturing-ui-evidence`](../capturing-ui-evidence/SKILL.md) — the judging standard
  and capture contract behind the gate; the `ui-reviewer` and `ui-capture-worker`
  agents load them automatically.
- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) — what
  the implementer agents consult before writing code.

Other plugins are a different matter: `tsh-product-testing` (E2E suites) and
`tsh-platform-engineering` (CI, deployment) may not be installed. Name the gap to the
user, never path into them, and never block on one.
