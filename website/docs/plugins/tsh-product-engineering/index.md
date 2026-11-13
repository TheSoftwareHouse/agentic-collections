---
title: TSH Product Engineering
sidebar_label: Overview
sidebar_position: 0
description: Spec-driven feature implementation with committed plan files, delegated implementer subagents, a Figma-backed UI verification gate, root-cause debugging and structured pre-merge code review.
sources:
  - plugins/tsh-product-engineering/.claude-plugin/plugin.json
  - plugins/tsh-product-engineering/README.md
sources_hash: "0bb89eebbc7068a1829a46bfd0b41545bd407d844b1385d0d2be1206b3a8e29a"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Product Engineering

`tsh-product-engineering` carries TSH's spec-driven implementation workflow: a plan file the team can read and commit, implementer subagents that keep file churn and MCP traffic out of your conversation, a Figma-backed UI verification gate driven by Playwright CLI capture, root-cause bug fixing guarded by a regression test, and a delegated review gate at the end.

## Who installs it and where

Install it at **user scope**. The plugin travels with you, not with a repository. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here.

Once installed, skills are invoked as `/tsh-product-engineering:<skill>` and agents as `@tsh-product-engineering:<agent>`. Release notes are on the [changelog page](/docs/changelog/tsh-product-engineering).

## What it ships

<PluginComponents plugin="tsh-product-engineering" />

Every skill except `verifying-ui` is model-invocable, and the descriptions are written to route on the work you describe, such as "implement this ticket", "plan this feature", "is this ready to merge" or "does this page match the design". Each skill also names the sibling that owns the adjacent job, so they do not compete for the same request.

`verifying-ui` and `capturing-ui-evidence` stay out of the `/` menu (`user-invocable: false`). They are contracts that the UI agents preload, not commands worth typing. `verifying-ui` is also `disable-model-invocation: true`, so "does this page match the design?" routes to [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui), the pass that applies the standard, and never to the standard itself.

## How the pieces fit

| Stage | Skill | Agents involved |
| :-- | :-- | :-- |
| Plan | [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) writes the plan file and the verification document | none |
| Implement | [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) runs the plan from the main conversation | [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer), [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) |
| Verify UI | [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) runs one capture-and-judge pass, repeated by the gate in the orchestrator | [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker), [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) |
| Final verification | the orchestrator's final phase | [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) and [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier), in parallel |
| Fix a bug | [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) | loaded by `software-engineer` |
| Record the project's checks | [`capturing-project-checks`](/docs/plugins/tsh-product-engineering/skills/capturing-project-checks) writes the project's verification and security-invariant skills, which the stages above then read | none |
| Audit security | [`auditing-application-security`](/docs/plugins/tsh-product-engineering/skills/auditing-application-security) audits a whole service or a named surface, not one change | [`security-auditor`](/docs/plugins/tsh-product-engineering/agents/security-auditor), read-only |

For the end-to-end flows see [feature implementation](/docs/workflows/feature-implementation), [UI verification](/docs/workflows/ui-verification) and [debugging](/docs/workflows/debugging).

## Prerequisites

- **Playwright CLI.** All browser evidence in this plugin runs on [Playwright CLI](/docs/integrations/playwright-cli): the UI verification gate's capture, `ui-engineer`'s standalone screenshot checks and `feature-verifier`'s browser walkthroughs. Before the first capture, the workflow runs `playwright-cli --version` (with an `npx` fallback) and, when neither answers, asks whether to install it for you or wait while you do it yourself. The install command is `npm install -g @playwright/cli@latest`.
- **Figma MCP server, bundled by `tsh-core`.** Design fetching needs the [Figma MCP server](/docs/integrations/figma). This plugin deliberately does not ship a second copy. Install `tsh-core` alongside it and run `/mcp` once to authenticate; every call then runs under your own Figma account. Until that sign-in happens, agents stop and report what is missing rather than guessing at a design, and `ui-reviewer` reports `VERIFICATION NOT RUN`. This applies to the judgment side only: capture needs no design reference, and a UI task with no design at all is implemented from the plan and never enters the gate.
- **A running app and its exact dev server URL**, for UI work. The workflow asks you to confirm the URL once and pins it for the whole loop.

When the page under verification needs a login, capture reuses whatever the project already has: a documented auth recipe, an existing E2E setup, existing `.env` variables that match the login form, or a seeded development account. Only when none of those exists does the flow derive `TSH_UI_LOGIN_*` variable names and ask you to add them to `.env`. Nothing is bypassed, and credentials never travel through the chat.

## MCP servers and hooks

This plugin ships no `.mcp.json` and no hooks. It bundled the Playwright MCP server through version 0.6.0 and replaced it with Playwright CLI, so that only file paths and measured values enter model context. Figma and Atlassian access come from `tsh-core`. The Jira and Confluence access is bundled there because every discipline reads from Jira, not just this one; authenticate once with `/mcp`.

## Not covered by this plugin

E2E test suites belong to `tsh-product-testing`, infrastructure and CI to `tsh-platform-engineering`, and discovery and business-analysis work to `tsh-product-management`. Git worktree lifecycle lives in `tsh-core`. Deeper analysis skills such as codebase analysis and gap analysis are candidates for a later wave, according to the plugin README.

## Source

- [`plugins/tsh-product-engineering/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/README.md)
- [`plugins/tsh-product-engineering/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/.claude-plugin/plugin.json)
