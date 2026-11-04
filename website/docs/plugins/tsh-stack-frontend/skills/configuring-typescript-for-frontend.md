---
title: Configuring TypeScript for Frontend
sidebar_label: configuring-typescript-for-frontend
sidebar_position: 1
description: TSH's TypeScript setup for browser-targeted code, covering the version to pin, the tsconfig baseline for a bundler-resolved app and the React + Vite layout.
sources:
  - plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend/SKILL.md
  - plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend/references/
sources_hash: "100c4f4238de831e3613031765998353e3bb52cf7f908add86d2b68ac2f512c0"
---

# Configuring TypeScript for Frontend

**Plugin:** [`tsh-stack-frontend`](/docs/plugins/tsh-stack-frontend/)  
**Invoke:** `/tsh-stack-frontend:configuring-typescript-for-frontend` (Claude also loads it when the work matches its description)  
**Used by:** no agent loads it. [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) lists it as a related skill and defers compiler setup to it

TSH's recommended TypeScript setup for code that runs **in a browser**: which version to pin, the `tsconfig.json` baseline for a bundler-resolved app, and the React + Vite project layout. The skill is about **configuration**. Type modelling (unions, branded types, `unknown` over `any`), component patterns, state management and styling are out of scope, and so is Node-targeted server code, which resolves modules differently and is compiled as a separate project.

Its frontmatter declares `paths` globs: `**/*.tsx`, `**/tsconfig*.json`, `**/vite.config.*` and `**/*.ts`.

## The rule it exists to enforce

**Vite does not type-check.** `vite build` runs esbuild and Rollup, which strip types without reading them, so a frontend repo can ship type errors indefinitely while every build passes green. A real type-check as its own CI step that fails the pipeline (`tsc -b`, or `tsc --noEmit` on a single config) is the first thing the skill checks, before any flag tuning.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Version policy** | Pin an exact TypeScript version in `devDependencies`, because TypeScript does not follow semver. Upgrade in its own PR, one minor at a time, and never fix an error wave by loosening `tsconfig` |
| **Baseline config** | `target: es2023`, `module: esnext`, `moduleResolution: bundler`, `jsx: react-jsx`, `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noEmit`, `isolatedModules`, `verbatimModuleSyntax`, with `strict`, `target`, `types` and `module` written out explicitly |
| **Emit ownership** | `noEmit: true` when a bundler owns the output, `allowImportingTsExtensions` only alongside it, no `outDir` in an app config |
| **Strictness** | `strict` is always on; progressive enabling of the sub-flags for legacy code; `strictNullChecks: false` is the one to avoid |
| **Module resolution** | `bundler` for app source; build-time files that Node executes, such as `vite.config.ts`, go in a separate config with Node resolution. `moduleResolution: node` is never left in a frontend project |
| **Split-config layout** | Root `tsconfig.json` with `files: []` and references to `tsconfig.app.json` and `tsconfig.node.json`, each with its own `tsBuildInfoFile` |
| **Bundler globals** | `types` set explicitly, `vite/client`, project-specific variables declared once in `src/vite-env.d.ts`, `VITE_` prefix, no `process.env` in app source |
| **Path aliases** | Mirrored in both `tsconfig` `paths` and the bundler's resolver, or generated from one source, with no `baseUrl` |
| **React types** | `@types/react` and `@types/react-dom` on the same major as `react`, deduplicated when errors mention two incompatible `ReactNode` types |
| **Brownfield adoption** | The baseline is a recommendation for new projects. Existing repos get the smallest staged change, with the type gate going in before strictness increases |

## Version baseline

The concrete layout is written against **Vite 8 and React 19** with TypeScript in the `6.x` line, which is what `create-vite`'s React + TypeScript template currently ships. The skill notes that `7.x` is the latest stable TypeScript line, so the template is deliberately one major behind. Earlier Vite majors and TypeScript `5.x` are supported by the principles, but the file layout and several defaults differ. For Vue, Svelte, Angular or Next.js, the compiler-option guidance applies and the Vite-specific layout is illustrative only.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Treat the baseline as a recommendation for new projects; in an existing repo propose the smallest staged change and never rewrite a working `tsconfig.json` wholesale |
| MUST | Run a real type-check in CI as its own step |
| MUST | Enable `strict`; a project that cannot do it wholesale enables the flags progressively and records the gap |
| MUST | Pin an exact TypeScript version, with no `^` |
| MUST | Use `moduleResolution: bundler` only where a bundler resolves the imports |
| NEVER | Leave `moduleResolution: node` or `node10` in a frontend project |
| MUST | Set `noEmit: true` when a bundler owns the output |
| MUST | Mirror every `paths` alias in the bundler's resolver |
| MUST | Declare bundler-injected globals in a `.d.ts` the project owns |
| MUST | Treat a `@ts-expect-error` as debt, with a comment on the cause and the condition for removal; prefer it over `@ts-ignore` |

## How it works

1. **Read the ground truth**: every `tsconfig*.json`, how they relate, and `package.json` for the TypeScript pin, framework and bundler majors, and whether a type-check runs in the build, lint or CI scripts.
2. **Decide greenfield or brownfield.** A new project takes the baseline as written.
3. **Load the relevant references** before editing any `tsconfig.json`, and before adding or splitting a config in a Vite project.
4. **Check the type gate first.** Strictness is worth nothing if nothing runs the compiler.
5. **Apply the smallest change**, and say explicitly when a change affects the bundler's behaviour and not just type checking.
6. **Verify**: type-check, build and tests, and load the app in a browser after any change to `target`, `lib` or the config split.

## References

| Reference | Loaded when |
| :-- | :-- |
| Compiler options for the browser | Writing or reviewing a frontend `tsconfig.json` |
| React + Vite project | The project is built with Vite, or needs a second config for build-time files |
| Version and upgrades | Choosing, justifying or raising the TypeScript version |
| Adopting in a brownfield project | The repo already has a working config that differs from the baseline |

Two details from the version reference that decide real cases:

- **TypeScript 7.0 and embedded languages.** The 7.0 native compiler does not support embedded language tooling (Vue, Svelte, Astro, MDX, Angular templates), so such projects stay on `6.x` until their tooling states 7.0 support. `7.x` is preferred for React, Preact, Solid and plain-DOM projects.
- **TypeScript 6.0 changed defaults.** `strict` became `true`, `types` became `[]`, and `moduleResolution: node`, `baseUrl` and several other options are deprecated ahead of removal in 7.0. Writing `strict`, `target`, `module` and `types` out explicitly before crossing into 6.0 turns the default change into a no-op.

## Related skills and near-twins

- [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend): the component and module conventions on top of this compiler setup.
- **Near-twins.** [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) in `tsh-stack-nodejs` and [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) in `tsh-stack-serverless` carry the same version policy and strictness ladder on purpose, because skills cannot link across plugins. The target-specific parts differ.
- `tsh-product-engineering` is named in the skill as an optional discipline-level companion, never a prerequisite.

The skill does not configure Node or server builds, bundler plugins beyond what typing requires, linting, formatting or testing frameworks.

## Source

[`plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend/SKILL.md)
