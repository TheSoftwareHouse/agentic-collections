---
title: Transcript Cleaner
sidebar_label: transcript-cleaner
sidebar_position: 1
description: Read-only worker agent that cleans and structures a raw workshop or meeting transcript and returns it as a report.
sources:
  - plugins/tsh-product-management/agents/transcript-cleaner.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
  - plugins/tsh-product-management/skills/processing-workshop-transcripts/SKILL.md
sources_hash: "d4301408bb9bfe93f520ef66c797bbe556720a6194a738382751faad23844e75"
---

# Transcript Cleaner

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:transcript-cleaner`  
**Model:** `haiku`  
**Tools:** `Read, Grep, Glob`  
**Preloaded skill:** [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts)

Turns noisy discussion material into a disciplined, business-facing transcript that later analysis and extraction phases can rely on. It is a worker for the business-analysis workflow, so the main conversation does not spend its context on the raw text.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation must name the transcript files or paths it owns. If none is given or the file cannot be read, it stops and reports what is missing instead of improvising a source |
| **Procedure** | Follows the preloaded `processing-workshop-transcripts` skill in full: identify format and metadata, tag participants, remove non-business content, group by topic, extract decisions, action items and open questions, preserve quotes where wording matters, and collect the client's terms and their inflected surface forms as terminology candidates |
| **PDFs** | Read with `Read`, with an explicit `pages` range beyond 10 pages and chunks of at most 20. A scanned PDF with no text layer returns empty content, which it reports rather than inferring |
| **Scope** | Stays inside the material the delegation assigns and does not explore the repository |
| **Missing metadata** | When metadata is absent from the source it records "not stated in source" and never reconstructs a date, a role or a decision |
| **Boundaries** | No write tools and no interactive tool. Anything it would have asked goes under `## Open Questions`. It creates no backlog items, epics, stories or Jira tasks and never speaks to the user directly |

## What it returns

Its final message is the return value, which the orchestrator consumes verbatim, with no preamble:

- Meeting Metadata
- Participants
- Discussion Topics
- Key Decisions
- Action Items
- Open Questions
- Preserved Context
- Terminology
- Ambiguities for BA Analysis

## Used by

[`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) delegates transcript cleanup and structuring to it, through its `delegating-to-workers.md` reference. [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts) describes how to run when loaded into this agent.

## Source

[`plugins/tsh-product-management/agents/transcript-cleaner.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/transcript-cleaner.md)
