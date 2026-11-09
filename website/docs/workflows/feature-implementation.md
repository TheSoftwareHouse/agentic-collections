---
title: Feature implementation
sidebar_label: Feature implementation
sidebar_position: 2
description: How a feature, ticket or plan goes from request to verified change — a committed plan, implementer subagents working from it, a verification pyramid and a final phase where code review and functional verification run in parallel.
sources:
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/
  - plugins/tsh-product-engineering/skills/creating-implementation-plans/
  - plugins/tsh-product-engineering/skills/discovering-technical-context/
  - plugins/tsh-product-engineering/skills/reviewing-code/
  - plugins/tsh-product-engineering/agents/software-engineer.md
  - plugins/tsh-product-engineering/agents/ui-engineer.md
  - plugins/tsh-product-engineering/agents/code-reviewer.md
  - plugins/tsh-product-engineering/agents/feature-verifier.md
sources_hash: "33f5321d615962d3d6d37bd7ac40632019fbd9497bc3a652276db08034e8dfbd"
---

# Feature implementation

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/) · **Start with:** `/tsh-product-engineering:orchestrating-feature-implementation`, or describe the work ("implement this", "do this ticket") and [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) loads on its own.

The main conversation is the orchestrator: it owns the plan, the todo list, the delegation and the gates. Implementation runs in subagents, so their file reads, tool output and MCP traffic stay out of the main context. The plan file is the contract — every delegate works from it, because subagents never see the conversation.

Local repository rules outrank the workflow. If the project defines its own delivery workflow (branching, review, CI gates), this one runs inside it.

## At a glance

<!-- PHASE2(visual): the flow is a plain-text block because @docusaurus/theme-mermaid is not installed — the old site drew its workflows as diagrams — decide in Phase 2 whether to add the Mermaid theme or a diagram component -->

```text
request ─▶ plan + verification document        (creating-implementation-plans, main conversation)
        ─▶ user reads the plan → "Execute the plan"
        ─▶ tasks, in plan order; parallel groups in one message
             software-engineer │ ui-engineer          (one subagent per task)
        ─▶ orchestrator gates each report, ticks the plan, runs each phase's Verification line once
        ─▶ UI verification gate, per Figma-backed UI item  (see UI verification)
        ─▶ final verification phase, in parallel
             code-reviewer      │ feature-verifier
        ─▶ findings → scoped fixes → scoped re-checks
        ─▶ close: report to the user
```

## Who does what

| Step | Runs in | Component |
| :-- | :-- | :-- |
| Write the plan and the verification document | Main conversation | [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans), using [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) for the Technical Context |
| Orchestrate: gate reports, tick the plan, run phase checks, route findings | Main conversation | [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) |
| Backend, logic, tests, configuration tasks | Subagent (`sonnet`) | [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer) |
| UI tasks backed by a design | Subagent (`sonnet`) | [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) |
| UI capture and design judgment, per gate iteration | Subagents | [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) and [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) — see [UI verification](./ui-verification) |
| Code review, in the final verification phase | Subagent (`opus`, read-only) | [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer), applying [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) |
| Functional verification, in the final verification phase | Subagent (`sonnet`, read-only) | [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier) |
| Trivial single-file change with no design decision | Main conversation, inline | — |
| A bug whose cause is not yet known | Main conversation | [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) — see [Debugging](./debugging) |

Authoring E2E suites, infrastructure and CI, and discovery or analysis work are out of scope here: the orchestrator names the gap to the user instead of improvising. The `tsh-product-testing` and `tsh-platform-engineering` plugins may not be installed, and the workflow never blocks on them.

## Step by step

### 1. Plan

A non-trivial change needs a plan file the user has read. With no plan, the orchestrator writes one through [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans); only a single-file change with no design decision may go ahead without one.

The plan is saved at `specifications/<task-id>/<task-name>.plan.md`, where `<task-id>` is the ticket ID or a short kebab-case task name. Its sections are chosen from a set of building blocks to match the task's risk — a config tweak gets a goal and two tasks, a schema migration gets the full treatment. What a plan carries:

- **A Goal**, with a Success Measure and a Do NOT touch / do NOT add list — the one block every plan needs.
- **Technical Context**, whenever any task will be delegated or the plan will outlive the session — which covers every plan whose tasks this workflow delegates. It holds stack and versions, conventions and the verbatim verification commands, found by [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) (plan context, then project instructions, then codebase patterns, then external documentation) and persisted so implementers never rediscover them.
- **Phases and tasks**, always — though a small change may be a single phase, or tasks only. Each task names every file it touches in a `**Files:**` field, labelled `create`, `modify` or `reuse`, and has a Definition of Done with at least one objectively verifiable check, scoped to the task's own files. Tasks and Definition of Done items are `- [ ]` checkboxes.
- **Parallel groups**, when two or more tasks are genuinely independent, marked explicitly — only tasks that do not consume each other's output and whose `**Files:**` lists are disjoint.
- **A final verification phase** for every non-trivial plan: a code-review task and a functional-verification task, run in parallel.

No implementation code goes into the plan — type definitions, signatures and API shapes may pin a contract. There are no approval tables or status fields: the user approves by reading the plan and saying so.

At planning time the skill also drafts the **verification document**, `specifications/<task-id>/<task-name>.verification.md`, and asks the user which functional checks it should include — browser walkthrough, API calls, database state, log checks, data seeding. A project with a committed E2E suite lists running it as scenario zero.

### 2. Get the go-ahead

