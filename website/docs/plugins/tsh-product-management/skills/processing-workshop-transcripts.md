---
title: Processing Workshop Transcripts
sidebar_label: processing-workshop-transcripts
sidebar_position: 5
description: Cleans a raw workshop or meeting transcript into a structured business document with decisions, action items and open questions.
sources:
  - plugins/tsh-product-management/skills/processing-workshop-transcripts/
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
sources_hash: "775b1c6b5179ea826ee2044c0174bfbac99573e8376d036b7abe969f91c98145"
---

# Processing Workshop Transcripts

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:processing-workshop-transcripts`. Claude also loads it when a request matches its description.  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) (step 2, when raw discussion material is supplied), [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) and the [`transcript-cleaner`](/docs/plugins/tsh-product-management/agents/transcript-cleaner) agent, which preloads it.

Turns noisy discussion material into a document that later phases can rely on. It removes greetings, filler and tangents while preserving every actionable and business-critical point. It does not extract epics or stories, judge scope, or resolve contradictions between sources: it produces one cleaned transcript and stops.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Content preservation** | Every decision, commitment, constraint and open question is kept, including ones stated in passing. When in doubt whether a passage is business-relevant, keep it |
| **Preserved Context** | The exact wording of requirements, constraints and conflicting viewpoints is kept with attribution |
| **No invention** | Metadata, roles or decisions the source does not state are recorded as "not stated in source". The contents of a scanned PDF with no text are never inferred: the skill reports it and asks for a text-based version |
| **Client terminology** | The client's own terms are never normalised or paraphrased. They are kept as said, including inflected surface forms, in the transcript's Terminology section |
| **Input formats** | Speaker-labelled, plain notes, timestamped, mixed, or PDF. PDFs are read with `Read`, with an explicit `pages` range beyond 10 pages and chunks of at most 20 |
| **Execution context** | In the main conversation it asks for missing metadata and writes the file itself. As the `transcript-cleaner` subagent it has no interactive and no write tool and returns the transcript as its final message |

## How it works

1. Identify the format and metadata: date, duration (computed from first and last timestamp), topic and context.
2. Tag participants with name and role where stated or unambiguous. A participant without a stated role is listed without one.
3. Remove non-business content: greetings, small talk, filler words, technical difficulties, tangents and repeated restatements, keeping the clearest version of each point.
4. Group by discussion topic, with a descriptive heading per topic, speaker attribution where available, chronological order within a topic, and a resurfacing topic consolidated under one heading.
5. Extract key decisions, both explicit and implicit, with who made or endorsed them and any conditions.
6. Extract action items (what, who, deadline) and open questions.
7. Preserve critical raw context as exact quotes where the original wording matters.
8. Write `specifications/<workshop-name>/cleaned-transcript.md` and check that nothing business-relevant was dropped and that the Terminology section captures every client term encountered.

## What it produces

`cleaned-transcript.md` with these sections, in order: Meeting Metadata, Participants, Executive Summary, Discussion Topics, Key Decisions, Action Items, Open Questions, Preserved Context and Terminology. The shape is fixed by the skill's `cleaned-transcript-example.md` reference, which the skill always loads before writing.

## Related skills

- [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) consumes the cleaned transcript as its primary input.
- [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context) synthesizes it with the other workshop materials.

## Source

[`plugins/tsh-product-management/skills/processing-workshop-transcripts/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/processing-workshop-transcripts/SKILL.md)
