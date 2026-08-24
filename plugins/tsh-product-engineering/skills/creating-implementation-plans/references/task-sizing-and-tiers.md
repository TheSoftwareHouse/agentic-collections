# Task sizing and verification tiers

Use this reference every time work is broken into phases and tasks, together with
[the building blocks](./plan-building-blocks.md). Sizing decides where a task's
boundaries sit; the tiers decide where each check runs. They are one system: a task
that seems to need a higher tier's check is a task cut at the wrong boundary.

## Task sizing

**Why:** A task is one delegation to one subagent. Each boundary costs a full context
re-read at the start and a report-and-gate cycle at the end, so a plan split too fine
spends more on handoffs than on work — and hands the orchestrator an integration
problem the planner should have solved. Split too coarse and the delegation stops
being reviewable.

**The rule:** a task is the smallest change that leaves the project's static gate
green on its own. A change that cannot typecheck or build until a later task lands is
not a task; it is half of one.

The tell is a Definition of Done written as `typecheck passes *(blocked until Task
1.3)*`. That is the plan admitting the seam is in the wrong place — merge the two
tasks rather than deferring the gate.

Practical bounds:

- **A contract change and the call sites it breaks are one task.** Widening a shared
  signature is not a deliverable; a working codebase using the wider signature is.
  Produce that task's `**Files:**` list from a search, not recall: grep the
  contract's name and its distinctive fields across the workspace — test
  directories, fixtures, and untyped scripts included — then run the sweep in
  [`inventory-sweep.md`](./inventory-sweep.md), which finds the enumerating
  inventories a name search cannot: they list every existing member and never the
  new one. Every breakage the list misses surfaces as a failed gate one tier
  later, in a file no delegate owns.
- **Split by behavior, not by layer.** "The export endpoint" — serializer, route, and
  their tests — beats three tasks that each deliver one file of it.
- **Two to five tasks per phase** is the usual shape.
- **Upper bound: a task must stay reviewable.** If its description needs more than a
  paragraph, or lists behaviors that could ship separately, split it — by behavior.
- **Never split a coherent change to create a parallel group** — see
  [Parallel groups](./plan-building-blocks.md#parallel-groups), which owns the rule.

## Verification tiers

**Why:** Every check a plan names gets run by someone. Naming one check at two tiers
runs it twice for the same answer, and that duplication — not the work — is what
makes a delegated workflow feel slow.

Assign each check to exactly one tier, by its **scope**:

| Check | Tier | Runs |
| --- | --- | --- |
| Unit or component tests over the files this task wrote | Task Definition of Done | once per task |
| Deterministic content assertion, for a task with no runnable command | Task Definition of Done | once per task |
| Integration check of the interaction this phase's tasks assembled | Phase `Verification:` line | once per phase |
| Typecheck, lint, or build at package or project scope | Phase `Verification:` line | once per phase |
| Full suites, E2E, functional scenarios, security and anti-pattern review | Final verification phase | once per plan |

Four consequences the plan must respect:

- **A task's Definition of Done never carries a package- or project-wide typecheck,
  lint, or build.** One task cannot make those pass or fail alone, and running them
  per task pays N times for one answer. A task that seems to need one is too small —
  see [Task sizing](#task-sizing).
- **Running a formatter is not a check.** It is part of doing the work: it runs
  before the task's checks and never justifies re-running one that already passed.
  Give it no Definition of Done line and no place on a phase `Verification:` line. If
  the project mandates one, record it in Technical Context as a convention and let
  the final review's static gate catch a miss.
- **A phase checkpoint may subsume test files individual tasks created.** That
  overlap is correct — a checkpoint covers the phase, a Definition of Done covers one
  task. Do not "fix" it by widening task Definitions of Done or dropping the phase
  line.
- **The phase line's typecheck or build must compile the phase's test sources.**
  Check what each gate actually compiles while persisting Technical Context: a
  package whose `typecheck` and `build` exclude spec files (a `tsconfig.build` that
  omits them) can carry an uncompilable test through every checkpoint until the
  final full pass. Where that is the case, the phase `Verification:` line uses the
  package-scoped test run — the command that does compile them — instead.
