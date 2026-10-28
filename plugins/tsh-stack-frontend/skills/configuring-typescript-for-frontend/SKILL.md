---
name: configuring-typescript-for-frontend
description: "Configures TypeScript for browser-targeted frontend projects: which version to pin, the tsconfig baseline for a bundler-resolved app, and the React + Vite project layout. Use when starting a frontend project, editing a frontend tsconfig, diagnosing JSX or module-resolution errors, or upgrading TypeScript in a browser app."
when_to_use: "Trigger on: setting up tsconfig.json for a React or Vite app, moduleResolution bundler questions, jsx or DOM lib errors, a separate tsconfig for vite.config.ts, typing import.meta.env, path aliases that resolve in the editor but not in the build, a build that ships type errors because Vite only transpiles, or an upgrade of the pinned TypeScript version in a frontend repo."
paths:
  - "**/*.tsx"
  - "**/tsconfig*.json"
  - "**/vite.config.*"
  - "**/*.ts"
---

# Configuring TypeScript for Frontend

TSH's recommended TypeScript setup for code that runs **in a browser**: which
version to pin, the `tsconfig.json` baseline for a bundler-resolved app, and the
React + Vite project layout.

This skill is about **configuration**. How to model types — unions, branded types,
`unknown` over `any` — is out of its scope, as are component patterns, state
management, and styling. Node-targeted server code is out of scope too: it resolves
modules differently and needs its own config, so a repo with both compiles them as
separate projects.

## When to Use

- Setting up `tsconfig.json` for a new frontend app, or reviewing an existing one
- Choosing the TypeScript version for a frontend project, or justifying the pinned one
- Deciding `target`, `lib`, `module`, and `moduleResolution` for a bundled app
- Adding the second config that covers `vite.config.ts` and other build-time files
- Typing `import.meta.env`, static asset imports, or other bundler-provided globals
- Fixing a path alias that type-checks but fails to resolve at build time
- Upgrading TypeScript and triaging the resulting errors

## Version Baseline

The concrete layout in this skill is written against **Vite 8 + React 19** with
TypeScript in the `6.x` line, which is what `create-vite`'s React + TypeScript
template currently ships. Note that `7.x` is the latest stable TypeScript line, so
the template is deliberately one major behind — see
[`typescript-version-and-upgrades.md`](./references/typescript-version-and-upgrades.md)
for why that gap exists and when to close it. Read the target repository's
`package.json` before applying anything here.

Earlier Vite majors, and TypeScript `5.x`, are fully supported by the *principles*
here — but the file layout and several defaults differ, so check the versions in
play before copying any config verbatim. For a project on Vue, Svelte, Angular, or
Next.js, treat the compiler-option guidance as applicable and the Vite-specific
layout as illustrative only.

## Applicability and Precedence

Read the target repository's `tsconfig.json` (and anything it extends),
`package.json`, and bundler config before proposing anything. **Local conventions
outrank this skill's defaults.** Apply this guidance where the repository is
silent, and record a deliberate deviation rather than silently mixing conventions.

**The baseline below is a recommendation for new projects, not a verdict on
existing ones.** A working `tsconfig.json` that differs from it is not a defect.
In an existing repo, propose the smallest staged change that serves the task at
hand and read
[`adopting-in-a-brownfield-project.md`](./references/adopting-in-a-brownfield-project.md)
before proposing anything wider.

