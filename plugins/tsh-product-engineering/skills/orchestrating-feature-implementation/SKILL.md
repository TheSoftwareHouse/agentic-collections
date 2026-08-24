---
name: orchestrating-feature-implementation
description: "Implements a feature, ticket, or plan end to end from the main conversation: confirms a plan file exists, delegates each task to implementer subagents — in parallel where the plan allows — gates on their reports, then closes with the plan's final verification phase: code review and functional verification in parallel. Use for any feature request or multi-file change, before the first file is edited."
when_to_use: "Trigger on: 'implement this', 'build this feature', 'do this ticket', executing or resuming a *.plan.md, work spanning more than one file or task, delegating implementation to subagents or running tasks in parallel, or a change that looks obvious enough to just start editing. Writing the plan is creating-implementation-plans; judging finished work is reviewing-code."
---

# Orchestrating Feature Implementation

In this workflow the main conversation is the orchestrator: it owns the plan, the
todo list, the delegation, and the gates. Implementation work runs in subagents so
their file reads, tool output, and MCP traffic stay out of this context. The plan
file is the contract — every delegate works from it, because subagents never see this
conversation.

Verification follows a pyramid, and a check belongs to exactly one tier of it by its
scope: a task runs the file-scoped tests over what it wrote and is trusted from its
report; a phase closes with one integration checkpoint plus the package-wide
typecheck or build, executed by `gate-runner`; the plan's final verification phase is
the single full, evidence-based pass. No check runs twice, and running a formatter is
not a check.

## When to Use

- A feature, fix, or task is ready to be implemented.
- A `*.plan.md` exists (possibly from a previous session) and should be executed.
- Implementation spans several tasks that benefit from parallel delegation.

## Applicability and Precedence

Local repository rules outrank this skill. If the project defines its own delivery
workflow (branching, review, CI gates), run this workflow inside it, not instead
of it. Invoking this skill is itself the user's request to launch the subagents it
names: the delegations below are the deliverable, not an optional optimization.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Have a plan file the user has read before non-trivial implementation starts. No plan → create one first via `creating-implementation-plans`, which ships in this plugin and is always available. Only a genuinely trivial change (single file, no design decision) may proceed planless. |
| MUST | Route repository discovery through `context-scout` — before planning, before a delegation, after a surprising report. Ask locate/enumerate/excerpt questions, several scouts in parallel, and read only their bounded reports. A source file dumped into this conversation through a shell command is an inline read all the same; direct reads here are the workflow's own artifacts — the plan, the verification document, git state, task reports. |
| MUST | Make every delegation self-contained: exact plan path, task ID(s), the exact section headings of the plan sections the delegate needs — Goal, Technical Context, its own tasks, any section a task references — and any pinned inputs (dev server URL, design URLs, the working branch). Delegates locate sections by heading, never by line number — the plan mutates during execution (amendments, ticked boxes), so line ranges rot between delegations. Subagents have no conversation history, and they read the named sections, never the whole plan. |
| MUST | Launch everything the plan lets run: a parallel group's subagents go in a single message, and a phase the plan marks `Independent of Phase N` runs concurrently with it — each phase gating on its own checkpoint. Tasks share a launch only inside a marked group with disjoint `**Files:**` lists; everything else follows its named dependency edges, never an assumed order. |
| MUST | Batch consecutive dependency-chained tasks in the same package into one delegation when the batch is light: two or three tasks, combined `**Files:**` lists around ten files or fewer, no integration-stack, E2E, or browser run among them, and never across a phase boundary — the checkpoint runs between. Anything heavier is one task per delegate: a delegate pushed into context compaction mid-batch loses the plan it is executing, which costs more than the handoffs saved. |
| MUST | Gate on every task report: confirm it names each Definition of Done command with a passing result, and read the files-changed and deviations sections critically — they are gate inputs, not decoration. Re-run nothing at this tier; the final verification phase re-establishes evidence. A failed, blocked, or command-less report stops the flow. |
| MUST | Execute each phase's `Verification:` line exactly once on success, when its last task completes, by delegating it to `gate-runner` with the commands verbatim — an integration-scoped check of what the phase's tasks created plus one typecheck or build — and gating on its verbatim report; raw gate output never enters this context. A failed checkpoint runs again only after its scoped fix lands. Never a re-run of task Definitions of Done, never a full suite. |
| NEVER | Run a check outside its tier: no package- or project-wide typecheck, lint or build at task tier, no full suite at phase tier, and never a re-run of anything because a formatter touched files. |
| MUST | Mirror plan tasks in the todo list and update it after each completed task. Implementers tick their own task and Definition of Done boxes; when gating a report, confirm the ticks match it and tick anything the delegate missed — a box left unchecked after its work passed lies to the next session. |
| MUST | Stop on any material deviation from the plan: update the plan file, tell the user what changed and why, and let them re-read before continuing. A deviation that changes a pinned contract updates the plan's pinned-contract block in the same edit — amended task prose beside a stale contract block misleads every later delegate. |
| MUST | Close by executing the plan's final verification phase exactly once: launch `gate-runner` (the gate commands verbatim from Technical Context, E2E excluded) and `feature-verifier` in a single message; when the runner returns, delegate `code-reviewer` with its report embedded, stating verbatim that functional and E2E verification runs in the parallel verifier. A legacy plan without that phase gets a single full-scope `code-reviewer` delegation instead. |
| NEVER | Re-run full suites between tasks, or add any review or verification pass after the final verification phase has passed. Findings route back as scoped fixes with scoped re-checks — never a second full pass. |
| NEVER | Re-run any check to recover lost or truncated output, or for extra confidence. Capture a long check's full output to a file on its first run and read the result from the capture; the only thing that justifies running a check again is a fix landed since it last ran. |
| NEVER | Treat task-tier trust as the final word — it holds only because the final phase re-runs everything once — or a clean build as a substitute for UI verification against the design. |

