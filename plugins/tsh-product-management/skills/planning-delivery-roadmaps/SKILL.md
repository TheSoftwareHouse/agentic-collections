---
name: planning-delivery-roadmaps
description: "Reconciles approved epics, accepted quality findings, a project baseline and any existing roadmap into one Markdown-only, per-project roadmap: client-facing outcome waves and an internal coordination view, linked by project-scoped stable epic IDs. Use after the task list is confirmed and before Jira formatting; it creates no Jira data and changes no statuses."
when_to_use: "Trigger on: planning delivery waves, 'what order do we build this in', reconciling a new workshop against an existing roadmap, allocating epics to parallel tracks, or updating a project roadmap after a backlog change."
---

# Planning Delivery Roadmaps

Produces one dual-audience planning artifact per project: what the client will see
demonstrated, and how the work can safely be coordinated internally — the two views
bound together by stable epic identity.

## Applicability and Precedence

An existing `specifications/projects/<project-name>/roadmap.md` outranks fresh
interpretation: prior identities, delivery history and recorded decisions are
retained, never rewritten. The Epic Delivery Contract from
`extracting-epics-and-stories` is evidence about an epic; this skill decides what
that evidence permits.

## Explicit Exclusions

Markdown only. No Jira releases, custom fields, synchronization, formatter changes
or status mutation. No calendar dates, estimates, team assignments, assignees or
resource planning.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Identify every epic by one project-scoped stable ID, reused across all views and all future updates. Workshop-local labels like `Epic 1` are not identity. |
| MUST | Record an explicit `Match` decision with evidence, or `Review required`, whenever an incoming epic arrives without an ID. |
| MUST | Allocate every active epic to exactly one wave, or document the exception and its reason. |
| MUST | Give every wave a demonstrable client outcome. |
| MUST | Run the whole reconciliation in one context — never split it across workers. Partial epic sets produce conflicting ID allocations. |
| NEVER | Silently delete a record or reassign a prior stable epic ID. |
| NEVER | Put an epic blocked on an unresolved required shared contract on a parallel track. |
| NEVER | Write the project roadmap before the Roadmap Review approval is recorded in `.gates.md`. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Roadmap example](./references/roadmap-example.md) | Before producing or updating any roadmap — always | The four tables, their columns, and the Change Log shape |

## Execution Context

Running in the main conversation: write the proposal to
`specifications/<workshop-name>/.roadmap-proposal.md`, run the Roadmap Review gate
yourself, and only then create or update the project roadmap. Running as the
`roadmap-planner` subagent: you have no interactive and no write tool — return the
proposal as your final message with anything unresolved under `## Review Required`.

## Procedure

1. **Collect the project inputs**: the approved epic list with its delivery
   contracts, accepted quality findings, the project baseline, and the existing
   `specifications/projects/<project-name>/roadmap.md` where one exists.
2. **Reconcile stable epic identities.** Match by stable ID when supplied. When one
   is absent, record a `Match` decision naming the matched prior ID and its
   evidence, or `Review required`, *before* issuing or reusing an ID. A genuinely
   new epic gets a new ID. Classify every record as `New`, `Revised`, `Unchanged`,
   `Completed`, `Deferred`, `Removed` or `Superseded`, and retain prior entries and
   delivery history.
3. **Build the two linked views** with the same stable IDs:
   - **Client-facing outcome waves** — each wave states a demonstrable client
     outcome and holds the active epics that deliver it.
   - **Internal coordination** — each allocated epic names its parallel track,
     blockers, required shared contracts, and declared dependency or contract state.

   Parallel tracks are permitted only where the declared dependency and
   shared-contract state make them safe. A technical enabler never stands alone as
   a non-demoable epic: embed it in a demonstrable vertical slice, or pair it with
   one in the same wave.
4. **Validate, then propose.** Check that every active epic is allocated once or
   excepted with a reason; every wave has a demonstrable client outcome; tracks are
   safe under the declared state; blockers and required shared contracts are
   visible; the two views carry matching IDs; the Change Log names the source
   workshop and every addition, revision, removal, deferment, completion and
   supersession; and historical entries survive.

   Then write the proposal to `.roadmap-proposal.md` and run **Roadmap Review**
   against the file — four tables across every epic in the project neither fit in a
   gate question nor survive context compaction. Revise the draft in place on
   rejection. Only once the approval is recorded in `.gates.md` may
   `specifications/projects/<project-name>/roadmap.md` be created or updated.

## Related Skills

- [`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md) — supplies
  delivery-ready epics, their contracts and their source context.
- [`reviewing-backlog-quality`](../reviewing-backlog-quality/SKILL.md) — supplies the
  accepted findings; its Pass R checks epic readiness but leaves wave, track and
  allocation decisions to this skill.
- [`formatting-jira-issues`](../formatting-jira-issues/SKILL.md) — runs after the
  approved roadmap, and is unaffected by it: no roadmap content reaches Jira.