Framework requirements outrank this skill. A meta-framework that owns its own
config — Next.js, Angular, SvelteKit, Nuxt — wins for the files it generates;
do not hand-edit fields the framework manages.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Treat this baseline as a recommendation for new projects. In an existing repo, propose the smallest staged change and record the remaining gap — never rewrite a working `tsconfig.json` wholesale to match this skill. |
| MUST | Run a real type-check in CI as its own step (`tsc -b`, or `tsc --noEmit` on a single-config project). Vite, esbuild, and SWC **strip types without checking them** — a green `vite build` proves nothing about type correctness. |
| MUST | Enable `strict`. A project that cannot turn it on wholesale enables the individual flags progressively and records the remaining gap — never ships `strict: false` as a permanent state. |
| MUST | Pin an exact TypeScript version in `devDependencies` (no `^`). TypeScript does not follow semver — patch and minor releases add errors to previously compiling code. |
| MUST | Use `moduleResolution: bundler` only where a bundler actually resolves the imports. Build-time files that Node executes directly — `vite.config.ts`, scripts — belong in a separate config with a Node resolution mode. |
| NEVER | Leave `moduleResolution: node`/`node10` in a frontend project. It predates `package.json` `exports`, resolves the wrong entry point for modern packages, and TypeScript 6.0 deprecates it (it errors unless `ignoreDeprecations: "6.0"` is set) ahead of removal in 7.0. |
| MUST | Set `noEmit: true` when a bundler owns the output. `allowImportingTsExtensions` is only legal alongside it, and two tools emitting into the same tree is a debugging trap. |
| MUST | Mirror every `paths` alias in the bundler's own resolver (or generate both from one source). `tsc` rewrites nothing — an unmirrored alias type-checks and then fails at build or run time. |
| MUST | Declare bundler-injected globals in a `.d.ts` the project owns — `import.meta.env`, asset imports, `vite/client`. Reaching for `any` because "the bundler provides it" discards the one place those values can be typed. |
| MUST | Treat a `@ts-expect-error` as debt: it carries a comment explaining the cause and the condition for removal. Prefer it over `@ts-ignore`, which silently rots when the error disappears. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Compiler options for the browser](./references/compiler-options-for-the-browser.md) | Writing or reviewing a frontend `tsconfig.json` | The baseline config, strictness ladder, `target`/`lib`/`module`/`moduleResolution` for a bundled app, `jsx`, `types`, emit ownership |
| [React + Vite project](./references/react-vite-project.md) | The project is built with Vite, or needs a second config for build-time files | The split-config layout, `tsc -b` as the type gate, `vite/client` and `import.meta.env` typing, path aliases, React-specific options |
| [Version and upgrades](./references/typescript-version-and-upgrades.md) | Choosing, justifying, or raising the TypeScript version | Version policy, what each recent major added, the 6.0 default changes, the 7.0 native compiler and its frontend caveats, upgrade procedure and triage |
| [Adopting in a brownfield project](./references/adopting-in-a-brownfield-project.md) | The repo already has a working config that differs from the baseline | Staged adoption order, ratcheting, per-flag sequencing, recording a deviation, when to leave a config alone |

## Procedure

**Step 1 — Read the ground truth.** Open every `tsconfig*.json` in the repo and
note how they relate (a root config with `references`, a single flat config, or a
framework-generated one). Read `package.json` for the pinned TypeScript version,
the framework and bundler majors, and whether a real type-check runs in the
`build`, `lint`, or CI scripts.

**Step 2 — Decide greenfield or brownfield.** A new project takes the baseline as
written. An existing project gets the smallest staged change — read
[`adopting-in-a-brownfield-project.md`](./references/adopting-in-a-brownfield-project.md)
first.

**Step 3 — Load the relevant references.** Read
[`compiler-options-for-the-browser.md`](./references/compiler-options-for-the-browser.md)
before editing any `tsconfig.json`, and
[`react-vite-project.md`](./references/react-vite-project.md) before adding or
splitting a config in a Vite project.

**Step 4 — Check the type gate first.** Before tuning flags, confirm a real
type-check runs and fails the build. Strictness is worth nothing if nothing runs
the compiler; this is the single most common gap in a frontend repo.

**Step 5 — Apply the smallest change.** Prefer the narrowest edit that achieves
the goal. Say explicitly when a change affects the bundler's behavior and not just
type checking.

**Step 6 — Verify.** Run the type-check, the build, and the test suite. Load the
app in a browser after any change to `target`, `lib`, or the config split: a
passing type-check does not prove the bundle still runs.

## Related Skills

- `tsh-product-engineering` — TSH's discipline-level implementation and review
  workflows, independent of language. Optional; treat it as a bonus, never a
  prerequisite.

This skill configures the TypeScript compiler only. It does not configure Node or
server builds, does not set up bundler plugins beyond what typing requires, and
does not cover type modelling, linting, formatting, or testing frameworks.
