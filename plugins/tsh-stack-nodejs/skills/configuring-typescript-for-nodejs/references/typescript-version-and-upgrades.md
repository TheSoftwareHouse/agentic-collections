# TypeScript Version and Upgrades

Use this reference when choosing a TypeScript version for a Node project,
justifying (or challenging) the version an existing repo is on, or working through
the error wave an upgrade produced.

## Contents

- [Version Policy](#version-policy)
- [Choosing a Version](#choosing-a-version)
- [What Each Recent Major Added](#what-each-recent-major-added)
- [The Native Compiler Port](#the-native-compiler-port)
- [The Upgrade Procedure](#the-upgrade-procedure)
- [Triaging the Error Wave](#triaging-the-error-wave)
- [Known Breaking Changes by Major](#known-breaking-changes-by-major)
- [Migrating CommonJS to ESM](#migrating-commonjs-to-esm)
- [Verifying Live](#verifying-live)

## Version Policy

| Severity | Rule |
| --- | --- |
| MUST | Pin an exact version in `devDependencies`: `"typescript": "5.8.3"`, never `"^5.8.3"`. |
| MUST | Upgrade deliberately, as its own commit or PR, with the error triage that follows it. |
| PREFER | Stay within one minor of the latest stable release across the estate, so an upgrade is never a multi-major jump. |
| AVOID | Letting a repo fall more than two minors behind. The cost of catching up grows faster than the cost of keeping up. |

**TypeScript does not follow semver.** A minor release routinely adds new errors to
code that previously compiled, because better inference finds real bugs. This is
why the version is pinned: an unpinned caret range means CI can break on a release
nobody made. Treat every TypeScript bump as potentially breaking, and never let one
ride along inside an unrelated dependency update.

Pinning is not the same as freezing. A pinned version that nobody ever raises
becomes the reason a project cannot adopt a library, a framework major, or a Node
runtime. Schedule the upgrade; don't wait for a forcing function.

## Choosing a Version

**New project.** Take the latest stable release — with one check first. The current
stable line is the Go-native `7.x`, and it is not a drop-in for every stack. For a
plain Node service it is the right default. For a decorator-based one (NestJS,
TypeORM), confirm the frameworks compile and run under it before committing;
falling back to the newest `6.x` is a legitimate, temporary answer, and it is
cheaper than discovering the problem after the service is built.

**Existing project.** The version is constrained from below by what the code
already uses, and from above by three things worth checking before proposing a
bump:

1. **Framework support.** NestJS and TypeORM each declare a supported TypeScript
   range. Exceeding it is unsupported even when it compiles.
2. **`@types/*` packages.** These are written against a compiler version. A too-new
   compiler can surface errors inside `node_modules/@types`.
3. **Build tooling.** `ts-jest`, `ts-node`, `tsx`, SWC, and ESLint's TypeScript
   parser each track compiler internals and lag a release behind at times.

**Monorepo.** One TypeScript version for the whole repo, hoisted to the root.
Per-package versions produce type identity mismatches that surface as
incomprehensible errors — the same nominal type from two compiler versions is not
assignable to itself.

## What Each Recent Major Added

Highlights that change how you write or configure code. This is not a changelog;
consult the release notes for the full list.

**TypeScript 5.0**

- Stage 3 **standard decorators**, without `experimentalDecorators`. These are a
  different feature from the legacy decorators NestJS and TypeORM require — see
  [`decorators-and-metadata.md`](./decorators-and-metadata.md).
- `verbatimModuleSyntax`, replacing `importsNotUsedAsValues` and
  `preserveValueImports`.
- `const` type parameters, for inferring literal types without `as const` at every
  call site.
- `extends` accepting an array in `tsconfig.json`.

**TypeScript 5.2**

- `using` / `await using` declarations (explicit resource management).
- Decorator metadata, layering `Symbol.metadata` onto standard decorators.

**TypeScript 5.4**

- Preserved narrowing in closures created after their last assignment.
- The `NoInfer<T>` utility type.

**TypeScript 5.5**

- **Inferred type predicates** — a function returning a boolean can now narrow
  without an explicit `x is T` annotation.
- `${configDir}` in `tsconfig.json`, making shared base configs genuinely portable.
- `isolatedDeclarations`, for projects that need declaration emit without a full
  type-check.

**TypeScript 5.6**

- Disallowed nullish and truthy checks that are always true — catches a real family
  of bugs, such as testing a function object rather than calling it.

**TypeScript 5.7**

- `target: es2024`.
- Checks for variables used before any assignment on some path.

**TypeScript 5.8**

- `erasableSyntaxOnly`, which restricts the language to syntax that can be stripped
  without emit. Required if the code runs under Node's native type-stripping — and
  it bans `enum`, `namespace`, and constructor **parameter properties**, which are
  load-bearing in NestJS DI.
- Granular checks on return expressions in conditional types.

**TypeScript 5.9**

- `import defer` for deferred module evaluation.
- `module: node20`.

**TypeScript 6.0** — the bridge release. It ships few features and mostly changes
**defaults**, to line the ecosystem up for 7.0:

| Option | Was | Is |
| --- | --- | --- |
| `strict` | `false` | **`true`** |
| `module` | `commonjs` | `esnext` |
| `target` | `es2015` | a floating current ES version |
| `types` | every `@types/*` package | **`[]`** |
| `rootDir` | inferred from the file set | the directory holding `tsconfig.json` |
| `noUncheckedSideEffectImports` | `false` | `true` |

It also **deprecates** `target: es5`, `downlevelIteration`, `moduleResolution: node`
(`node10`) and `classic`, `module: amd`/`umd`/`systemjs`/`none`, `outFile`, the legacy
`module Foo {}` namespace syntax, `baseUrl`, `esModuleInterop: false` and
`alwaysStrict: false` — each errors unless you set `"ignoreDeprecations": "6.0"`,
which is a temporary measure, not a setting to live with; the removals land in
7.0. Running `tsc foo.ts` with a `tsconfig.json` present is now an error.

Two of those defaults bite Node services specifically: `types: []` means ambient
Node globals disappear until you add `"types": ["node"]`, and the floating `target`
implies **`useDefineForClassFields: true`**, which breaks decorator-based DI unless
the flag is set explicitly. Both are already in the baseline for this reason.

**TypeScript 7.0** — the compiler rewritten in Go, reported at 8–12× faster on full
builds. It adopts 6.0's defaults and drops every 6.0 deprecation with no
compatibility flag, so **6.0 is the required stepping stone**.

## The Native Compiler and the 7.0 Migration

7.0 is not a drop-in replacement. Before proposing it for a service:

| Severity | Rule |
| --- | --- |
| MUST | Go through 6.0 first, clearing every deprecation. 7.0 has no `ignoreDeprecations` escape hatch. |
| MUST | Verify decorator support against the frameworks in play before adopting 7.0 in a NestJS or TypeORM codebase. `experimentalDecorators` and `emitDecoratorMetadata` are not documented as removed, but "not removed" is not the same as "verified" — read the framework's `peerDependencies` and compile the real project. |
| MUST | Replace `baseUrl` with `paths` entries relative to the project root, and any `moduleResolution: node` with `nodenext`. Both are hard errors. |
| MUST | Check tooling that consumes the compiler's programmatic API — `typescript-eslint`, custom transformers, codegen. 7.0 has no stable API yet; the `@typescript/typescript6` package exists so those tools can run 6.0 alongside 7.0. |
| PREFER | Keeping TypeScript current so this migration is not stacked on a multi-major backlog. |

Custom transformers are the most exposed thing in any repo. Inventory them before
planning the move, not during it.

## The Upgrade Procedure

| Severity | Rule |
| --- | --- |
| MUST | Upgrade in its own PR, containing the version bump and the fixes it forces — nothing else. |
| MUST | One minor at a time when more than one behind. Jumping 5.2 → 5.9 merges several independent error waves into one unreadable diff. |
| MUST | Run the application after the type-check passes. Emit-affecting options can change with a version's defaults. |
| NEVER | Fix the wave by loosening `tsconfig`. New errors are usually correct; the previous version was wrong to accept the code. |

The sequence:

1. **Read the release notes for every version you're crossing**, specifically the
   "Breaking Changes" section. This is the step people skip, and it is the one that
   explains most of the errors.
2. **Bump the pin**, exactly: `"typescript": "5.9.2"`.
3. **Bump the toolchain with it.** `@typescript-eslint/*`, `ts-jest`, `ts-node`,
   `tsx`, and any custom transformer track compiler internals; a mismatch produces
   errors that have nothing to do with your code.
4. **`tsc --noEmit`** and capture the full output before changing anything.
5. **Triage** (below), then fix by category rather than file by file.
6. **Run the tests, then run the service** — including a DI-heavy path, since
   decorator metadata failures are invisible to the type-check.
7. **Regenerate the lockfile** and confirm CI reproduces the local result.

## Triaging the Error Wave

Sort errors by code, not by file — a version bump produces a few root causes
duplicated across many locations.

```shell
npx tsc --noEmit 2>&1 | grep -oE 'error TS[0-9]+' | sort | uniq -c | sort -rn
```

Then classify each cluster:

| Category | Signal | Action |
| --- | --- | --- |
| **Real bug the old compiler missed** | Better inference found an actual null, an unreachable branch, an always-truthy check | Fix the code. This is the upgrade paying for itself. |
| **Type-only, behavior unchanged** | Stricter library types, a narrowed built-in signature | Fix the annotation. |
| **Third-party types** | Error originates in `node_modules/@types` | Update the `@types` package. Do not patch around it; `skipLibCheck: false` temporarily to see the whole picture. |
| **Genuinely blocked** | A dependency is incompatible and unmaintained | `@ts-expect-error` with a comment naming the dependency and the unblock condition. Do not disable a compiler flag. |

If a cluster is large and mechanical, fix it with a codemod rather than by hand —
but review the diff, because a mechanical fix applied to a real bug hides it.

## Known Breaking Changes by Major

Consult the official release notes as the authority; this records the changes that
most often force work.

**5.0**

- `importsNotUsedAsValues` and `preserveValueImports` are deprecated in favour of
  `verbatimModuleSyntax`. Migrate rather than silence the deprecation.
- Several long-deprecated flags were removed (`noImplicitUseStrict`,
  `keyofStringsOnly`, `suppressImplicitAnyIndexErrors`, `out`, and others). A
  project relying on `suppressImplicitAnyIndexErrors` will surface a large number
  of previously hidden index errors — that is the flag's whole purpose.
- Enum members are more consistently typed, which can break code comparing enums
  across declarations.

**5.1** — Stricter checks on `undefined`-returning functions and getter/setter type
relationships.

**5.2** — `using` declarations arrive; the identifier `using` in an unusual
position can now parse differently. Decorator metadata lands for standard
decorators only.

**5.3** — Import attributes; narrowing improvements that can change which branch
the compiler considers reachable.

**5.4** — Preserved narrowing in closures changes inference in code that previously
widened. `NoInfer<T>` arrives. Some `Object.groupBy`-era library types shift.

**5.5** — **Inferred type predicates** are the notable one: functions that return
booleans now narrow automatically, which can *change* the type at call sites and
surface errors in code downstream of a hand-written predicate.

**5.6** — **Disallowed nullish and truthy checks.** Always-truthy expressions
(`if (someFunction)` where a call was intended, regex literals in a condition)
become errors. These are almost always real bugs.

**5.7** — Checks on variables never assigned on some path. `target: es2024`.

**5.8** — Granular return-expression checks in conditional types.
`erasableSyntaxOnly` is opt-in and bans `enum`, `namespace`, and parameter
properties — see [`decorators-and-metadata.md`](./decorators-and-metadata.md).

**5.9** — `import defer`, `module: node20`.

**6.0** — the largest breaking release in years, almost entirely through changed
defaults and removed options. See the table above. The two that produce the most
confusing failures: `types: []` (ambient globals vanish, so `process` and `Buffer`
stop resolving) and the floating `target` (which flips
`useDefineForClassFields` on and empties injected fields at runtime). Set both
explicitly *before* upgrading and neither can surprise you.

**7.0** — the Go compiler. Adopts 6.0's defaults and removes 6.0's deprecations
outright, with no `ignoreDeprecations` fallback. Not a drop-in: expect work in
tooling that uses the compiler API.

## Migrating CommonJS to ESM

Often bundled with a TypeScript upgrade, because `moduleResolution: node16` forces
the question.

| Severity | Rule |
| --- | --- |
| MUST | Set `"type": "module"` in `package.json` and `module`/`moduleResolution` to `node16` or `nodenext` together. Changing one without the other produces resolution errors that look like missing files. |
| MUST | Add explicit file extensions to relative imports (`./foo.js`, referring to the *emitted* file even from a `.ts` source). This is Node's rule, not TypeScript's. |
| MUST | Replace `__dirname` and `__filename` with `import.meta.url` derivations, and `require` with `createRequire` where a CJS-only dependency demands it. |
| NEVER | Mix `"type": "module"` with `module: commonjs`. Use the `.mts`/`.cts` extensions when a project genuinely needs both. |
| MUST | Check every dependency's `exports` map for ESM support before starting. One CJS-only dependency with no named exports can force `createRequire` throughout. |

Decorator-heavy projects should sequence this separately from any decorator or
class-field change — debugging a DI failure and a resolution failure at the same
time is materially harder than doing them one after the other.

## Verifying Live

Version facts go stale. Before pinning or recommending a version, check:

```shell
npm view typescript version              # latest stable
npm view typescript dist-tags            # including beta/rc
npm ls typescript                        # what this repo actually resolves
npx tsc --version                        # what the local toolchain runs
```

When a framework constrains the range, read its `peerDependencies` rather than its
documentation — the manifest is the enforced contract:

```shell
npm view @nestjs/core peerDependencies
```
