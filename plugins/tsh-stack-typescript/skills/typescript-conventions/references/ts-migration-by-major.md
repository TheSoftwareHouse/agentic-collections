# Migrating Between TypeScript Versions

Use this reference when upgrading the TypeScript version, or when an upgrade has
produced an error wave you need to triage.

## Contents

- [The Upgrade Procedure](#the-upgrade-procedure)
- [Triaging the Error Wave](#triaging-the-error-wave)
- [Known Breaking Changes by Major](#known-breaking-changes-by-major)
- [Adopting Strictness in a Legacy Codebase](#adopting-strictness-in-a-legacy-codebase)
- [Migrating CommonJS to ESM](#migrating-commonjs-to-esm)

## The Upgrade Procedure

| Severity | Rule |
| --- | --- |
| MUST | Upgrade in its own PR, containing the version bump and the fixes it forces — nothing else. |
| MUST | One minor at a time when more than one behind. Jumping 5.2 → 5.9 merges several independent error waves into one unreadable diff. |
| MUST | Run the application after the type-check passes. Emit-affecting options can change with a version's defaults. |
| NEVER | Fix the wave by loosening `tsconfig`. New errors are usually correct; the previous version was wrong to accept the code. |

The sequence:

1. **Read the release notes for every version you're crossing**, specifically the
   "Breaking Changes" section. This is the step people skip, and it is the one
   that explains most of the errors.
2. **Bump the pin**, exactly: `"typescript": "5.9.2"`.
3. **Bump the toolchain with it.** `@typescript-eslint/*`, `ts-jest`, `ts-node`,
   and any custom transformer track compiler internals; a mismatch produces
   errors that have nothing to do with your code.
4. **`tsc --noEmit`** and capture the full output before changing anything.
5. **Triage** (below), then fix by category rather than file by file.
6. **Run the tests, then run the application.**
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

Consult the official release notes as the authority; this records the changes
that most often force work.

**5.0**

- `importsNotUsedAsValues` and `preserveValueImports` are deprecated in favour of
  `verbatimModuleSyntax`. Migrate rather than silence the deprecation.
- Several long-deprecated flags were removed (`noImplicitUseStrict`,
  `keyofStringsOnly`, `suppressImplicitAnyIndexErrors`, `out`, and others). A
  project relying on `suppressImplicitAnyIndexErrors` will surface a large number
  of previously hidden index errors — that is the flag's whole purpose.
- Enum members are more consistently typed, which can break code comparing enums
  across declarations.

**5.1** — Stricter checks on `undefined`-returning functions and getter/setter
type relationships.

**5.2** — `using` declarations arrive; the identifier `using` in an unusual
position can now parse differently. Decorator metadata lands for standard
decorators only.

**5.3** — Import attributes; narrowing improvements that can change which branch
the compiler considers reachable.

**5.4** — Preserved narrowing in closures changes inference in code that
previously widened. `NoInfer<T>` arrives. Some `Object.groupBy`-era library types
shift.

**5.5** — **Inferred type predicates** are the notable one: functions that return
booleans now narrow automatically, which can *change* the type at call sites and
surface errors in code downstream of a hand-written predicate.

**5.6** — **Disallowed nullish and truthy checks.** Always-truthy expressions
(`if (someFunction)` where a call was intended, regex literals in a condition)
become errors. These are almost always real bugs.

**5.7** — Checks on variables never assigned on some path. `target: es2024`.

**5.8** — Granular return-expression checks in conditional types.
`erasableSyntaxOnly` is opt-in and bans `enum`, `namespace`, and parameter
properties — see [`ts-decorators-and-metadata.md`](./ts-decorators-and-metadata.md).

**5.9** — `import defer`, `module: node20`.

**6.x and the native port** — the `6.x` JavaScript line is positioned to carry
deprecation warnings ahead of the Go-based native compiler. Verify current status
live before planning around it; see
[`ts-version-baselines.md`](./ts-version-baselines.md).

## Adopting Strictness in a Legacy Codebase

Turning on `strict` wholesale in a mature codebase produces thousands of errors
and stalls. Sequence it instead.

1. **Enable the cheap flags first**, each in its own PR: `noImplicitThis`,
   `alwaysStrict`, `strictBindCallApply`, `strictFunctionTypes`.
2. **`noImplicitAny` next.** Fix by annotating, not by adding explicit `any` —
   the latter converts a tracked gap into an untracked one.
3. **`strictNullChecks` last, and incrementally.** This is the large one. Two
   workable approaches:
   - **Directory by directory**, with a separate `tsconfig.strict.json` that
     `include`s only the migrated paths and runs as a second CI check. The
     migrated set only grows.
   - **File by file**, using a tool that tracks the allowlist of not-yet-strict
     files and fails when the list grows.
4. **Ratchet, don't gate.** Whatever the mechanism, the rule is that the
   unmigrated set may shrink but never grow. A migration without a ratchet
   regresses faster than it progresses.

| Severity | Rule |
| --- | --- |
| MUST | Apply `strict` to all new files from day one, whatever the legacy state. |
| NEVER | Add explicit `any` annotations to satisfy `noImplicitAny`. That defeats the point and hides the remaining work. |
| MUST | Keep the migration visible — a count in CI output, not a wiki page. |

## Migrating CommonJS to ESM

Often bundled with a TypeScript upgrade because `moduleResolution: node16`
forces the question.

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
