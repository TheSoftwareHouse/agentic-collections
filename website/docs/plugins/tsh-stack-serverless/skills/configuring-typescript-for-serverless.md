---
title: Configuring TypeScript for Serverless
sidebar_label: configuring-typescript-for-serverless
sidebar_position: 1
description: Configures TypeScript for AWS Lambda services bundled by Serverless Framework or OSLS, covering the Node runtime and TypeScript version, the ESM tsconfig baseline, and choosing between esbuild and webpack with ts-loader.
sources:
  - plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless/
sources_hash: "b7a96dde26df006be0b331b229c565fe9b57da840b1bbba99a5841d6c36989bf"
---

# Configuring TypeScript for Serverless

**Plugin:** [`tsh-stack-serverless`](/docs/plugins/tsh-stack-serverless/)  
**Invoke:** `/tsh-stack-serverless:configuring-typescript-for-serverless`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions) and [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) link to it as the owner of the compiler and bundler baseline, and the library policy of the latter links to its bundler reference for the full bundler-and-ORM reasoning.

TSH's recommended TypeScript setup for AWS Lambda handler code deployed through Serverless Framework or OSLS: which Node runtime and TypeScript version to target, the `tsconfig.json` baseline for bundler-emitted ESM output, and how to choose the bundler, a choice this plugin treats as paired with the ORM and never independent of it.

The skill is about compiling and bundling, not about what runs once the function starts. What a handler does is [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions), and how the function is declared and deployed is [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service).

Use it when setting up or reviewing `tsconfig.json` for a Lambda service, choosing esbuild or webpack with `ts-loader` together with the ORM decision it constrains, deciding `target`, `module` and `moduleResolution` for a bundled ESM-deployed function, diagnosing a bundle that compiles cleanly and fails only once packaged and invoked, moving a service between CommonJS and ESM, or pinning or raising the TypeScript version or the declared Node runtime.

## Version baseline

The skill targets OSLS v4 or Serverless Framework v3, AWS Lambda, and Node.js 24 (`nodejs24.x`). `nodejs22.x` stays in range until its 2027-04-30 deprecation, but never for a new service. A new service starts on OSLS, since Serverless Framework v3 is end of life and its type package stops at `nodejs20.x`. If the project sits outside that range, or on a Node runtime older than 22, the skill stops and reports the mismatch instead of proposing settings tuned for a version it was not written against.

Local conventions outrank the skill's defaults, and a deliberate deviation is recorded rather than silently mixed in.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Baseline `tsconfig.json`** | `target: es2023`, `lib: ["es2023"]`, `module` and `moduleResolution: nodenext`, `types: ["node"]`, `strict`, `isolatedModules`, `esModuleInterop`, `resolveJsonModule`, `skipLibCheck` and `sourceMap`, with `target` and `lib` matched to the Node major declared as the runtime |
| **Runtime pinning** | The Node major in the service configuration, `target`, `lib` and the `@types/node` major must agree, and are re-checked whenever the runtime is bumped. A newer `@types/node` passes the type-check and throws at invocation |
| **Bundler and ORM as one choice** | esbuild cannot emit `emitDecoratorMetadata`, so a decorator-based ORM under esbuild compiles clean and fails at runtime. Three pairings are laid out with their costs: esbuild with Drizzle ORM, webpack with `ts-loader` and TypeORM, and esbuild with TypeORM through a `tsc` or SWC pass |
| **Decorator flags** | `experimentalDecorators`, `emitDecoratorMetadata` and an explicit `useDefineForClassFields: false` belong only to a pairing that uses a decorator-based ORM. Every TypeORM column gets an explicit `type` in every pairing |
| **ESM versus CommonJS** | The ESM-only middy line forces the whole bundle to ESM, which touches `package.json` (`"type": "module"`), `tsconfig.json` (`nodenext`, `.js` suffixes on relative imports) and the bundler output |
| **CommonJS dependencies in an ESM bundle** | Three failure shapes (a dynamic `require()`, a wrongly external dependency, and a mismatch between an ESM wrapper and CommonJS internals), the AWS SDK main-field case, and a diagnostic table by symptom |
| **Source maps** | `sourceMap: true` plus a bundler configured to emit and package a matching map. For deployed code prefer a map without inlined source content |
| **Type-check gate** | The bundler is a transpiler, never a type checker, so `tsc --noEmit` is a separate failing gate |
| **Prisma** | Deliberately not offered as the esbuild pairing, because its query engine is a native binary that must reach the Lambda alongside the bundle |

The skill does not carry a webpack configuration. For the webpack pairing it gives the compiler settings and the shared-output-directory trap, and the webpack config itself is the team's to write.

## How it works

1. **Read the ground truth.** `tsconfig.json`, `package.json` (`type`, `engines`, the pinned TypeScript and `serverless` or OSLS versions) and the service configuration's declared runtime. Note the current bundler and whether the service uses a decorator-based ORM.
2. **Confirm the version baseline**, and stop and report if the project sits outside it.
3. **Settle the bundler-and-ORM pairing before touching decorator flags**, because whether those flags do anything depends on this choice.
4. **Apply the baseline.** Greenfield takes it as written, while an existing config gets the smallest change that serves the task.
5. **Decide the module format** before moving between CommonJS and ESM, or before adding a dependency that might not behave under the bundle's resolution rules.
6. **Verify.** Run `tsc --noEmit`, package the service and inspect the packaged artifact. For any emit-affecting change, invoke the packaged function, because a clean type-check proves nothing about bundler resolution, decorator metadata or module-format mismatches.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Treat the bundler as a transpiler, never a type checker, and run `tsc --noEmit` as a separate mandatory gate |
| MUST | Match the Node runtime declared in the service configuration to `target`, `lib` and the `@types/node` major |
| MUST | Decide the bundler and the ORM together, as one paired choice, before either is adopted alone |
| MUST | Pin an exact TypeScript version in `devDependencies` (no `^`) |
| MUST | Use `module` and `moduleResolution: nodenext` for an ESM-deployed bundle, and keep relative imports between source files suffixed `.js` |
| NEVER | Enable `verbatimModuleSyntax` with `emitDecoratorMetadata` without verifying at runtime first |
| MUST | Verify by executing the packaged artifact after changing anything about how the bundler resolves or externalizes a dependency |

## References

| Reference | Load when |
| :-- | :-- |
| Runtime and module format | Pinning the Node runtime, deciding ESM versus CommonJS for the bundle, or a dependency fails only once packaged |
| Bundler tradeoffs | Choosing or switching the bundler, or a decorator-based entity fails at runtime with no build error |
| Compiler options for serverless | Writing or reviewing a Lambda `tsconfig.json` |

## Related skills

- [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions) owns everything inside the handler once it is compiled.
- [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) owns the deployable service definition and the library policy, which states where the bundler-and-ORM pairing is settled and where it is not.
- [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) in `tsh-stack-nodejs` covers the same language for a Node server process, not a bundled Lambda artifact. Its ESM, CommonJS and module-resolution guidance does not transfer to a bundler-emitted bundle.

The skill does not configure handler code, service or IAM definitions, or non-serverless Node and browser TypeScript.

## Source

[`plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless/SKILL.md)
