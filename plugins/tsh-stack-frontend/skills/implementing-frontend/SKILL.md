---
name: implementing-frontend
description: "Frontend component implementation patterns for browser apps: composition over prop sprawl, design tokens over hardcoded values, the Figma-to-code workflow with a mandatory design read before the first line of markup, typed props, barrel-file rules, and the three UI states every data-dependent component handles. Use when implementing UI components, translating a Figma design into code, or integrating with a design system."
when_to_use: "Trigger on: implementing or restructuring UI components, translating Figma designs into code, choosing where component state lives, wiring design tokens, organizing component modules and barrel files, or handling loading/error/empty states. Compiler setup is configuring-typescript-for-frontend; a11y implementation patterns are ensuring-accessibility."
---

# Implementing Frontend

Patterns for building reusable, composable frontend components with design-system
integration and a structured Figma-to-code workflow.

## Applicability and Precedence

Local repository rules outrank this skill: the project's existing component
patterns, design system, and styling approach win over the defaults here. These
patterns are framework-agnostic; load the framework reference below for the
project's framework.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | For a Figma-backed task, fetch and study the design through the Figma MCP before writing or editing any markup, layout, or styling. This pre-implementation design read is a hard gate, distinct from any post-implementation verification loop. |
| NEVER | Implement from assumptions. Design context, tokens, or specs missing or unclear → stop and raise it (as a subagent, report the blocker to the caller; in the main conversation, ask the user). Missing information produces wrong UI; asking produces correct UI. |
| MUST | Take every visual value (colors, spacing, typography, shadows, radii) from the project's design system tokens. No exact token match → use the closest existing token and document the deviation; a genuinely new value → flag it and ask before creating a token. |
| NEVER | Use `export default`, untyped or `any` props, or a component with more than ~7 props where composition (children, slots, compound components) would do. |
| MUST | Handle all three UI states in every data-dependent component: loading (progress indicator), error (meaningful message plus recovery action), empty (helpful message when no data). |
| MUST | Declare what the UI looks like from state; never imperatively manipulate the DOM. Compose complex UIs from small, single-responsibility components. |

## Implementation Process

1. **Fetch and review the Figma design** (Figma-backed tasks — the gate above).
   Resolve the node, export the node image via the Figma MCP, and extract layout,
   spacing, typography, colors, dimensions, variants, and states.
2. **Gather design context.** Map every Figma value to an existing design token:
   extract the raw value → search the codebase for a matching token → use it; no
   exact match → closest token plus a documented deviation; truly new → ask first.
   Identify every state the design implies (default, hover, focus, active,
   disabled, loading, error, empty) and the responsive breakpoints, mapped to the
   project's existing responsive tokens or media queries.
3. **Plan component structure.** Decide reusable component vs page-specific layout;
   define the typed props interface with sensible defaults; place state using the
   state framework in the reference below; search for existing similar components
   and extend or compose rather than duplicate; sketch the component tree and where
   state lives.
4. **Implement.** Composition patterns (children/slots, render delegation, compound
   components) over prop sprawl; explicit prop types co-located in
   `ComponentName.types.ts`; named exports only; the framework's error-boundary
   mechanism around data-dependent sections; the three UI states; tokens for every
   visual value.
5. **Organize modules.** Barrel `index.ts` files only at public API boundaries, with
   named re-exports — rules in the reference below.
6. **Verify.** If the calling workflow provides a verification loop (a UI
   verification gate run by the orchestrator), defer to it — do not duplicate
   verification here. Otherwise, compare the rendered result against the Figma
   design yourself and walk through each interaction state, iterating until it
   matches within tolerance.

## Component Checklist

```text
- [ ] Single responsibility — one clear purpose
- [ ] Typed props — explicit types, sensible defaults
- [ ] Named export — no default exports
- [ ] Design tokens — no hardcoded visual values
- [ ] Error state — handles failure gracefully
- [ ] Loading state — shows progress indicator
- [ ] Empty state — meaningful message when no data
- [ ] Composition — uses children/slots, not prop sprawl
```

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Component guidelines](./references/component-guidelines.md) | Deciding where state lives, adding a barrel file, or reviewing for anti-patterns | The state decision framework, barrel-file rules, the anti-pattern table |
| [React patterns](./references/react-patterns.md) | The project uses React | How React implements the composition, state, error-handling, and performance patterns above |

## Related Skills

- [`configuring-typescript-for-frontend`](../configuring-typescript-for-frontend/SKILL.md)
  — the compiler setup underneath these components.
- [`ensuring-accessibility`](../ensuring-accessibility/SKILL.md) — the a11y patterns
  every component here must also satisfy.
- UI verification against Figma (capture, tolerances, PASS gates) lives in the
  `tsh-product-engineering` plugin (`reviewing-ui` and its agents), which may not be
  installed — name the gap rather than improvising verification here.
