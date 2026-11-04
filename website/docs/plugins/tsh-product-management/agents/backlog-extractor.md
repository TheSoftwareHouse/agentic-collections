---
title: Backlog Extractor
sidebar_label: backlog-extractor
sidebar_position: 3
description: Read-only worker agent that drafts intent briefs and extracts epics and user stories for an assigned epic scope, returned as a report.
sources:
  - plugins/tsh-product-management/agents/backlog-extractor.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
sources_hash: "971616d8529bfe23c34fb55381070f2b4f621bef6c744972c855bf4f5cc1163b"
---

# Backlog Extractor

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:backlog-extractor`  
**Model:** `sonnet`  
**Tools:** `Read, Grep, Glob`  
**Preloaded skill:** [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories)

Turns approved business intent into structured backlog content that a stakeholder can read without technical knowledge. It is designed so that a large backlog fans out: one agent per epic.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation must name the source files to read and the exact scope it owns: which epic or epics. If the scope or the inputs are missing, it stops and reports what is absent instead of widening the scope. PDFs are read with `Read` and an explicit `pages` range beyond 10 pages |
| **Procedure** | Follows the preloaded `extracting-epics-and-stories` skill and applies its templates exactly |
| **Epic boundary** | Stories belonging to another worker's epic are not its, even when the material discusses them |
| **Traceability** | Every story carries a `Source` pointing back to the material it came from |
| **Delivery contract** | Every epic carries a complete Epic Delivery Contract: customer outcome, end-to-end boundary, explicit exclusions, demonstrable scenario or criteria, known dependency or required shared contract, and the collaboration/concurrency classification. Downstream review and roadmap planning read those fields, and a missing one becomes a finding against the epic |
| **Boundaries** | No write tools, no interactive tool and no Atlassian tools. It never creates Jira tasks. Acceptance criteria stay as business-friendly `GIVEN / WHEN / THEN` scenarios with no implementation jargon |

## What it returns

Its final message is the return value, with no preamble:

- Intent Brief, only when asked: goal, in and out of scope, stakeholders, likely epics, baseline overlap, open questions
- Epics: per epic its ID, title, 2 to 3 sentence business description, success criteria and delivery contract
- Stories: per story its ID, title, "As a… I want… So that…", Source, GIVEN/WHEN/THEN criteria, technical notes only if discussed, and a priority suggestion
- Cross-Epic Dependencies
- Assumptions
- Out of Scope
- Open Questions

## Used by

[`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) delegates intent brief drafting, epic identification and story extraction to it, through its `delegating-to-workers.md` reference (one agent per epic, or 2 to 3 small epics per agent). The orchestrator then merges the results and writes `extracted-tasks.md` itself.

## Source

[`plugins/tsh-product-management/agents/backlog-extractor.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/backlog-extractor.md)
