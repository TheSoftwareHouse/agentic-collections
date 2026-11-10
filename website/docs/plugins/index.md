---
title: Plugins
sidebar_label: Overview
sidebar_position: 1
description: The three plugin families in Agentic Collections — core, disciplines and stacks — which scope each one installs at, and why.
sources:
  - README.md
  - CLAUDE.md
  - .claude-plugin/marketplace.json
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-platform-engineering/README.md
sources_hash: "bcc5aaabf70adc4ee652f78379123155208c15f9760c52751182f26a2478f567"
---

import { PluginList } from '@site/src/components/PluginComponents';

# Plugins

Agentic Collections publishes three families of plugins: **core** for what holds regardless of role and stack, **disciplines** for _how we work_, and **stacks** for _what we work with_. The families exist so they can install differently: a discipline plugin travels with **you**, a stack plugin with the **repo**, and `tsh-core` with you, because it depends on nothing at all.

Every skill and agent is namespaced by its plugin. Invoke a skill as `/<plugin>:<skill>` and mention an agent as `@<plugin>:<agent>`. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README.

## Core — the ground under both

Install it at **User** scope, the same as your discipline plugin. It depends on neither your role nor the repo, so it should follow you everywhere.

<PluginList family="core" />

`tsh-core` is one plugin, not a family. Anything that would change if you switched job belongs in a discipline plugin, and anything that would change if the repo switched language belongs in a stack plugin. Its admission bar is the highest in the repo, because everyone installs it and every skill in it spends every teammate's context.

Other plugins may assume it is installed and refer to it by name. It bundles the Atlassian, Figma and Context7 MCP servers, which the discipline plugins use instead of shipping their own copies.

## Disciplines — how we work

Install the one that matches your job, at **User** scope. Your job doesn't change from repo to repo.

<PluginList family="discipline" />

When work spans two disciplines, it lives in the plugin that owns the _outcome_, not the one that owns the tooling: an accessibility audit belongs to `tsh-product-testing` even though it reads component code.

## Stacks — what we work with

Install what the project is built on, at **Project** scope. The repo already knows what it is written in, so everyone working on it should get the same guidance, and nobody should carry another stack's skills around.

<PluginList family="stack" />

A stack here is a **runtime target** or a **cloud provider**, not a language. A repository has exactly one cloud provider but may have more than one runtime target. The frontend, Node and serverless plugins all carry TypeScript guidance, because a browser app, a Node service and a Lambda bundle need different compiler configuration. Every stack gets its own plugin, named `tsh-stack-<stack-name>`, once it has real content to ship.

## Scopes

Each install asks you to pick a scope.

| Scope | Who gets it | Where it's written |
| :-- | :-- | :-- |
| **User** | You, in every project | Your user settings |
| **Project** | Everyone working on this repo | The repo's `.claude/settings.json`, which is committed, so it travels with the repo |
| **Local** | You, in this repo only | `.claude/settings.local.json`, which you keep out of git |

- **Scope is resolved against your current directory.** Run `project` and `local` installs from the target repo's root.
- **Scopes stack.** A committed project set is a starting point: anyone can add their own plugins on top at `user` or `local` scope, and both sets load together.
- **Installing never copies plugin files into your project.** Everything lives in `~/.claude/plugins/marketplaces/`, whatever the scope. Scope decides which projects load a plugin, not where it is stored.

Installing at `project` scope writes the repo's `.claude/settings.json` for you; commit that file and the whole team gets the set. The README section [Onboarding a whole project team at once](https://github.com/TheSoftwareHouse/agentic-collections#onboarding-a-whole-project-team-at-once) shows the file and why `tsh-core` is deliberately left out of it.
