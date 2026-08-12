# React + Vite Project Configuration

Use this reference when the project is built with Vite, when it needs a second
config for build-time files, or when a path alias, `import.meta.env`, or an asset
import will not type-check.

Everything below is TSH's recommendation, and Vite's own template is the starting
point rather than a competitor to it. Where they differ, this file says so.

## Contents

- [The Split-Config Layout](#the-split-config-layout)
- [Why Two Configs](#why-two-configs)
- [The Type Gate](#the-type-gate)
- [Bundler Globals and `vite-env.d.ts`](#bundler-globals-and-vite-envdts)
- [Path Aliases](#path-aliases)
- [React Type Packages](#react-type-packages)
- [Adding a Test Config](#adding-a-test-config)
- [Verifying Against the Template](#verifying-against-the-template)

## The Split-Config Layout

`create-vite`'s React + TypeScript template ships three files, and the shape is
worth keeping:

```text
tsconfig.json           # no files of its own; references the other two
tsconfig.app.json       # browser source, bundler-resolved
tsconfig.node.json      # build-time files Node executes
```

The root config owns nothing and delegates:

```jsonc
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

The app config, as the template ships it (Vite 8, React 19, TypeScript `6.x`):

```jsonc
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "es2023",
    "lib": ["ES2023", "DOM"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "types": ["vite/client"],
    "jsx": "react-jsx",
    "moduleDetection": "force",
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "allowArbitraryExtensions": true,
    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true,
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

And the build-time config:

```jsonc
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "es2023",
    "lib": ["ES2023"],
    "module": "nodenext",
    "types": ["node"],
    "moduleDetection": "force",
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true,
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["vite.config.ts"]
}
```

Four observations that matter more than they look:

- **`strict` is absent, and the template is still strict.** TypeScript 6.0 made
  `strict: true` the default. A project pinned to `5.x` inherits none of that and
  must set `strict` explicitly — copying this template onto a 5.x pin produces a
  silently non-strict project. TSH's baseline writes `strict: true` out for exactly
  this reason.
- **`erasableSyntaxOnly` bans `enum`, `namespace`, and constructor parameter
  properties.** That is a good constraint in browser code — prefer a `const` object
  with a derived union over an `enum` — but it will reject code moved in from a
  decorator-based backend.
- **`allowArbitraryExtensions`** is what lets `import styles from './x.module.css'`
  resolve against a `./x.module.css.d.ts`. It is only about type resolution; the
  bundler still does the real work.
- **`module: nodenext` in the node config, not `bundler`.** Vite loads
  `vite.config.ts` through Node, so it gets Node's resolution rules. This is the
  whole point of the split.

Add the correctness flags from
[`compiler-options-for-the-browser.md`](./compiler-options-for-the-browser.md)
(`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`) to
the app config. The template omits them; they are the highest-value additions.

`noUnusedLocals` and `noUnusedParameters` are the two template flags worth
reconsidering — they turn an in-progress refactor into a wall of errors, and the
linter enforces the same thing with autofix and per-rule scoping.

## Why Two Configs

One config cannot describe both halves of a Vite project, because the two halves
disagree on every environmental option:

| | App source | `vite.config.ts` and scripts |
| --- | --- | --- |
| Who resolves imports | the bundler | Node |
| `moduleResolution` | `bundler` | `nodenext` |
| `lib` | needs `DOM` | must not have `DOM` |
| `types` | `vite/client` | `node` |

Collapsing them means one of two failures: `DOM` in scope for Node files, so
`document` looks available in a build script, or `types: ["node"]` in scope for app
files, so `process.env` type-checks in code that ships to a browser and is
`undefined` there.

| Severity | Rule |
| --- | --- |
| MUST | Keep app source and build-time files in separate configs. Add new `*.config.ts` files to the node config's `include`, not the app's. |
| MUST | Give each referenced project its own `tsBuildInfoFile`. Sharing one silently invalidates incremental builds. |
| NEVER | Add `DOM` to the build-time config's `lib` to fix an error. The error is telling you the file is in the wrong project. |

If `tsc -b` reports that a referenced project needs `composite: true`, add it —
older compiler lines require it for project references, and the requirement is
independent of everything else here.

## The Type Gate

Vite never type-checks. `vite build` runs esbuild and Rollup, both of which strip
types without reading them.

```jsonc
{
  "scripts": {
    "build": "tsc -b && vite build",
    "typecheck": "tsc -b --noEmit"
  }
}
```

| Severity | Rule |
| --- | --- |
| MUST | Run `tsc -b` on the **root** config. It walks every referenced project; `tsc --noEmit -p tsconfig.app.json` silently skips `vite.config.ts`. |
| MUST | Make it a CI step that fails the pipeline, not just a local script. |
| PREFER | Keeping it in the `build` script too, as the template does, so a local build fails the same way CI does. |
| AVOID | `vite-plugin-checker` as the only gate. It is excellent for dev-server feedback and it is not a substitute for a step CI can fail on. |

## Bundler Globals and `vite-env.d.ts`

`types: ["vite/client"]` supplies the ambient declarations for asset imports,
`?raw` and `?worker` suffixes, and the base `ImportMetaEnv`. Project-specific
environment variables are yours to declare:

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_SENTRY_DSN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

| Severity | Rule |
| --- | --- |
| MUST | Declare each variable the app reads, once, in `src/vite-env.d.ts`. Casting `import.meta.env` at the point of use gives up the only place these can be typed. |
| MUST | Prefix browser-exposed variables with `VITE_`. Vite only injects that prefix — an unprefixed variable is `undefined` at runtime while the type says `string`. |
| MUST | Type an optional variable as optional. Declaring everything `string` when `.env` may omit it is the same lie `any` would be. |
| NEVER | Read `process.env` in app source. It does not exist in the browser; that is what `import.meta.env` replaces. |

Declaring a variable does not prove it is set. Validate the environment at startup
if a missing value should fail loudly rather than surface as `undefined` deep in a
request.

## Path Aliases

An alias must be declared **twice** — once for the checker, once for the bundler —
because `tsc` rewrites nothing:

```jsonc
// tsconfig.app.json
{ "compilerOptions": { "paths": { "@/*": ["./src/*"] } } }
```

```ts
// vite.config.ts
resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } }
```

| Severity | Rule |
| --- | --- |
| MUST | Mirror every alias in both places, or generate both from one source with `vite-tsconfig-paths`. An unmirrored alias type-checks and then fails at build time. |
| MUST | Write `paths` relative to the project root. Do not add `baseUrl` — TypeScript 6.0 deprecated it and 7.0 removes it. |
| PREFER | One alias root (`@/*`) over a set of per-directory aliases. Each one is a pair of declarations that can drift. |
| AVOID | Aliases that cross a package boundary in a monorepo. Use the workspace package name; the resolver already handles it. |

## React Type Packages

| Severity | Rule |
| --- | --- |
| MUST | Keep `@types/react` and `@types/react-dom` on the same major as `react`. |
| MUST | Deduplicate `@types/react` when errors mention two incompatible `ReactNode` or `JSX.Element` types — that is always duplicate copies in the tree, not your code. Check with `npm ls @types/react`. |
| PREFER | `jsx: "react-jsx"`. The dev variant is selected by the build, not by your config. |

React 19 moved several long-deprecated types; a component library still on React 18
types can force a resolution override in the package manager. Prefer upgrading the
library.

## Adding a Test Config

Test files need globals the app does not, and they must not widen the app's config.
Add a third project rather than loosening the first:

```jsonc
// tsconfig.test.json
{
  "extends": "./tsconfig.app.json",
  "compilerOptions": {
    "types": ["vite/client", "vitest/globals"],
    "noEmit": true
  },
  "include": ["src/**/*.test.ts", "src/**/*.test.tsx", "src/test-setup.ts"]
}
```

Reference it from the root config so `tsc -b` checks it too. Excluding test files
from the app config's `include` keeps test-only helpers out of the shipped graph.

## Verifying Against the Template

The template moves with Vite and React majors. Before treating any block above as
current, read the source:

```shell
npm create vite@latest scratch -- --template react-ts   # generate and diff
npm view vite version
npm view typescript version
npm ls @types/react @types/react-dom
```

The template's own files live in `create-vite/template-react-ts/` in the Vite
repository. Diff the generated `tsconfig.app.json` against this reference when a
project is being set up — a mismatch means this file is behind, not that the
template is wrong.
