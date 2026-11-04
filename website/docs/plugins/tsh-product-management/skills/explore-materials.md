---
title: Explore Materials
sidebar_label: explore-materials
sidebar_position: 2
description: Entry-point command for Explore Mode, which reads workshop materials and writes a business-context summary without creating any backlog items.
sources:
  - plugins/tsh-product-management/skills/explore-materials/
  - plugins/tsh-product-management/skills/analyze-materials/SKILL.md
  - plugins/tsh-product-management/agents/discovery-analyst.md
sources_hash: "869d75f986b50d754f600e59211477e54a9e7a203e6581b110f7d7d0e405d077"
---

# Explore Materials

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:explore-materials <materials>`. It runs only when you invoke it (`disable-model-invocation: true`).  
**Used by:** [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) offers it first when the supplied materials are too ambiguous to commit to a backlog.

Use it when you want to understand the material first, or when it is too ambiguous to commit to epics and stories. It invokes [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) in Explore Mode, which stops at a context summary. If you supply nothing, it asks which materials to explore before doing anything else.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Accepted input** | A transcript path, a Figma link, a PDF path, or a folder of workshop assets |
| **Reading** | The reading itself is [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context), plus [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts) when raw discussion notes are present |
| **Delegation** | Exploration may be delegated to the [`discovery-analyst`](/docs/plugins/tsh-product-management/agents/discovery-analyst) worker, but results always come back through the main conversation before anything moves toward extraction. That worker has no design-tool access, so the design context is fetched in the main conversation and passed into its prompt |
| **Design links** | Figma and FigJam links are read through whatever Figma MCP tools the session provides. The command checks that they are connected before promising design analysis and says so plainly when they are not |
| **Boundary** | It does not create epics, stories or Jira-ready backlog items unless the user explicitly asks to continue after reading the summary |

## How it works

1. Review the supplied materials and any existing project baseline. PDFs are read with `Read`.
2. Clean the transcript first when raw discussion notes are present.
3. Summarize the workshop context in business language.
4. Identify the main actors, business entities and likely epic candidates.
5. Note overlap with an existing backlog or baseline.
6. Capture ambiguities, risks and open questions that should be resolved before extraction.
7. Recommend whether the material is ready for an intent brief and extraction.

## What it returns

`specifications/<workshop-name>/workshop-context-summary.md`, kept business-facing, with at least:

- workshop or topic context
- actors and business entities
- existing backlog or baseline overlap
- likely epic candidates
- key ambiguities, risks and open questions
- a recommendation on readiness for the intent brief and extraction

To continue, the handoff is explicit rather than a slide into extraction: run `/tsh-product-management:analyze-materials` with the same materials.

## Related skills

- [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) runs Explore Mode.
- [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) is the full-workflow entry point to continue with.

## Source

[`plugins/tsh-product-management/skills/explore-materials/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/explore-materials/SKILL.md)