## Task Routing

| Work | Route to |
| --- | --- |
| UI task backed by a design (Figma URL or design reference in the plan) | `ui-engineer` subagent |
| Any other implementation task — backend, logic, tests, config | `software-engineer` subagent |
| Trivial single-file change with no design decision | Inline, in this conversation |
| Executing a phase checkpoint's `Verification:` line, or the final verification phase's gates | `gate-runner` subagent |
| Code review, in the final verification phase | `code-reviewer` subagent |
| Functional verification of the delivered feature, in the final verification phase | `feature-verifier` subagent |
| Repository discovery — conventions, call sites, inventories — ahead of planning or a delegation | `context-scout` subagent |
| Authoring E2E test suites, infrastructure/CI | Out of scope here — name the gap to the user instead of improvising |

## Procedure

1. **Establish the state.** Snapshot `git status` first: pre-existing
   working-tree modifications are named to the user as outside this work's scope
   now — not discovered by the final review — and are never staged with the
   feature. Then locate the plan (default
   `specifications/<task-id>/<task-name>.plan.md`). Check it is actionable: tasks
   name files and Definitions of Done, no material open questions, phases that state
   their parallelism — groups, phase independence where it holds, or the dependency
   justifying each sequential edge; a
   multi-behavior plan arriving as an unjustified chain is not actionable — and, for
   a non-trivial plan, a final verification phase whose verification document
   (`specifications/<task-id>/<task-name>.verification.md`) exists. Missing, stale,
   or an unjustified chain → follow
   [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md)
   and iterate with the user until they are happy with it. Enter that skill before
   exploring: discovery that feeds the plan belongs to `context-scout` from the
   first question, not to warm-up reads of the repository in this conversation.
2. **Confirm the go-ahead.** For a plan created or changed in this session, ask the
   user to read it before execution. Their word is the gate — there are no approval
   fields to fill.
3. **Create todos.** One per plan task, including the final verification phase's
   tasks, in plan order, parallel groups noted.
