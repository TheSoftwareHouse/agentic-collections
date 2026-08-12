---
name: configuring-typescript-for-nodejs
description: "Configures TypeScript for Node.js server projects: which version to pin, the tsconfig baseline for a Node-resolved runtime, and the decorator-metadata settings NestJS and TypeORM require. Use when starting a Node service, editing a server tsconfig, diagnosing emitDecoratorMetadata or class-field problems, or upgrading TypeScript in a backend."
when_to_use: "Trigger on: setting up tsconfig.json for a Node service, module or moduleResolution nodenext questions, experimentalDecorators or emitDecoratorMetadata problems, useDefineForClassFields breaking dependency injection or TypeORM entities, CommonJS to ESM questions forced by a resolution change, or an upgrade of the pinned TypeScript version in a backend repo."
paths:
  - "**/tsconfig*.json"
  - "**/*.ts"
  - "**/*.mts"
  - "**/*.cts"
  - "**/nest-cli.json"
---

# Configuring TypeScript for Node.js

TSH's recommended TypeScript setup for code that runs **on Node**: which version
to pin, the `tsconfig.json` baseline for a Node-resolved runtime, and the
decorator and class-field settings NestJS, TypeORM, and `class-validator` depend
on.

This skill is about **configuration**. How to model types — unions, branded
types, `unknown` over `any` — is out of its scope. Browser-targeted code is out of
scope too: a bundler-resolved frontend needs a different baseline, so a repo with
both compiles them as separate configs.

## When to Use

- Setting up `tsconfig.json` for a new Node service, or reviewing an existing one
- Choosing the TypeScript version for a Node project, or justifying the pinned one
- Deciding `target`, `module`, and `moduleResolution` for a deployed Node major
- Diagnosing decorator, DI, or reflection behavior that changed under a flag
- Moving a Node project from CommonJS to ESM
- Upgrading TypeScript and triaging the resulting errors

## Applicability and Precedence

Read the target repository's `tsconfig.json` (and anything it extends),
`package.json`, and build tooling before proposing anything. **Local conventions
outrank this skill's defaults.** Apply this guidance where the repository is
silent, and record a deliberate deviation rather than silently mixing conventions.

**The baseline below is a recommendation for new projects, not a verdict on
existing ones.** A working `tsconfig.json` that differs from it is not a defect.
In an existing repo, propose the smallest staged change that serves the task at
hand and read
[`adopting-in-a-brownfield-project.md`](./references/adopting-in-a-brownfield-project.md)
before proposing anything wider.

