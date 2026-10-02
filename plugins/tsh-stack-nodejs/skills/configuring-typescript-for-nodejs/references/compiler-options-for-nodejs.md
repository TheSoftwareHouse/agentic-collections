# TypeScript Compiler Options for Node.js

Use this reference when writing or reviewing a `tsconfig.json` for code that runs
on Node. Read it before editing one: several options below change **emitted
output**, not just type checking, and a config change that type-checks cleanly can
still break a running service.

For a browser-targeted config, none of the module and resolution guidance here
applies — a bundler resolves differently, and that belongs to a frontend config.

## Contents

- [The Baseline Config](#the-baseline-config)
- [Strictness](#strictness)
- [Beyond `strict`](#beyond-strict)
- [Target, Module, and Resolution on Node](#target-module-and-resolution-on-node)
- [Ambient Types](#ambient-types)
- [Options That Change Runtime Behavior](#options-that-change-runtime-behavior)
- [Output and Project Layout](#output-and-project-layout)
- [Type-checking Is Not Building](#type-checking-is-not-building)

## The Baseline Config

Start here for a new Node service and subtract only with a recorded reason.

```jsonc
{
  "compilerOptions": {
    // Language and environment — match the deployed Node major.
    "target": "es2022",
    "lib": ["es2023"],
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "types": ["node"],

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
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

A decorator-based project (NestJS, TypeORM) adds `experimentalDecorators`,
`emitDecoratorMetadata`, and an explicit `useDefineForClassFields: false` — see
[`decorators-and-metadata.md`](./decorators-and-metadata.md) for why each is
required rather than optional.

Several options above are written out even though a modern compiler would default
to them. That is deliberate: `strict`, `types`, `rootDir`, `module`, and `target`
all **changed defaults in TypeScript 6.0**, and a config that states them survives
the upgrade unchanged instead of silently acquiring new behavior. See
[`typescript-version-and-upgrades.md`](./typescript-version-and-upgrades.md).

Three entries deserve a note:

- **`skipLibCheck: true`** is a pragmatic default, not a correctness one. It skips
  type-checking `.d.ts` files, which hides real conflicts between competing
  `@types` versions. Keep it on for build speed, but turn it off temporarily when
  diagnosing a type error that seems to come from nowhere.
- **`isolatedModules: true`** guarantees every file can be transpiled
  independently, which is what SWC, esbuild, and `tsx` actually do. Turn it on from
  the start; retrofitting it into a mature codebase is tedious.
- **`declaration: true`** earns its place in a published library and is mostly
  noise in a deployed service. Drop it for an application, keep it for a package
  another workspace consumes.

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

`strictPropertyInitialization` interacts with decorator-based DI and ORM entities:
a field the framework populates looks uninitialized to the compiler. Use `!`
definite assignment on those fields rather than turning the flag off.

For the order to enable these in an existing codebase, see
[`adopting-in-a-brownfield-project.md`](./adopting-in-a-brownfield-project.md).

## Beyond `strict`

These are not included in `strict` and are worth enabling deliberately.

| Option | What it catches | Cost |
| --- | --- | --- |
| `noUncheckedIndexedAccess` | `arr[i]` and `record[key]` returning `T` when the index may not exist. The single highest-value flag outside `strict`. | Noisy at first; adds `??` and guards at every index access. |
| `exactOptionalPropertyTypes` | `{ a?: string }` being assigned an explicit `undefined`, which is a different thing from absent. | Surfaces in object spreads and partial update DTOs. |
| `noImplicitOverride` | A method that shadows a base method without saying so, and silently stops overriding when the base is renamed. | Low — add the `override` keyword. |
| `noFallthroughCasesInSwitch` | A missing `break`. | Low. |
| `noPropertyAccessFromIndexSignature` | `config.someKey` on an index-signature type, where the key was never declared. Useful against `process.env` access. | Forces bracket access for dynamic keys; a readability trade. |
| `noUnusedLocals` / `noUnusedParameters` | Dead bindings. | Better handled by ESLint, which can fix and scope per-rule. Prefer the linter. |

`allowUnreachableCode: false` and `allowUnusedLabels: false` are cheap additions
once the rest is in place.

## Target, Module, and Resolution on Node

Set these from the Node version that actually runs the code, not from habit. The
authority is `engines` in `package.json`, the CI image, and the deployment
runtime — check that they agree before trusting any of them.

**`target`** decides which syntax is downlevelled. Set it to what the deployed
Node major implements. Targeting lower than necessary produces slower, larger
output, and it silently flips `useDefineForClassFields` — see below.

**`module` and `moduleResolution`** must agree with the loader:

| Node setup | `module` | `moduleResolution` |
| --- | --- | --- |
| ESM, or dual ESM/CJS | `node16` / `nodenext` / `node20` | `node16` / `nodenext` |
| CommonJS only | `commonjs` | `node16` |

| Severity | Rule |
| --- | --- |
| NEVER | Use the legacy `moduleResolution: node` (`node10`). It predates `package.json` `exports` and silently resolves the wrong entry point for modern packages — and TypeScript 6.0 deprecates it (it errors unless `ignoreDeprecations: "6.0"` is set) ahead of removal in 7.0, so it is also an upgrade blocker. |
| MUST | Use `node16`/`nodenext` for Node code. This is the only family of settings that models Node's real ESM/CJS rules, including the file-extension requirements in import specifiers. |
| NEVER | Use `moduleResolution: bundler` for code Node loads directly. It permits extensionless imports that Node rejects at runtime. |
| MUST | Keep `module` and `moduleResolution` in the same family. Mixing them produces resolution errors that read like missing files. |

Switching to `node16`/`nodenext` in a CommonJS project forces the ESM question,
because the resolver starts honouring `"type"` in `package.json`. That migration
is its own piece of work — see
[`typescript-version-and-upgrades.md`](./typescript-version-and-upgrades.md).

**`lib`** is independent of `target`: it declares what APIs exist, not what syntax
is emitted. A project targeting `es2022` on a newer Node can raise `lib` to get
newer standard-library types without changing emit.

## Ambient Types

`types` controls which `@types/*` packages are included **automatically**, and
leaving it unset means every package under `node_modules/@types` is in scope —
including test globals in production source, and DOM types pulled in transitively.

| Severity | Rule |
| --- | --- |
| MUST | Set `types` explicitly. `["node"]` for service source; add test globals only in the config that covers tests. |
| MUST | Match `@types/node` to the deployed Node major. A newer `@types/node` types APIs the runtime does not have, and the type-check passes while the service throws. |

## Options That Change Runtime Behavior

Everything in this section alters emitted JavaScript. A green `tsc --noEmit`
proves nothing about them — run the service.

**`useDefineForClassFields`** — defaults to `true` when `target` is `ES2022` or
higher. It emits class fields with `Object.defineProperty` semantics rather than
assignment, so a declared-but-uninitialized field is *defined as `undefined`*,
overwriting anything a decorator, base constructor, or DI container set. This is
the classic cause of "my injected dependency is suddenly `undefined`" after a
`target` bump. Set it explicitly; see
[`decorators-and-metadata.md`](./decorators-and-metadata.md).

**`verbatimModuleSyntax`** — emits imports exactly as written, dropping anything
declared `import type`. Correct and desirable in a project without decorator
metadata. In a project using `emitDecoratorMetadata`, it can elide an import the
metadata emit still needs at runtime, producing a runtime `undefined` for a
design-time type.

**`experimentalDecorators` / `emitDecoratorMetadata`** — select the legacy
decorator implementation and its metadata emit. Framework-mandated for NestJS and
TypeORM; covered in the decorators reference.

**`erasableSyntaxOnly`** (5.8+) — bans `enum`, `namespace`, and constructor
parameter properties so a file can be run by a type-stripping runtime. Required
for Node's native TypeScript execution, and directly incompatible with the
parameter-property DI style NestJS is built on.

**`importHelpers`** — emits helper calls against `tslib` instead of inlining them.
Reduces output size; adds a runtime dependency.

## Output and Project Layout

- **`outDir` plus `rootDir`**, not `outDir` alone. Without `rootDir`, adding a file
  above the common source root silently reshapes `dist/`, and the start script
  stops finding the entry point.
- **One root `tsconfig.json` per repo**, with packages extending it. Use
  `${configDir}` (5.5+) in the base config so relative paths resolve against the
  extending file rather than the base.
- **Separate configs for separate graphs.** Source, tests, and build scripts have
  different `types` and `include` needs. Extend a shared base instead of widening
  one config to cover all three.
- **`paths` aliases must be mirrored in the runtime resolver.** `tsc` rewrites
  nothing at emit — the alias resolves at type-check time and then fails at
  runtime unless `tsconfig-paths`, the bundler, or the package `imports` field
  reproduces it. Prefer Node's subpath `imports` (`#internal/*`); it works at
  runtime without extra tooling.
- **Do not add `baseUrl`.** TypeScript 6.0 deprecated it and 7.0 removes it. Write
  `paths` entries relative to the project root instead.
- **Project references** (`composite: true`) for large monorepos, when build
  ordering and incremental rebuilds matter more than the added configuration.

## Type-checking Is Not Building

SWC, esbuild, Babel, `tsx`, and `ts-jest` in `isolatedModules` mode all
**transpile without checking types**. They strip types and emit JavaScript; they
do not read your `tsconfig` strictness. The NestJS CLI's SWC builder is in this
category.

| Severity | Rule |
| --- | --- |
| MUST | Run `tsc --noEmit` as its own CI step, independent of the build and the tests. |
| MUST | Fail CI on that step. A type-check that runs but doesn't gate is decoration. |
| PREFER | Run it in the editor too, but never rely on the editor as the gate — it checks open files against possibly different settings. |
