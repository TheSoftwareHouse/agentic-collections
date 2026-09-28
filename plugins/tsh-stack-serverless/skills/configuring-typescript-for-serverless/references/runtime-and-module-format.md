# Node Runtime and Module Format on Lambda

Use this reference when pinning the Node runtime for a function, deciding ESM
versus CommonJS for a Lambda bundle, or diagnosing a dependency that resolves in
tests but fails once the packaged artifact runs.

## Table of Contents

- [Pinning the Runtime](#pinning-the-runtime)
- [ESM or CommonJS on Lambda](#esm-or-commonjs-on-lambda)
- [CommonJS Dependencies Inside an ESM Bundle](#commonjs-dependencies-inside-an-esm-bundle)
- [Diagnosing a Packaging-Only Failure](#diagnosing-a-packaging-only-failure)

## Pinning the Runtime

The Node major declared in the service configuration (the function or provider
runtime, e.g. `nodejs22.x`) and the Node major the code is built against are two
separate settings that must agree, and nothing forces them to.

| Severity | Rule |
| --- | --- |
| MUST | Set `target` and `lib` in `tsconfig.json` from the same Node major the service configuration declares as its runtime — not from habit, and not from whatever the local Node happens to be. |
| MUST | Match `@types/node`'s major to the declared runtime. A newer `@types/node` types APIs that do not exist in the deployed runtime; the type-check passes and the function throws at invocation. |
| MUST | Re-check both whenever the runtime is bumped. A runtime bump with no corresponding `tsconfig.json` or `@types/node` change is a silent drift, not a completed upgrade. |

A runtime bump is worth treating as its own change with its own verification —
packaging and invoking the function — rather than a side effect of an unrelated
edit.

## ESM or CommonJS on Lambda

Middy's current major line publishes an import-only exports map: an ESM-only
package with no CommonJS entry point at all. Any dependency shaped that way
forces the whole bundle it is loaded from into ESM — there is no partial
adoption.

Moving a service to ESM touches every layer at once:

- `package.json` declares `"type": "module"`.
- `tsconfig.json` uses `module`/`moduleResolution: nodenext`, and relative
  imports between your own files carry the runtime-relative `.js` extension
  even though the source is `.ts` — NodeNext resolves imports the way Node
  itself will, not the way the source is named.
- The bundler is configured to emit native ESM output, not CommonJS wrapped to
  look like it.
- Tooling that only needs to run locally (a bundler config file, a script) can
  stay CommonJS; the constraint is on the deployed artifact and the package
  graph it pulls in, not on every file in the repository.

Picking ESM or CommonJS per file, or per dependency, without deciding the
bundle's module format first produces exactly the resolution failures in the
next section — they are a consequence of the mismatch, not an independent risk.

| Severity | Rule |
| --- | --- |
| MUST | Decide the bundle's module format before adding a dependency, not after one fails to resolve. Check whether anything already in the dependency graph publishes an import-only exports map — that decision has already been made for you. |
| NEVER | Assume a package that works when run through a TypeScript-executing test runner will resolve the same way once bundled. The runner and the bundler apply different resolution rules. |

## CommonJS Dependencies Inside an ESM Bundle

An ESM bundle does not make every dependency in it well-behaved. Node driver
packages and native-binding wrappers are commonly still CommonJS internally, and
three distinct failure shapes come out of that mismatch — all invisible until the
packaged artifact actually runs:

1. **A dynamic `require()` inside a dependency.** Some drivers resolve their
   actual implementation with a runtime `require(name)` rather than a static
   `import`, specifically so they can support several backends without bundling
   all of them. A bundler's static analysis cannot see that call, so the
   implementation never makes it into the bundle. The build succeeds; the
   function throws a "package not installed" error on its first real use.
2. **A dependency listed as external that isn't actually available at
   runtime.** Marking something external tells the bundler "resolve this at
   runtime instead of bundling it." In a CommonJS bundle that produces a
   `require` a runtime lookup can often still satisfy through a package's own
   fallback handling; in an ESM bundle the same entry becomes a bare `import`
   of a package that was never installed, and the artifact fails to load
   outright.
3. **A dependency that publishes both an ESM wrapper and CommonJS internals,
   where the two disagree about the module's shape.** Forcing ESM resolution
   globally (because something else in the bundle, like Middy, requires it)
   can hand such a dependency's own internal `require()` calls a module
   namespace object instead of the constructor or class it expects, producing
   an error inside the dependency itself at import time.

**The case you are most likely to hit first is the AWS SDK.** Its packages ship
no `exports` map — only `main` (a CommonJS build) and `module` (an ESM build) —
and esbuild's default field order for `platform: "node"` prefers `main`. An ESM
bundle therefore pulls in the CommonJS build, whose internal
`require("node:https")` the bundle cannot satisfy, and the artifact throws
`Dynamic require of "node:https" is not supported` the moment it is imported.
Setting the bundler's main-field order to prefer `module` over `main` fixes it.
Nothing catches this except executing the packaged artifact: the type-check
passes, and so does every source-level test.

The common thread: the fix is never to widen module resolution further and hope
it resolves everything — that is what caused case 3. Instead, pin the
problematic dependency to a known-good behavior individually: force a static
import so a dynamic `require()` can be seen, or pin a specific sub-dependency to
its CommonJS entry point rather than letting global resolution decide. A
dependency that ships both an ESM wrapper and CommonJS internals gets the same
treatment as any other case of this: pinned individually, not solved by
adjusting a global setting.

| Severity | Rule |
| --- | --- |
| MUST | Verify by executing the packaged artifact — not just running the test suite — after changing anything about how the bundler resolves or externalizes a dependency. Source-level test runners bypass bundling entirely and cannot see these failures. |
| NEVER | Silence a bundler's "cannot resolve" or "critical dependency" warning globally to make output quieter. That warning is frequently the only build-time signal that a dynamic `require()` exists and will fail at runtime; scope any suppression to the specific dependency that is already understood to be safe. |
| NEVER | Add configuration to *enable* those warnings. They are on by default — this rule is about not turning them off, and there is nothing to switch on. Reaching for an unfamiliar option to satisfy it lands on the wrong knob. |
| MUST | Treat a fix to dependency resolution (an alias, a pinned entry point, an externals change) as needing the same runtime verification as a production incident would — these bugs reproduce in the deployed artifact and nowhere else. |

## Diagnosing a Packaging-Only Failure

| Symptom | Likely cause |
| --- | --- |
| `DriverPackageNotInstalledError`, or an equivalent "package not installed" thrown only on the first real invocation | A dependency's dynamic `require()` was invisible to the bundler; the implementation it loads at runtime was never bundled. |
| `ERR_MODULE_NOT_FOUND` for a package that is not actually a direct dependency | An `externals` entry became a bare ESM import once the bundle switched to native ESM output. |
| A dependency throws while extending or calling a namespace object (`class X extends <namespace>` or similar) | Global ESM resolution handed that dependency's internal `require()` a module namespace object instead of the value it expected. Pin that dependency to its CommonJS entry point. |
| `Dynamic require of "node:https" is not supported`, or a similar dynamic require, thrown at import time | The bundler resolved a dependency's CommonJS build into an ESM bundle because the package publishes no `exports` map. Prefer the ESM entry in the bundler's main-field order. |
| Everything works under the test runner and fails only once packaged and invoked | The test runner executes TypeScript source directly and never exercises the bundler's resolution at all. Verify against the packaged artifact. |

## Sources

Verified 2026-09-18:

- [middy — Upgrade 4.x to 5.x](https://middy.js.org/docs/upgrade/4-5/) — the release that dropped CommonJS and made middy import-only

The three CommonJS-inside-ESM failure shapes are drawn from failures hit while moving a
real service to ESM, not from a specification; expect the specific packages that trigger
them to change as drivers ship native ESM.
