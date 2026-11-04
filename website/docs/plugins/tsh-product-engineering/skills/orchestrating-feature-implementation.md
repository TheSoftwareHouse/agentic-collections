---
title: Orchestrating Feature Implementation
sidebar_label: orchestrating-feature-implementation
sidebar_position: 5
description: Implements a feature, ticket or plan end to end from the main conversation by delegating each plan task to implementer subagents and closing with parallel code review and functional verification.
sources:
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/
sources_hash: "d15dec6f879c7a2153a83cd0ec484b6ac3d2defc051f3354126a4ee7952c65b9"
---

# Orchestrating Feature Implementation

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:orchestrating-feature-implementation`  
**Used by:** no agent preloads it. It is the entry point that delegates to [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer), [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer), [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker), [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer), [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) and [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier). Referenced by [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) (executes the finished plan) and [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) (owns the verify-fix loop that repeats a review pass); [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) and [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) name it as the owner of implementation work.

In this workflow the main conversation is the orchestrator. It owns the plan, the todo list, the delegation and the gates. Implementation work runs in subagents, so their file reads, tool output and MCP traffic stay out of the main context. The plan file is the contract: every delegate works from it, because subagents never see the conversation.

Verification follows a pyramid. Each task runs only its own scoped checks and is trusted from its report, each phase closes with one integration checkpoint, and the plan's final verification phase is the single full, evidence-based pass. No check runs twice.

Use it for any feature request or multi-file change, before the first file is edited, and to execute or resume a `*.plan.md`. Local repository rules outrank the skill: if the project defines its own delivery workflow, this one runs inside it.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Plan first** | A plan file the user has read must exist before non-trivial implementation. No plan means the skill creates one via `creating-implementation-plans`. Only a single-file change with no design decision may proceed without one |
| **Self-contained delegation** | Every delegation carries the exact plan path, the task IDs, the instruction to read the plan's Technical Context first, and any pinned inputs such as the dev server URL and design URLs |
| **Parallel groups** | Tasks run in parallel only when the plan marks them as one group and their `**Files:**` lists are disjoint. The group's subagents launch in a single message |
| **Report gating** | Each task report must name every Definition of Done command with a passing result. A failed, blocked or command-less report stops the flow. Nothing is re-run at the task tier |
| **Phase checkpoints** | Each phase's `Verification:` line runs exactly once, when its last task completes: an integration-scoped check plus one typecheck or build |
| **Deviations** | A material deviation from the plan stops the flow: update the plan file, tell the user what changed and why, and let them re-read before continuing |
| **UI verification gate** | Every Figma-backed UI task closes through a verify-fix loop of up to 5 iterations per item, using fresh capture and an independent verdict |
| **Final verification phase** | `code-reviewer` and `feature-verifier` run concurrently, exactly once. Findings route back as scoped fixes, never as a second full pass |

## Task routing

| Work | Routed to |
| :-- | :-- |
| UI task backed by a design (Figma URL or design reference in the plan) | `ui-engineer` subagent |
| UI verification capture, per gate iteration | `ui-capture-worker` subagent |
| UI verification verdict, per gate iteration | `ui-reviewer` subagent |
| Any other implementation task: backend, logic, tests, config | `software-engineer` subagent |
| Trivial single-file change with no design decision | Inline, in the main conversation |
| A bug whose cause is not yet established | `debugging-code`, in the main conversation |
| Code review in the final verification phase | `code-reviewer` subagent |
| Functional verification in the final verification phase | `feature-verifier` subagent |
| E2E test authoring, infrastructure and CI, discovery or analysis work | Out of scope here; the skill names the gap to the user instead of improvising |

## How it works

1. **Establish the state.** Locate the plan (default `specifications/<task-id>/<task-name>.plan.md`) and check that it is actionable: tasks name files and Definitions of Done, no material open questions, and for a non-trivial plan a final verification phase whose verification document exists. Missing or stale means following `creating-implementation-plans`.
2. **Confirm the go-ahead.** For a plan created or changed in this session, the user is asked to read it through the AskUserQuestion tool, not as a prose question at the end of a turn.
3. **Create todos.** One per plan task, including the final verification phase's tasks, with parallel groups noted.
4. **Collect pinned inputs up front.** For UI work or browser and API verification scenarios: the exact full dev server URL, confirmed by the user and never inferred, and every design URL.
5. **Execute.** Walk the plan in order; launch parallel groups in one message.
6. **Record and gate.** Read each report, confirm the Definition of Done commands ran, tick the plan's boxes, update the todo, and run the phase's `Verification:` line when its last task completes.
7. **Run the UI verification gate** after each Figma-backed UI task, following the gate reference.
8. **Execute the final verification phase.** Launch `code-reviewer` and `feature-verifier` concurrently. The reviewer's delegation states verbatim that functional and E2E verification runs in the parallel verifier. A legacy plan without this phase gets a single full-scope `code-reviewer` instead.
9. **Route the findings.** Each actionable finding goes back to the implementer that owns it as a scoped follow-up, with only scoped re-checks. A fix that changes rendered UI on a Figma-backed screen reopens that item's gate.
10. **Close.** Report what shipped, the UI Verification Summary, verification results, the review outcome, and anything recorded in the plan as deviation or follow-up.

## The UI verification gate

The reference `ui-verification-gate.md` is loaded before the first UI delegation and again before closing any UI item. It defines:

- **Inputs pinned before iteration 1:** Playwright CLI availability, the exact full dev server URL, the Figma URL or node, the locale, language and text direction the design represents, authentication prepared before the first capture, and the shared verification root `specifications/<task-id>/ui-verification/`. URL, locale, auth and visible design-versus-ticket conflicts go to the user in one question round.
- **The loop:** per item, never batched. Fix all differences from the latest report, run one pass as `reviewing-ui` defines it (fresh capture, then a fresh judgment), and stop on PASS. A FAIL continues the loop. `VERIFICATION NOT RUN` is a blocker that consumes no iteration budget.
- **Reuse rules:** the named browser session survives the loop, and resuming the previous capture worker (SendMessage) is preferred for the next iteration, while the reviewer is always fresh.
- **Hard rules:** the orchestrator saves every reviewer report to `iteration-<N>/report.md` itself, rejects a report that breaks the contract, and treats a FAIL with nothing to fix as `VERIFICATION NOT RUN`. A type check, build, unit test or code review never closes a UI item.
- **Escalation after 5 FAIL iterations:** a structured summary and a user choice between continuing with an extra iteration count, accepting the item as `ESCALATED`, or a custom instruction.
- **Closing:** every item ends PASSED or user-acknowledged ESCALATED before the final verification phase, and a UI Verification Summary is reported separately from code review.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| `ui-verification-gate.md` | The plan contains a Figma-backed UI task, before the first UI delegation, and again before closing any UI item |

## Related skills

- [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans): authors the plan and the verification document this workflow executes.
- [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code): the standard the final review gate applies.
- [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui): the single verification pass the UI gate repeats.
- [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui) and [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence): the judging standard and capture contract behind the gate.
- [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context): what the implementer agents consult before writing code.
- [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code): the route for a bug whose cause is not yet established.

`tsh-product-testing` (E2E suites) and `tsh-platform-engineering` (CI, deployment) may not be installed. The skill names the gap to the user and never blocks on one.

For the end-to-end picture see the [feature implementation workflow](/docs/workflows/feature-implementation).

## Source

[`plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md)
