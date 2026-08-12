# Adopting the Baseline in a Brownfield Project

Use this reference whenever the repository already has a working `tsconfig.json`
that differs from the baseline. The baseline is what TSH recommends for a **new**
frontend project; it is not a standard existing repos are in violation of.

## Contents

- [Start by Not Changing Anything](#start-by-not-changing-anything)
- [Turning On the Type Gate](#turning-on-the-type-gate)
- [Order of Adoption](#order-of-adoption)
- [Enabling `strict` Incrementally](#enabling-strict-incrementally)
- [Splitting One Config Into Two](#splitting-one-config-into-two)
- [Recording a Deliberate Deviation](#recording-a-deliberate-deviation)

## Start by Not Changing Anything

| Severity | Rule |
| --- | --- |
| MUST | Establish what the current config is *for* before proposing a change. A flag that looks wrong is often load-bearing for the bundler, a framework, or a dependency. |
| MUST | Scope config changes to the task at hand. A request to add a component is not a mandate to modernise `tsconfig.json`. |
| NEVER | Replace a working config wholesale with the baseline. The diff is unreviewable, and in a frontend repo it can change what ships without changing any source. |
| MUST | Propose config work as its own change, separate from feature work, so a regression has one plausible cause. |

Three situations where the right answer is to leave the config alone:

- **A framework owns the file.** Next.js, Angular, and Nuxt generate or manage
  `tsconfig.json` fields. Hand-editing those is reverted on the next build at best.
- **The app is in maintenance.** Low change rate, small team, no new features. The
  migration cost lands now and the benefit never accrues.
- **The deviation is deliberate and recorded.** If a comment or an ADR explains it,
  the decision has already been made by people with more context.

## Turning On the Type Gate

This is the brownfield situation specific to frontend work, and it is worth handling
before any flag tuning.

Because Vite and esbuild never type-check, a repo can build green for years while
accumulating type errors. Adding `tsc -b` to CI in that repo does not produce a
config discussion — it produces several hundred errors at once, and reverting is
the path of least resistance.

Sequence it so the gate goes in *first* and the backlog shrinks after:

1. **Measure before proposing.** Run the check locally and count by error code:

   ```shell
   npx tsc -b 2>&1 | grep -oE 'error TS[0-9]+' | sort | uniq -c | sort -rn
   ```

2. **Add the step in reporting-only mode** if the count is large — run it in CI,
   print the output, do not fail the build yet. This makes the number visible to
   everyone instead of to whoever proposed the change.
3. **Fix by cluster, not by file.** One error code at a time, each its own PR. The
   top three codes are usually most of the count.
4. **Flip the step to failing** the moment the count reaches zero, in the same PR
   that clears the last cluster. A gate that reports without failing decays.
5. **If zero is far away, ratchet instead.** Check a subset — `tsconfig.strict.json`
   including only migrated directories — and fail on that. The migrated set may grow
   and never shrink.

| Severity | Rule |
| --- | --- |
| MUST | Get *a* failing type-check into CI, even over a subset. A repo with no gate accumulates errors faster than any cleanup can clear them. |
| NEVER | Introduce the gate and the strictness increase in the same change. Fix what today's settings already reject first. |
| MUST | Include the build-time config in what gets checked once the app config is clean. `vite.config.ts` is where the Node/browser confusion hides. |

## Order of Adoption

When there *is* a reason to move a config toward the baseline, sequence it so each
step is independently reviewable and revertable. Cheapest and safest first:

1. **`forceConsistentCasingInFileNames`, `skipLibCheck`, `moduleDetection: force`.**
   Type-only, near-zero risk.
2. **`isolatedModules`.** Type-only, but surfaces real re-export problems. The
   bundler already behaves this way; the flag makes the compiler agree.
3. **`verbatimModuleSyntax`.** Forces `import type` to be explicit. Safe in browser
   code, and it can reveal a side-effect import that was being elided.
4. **Explicit `types`.** Narrowing to `["vite/client"]` removes ambient globals the
   source may have been leaning on — usually Node types that never existed at
   runtime anyway. Those errors are real bugs, not migration noise.
5. **The `strict` sub-flags**, one at a time — see below.
6. **`noUncheckedIndexedAccess` and the rest of the beyond-`strict` set.** After
   `strict` is complete, never alongside it.
7. **`moduleResolution` to `bundler`.** Behavioural: changes which files resolve.
   Its own PR.
8. **Splitting the config**, and any `target`/`lib` change. Last, and verified by
   loading the built app.

The rule underneath the ordering: **never combine a type-only change with one that
changes what the bundler receives.** When something breaks, you want one candidate
cause.

## Enabling `strict` Incrementally

Turning on `strict` wholesale in a mature codebase produces thousands of errors and
stalls. Sequence it instead.

1. **Enable the cheap flags first**, each in its own PR: `noImplicitThis`,
   `alwaysStrict`, `strictBindCallApply`, `strictFunctionTypes`.
2. **`noImplicitAny` next.** Fix by annotating, not by adding explicit `any` — the
   latter converts a tracked gap into an untracked one. In a React codebase most of
   this wave is untyped props and event handlers, which is mechanical.
3. **`strictNullChecks` last, and incrementally.** This is the large one. Two
   workable approaches:
   - **Directory by directory**, with a separate `tsconfig.strict.json` that
     `include`s only migrated paths and runs as a second CI check. The migrated set
     only grows.
   - **File by file**, using a tool that tracks the allowlist of not-yet-strict
     files and fails when the list grows.
4. **Ratchet, don't gate.** Whatever the mechanism, the unmigrated set may shrink but
   never grow. A migration without a ratchet regresses faster than it progresses.

| Severity | Rule |
| --- | --- |
| MUST | Apply `strict` to all new files from day one, whatever the legacy state. |
| NEVER | Add explicit `any` annotations to satisfy `noImplicitAny`. That defeats the point and hides the remaining work. |
| MUST | Keep the migration visible — a count in CI output, not a wiki page. |

An upgrade to TypeScript 6.0 forces this question, because `strict` becomes the
default. A repo that is not ready should write `strict: false` explicitly *before*
the upgrade, so the version bump is not also a strictness migration — and then treat
that line as tracked debt, not a resting state.

## Splitting One Config Into Two

A single flat config covering both app source and `vite.config.ts` is the most
common brownfield shape, and splitting it is mostly mechanical:

1. Create `tsconfig.app.json` and `tsconfig.node.json`, both extending nothing at
   first — copy the existing options into each.
2. Narrow each one: remove `DOM` from the node config's `lib`, remove `node` from
   the app config's `types`, set the node config's resolution to `nodenext`.
3. Turn the original `tsconfig.json` into a root config with `files: []` and
   `references` to both.
4. Change the CI command to `tsc -b` so it walks both projects.
5. Expect one error class: app files that were quietly using Node globals. Those are
   real defects — `process.env` in browser code is `undefined` at runtime.

| Severity | Rule |
| --- | --- |
| MUST | Give each project its own `tsBuildInfoFile`. Sharing one silently invalidates incremental builds. |
| MUST | Move build-time files into the node config's `include` rather than widening the app config to accept them. |
| NEVER | Keep an `include` that covers `vite.config.ts` from the app project after the split. Two projects owning one file produces contradictory errors. |

## Recording a Deliberate Deviation

A deviation that is written down is a decision; one that isn't is indistinguishable
from an accident, and the next contributor will "fix" it.

| Severity | Rule |
| --- | --- |
| MUST | Record the reason next to the setting, as a `jsonc` comment where the format allows it. |
| MUST | Name the constraint, not the preference: which framework, which dependency, which browser target forces it. |
| PREFER | An unblock condition, so the deviation can be retired rather than inherited forever. |

```jsonc
{
  "compilerOptions": {
    // Pinned to the 6.x line: vue-tsc has no 7.0 support, and template types are
    // not checked by tsc alone. Revisit when vue-tsc declares TypeScript 7.
    // strictNullChecks migration tracked in tsconfig.strict.json; ~40 files left.
    "strictNullChecks": false
  }
}
```

When the deviation shapes how people write code — a not-yet-strict directory, a
permanent resolution choice, a framework-managed field — it belongs in the
repository's own documentation as well, where a reader will find it before opening
`tsconfig.json`.
