# Adopting the Baseline in a Brownfield Project

Use this reference whenever the repository already has a working `tsconfig.json`
that differs from the baseline. The baseline is what TSH recommends for a **new**
Node project; it is not a standard existing repos are in violation of.

## Contents

- [Start by Not Changing Anything](#start-by-not-changing-anything)
- [Order of Adoption](#order-of-adoption)
- [Enabling `strict` Incrementally](#enabling-strict-incrementally)
- [The Riskiest Changes](#the-riskiest-changes)
- [Recording a Deliberate Deviation](#recording-a-deliberate-deviation)

## Start by Not Changing Anything

| Severity | Rule |
| --- | --- |
| MUST | Establish what the current config is *for* before proposing a change. A flag that looks wrong is often load-bearing for a framework, a build tool, or a dependency. |
| MUST | Scope config changes to the task at hand. A request to add a feature is not a mandate to modernise `tsconfig.json`. |
| NEVER | Replace a working config wholesale with the baseline. The diff is unreviewable and it mixes emit changes with type-only changes. |
| MUST | Propose config work as its own change, separate from feature work, so a regression has one plausible cause. |

Three situations where the right answer is to leave the config alone:

- **The service is in maintenance.** No new features, small team, low change rate.
  The upgrade cost lands now and the benefit never accrues.
- **A framework pins the setting.** `useDefineForClassFields: false` in a NestJS
  repo is correct, not legacy. So is `experimentalDecorators`.
- **The deviation is deliberate and recorded.** If there is a comment or an ADR
  explaining it, the decision has already been made by people with more context.

## Order of Adoption

When there *is* a reason to move a config toward the baseline, sequence it so each
step is independently reviewable and independently revertable. Cheapest and safest
first:

1. **`forceConsistentCasingInFileNames`, `esModuleInterop`, `skipLibCheck`.**
   Type-only, near-zero risk, no emit change.
2. **`isolatedModules`.** Type-only, but can surface real re-export problems. Land
   it before adopting any transpile-only runner.
3. **Explicit `types`.** Narrowing `types` to `["node"]` removes ambient globals
   that source files may have been leaning on. Fixes are mechanical.
4. **The `strict` sub-flags**, one at a time — see the next section.
5. **`noUncheckedIndexedAccess` and the rest of the beyond-`strict` set.** Do these
   after `strict` is complete, never alongside it.
6. **`module` / `moduleResolution`.** Behavioural: changes which files resolve.
   Its own PR, always.
7. **`target`, `useDefineForClassFields`, `verbatimModuleSyntax`.** Emit-affecting.
   One at a time, each with the application actually run.

The rule underneath the ordering: **never combine a type-only change with an
emit-affecting one in the same commit.** When something breaks, you want one
candidate cause.

## Enabling `strict` Incrementally

Turning on `strict` wholesale in a mature codebase produces thousands of errors and
stalls. Sequence it instead.

1. **Enable the cheap flags first**, each in its own PR: `noImplicitThis`,
   `alwaysStrict`, `strictBindCallApply`, `strictFunctionTypes`.
2. **`noImplicitAny` next.** Fix by annotating, not by adding explicit `any` — the
   latter converts a tracked gap into an untracked one.
3. **`strictPropertyInitialization`** before `strictNullChecks` in a decorator-heavy
   repo. Most of its errors are ORM entities and injected fields, and the fix is a
   `!` definite assignment assertion on exactly those fields — mechanical, and it
   isolates a large error cluster from the harder migration that follows.
4. **`strictNullChecks` last, and incrementally.** This is the large one. Two
   workable approaches:
   - **Directory by directory**, with a separate `tsconfig.strict.json` that
     `include`s only the migrated paths and runs as a second CI check. The migrated
     set only grows.
   - **File by file**, using a tool that tracks the allowlist of not-yet-strict
     files and fails when the list grows.
5. **Ratchet, don't gate.** Whatever the mechanism, the rule is that the unmigrated
   set may shrink but never grow. A migration without a ratchet regresses faster
   than it progresses.

| Severity | Rule |
| --- | --- |
| MUST | Apply `strict` to all new files from day one, whatever the legacy state. |
| NEVER | Add explicit `any` annotations to satisfy `noImplicitAny`. That defeats the point and hides the remaining work. |
| MUST | Keep the migration visible — a count in CI output, not a wiki page. |

## The Riskiest Changes

Three changes account for most brownfield config incidents. Each is safe to make
and unsafe to make *casually*.

**`target` bump.** Raising `target` to `ES2022` or above flips
`useDefineForClassFields` to `true` by default, which redefines class fields in the
constructor and wipes values a DI container or ORM driver set. Before the bump, set
`useDefineForClassFields: false` explicitly in its own commit, so the two effects
are separable.

**`moduleResolution` to `node16`/`nodenext`.** The resolver starts honouring
`"type"` and `exports`, so imports that previously resolved may stop, and CommonJS
assumptions surface as errors that read like missing files. Expect this to pull the
ESM question forward — that migration belongs in its own PR.

**`verbatimModuleSyntax` in a decorator project.** It elides `import type`
declarations that `emitDecoratorMetadata` still needs at runtime. The failure is a
runtime `undefined`, invisible to `tsc --noEmit`. Verify by running the service,
not by type-checking it.

## Recording a Deliberate Deviation

A deviation that is written down is a decision; one that isn't is indistinguishable
from an accident, and the next contributor will "fix" it.

| Severity | Rule |
| --- | --- |
| MUST | Record the reason next to the setting, as a `jsonc` comment in `tsconfig.json` where the format allows it. |
| MUST | Name the constraint, not the preference: which framework, which dependency, which runtime forces it. |
| PREFER | An unblock condition, so the deviation can be retired rather than inherited forever. |

```jsonc
{
  "compilerOptions": {
    // NestJS 11 + TypeORM 0.3 require legacy decorator metadata; standard
    // decorators do not support parameter decorators. Revisit when Nest ships
    // standard-decorator support.
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "useDefineForClassFields": false
  }
}
```

When the deviation is broad enough to shape how people write code — a
not-yet-strict directory, a permanent `moduleResolution` choice — it belongs in the
repository's own documentation as well, where a reader will find it before opening
`tsconfig.json`.
