# Plan building blocks

Use this reference when assembling or revising a plan's structure. Each block below
explains why it exists and when it earns its place. Pick deliberately: a section that
adds no decision-relevant information for *this* task is noise the reader pays for on
every read. When in doubt: include for a risky task, drop for a trivial one.

## Table of Contents

[Task Details](#task-details) · [Goal](#goal) · [Proposed Solution](#proposed-solution) ·
[Current Implementation Analysis](#current-implementation-analysis) ·
[Open Questions](#open-questions) · [Technical Context](#technical-context) ·
[Phases and Tasks](#phases-and-tasks) · [Definition of Done rules](#definition-of-done-rules) ·
[Parallel groups](#parallel-groups) · [Final Verification Phase](#final-verification-phase) ·
[Security Considerations](#security-considerations) · [Acceptance Criteria](#acceptance-criteria) ·
[Improvements (Out of Scope)](#improvements-out-of-scope) · [Changelog](#changelog)

## Task Details

**Why:** Links the plan to its source of truth — the ticket, the research notes, the
conversation that produced it — so anyone opening the file cold can trace them.

**Include when:** A ticket ID, research document, or external reference exists.
**Drop when:** The plan's Goal section already carries all the context there is.

## Goal

**Why:** One sentence stating the single most important outcome forces the plan to
have a point. A **Success Measure** makes "done" checkable, and a **Do NOT touch /
do NOT add** list is the cheapest scope-creep defense that exists — implementers and
reviewers both read it.

**Include when:** Always. This is the one block every plan needs.

Format: a `**Goal**:` line, a `**Success Measure**:` line, and a
`**Do NOT touch / do NOT add**:` list.

## Proposed Solution

**Why:** Explains the approach and the reasoning behind it so a reviewer can disagree
with the *design* before anyone writes code. Diagrams welcome. This is also where the
no-implementation-code rule bites: contracts (signatures, DTOs, API shapes) yes,
bodies no — the plan pins *what*, the implementer owns *how*.

**Include when:** There was a genuine design decision — more than one way to do it.
**Drop when:** The change is mechanical and the tasks speak for themselves.

## Current Implementation Analysis

**Why:** The reuse-first rule needs evidence. Listing what is **already implemented**
(reuse, with paths), what is **to be modified**, and what is **to be created** stops
the most expensive planning failure: building a parallel version of something that
already exists.

**Include when:** The change touches an existing codebase in any non-trivial way.
**Drop when:** Greenfield, or a change confined to one file you have already read.

## Open Questions

**Why:** An unresolved question inside a task becomes an implementer's improvised
decision. Parking questions in a table with an Answer column makes them visible and
resolvable before execution starts.

**Include when:** Anything material is still unknown at drafting time.
**Rule:** Do not hand a plan to implementation while a material question is open —
resolve it with the user first.

## Technical Context

**Why:** Implementer subagents start with no conversation history. This section is
the discovered context, persisted once so every delegate reads it instead of
re-scanning the repository — the single biggest token and latency saving in the whole
workflow.

**Include when:** Any task will be delegated, or the plan will outlive the session.

Typical content, kept to what the tasks actually need:

- **Tech stack** — language, framework, key libraries *with versions*; package
  manager, build tool, test runner.
- **Conventions** — the project-instruction rules and codebase patterns that govern
  the touched area (naming, layering, error handling, validation).
- **Testing patterns** — test framework, file naming, mocking strategy, and the
  verbatim commands for unit, integration, e2e, lint, and build.
- **Database patterns** — ORM, migration tool, entity conventions, when relevant.

## Phases and Tasks

**Why:** Phases give verification checkpoints; tasks give delegable units. A task
that names its files and its done-condition can be handed to a subagent as-is.

**Include when:** Always — though a small change may be a single phase, or tasks only.

Each **phase** carries a Goal (how it advances the plan's Goal), a short Description,
a parallelism statement — its groups, or the dependency forcing each sequential edge,
plus `Independent of Phase N` when the phase shares no files and no contracts with a
predecessor; see [Parallel groups](#parallel-groups) — and a `**Verification:**` line — the phase
tier of [Verification tiers](./task-sizing-and-tiers.md#verification-tiers): one integration-level check of
what this phase's tasks assembled, plus the package- or project-wide typecheck or
build, sourced verbatim from Technical Context and never assumed. It is a checkpoint,
not a repeat: never the task Definitions of Done again, never a full suite.

A phase holds two to five tasks. More than that and the tasks are file-sized — see
[Task sizing](./task-sizing-and-tiers.md#task-sizing).

The last phase of every non-trivial plan is the
[Final Verification Phase](#final-verification-phase).

Each **task** is one delegation to one subagent, sized per
[Task sizing](./task-sizing-and-tiers.md#task-sizing), and carries:

- **Description** — near-imperative, naming the files and the behavior to change.
- **Files:** — every file touched, each labeled `create` / `modify` / `reuse`. If a
  file was created by an earlier task, back-reference it: `(modify — created in
  Task 1.1)`.
- **Definition of Done** — a checkbox list; rules below.
- **Stop Rule** *(optional)* — one sentence telling the implementer to stop and
  report instead of improvising when an expected seam is missing or the task cannot
  proceed safely.
- **Clues** *(optional)* — file paths, line ranges, reference patterns, gotchas.

## Definition of Done rules

Scope comes from [Verification tiers](./task-sizing-and-tiers.md#verification-tiers). These rules cover the
rest of what makes a plan verifiable rather than aspirational:

- At least one check per task must be objectively verifiable by a reviewer.
- **Every item must be satisfiable by the task alone.** An item that depends on a
  later task landing is a sizing error, not a caveat to write down.
- A task that changes code includes at least one runnable command taken **verbatim**
  from Technical Context, matched to the app the task's files belong to — for example
  `pnpm vitest run src/reports/csv-serializer.spec.ts`. Never assume the stack.
- Commands are file-scoped: the test files this task creates or modifies, at whatever
  layer they sit — a task that delivers an integration test runs that file.
  Directory-, package- and project-wide runs belong to a later tier.
- A docs, config, content, or asset task with no runnable command uses a
  deterministic content assertion instead — for example
  `docs/reports.md contains an "## Export" section`.
- Three to six items is the usual shape. A Definition of Done that restates the
  description line by line is bookkeeping, not verification.
- No deployment steps, no manual QA steps, and nothing a code reviewer could not
  confirm during review.

## Parallel groups

**Why:** The orchestrator launches a group's subagents in one message; they run
concurrently. Independence is decided here — only the planner sees the whole
dependency picture — and the plan must show it was examined: designed, not noticed.

**Include when:** Always — every phase marks its groups or justifies its edges.

Rules:

- Two tasks may share a group only when neither consumes the other's output **and**
  their `**Files:**` lists are disjoint. Shared files mean concurrent writers — never
  allowed.
- Mark groups explicitly where the tasks are defined, for example:
  `Parallel group A: Tasks 2.1, 2.2, 2.3 — independent, disjoint files.`
- A chained phase justifies each edge instead, for example:
  `Sequential: 2.2 consumes the DTO 2.1 creates.` An edge with no data or contract
  dependency behind it — only layering habit — is a mis-slicing: re-cut by behavior.
- Unsure whether two tasks are independent? Check, don't sequence: diff their
  `**Files:**` lists and grep each task's outputs against the other's inputs. An
  edge is earned by a dependency the check finds or cannot rule out — never by an
  unexamined "probably related", which costs a delegation slot on every execution
  of the plan.

Most accidental chains come from slicing by layer, or from every task appending one
line to the same registration files — barrels, module registration, route tables.
The fix is fork–join: a short **foundation task** pins the contracts and touches each
shared hotspot file once, pre-registering stubs; a **wide parallel group** fills in
the behaviors, files disjoint by construction; a tiny **stitch task** follows only
where pre-registration is impossible. Width bought this way is free — width bought
by splitting one coherent change is a sizing error.

Independence holds between phases too. A phase that consumes nothing from a
predecessor — no shared files, no contract crossing the boundary, typically a
different package — is marked `Independent of Phase N` in its parallelism statement,
and the orchestrator runs the two concurrently, each closing with its own
checkpoint. Multi-package features are the usual win: the API phase and the frontend
phase that both build only on Phase 1's contracts run side by side instead of
queueing. The final verification phase is never independent — it gates on everything.

## Final Verification Phase

**Why:** This is the single full pass — the last row of
[Verification tiers](./task-sizing-and-tiers.md#verification-tiers). Every earlier check is deliberately narrow
so this one can afford to be complete, exactly once. After it passes nothing
re-reviews or re-verifies: findings route back as scoped fixes with scoped re-checks.

**Include when:** Always, as the last phase of every non-trivial plan. A plan trivial
enough to skip it is trivial enough not to need a plan.

It contains exactly two tasks, a canonical parallel pair — the reviewer is read-only
while the verifier exercises the running app, so they are disjoint by construction:

- **Code review** — delegated to `code-reviewer` with the plan path, the changed-file
  list, and the `gate-runner` report the orchestrator fronts it with: the gates run
  once, and the reviewer judges from their verbatim results — implementation reports
  are claims. The delegation states that functional and E2E verification runs in the
  parallel verifier, so the reviewer excludes those suites.
- **Functional verification** — delegated to `feature-verifier` with the path to the
  plan's verification document (`specifications/<task-id>/<task-name>.verification.md`,
  drafted at planning time with the user — see
  [the verification-document reference](./verification-doc.md)). It executes the
  document's scenarios against the running app: browser walkthroughs with examined
  screenshots, real API calls, database and log checks, seeding where the document
  says so.

A project with a **committed E2E suite** lists running it as scenario zero of the
verification document — on the verifier's side, so it runs exactly once. This phase
verifies feature behavior; design fidelity against Figma was already verified by
`ui-engineer` per component and is not repeated here.

## Security Considerations

**Why:** Security review at plan time costs one paragraph; at incident time it costs
a weekend. Name the considerations specific to this change — input validation, authz
boundaries, secrets handling, injection surfaces.

**Include when:** The change touches input handling, auth, personal data, file or
network access, or query construction.
**Drop when:** Nothing above applies — an empty boilerplate section trains readers to
skip it.

## Acceptance Criteria

**Why:** A checkbox list of the conditions that prove the requirement is met, checked
during final review. Distinct from per-task Definitions of Done: DoD proves a task
was executed; acceptance criteria prove the feature works.

**Include when:** The task came with acceptance criteria, or the feature has
user-observable behavior worth enumerating. Criteria with user-observable behavior
are also the raw material for the verification document's scenarios.

## Improvements (Out of Scope)

**Why:** Planning surfaces adjacent problems. Recording them here keeps the plan's
scope intact while preserving the findings — this is where "plan only the current
task" sends everything else.

**Include when:** Anything tempting-but-out-of-scope came up. That is nearly always.

## Changelog

**Why:** A dated list of material plan changes keeps a long-lived plan honest across
sessions and revisions.

**Include when:** The plan will be revised across sessions or by several people.
**Drop when:** The plan will likely be executed once, shortly after writing —
git history already covers it.
