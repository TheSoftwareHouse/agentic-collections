---
title: Implementing Frontend
sidebar_label: implementing-frontend
sidebar_position: 3
description: TSH conventions for any change to frontend application code, from named React imports and module boundaries to a mandatory Figma read before markup.
sources:
  - plugins/tsh-stack-frontend/skills/implementing-frontend/SKILL.md
  - plugins/tsh-stack-frontend/skills/implementing-frontend/references/
sources_hash: "4785d73dc2828ba65c4a4b216d5bb30ef33bb63ac4e5f41346847dc6870780db"
---

# Implementing Frontend

**Plugin:** [`tsh-stack-frontend`](/docs/plugins/tsh-stack-frontend/)  
**Invoke:** `/tsh-stack-frontend:implementing-frontend` (Claude also loads it when the work matches its description)  
**Used by:** [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) in `tsh-product-engineering`, which loads it by name when `tsh-stack-frontend` is installed. [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) lists it as a related skill

TSH conventions for frontend application code: how components are composed, where state and modules live, and, when the task has a design, the Figma-to-code workflow that comes before any markup. It covers **every** change to frontend application code, with or without a design: a new screen from Figma, a custom hook, a store or API client, a refactor that moves modules, or a data or logic change that renders nothing new. Each rule scopes itself: the Figma gate applies only when the task has a design reference, the token and UI-state rules to code that renders, and the import, export, typing and module rules to all of it.

The project's existing component patterns, design system and styling approach outrank the skill's defaults. The design and module rules are framework-agnostic; the React rules apply when `package.json` depends on `react`, which is the only framework this plugin covers today.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Figma-first** | For a Figma-backed task, the design is fetched and studied through the Figma MCP before any markup, layout or styling is written. This pre-implementation read is a hard gate, distinct from any post-implementation verification loop |
| **No assumptions** | Missing or unclear design context, tokens or specs stop the work: a subagent reports the blocker to the caller, the main conversation asks the user |
| **Design tokens** | Every visual value comes from the project's tokens. No exact match means the closest token plus a documented deviation; a genuinely new value is flagged and asked about before a token is created |
| **Components** | Single responsibility, typed props, no `export default`, no `any` props, no component with more than about 7 props where composition would do, declarative UI from state |
| **React imports** | Named imports from `react`, for example `import { useState, type ReactNode } from 'react'`. Never `import * as React`, `import React`, `React.useState`, `React.memo` or `React.FC`. A project that already uses the namespace style consistently keeps it |
| **UI states** | Loading, error (a meaningful message plus a recovery action) and empty, in every data-dependent component |
| **Modules** | A barrel `index.ts` only at a public API boundary, with named re-exports. After a move or rename, every importer is updated and the old file is deleted; a pass-through file is not a barrel |
| **State placement** | A decision table: local, lifted, context or DI, global store, server cache |
| **React patterns** | Composition, state, error boundaries and performance techniques in React terms, plus an ESLint rule that enforces the import style |

## Version baseline

The React rules target **React 19** with the automatic JSX runtime (`jsx: react-jsx`), and the skill reads the project's `package.json` first:

| Situation | What the skill does |
| :-- | :-- |
| React is pinned | Follows that version. React 18 is fine; every rule holds |
| No `package.json` yet (greenfield) | Installs the latest stable release, with `react-dom` on the same version and `@types/react` and `@types/react-dom` on the same major |
| Installed major is newer than 19 | Checks what changed since 19 in the current React documentation, through `context7` or react.dev, before applying the skill; the documentation wins where they disagree |
| Classic JSX runtime (`jsx: react`) | Keeps `import React from 'react'` in files with JSX, still imports hooks and types by name, says so, and treats the move to `react-jsx` as its own change |

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | For a Figma-backed task, fetch and study the design through the Figma MCP before writing or editing any markup, layout or styling |
| NEVER | Implement from assumptions |
| MUST | Take every visual value from the design system tokens |
| NEVER | Use `export default`, untyped or `any` props, or a component with more than about 7 props where composition would do |
| MUST | Handle loading, error and empty states in every data-dependent component |
| MUST | Declare the UI from state; never manipulate the DOM imperatively |
| MUST | Import what you use from `react` by name |
| MUST | Add a barrel only at a public API boundary, with named re-exports |
| NEVER | Leave a pass-through file after moving or renaming a module. Exceptions: the public API of a package other code consumes, kept and marked `@deprecated`, and a re-export a plan explicitly stages as transitional |

## How it works

Steps 1 and 2 apply when the task has a design reference. Without one, such as a hook, a refactor or a data or logic change, the process starts at step 3.

1. **Fetch and review the Figma design**: resolve the node, export the node image via the Figma MCP, and extract layout, spacing, typography, colours, dimensions, variants and states.
2. **Gather design context**: map every Figma value to an existing token, identify every state the design implies and the responsive breakpoints.
3. **Plan the structure**: reusable component, custom hook or page-specific code; typed props and hook signatures; state placement; search for existing similar components and hooks to extend or compose. A module move lists every importer it will rewrite.
4. **Implement**: composition over prop sprawl, explicit prop types co-located in `ComponentName.types.ts`, named exports and `react` imports, the framework's error-boundary mechanism around data-dependent sections, the three UI states, and tokens for every visual value.
5. **Organize modules**: barrels only at public boundaries, no importer left on an old path.
6. **Verify**: run the project's type check and linter. For a design-backed task, if the calling workflow provides a UI verification loop, defer to it instead of duplicating it; otherwise compare the rendered result against the design and walk through each interaction state.

The skill ends with a ten-item component checklist, which doubles as the frontend review checklist for the diff.

## References

| Reference | Loaded when |
| :-- | :-- |
| Component guidelines | Deciding where state lives, adding a barrel file, moving or splitting modules, or reviewing for anti-patterns |
| React patterns | Before writing or reviewing React code |

The component guidelines hold the state decision framework, barrel-file rules (named re-exports only, no `export * from`, one level deep) and an anti-pattern table. The React patterns hold how React implements composition (`children`, render props, compound components, slots), state hooks, error boundaries and performance techniques, with the rule of thumb not to memoize by default, and the ESLint `no-restricted-syntax` configuration that enforces the import style. The skill proposes that rule when the project does not enforce the style yet, and adds it only once the team agrees.

## Boundaries and dependencies

- **Compiler setup** is [`configuring-typescript-for-frontend`](/docs/plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend). The accessibility patterns every component must satisfy are [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility).
- **UI verification against Figma** (capture, tolerances, PASS gates) lives in `tsh-product-engineering`: `reviewing-ui` and its agents. That plugin may not be installed, and the skill says to name the gap rather than improvise verification.
- **Figma MCP and `context7`** come from [`tsh-core`](/docs/plugins/tsh-core/). See the [Figma](/docs/integrations/figma) and [Context7](/docs/integrations/context7) integration pages.

## Related skills

- [`configuring-typescript-for-frontend`](/docs/plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend): the compiler setup underneath these components.
- [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility): accessibility implementation patterns.

## Source

[`plugins/tsh-stack-frontend/skills/implementing-frontend/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-frontend/skills/implementing-frontend/SKILL.md)
