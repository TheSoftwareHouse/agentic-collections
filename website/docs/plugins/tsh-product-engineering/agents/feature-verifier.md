---
title: Feature Verifier
sidebar_label: feature-verifier
sidebar_position: 2
description: Executes a plan's verification document against the running application and returns per-scenario evidence from E2E suites, browser walkthroughs, real API calls and database and log checks.
sources:
  - plugins/tsh-product-engineering/agents/feature-verifier.md
sources_hash: "8b698f6db901273943ef075199fb75086391fa6a48d72f9fcc7dcbed3e93e46f"
---

# Feature Verifier

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Mention:** `@tsh-product-engineering:feature-verifier`  
**Model:** `sonnet`  
**Tools:** no `tools` list in the frontmatter; `disallowedTools: Write, Edit`  
**Skills preloaded:** none

Proves that a delivered feature works by executing the plan's verification document against the running application and collecting evidence per scenario. It does not fix code and does not review it. The parallel [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) owns the code, and the verifier owns the running behavior. Use it in a plan's final verification phase, in parallel with code review.

## Inputs it requires

The delegation must name the verification document path (`specifications/<task-id>/<task-name>.verification.md`) and the pinned dev server URL where scenarios need one. If an input is missing, the document is unreadable, or the environment the document describes cannot be reached, it stops and reports exactly what is missing. It never improvises scenarios or guesses a URL.

## Responsibilities

1. Reads the verification document in full: environment, seeding, scenarios in order, pass criteria and boundaries.
2. Confirms the environment matches the document, with the server reachable at the pinned URL and required services up. Runs the seeding commands verbatim and confirms the expected post-seed state before continuing.
3. Executes the scenarios in the document's order, exactly as written. It does not skip steps, reorder them or substitute an easier check.
4. Collects the evidence each scenario demands, then reports.

### Evidence rules

| Scenario type | How it is verified |
| :-- | :-- |
| **Browser** | Drives the app with the Playwright CLI (`playwright-cli`, or `npx playwright cli`) in a named session. At each stated step it saves a screenshot into `specifications/<task-id>/verification-evidence/`, then reads and examines the image. Accessibility snapshots, DOM assertions and click-throughs are navigation, never verification. When neither CLI form is available it stops and reports that the machine needs `npm install -g @playwright/cli@latest` |
| **API** | Sends the real request as specified and records the actual status and the response fields the document names. A response is never inferred from code |
| **Database and logs** | Runs the document's stated queries and searches verbatim and records what came back |
| **E2E suite** | Runs the stated command verbatim and records its pass or fail output |

## Boundaries

- Never fixes, edits or works around application code or configuration. A failing scenario is a finding.
- Never bypasses, fakes, seeds or injects authentication state. Logging in through the application's real sign-in flow with the account the document names is allowed, and credentials stay out of reports.
- Treats the delegated dev server URL as pinned and never switches ports or starts a different server.
- Never runs `git clean`, `git reset`, `git stash`, `git restore` or `git checkout -- <path>`, because pre-existing uncommitted changes are intentional.

## What it returns

A structured report. Per scenario, in order, it states pass or fail with the evidence the document demanded: what the examined screenshot showed, response status and fields, rows returned, log lines or suite output. Then it lists blockers, each with exactly what is needed to clear it. A clean run is stated plainly, and findings are never invented.

## Used by

- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) delegates to it in the final verification phase, with the verification document path and the pinned inputs.
- [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) defines the functional-verification task it executes and drafts the verification document it runs.

## Source

[`plugins/tsh-product-engineering/agents/feature-verifier.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/agents/feature-verifier.md)
