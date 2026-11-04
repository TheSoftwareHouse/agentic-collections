---
title: Planning Delivery Roadmaps
sidebar_label: planning-delivery-roadmaps
sidebar_position: 9
description: Reconciles approved epics, accepted quality findings, a project baseline and any existing roadmap into one Markdown-only per-project roadmap with client-facing waves and an internal coordination view.
sources:
  - plugins/tsh-product-management/skills/planning-delivery-roadmaps/
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
sources_hash: "a38213ab924a9a60f3ebdd925bb041296e087c61ac3e716d76e48ab0e2a8c178"
---

# Planning Delivery Roadmaps

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:planning-delivery-roadmaps`. Claude also loads it when a request matches its description.  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) (step 8) and the [`roadmap-planner`](/docs/plugins/tsh-product-management/agents/roadmap-planner) agent, which preloads it. The orchestrator may also apply it inline instead of delegating.

Produces one dual-audience planning artifact per project: what the client will see demonstrated, and how the work can safely be coordinated internally, the two views bound together by stable epic identity. It runs after the task list is confirmed and before Jira formatting, and it creates no Jira data and changes no statuses.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Markdown only** | No Jira releases, custom fields, synchronization, formatter changes or status mutation. No calendar dates, estimates, team assignments, assignees or resource planning |
| **Stable epic IDs** | Every epic has one project-scoped stable ID reused across all views and all future updates. Workshop-local labels such as `Epic 1` are not identity |
| **Reconciliation** | An incoming epic without an ID gets an explicit `Match` decision with evidence, or `Review required`, before an ID is issued or reused. Every record is classified as `New`, `Revised`, `Unchanged`, `Completed`, `Deferred`, `Removed` or `Superseded`, and prior entries and delivery history are retained |
| **Two linked views** | Client-facing outcome waves, each with a demonstrable client outcome, and an internal coordination view naming each epic's parallel track, blockers, required shared contracts and declared dependency or contract state |
| **Tracks and enablers** | Parallel tracks are allowed only where the declared dependency and shared-contract state make them safe. An epic blocked on an unresolved required shared contract never goes on a parallel track. A technical enabler is embedded in a demonstrable vertical slice or paired with one in the same wave |
| **Allocation** | Every active epic is allocated to exactly one wave, or the exception and its reason are documented |
| **Single context** | The whole reconciliation runs in one context and is never split across workers, because partial epic sets produce conflicting ID allocations |
| **Precedence** | An existing `specifications/projects/<project-name>/roadmap.md` outranks fresh interpretation. The Epic Delivery Contract is evidence about an epic, and this skill decides what that evidence permits |

## How it works

1. Collect the project inputs: the approved epic list with its delivery contracts, accepted quality findings, the project baseline and the existing roadmap where one exists.
2. Reconcile stable epic identities and classify every record.
3. Build the client-facing and internal views with the same stable IDs.
4. Validate, then propose. The checks cover single allocation or a documented exception, a demonstrable outcome per wave, safe tracks, visible blockers and shared contracts, matching IDs across the two views, a Change Log naming the source workshop and every change, and surviving history. The proposal is written to `.roadmap-proposal.md` and Roadmap Review runs against that file. The draft is revised in place on rejection.

The project roadmap at `specifications/projects/<project-name>/roadmap.md` is created or updated only after the Roadmap Review approval is recorded in `.gates.md`. As the `roadmap-planner` subagent the skill has no interactive and no write tool: it returns the proposal as its final message with anything unresolved under `## Review Required`.

## What it produces

A roadmap with these sections: Project Identity and Context, Client-Facing Outcome-Based Waves, Internal Coordination, Stable Epic Catalog and Reconciliation State, and Change Log.

## Related skills

- [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) supplies delivery-ready epics, their contracts and their source context.
- [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) supplies the accepted findings. Its Pass R checks epic readiness but leaves wave, track and allocation decisions to this skill.
- [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) runs after the approved roadmap and is unaffected by it: no roadmap content reaches Jira.

## Source

[`plugins/tsh-product-management/skills/planning-delivery-roadmaps/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/planning-delivery-roadmaps/SKILL.md)
