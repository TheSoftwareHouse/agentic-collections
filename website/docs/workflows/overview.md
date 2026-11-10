---
title: Workflows overview
sidebar_label: Overview
sidebar_position: 1
description: The five end-to-end workflows the plugins ship — feature implementation, UI verification, debugging, business analysis and project context — who runs each step, where people decide, and which plugins each one needs.
sources:
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/
  - plugins/tsh-product-engineering/skills/creating-implementation-plans/SKILL.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md
  - plugins/tsh-product-engineering/skills/debugging-code/SKILL.md
  - plugins/tsh-product-engineering/agents/feature-verifier.md
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/SKILL.md
  - plugins/tsh-product-management/skills/initializing-project-context/SKILL.md
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/skills/navigating-project-context/SKILL.md
  - plugins/tsh-core/skills/init/SKILL.md
  - plugins/tsh-core/skills/managing-claude-context/SKILL.md
sources_hash: "6d0b2fd749ca74915167090f4d40a212701ced64482f152891c3ee62bc8d6f87"
---

# Workflows overview

<!-- PHASE2(narrative): a Workflows section with one overview page and one page per flow — the section shape follows the old site's workflow pages — decide in Phase 2 whether workflows stay a separate section or fold into the plugin pages that own them -->

A workflow here is a chain of skills and agents that takes one kind of work from request to result. Each page below says which step runs in the main conversation and which in a subagent, where a person has to decide, and which files the workflow leaves behind.

## The five workflows

| Workflow | Starts with | Plugins it needs |
| :-- | :-- | :-- |
| [Feature implementation](./feature-implementation) | [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation), which writes a plan first through [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) | `tsh-product-engineering`; `tsh-core` for the Figma MCP server when a task is backed by a design; the Playwright CLI on the machine when a task is UI work or the verification document has browser scenarios |
| [UI verification](./ui-verification) | [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) for one pass, or the UI verification gate inside feature implementation | `tsh-product-engineering` and `tsh-core` (Figma MCP), plus the Playwright CLI on the machine |
| [Debugging](./debugging) | [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) | `tsh-product-engineering` |
| [Business analysis](./business-analysis) | [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) or [`explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials), both running [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) | `tsh-product-management`; `tsh-core` for the Atlassian MCP server (Jira) and the Figma MCP server (designs) |
| [Project context](./project-context) | [`/tsh-core:init`](/docs/plugins/tsh-core/skills/init) for a repository's own Claude Code context; [`initializing-project-context`](/docs/plugins/tsh-product-management/skills/initializing-project-context) for a project's shared knowledge base | `tsh-core` for the repository side; `tsh-product-management` for the knowledge-base side |

How to install each plugin, and at which scope, is on the [installation page](/docs/getting-started/installation).

## What the workflows have in common

- **The main conversation orchestrates.** In feature implementation and business analysis it owns the plan or the gate ledger, the delegation and every question to the user. Subagents do the reading and the implementation work, and start with no conversation history, so every delegation carries the file paths they need.
- **State lives in files, not in the conversation.** Feature implementation works from a plan file at `specifications/<task-id>/<task-name>.plan.md`. Business analysis records each gate approval in `specifications/<workshop-name>/.gates.md` before the action it unlocks.
- **People decide at named points.** A plan is executed only after the user has read it. Nothing reaches Jira before Gate 2 is recorded. A project-context skill creates a branch, commits or pushes only after its own yes for that step.
- **Workflows hand over to each other.** A bug whose fix outgrows a minimal change leaves [debugging](./debugging) for a plan. Every Figma-backed UI task in [feature implementation](./feature-implementation) closes through [UI verification](./ui-verification). The domain dictionary that [business analysis](./business-analysis) produces is wired into a repository by `managing-claude-context`, part of [project context](./project-context).
- **Missing plugins are named, not worked around.** A skill that needs another plugin's work — E2E suites, infrastructure, implementation — names the gap to the user instead of improvising it.
