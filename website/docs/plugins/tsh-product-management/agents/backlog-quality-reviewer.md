---
title: Backlog Quality Reviewer
sidebar_label: backlog-quality-reviewer
sidebar_position: 4
description: Read-only worker agent that runs assigned Lite or Full quality-review passes over an approved epic and story list and returns structured, confidence-scored suggestions.
sources:
  - plugins/tsh-product-management/agents/backlog-quality-reviewer.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
sources_hash: "46ecfbaa9192801b80745eeef71035963501f1a01767265df93945f617740402"
---

# Backlog Quality Reviewer

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:backlog-quality-reviewer`  
**Model:** `opus`  
**Tools:** `Read, Grep, Glob, WebSearch, WebFetch`  
**Preloaded skill:** [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality)

Finds the gaps a workshop left in a backlog, such as missing lifecycle operations, unguarded preconditions, absent error states, unnotified actors and epics that cannot be demonstrated, and proposes exact corrections. It is used to split a review across several agents, one batch of passes each, before the Gate 1.5 disposition.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation must name the task list (or its path) and the specific passes assigned. It runs only those. If the assignment is missing, it stops and reports it instead of running the full set on its own initiative |
| **Atlassian access** | None. Any Jira or board context arrives inline in the delegation prompt |
| **Procedure** | Follows the preloaded `reviewing-backlog-quality` skill: applies the protected-status filter, builds only as much of the domain model as its passes require, runs each assigned pass and turns every finding into a structured suggestion with a confidence level, an action type and the exact proposed text |
| **Pass J** | Findings are Medium or Low confidence, never High, and cite what was found. If `WebSearch` and `WebFetch` are unavailable it says Pass J was skipped instead of speculating |
| **Protected tasks** | Done, Cancelled and PO APPROVE tasks, per the Protected Status Policy supplied in its prompt, are excluded from analysis and never the target of a suggestion. A suggestion generated against one is dropped before returning |
| **Boundaries** | No write tools, so it never modifies the task list, and no interactive tool. It adds no scope the source materials or a universal pattern do not imply and does not estimate effort or change priorities |

## What it returns

Its final message is the return value, with no preamble:

- Review Mode and Passes Run
- Domain Model, only if asked
- Suggestions
- Protected Tasks Excluded, or "none"
- Notes for the Orchestrator

Each suggestion has an ID (`QR-nn`), a confidence (`High`, `Medium` or `Low`), an action type (`ADD_ACCEPTANCE_CRITERION`, `MODIFY_STORY`, `ADD_TECHNICAL_NOTE`, `NEW_STORY`, `NEW_EPIC` or `MODIFY_EPIC`), its target epic and story, the finding, the exact proposed text and the contributing pass letters.

## Used by

[`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) delegates Lite and Full review passes to it, through its `delegating-to-workers.md` reference. The active passes are split into roughly equal batches across agents, and the orchestrator merges the results and assigns consistent IDs before Gate 1.5.

## Source

[`plugins/tsh-product-management/agents/backlog-quality-reviewer.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/backlog-quality-reviewer.md)
