---
name: typescript-conventions
description: "TSH conventions for TypeScript itself: which language version to target, how to configure the compiler, how to model types, and how to move between majors. Use when starting a TypeScript project, changing tsconfig, upgrading the TypeScript version, or deciding how strictly to type new code."
when_to_use: "Trigger on: picking a TypeScript version, writing or reviewing tsconfig.json, turning on strict flags, an upgrade from one TypeScript major to the next, decorator or emitDecoratorMetadata problems, module resolution errors, or a review comment about `any`, type assertions, or unsafe casts."
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.mts"
  - "**/*.cts"
  - "**/tsconfig*.json"
---

# TypeScript Conventions

TSH's language-level guidance for TypeScript: version policy, compiler
configuration, type modelling, and migration between majors. It is deliberately
framework-neutral — it applies equally to a NestJS API, a React app, a CLI, or a
Lambda handler.

## When to Use

- Choosing the TypeScript version for a new project, or justifying the one in an existing repo
- Writing or reviewing `tsconfig.json`, especially strictness and module resolution
- Diagnosing decorator, metadata, or class-field behavior that changed under a flag
- Deciding how to model a type: union vs enum, interface vs type, generic vs overload
- Upgrading across a TypeScript major and triaging the resulting errors
- Reviewing code for `any`, unsafe assertions, or types that lie

## Applicability and Precedence

Read the target repository's `tsconfig.json`, `package.json`, and existing code
before applying anything here. **Local conventions outrank this skill's defaults.**
Apply this guidance where the repository is silent, and record a deliberate
deviation rather than silently mixing conventions.

Framework requirements also outrank this skill. NestJS, Angular, and TypeORM each
constrain decorator and class-field settings in ways that override the general
recommendations below; where a framework skill and this one disagree, the
framework skill wins for files it owns.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Enable `strict`. A project that cannot turn it on wholesale enables the individual flags progressively and records the remaining gap — never ships `strict: false` as a permanent state. |
| NEVER | Use `any` to silence an error. Use `unknown` and narrow, or model the type properly. `any` is acceptable only at a genuinely untyped boundary, and only with a comment naming the reason. |
| NEVER | Use a type assertion (`as`) to claim something the compiler disproved. Assertions are for facts the compiler cannot know, not for overruling it. `as unknown as T` is a defect unless a comment justifies it. |
| MUST | Pin an exact TypeScript version in `devDependencies` (no `^`). TypeScript does not follow semver — patch and minor releases add errors to previously compiling code. |
| MUST | Set `moduleResolution` to match the runtime that actually loads the code (`node16`/`nodenext` for Node, `bundler` when a bundler resolves). Never leave the legacy `node`/`node10` resolver in a new project. |
| MUST | Type-check in CI as its own step. A build that only transpiles (esbuild, SWC, Babel, Vite) does not check types; without a separate `tsc --noEmit`, type errors reach production. |
| NEVER | Enable `verbatimModuleSyntax` in a project relying on `emitDecoratorMetadata` without verifying it first — it elides type-only imports the metadata emit still needs at runtime. See the decorators reference. |
| MUST | Treat a `@ts-expect-error` as debt: it carries a comment explaining the cause and the condition for removal. Prefer it over `@ts-ignore`, which silently rots when the error disappears. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Version baselines](./references/ts-version-baselines.md) | Choosing or justifying a TypeScript version | Version policy, what each recent major added, how to pick a target for a new or existing project |
| [Compiler options](./references/ts-compiler-options.md) | Writing or reviewing `tsconfig.json` | Strictness ladder, module/target/resolution, the baseline config, and flags that change runtime behavior |
| [Decorators and metadata](./references/ts-decorators-and-metadata.md) | Decorator, DI, or reflection behavior is involved | Legacy vs standard decorators, `emitDecoratorMetadata`, `useDefineForClassFields`, `verbatimModuleSyntax`, and the framework constraints they impose |
| [Type modelling](./references/ts-type-modelling.md) | Deciding how to express a type | `unknown` over `any`, discriminated unions, branded types, `satisfies`, interface vs type, generic discipline |
| [Migration by major](./references/ts-migration-by-major.md) | Upgrading TypeScript | Upgrade procedure, per-major breaking changes, and how to triage the resulting error wave |

## Procedure

**Step 1 — Read the ground truth.** Open `tsconfig.json` (and any config it
extends), the `typescript` entry in `package.json`, and the build tooling. Note
the current version, strictness, `target`, `module`, and `moduleResolution`
before proposing anything.

**Step 2 — Load the relevant references.** Use the table above. Read
[`ts-compiler-options.md`](./references/ts-compiler-options.md) before editing any
`tsconfig.json`, and [`ts-decorators-and-metadata.md`](./references/ts-decorators-and-metadata.md)
before touching a project that uses decorators — those two account for most of
the ways a "harmless" config change breaks a running application.

**Step 3 — Establish the version baseline.** Confirm the TypeScript version is
pinned and supported. If the change requires a newer version, treat the upgrade
as its own step with its own verification, not as a side effect.

**Step 4 — Apply the change.** Prefer the smallest config change that achieves
the goal. Flags that alter emit (`useDefineForClassFields`, `verbatimModuleSyntax`,
`experimentalDecorators`, `target`) change runtime behavior, not just type
checking — call that out explicitly whenever you propose one.

**Step 5 — Verify.** Run `tsc --noEmit` and the project's test suite. For any
emit-affecting flag, also run the application: a passing type-check does not
prove the runtime still works.

## Related Skills

Optional and may not be installed — treat each as a bonus, never a prerequisite:

- [`implementing-nestjs-api`](../implementing-nestjs-api/SKILL.md) — ships in this
  same plugin, so it is always available alongside this skill. It owns the NestJS
  decorator, DI, and TypeORM constraints that this skill only summarizes.
- `tsh-product-engineering` — TSH's discipline-level implementation and review
  workflows, independent of language.
