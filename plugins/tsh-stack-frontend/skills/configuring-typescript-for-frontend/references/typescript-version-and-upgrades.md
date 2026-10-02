# TypeScript Version and Upgrades

Use this reference when choosing a TypeScript version for a frontend project,
justifying (or challenging) the version an existing repo is on, or working through
the error wave an upgrade produced.

## Contents

- [Version Policy](#version-policy)
- [Choosing a Version](#choosing-a-version)
- [The 7.0 Embedded-Language Constraint](#the-70-embedded-language-constraint)
- [What Each Recent Major Added](#what-each-recent-major-added)
- [The Upgrade Procedure](#the-upgrade-procedure)
- [Triaging the Error Wave](#triaging-the-error-wave)
- [Known Breaking Changes by Major](#known-breaking-changes-by-major)
- [Verifying Live](#verifying-live)

## Version Policy

| Severity | Rule |
| --- | --- |
| MUST | Pin an exact version in `devDependencies`: `"typescript": "6.0.2"`, never `"^6.0.2"`. |
| MUST | Upgrade deliberately, as its own commit or PR, with the error triage that follows it. |
| PREFER | Stay within one minor of the latest stable release the project's framework supports, so an upgrade is never a multi-major jump. |
| AVOID | Letting a repo fall more than two minors behind. The cost of catching up grows faster than the cost of keeping up. |

**TypeScript does not follow semver.** A minor release routinely adds new errors to
code that previously compiled, because better inference finds real bugs. This is
why the version is pinned: an unpinned caret range means CI can break on a release
nobody made. Treat every TypeScript bump as potentially breaking, and never let one
ride along inside an unrelated dependency update.

A frontend repo has a second reason to pin: the type-check is often the *only*
place the compiler runs, since the bundler ignores it. An unexpected compiler
version changes what CI rejects without changing a line of source.

Pinning is not the same as freezing. A pinned version that nobody ever raises
becomes the reason a project cannot adopt a component library or a framework major.
Schedule the upgrade; don't wait for a forcing function.

## Choosing a Version

**New project.** Take the latest stable release your framework supports — which is
not always the latest release. The `7.x` line is the Go-native compiler and the
current stable line; `create-vite`'s React template still pins `6.x`. For a React
or plain-DOM app, `7.x` is a reasonable default. For anything with template syntax,
read the next section first.

**Existing project.** The version is constrained from below by what the code already
uses, and from above by three things worth checking before proposing a bump:

1. **Framework support.** Angular pins a supported TypeScript range and enforces it.
   Vue and Svelte depend on their own type-checkers tracking the compiler.
2. **`@types/*` packages.** `@types/react` in particular is written against a
   compiler version, and a too-new compiler surfaces errors inside `node_modules`.
3. **Tooling that reads the compiler API.** `typescript-eslint`, `vue-tsc`,
   `svelte-check`, `vite-plugin-checker`, and any codegen step track compiler
   internals and lag a release behind at times.

**Monorepo.** One TypeScript version for the whole repo, hoisted to the root.
Per-package versions produce type identity mismatches that surface as
incomprehensible errors — the same nominal type from two compiler versions is not
assignable to itself.

## The 7.0 Embedded-Language Constraint

This is the frontend-specific reason not to reach for the newest version reflexively.

TypeScript 7.0's native compiler **does not support embedded language tooling** —
Vue, Svelte, Astro, MDX, and Angular templates. That support requires the 6.0
JavaScript implementation.

| Severity | Rule |
| --- | --- |
| MUST | Stay on the `6.x` line for a project whose types live partly inside templates — Vue SFCs, Svelte components, Astro files, Angular templates — until its tooling states 7.0 support. |
| MUST | Verify by running the framework's own checker (`vue-tsc`, `svelte-check`), not just `tsc`. `tsc` passing proves nothing about template type-checking. |
| PREFER | `7.x` for React, Preact, Solid, and plain-DOM projects, where all types live in `.ts`/`.tsx` files. |

`6.x` is not a legacy line to apologise for — it is the supported path for a large
part of the frontend ecosystem, and it already carries every new default that 7.0
enforces.

## What Each Recent Major Added

Highlights that change how you write or configure code. This is not a changelog;
consult the release notes for the full list.

**TypeScript 5.0**

- `verbatimModuleSyntax`, replacing `importsNotUsedAsValues` and
  `preserveValueImports`.
- `moduleResolution: bundler` — the mode frontend projects should be on.
- `const` type parameters, for inferring literal types without `as const` at every
  call site.
- Stage 3 standard decorators, without `experimentalDecorators`.

**TypeScript 5.2** — `using` / `await using` declarations.

**TypeScript 5.4** — preserved narrowing in closures created after their last
assignment; the `NoInfer<T>` utility type.

**TypeScript 5.5**

- **Inferred type predicates** — a function returning a boolean narrows without an
  explicit `x is T` annotation.
- `${configDir}` in `tsconfig.json`, making shared base configs genuinely portable.

**TypeScript 5.6** — disallowed nullish and truthy checks that are always true.
Catches a real family of bugs, including a component tested rather than called.

**TypeScript 5.7** — `target: es2024`; checks for variables used before assignment
on some path.

**TypeScript 5.8** — `erasableSyntaxOnly`, restricting the language to syntax a
runtime can strip. It bans `enum`, `namespace`, and constructor parameter
properties; Vite's template now enables it.

**TypeScript 5.9** — `import defer`; `module: node20`.

**TypeScript 6.0** — the bridge release. Few features, mostly changed **defaults**:

| Setting | Was | Is |
| --- | --- | --- |
| `strict` | `false` | **`true`** |
| `module` | `commonjs` | `esnext` |
| `target` | `es2015` | a floating current ES version |
| `types` | every `@types/*` package | **`[]`** |
| `rootDir` | inferred from the file set | the directory holding `tsconfig.json` |
| `noUncheckedSideEffectImports` | `false` | `true` |

It also **deprecates** `target: es5`, `downlevelIteration`, `moduleResolution: node`
(`node10`), `module: amd`/`umd`/`systemjs`/`none`, `outFile`, the legacy
`module Foo {}` namespace syntax and `baseUrl` — each errors unless you set
`"ignoreDeprecations": "6.0"`, which is a temporary measure, not a setting to live
with; the removals land in 7.0. `moduleResolution: classic` is the one outright
removal in 6.0. The `dom` lib now includes `dom.iterable` and `dom.asynciterable` by default,
and `moduleResolution: bundler` is finally allowed with `module: commonjs`.

Two of those defaults matter most in a frontend repo: `strict: true` means a
project that was quietly non-strict starts failing, and `types: []` means ambient
declarations disappear until `types` names them (`["vite/client"]` for an app).

**TypeScript 7.0** — the compiler rewritten in Go, reported at 8–12× faster on full
builds. It adopts 6.0's defaults, removes every 6.0 deprecation with no
compatibility flag, and drops embedded-language support. **6.0 is the required
stepping stone**, and there is no stable programmatic compiler API yet — the
`@typescript/typescript6` package exists so tools like `typescript-eslint` can run
6.0 alongside it.

## The Upgrade Procedure

| Severity | Rule |
| --- | --- |
| MUST | Upgrade in its own PR, containing the version bump and the fixes it forces — nothing else. |
| MUST | One minor at a time when more than one behind. Jumping 5.2 → 6.0 merges several independent error waves into one unreadable diff. |
| MUST | Build and load the app after the type-check passes. A checker-only verification misses changes in what the bundler receives. |
| NEVER | Fix the wave by loosening `tsconfig`. New errors are usually correct; the previous version was wrong to accept the code. |

The sequence:

1. **Read the release notes for every version you're crossing**, specifically the
   "Breaking Changes" section. This is the step people skip, and it is the one that
   explains most of the errors.
2. **Bump the pin**, exactly.
3. **Bump the toolchain with it.** `typescript-eslint`, `vue-tsc`, `svelte-check`,
   `vite-plugin-checker`, and any codegen track compiler internals; a mismatch
   produces errors that have nothing to do with your code.
4. **`tsc -b`** and capture the full output before changing anything.
5. **Triage** (below), then fix by category rather than file by file.
6. **Run the tests, then build and load the app.**
7. **Regenerate the lockfile** and confirm CI reproduces the local result.

Crossing into 6.0 has two extra steps worth doing *first*, because they convert a
default change into a no-op: write `strict`, `target`, `module`, and `types` out
explicitly in the current version, and land that as its own commit.

## Triaging the Error Wave

Sort errors by code, not by file — a version bump produces a few root causes
duplicated across many locations.

```shell
npx tsc -b 2>&1 | grep -oE 'error TS[0-9]+' | sort | uniq -c | sort -rn
```

Then classify each cluster:

| Category | Signal | Action |
| --- | --- | --- |
| **Real bug the old compiler missed** | Better inference found an actual null, an unreachable branch, an always-truthy check | Fix the code. This is the upgrade paying for itself. |
| **Type-only, behavior unchanged** | Stricter library types, a narrowed built-in signature | Fix the annotation. |
| **Third-party types** | Error originates in `node_modules/@types` | Update the `@types` package, and check for duplicate majors of `@types/react`. Do not patch around it; `skipLibCheck: false` temporarily to see the whole picture. |
| **Missing ambient declaration** | `import.meta.env`, an asset import, or a global suddenly unknown | A `types` default changed. Name the declaration package explicitly rather than casting at the use site. |
| **Genuinely blocked** | A dependency is incompatible and unmaintained | `@ts-expect-error` with a comment naming the dependency and the unblock condition. Do not disable a compiler flag. |

If a cluster is large and mechanical, fix it with a codemod rather than by hand —
but review the diff, because a mechanical fix applied to a real bug hides it.

## Known Breaking Changes by Major

Consult the official release notes as the authority; this records the changes that
most often force work.

**5.0** — `importsNotUsedAsValues` and `preserveValueImports` deprecated in favour
of `verbatimModuleSyntax`. Several long-deprecated flags removed
(`suppressImplicitAnyIndexErrors` among them, which surfaces every index error it
was hiding).

**5.1** — stricter checks on `undefined`-returning functions and getter/setter type
relationships.

**5.2** — `using` declarations arrive; the identifier `using` in an unusual position
can parse differently.

**5.3** — import attributes; narrowing improvements that change which branch the
compiler considers reachable.

**5.4** — preserved narrowing in closures changes inference in code that previously
widened.

**5.5** — **inferred type predicates**: functions returning booleans now narrow
automatically, which can *change* the type at call sites and surface errors
downstream of a hand-written predicate.

**5.6** — **disallowed nullish and truthy checks.** Always-truthy expressions
become errors. These are almost always real bugs.

**5.7** — checks on variables never assigned on some path.

**5.8** — granular return-expression checks in conditional types.

**6.0** — the largest breaking release in years, almost entirely through changed
defaults and removed options. See the table above. In a frontend repo the two most
confusing failures are a suddenly-strict project and vanished ambient types.

**7.0** — the Go compiler. Adopts 6.0's defaults, removes its deprecations
outright, and does not support embedded languages. Not a drop-in.

## Verifying Live

Version facts go stale, and this file names specific majors. Before pinning or
recommending a version, check:

```shell
npm view typescript version              # latest stable
npm view typescript dist-tags            # including beta/rc
npm ls typescript                        # what this repo actually resolves
npx tsc --version                        # what the local toolchain runs
```

When a framework or checker constrains the range, read its `peerDependencies`
rather than its documentation — the manifest is the enforced contract:

```shell
npm view vue-tsc peerDependencies
npm view typescript-eslint peerDependencies
```
