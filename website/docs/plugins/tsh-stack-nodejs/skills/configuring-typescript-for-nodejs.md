---
title: Configuring TypeScript for Node.js
sidebar_label: configuring-typescript-for-nodejs
sidebar_position: 1
description: Configures TypeScript for Node.js server projects, covering which version to pin, the tsconfig baseline for a Node-resolved runtime, and the decorator-metadata settings NestJS and TypeORM require.
sources:
  - plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs/
sources_hash: "95a597be0d905edef3f371f07c7b0df3cc466d68968f62c69b12266ed2408d82"
---

# Configuring TypeScript for Node.js

**Plugin:** [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/)  
**Invoke:** `/tsh-stack-nodejs:configuring-typescript-for-nodejs`, and Claude also loads it when the work matches its description  
**Used by:** no agent or skill outside the plugin loads it by name. [`implementing-nestjs-api`](/docs/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api) and [`modelling-types-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs) link to it as the owner of the compiler baseline they assume, and the serverless sibling [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) points to it as the Node-server counterpart.

TSH's recommended TypeScript setup for code that runs on Node: which version to pin, the `tsconfig.json` baseline for a Node-resolved runtime, and the decorator and class-field settings that NestJS, TypeORM and `class-validator` depend on. The skill is about configuration only. How to model types is out of scope, and so is browser-targeted code, which needs a different baseline: a repository with both compiles them as separate configs.

Use it when setting up `tsconfig.json` for a Node service, choosing or raising the pinned TypeScript version, deciding `target`, `module` and `moduleResolution` for a deployed Node major, diagnosing decorator, DI or reflection behavior that changed under a flag, moving a project from CommonJS to ESM, or triaging the error wave after an upgrade.

The baseline is a recommendation for new projects, not a verdict on existing ones. Local conventions outrank the skill's defaults, and in an existing repository the skill proposes the smallest staged change. Framework requirements outrank it too: where a framework skill and this one disagree, the framework skill wins for the files it owns.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Version policy** | Pin an exact TypeScript version in `devDependencies` (no `^`), because TypeScript does not follow semver. Upgrade in its own PR, one minor at a time. For a new project take the latest stable release, but for a NestJS or TypeORM codebase confirm the frameworks compile and run under it first; the newest `6.x` is a legitimate temporary fallback |
| **Baseline `tsconfig.json`** | `target: es2022`, `lib: ["es2023"]`, `module` and `moduleResolution: nodenext`, `types: ["node"]`, `strict` plus `noUncheckedIndexedAccess`, `noImplicitOverride`, `noFallthroughCasesInSwitch` and `exactOptionalPropertyTypes`, with `outDir` and `rootDir` set together |
| **Module resolution** | `node16`, `nodenext` or `node20` for Node code; never the legacy `node10` resolver, and never `bundler` for code Node loads directly. `module` and `moduleResolution` stay in the same family |
| **Strictness** | `strict` is mandatory. A legacy codebase enables the sub-flags one at a time and tracks the remaining gap; it never ships `strict: false` as a permanent state |
| **Decorators and metadata** | NestJS 11, TypeORM 0.3, `class-validator` and `class-transformer` use legacy decorators (`experimentalDecorators`) and need an explicit `useDefineForClassFields: false`. `emitDecoratorMetadata` is required for NestJS, `class-validator` and `class-transformer`, and for TypeORM only where column types are implicit |
| **Emit-affecting flags** | `useDefineForClassFields`, `verbatimModuleSyntax` and `erasableSyntaxOnly` change emitted output. `verbatimModuleSyntax` can elide imports that the metadata emit still needs, and `erasableSyntaxOnly` bans constructor parameter properties, the idiomatic NestJS DI style |
| **Type-check gate** | SWC, esbuild, `tsx` and Babel transpile without checking types, so `tsc --noEmit` runs as its own failing CI step |
| **Upgrades** | What each recent major added, the 6.0 default changes (`strict`, `module`, `target`, `types`, `rootDir`), the 7.0 native compiler and why 6.0 is the stepping stone, the upgrade sequence, and how to triage the error wave by error code |
| **CommonJS to ESM** | `"type": "module"` together with `nodenext`, explicit `.js` extensions on relative imports, `import.meta.url` derivations in place of `__dirname` and `__filename`, and no mixing `"type": "module"` with `module: commonjs` |
| **Brownfield adoption** | Start by not changing anything, adopt flags in a safe order, enable `strict` incrementally with a ratchet, and record a deliberate deviation next to the setting |

## How it works

1. **Read the ground truth.** `tsconfig.json` and everything it extends, the `typescript` entry in `package.json`, the `engines` field or CI image that fixes the Node version, and the build and test runners.
2. **Decide greenfield or brownfield.** A new project takes the baseline as written. An existing project gets the smallest staged change.
3. **Load the relevant references.** Compiler options before editing any `tsconfig.json`, and the decorators reference before touching a project that uses decorators.
4. **Establish the version baseline.** Confirm the pin is exact and supported by the frameworks in `peerDependencies`. An upgrade is its own step with its own verification.
5. **Apply the smallest change**, and say so whenever a proposed flag alters emit.
6. **Verify.** Run `tsc --noEmit` and the test suite. For any emit-affecting flag, also start the application and exercise a DI-heavy path, because a passing type-check does not prove the runtime still wires up.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Treat the baseline as a recommendation for new projects and never rewrite a working `tsconfig.json` wholesale |
| MUST | Enable `strict`, and pin an exact TypeScript version |
| MUST | Set `module` and `moduleResolution` to `node16` or `nodenext` (or `node20` on a current Node) |
| MUST | Set `useDefineForClassFields` explicitly in any project using decorators, and `false` for NestJS, TypeORM and `class-validator` codebases |
| NEVER | Enable `verbatimModuleSyntax` with `emitDecoratorMetadata` without verifying at runtime, or `erasableSyntaxOnly` in a decorator-DI project before converting parameter properties |
| MUST | Type-check in CI as its own step, and run the application after changing any emit-affecting option |
| MUST | Treat a `@ts-expect-error` as debt with a comment naming the cause and the condition for removal |

## References

| Reference | Load when |
| :-- | :-- |
| Compiler options for Node.js | Writing or reviewing a Node `tsconfig.json` |
| Decorators and metadata | Decorators, DI or runtime reflection are involved |
| Version and upgrades | Choosing, justifying or raising the TypeScript version |
| Adopting in a brownfield project | The repository already has a working config that differs from the baseline |

## Related skills

- [`implementing-nestjs-api`](/docs/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api) owns the NestJS module, CQRS, TypeORM and REST guidance that sits on top of this configuration.
- [`modelling-types-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs) owns type shapes. This skill does not cover type modelling, linting or formatting.
- [`configuring-typescript-for-frontend`](/docs/plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend) is the near-twin for browser-targeted code in `tsh-stack-frontend`, and [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) is the one for bundled Lambda code. The skill does not configure browser or bundler builds.
- `tsh-product-engineering` supplies discipline-level implementation and review workflows. The skill treats it as optional and never as a prerequisite.

## Source

[`plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs/SKILL.md)
