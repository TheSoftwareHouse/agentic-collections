---
title: Formatting Jira Issues
sidebar_label: formatting-jira-issues
sidebar_position: 10
description: Formats an approved epic and story list into Jira-ready issues against a benchmark template, manages the Gate 2 push, and imports an existing Jira backlog into the same local format.
sources:
  - plugins/tsh-product-management/skills/formatting-jira-issues/
  - plugins/tsh-product-management/skills/analyze-materials/SKILL.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
sources_hash: "776e00926eca9147b7ed0ba53fa55bd95f7699a770bf064cf84caef659de63b0"
---

# Formatting Jira Issues

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:formatting-jira-issues`. Claude also loads it when a request matches its description. It can be started directly, without the orchestrator.  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) (step 10 and Import Mode), [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) (Jira keys or a project key start in Import Mode) and the [`jira-formatter`](/docs/plugins/tsh-product-management/agents/jira-formatter) agent, which preloads it.

Applies one consistent template to every task, preserves source traceability, validates completeness, and manages the review gate between a local markdown file and real Jira issues. It does not extract or invent scope, estimate, or decide roadmap waves, and no roadmap content reaches Jira. The project's own Jira conventions (naming, labels, priority scheme, issue types) outrank its defaults.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Benchmark template** | Epic and story field sets, description formats in Jira markdown, and acceptance criteria as `(/)` checklist items. Epic summaries follow `<Domain Area>: <Business Capability>` and story summaries follow `<User/Actor> can <action>` |
| **Priority mapping** | Critical to Highest, High to High, Medium to Medium, Low to Low |
| **Sizing** | A Small, Medium or Large suggestion marked as guidance for refinement, not an estimate |
| **Jira Key and Status** | Every epic and story carries a `Jira Key`, the real key or `—` when never pushed. A task that already has a key is updated, never recreated. Each returned key is written back into `jira-tasks.md` immediately after the issue is created |
| **Protected tasks** | Done, Cancelled and PO APPROVE tasks are preserved exactly as imported, marked `🔒` in their `###` heading, and skipped by every formatting, validation and update step. The Jira write guard parses that heading marker |
| **Gate 2** | Approval is recorded in `.gates.md` before the first Jira write call, naming the target project key. A `PreToolUse` hook enforces it |
| **Sync summary** | Created, updated and skipped tasks, with counts, are presented and approved before pushing |
| **Import Mode** | Fetches a project key, specific epic keys or a JQL query with the Atlassian read tools and writes `jira-tasks.md` with keys populated. Import is read-only and Gate 2 does not apply until local changes are pushed back |
| **Canonical terms** | Issue titles and descriptions use the project's canonical terms when a domain dictionary exists. The `UI label` column never replaces the identifier in a title |
| **Execution context** | Jira mutation and file writing belong to the orchestrator. As the `jira-formatter` subagent the skill has no write or Atlassian tools and returns formatted content, the completeness table, the sync summary or the verification diff |

## How it works

1. Load the benchmark template, `extracted-tasks.md` and the domain dictionary if one exists.
2. Format each epic: summary, description (business overview, business value, success criteria), acceptance criteria, labels drawn from the epic's domain and the mapped priority.
3. Format each story: summary, a description with context, Source Context, the user story statement, numbered requirements and technical notes only where the extraction carried them, plus acceptance criteria, sizing guidance, labels, parent epic and priority.
4. Validate completeness against the template and produce a completeness table.
5. Flag uncertain fields and ask, batching up to 4 independent field questions per `AskUserQuestion` call, each about a different task.
6. Run the formatting review from the file with one question (`Approve as-is`, `I'll edit the file`, `Walk me through the changes` or `Rework — I'll explain`).
7. Save `specifications/<workshop-name>/jira-tasks.md`.
8. Push, verify and refresh, following the `pushing-to-jira.md` reference: Gate 2, the sync summary, creation and update order, post-push verification, and archive and baseline refresh.

Content destined for Jira uses Jira markdown (`h2.`, `*bold*`, `_italic_`, `* item`, `{noformat}`). The local markdown file stays standard markdown.

## Pushing to Jira

The reference covers steps 8 to 11, all orchestrator-only:

- **Step 8, push approval:** the target project key, board or backlog, and whether to create everything at once or in batches, each asked as its own question.
- **Step 9, create or update:** epics first, then stories linked to them, then links between stories. Updates check status first and do not change issue type or parent link unless asked.
- **Step 10, verification:** issues are read back and checked per task for summary, parent linkage, acceptance criteria, description sections and status.
- **Step 11, archive and baseline:** session artifacts are archived under `specifications/projects/<project-name>/sessions/<YYYY-MM-DD>-<workshop-name>/`, which also closes the gate, and `task-baseline.md` is refreshed with `Jira Key` as the primary identity.

A single change outside the main workflow is refused for a protected task. Otherwise it updates `jira-tasks.md` first and asks once whether to push it now. That push still needs an approved Gate 2 row naming the task's project key.

## Related skills

- [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) supplies the task list this skill formats.
- [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) runs before formatting and applies equally to an imported backlog.

## Source

[`plugins/tsh-product-management/skills/formatting-jira-issues/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/formatting-jira-issues/SKILL.md)
