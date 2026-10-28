# Library policy

Use this reference when choosing a dependency for a serverless service, or
reviewing one somebody else chose. It states what TSH uses, what TSH avoids,
and — for the two questions the team has not settled — what to do instead of
inventing a default.

## Table of Contents

- [Settled](#settled)
- [Not settled yet](#not-settled-yet)
- [What we avoid, and why](#what-we-avoid-and-why)
- [Adding a dependency that is not listed](#adding-a-dependency-that-is-not-listed)
- [Versions come from the registry, never from memory](#versions-come-from-the-registry-never-from-memory)
- [The toolchain every service carries](#the-toolchain-every-service-carries)

## Settled

| Concern | We use | Notes |
| --- | --- | --- |
| Framework | **OSLS v4** — `"serverless": "npm:osls@^4"` | The `serverless` binary and every plugin keep working unchanged under the alias. |
| Service configuration | **TypeScript** — `serverless.ts` plus a per-function definition | Not `serverless.yml`: the configuration then passes the same type checker as the rest of the code, and a value resolved in TypeScript is visible to `grep`. |
| HTTP middleware | **middy 7** | Import-only ESM, which is what forces the deployed bundle to ESM. |
| Validation | **zod** | One schema per function covering the whole event; the payload type is inferred from it, never written a second time. |
| Runtime | **Node 24 on `arm64`** — `nodejs24.x`, supported by Lambda until 2028-04-30; `nodejs22.x` is deprecated on 2027-04-30 | `target`, `lib` and `@types/node` all match this major. |
| Database | **PostgreSQL** | The connection-budget arithmetic and the secret's shape assume a connection-per-invocation relational database. |
| Secrets | **AWS Secrets Manager** | The stack owns the container, a human owns the value, the function receives an identifier. |
| Orchestration | **Step Functions**, definition in ASL | Declarative YAML, one directory per step. |
| Structured logging | **JSON to stdout**, one line per event, request id on every line | The library is not the point; the shape is. Whatever the project uses must carry timestamp, level, service, stage and request id. |

## Not settled yet

Two choices the team has deliberately left open. "Open" does **not** mean pick
one quietly — it means the rules below apply.

**The ORM for a greenfield service.** TSH runs **TypeORM 0.3** in production
today and has stated the intent to move to something lighter, without naming a
replacement. So:

- An existing service stays on what it has. Do not migrate an ORM as a side
  effect of another task.
- A new service inherits the decision from the team, not from the model. Ask
  which ORM to use (in the main conversation) or report it as a blocker (as a
  subagent) rather than choosing.
- Whatever is chosen, the **bundler pairing rule still decides half of it**: a
  decorator-based ORM needs `emitDecoratorMetadata`, which esbuild cannot
  produce. See
  `${CLAUDE_PLUGIN_ROOT}/skills/configuring-typescript-for-serverless/references/bundler-tradeoffs.md`.
  A decorator-free ORM removes the constraint; a decorator-based one forces
  webpack with `ts-loader`, or a compiler pass ahead of esbuild.

**The test runner.** The reference boilerplate uses **mocha with sinon,
`node:assert` and c8** — a real, working choice, not yet blessed as the house
standard for new services. So follow the repository's existing runner, and for
a repository with none, ask rather than introduce one. The *layers* are
settled regardless of runner and are in
`${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/references/testing-lambda-code.md`:
a service test with fakes, a handler test when the chain is the behaviour, and
an integration test per real repository.

| Severity | Rule |
| --- | --- |
| MUST | Treat an unsettled choice as a question for the team, not a gap to fill with a default. |
| NEVER | Migrate an existing service's ORM or test runner as a side effect of an unrelated task. |

## What we avoid, and why

| Not used | Reason |
| --- | --- |
| **Serverless Framework v3** | End of life since the close of 2024: no security fixes, a runtime schema and type package that stop at `nodejs20.x`, AWS SDK v2 pinned underneath. |
| **Serverless Framework v4** | A different product line with its own licensing and a built-in bundler; not what this guidance is written against. |
| **`serverless.yml`** | No type checking over the service definition, and framework-templated values are invisible to both the compiler and `grep`. |
| **Prisma** | The query engine is a separate native binary that has to reach the Lambda alongside the bundle — a packaging problem the pure-TypeScript alternatives do not have. |
| **Managed IAM policies** | Permissions nobody reviewing this service's code can see. Write every statement out, including the CloudWatch Logs boilerplate. |
| **A secret value in a function's environment** | Stored verbatim in the CloudFormation template and readable through `lambda:GetFunctionConfiguration`. |
| **Retry logic inside a workflow task** | Retries belong to the state machine; a task that also retries itself multiplies attempts against a downstream that is already failing. |
| **`console.*` in application code** | Bypasses the structured format, the redaction and the request-id enrichment the logger provides. |

## Adding a dependency that is not listed

Three questions, in order. A dependency that fails the first is a defect
regardless of how convenient it is.

1. **Does it reach the Lambda, and how?** A native binary or a
   platform-specific artifact is a packaging decision, not just an install —
   see the module-format reference. A pure-TypeScript library is free.
2. **Does it force the module format?** An import-only package pushes the
   whole bundle to ESM; one that only ships CommonJS internals may break
   inside an ESM bundle in ways no type-check or source-level test sees.
3. **Does it duplicate something already on the list?** A second schema
   library, a second logger or a second HTTP client in one service is a
   maintenance cost with no offsetting benefit.

## Versions come from the registry, never from memory

Resolve the current version of every dependency at the moment you add it:

```shell
npm view <package> version
```

Write that, within the constraints the rest of this guidance sets:
`@types/node` at the deployed runtime's major, TypeScript pinned exactly (no
`^` — it does not follow semver for its error surface), the framework as
`npm:osls@^4`.

A version recalled rather than looked up is the version from a model's
training data, months to a year stale, and nothing in a build warns about it.
This is not hypothetical: an earlier service written against this guidance
came out with `drizzle-orm ^0.38` against a registry at `0.45`, `zod ^3.24`
against `4.6`, and TypeScript `5.7.2` against `7.0` — a whole major behind on
two of them, installed clean, tests green.

**The newest is not always installable.** `latest` from the registry can be
ahead of the toolchain that has to work with it, and the lint step is where this
bites: typescript-eslint declares a peer range on TypeScript and refuses to
start outside it, so the newest compiler and a working `lint` cannot both be
satisfied. Lint is a settled part of the gate, so the compiler waits. Pin the
newest version that the whole gate accepts, record why in a decision record, and
revisit when the blocker ships support — do not drop lint from `verify` to make
room for a compiler.

| Severity | Rule |
| --- | --- |
| MUST | Resolve every dependency version from the registry when adding it; never write one from memory. |
| MUST | Pin TypeScript exactly, and match `@types/node` to the runtime's major. |
| MUST | Pin the newest version that passes the whole `verify` gate, not the newest that exists. A version that breaks lint is not installable, whatever the registry says. |

## The toolchain every service carries

Settled, and not interesting enough to re-decide per project:

| Concern | We use |
| --- | --- |
| Lint | **ESLint**, flat config, with **Prettier** as the formatter |
| Pre-commit | **lint-staged** on a hook, so the gate runs on what is being committed |
| Commit messages | **commitlint** with the conventional config |

These belong in the `verify` gate as its `lint` step — see
[`packaging-and-template-checks.md`](./packaging-and-template-checks.md). A
service whose `verify` has no `lint` step is missing one, not opting out.

## Sources

Verified 2026-09-21:

- [What will happen with V3 apps on 1st Jan 2025 — serverless/serverless discussion](https://github.com/serverless/serverless/discussions/12899) — v3 receives no security fixes after 2024
- [Serverless Framework — Upgrading to v4](https://www.serverless.com/framework/docs/guides/upgrading-v4) — the licensing and bundler changes that make v4 a different product line
- [Choose between REST APIs and HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html) — the feature matrix behind the gateway position

Package majors (`osls@4`, `middy@7`) were checked against the npm registry on the
same date and move independently of this file. The two unsettled choices are
unsettled as of that date — if the team has since decided, this table is the place
to record it.
