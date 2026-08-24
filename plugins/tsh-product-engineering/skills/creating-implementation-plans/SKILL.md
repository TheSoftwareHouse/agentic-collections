---
name: creating-implementation-plans
description: "Writes TSH's implementation plan as a committed file at specifications/<task-id>/<task-name>.plan.md: phased tasks that each name their files and a verifiable Definition of Done, technical context persisted for implementers, explicit parallel groups. Use when a plan, spec, or task breakdown is asked for — a plan kept outside the repository cannot be committed, reviewed in a PR, or read by an implementer subagent."
when_to_use: "Trigger on: 'write an implementation plan', 'plan this feature', 'break this into tasks', revising an existing *.plan.md, preparing tasks for parallel implementation, or any spec-driven development request. Writes the plan only — executing it is orchestrating-feature-implementation."
---

# Creating Implementation Plans

This skill turns a designed solution into a plan document that a human can review in
minutes and an implementer subagent can execute without seeing the conversation. The
plan is a file, not a chat message: it survives the session, travels in a commit, and
is the single handoff artifact for delegated implementation.

## When to Use

- A feature or task needs a plan before implementation starts.
- An existing `*.plan.md` needs revision after new findings or user feedback.
- Work will be delegated to implementer subagents — possibly several in parallel —
  and each needs a self-contained specification.

## Applicability and Precedence

Local repository rules outrank this skill. If the project has its own planning or
specification convention (location, naming, required sections), follow it and apply
this skill's rules only where the local convention is silent.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Save the plan as a file. Default: `specifications/<task-id>/<task-name>.plan.md`, where `<task-id>` is the ticket ID or a short kebab-case task name. Run `git check-ignore` on the path and tell the user when it is ignored — an ignored plan never travels in a commit, and its checkbox audit trail stays local to one machine. |
| MUST | Choose sections deliberately from the building blocks — match plan depth to task risk. A config tweak gets a goal and two tasks; a schema migration gets the full treatment. |
| MUST | Gather evidence through read-only `context-scout` subagents — several in parallel, one question-cluster each — which return file:line locations and bounded verbatim excerpts, never conclusions. Read directly only the design-critical files the plan pins contracts against, and write the Technical Context yourself from the returned evidence: interpretation is never delegated. This holds from the first exploratory question, whatever tool does the reading — a file dumped into the conversation through a shell command is an inline read all the same. |
| NEVER | Put implementation code in the plan. Type definitions, function signatures, DTOs, and API shapes are allowed to pin a contract; pseudo-code only for genuinely complicated algorithms. |
| MUST | Name every file each task touches in a `**Files:**` field, each labeled `create`, `modify`, or `reuse`. |
| MUST | Size a task as the smallest change that leaves the project's static gate green on its own — a contract change and the call sites it breaks are one task. Split by behavior, not by layer; two to five tasks per phase. A Definition of Done item that cannot pass until a later task lands means the two are one task: merge them. |
| MUST | Assign every check to exactly one tier by its scope: file-scoped tests to the task's Definition of Done, the phase's integration check and the package-wide typecheck, lint or build to the phase `Verification:` line, full suites and functional scenarios to the final verification phase. |
| MUST | Give every task a Definition of Done whose every item the task can satisfy alone, with at least one objectively verifiable check. Commands come verbatim from the plan's Technical Context — never assumed from Node/npm — and are file-scoped: the test files the task itself writes. |
| NEVER | Put a package- or project-wide typecheck, lint or build in a task's Definition of Done, or a formatter run at any tier — formatting is part of doing the work, not a check, and never a reason to re-run one. |
| MUST | Prove commands and artifacts before handover — once per shape, never per instance: every command names a script that exists in the project's manifest (a lookup, not a run) with paths that exist or that its own task creates, and each distinct file-scoped runner shape is executed once per package to prove it actually scopes, by its reported file count — one proven shape covers every command that uses it. Artifacts a Definition of Done or verification scenario names and the plan does not itself create — endpoint routes, tables, fixtures, env vars — are each checked against source with a search. An invented one surfaces mid-execution, where it stops the delegation line; in a verification document it deadlocks the final phase on a precondition that can never pass. |
| MUST | Sweep for exhaustive assertion inventories before handover, searching by inventory pattern — `information_schema`, migration ledgers, `toEqual([`, allowlists, fake-server fixtures — across every test tier, e2e and integration included. An enumerating inventory names every existing member and never the new one, so a search for the contract's name cannot find it; and one living in an e2e suite is invisible to every checkpoint before the final phase. Close each hit: a task's `**Files:**` list, or a checked-unaffected note in the plan. |
| MUST | End every non-trivial plan with a final verification phase: a code-review task and a functional-verification task, executable in parallel. Draft the verification document at `specifications/<task-id>/<task-name>.verification.md` at planning time, and ask the user which functional checks it should include — before implementation starts. |
| MUST | Design for parallel execution, then prove it: parallel is the default state, and a sequential edge exists only where a named data or contract dependency forces it. Every phase states its groups or justifies each edge, and a phase sharing no files and no contracts with its predecessor is marked independent of it, so the orchestrator runs both concurrently. Tasks share a group only when neither consumes the other's output AND their `**Files:**` lists are disjoint. An edge justified only by layering, or by shared registration hotspots fork–join would remove, is a mis-slicing — re-cut by behavior; never split a coherent change to manufacture a group. |
| MUST | Consult the Current Implementation Analysis before planning new components — reuse or extend existing code first. |
| MUST | Plan only the current task. Record prerequisite or follow-up work under Improvements (Out of Scope), not as extra phases. |
| NEVER | Add approval tables, revision predicates, or status bookkeeping. The user approves by reading the plan and saying so; iterate until they are satisfied. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Plan building blocks](./references/plan-building-blocks.md) | Assembling or revising a plan's structure — every time, before drafting | Every candidate section: why it exists, when to include it, when to drop it, plus parallel-group design and the Definition of Done rules in full |
| [Task sizing and verification tiers](./references/task-sizing-and-tiers.md) | Breaking work into phases and tasks — every time, with the building blocks | The smallest-green-change sizing rule and its practical bounds, and the tier table assigning every check to task, phase, or final verification |
| [Inventory sweep](./references/inventory-sweep.md) | Any task changes a contract — a schema, a shared type, an API response, an enum | Why enumerating inventories evade a name search, the sweep table keyed by change type, and the closure rule |
| [Worked example](./references/plan-example.md) | Unsure how a finished plan reads, or calibrating depth for a mid-size task | One complete plan for a small feature — illustrative, not a template to fill |
| [Verification document](./references/verification-doc.md) | Drafting the final verification phase's document — every non-trivial plan | The document's building blocks, scenario tags, evidence rules, and a compact worked example |

