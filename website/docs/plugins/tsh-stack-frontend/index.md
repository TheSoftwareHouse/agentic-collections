---
title: TSH Stack Frontend
sidebar_label: Overview
sidebar_position: 1
description: TSH conventions for browser-targeted frontend code, covering TypeScript configuration, implementation conventions with a Figma-first workflow, and WCAG 2.1 AA implementation.
sources:
  - plugins/tsh-stack-frontend/.claude-plugin/plugin.json
  - plugins/tsh-stack-frontend/README.md
sources_hash: "08d8610e2a3667459c9757cfd22c47fcceccc06e820641d586e6fe687ea277be"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack Frontend

TSH conventions for browser-targeted frontend code: TypeScript compiler configuration for bundler-resolved applications, implementation conventions for any change to frontend code with a Figma-first workflow when a design exists, and WCAG 2.1 AA accessibility implementation.

## Who installs it and where

`tsh-stack-frontend` is a **stack** plugin, not a discipline plugin. Install it into any project with a frontend, at **project** scope, so it travels with the repo. Your discipline plugin (`tsh-product-engineering` and friends) travels with you at **user** scope, and so does [`tsh-core`](/docs/plugins/tsh-core/). The install commands and the scope prompt are on the [installation page](/docs/getting-started/installation), which renders the repository README. The marketplace entry is `tsh-stack-frontend@tsh-agentic-collections`.

A stack here is a **runtime target**, not a language. That is why the plugin exists separately from `tsh-stack-nodejs`: most TSH projects have a frontend whatever their backend is written in, so a Go, PHP or Java team writing React can install this without a NestJS surface arriving with it.

## What it ships

<PluginComponents plugin="tsh-stack-frontend" />

The plugin ships skills only. The skills are model-invocable: Claude loads them when the work matches their descriptions, so you do not have to remember to type the commands.

The rule the plugin exists to enforce, if you read nothing else: **Vite does not type-check.** `vite build` runs esbuild and Rollup, which strip types without reading them, so a frontend repo can ship type errors indefinitely while every build passes green. A real `tsc -b` step that fails CI is, in the README's words, the single highest-value thing in here.

## Accessibility: building versus auditing

[`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) covers accessibility while implementing a component. Auditing an existing page for violations is [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility) in [`tsh-product-testing`](/docs/plugins/tsh-product-testing/). Each side names the other, and the audit skill may not be installed, in which case the implementation skill names the gap rather than improvising an audit.

## Works with

`implementing-frontend` and `ensuring-accessibility` are the implementation-side half of TSH's frontend flow. The verification half, the UI verification gate that captures the running app with the Playwright CLI and judges it against Figma, lives in `tsh-product-engineering`, installed at user scope. Each side works without the other; together they reproduce the full flow.

## Dependencies

- **`tsh-core`.** `implementing-frontend` treats reading the design as a hard gate, and that read goes through the Figma MCP server that `tsh-core` bundles. After installing `tsh-core`, run `/mcp` once per machine, pick `figma` and finish the browser login. Every call runs under your own Figma account. See the [Figma](/docs/integrations/figma) integration page.
- **`context7`.** The React version policy in `implementing-frontend` looks up current React documentation through `context7`, which `tsh-core` also bundles. It needs no login; without it the skill falls back to react.dev. See the [Context7](/docs/integrations/context7) integration page.
- **Without a Figma sign-in** the verification gate in `tsh-product-engineering` degrades honestly: components with no design reference are still implemented from the plan, and ones that need a design report what is missing rather than guessing.
- **MCP servers and hooks.** The plugin ships no `.mcp.json` and no `hooks/hooks.json`. The Figma server deliberately lives in `tsh-core` rather than here: this is a project-scope plugin, so a repository that did not install it would leave the verification gate with no design source at all.

## Not covered yet

The README states these gaps are scope, not oversight:

- **Next.js, Angular, Svelte/SvelteKit, Vue/Nuxt.** The compiler-option guidance applies to all of them; the concrete layout is Vite-specific.
- **State management and styling systems** beyond the component-level patterns in `implementing-frontend`.
- **Testing, linting and formatting** setup.
- **Type modelling**, such as unions, branded types and `unknown` over `any`.

## Scope

The routing question for this plugin is whether the guidance would change if the project switched runtime target or framework. If yes, it belongs here. If it would change when the **reader** switched job, it belongs in a discipline plugin. Server-side code is out of scope, including the Node-executed build-time files in a frontend repo: the compiler skill covers how to isolate them in their own `tsconfig`, not how to configure a Node service, which is [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/).

## Changelog

Release notes are on the [changelog page](/docs/changelog/tsh-stack-frontend). Updates arrive with `/plugin update`.
