---
title: Discovery Analyst
sidebar_label: discovery-analyst
sidebar_position: 2
description: Read-only worker agent that synthesizes workshop materials into a structured business summary with epic candidates, overlap, contradictions and open questions.
sources:
  - plugins/tsh-product-management/agents/discovery-analyst.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
sources_hash: "ae56dafdf3e971b9ad06ff71694e998833f1a5e919c0b4338bf75283a7ae862e"
---

# Discovery Analyst

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:discovery-analyst`  
**Model:** `sonnet`  
**Tools:** `Read, Grep, Glob`  
**Preloaded skill:** [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context)

Connects transcripts, documents, and the design and backlog context supplied by the orchestrator into a structured business summary that supports later extraction, without committing to any backlog item itself. It serves Explore Mode and the material-analysis phase before extraction, and one agent can be assigned per document across a large bundle.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation must name the documents, designs or activity it owns and state what is explicitly not its. If it names nothing readable, the agent stops and reports that |
| **Procedure** | Follows the preloaded `analyzing-discovery-context` skill: reads every source the delegation assigns, attributes each finding to where it came from and separates evidence from inference. While synthesizing it collects term candidates and their source-language forms alongside the epic candidates |
| **Design context** | It has no Atlassian and no design-tool access. Jira, board and Figma context arrive inline in the delegation prompt. If the delegation asks it to interpret a design and supplies no design context, it reports a blocker instead of guessing |
| **Design scope** | Supplied design context is interpreted for what the system must do: screens, flows, states, annotated business logic. Styling, pixel measurements and CSS values are out of scope |
| **Contradictions** | Cross-source contradictions are its highest-value output. It surfaces them explicitly instead of resolving them |
| **PDFs** | Read with `Read`, with an explicit `pages` range beyond 10 pages, chunks of at most 20, and a report rather than a guess when a scanned file comes back empty |
| **Boundaries** | No write tools and no interactive tool. It produces no final epics or stories, which is the extraction worker's job, and never speaks to the user directly |

## What it returns

Its final message is the return value, with no preamble:

- Business Context
- Actors and Business Entities
- Likely Epic Candidates
- Term Candidates
- Baseline / Backlog Overlap
- Open Questions
- Contradictions and Gaps
- Blockers (unreadable files, inaccessible designs, unsupported formats, or "none")

## Used by

[`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) delegates multi-source synthesis, baseline overlap and open questions to it, through its `delegating-to-workers.md` reference. [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) allows Explore Mode reading to be delegated to it.

## Source

[`plugins/tsh-product-management/agents/discovery-analyst.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/discovery-analyst.md)
