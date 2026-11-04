---
title: Extracting Epics and Stories
sidebar_label: extracting-epics-and-stories
sidebar_position: 7
description: Turns processed workshop materials into a business-oriented backlog, starting with an approved intent brief, then epics with a delivery contract and stories with source traceability.
sources:
  - plugins/tsh-product-management/skills/extracting-epics-and-stories/
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
sources_hash: "132082beb6f07c30722f36621a40454f5516425fd211f86e7b92932886cc10ae"
---

# Extracting Epics and Stories

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:extracting-epics-and-stories`. Claude also loads it when a request matches its description.  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) (steps 4 and 5) and the [`backlog-extractor`](/docs/plugins/tsh-product-management/agents/backlog-extractor) agent, which preloads it.

Identifies discrete pieces of work from discovery material and structures them for stakeholder review and eventual Jira creation. The output is a backlog, not a technical specification: no architecture or implementation detail, no QA-perspective test design, no story point estimates, no sprint or release planning.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Intent brief first** | An approved `intent-brief.md` outranks the raw materials. The brief must be approved at Gate 0 before a single story is extracted, and extraction does not quietly go beyond it |
| **Epics as vertical slices** | Each epic is a cohesive business capability one developer can complete holistically and demonstrate to the client. Granularity is set by demonstrable customer outcome, not by a target count |
| **Epic Delivery Contract** | Every epic carries Customer Outcome, End-to-End Boundary, Explicit Exclusions, Demonstrable Scenario or Criteria, Known Dependency or Required Shared Contract, and a Collaboration/Concurrency Classification. Downstream delivery-readiness review and roadmap planning both read these fields |
| **Classification** | Exactly one of `Independent parallel work`, `Blocked work` or `Shared contract explicitly resolved`. It records evidence about the epic; waves and tracks are roadmap planning's decision |
| **Stories** | Each story has a short action-oriented title, "As a [role], I want [capability] so that [benefit]", a `Source` field pointing back to the material, acceptance criteria primarily as `GIVEN / WHEN / THEN` scenarios, technical notes only where the workshop raised them, and a priority suggestion (Critical, High, Medium, Low) |
| **Business language** | No implementation jargon, and stories are never treated as the primary delivery unit: they are detail beneath a contracted epic |
| **Terminology** | If `domain-dictionary.md` exists for the project it is consumed as canonical terms. The skill never mints a canonical term: an unknown term goes to the dictionary's unresolved-terms inbox |
| **Execution context** | In the main conversation it asks, runs the gates and writes the files. As the `backlog-extractor` subagent it has no interactive and no write tool, stays inside its assigned epic boundary and returns the content with questions under `## Open Questions` |

## How it works

1. Review every input: the Explore Mode summary if it ran, the cleaned transcript, Figma and FigJam flows, PDFs, other documents, the project baseline and the domain dictionary if one exists.
2. Draft the intent brief: goal, in scope, out of scope, key stakeholders and actors, likely epic candidates, baseline overlap and open questions. Scope decisions only.
3. Run Gate 0 and iterate until the user approves.
4. Identify epics as end-to-end vertical slices and record each Epic Delivery Contract, plus a business-oriented title, a 2 to 3 sentence value description and high-level success criteria.
5. Break each contracted epic into stories, one deliverable piece of user-facing functionality each, small enough for a single sprint as a guideline.
6. Write each story with the fields above.
7. Map dependencies in plain notation ("Story 1.2 is blocked by Story 1.1").
8. Record assumptions, labelling every interpretation made where intent was unclear, and what was explicitly excluded.
9. Run Gate 1 file-first: write the draft `extracted-tasks.md`, present a compact summary in chat with any story the skill is less than confident about flagged, and ask one `AskUserQuestion` (`Approve as-is`, `I'll edit the file`, `Walk me through the flagged stories` or `Rework — I'll explain`). Flagged stories are walked through in batches of up to 4 per call. A 15-story breakdown is never one popup per story.
10. Save `intent-brief.md` and `extracted-tasks.md` in `specifications/<workshop-name>/`. The orchestrator records the Gate 1 approval in `.gates.md`.

## What it produces

`intent-brief.md`, with sections Workshop Summary, Goal, In Scope, Out of Scope, Key Stakeholders / Actors, Candidate Epics, Baseline Overlap / Existing Backlog Notes, Open Questions and Gate 0 Approval.

`extracted-tasks.md`, with sections Workshop Summary, Epics Overview, one section per epic (its Epic Delivery Contract, business description, success criteria and stories), Dependencies, Assumptions, Out of Scope and Open Questions for Stakeholders.

## Related skills

- [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts) supplies the cleaned transcript.
- [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context) supplies business context and baseline comparison before extraction.
- [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) reviews what this skill produces and checks the Epic Delivery Contract in Pass R.

## Source

[`plugins/tsh-product-management/skills/extracting-epics-and-stories/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/extracting-epics-and-stories/SKILL.md)