4. **Collect pinned inputs up front.** Always: the working branch — on the default
   branch, ask once whether to create one before the first file is edited; a
   mid-execution branching note gets lost where a pinned input does not. If any task
   is UI work, or the verification document names a browser or API scenario: the dev
   server URL and every design URL, before the first delegation. Ask the user for
   whatever is missing; forward these unchanged to every delegate that needs them,
   the verifier included.
5. **Execute.** Treat the plan as a dependency graph, not a queue: at every gate,
   launch everything whose dependencies have passed — the current phase's next
   group, and the opening group of any phase marked independent of the ones still
   running — in one message. Within a chain, batch consecutive tasks into one
   delegation when the batching rule allows it; otherwise one task at a time. Each
   delegation states the plan path, the task ID(s) in execution order, the section
   headings to read — Goal, Technical Context, the tasks themselves, any section a
   task references — the expected result shape (files changed and verification
   output per task, deviations), and the pinned inputs.
6. **Record and gate.** After each task: read the report, confirm the Definition of
   Done commands ran and passed as reported, confirm the delegate ticked its boxes
   (tick any it missed), update the todo — and re-run nothing. When a phase's last
   task completes, delegate the phase's `Verification:` line to `gate-runner` —
   commands verbatim — and gate on its report, once. A failed report or
   phase check stops its own line: an independent phase already running continues,
   but nothing new launches downstream of the failure until it is resolved (with
   the user if needed). A batched
   report gates per task: when a batch fails at task N, the earlier tasks stand and
   the remainder goes to a **fresh** delegate — never ask the agent that just failed
   or filled its context to push on.

   Two plan defects surface here, both sizing errors. A task Definition of Done
   carrying a package-wide typecheck, lint or build is mis-tiered: accept the report
   without it and let the phase checkpoint cover it. A report saying an item is
   blocked until a later task lands means those tasks are one task: merge them in the
   plan before continuing, and tell the user.
7. **Execute the final verification phase.** When all implementation tasks are done,
   launch `gate-runner` and `feature-verifier` in one message: the runner with the
   gate commands verbatim from Technical Context — static gates, unit and
   integration suites, the build, E2E excluded — the verifier with the verification
   document path and the pinned inputs. When Technical Context shows a build
   artifact both sides touch — a package `dist/` the build recreates and the E2E
   prelude rebuilds — name it in both delegations and authorize exactly one re-run
   of a command that fails with a missing-or-partial-artifact signature, both
   outcomes reported. When the runner returns, delegate
   `code-reviewer` with the plan path, the full list of changed files, the runner's
   report embedded as executed evidence, and the sentence assigning functional and
   E2E verification to the parallel verifier. The suites and the functional
   scenarios overlap in time; the reviewer's reading starts once the gate results
   are known. For a legacy plan without this phase, delegate a single full-scope
   `code-reviewer` instead.
8. **Route the findings.** Send each actionable finding back to the implementer that
   owns it (`ui-engineer` for UI, `software-engineer` otherwise) as a scoped
   follow-up task; re-run only the checks scoped to each fix — never a second full
   review or verification pass. A finding that invalidates part of the plan is a
   material deviation — rule above applies.
9. **Close.** Report to the user: what shipped, verification results, review outcome,
   and anything recorded in the plan as deviation or follow-up.

## Related Skills

All three ship in this plugin — if this skill loaded, they are installed. The plan
rule above depends on the first: it is a prerequisite, not a bonus. So does the
`feature-verifier` agent, together with the Playwright MCP server the plugin bundles
for it.

- [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md) —
  authors the plan and the verification document this workflow executes.
- [`reviewing-code`](../reviewing-code/SKILL.md) — the standard the final review
  gate applies; the `code-reviewer` agent loads it automatically.
- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) — what
  the implementer agents consult before writing code.

Other plugins are a different matter: `tsh-product-testing` (E2E suites) and
`tsh-platform-engineering` (CI, deployment) may not be installed. Name the gap to the
user, never path into them, and never block on one.