For a plan created or changed in this session, the orchestrator asks the user to read it, through the AskUserQuestion tool ("Execute the plan" / "Wait — I want changes"), never as a prose question at the end of a turn. The user's word is the gate.

The orchestrator then creates one todo per plan task, final verification tasks included. If any task is UI work, or the verification document names a browser or API scenario, it collects the **pinned inputs** up front: the exact full dev server URL, confirmed by the user — never inferred from config, processes or port scans — and every design URL. A Figma-backed UI task without a design URL gets one from the user, recorded in the plan, before the first delegation.

### 3. Delegate the tasks

The orchestrator walks the plan in order. A parallel group's subagents are launched in a single message; everything else runs one task at a time. Each delegation is self-contained: the plan path, the task IDs, the instruction to read the plan's Technical Context first, the expected report shape, and the pinned inputs.

- [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer) implements the task as written, runs its Definition of Done commands verbatim — never widened to directory- or project-wide suites — and ticks the plan's checkboxes for its own scope only. A fix for a reported failure follows [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code). It never discards pre-existing uncommitted changes and never runs `git bisect`; it reports the last good and first bad commit for the main conversation instead.
- [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) fetches the design through the Figma MCP before writing markup, implements it, and runs the Definition of Done commands. When the delegation says the UI verification gate runs after the task, it leaves all rendered-result checking to the gate.

Both stop and report a missing input instead of guessing it. `software-engineer` also stops and reports, instead of improvising, when a task's Stop Rule fires or an expected seam is not there.

### 4. Gate every report

After each task the orchestrator reads the report, confirms that each Definition of Done command ran and passed, reads the files-changed and deviations sections critically, ticks the task's boxes in the plan and updates the todo. It re-runs nothing at this tier. A failed, blocked or command-less report stops the line until it is resolved, with the user if needed.

When a phase's last task completes, the orchestrator runs that phase's `Verification:` line exactly once: an integration-scoped check of what the phase created, plus one typecheck or build.

A material deviation from the plan stops the flow: the orchestrator updates the plan file, tells the user what changed and why, and lets them re-read it before continuing.

### 5. Close each UI item through the gate

Every Figma-backed UI task goes through the UI verification gate before the final phase: fresh `ui-capture-worker` artifacts judged by `ui-reviewer`, iterated up to five times per item, then an escalation question to the user. The final verification phase starts only when every UI item is PASSED or ESCALATED with the user's acknowledgement. The details are on the [UI verification](./ui-verification) page.

### 6. Run the final verification phase

The orchestrator delegates both tasks at once — in a single message, or as immediately consecutive background delegations:

- [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) gets the plan path, the full list of changed files and the sentence assigning functional and E2E verification to the parallel verifier. It runs static checks, unit and integration suites and the build itself — an implementation report is a claim, not evidence — and applies [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code): plan comparison, coverage per test layer, high-risk anti-patterns, the security baseline, scalability, and any stack skill installed in the session. It returns a verdict, findings ordered blocker / major / minor, the checks it executed, a coverage assessment and what passed.
- [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier) gets the verification document and the pinned inputs, and executes the scenarios against the running application in order: E2E suite runs, browser walkthroughs driven with the Playwright CLI and screenshots it examines, real API calls, database and log checks. It returns pass or fail per scenario with evidence.

A legacy plan without a final verification phase gets a single full-scope `code-reviewer` delegation instead.

### 7. Route the findings, then close

Each actionable finding goes back to the implementer that owns it — `ui-engineer` for UI, `software-engineer` otherwise — as a scoped follow-up task, with only the checks scoped to that fix re-run. There is never a second full review or verification pass. A fix that changes rendered UI on a Figma-backed screen reopens that item's UI gate; a finding that invalidates part of the plan is a material deviation.

The orchestrator closes with a report to the user: what shipped, the UI Verification Summary, verification results, the review outcome, and anything recorded in the plan as a deviation or follow-up.

## The verification pyramid

| Tier | What runs | When |
| :-- | :-- | :-- |
| Task | The task's own Definition of Done commands, scoped to its files | By the implementer, once; trusted from its report |
| Phase | The phase's `Verification:` line — one integration check plus one typecheck or build | By the orchestrator, once, when the phase's last task completes |
| Final | Full code review with tests, linters and build, plus the verification document against the running app | Once, by `code-reviewer` and `feature-verifier` in parallel |

No check runs twice, and nothing re-reviews or re-verifies after the final phase has passed. A clean build is never a substitute for UI verification against the design.

## Where people decide

| Point | What the user decides |
| :-- | :-- |
| Planning | Answers ambiguous requirements before drafting; chooses which functional checks go into the verification document |
| Go-ahead | Reads the plan and chooses "Execute the plan" or "Wait — I want changes" |
| Pinned inputs | Confirms the exact dev server URL; supplies missing design URLs |
| Material deviation | Re-reads the updated plan before the flow continues |
| Blocked task or phase check | Helps resolve it, when the orchestrator cannot alone |
| UI escalation | After five FAIL iterations of one item: continue with a chosen number of iterations, accept as ESCALATED, or give a custom instruction |

## What it leaves behind

| Artifact | Path |
| :-- | :-- |
| Plan, with ticked checkboxes | `specifications/<task-id>/<task-name>.plan.md` |
| Verification document | `specifications/<task-id>/<task-name>.verification.md` |
| UI verification evidence and reports | `specifications/<task-id>/ui-verification/` |
| Screenshots from browser scenarios | `specifications/<task-id>/verification-evidence/` |

The plan is meant to be committed: a plan kept outside the repository cannot be reviewed in a pull request or read by an implementer subagent.