## Procedure

1. **Confirm the inputs.** You need the task's goal, constraints, and acceptance
   expectations. If requirements are ambiguous, ask the user before drafting —
   an ambiguous plan just moves the ambiguity into implementation.
2. **Establish technical context.** Follow
   [`discovering-technical-context`](../discovering-technical-context/SKILL.md): read
   project instructions, then existing patterns — gathering through `context-scout`
   subagents, launched in parallel with one question-cluster each, so raw file
   content and dead-end reads stay out of this conversation. Read directly only the
   design-critical files the plan will pin contracts against, and write the
   Technical Context yourself from the returned evidence. You will persist what you
   find into the plan so implementers never rediscover it.
3. **Pick the building blocks.** Read
   [`./references/plan-building-blocks.md`](./references/plan-building-blocks.md) and
   select the sections this task actually needs. Tell the user in one line which
   blocks you dropped and why.
4. **Analyze the current implementation.** List what already exists to reuse, what
   must change, and what is genuinely new — with file paths. Locating is scout work:
   send the sweeps to `context-scout` and judge reuse from the excerpts it returns.
5. **Break the work into phases and tasks.** Size each task by the rule above —
   one coherent, independently green change, not one file — then give it a
   near-imperative description naming the files and the behavior to change, a
   `**Files:**` field, a Definition of Done whose every item it can satisfy alone,
   and optionally a Stop Rule and Clues. Assign each check to its tier before moving
   on; the tier table in
   [`./references/task-sizing-and-tiers.md`](./references/task-sizing-and-tiers.md)
   is the arbiter.
6. **Sweep exhaustive inventories.** With the `**Files:**` lists drafted, delegate
   the searches of the sweep in
   [`./references/inventory-sweep.md`](./references/inventory-sweep.md) to
   `context-scout`: search by
   inventory pattern, not contract name — an enumerating inventory lists every
   existing member and never the new one — across every test tier, fixtures and
   fake servers included. Close each hit into a task's `**Files:**` list or a
   checked-unaffected note in the plan.
7. **Audit the dependency edges, then mark parallel groups.** For every sequential
   pair of tasks, name the data or contract dependency that forces the order. An
   edge with none behind it — layering habit, or one shared registration file — is a
   re-slicing candidate: re-cut by behavior, or apply the fork–join pattern from the
   building-blocks reference. Write the verdict into each phase: an explicit group
   (for example `Parallel group A: Tasks 2.1–2.3 — independent, disjoint files.`) or
   the justification per remaining edge. The orchestrator will launch one subagent
   per task in the group, so the disjoint-files rule is what prevents them from
   overwriting each other. Then audit the phase edges the same way: a phase that
   consumes nothing from its predecessor — disjoint files, no contract crossing the
   boundary — is marked `Independent of Phase N`, and the orchestrator runs the two
   concurrently, each closing with its own checkpoint.
8. **Persist the Technical Context** into the plan: stack and versions, conventions,
   and the verbatim verification commands the Definitions of Done use.
9. **Prove the commands and the nouns — once per shape.** Check every Definition of
   Done and phase `Verification:` command against the repository before handover:
   the script exists in the project manifest (a lookup, not a run), and its paths
   exist or are created by the task that runs them. Then execute each **distinct**
   file-scoped runner shape once per package and read its reported file count — a
   runner can silently swallow its path arguments and go green on the whole suite,
   and one proven run covers every command sharing that shape; never re-prove the
   same shape per task. Then search the source for each artifact a Definition of
   Done or verification scenario names and the plan does not itself create —
   endpoint routes, tables, fixtures, env vars. Each mismatch found now is a
   mid-execution plan revision avoided; an invented endpoint in the verification
   document is a final phase deadlocked on a precondition that can never pass.
10. **Draft the verification document.** Read
   [`./references/verification-doc.md`](./references/verification-doc.md), propose
   the candidate checks — browser walkthrough, API calls, database state, log checks,
   data seeding — and ask the user which to include. Save the document next to the
   plan.
11. **Hand the plan and the verification document to the user.** Ask them to read
   both and iterate together until they say what they mean. The plan file is the
   agreement; there is nothing to sign.

## Related Skills

Both ship in this plugin — if this skill loaded, they are installed. Step 2 of the
procedure depends on the first.

- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  populates the plan's Technical Context section. Required by Step 2.
- [`orchestrating-feature-implementation`](../orchestrating-feature-implementation/SKILL.md) —
  executes the finished plan.
