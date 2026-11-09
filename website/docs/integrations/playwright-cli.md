---
title: Playwright CLI
sidebar_label: Playwright CLI
sidebar_position: 7
description: The Playwright CLI is a command-line tool, not an MCP server — what installing and using it involves, and which workflows capture UI evidence or explore pages with it.
sources:
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/skills/capturing-ui-evidence/SKILL.md
  - plugins/tsh-product-engineering/skills/capturing-ui-evidence/references/playwright-cli-commands.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/references/ui-verification-gate.md
  - plugins/tsh-product-engineering/agents/ui-capture-worker.md
  - plugins/tsh-product-engineering/agents/ui-engineer.md
  - plugins/tsh-product-engineering/agents/feature-verifier.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-product-testing/agents/e2e-engineer.md
  - plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/SKILL.md
  - plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/references/playwright-cli-exploration.md
sources_hash: "f9422c44fc3f65382b9914e7399ca99cffda072d20ffa76577e4e53e2859396f"
---

# Playwright CLI

All browser evidence in the TSH plugins runs on the
[Playwright CLI](https://www.npmjs.com/package/@playwright/cli). It is a command-line
tool you install, not an MCP server, and no plugin bundles it.

Its output is files on disk, so only paths and measured values enter the model's
context. That is why it replaced the Playwright MCP server that `tsh-product-engineering`
bundled through 0.6.0, and it means one browser tool across `tsh-product-engineering`
and `tsh-product-testing`, with none of its output spending MCP tool context.

## Install

Have `playwright-cli` on the machine. Node.js is required either way.

```shell
npm install -g @playwright/cli@latest
```

Alternatively, use a project-local install reached through `npx playwright cli` (the
`playwright` package's `cli` subcommand). This is the form the
[Playwright CLI README](https://github.com/microsoft/playwright-cli#readme) documents and the
one both `tsh-product-engineering` and `tsh-product-testing` use. Never use
`npx playwright-cli`, which fetches a deprecated package.

You do not have to remember this. Before the first capture or exploration, the
workflow runs `playwright-cli --version`, with an `npx` fallback, and when neither
answers it asks whether to install the CLI for you or wait while you do it yourself.
An agent that cannot ask reports the missing prerequisite instead, and never guesses
locators blind.

## What uses it

| Component | What it does with the CLI |
| :-- | :-- |
| [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) and its contract [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence) | Collect the three ACTUAL artifacts for UI verification |
| [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) and [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) | Check the CLI is available before a capture or the UI verification gate runs |
| [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) | Standalone screenshot checks of its own implementation |
| [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier) | Browser walkthroughs, with per-step screenshots as evidence |
| [`e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) and [`writing-playwright-e2e-tests`](/docs/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests) | Explore the live page to confirm a locator before it is committed to a test |

## How UI evidence is captured

`capturing-ui-evidence` is the mechanical capture contract. It drives the CLI against
the dev server URL you confirmed once, and writes three artifacts into the iteration
directory under `specifications/<task-id>/ui-verification/`:

- `actual.png`, a full-page screenshot,
- `computed-styles.json`, the computed styles of the measured elements,
- `a11y-snapshot.yml`, the accessibility snapshot.

When a Figma URL is supplied, the shared reference image is exported through the
[Figma](/docs/integrations/figma) server, never through the browser. Capture only
collects evidence; judging it is the `ui-reviewer` agent's job.

The procedure uses a named session (`open -s <name>`), `resize` to the design width,
`goto` the full URL, `run-code` to stabilize the render and take the screenshot,
`snapshot` and `eval` for the other two artifacts, and `close` at the end. Commands
run from the repository root so the CLI's own `.playwright-cli/` scratch directory
stays there, where it is git-ignored. Authentication reuses the project's own login
path, and a login is never bypassed or faked.

## How E2E exploration uses it

For `tsh-product-testing`, `snapshot` returns the accessibility tree that `getByRole`
resolves against. So it is how a locator gets confirmed before it goes into a test,
and a candidate locator string can be executed against the live page. A test that
drives no browser, such as a pure API scenario, has no locators to confirm.

If the dev server is unreachable, confirmation may be skipped, and the report must
name that.

## Before you run a capture

Have the target app running, and know its exact full dev server URL. The workflow
asks you to confirm the URL once and pins it for the whole loop.
