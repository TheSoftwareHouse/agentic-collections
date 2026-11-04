---
title: Orchestrating Business Analysis
sidebar_label: orchestrating-business-analysis
sidebar_position: 4
description: Runs the business-analysis workflow end to end from the main conversation, from workshop material to Jira-ready epics and stories and a delivery roadmap, behind five human review gates.
sources:
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/
  - plugins/tsh-product-management/skills/analyze-materials/SKILL.md
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
sources_hash: "f8f83ff2b729178b088a288091ea0c65fe72076bd1ed72f5a13ae9c65471cdc2"
---

# Orchestrating Business Analysis

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:orchestrating-business-analysis`. Claude also loads it when a request matches its description. The entry-point commands [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) and [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) both invoke it.  
**Used by:** [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials), [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) (Explore Mode)

Runs the business-analysis workflow from the main conversation. The main conversation is the orchestrator: it owns the materials, the gates, the files and the Jira mutations, while the reading and drafting run in read-only worker subagents so their document parsing stays out of its context. Output is business-oriented throughout: epics and stories a stakeholder understands without technical knowledge, with technical notes only where the workshop raised them.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Entry points** | Workshop materials start at transcript processing. Jira issue keys or a project key skip to Import Mode in [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) and join at the quality review. Explore Mode produces `workshop-context-summary.md` and stops, with no epics or stories unless the user asks to continue |
| **Review gates** | Five gates: 0 (intent brief), 1 (extraction), 1.5 (quality review), 1.75 (roadmap proposal), 2 (Jira push). Every approval is written to the ledger before the action it unlocks |
| **Gate ledger** | `specifications/<workshop-name>/.gates.md` is the source of truth, not the conversation. The Gate 2 row names the target project key, which the Jira-write hook matches against |
| **Protected Status Policy** | Tasks with status Done, Cancelled or PO APPROVE are immutable everywhere in the workflow. The policy block is pasted verbatim into any delegation prompt that touches existing tasks |
| **Delegation** | Read-only workers do the reading and drafting; the orchestrator keeps every question, persistent write and Jira mutation. Parallel `Agent` calls go out in one message, after the user confirms the suggestion to parallelize. At most 5 workers run at once |
| **Roadmap** | Planned by a single `roadmap-planner` by default and never fanned out, because reconciliation needs the whole epic set in one context. The proposal is written to `.roadmap-proposal.md`, then to the project roadmap only after Roadmap Review approval |
| **Jira access** | Through whichever Atlassian MCP server the session exposes, with tool names discovered before the first push instead of assumed. Reads are never gated; the push follows a fixed safe sequence |
| **Exclusions** | No technical specifications or architecture decisions, no implementation, test or deployment plans, no story point estimates. Where the work needs one of those, the gap is named to the user |

## Non-negotiable rules

- Record every gate approval in `.gates.md` before taking the action it unlocks.
- Keep the Jira gate's ledger row numbered `2`. The `PreToolUse` hook matches it by number, which is why Roadmap Review is `1.75`.
- Never push to Jira before Gate 2 is recorded. If a write is blocked, verify the ledger instead of working around the hook.
- Keep every user-facing question, persistent write and Jira mutation in the main conversation. Workers write nothing and speak to nobody.
- Never fan out roadmap planning.
- Never guess where you could ask: exhaust the materials first, then ask.

## How it works

1. Create the gate ledger at `specifications/<workshop-name>/.gates.md`.
2. Process the transcript with [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts) when raw discussion material is supplied.
3. Analyze the remaining materials and the project baseline with [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context). This is the phase that most often justifies parallel workers. If `domain-dictionary.md` exists for the project it is consumed as canonical terms; otherwise the skill suggests [`/tsh-product-management:domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary).
4. Draft the intent brief with [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories), then run and record Gate 0.
5. Extract epics and stories, then run and record Gate 1.
6. Run the quality review with [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) automatically after Gate 1. Present the suggestions file-first at Gate 1.5, apply what the user accepts, and record it.
7. Summarize what changed in `extracted-tasks.md` and proceed only on confirmation.
8. Send the confirmed tasks, accepted findings, baseline and any existing roadmap to a single [`roadmap-planner`](/docs/plugins/tsh-product-management/agents/roadmap-planner), which applies [`planning-delivery-roadmaps`](/docs/plugins/tsh-product-management/skills/planning-delivery-roadmaps) and returns an in-memory proposal. Write it to `.roadmap-proposal.md`. The orchestrator may instead apply `planning-delivery-roadmaps` inline, and says that it did and why.
9. Run Roadmap Review from the file and record the approval in the `1.75` row. Only then create or update `specifications/projects/<project-name>/roadmap.md`.
10. Format for Jira with [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) and save `jira-tasks.md`.
11. Run Gate 2: confirm the target project and push scope, and record the approval before any write call.
12. Push, read the issues back to verify, archive the session artifacts and refresh the project baseline.

The skill ends with exactly one suggested next step and the command to run, without running it. If the session ended before Gate 2, it names the gate it stopped at, the file that holds the current state, and how to resume.

## Session artifacts

In `specifications/<workshop-name>/`: `.gates.md`, `cleaned-transcript.md`, `workshop-context-summary.md` (Explore Mode only), `intent-brief.md`, `extracted-tasks.md`, `quality-review.md`, `.roadmap-proposal.md` (draft) and `jira-tasks.md`.

Outliving the session, in `specifications/projects/<project-name>/`: `roadmap.md`, `task-baseline.md` and `domain-dictionary.md`. The dictionary keeps its own gate ledger, `.dictionary-gates.md`, at that same project scope.

## References

| Reference | Load when |
| :-- | :-- |
| `review-gates-and-ledger.md` | Before the first gate and before recording any approval: the five gates, the ledger format, the hook interlock, how to ask well |
| `protected-status-policy.md` | Whenever existing tasks are in play and before every delegation that touches them |
| `delegating-to-workers.md` | Before spawning any worker: routing, when to parallelize, the prompt contract, merge rules |
| `working-with-jira.md` | Any Jira read, push or iteration-mode session |
| `reading-workshop-materials.md` | Processing PDFs, designs or mixed material bundles |

## Related skills

[`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts), [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context), [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories), [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality), [`planning-delivery-roadmaps`](/docs/plugins/tsh-product-management/skills/planning-delivery-roadmaps), [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) and [`domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary). The Jira-write hook that enforces Gate 2 is described on the [plugin page](/docs/plugins/tsh-product-management/).

## Source

[`plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md)
