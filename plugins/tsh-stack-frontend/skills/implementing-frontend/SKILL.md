---
name: implementing-frontend
description: "TSH conventions for any change to frontend application code, React today, with or without a design: components, custom hooks and the non-UI modules around them, named imports from react, typed props, module boundaries and barrel files, the three UI states every data-dependent component handles, design tokens, and a mandatory Figma read before markup when a design exists. Use when writing or refactoring any browser app code — a component, hook, store, API client, utility or module move, in a .ts, .tsx or .jsx file."
when_to_use: "Trigger on: writing or changing any code in a browser app — UI components, custom hooks, context providers, stores, API clients and utilities — translating a Figma design into code, frontend work with no design such as a refactor, data wiring or a logic change, moving or splitting modules and barrel files, choosing where state lives, wiring design tokens, or starting or upgrading a React app. Compiler setup is configuring-typescript-for-frontend; a11y implementation patterns are ensuring-accessibility."
---

# Implementing Frontend

TSH conventions for frontend application code: how components are composed, where
state and modules live, and — when the task has a design — the Figma-to-code
workflow that comes before any markup.

## Applicability and Precedence

This skill covers **every** change to frontend application code, with or without a
design: a new screen from Figma, a custom hook, a store or API client, a refactor that
moves modules, a data or logic change that renders nothing new. The rules scope
themselves: the Figma gate applies only when the task has a design reference, the
token and UI-state rules to code that renders, and the import, export, typing and
module rules to all of it.

Local repository rules outrank this skill: the project's existing component
patterns, design system, and styling approach win over the defaults here. The design
and module rules are framework-agnostic; the React rules apply when `package.json`
depends on `react`, which is the only framework this plugin covers today.

## Version Baseline

The React rules target **React 19** with the automatic JSX runtime
(`jsx: react-jsx`). Read the project's `package.json` before writing React code:

- **React is pinned** → follow that version. React 18 is fine; every rule here holds.
- **No `package.json` yet — a greenfield app** → install the latest stable release
  (`npm view react version`), with `react-dom` on the same version and
  `@types/react` / `@types/react-dom` on the same major.
- **The installed major is newer than 19** → check what changed since 19 in the
  current React documentation — through `context7`, which `tsh-core` bundles, or
  react.dev — before applying this skill; where they disagree, the documentation
  wins.
- **The project compiles JSX with the classic runtime** (`jsx: react`) → JSX needs
  `React` in scope there, so the import rule below does not apply. Say so, and treat
  the move to `react-jsx` as its own change (`configuring-typescript-for-frontend`).

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | For a Figma-backed task, fetch and study the design through the Figma MCP before writing or editing any markup, layout, or styling. This pre-implementation design read is a hard gate, distinct from any post-implementation verification loop. |
| NEVER | Implement from assumptions. Design context, tokens, or specs missing or unclear → stop and raise it (as a subagent, report the blocker to the caller; in the main conversation, ask the user). Missing information produces wrong UI; asking produces correct UI. |
| MUST | Take every visual value (colors, spacing, typography, shadows, radii) from the project's design system tokens. No exact token match → use the closest existing token and document the deviation; a genuinely new value → flag it and ask before creating a token. |
| NEVER | Use `export default`, untyped or `any` props, or a component with more than ~7 props where composition (children, slots, compound components) would do. |
| MUST | Handle all three UI states in every data-dependent component: loading (progress indicator), error (meaningful message plus recovery action), empty (helpful message when no data). |
| MUST | Declare what the UI looks like from state; never imperatively manipulate the DOM. Compose complex UIs from small, single-responsibility components. |
| MUST | Import what you use from `react` by name: `import { useState, type ReactNode } from 'react'`. NEVER `import * as React`, `import React`, `React.useState`, `React.memo` or `React.FC`. A project that already uses the namespace style consistently keeps it — don't mix the two in one codebase. |
| MUST | Add a barrel `index.ts` only at a public API boundary — a folder other modules consume — with named re-exports. A folder serving one parent is imported directly. |
| NEVER | Leave a pass-through file after moving or renaming a module. A file that only re-exports the new location is not a barrel: update every importer to the new path and delete the old file in the same change. |

## Implementation Process

Steps 1–2 apply when the task has a design reference. Without one — a hook, a
refactor, a data or logic change — start at step 3.

1. **Fetch and review the Figma design** (the gate above). Resolve the node, export
   the node image via the Figma MCP, and extract layout, spacing, typography, colors,
   dimensions, variants, and states.
2. **Gather design context.** Map every Figma value to an existing design token:
   extract the raw value → search the codebase for a matching token → use it; no
   exact match → closest token plus a documented deviation; truly new → ask first.
   Identify every state the design implies (default, hover, focus, active,
   disabled, loading, error, empty) and the responsive breakpoints, mapped to the
   project's existing responsive tokens or media queries.
3. **Plan the structure.** Decide reusable component, custom hook, or page-specific
   code; define typed props and hook signatures with sensible defaults; place state
   using the state framework in the reference below; search for existing similar
   components and hooks and extend or compose rather than duplicate. A module move
   lists every importer it will rewrite.
4. **Implement.** Composition patterns (children/slots, render delegation, compound
   components) over prop sprawl; explicit prop types co-located in
   `ComponentName.types.ts`; named exports and named `react` imports; the
   framework's error-boundary mechanism around data-dependent sections; the three
   UI states; tokens for every visual value.
5. **Organize modules.** Barrels only at public API boundaries; after a move, no
   importer points at the old path and the old file is gone — rules in the
   reference below.
6. **Verify.** Run the project's type check and linter. For a design-backed task, if
   the calling workflow provides a verification loop (a UI verification gate run by
   the orchestrator), defer to it — do not duplicate verification here. Otherwise,
   compare the rendered result against the Figma design yourself and walk through
   each interaction state, iterating until it matches within tolerance.

## Component Checklist

The same list is the frontend review checklist: when reviewing a frontend change,
check the diff against it and the Non-negotiable Rules above.

```text
- [ ] Single responsibility — one clear purpose
- [ ] Typed props — explicit types, sensible defaults
- [ ] Named export — no default exports
- [ ] Named react imports — no React namespace, no React.FC
- [ ] Design tokens — no hardcoded visual values
- [ ] Error state — handles failure gracefully
- [ ] Loading state — shows progress indicator
- [ ] Empty state — meaningful message when no data
- [ ] Composition — uses children/slots, not prop sprawl
- [ ] Modules — barrels only at public boundaries, no pass-through files after a move
```

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Component guidelines](./references/component-guidelines.md) | Deciding where state lives, adding a barrel file, moving or splitting modules, or reviewing for anti-patterns | The state decision framework, barrel-file details, the anti-pattern table |
| [React patterns](./references/react-patterns.md) | Before writing or reviewing React code | How React implements the composition, state, error-handling, and performance patterns above, plus the lint rule that enforces the import style |

## Related Skills

- [`configuring-typescript-for-frontend`](../configuring-typescript-for-frontend/SKILL.md)
  — the compiler setup underneath these components.
- [`ensuring-accessibility`](../ensuring-accessibility/SKILL.md) — the a11y patterns
  every component here must also satisfy.
- UI verification against Figma (capture, tolerances, PASS gates) lives in the
  `tsh-product-engineering` plugin (`reviewing-ui` and its agents), which may not be
  installed — name the gap rather than improvising verification here.
