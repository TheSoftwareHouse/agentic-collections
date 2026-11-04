---
title: 'TSH Stack: Node.js'
sidebar_label: Overview
sidebar_position: 0
description: TSH conventions for TypeScript on Node.js, covering compiler configuration for a Node runtime, backend type modelling, and NestJS API implementation and review.
sources:
  - plugins/tsh-stack-nodejs/.claude-plugin/plugin.json
  - plugins/tsh-stack-nodejs/README.md
sources_hash: "7daeca73f7ec157be5ee3a6f5a10f4255815c810bf6ac8c71c62647da4ae248e"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: Node.js

`tsh-stack-nodejs` carries TSH's conventions for TypeScript on Node.js: the compiler configuration for a Node runtime, how to model types in a backend, and NestJS API implementation and review.

A stack in this marketplace is a **runtime target**, not a language. Browser-targeted TypeScript lives in [`tsh-stack-frontend`](/docs/plugins/tsh-stack-frontend/), because a bundled app and a Node service need genuinely different compiler configuration, and because most projects have a frontend whatever their backend is written in. A fullstack TypeScript repository installs both plugins. Framework skills live inside their runtime's plugin: `implementing-nestjs-api` belongs here, not in a separate NestJS plugin.

## Who installs it and where

Install it at **project scope**, so it travels with the repository: the repository already knows what it runs on. Your discipline plugin (for example [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)) and [`tsh-core`](/docs/plugins/tsh-core/) travel with you at user scope. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here.

Once installed, skills are invoked as `/tsh-stack-nodejs:<skill>`. Release notes are on the [changelog page](/docs/changelog/tsh-stack-nodejs).

## What it ships

<PluginComponents plugin="tsh-stack-nodejs" />

All three skills are model-invocable: Claude loads them when the work matches their description, so you do not have to type the command.

## How the skills layer

The three skills build on each other, and because they ship in one plugin, the links between them always resolve.

| Layer | Skill | Owns |
| :-- | :-- | :-- |
| Compiler baseline | [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) | Version pin, `tsconfig.json` baseline for a Node runtime, decorator-metadata and class-field settings |
| Type shapes | [`modelling-types-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs) | How to express a backend type so illegal states cannot compile |
| Framework | [`implementing-nestjs-api`](/docs/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api) | NestJS module, CQRS, TypeORM and REST guidance, on top of the compiler baseline |

## Near-twins in other stack plugins

`configuring-typescript-for-nodejs` has a near-twin, [`configuring-typescript-for-frontend`](/docs/plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend), in `tsh-stack-frontend`. Version policy, the strictness ladder and the upgrade procedure exist in both on purpose, because a skill cannot link across plugins. The target-specific parts stay different. [`tsh-stack-serverless`](/docs/plugins/tsh-stack-serverless/) carries a third relative, [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless), for bundler-emitted Lambda code.

## MCP servers, hooks and agents

This plugin ships no agents, no `.mcp.json` and no hooks.

## Not covered yet

The plugin README lists these gaps as deliberate scope:

- **Build toolchain choice**: `tsc` versus SWC versus esbuild versus `tsx`. The type-gate rule is covered, but picking the transpiler is not.
- **Monorepo project references** beyond a short note.
- **Non-Nest frameworks**: Express, Fastify and Hono have no skill of their own.

## Source

- [`plugins/tsh-stack-nodejs/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-nodejs/README.md)
- [`plugins/tsh-stack-nodejs/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-nodejs/.claude-plugin/plugin.json)
