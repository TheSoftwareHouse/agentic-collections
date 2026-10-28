# TSH Product Testing

Quality assurance: Playwright end-to-end tests that do not flake, and WCAG 2.1 AA
accessibility audits that report the success criterion behind every finding.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-product-testing@tsh-agentic-collections
```

## What's in it

### Skills

| Skill | Use for |
| :-- | :-- |
| `writing-playwright-e2e-tests` | Mapping acceptance criteria to scenarios, Page Objects, user-visible locators, anti-flake rules, the bounded debug loop, CI readiness |
| `auditing-accessibility` | WCAG 2.1 AA audits — semantics, keyboard and focus, ARIA correctness, contrast, reflow, axe-core triage — and the same criteria when building |

Invoked as `/tsh-product-testing:<skill>`.

### Agents

| Agent | Use for |
| :-- | :-- |
| `e2e-engineer` | Delegated E2E test tasks, and diagnosing a flaky suite |

Invoked as `@tsh-product-testing:e2e-engineer`.

Release notes live in [`CHANGELOG.md`](CHANGELOG.md).

### Bundled MCP servers

`.mcp.json` ships `context7` for Playwright API documentation. For Playwright, query
the library ID `/microsoft/playwright.dev` directly rather than resolving it.

### Prerequisite: Playwright CLI

**Live-page exploration runs on the
[Playwright CLI](https://www.npmjs.com/package/@playwright/cli)** — its `snapshot` is
the accessibility tree `getByRole` resolves against, so it is how a locator gets
confirmed before it is committed to a test, and it executes a candidate locator
string against the live page. Have `playwright-cli` on the machine:
`npm install -g @playwright/cli@latest`, or a project-local install reached via
`npx playwright-cli` (Node.js required either way). The workflow checks availability
before its first exploration and, when the CLI is missing, asks whether to install it
for you or wait while you do it yourself — a subagent, which cannot ask, reports the
missing prerequisite instead. Neither ever guesses locators blind. This matches `tsh-product-engineering`, whose UI evidence
runs on the same CLI — one browser tool across both plugins, and none of its output
spends MCP tool context.

## Assumes tsh-core

`e2e-engineer` reads acceptance criteria from a Jira issue key using the Atlassian MCP
tools that `tsh-core` bundles, and reports written for people outside the team go
through `/tsh-core:writing-technical-documents`. Install it — it depends on nothing:

```shell
/plugin install tsh-core@tsh-agentic-collections
```

Without it, supply acceptance criteria directly instead of by issue key.

## Conventions this plugin holds to

- **A failing test is either a wrong test or a real bug**, and deciding which is the
  work. Nothing here weakens an assertion to reach green: an application defect becomes
  `test.fixme('BUG: …')` plus a reported bug.
- **One green run is not evidence.** A test is done after 3+ consecutive headless
  passes.
- **Every accessibility finding names its WCAG success criterion**, so it can be
  prioritized and verified rather than argued about.
- **The project's existing test conventions outrank these defaults.** Both skills start
  by establishing them.
- **Never bypass authentication.** Real sign-in with environment-supplied credentials
  is fine; seeding or faking session state is not.

## Scope

This plugin covers QA: does the software work, and can everyone use it. **Verifying that
implemented UI matches its design** is a separate concern and does not live here — that
work belongs with product engineering, alongside the implementation loop it feeds.

## Contributing

Add an agent as `agents/<agent-name>.md`, a skill as `skills/<skill-name>/SKILL.md`.
Start from [`templates/agent.md`](../../templates/agent.md) or
[`templates/SKILL.md`](../../templates/SKILL.md), and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.
