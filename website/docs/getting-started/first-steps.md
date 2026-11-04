---
title: First steps
sidebar_label: First steps
sidebar_position: 4
description: Set up a repository with /tsh-core:init, then invoke skills and agents by their plugin-namespaced names.
sources:
  - README.md
  - plugins/tsh-core/README.md
  - plugins/tsh-core/skills/init/SKILL.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-testing/README.md
sources_hash: "34cb43cc6d4d33a631b7288fabf39cea16fbbb979182cf3bf301153bf58adf7a"
---

# First steps

With the plugins [installed](/docs/getting-started/installation), there are three
things to do: set up the repository, learn how components are invoked, and run a
first task.

## Set up the repository with `/tsh-core:init`

Run it once per repository, inside that repository:

```shell
/tsh-core:init
```

`init` takes a repository from any starting state, whether nothing, a partial setup
or a drifted one, to a complete set of Claude Code context. It audits what already
loads, then creates or repairs:

- the root `CLAUDE.md`, and nested ones where ownership demands,
- path-scoped rules in `.claude/rules/`,
- the decision-record archive and its index.

It does this by running the skills that own those artifacts, in order, and it adds a
maintenance section to `CLAUDE.md` so future sessions know which skill keeps each
artifact true.

- It is safe to re-run: the second pass is a repair, not a rewrite.
- It never overwrites an existing `CLAUDE.md` wholesale; it revises in place and reports what changed.
- It does not invent decision records; it lists candidates for a human to confirm.
- It ends with a report of what was created, repaired and left alone, and flags the result as a proposal for your team to review.

`init` is a command you type. It is deliberately not model-invocable, so a setup
request phrased in prose routes to
[`managing-claude-context`](/docs/plugins/tsh-core/skills/managing-claude-context)
instead.

## Invoke skills and agents

Both are namespaced by plugin, and they are invoked differently:

```shell
/tsh-product-testing:<skill-name>     # skills: type / and the plugin name
@tsh-product-testing:<agent-name>     # agents: @-mention typeahead
```

- Most skills are model-invocable: Claude loads one when your request matches its description, so you can describe the work ("implement this ticket", "is this ready to merge") instead of remembering a command.
- Some skills are commands only. `/tsh-core:init` is one; in `tsh-product-management` the entry points `analyze-materials` and `explore-materials` are too.
- Some skills are internal contracts that agents preload and stay out of the `/` menu, for example `capturing-ui-evidence`.

To see exactly what a plugin gives you, run `/plugin`, open the **Installed** tab and
press Enter on it, or run `claude plugin details tsh-product-testing@tsh-agentic-collections`
from the shell.

## Run a first task

Pick the line that matches your work. Each links to the full page.

| You want to | Try | Needs |
| :-- | :-- | :-- |
| Implement a feature, ticket or plan end to end | [`/tsh-product-engineering:orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) | `tsh-product-engineering` |
| Break a feature into a committed plan file | [`/tsh-product-engineering:creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) | `tsh-product-engineering` |
| Fix a bug at its root cause | [`/tsh-product-engineering:debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) | `tsh-product-engineering` |
| Review a change before merge | [`/tsh-product-engineering:reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) | `tsh-product-engineering` |
| Check a UI against its Figma design | [`/tsh-product-engineering:reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) | Figma sign-in, [`playwright-cli`](/docs/integrations/playwright-cli), a running app and its exact dev server URL |
| Write or de-flake Playwright E2E tests | [`/tsh-product-testing:writing-playwright-e2e-tests`](/docs/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests) or [`@tsh-product-testing:e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) | `tsh-product-testing` |
| Turn workshop material into a Jira-ready backlog | [`/tsh-product-management:analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) with a transcript path, a Figma or FigJam link, a PDF or a folder | Atlassian sign-in for anything Jira |

For the end-to-end flows, see the [workflows](/docs/workflows/overview).

## If something does not show up

See [Troubleshooting](/docs/getting-started/troubleshooting).
