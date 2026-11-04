---
title: Jira Formatter
sidebar_label: jira-formatter
sidebar_position: 6
description: Read-only worker agent that applies the Jira benchmark template, produces the completeness table and prepares verification diffs, with no Jira calls and no file writes.
sources:
  - plugins/tsh-product-management/agents/jira-formatter.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/delegating-to-workers.md
sources_hash: "6bee42dbb4acc019212fa168c84d7db614364ecf046e56e547df76590b7f4473"
---

# Jira Formatter

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:jira-formatter`  
**Model:** `haiku`  
**Tools:** `Read, Grep, Glob`  
**Preloaded skill:** [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues)

Produces clean, template-conformant Jira content and the tables that let the orchestrator decide what to push. It keeps bulk formatting work out of the main conversation. The mutation itself is never its job: it performs no Jira calls and writes no files.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation must name the extracted tasks or Jira-ready draft to format and the benchmark template to apply. For a verification diff it must also supply the read-back payload from Jira, since the agent cannot fetch it. If a required input is missing it stops and says which one |
| **Procedure** | Follows the preloaded `formatting-jira-issues` skill: applies the benchmark template to each epic and story, maps priorities, proposes labels, validates completeness against the template and flags every field it could not fill with confidence |
| **Orchestrator-only steps** | Steps 8 to 11 of the skill (push approval, Jira mutation, verification against live Jira, archiving and baseline refresh) are not attempted |
| **Protected tasks** | Preserved verbatim per the Protected Status Policy supplied in its prompt: marked `🔒` in the task's `###` heading, not formatted, and listed |
| **Jira markdown** | Jira conventions (`h2.`, `*bold*`, `_italic_`, `* item`, `(/) criterion`) apply only to content destined for Jira itself. The local markdown file stays standard markdown |
| **Boundaries** | No write tools, no interactive tool, no Atlassian tools and no create or update side effects. Uncertain fields go in its output for the orchestrator to ask about |

## What it returns

Its final message is the return value, with no preamble:

- Formatted Tasks, in benchmark shape including `Jira Key` (`—` when not yet pushed)
- Completeness Table: task, required fields populated yes or no, notes
- Uncertain Fields: task, field, why it could not be filled
- Protected Tasks Skipped: title, key, status, or "none"
- Verification Diff, only with a read-back payload: per task, field by field, expected versus actual, with mismatches called out
- Baseline Refresh Content, only when asked: merged entries keyed by Jira Key

## Used by

[`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) delegates Jira-ready formatting, verification diffs and baseline content to it, through its `delegating-to-workers.md` reference.

## Source

[`plugins/tsh-product-management/agents/jira-formatter.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/jira-formatter.md)
