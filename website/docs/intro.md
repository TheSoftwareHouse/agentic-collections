---
title: Introduction
sidebar_label: Introduction
sidebar_position: 1
slug: /
description: Agentic Collections is The Software House's Claude Code plugin marketplace — skills and agents for how we work, what we work with, and a small core that holds regardless of either.
sources:
  - README.md
  - CLAUDE.md
  - .claude-plugin/marketplace.json
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-platform-engineering/README.md
sources_hash: "2585ec9e5a872d27ddf2629a8024c07060b99bbe6a3b810451b1bc5bf497bb2c"
---

import { PluginList } from '@site/src/components/PluginComponents';

# Introduction

**Agentic Collections** is a [Claude Code](https://code.claude.com/docs) plugin marketplace from [The Software House](https://tsh.io). It carries custom agents and skills you can install into any project.

The plugins are not an application: there is no build step and no runtime. They are mostly Markdown and JSON that Claude Code loads, plus the few hook and helper scripts some skills run. Every skill and agent is namespaced by its plugin, so you invoke a skill as `/<plugin>:<skill>` and mention an agent as `@<plugin>:<agent>`.

## Three families

The marketplace publishes three families of plugins, and each one installs at a different scope.

| Family | What it carries | Install at |
| :-- | :-- | :-- |
| **Core** (`tsh-core`) | The ground under both: one small plugin of tool mechanics that depend on neither your role nor the repo | **User** scope. It follows you everywhere |
| **Disciplines** (`tsh-<discipline>`) | How we work: one plugin per discipline | **User** scope. Your job doesn't change from repo to repo |
| **Stacks** (`tsh-stack-<stack-name>`) | What we work with: one plugin per technology stack | **Project** scope. The repo already knows what it is written in |

The [Plugins](/docs/plugins/) page explains the scopes in more detail and links every plugin to its own page.

## Verticals

The discipline plugins and the context tooling cover five verticals. Each one links to the work it does today on the [Use cases](/docs/use-cases) page.

| Vertical | What it covers | Plugin |
| :-- | :-- | :-- |
| [Product Management](/docs/use-cases#product-management) | Discovery workshop material — transcripts, Figma, PDFs, codebase context — turned into Jira-ready epics and user stories, a per-product domain dictionary and an outcome-based delivery roadmap, behind five human review gates | [`tsh-product-management`](/docs/plugins/tsh-product-management/) |
| [Product Engineering](/docs/use-cases#product-engineering) | Committed plan files, delegated implementer subagents, a Figma-backed UI verification gate driven by Playwright CLI capture, root-cause bug fixing guarded by a regression test, and structured pre-merge code review | [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/) |
| [Product Testing](/docs/use-cases#product-testing) | Playwright end-to-end tests proven stable by repeated headless runs, and WCAG 2.1 AA accessibility audits that report the success criterion behind every finding | [`tsh-product-testing`](/docs/plugins/tsh-product-testing/) |
| [Platform Engineering](/docs/use-cases#platform-engineering) | Terraform modules, pipelines with OIDC and plan gates, Kubernetes workloads, observability with SLOs, secrets management and cloud cost audits — validated, not applied: `devops-engineer` runs a mutating command only on an explicit instruction naming that command | [`tsh-platform-engineering`](/docs/plugins/tsh-platform-engineering/) |
| [Context management](/docs/use-cases#context-management) | The context files Claude Code loads in each repository — `CLAUDE.md`, path-scoped rules, decision records — and a project's shared knowledge base | [`tsh-core`](/docs/plugins/tsh-core/) and the project-context skills in [`tsh-product-management`](/docs/plugins/tsh-product-management/) |

### Stacks

Stack plugins carry what would change if the repo switched language, framework or cloud. A stack is a **runtime target** or a **cloud provider**, not a language: a repository has exactly one cloud provider but may have more than one runtime target, such as a frontend, a Node service and a Lambda bundle in one repo. Install the ones the repo is built on. See [Stacks](/docs/use-cases#stacks) for what they add to the work above.

### `tsh-core`, the foundation

`tsh-core` holds what stays true regardless of discipline and stack: Git worktree lifecycle, the house standard for writing technical documents, authoring Claude Code extensions, the project-context files Claude Code loads, the decision-record format, and a one-command project setup. It also bundles three MCP servers: Atlassian for Jira and Confluence, Figma for design context, and Context7 for library documentation. Other plugins rely on those servers instead of shipping their own copies, so install `tsh-core` alongside whatever else you pick.

## What's in the marketplace

### Core

<PluginList family="core" />

### Disciplines

<PluginList family="discipline" />

### Stacks

<PluginList family="stack" />

## Where to start by task

{/* PHASE2(narrative): "Where to start by task" table — shape taken from the Quick Wins table of the Copilot Collections intro (problem → command, minus its time estimates) — decide in Phase 2 whether the intro keeps a task table or links straight to use cases */}

| You want to | Start with |
| :-- | :-- |
| Turn workshop material into Jira-ready epics and stories | [`/tsh-product-management:analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) |
| Understand workshop material before committing to any backlog item | [`/tsh-product-management:explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) |
| Implement a feature, ticket or plan end to end | [`/tsh-product-engineering:orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) |
| Fix a bug whose cause is not yet known | [`/tsh-product-engineering:debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) |
| Judge whether a change is ready to merge | [`/tsh-product-engineering:reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) |
| Check whether a page matches its Figma design | [`/tsh-product-engineering:reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) |
| Write or de-flake Playwright end-to-end tests | [`@tsh-product-testing:e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) |
| Audit a service's code and dependencies for security | [`/tsh-product-engineering:auditing-application-security`](/docs/plugins/tsh-product-engineering/skills/auditing-application-security) |
| Audit infrastructure for security, cost and practice gaps | [`@tsh-platform-engineering:infrastructure-auditor`](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor) |
| Set up Claude Code's context in a repository | [`/tsh-core:init`](/docs/plugins/tsh-core/skills/init) |

Most skills are model-invocable: describe the work in plain words, such as "implement this ticket" or "is this ready to merge", and Claude loads the matching skill. A few entry points, such as `/tsh-core:init` and `/tsh-product-management:analyze-materials`, run only when you type them.

## How to start

1. Check the [prerequisites](/docs/getting-started/prerequisites). Agentic Collections requires Claude Code v2.1 or newer.
2. [Install](/docs/getting-started/installation): add the marketplace once, then install the plugins you want.
3. [Connect your tools](/docs/getting-started/connecting-tools): sign in to Atlassian and Figma once per machine with `/mcp`.
4. Take your [first steps](/docs/getting-started/first-steps) with the skills and agents you installed.

## Where to go next

- [Workflows](/docs/workflows/overview) — how the skills and agents work together on a real task.
- [Plugins](/docs/plugins/) — every plugin, skill and agent, with its own page.
- [Integrations](/docs/integrations/overview) — the MCP servers and the Playwright CLI the plugins use.
- [Use cases](/docs/use-cases) — what each vertical does today.
- [For CTOs](/docs/for-ctos) — the case for adopting it across a team.
