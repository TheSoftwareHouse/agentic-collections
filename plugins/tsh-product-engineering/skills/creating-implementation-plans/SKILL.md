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
| MUST | Save the plan as a file. Default: `specifications/<task-id>/<task-name>.plan.md`, where `<task-id>` is the ticket ID or a short kebab-case task name. |
| MUST | Choose sections deliberately from the building blocks — match plan depth to task risk. A config tweak gets a goal and two tasks; a schema migration gets the full treatment. |
| NEVER | Put implementation code in the plan. Type definitions, function signatures, DTOs, and API shapes are allowed to pin a contract; pseudo-code only for genuinely complicated algorithms. |
| MUST | Name every file each task touches in a `**Files:**` field, each labeled `create`, `modify`, or `reuse`. |
| MUST | Give every task a Definition of Done with at least one objectively verifiable check. Commands come verbatim from the plan's Technical Context — never assumed from Node/npm — and scoped to the task's own files: targeted unit tests, lint or typecheck on the changed area, plus any test file the task itself creates. Never directory- or project-wide suites — integration interactions belong to phase verification, full passes to the final verification phase. |
| MUST | End every non-trivial plan with a final verification phase: a code-review task and a functional-verification task, executable in parallel. Draft the verification document at `specifications/<task-id>/<task-name>.verification.md` at planning time, and ask the user which functional checks it should include — before implementation starts. |
| MUST | Mark independent tasks as an explicit parallel group. Tasks qualify only when neither depends on the other's output AND their `**Files:**` lists are disjoint. |
| MUST | Consult the Current Implementation Analysis before planning new components — reuse or extend existing code first. |
| MUST | Plan only the current task. Record prerequisite or follow-up work under Improvements (Out of Scope), not as extra phases. |
| NEVER | Add approval tables, revision predicates, or status bookkeeping. The user approves by reading the plan and saying so; iterate until they are satisfied. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Plan building blocks](./references/plan-building-blocks.md) | Assembling or revising a plan's structure — every time, before drafting | Every candidate section: why it exists, when to include it, when to drop it, and the Definition of Done rules in full |
| [Worked example](./references/plan-example.md) | Unsure how a finished plan reads, or calibrating depth for a mid-size task | One complete plan for a small feature — illustrative, not a template to fill |
| [Verification document](./references/verification-doc.md) | Drafting the final verification phase's document — every non-trivial plan | The document's building blocks, scenario tags, evidence rules, and a compact worked example |

## Procedure

1. **Confirm the inputs.** You need the task's goal, constraints, and acceptance
   expectations. If requirements are ambiguous, ask the user before drafting —
   an ambiguous plan just moves the ambiguity into implementation.
2. **Establish technical context.** Follow
   [`discovering-technical-context`](../discovering-technical-context/SKILL.md): read
   project instructions, then existing patterns. You will persist what you find into
   the plan so implementers never rediscover it.
3. **Pick the building blocks.** Read
   [`./references/plan-building-blocks.md`](./references/plan-building-blocks.md) and
   select the sections this task actually needs. Tell the user in one line which
   blocks you dropped and why.
4. **Analyze the current implementation.** List what already exists to reuse, what
   must change, and what is genuinely new — with file paths.
5. **Break the work into phases and tasks.** Each task gets a near-imperative
   description naming the files and the behavior to change, a `**Files:**` field, a
   Definition of Done scoped to the task's own files, and optionally a Stop Rule and
   Clues.
6. **Mark parallel groups.** Group tasks that can run concurrently and say so
   explicitly (for example `Parallel group A: Tasks 2.1–2.3`). The orchestrator will
   launch one subagent per task in the group, so the disjoint-files rule is what
   prevents them from overwriting each other.
7. **Persist the Technical Context** into the plan: stack and versions, conventions,
   and the verbatim verification commands the Definitions of Done use.
8. **Draft the verification document.** Read
   [`./references/verification-doc.md`](./references/verification-doc.md), propose
   the candidate checks — browser walkthrough, API calls, database state, log checks,
   data seeding — and ask the user which to include. Save the document next to the
   plan.
9. **Hand the plan and the verification document to the user.** Ask them to read
   both and iterate together until they say what they mean. The plan file is the
   agreement; there is nothing to sign.

## Related Skills

Both ship in this plugin — if this skill loaded, they are installed. Step 2 of the
procedure depends on the first.

- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  populates the plan's Technical Context section. Required by Step 2.
- [`orchestrating-feature-implementation`](../orchestrating-feature-implementation/SKILL.md) —
  executes the finished plan.
