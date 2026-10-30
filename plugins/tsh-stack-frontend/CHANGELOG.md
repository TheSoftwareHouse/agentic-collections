# Changelog

All notable changes to `tsh-stack-frontend` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.3.0] - 2026-10-30

### Changed

- **`implementing-frontend` now covers every change to frontend code, not only
  Figma-backed components.** Its description used to name components, Figma and
  design tokens, so a custom hook, a refactor or a module move never loaded it and
  the agent fell back to its own habits. It now claims any frontend change, with or
  without a design: the Figma gate applies only when the task has a design reference,
  and the procedure has a path for work that has none.
- **Named imports from `react` are a non-negotiable rule.** `import * as React`,
  `React.useState` and `React.FC` were not covered anywhere, and the React reference
  itself used `React.memo` and `React.lazy`. The rule sits in `SKILL.md`, the
  reference shows the named form, and it carries an ESLint `no-restricted-syntax`
  rule the agent proposes — and adds only once the team agrees — to enforce it. A
  codebase that already uses the namespace style consistently keeps it.
- **No pass-through files after a module move.** The barrel rules moved from a
  reference into `SKILL.md`, because the reference loaded only "when adding a barrel
  file" and a module move never matched. A file left at the old path that only
  re-exports the new one is now named as a shim to delete, not a barrel to keep.
- **A React version policy.** The skill follows the version `package.json` pins; a
  greenfield app installs the latest stable React, and a major newer than 19 is
  checked against the current documentation through `context7`, which `tsh-core`
  bundles.
- **The code-splitting example fits the named-exports rule.** `lazy` needs a default
  export, so the example now maps the named export with `.then`.

## [0.2.2] - 2026-10-02

### Fixed

- **TypeScript 6.0 facts.** `configuring-typescript-for-frontend` said 6.0
  "removed" `moduleResolution: node`/`node10`, `target: es5`, `downlevelIteration`,
  `outFile` and the legacy module kinds, in the rules table and two references. 6.0
  deprecates them behind `ignoreDeprecations: "6.0"`; the removals land in 7.0.
  Corrected in step with the same fix in `tsh-stack-nodejs` 0.1.1.

## [0.2.1] - 2026-09-21

### Changed

- **The README now says where the Figma MCP server comes from: `tsh-core` 0.10.0
  bundles it.** `implementing-frontend` has always made the design read a hard gate
  before the first line of markup, without ever saying which server satisfies it —
  and until now no plugin in this marketplace shipped one. A new **Assumes tsh-core**
  section covers the install, the one-per-machine `/mcp` sign-in, and why the server
  is not bundled here: this is a `project`-scope plugin, so hosting it would leave
  every repository that does not install it — including ones running
  `tsh-product-engineering`'s UI verification gate — with no design source.
- No skill content changed.

## [0.2.0] - 2026-08-26

### Added

- **`implementing-frontend`** — component implementation patterns migrated from
  `copilot-collections` (`tsh-implementing-frontend`): composition over prop sprawl,
  design tokens over hardcoded values, typed props and named exports, the three UI
  states for data-dependent components, barrel-file rules, and the Figma-to-code
  workflow whose first step — reading the design through the Figma MCP before the
  first line of markup — is a hard gate. Framework-agnostic core with a React
  reference. This closes the "component patterns" gap the README listed since 0.1.0.
- **`ensuring-accessibility`** — WCAG 2.1 AA implementation patterns migrated from
  `copilot-collections` (`tsh-ensuring-accessibility`): semantic HTML first,
  per-widget keyboard maps, focus management, ARIA only where HTML falls short,
  contrast minimums, zoom/reflow criteria, RTL rules, and an axe-core CLI
  verification step. Implementation-time patterns only — auditing an existing page
  stays with `tsh-product-testing`'s `auditing-accessibility`, and both skills name
  each other so they don't compete for the same request.
- Both skills support the frontend flow in `tsh-product-engineering` 0.7.0 (the
  `ui-engineer` + UI verification gate), but stand alone: they reference that plugin
  by name only, never by path, and work without it.

## [0.1.0] - 2026-08-12

Initial release. This plugin is one half of the split of `tsh-stack-typescript`,
which has been removed: a stack is now a **runtime target**, not a language. Most
TSH projects have a frontend whatever their backend is written in, so browser-side
guidance had to be installable on its own.

### Added

- `configuring-typescript-for-frontend`, covering the `tsconfig.json` baseline for a
  bundler-resolved browser app: `moduleResolution: bundler`, `jsx: react-jsx`,
  `lib: DOM`, emit owned by the bundler, explicit ambient `types`, and the
  strictness ladder.
- A `react-vite-project.md` reference for the split-config layout — a root config
  with `references`, a browser `tsconfig.app.json`, and a Node-resolved
  `tsconfig.node.json` for `vite.config.ts` — plus typing `import.meta.env` and asset
  imports, mirroring path aliases between the checker and the bundler, `@types/react`
  duplication, and adding a test-only project. Written against Vite 8 + React 19 and
  verified against `create-vite`'s current template.
- **A real type-check as a non-negotiable rule.** Vite, esbuild, and SWC strip types
  without checking them, so a frontend repo can ship type errors indefinitely while
  every build passes green. The skill treats getting a failing `tsc -b` into CI as
  the first thing to fix, ahead of any flag tuning, and the brownfield reference has
  a staged procedure for turning that gate on in a repo that has never had one.
- A brownfield posture stated as a non-negotiable rule: the baseline is a
  recommendation for new projects, and an existing `tsconfig.json` that differs from
  it is not a defect. Framework-managed configs (Next.js, Angular, Nuxt) are left
  alone.
- Version and upgrade guidance reflecting **TypeScript 6.0 and 7.0**, including the
  frontend-specific constraint that 7.0's native compiler does **not** support
  embedded-language tooling — Vue, Svelte, Astro, MDX, and Angular templates still
  require the 6.0 line, and `vue-tsc`/`svelte-check` are the real gate for those
  projects.

### Notes

Version policy, the strictness ladder, the upgrade procedure, and the brownfield
adoption material are duplicated from `tsh-stack-nodejs` on purpose: a skill cannot
read files in another plugin, so shared knowledge has to be co-located. The
target-specific parts are genuinely different, and are meant to stay that way. When
one copy changes, check the other.
