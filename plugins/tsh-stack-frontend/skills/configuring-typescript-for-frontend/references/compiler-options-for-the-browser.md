# TypeScript Compiler Options for the Browser

Use this reference when writing or reviewing a `tsconfig.json` for code that ships
to a browser. Read it before editing one.

The governing difference from a server config: **the bundler owns the output**.
TypeScript is a checker here, not a build step, which changes what several options
are for and makes one of them (`noEmit`) close to mandatory.

## Contents

- [The Baseline Config](#the-baseline-config)
- [Who Owns Emit](#who-owns-emit)
- [Strictness](#strictness)
- [Beyond `strict`](#beyond-strict)
- [Target, Lib, Module, and Resolution](#target-lib-module-and-resolution)
- [JSX](#jsx)
- [Ambient Types and Bundler Globals](#ambient-types-and-bundler-globals)
- [Options That Change Behavior](#options-that-change-behavior)
- [Type-checking Is Not Building](#type-checking-is-not-building)

## The Baseline Config

For a new bundler-driven app. In a Vite project this is the *app* half of a
two-config layout — see [`react-vite-project.md`](./react-vite-project.md) for the
whole shape.

```jsonc
{
  "compilerOptions": {
    // Language and environment — the browser, not Node.
    "target": "es2023",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "types": ["vite/client"],
    "jsx": "react-jsx",

    // Correctness.
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,

    // The bundler emits; TypeScript only checks.
    "noEmit": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,

    // Ergonomics.
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

Notes on entries that are easy to get wrong:

- **`DOM.Iterable`** is only needed on TypeScript `5.x`. From 6.0 the `dom` lib
  includes it (and `dom.asynciterable`) by default; leaving it listed is harmless.
- **`skipLibCheck: true`** is a pragmatic default, not a correctness one. It hides
  real conflicts between competing `@types` versions — turn it off temporarily when
  a type error seems to come from nowhere, which in a React app usually means two
  `@types/react` versions in the tree.
- **`verbatimModuleSyntax: true`** is unambiguously correct here, and worth
  contrasting with a server config: it is only dangerous alongside
  `emitDecoratorMetadata`, which browser code does not use. It forces the
  `import type` distinction to be explicit, which is exactly what a
  transpile-per-file bundler needs.
- **`strict`, `target`, `types`, and `module` are written out** even where a modern
  compiler defaults to them. TypeScript 6.0 changed all four defaults; a config
  that states them survives the upgrade instead of silently acquiring new behavior.

## Who Owns Emit

| Severity | Rule |
| --- | --- |
| MUST | Set `noEmit: true` when a bundler produces the output. Two tools writing JavaScript into one tree produces stale artifacts that are extremely hard to reason about. |
| MUST | Pair `allowImportingTsExtensions` with `noEmit` (or `emitDeclarationOnly`). The compiler rejects the combination otherwise, and the flag only makes sense when nothing is emitted. |
| NEVER | Add `outDir` to a browser app config. If you find one, the repo probably has a leftover `tsc` build nobody runs. |
| PREFER | `declaration` only in a shared package another workspace type-checks against, never in an app. |

## Strictness

`strict` is an umbrella that currently enables `noImplicitAny`,
`strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`,
`strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`,
and `alwaysStrict`.

| Severity | Rule |
| --- | --- |
| MUST | Set `strict: true` in new projects. It is the default from TypeScript 6.0; state it anyway. |
| MUST | For a legacy codebase that cannot flip it at once, enable the sub-flags one at a time, land each with its fixes, and track the remaining gap somewhere visible. |
| NEVER | Disable a strict sub-flag to make a specific file compile. Fix the file, or isolate it with a narrowly scoped `@ts-expect-error` and a comment. |
| AVOID | `strictNullChecks: false`. It is by far the most valuable of the group, and the hardest to enable later — every additional month of code written without it deepens the eventual migration. |

For the order to enable these in an existing codebase, see
[`adopting-in-a-brownfield-project.md`](./adopting-in-a-brownfield-project.md).

## Beyond `strict`

These are not included in `strict` and are worth enabling deliberately.

| Option | What it catches | Cost |
| --- | --- | --- |
| `noUncheckedIndexedAccess` | `arr[i]` and `record[key]` returning `T` when the index may not exist. The single highest-value flag outside `strict`. | Noisy at first; adds `??` and guards at every index access. |
| `exactOptionalPropertyTypes` | `{ a?: string }` being assigned an explicit `undefined`, which is a different thing from absent. Surfaces often in component props. | Friction with libraries whose prop types are loose about it. |
| `noImplicitOverride` | A method that shadows a base method without saying so. | Low — add the `override` keyword. |
| `noFallthroughCasesInSwitch` | A missing `break`, including in reducers. | Low. |
| `noPropertyAccessFromIndexSignature` | `env.SOME_KEY` on an index-signature type where the key was never declared. | Forces bracket access for dynamic keys; a readability trade. |
| `noUnusedLocals` / `noUnusedParameters` | Dead bindings. Present in the Vite template, so many projects inherit them. | Fights you mid-refactor. Better handled by the linter, which can fix and scope per-rule. |

## Target, Lib, Module, and Resolution

**`target`** decides which syntax is downlevelled. In a bundled app this matters
less than it looks: the bundler applies its own browser-targeting pass (Vite's
`build.target`, esbuild's `target`, or Babel with a browserslist), and that is what
determines what actually ships. Keep `target` high — the bundler is the authority
on browser support, and downlevelling twice only produces worse output.

| Severity | Rule |
| --- | --- |
| MUST | Set browser support in the bundler's config and browserslist, not in `tsconfig.json`. `target` here governs what the checker accepts and what a stray `tsc` emit would produce. |
| MUST | Keep `lib` and `target` consistent with each other, and include `DOM`. A frontend config without `DOM` in `lib` reports `document` as undefined. |
| NEVER | Add `types: ["node"]` to an app config to silence an error about `process`. That types Node APIs the browser does not have. Use `import.meta.env`, or move the file to the build-time config. |

**`module` and `moduleResolution`** must match whoever resolves the imports:

| Who resolves | `module` | `moduleResolution` |
| --- | --- | --- |
| A bundler (Vite, webpack, Rspack) | `esnext` / `preserve` | `bundler` |
| Node, for build-time files | `nodenext` | `nodenext` |

| Severity | Rule |
| --- | --- |
| MUST | Use `bundler` for app source. It models what bundlers actually do, including extensionless imports and `exports` maps. |
| NEVER | Use `moduleResolution: node`/`node10`. Deprecated in TypeScript 6.0 and removed in 7.0, and wrong for modern packages before that. |
| MUST | Put files Node executes directly — `vite.config.ts`, codegen scripts, `*.config.ts` — in a separate config with Node resolution. `bundler` mode lets them import in ways Node will reject. |
| MUST | Set `moduleDetection: "force"` so every file is treated as a module. Without it, a file with no imports or exports becomes a global script and its top-level names collide. |

## JSX

| Option | Value | Why |
| --- | --- | --- |
| `jsx` | `react-jsx` | The automatic runtime. No `import React` needed in every file; `react-jsxdev` is selected by the dev build, not by you. |
| `jsx` | `preserve` | Only when another tool consumes the JSX afterwards — a meta-framework, or Babel with its own plugins. |

`jsx: react` (the classic runtime) is legacy. Migrating off it is mostly deleting
now-unused `import React from 'react'` lines, and the linter can find them.

For React specifically, `@types/react` and `@types/react-dom` must be on matching
majors, and duplicates in the dependency tree cause "two different `ReactNode`
types" errors — check with `npm ls @types/react`.

## Ambient Types and Bundler Globals

A bundler injects values TypeScript cannot see: `import.meta.env`, imported asset
URLs, `?raw` and `?worker` query suffixes, hot-module-reload handles. These are
typed by the bundler's own declaration package plus a `.d.ts` the project owns.

| Severity | Rule |
| --- | --- |
| MUST | Set `types` explicitly. Unset, every `@types/*` package in the tree is in scope — including Node globals and test globals in production source. TypeScript 6.0 changed the default to `[]`, so an unset `types` behaves differently across majors. |
| MUST | Declare project-specific environment variables in an interface the project owns, rather than casting `import.meta.env` at each use. One declaration types every call site. |
| MUST | Keep test-only globals out of the app config. Add them in the config that covers tests. |

See [`react-vite-project.md`](./react-vite-project.md) for the concrete
`vite-env.d.ts` shape.

## Options That Change Behavior

Most frontend config changes are type-only, and the exceptions are worth knowing.

**`verbatimModuleSyntax`** — emits imports exactly as written and drops
`import type`. In a browser project this is what you want. Its one real hazard is
a side-effect import that gets marked type-only by an over-eager auto-import or by
`@typescript-eslint/consistent-type-imports`, which then silently stops running the
module's side effects. `noUncheckedSideEffectImports` (default `true` from 6.0)
catches the related case of importing a module that has no types at all.

**`isolatedModules`** — guarantees every file can be transpiled independently,
which is exactly what esbuild and SWC do. Not optional in a bundled project; the
bundler already behaves this way, and the flag makes the compiler agree.

**`useDefineForClassFields`** — follows `target`, and standards-correct (`true`) is
the right choice in browser code. It only needs pinning in a project using
decorator-based class fields (MobX's older decorator API, Angular), where the
`defineProperty` semantics wipe values set elsewhere.

**`target` and `lib` mismatch** — raising `lib` without raising `target` type-checks
newer APIs while emitting older syntax. That is a legitimate combination when a
polyfill supplies the API, and a bug when nothing does.

## Type-checking Is Not Building

This is the most consequential difference between a frontend and a server setup,
and the most commonly missed.

Vite does **not** type-check. Neither does esbuild, SWC, or Babel. They strip
types and emit JavaScript without reading your strictness settings. A project can
ship type errors indefinitely while every build passes green.

| Severity | Rule |
| --- | --- |
| MUST | Run a real type-check as its own CI step: `tsc -b` for a project-references layout, `tsc --noEmit` for a single config. |
| MUST | Fail CI on that step. A type-check that runs but doesn't gate is decoration. |
| MUST | Include the build-time config in what gets checked. `tsc -b` on the root config covers every referenced project; a bare `tsc --noEmit` checks only one. |
| PREFER | Wiring it into the `build` script as well (`tsc -b && vite build`), so a local build fails the same way CI does. |
| AVOID | Relying on the editor as the gate. It checks open files, sometimes against different settings. |

Framework-specific checkers replace `tsc` rather than supplement it: `vue-tsc` for
Vue, `svelte-check` for Svelte, `astro check` for Astro. They exist because the
compiler cannot see types inside template syntax — use them where they apply.
