---
name: configuring-typescript-for-serverless
description: "Configures TypeScript for AWS Lambda services bundled by Serverless Framework or OSLS: which Node runtime and TypeScript version to target, the ESM tsconfig baseline for bundler-emitted handler code, and choosing between esbuild and webpack with ts-loader. Use when starting a Lambda service, editing a serverless project's tsconfig, or diagnosing a bundle that compiles but fails at runtime."
when_to_use: "Trigger on: setting up tsconfig.json for a Lambda service, ESM versus CommonJS inside a Lambda bundle, choosing or switching the bundler behind serverless package, decorator metadata breaking under esbuild, a CommonJS dependency failing inside an ESM bundle, source maps and stack traces in CloudWatch, or pinning the Node runtime version for a function."
paths:
  - "**/tsconfig*.json"
  - "**/*.ts"
  - "**/*.mts"
  - "**/*.cts"
---

# Configuring TypeScript for Serverless

TSH's recommended TypeScript setup for AWS Lambda handler code deployed through
Serverless Framework or OSLS: which Node runtime and TypeScript version to
target, the `tsconfig.json` baseline for bundler-emitted ESM output, and how to
choose the bundler — a choice this plugin treats as paired with the ORM, never
independent of it.

This skill is about **compiling and bundling**, not about what runs once the
function starts. What a handler does with the config below —
`implementing-lambda-functions` — and how the function itself is declared and
deployed — `configuring-serverless-service` — are out of scope here.

## When to Use

- Setting up `tsconfig.json` for a new Lambda service, or reviewing an existing one
- Choosing esbuild or webpack + `ts-loader` for packaging, together with the ORM decision it constrains
- Deciding `target`, `module`, and `moduleResolution` for a bundled, ESM-deployed function
- Diagnosing a bundle that compiles cleanly and fails only once packaged and invoked
- Moving a service between CommonJS and ESM
- Pinning or raising the TypeScript version, or the declared Node runtime

## Applicability and Precedence

Read the target service's `tsconfig.json`, `package.json` (`type`, `engines`,
`devDependencies`), and the service configuration's declared runtime before
proposing anything. **Local conventions outrank this skill's defaults.** Apply
this guidance where the service is silent, and record a deliberate deviation
rather than silently mixing conventions.

The bundler-and-ORM pairing (see
[`bundler-tradeoffs.md`](./references/bundler-tradeoffs.md)) constrains the
decorator-related compiler flags below — do not add
`experimentalDecorators`/`emitDecoratorMetadata` on the assumption they are
harmless; whether they do anything depends on which bundler is in use.

## Version Baseline

