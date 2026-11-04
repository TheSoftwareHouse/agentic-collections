---
title: Analyzing Discovery Context
sidebar_label: analyzing-discovery-context
sidebar_position: 6
description: Builds the business context around a task or workshop topic, finds the gaps, resolves them with the user and writes a research report, without committing to any backlog item.
sources:
  - plugins/tsh-product-management/skills/analyzing-discovery-context/
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
sources_hash: "753ad1ba42b1146648c54afb1cdf117574388d1391881a2c7d9ddebf540b905b"
---

# Analyzing Discovery Context

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:analyzing-discovery-context`. Claude also loads it when a request matches its description.  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) (step 3), [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) and the [`discovery-analyst`](/docs/plugins/tsh-product-management/agents/discovery-analyst) agent, which preloads it.

Builds the picture the rest of the workflow depends on: what is already known, where it came from, and what is still missing. It does not create epics or stories, write technical specifications or implementation plans, or estimate.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Input sources** | Research or plan files (`*.research.md`, `*.plan.md`), a Jira or task ID fetched through the session's Atlassian MCP tools, context supplied inline, and PDFs read with `Read` (explicit `pages` range beyond 10 pages) |
| **Gathering** | Searches by ID where one exists and by domain and jobs-to-be-done where it does not. Follows connected tasks, subtasks and the parent epic, and opens every external link, knowledge-base page and design the material references |
| **Baseline** | When `specifications/projects/<project-name>/task-baseline.md` exists it is continuity context, not a constraint on new scope |
| **Gap resolution** | Ambiguities and missing information are listed and asked about with `AskUserQuestion`, batching up to 4 independent questions per call and never two about the same item. It does not proceed until they are answered or the user says to continue |
| **Attribution** | Every finding is attributed to its source, so a reader can tell evidence from inference. A document it could not read is reported as a blocker, never guessed at |
| **Execution context** | In the main conversation it asks and writes the report itself. As the `discovery-analyst` subagent it has no interactive and no write tool and returns the analysis with its questions under `## Open Questions` |

## How it works

1. Determine the input source, which decides how much of the next two steps is needed.
2. Find the available sources: which task and knowledge tools the session has (Jira and Confluence through Atlassian, plus whatever else is connected) and whether a project baseline exists.
3. Gather from every source, exhausting the supplied materials before asking the user anything.
4. Identify the gaps and resolve them with the user.
5. Write the report, following the skill's `research-report-example.md` exactly and keeping every section. One section is added: Term Candidates, which lists the terms and source-language forms found in the material and feeds [`/tsh-product-management:domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary) next. The report records all findings, all sources, and every question with the answer it received.

## What it produces

A research report with these sections: Task Details, Business Impact, Gathered Information (knowledge base and task tools, codebase, relevant links, relevant charts and diagrams), Current Implementation Status (existing components, key files and directories), Gap Analysis (each question with its answer) and Term Candidates.

## Related skills

- [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts) runs first when the input includes a raw transcript.
- [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) consumes this context to draft the intent brief.

## Source

[`plugins/tsh-product-management/skills/analyzing-discovery-context/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/analyzing-discovery-context/SKILL.md)
