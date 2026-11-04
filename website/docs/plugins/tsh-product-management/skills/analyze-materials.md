---
title: Analyze Materials
sidebar_label: analyze-materials
sidebar_position: 1
description: Entry-point command for the full business-analysis workflow, from workshop materials or an existing Jira backlog to reviewed epics and stories.
sources:
  - plugins/tsh-product-management/skills/analyze-materials/
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
sources_hash: "047f578d46ad476051bc012acd16636b5fa4d57c19314e1ed33721d0bf8f730d"
---

# Analyze Materials

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:analyze-materials <materials>`. It runs only when you invoke it (`disable-model-invocation: true`).  
**Used by:** [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) points to it as the explicit handoff when the user wants to continue from Explore Mode to extraction.

A command, not a routing surface. It takes the materials or target you supply and hands the whole workflow to [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis). If you supply nothing, it asks what to process before doing anything else.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Accepted input** | A transcript path, a Figma or FigJam link, a PDF or a folder of documents, Jira issue keys, or a Jira project key |
| **What it runs** | It invokes `/tsh-product-management:orchestrating-business-analysis` and follows it end to end. The instructions say to invoke the skill rather than read its `SKILL.md`, because invoking it is what puts the skill's own configuration into effect |
| **Entry-point routing** | Transcript, designs, PDFs and notes start the standard workflow at transcript processing. Jira keys or a project key start Import Mode in [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues), then the quality review. Materials too ambiguous to commit to a backlog get an offer of [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) first |
| **Prerequisites check** | The workflow needs the Atlassian MCP server for anything Jira and Figma MCP for design links. The command checks what the session has and says so up front instead of discovering it at the push |

## What you end up with

In `specifications/<workshop-name>/`, named after the workshop topic in kebab-case (for example `specifications/user-onboarding/`):

- `.gates.md`, the gate ledger, created first and updated as each gate is approved
- `cleaned-transcript.md`, when a raw transcript was supplied
- `intent-brief.md`, approved at Gate 0 before extraction begins
- `extracted-tasks.md`, the epic and story breakdown, updated after quality review
- `quality-review.md`, every suggestion and its disposition
- `.roadmap-proposal.md`, the draft reviewed at the Roadmap Review gate
- `jira-tasks.md`, the Jira-ready tasks

Surviving the session, at project level:

- `specifications/projects/<project-name>/roadmap.md`, written only after Roadmap Review approval
- `specifications/projects/<project-name>/task-baseline.md`, refreshed after a verified push

## Related skills

- [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) owns the procedure, the five gates, the delegation and the Jira push.
- [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) is the entry point that stops at a business-context summary.

## Source

[`plugins/tsh-product-management/skills/analyze-materials/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/analyze-materials/SKILL.md)
