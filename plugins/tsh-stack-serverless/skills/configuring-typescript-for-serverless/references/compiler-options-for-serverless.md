# TypeScript Compiler Options for a Lambda Bundle

Use this reference when writing or reviewing a `tsconfig.json` for a service
whose handler code is bundled and deployed to Lambda. Several options here
change **emitted output**, and a bundle that compiles cleanly can still fail at
runtime — that gap is the reason `tsc --noEmit` and the bundler are treated as
two separate, mandatory steps below.

## Table of Contents

- [The Baseline Config](#the-baseline-config)
- [Decorators, Only If the ORM Pairing Needs Them](#decorators-only-if-the-orm-pairing-needs-them)
- [Source Maps for Readable CloudWatch Stack Traces](#source-maps-for-readable-cloudwatch-stack-traces)
- [The Bundler Does Not Check Types](#the-bundler-does-not-check-types)

## The Baseline Config

Start here for a new Lambda service and subtract only with a recorded reason.
`target` and `lib` must match the Node major declared as the function or
provider runtime — see
[`runtime-and-module-format.md`](./runtime-and-module-format.md) for why a
mismatch there passes the type-check and fails at invocation.

```jsonc
{
  "compilerOptions": {
    // Match these to the deployed runtime's Node major, not to habit.
    "target": "es2023",
    "lib": ["es2023"],
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "types": ["node"],

    // Correctness.
    "strict": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,

    // A bundled Lambda function has no meaningful separate `.d.ts` consumer.
    "isolatedModules": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,

    // Readable stack traces in CloudWatch — see below.
    "sourceMap": true
  },
  "exclude": ["node_modules"]
}
```

`isolatedModules: true` matters more here than in a plain Node service: it
guarantees every file compiles independently, which is the assumption both
esbuild and `ts-loader` in fast mode already make. Leaving it off hides a class
of errors the bundler will not catch either.

## Decorators, Only If the ORM Pairing Needs Them

`experimentalDecorators`, `emitDecoratorMetadata`, and an explicit
`useDefineForClassFields: false` belong in the baseline **only** for the
pairing that uses a decorator-based ORM (webpack + `ts-loader` + TypeORM, or the
esbuild-plus-compiler-pass compromise) — see
[`bundler-tradeoffs.md`](./bundler-tradeoffs.md) for the pairings and why the
choice is not independent of the bundler. A service on the esbuild + Drizzle
pairing has no decorated entities and should not carry these flags at all;
adding them speculatively invites exactly the silent-metadata failure the
pairing was chosen to avoid.

```jsonc
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    // Must stay false: standard class-field semantics would overwrite values
    // that decorators assign, breaking entity mapping and DI alike.
    "useDefineForClassFields": false
  }
}
```

| Severity | Rule |
| --- | --- |
| MUST | Add the three decorator flags only when the chosen pairing uses a decorator-based ORM. Do not carry them by default. |
| MUST | Set `useDefineForClassFields` explicitly rather than letting it default from `target`. Left implicit, raising `target` later silently flips it and breaks entity mapping with no code change to point to. |
| NEVER | Rely on these flags alone to guarantee metadata is emitted. They control whether TypeScript *can* emit it — whether the bundler actually runs TypeScript's compiler to produce that emit is the bundler choice covered in `bundler-tradeoffs.md`. |

## Source Maps for Readable CloudWatch Stack Traces

`sourceMap: true` in `tsconfig.json` is necessary but not sufficient: the
bundler has to be configured to emit and package the map alongside the bundle,
and to point stack traces at the original TypeScript rather than the bundled
output. Treat the two settings as one decision — a compiler flag with no
matching bundler configuration produces a map file that never gets used, and a
bundler configured for source maps with the compiler flag off has nothing to
map from.

The trade-off that matters here is size versus fidelity in a deployed artifact:
a source map that also inlines the original source text (rather than only line
mappings) makes CloudWatch traces fully readable at the cost of a noticeably
larger bundle. For a deployed Lambda function, prefer a map that omits the
original source and resolve line numbers back to source locally when
debugging; keep a fuller, inline map only for local development, where bundle
size does not matter and it also gets you working breakpoints.

| Severity | Rule |
| --- | --- |
| MUST | Enable `sourceMap: true` and configure the bundler to emit and package a matching map whenever functions run in a shared or production stage — a raw bundled stack trace with mangled or missing names is not debuggable. |
| PREFER | A map without inlined source content for anything actually deployed; keep full inline source maps to local/offline development only. |

## The Bundler Does Not Check Types

esbuild is a transpiler. `ts-loader` run in fast mode (its common configuration
for packaging speed) skips type checking too and only converts syntax. Neither
reads `tsconfig.json`'s strictness settings, and neither will fail a package
step over a type error — they strip types and emit JavaScript, full stop.

| Severity | Rule |
| --- | --- |
| MUST | Run `tsc --noEmit` as its own step, separate from packaging, in CI and as a pre-push gate. This is the only place type errors get caught at all when the bundler does not check types. |
| MUST | Fail the pipeline on that step. A type-check that runs without gating anything is decoration, not verification. |
| MUST | Pin an exact TypeScript version in `devDependencies` (no `^` range). TypeScript does not follow semver for error surface — a minor or patch release can add errors to code that compiled cleanly yesterday, and an unpinned range makes that happen without anyone changing anything. |
| PREFER | Running the type-check in the editor as well, but never as the only gate — it checks open files against whatever settings the editor's language server picked up, which is not guaranteed to be CI's settings. |