This plugin targets **OSLS v4 or Serverless Framework v3**, AWS Lambda, and
**Node.js 24** (`nodejs24.x`; `nodejs22.x` stays in range until its 2027-04-30
deprecation, never for a new service) — a new service starts on OSLS, since Serverless Framework v3
is end of life and its type package stops at `nodejs20.x`. Before proposing a
config, read the project's `package.json` (`engines`, the `serverless` or
`osls` dependency) and the service configuration's declared runtime. If the
project sits outside that range, stop and report the mismatch rather than
proposing settings tuned for a version this skill was not written against.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Treat the bundler as a transpiler, never a type checker. esbuild and `ts-loader` in fast mode both skip type checking entirely — `tsc --noEmit` is a separate, mandatory gate, run and failed on its own, independent of packaging. |
| MUST | Match the Node runtime declared in the service configuration to what the code is built against: `target`/`lib` in `tsconfig.json` and the `@types/node` major. A newer `@types/node` types APIs the deployed runtime does not have, and the mismatch passes the type-check and throws at invocation. |
| MUST | Decide the bundler and the ORM together, as one paired choice, before either is adopted alone — see [`bundler-tradeoffs.md`](./references/bundler-tradeoffs.md). esbuild cannot emit `emitDecoratorMetadata`; pairing it with a decorator-based ORM without a mitigation compiles clean and fails at runtime. |
| MUST | Pin an exact TypeScript version in `devDependencies` (no `^`). TypeScript does not follow semver for its error surface. |
| MUST | Use `module`/`moduleResolution: nodenext` for an ESM-deployed bundle, and keep relative imports between source files suffixed `.js` even though the source is `.ts` — NodeNext resolves the way Node itself will. |
| NEVER | Enable `verbatimModuleSyntax` in a project relying on `emitDecoratorMetadata` without verifying at runtime first — it can elide a type-only-looking import the metadata emit still needs. The failure is a runtime `undefined`, not a compile error. |
| MUST | Verify by executing the packaged artifact, not only the source through a test runner, after changing anything about how the bundler resolves or externalizes a dependency — see [`runtime-and-module-format.md`](./references/runtime-and-module-format.md). |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Runtime and module format](./references/runtime-and-module-format.md) | Pinning the Node runtime, deciding ESM versus CommonJS for the bundle, or a dependency fails only once packaged | Matching the declared runtime to build settings, ESM/CJS on Lambda, CommonJS dependencies breaking inside an ESM bundle, a diagnostic table by symptom |
| [Bundler tradeoffs](./references/bundler-tradeoffs.md) | Choosing or switching the bundler, or a decorator-based entity fails at runtime with no build error | Why the bundler and the ORM are one decision, the three pairings and their costs, why Prisma is not offered as the esbuild pairing |
| [Compiler options for serverless](./references/compiler-options-for-serverless.md) | Writing or reviewing a Lambda `tsconfig.json` | The baseline config, when the decorator flags apply, source maps for CloudWatch, why `tsc --noEmit` is a separate step |

## Procedure

**Step 1 — Read the ground truth.** Open `tsconfig.json`, `package.json`
(`type`, `engines`, the pinned TypeScript and `serverless`/OSLS versions), and
the service configuration's declared runtime. Note the current bundler and
whether the service uses a decorator-based ORM before proposing anything.

**Step 2 — Confirm the version baseline.** Stop and report if the project sits
outside OSLS v4 / Serverless Framework v3, or on a Node runtime older than 22.

**Step 3 — Settle the bundler-and-ORM pairing before touching decorator
flags.** Read
[`bundler-tradeoffs.md`](./references/bundler-tradeoffs.md) before adding or
removing `experimentalDecorators`, `emitDecoratorMetadata`, or
`useDefineForClassFields` — whether those flags do anything at all depends on
this choice.

**Step 4 — Apply the baseline.** Read
[`compiler-options-for-serverless.md`](./references/compiler-options-for-serverless.md)
before editing `tsconfig.json`. Greenfield takes the baseline as written; an
existing config gets the smallest change that serves the task, with the
remaining gap recorded.

**Step 5 — Decide the module format.** Read
[`runtime-and-module-format.md`](./references/runtime-and-module-format.md)
before moving a service between CommonJS and ESM, or before adding a
dependency that might not be well-behaved under the bundle's current
resolution rules.

**Step 6 — Verify.** Run `tsc --noEmit`, then package the service and inspect
the packaged artifact — a clean type-check proves nothing about bundler
resolution, decorator metadata, or module-format mismatches. For any
emit-affecting change, invoke the packaged function rather than trusting the
type-check alone.

## Related Skills

Ships in this plugin — if this skill loaded, they are installed.

- [`implementing-lambda-functions`](${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/SKILL.md) —
  owns everything inside the handler once it is compiled: the thin-handler
  split, middleware, validation, and logging.
- [`configuring-serverless-service`](${CLAUDE_PLUGIN_ROOT}/skills/configuring-serverless-service/SKILL.md) —
  owns the deployable service definition and the library policy, which states
  where this skill's bundler-and-ORM pairing is settled and where it is not.

`tsh-stack-nodejs` ships a sibling, `configuring-typescript-for-nodejs`, covering
the same language for a Node server process, not a bundled Lambda artifact — its
ESM/CommonJS and module-resolution guidance does not transfer to a
bundler-emitted bundle.

This skill does not configure handler code, service or IAM definitions, or
non-serverless Node/browser TypeScript.