Framework requirements outrank this skill. NestJS and TypeORM constrain decorator
and class-field settings in ways that override general recommendations; where a
framework skill and this one disagree, the framework skill wins for the files it
owns.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Treat this baseline as a recommendation for new projects. In an existing repo, propose the smallest staged change and record the remaining gap — never rewrite a working `tsconfig.json` wholesale to match this skill. |
| MUST | Enable `strict`. A project that cannot turn it on wholesale enables the individual flags progressively and records the remaining gap — never ships `strict: false` as a permanent state. |
| MUST | Pin an exact TypeScript version in `devDependencies` (no `^`). TypeScript does not follow semver — patch and minor releases add errors to previously compiling code. |
| MUST | Set `module` and `moduleResolution` to `node16`/`nodenext` (or `node20` on a current Node). Never leave the legacy `node`/`node10` resolver in a new project — it predates `package.json` `exports` and silently resolves the wrong entry point. |
| MUST | Set `useDefineForClassFields` **explicitly** in any project using decorators, and `false` for NestJS, TypeORM, and `class-validator` codebases. Left implicit, it flips with `target` and silently overwrites injected fields. |
| NEVER | Enable `verbatimModuleSyntax` in a project relying on `emitDecoratorMetadata` without verifying at runtime first — it elides type-only imports the metadata emit still needs. The failure is a runtime `undefined`, not a compile error. |
| NEVER | Enable `erasableSyntaxOnly` in a decorator-DI project without first converting every constructor parameter property to an explicit field assignment. It bans the idiomatic NestJS DI style outright. |
| MUST | Type-check in CI as its own step. A build that only transpiles (SWC, esbuild, `tsx`, Babel) does not check types; without a separate `tsc --noEmit`, type errors reach production. |
| MUST | Run the application — not just `tsc --noEmit` — after changing any emit-affecting option (`target`, `useDefineForClassFields`, `verbatimModuleSyntax`, `experimentalDecorators`). A green type-check cannot see this class of failure. |
| MUST | Treat a `@ts-expect-error` as debt: it carries a comment explaining the cause and the condition for removal. Prefer it over `@ts-ignore`, which silently rots when the error disappears. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Compiler options for Node.js](./references/compiler-options-for-nodejs.md) | Writing or reviewing a Node `tsconfig.json` | The baseline config, strictness ladder, `target`/`module`/`moduleResolution` for a deployed Node, `types`, emit and output layout, transpile-only runners |
| [Decorators and metadata](./references/decorators-and-metadata.md) | Decorators, DI, or runtime reflection are involved | Legacy vs standard decorators, `emitDecoratorMetadata`, `useDefineForClassFields`, `verbatimModuleSyntax`, `erasableSyntaxOnly`, framework baselines, diagnosing `undefined` injections |
| [Version and upgrades](./references/typescript-version-and-upgrades.md) | Choosing, justifying, or raising the TypeScript version | Version policy, what each recent major added, the upgrade procedure, per-major breaking changes, CommonJS to ESM |
| [Adopting in a brownfield project](./references/adopting-in-a-brownfield-project.md) | The repo already has a working config that differs from the baseline | Staged adoption order, ratcheting, per-flag sequencing, recording a deviation, when to leave a config alone |

## Procedure

**Step 1 — Read the ground truth.** Open `tsconfig.json` and every config it
extends, the `typescript` entry in `package.json`, the `engines` field or CI image
that fixes the Node version, and the build and test runners. Note the current
version, strictness, `target`, `module`, `moduleResolution`, and whether
decorators are in use before proposing anything.

**Step 2 — Decide greenfield or brownfield.** A new project takes the baseline as
written. An existing project gets the smallest staged change — read
[`adopting-in-a-brownfield-project.md`](./references/adopting-in-a-brownfield-project.md)
first.

**Step 3 — Load the relevant references.** Read
[`compiler-options-for-nodejs.md`](./references/compiler-options-for-nodejs.md)
before editing any `tsconfig.json`, and
[`decorators-and-metadata.md`](./references/decorators-and-metadata.md) before
touching a project that uses decorators. Those two account for most of the ways a
"harmless" config change breaks a running service.

**Step 4 — Establish the version baseline.** Confirm the TypeScript version is
pinned exactly and supported by the frameworks in `peerDependencies`. If the
change requires a newer version, treat the upgrade as its own step with its own
verification, not as a side effect.

**Step 5 — Apply the smallest change.** Prefer the narrowest edit that achieves
the goal. Whenever a proposed flag alters emit, say so explicitly in the same
breath as proposing it.

**Step 6 — Verify.** Run `tsc --noEmit` and the test suite. For any
emit-affecting flag, also start the application and exercise a DI-heavy path: a
passing type-check does not prove the runtime still wires up.

## Related Skills

- [`implementing-nestjs-api`](../implementing-nestjs-api/SKILL.md) — ships in this
  same plugin, so it is always available alongside this skill. It owns the NestJS
  module, CQRS, TypeORM, and REST guidance that sits on top of the compiler
  configuration here.
- `tsh-product-engineering` — TSH's discipline-level implementation and review
  workflows, independent of language. Optional; treat it as a bonus, never a
  prerequisite.

This skill does not configure browser or bundler builds, and does not cover type
modelling, linting, or formatting.
