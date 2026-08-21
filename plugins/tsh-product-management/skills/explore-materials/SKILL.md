---
name: explore-materials
description: "Entry point for Explore Mode: reads discovery workshop materials and produces a business-context summary with likely epic candidates and open questions, without creating any backlog items. Run /tsh-product-management:explore-materials with a transcript path, Figma link, PDF path, or folder of workshop assets."
disable-model-invocation: true
---

# Explore materials

Materials: **$ARGUMENTS**

If nothing was supplied, ask which materials to explore before doing anything else.

Use this when the user wants to understand the material first, or when it is too
ambiguous to commit to epics and stories yet.

## What this runs

Follow [`orchestrating-business-analysis`](../orchestrating-business-analysis/SKILL.md)
in **Explore Mode**, which stops at a context summary. The reading itself is
[`analyzing-discovery-context`](../analyzing-discovery-context/SKILL.md), plus
[`processing-workshop-transcripts`](../processing-workshop-transcripts/SKILL.md) when
raw discussion notes are present.

Exploration may be delegated to the `discovery-analyst` worker, but the results
always come back through this conversation before anything moves toward
extraction.

## Steps

1. Review the supplied materials and any existing project baseline. PDFs are read
   with `Read`; Figma and FigJam links through the Figma MCP tools the session
   provides.
2. Clean the transcript first when raw discussion notes are present.
3. Summarize the workshop context in business language.
4. Identify the main actors, business entities, and likely epic candidates.
5. Note overlap with an existing backlog or baseline.
6. Capture ambiguities, risks and open questions that should be resolved before
   extraction.
7. Recommend whether the material is ready for an intent brief and extraction.

## Output

Write `specifications/<workshop-name>/workshop-context-summary.md` with at least:

- Workshop/topic context
- Actors and business entities
- Existing backlog or baseline overlap
- Likely epic candidates
- Key ambiguities, risks and open questions
- Recommendation on readiness for the intent brief and extraction

Keep it business-facing.

## Boundary

**Do not create epics, stories or Jira-ready backlog items in this mode** unless the
user explicitly asks to continue after reading the summary.

If they do want to continue, hand off explicitly — say so rather than sliding into
extraction:

```text
/tsh-product-management:analyze-materials <same materials>
```
