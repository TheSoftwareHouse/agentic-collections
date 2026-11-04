---
title: Roadmap Planner
sidebar_label: roadmap-planner
sidebar_position: 5
description: Read-only worker agent that reconciles approved epics, accepted findings, a baseline and any existing roadmap into one validated in-memory roadmap proposal.
sources:
  - plugins/tsh-product-management/agents/roadmap-planner.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
sources_hash: "749a5c57e4b6854eef7df783e932a85ae991da29aae643601eab66743d660ff4"
---

# Roadmap Planner

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:roadmap-planner`  
**Model:** `opus`  
**Tools:** `Read, Grep, Glob`  
**Preloaded skill:** [`planning-delivery-roadmaps`](/docs/plugins/tsh-product-management/skills/planning-delivery-roadmaps)

Produces and validates an in-memory roadmap proposal from the inputs the orchestrator supplies. It does not approve the proposal and does not persist it. It is used as a single agent before the Roadmap Review gate and the work is never split across several agents. Its model tier is deliberate: silently reassigning a stable epic ID or dropping a delivery-history record is unrecoverable from the artifact itself.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation supplies, or names paths to, the approved epic list with its delivery contracts, the accepted quality findings, the project baseline and the existing roadmap where one exists |
| **Whole epic set** | Reconciliation needs the whole epic set in one context. If the prompt gives only a subset of the project's epics, it says so under `## Review Required` instead of allocating IDs against a partial picture |
| **Procedure** | Applies the preloaded `planning-delivery-roadmaps` skill to the supplied inputs without restating its procedure in the output |
| **Durable identity** | Matches by stable ID when supplied. When one is absent it records an explicit `Match` decision naming the matched prior ID and its evidence, or `Review required`, before issuing or reusing any ID. It never guesses |
| **History** | It never deletes a record or reassigns a prior stable ID |
| **Evidence, then permission** | An epic's collaboration classification tells it what is known and it decides what that permits. An epic blocked on an unresolved required shared contract never goes on a parallel track |
| **Boundaries** | No write tools and no interactive tool. No Atlassian tools: the roadmap is Markdown-only, with no Jira releases, custom fields, synchronization, formatter changes or status mutation. No calendar dates, estimates, team assignments, assignees or resource planning |

## What it returns

Its final message is the return value, following the section order of the skill's roadmap example. The orchestrator writes it to `.roadmap-proposal.md` and, after approval, to the project roadmap. It includes:

- project-scoped stable epic IDs, with matching existing epics retaining theirs
- an explicit `Match` result with evidence, or `Review required`, for every incoming epic that arrived without an ID
- a reconciliation classification for every record: `New`, `Revised`, `Unchanged`, `Completed`, `Deferred`, `Removed` or `Superseded`
- client-facing outcome waves and an internal coordination view sharing the same IDs
- one wave allocation per active epic or an explicit documented exception, each wave's demonstrable client outcome, and each epic's track, blockers and required shared contracts
- validation that tracks are safe under the declared dependency and contract state, that blockers are visible, and that active epics are allocated once or excepted
- Change Log entries naming the source workshop and every addition, revision, removal, deferment, completion and supersession

It closes with a `## Review Required` section for ambiguous identity matches, partial epic sets, a missing baseline, contradictory dependency state, or anything else the supplied inputs could not settle.

## Used by

[`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) routes the confirmed tasks, accepted findings, baseline and existing roadmap to a single `roadmap-planner` at step 8. The orchestrator may skip the agent and apply the skill inline when the epic contracts are already in its context or the backlog is large, and says that it did and why.

## Source

[`plugins/tsh-product-management/agents/roadmap-planner.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/roadmap-planner.md)
