---
title: TSH Product Testing
sidebar_label: Overview
sidebar_position: 1
description: Quality assurance plugin from The Software House, covering Playwright end-to-end tests proven stable by repeated headless runs, and WCAG 2.1 AA accessibility audits.
sources:
  - plugins/tsh-product-testing/.claude-plugin/plugin.json
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-product-engineering/skills/capturing-ui-evidence/SKILL.md
sources_hash: "094df34ee77038b8f11293cadac2139b55b17075a981f7c4d8fd452dedaef0ff"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Product Testing

Quality assurance: Playwright end-to-end tests proven stable by three or more consecutive headless runs, with any remaining flakiness reported rather than hidden, and WCAG 2.1 AA accessibility audits that report the success criterion behind every finding. The plugin covers QA, meaning does the software work and can everyone use it.

## Who installs it and where

`tsh-product-testing` is a **discipline** plugin. Install it at **user** scope so it follows you across projects, because your job does not change from repo to repo. The install commands and the scope prompt are on the [installation page](/docs/getting-started/installation), which renders the repository README. The marketplace entry is `tsh-product-testing@tsh-agentic-collections`.

## What it ships

<PluginComponents plugin="tsh-product-testing" />

Skills are invoked as `/tsh-product-testing:<skill>` and the agent as `@tsh-product-testing:e2e-engineer`.

## Conventions the plugin holds to

- **A failing test is either a wrong test or a real bug**, and deciding which is the work. Nothing here weakens an assertion to reach green: an application defect becomes `test.fixme('BUG: ...')` plus a reported bug.
- **One green run is not evidence.** A test is done after 3+ consecutive headless passes.
- **Every accessibility finding names its WCAG success criterion**, so it can be prioritized and verified rather than argued about.
- **The project's existing test conventions outrank these defaults.** Both skills start by establishing them.
- **Never bypass authentication.** Real sign-in with environment-supplied credentials is fine; seeding or faking session state is not.

## Auditing versus building accessibility

Accessibility is split by outcome. [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility) lives here and reports violations in an existing page, component or flow. Implementing accessible components belongs to [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) in [`tsh-stack-frontend`](/docs/plugins/tsh-stack-frontend/), the stack plugin that installs with the repo.

Verifying that implemented UI matches its design is a separate concern and does not live in this plugin. According to the plugin README, that work belongs with product engineering, alongside the implementation loop it feeds.

## Prerequisites and dependencies

- **Playwright CLI.** Live-page exploration runs on the [Playwright CLI](/docs/integrations/playwright-cli). Its `snapshot` is the accessibility tree that `getByRole` resolves against, so it is how a locator is confirmed before it is committed to a test. Have `playwright-cli` on the machine: `npm install -g @playwright/cli@latest`, or a project-local install reached via `npx playwright cli` — never `npx playwright-cli`, which fetches a deprecated package. The skill's own preflight checks the local install with `npx --no-install playwright cli --version`. See the [Playwright CLI integration page](/docs/integrations/playwright-cli) for the tool. The workflow checks availability before its first exploration and, when the CLI is missing, asks whether to install it or wait. A subagent, which cannot ask, reports the missing prerequisite instead.
- **MCP servers.** The plugin ships no `.mcp.json` and no `hooks/hooks.json`. Playwright API documentation comes from `context7`, which [`tsh-core`](/docs/plugins/tsh-core/) bundles; for Playwright, query the library ID `/microsoft/playwright.dev` directly.
- **`tsh-core`.** `e2e-engineer` reads acceptance criteria from a Jira issue key using the Atlassian MCP tools that `tsh-core` bundles, and reports written for people outside the team go through `/tsh-core:writing-technical-documents`. Without `tsh-core`, supply acceptance criteria directly instead of by issue key.

## Changelog

Release notes are on the [changelog page](/docs/changelog/tsh-product-testing).
