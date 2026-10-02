# Plan building blocks

Use this reference when assembling or revising a plan's structure. Each block below
explains why it exists and when it earns its place. Pick deliberately: a section that
adds no decision-relevant information for *this* task is noise the reader pays for on
every read. When in doubt for a risky task, include the block; when in doubt for a
trivial one, drop it.

## Table of Contents

- [Task Details](#task-details)
- [Goal](#goal)
- [Proposed Solution](#proposed-solution)
- [Current Implementation Analysis](#current-implementation-analysis)
- [Open Questions](#open-questions)
- [Technical Context](#technical-context)
- [Phases and Tasks](#phases-and-tasks)
- [Definition of Done rules](#definition-of-done-rules)
- [Parallel groups](#parallel-groups)
- [Final Verification Phase](#final-verification-phase)
- [Security Considerations](#security-considerations)
- [Acceptance Criteria](#acceptance-criteria)
- [Improvements (Out of Scope)](#improvements-out-of-scope)
- [Changelog](#changelog)

## Task Details

**Why:** Links the plan to its source of truth — the ticket, the research notes, the
conversation that produced it. Anyone opening the file cold can trace where the
requirements came from.

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
and a `**Verification:**` line: one integration-level check of the interaction this
phase's tasks created, plus one typecheck or build — sourced verbatim from Technical
Context, never assumed. It is a checkpoint, not a repeat: never the task Definitions
of Done again, never a full suite. The check may legitimately subsume test files
individual tasks created — a checkpoint covers the phase, a DoD covers one task — so
do not "fix" that overlap by widening task DoDs or dropping the phase line.

The last phase of every non-trivial plan is the
[Final Verification Phase](#final-verification-phase).

Each **task** carries:

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

These are what make a plan verifiable rather than aspirational:

- At least one check per task must be objectively verifiable by a reviewer.
- A task that changes code includes at least one runnable command taken **verbatim**
  from Technical Context, matched to the app the task's files belong to — for example
  `pnpm vitest run src/reports/csv-serializer.spec.ts` or
  `uv run pytest tests/reports/test_export.py`. Never assume the stack.
- Commands are scoped to the task's own files. A file-scoped run of a test file the
  task itself creates or modifies is fine at any layer — a task that delivers an
  integration test runs that file. Directory- and project-wide runs are not: the
  final verification phase provides the full-pass evidence, so task checks stay
  cheap.
- A docs, config, content, or asset task with no runnable command uses a
  deterministic content assertion instead — for example
  `docs/reports.md contains an "## Export" section`.
- No deployment steps, no manual QA steps, and nothing a code reviewer could not
  confirm during review.

## Parallel groups

**Why:** The orchestrator can launch several implementer subagents in one message and
they run concurrently. The plan is where independence is decided, because only the
planner sees the whole dependency picture.

**Include when:** Two or more tasks are genuinely independent.

Rules:

- Two tasks may share a group only when neither consumes the other's output **and**
  their `**Files:**` lists are disjoint. Shared files mean concurrent writers — never
  allowed.
- Mark groups explicitly where the tasks are defined, for example:
  `Parallel group A: Tasks 2.1, 2.2, 2.3 — independent, disjoint files.`
- When unsure whether two tasks are independent, they are not. Sequencing is cheap;
  untangling interleaved edits is not.

## Final Verification Phase

**Why:** This is the single full pass. Every earlier check is deliberately scoped —
task Definitions of Done to their own files, phase checkpoints to their phase — so
this one can afford to be complete, exactly once. After it passes, nothing
re-reviews and nothing re-verifies: findings route back as scoped fixes with scoped
re-checks.

**Include when:** Always, as the last phase of every non-trivial plan. A plan trivial
enough to skip it is trivial enough not to need a plan.

It contains exactly two tasks, a canonical parallel pair — the reviewer is read-only
while the verifier exercises the running app, so they are disjoint by construction:

- **Code review** — delegated to `code-reviewer` with the plan path and the full
  changed-file list. It runs static checks, unit and integration suites, and the
  build itself — implementation reports are claims, and this task is the one place
  evidence is re-established. The delegation states that functional and E2E
  verification runs in the parallel verifier, so the reviewer excludes those suites.
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
the UI verification gate per component and is not repeated here.

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
