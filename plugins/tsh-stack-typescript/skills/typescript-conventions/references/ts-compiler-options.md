# TypeScript Compiler Options

Use this reference when writing or reviewing a `tsconfig.json`. Read it before
editing one: several options below change **emitted output**, not just type
checking, and a config change that type-checks cleanly can still break a running
application.

## Contents

- [The Baseline Config](#the-baseline-config)
- [Strictness](#strictness)
- [Beyond `strict`](#beyond-strict)
- [Target, Module, and Resolution](#target-module-and-resolution)
- [Options That Change Runtime Behavior](#options-that-change-runtime-behavior)
- [Project Layout](#project-layout)
- [Type-checking Is Not Building](#type-checking-is-not-building)

## The Baseline Config

Start here and subtract only with a recorded reason.

```jsonc
{
  "compilerOptions": {
    // Language and environment — match the actual runtime.
    "target": "es2022",
    "lib": ["es2023"],
    "moduleResolution": "node16",
    "module": "node16",

    // Correctness.
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,

    // Interop and emit.
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "declaration": true,
    "sourceMap": true,
    "outDir": "dist"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

Two entries in that list deserve a note:

- **`skipLibCheck: true`** is a pragmatic default, not a correctness one. It
  skips type-checking `.d.ts` files, which hides real conflicts between competing
  `@types` versions. Keep it on for build speed, but turn it off temporarily when
  diagnosing a type error that seems to come from nowhere.
- **`isolatedModules: true`** guarantees every file can be transpiled
  independently, which is what esbuild, SWC, and Babel actually do. Turn it on
  from the start; retrofitting it into a mature codebase is tedious.

## Strictness

`strict` is an umbrella that currently enables `noImplicitAny`,
`strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`,
`strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`,
and `alwaysStrict`.

| Severity | Rule |
| --- | --- |
| MUST | Set `strict: true` in new projects. |
| MUST | For a legacy codebase that cannot flip it at once, enable the sub-flags one at a time, land each with its fixes, and track the remaining gap somewhere visible. |
| NEVER | Disable a strict sub-flag to make a specific file compile. Fix the file, or isolate it with a narrowly scoped `@ts-expect-error` and a comment. |
| AVOID | `strictNullChecks: false`. It is by far the most valuable of the group, and the hardest to enable later — every additional month of code written without it deepens the eventual migration. |

The practical order for an incremental rollout, easiest to hardest:
`noImplicitThis` → `alwaysStrict` → `strictBindCallApply` → `strictFunctionTypes`
→ `noImplicitAny` → `strictPropertyInitialization` → `strictNullChecks`.

## Beyond `strict`

These are not included in `strict` and are worth enabling deliberately.

| Option | What it catches | Cost |
| --- | --- | --- |
| `noUncheckedIndexedAccess` | `arr[i]` and `record[key]` returning `T` when the index may not exist. The single highest-value flag outside `strict`. | Noisy at first; adds `?? ` and guards at every index access. |
| `exactOptionalPropertyTypes` | `{ a?: string }` being assigned an explicit `undefined`, which is a different thing from absent. | Surfaces in object spreads and partial updates. |
| `noImplicitOverride` | A method that shadows a base method without saying so, and silently stops overriding when the base is renamed. | Low — add the `override` keyword. |
| `noFallthroughCasesInSwitch` | A missing `break`. | Low. |
| `noPropertyAccessFromIndexSignature` | `config.someKey` on an index-signature type, where the key was never declared. | Forces bracket access for dynamic keys; a readability trade. |
| `noUnusedLocals` / `noUnusedParameters` | Dead bindings. | Better handled by ESLint, which can fix and scope per-rule. Prefer the linter. |

`allowUnreachableCode: false` and `allowUnusedLabels: false` are cheap additions
once the rest is in place.

## Target, Module, and Resolution

Set these from the runtime the code actually executes on, not from habit.

**`target`** decides which syntax is downlevelled. Set it to what the runtime
supports. Targeting lower than necessary produces slower, larger output and
changes class-field semantics (see below). For a Node service, target the ES
version the deployed Node major implements.

**`module` and `moduleResolution`** must agree with the loader:

| Runtime | `module` | `moduleResolution` |
| --- | --- | --- |
| Node, ESM or dual | `node16` / `nodenext` / `node20` | `node16` / `nodenext` |
| Node, CommonJS only | `commonjs` | `node16` |
| Bundled (Vite, webpack, esbuild) | `esnext` / `preserve` | `bundler` |

| Severity | Rule |
| --- | --- |
| NEVER | Use the legacy `moduleResolution: node` (`node10`) in a new project. It predates `package.json` `exports` and will silently resolve the wrong entry point for modern packages. |
| MUST | Use `node16`/`nodenext` for Node code. This is the only setting that models Node's real ESM/CJS rules, including the file-extension requirements in import specifiers. |
| MUST | Use `bundler` only when a bundler actually resolves the imports. It permits extensionless imports that Node will reject at runtime. |

**`lib`** is independent of `target`: it declares what APIs exist, not what
syntax is emitted. A project targeting `es2022` on a newer Node can raise `lib`
to get newer standard-library types without changing emit.

## Options That Change Runtime Behavior

Everything in this section alters emitted JavaScript. A green `tsc --noEmit`
proves nothing about them — run the application.

**`useDefineForClassFields`** — defaults to `true` when `target` is `ES2022` or
higher. It emits class fields with `Object.defineProperty` semantics rather than
assignment, so a declared-but-uninitialized field is *defined as `undefined`*,
overwriting anything a decorator or base constructor set. This is the classic
cause of "my injected dependency is suddenly `undefined`" after a `target` bump.
See [`ts-decorators-and-metadata.md`](./ts-decorators-and-metadata.md).

**`verbatimModuleSyntax`** — emits imports exactly as written, dropping anything
declared `import type`. Correct and desirable in most projects. In a project
using `emitDecoratorMetadata`, it can elide an import the metadata emit still
needs at runtime, producing a runtime `undefined` for a design-time type.

**`experimentalDecorators` / `emitDecoratorMetadata`** — select the legacy
decorator implementation and its metadata emit. Framework-mandated; covered in
the decorators reference.

**`erasableSyntaxOnly`** (5.8+) — bans `enum`, `namespace`, and constructor
parameter properties so the file can be run by a type-stripping runtime. Required
for Node's native TypeScript execution, and directly incompatible with NestJS's
parameter-property DI style.

**`importHelpers`** — emits helper calls against `tslib` instead of inlining
them. Reduces output size; adds a runtime dependency.

## Project Layout

- **One root `tsconfig.json` per repo**, with packages extending it. Use
  `${configDir}` (5.5+) in the base config so relative paths resolve against the
  extending file rather than the base.
- **Separate configs for separate graphs.** Source, tests, and build scripts have
  different `lib`, `types`, and `include` needs. Extend a shared base instead of
  widening one config to cover all three.
- **`paths` aliases must be mirrored in the runtime resolver.** `tsc` rewrites
  nothing at emit — the alias resolves at type-check time and then fails at
  runtime unless the bundler, `tsconfig-paths`, or the package `imports` field
  reproduces it. Prefer Node's subpath `imports` (`#internal/*`) in Node
  projects; it works at runtime without extra tooling.
- **Project references** (`composite: true`) for large monorepos, when build
  ordering and incremental rebuilds matter more than the added configuration.

## Type-checking Is Not Building

esbuild, SWC, Babel, Vite, and `ts-jest` in `isolatedModules` mode all **transpile
without checking types**. They strip types and emit JavaScript; they do not read
your `tsconfig` strictness.

| Severity | Rule |
| --- | --- |
| MUST | Run `tsc --noEmit` as its own CI step, independent of the build and the tests. |
| MUST | Fail CI on that step. A type-check that runs but doesn't gate is decoration. |
| PREFER | Run it in the editor too, but never rely on the editor as the gate — it checks open files against possibly different settings. |
