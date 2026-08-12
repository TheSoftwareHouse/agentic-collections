# TypeScript Version Baselines

Use this reference when choosing a TypeScript version for a new project, or
justifying (or challenging) the version an existing repo is on.

## Contents

- [Version Policy](#version-policy)
- [Choosing a Version](#choosing-a-version)
- [What Each Recent Major Added](#what-each-recent-major-added)
- [The Native Compiler Port](#the-native-compiler-port)
- [Verifying Live](#verifying-live)

## Version Policy

| Severity | Rule |
| --- | --- |
| MUST | Pin an exact version in `devDependencies`: `"typescript": "5.8.3"`, never `"^5.8.3"`. |
| MUST | Upgrade deliberately, as its own commit or PR, with the error triage that follows it. |
| PREFER | Stay within one minor of the latest stable release across the estate, so an upgrade is never a multi-major jump. |
| AVOID | Letting a repo fall more than two minors behind. The cost of catching up grows faster than the cost of keeping up. |

**TypeScript does not follow semver.** A minor release routinely adds new errors
to code that previously compiled, because better inference finds real bugs. This
is why the version is pinned: an unpinned caret range means CI can break on a
release nobody made. Treat every TypeScript bump as potentially breaking, and
never let one ride along inside an unrelated dependency update.

Pinning is not the same as freezing. A pinned version that nobody ever raises
becomes the reason a project cannot adopt a library, a framework major, or a
Node runtime. Schedule the upgrade; don't wait for a forcing function.

## Choosing a Version

**New project.** Take the latest stable release. There is no benefit to starting
behind, and starting current means the first upgrade is small.

**Existing project.** The version is constrained from below by what the code
already uses, and from above by three things worth checking before proposing a
bump:

1. **Framework support.** Angular, NestJS, and TypeORM each declare a supported
   TypeScript range. Exceeding it is unsupported even when it compiles.
2. **`@types/*` packages.** These are written against a compiler version. A
   too-new compiler can surface errors inside `node_modules/@types`.
3. **Build tooling.** `ts-jest`, `ts-node`, SWC, and ESLint's TypeScript parser
   each track compiler internals and lag a release behind at times.

**Monorepo.** One TypeScript version for the whole repo, hoisted to the root.
Per-package versions produce type identity mismatches that surface as
incomprehensible errors — the same nominal type from two compiler versions is not
assignable to itself.

## What Each Recent Major Added

Highlights that change how you write or configure code. This is not a changelog;
consult the release notes for the full list.

**TypeScript 5.0**

- Stage 3 **standard decorators**, without `experimentalDecorators`. These are a
  different feature from the legacy decorators most frameworks still require —
  see [`ts-decorators-and-metadata.md`](./ts-decorators-and-metadata.md).
- `verbatimModuleSyntax`, replacing `importsNotUsedAsValues` and
  `preserveValueImports`.
- `const` type parameters, for inferring literal types without `as const` at every call site.
- `moduleResolution: bundler`.
- `extends` accepting an array in `tsconfig.json`.

**TypeScript 5.2**

- `using` / `await using` declarations (explicit resource management).
- Decorator metadata, layering `Symbol.metadata` onto standard decorators.

**TypeScript 5.4**

- Preserved narrowing in closures created after their last assignment.
- The `NoInfer<T>` utility type.

**TypeScript 5.5**

- **Inferred type predicates** — a function returning a boolean can now narrow
  without an explicit `x is T` annotation. This removes a large class of
  hand-written predicates.
- `${configDir}` in `tsconfig.json`, making shared base configs genuinely portable.
- `isolatedDeclarations`, for projects that need declaration emit without a full
  type-check.

**TypeScript 5.6**

- Disallowed nullish and truthy checks that are always true — catches a real
  family of bugs, such as testing a function object rather than calling it.

**TypeScript 5.7**

- `target: es2024`.
- Checks for variables used before any assignment on some path.

**TypeScript 5.8**

- `erasableSyntaxOnly`, which restricts the language to syntax that can be
  stripped without emit. Required if the code runs under Node's native
  type-stripping — and it bans `enum`, `namespace`, and constructor **parameter
  properties**, which are load-bearing in NestJS DI.
- Granular checks on return expressions in conditional types.

**TypeScript 5.9**

- `import defer` for deferred module evaluation.
- `module: node20`.

## The Native Compiler Port

Microsoft is porting the compiler to Go for a large speed increase, shipping as a
separate native executable ahead of a `7.0` line, with the `6.x` JavaScript line
carrying deprecations that smooth the transition.

Treat this as **forward-looking, and verify current status live** before acting on
it — release timing and the exact version numbering have moved. Two things are
worth doing today regardless of when it lands:

- Keep TypeScript current, so the eventual migration is not stacked on top of a
  multi-major backlog.
- Prefer configuration and syntax that are not tied to compiler internals.
  Anything reaching into the TypeScript API, custom transformers in particular,
  is the most exposed and should be inventoried now.

## Verifying Live

Version facts go stale. Before pinning or recommending a version, check:

```shell
npm view typescript version              # latest stable
npm view typescript dist-tags            # including beta/rc
npm ls typescript                        # what this repo actually resolves
npx tsc --version                        # what the local toolchain runs
```

When a framework constrains the range, read its `peerDependencies` rather than
its documentation — the manifest is the enforced contract:

```shell
npm view @nestjs/core peerDependencies
```
