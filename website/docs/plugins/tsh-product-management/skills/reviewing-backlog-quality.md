---
title: Reviewing Backlog Quality
sidebar_label: reviewing-backlog-quality
sidebar_position: 8
description: Reviews an approved epic and story list for gaps, missing edge cases and delivery-readiness problems, and produces individually accept-or-reject suggestions.
sources:
  - plugins/tsh-product-management/skills/reviewing-backlog-quality/
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
sources_hash: "8f0f686f51dc6303500d848a2fe559f842fa5b1f3c7be7bcf3da715e2091f232"
---

# Reviewing Backlog Quality

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:reviewing-backlog-quality`. Claude also loads it when a request matches its description.  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) (step 6, run automatically after Gate 1) and the [`backlog-quality-reviewer`](/docs/plugins/tsh-product-management/agents/backlog-quality-reviewer) agent, which preloads it.

Runs a structured gap analysis over a Gate 1-approved task list and turns each finding into a suggestion the user accepts or rejects individually. The audit trail is `quality-review.md`; accepted suggestions are applied to `extracted-tasks.md`. It also applies to an imported Jira backlog. It makes no technical architecture decisions, no effort estimates or priority changes, adds no scope the source materials or a universal pattern do not imply, and does no Jira writes: Jira access is read-only, for enrichment only.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Review modes** | Lite is the default for small, low-risk workshops (roughly up to 3 epics and 12 stories) and runs passes A, B, E, H, I, K, then R. Full is for larger workshops, regulated domains, high-risk scope or on request, and runs A to J, K, then R |
| **Analysis passes** | A entity lifecycle, B cross-feature state validation, C bulk operation idempotency, D actor dashboard completeness, E precondition guards, F third-party boundary clarity, G platform operations perspective, H error state and edge case coverage, I notification and communication gaps, J domain-specific research, K terminology consistency, R pre-roadmap delivery-readiness |
| **Pass K** | Checks the task list against the project's domain dictionary. It runs in both modes only when a dictionary exists; otherwise the skip is recorded in the review output |
| **Pass R** | Mandatory on every non-protected epic in both modes. It checks the Epic Delivery Contract content from extraction and does not validate waves, tracks or allocation, which belong to roadmap planning |
| **Pass J** | Uses `WebSearch` and `WebFetch` for domain research. Its findings are Medium or Low confidence, never High, and cite what was found. If neither tool is available the pass is skipped and the skip is stated |
| **Suggestions** | Each has a confidence level (High, Medium or Low), an action type (`ADD_ACCEPTANCE_CRITERION`, `MODIFY_STORY`, `ADD_TECHNICAL_NOTE`, `NEW_STORY`, `NEW_EPIC` or `MODIFY_EPIC`) and the exact proposed text in the format `extracted-tasks.md` already uses. Overlapping findings merge into one suggestion naming all contributing passes |
| **Protected tasks** | Tasks with status Done, Cancelled or PO APPROVE are filtered out before the passes run. Any suggestion that targets one is dropped, and the target's status is re-checked immediately before an accepted suggestion is applied |
| **Execution context** | In the main conversation it asks and applies accepted changes itself. As the `backlog-quality-reviewer` subagent it has no interactive tool, no write tool and no Atlassian access, runs only its assigned passes and returns the suggestions as its final message |

## How it works

1. Load the inputs and select the mode. `extracted-tasks.md` is mandatory. The chosen mode is recorded before anything runs.
2. Gather Jira board context, optionally: only when Atlassian tools are available and the user has named a project. The review works identically without it.
3. Build the domain model from the task list alone: actors, entities and the relationships between them. It is a business map, not a technical data model.
4. Run the active passes, after the protected-status filter.
5. Enrich with domain research where `WebSearch` and `WebFetch` are available, folding the results into Pass J.
6. Classify each finding into a suggestion. Where Jira context exists, duplicates are noted ("already tracked as PROJ-123, consider linking").
7. Run Gate 1.5 file-first: write all suggestions to `quality-review.md` as checkbox items with stable IDs, ordered by epic, then confidence, with new-epic proposals last. Ask one `AskUserQuestion` (`Accept all High`, `I'll tick the file`, `Walk me through them` or `Skip review`). When asked to walk through, suggestions go in batches of 4 per call. Free-text dispositions are honoured without re-asking per item, and every decision, including a rejection, is recorded in the file.
8. Apply accepted suggestions to `extracted-tasks.md`, re-checking protected status first, and update the Workshop Summary counts.
9. Save the report to `specifications/<workshop-name>/quality-review.md`: the domain model, every suggestion generated, each disposition and a summary of what was applied.

The skill never modifies the task list without an explicit accept from the user.

## Related skills

- [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) supplies the task list and defines the Epic Delivery Contract that Pass R checks.
- [`planning-delivery-roadmaps`](/docs/plugins/tsh-product-management/skills/planning-delivery-roadmaps) consumes the accepted findings and owns every wave, track and allocation decision.
- [`domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary) is offered the domain model built here as a starting point when no dictionary exists.

## Source

[`plugins/tsh-product-management/skills/reviewing-backlog-quality/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/reviewing-backlog-quality/SKILL.md)
