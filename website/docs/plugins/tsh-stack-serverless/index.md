---
title: 'TSH Stack: Serverless'
sidebar_label: Overview
sidebar_position: 0
description: TSH practices for AWS Lambda services on OSLS v4 with Node.js 24 on arm64, covering library policy, project structure, TypeScript and bundler configuration, handler implementation, and the deployable service definition.
sources:
  - plugins/tsh-stack-serverless/.claude-plugin/plugin.json
  - plugins/tsh-stack-serverless/README.md
sources_hash: "27653af37aca659146b6bac2a22e9476c10c81ffcb03799cd4be62fe018b53ca"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: Serverless

`tsh-stack-serverless` carries TSH's practices for AWS Lambda services on OSLS v4 (the `osls` npm package, the community-maintained open-source fork of Serverless Framework v3) with Node.js 24 on `arm64`. It states what TSH recommends and when, which libraries it uses and which it avoids, and covers compiler and bundler configuration, handler implementation, and the deployable service definition. It ships no bootstrap and no example project: the practices are what make a service come out TSH-shaped.

## Who installs it and where

Install it at **project scope**, into the projects that deploy to Lambda, so it travels with the repository: the repository already knows what it deploys to. Your discipline plugin (for example [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)) and [`tsh-core`](/docs/plugins/tsh-core/) travel with you at user scope. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here.

Once installed, skills are invoked as `/tsh-stack-serverless:<skill>`. Release notes are on the [changelog page](/docs/changelog/tsh-stack-serverless).

## What it ships

<PluginComponents plugin="tsh-stack-serverless" />

All three skills are model-invocable: Claude loads them when the work matches their description, so you do not have to type the command.

The skills split the work along the seams of a Lambda service:

| Skill | Owns |
| :-- | :-- |
| [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) | Compiling and bundling: the runtime and TypeScript version, the ESM `tsconfig.json` baseline, and the bundler-and-ORM pairing |
| [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions) | The handler layer: the thin-handler and pure-service split, middy middleware, validation, errors, logging and tests |
| [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) | The deployable service definition and the library policy |

## Choices this plugin has an opinion on

The plugin takes a position on some choices and deliberately does not on others. The full policy, including what TSH avoids and why, lives in the `library-policy.md` reference of `configuring-serverless-service`.

**Settled:** OSLS v4 over Serverless Framework (v3 is end of life and v4 is a different product), the service configuration in TypeScript rather than `serverless.yml`, middy 7, zod, PostgreSQL, Secrets Manager, and Step Functions with the definition in ASL.

**Not settled:** the ORM for a new service, and the test runner. The plugin says so and tells the model to ask rather than pick.

Three of those decisions change which of the plugin's other rules still apply:

- **The bundler and the ORM are one choice, not two.** esbuild cannot emit `emitDecoratorMetadata`. Paired with a decorator-based ORM, entities compile with no build error while the metadata is silently dropped, and the failure surfaces at runtime as a missing or wrongly guessed column type. So the two are decided together: webpack with `ts-loader` for a decorator-based ORM, esbuild for a decorator-free one, or esbuild behind a compiler pass when a decorator-based ORM is non-negotiable.
- **REST API is what the operational guidance covers end to end.** Access logging, stage throttling and the packaged-template checks are written against it. HTTP API is cheaper per request and ships a built-in JWT authorizer, but it has no X-Ray tracing, no execution logs, no WAF, no API keys or per-client throttling, no resource policies or private endpoints, and no caching.
- **PostgreSQL is the assumed datastore.** The connection-budget arithmetic, the secret's shape and the local `docker-compose.yaml` are built around a connection-per-invocation relational database.

## Scope and neighbours

Infrastructure defined by the service (its functions, the execution role they run under, API Gateway, Step Functions) belongs here. Infrastructure that outlives the service and is managed with Terraform (VPC, RDS, networking) belongs in [`tsh-stack-aws`](/docs/plugins/tsh-stack-aws/). A repository that runs Lambda behind a VPC and a managed database installs both plugins. How to build the deploy pipeline (the CI system, OIDC and the deploy role) belongs to [`tsh-platform-engineering`](/docs/plugins/tsh-platform-engineering/).

The compiler guidance has near-twins in [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) (`configuring-typescript-for-nodejs`) and [`tsh-stack-frontend`](/docs/plugins/tsh-stack-frontend/skills/configuring-typescript-for-frontend) (`configuring-typescript-for-frontend`). Version policy and the strictness ladder exist in all three on purpose, because skills cannot link across plugins, and the target-specific parts, such as the bundler-and-ORM pairing, stay different.

## MCP servers, hooks and agents

This plugin ships no agents, no `.mcp.json` and no hooks.

## Not covered yet

The plugin README lists these gaps as deliberate scope:

- **Databases**, planned for v0.2 as `accessing-databases-from-lambda`: connection lifecycle per execution environment, pool size against reserved concurrency, and expand and contract migrations.
- **Step Functions beyond the basics.** The task rules are covered, while `Map` and `Parallel`, compensation and running a workflow locally are planned for v0.2 as `implementing-step-functions-workflows`.
- **Authentication.** The source material carries no example, and inventing one would be guidance TSH has not agreed to.
- **The deploy pipeline itself.** `configuring-serverless-service` states what the pipeline must do, and building it belongs to `tsh-platform-engineering`.
- **Webpack configuration**, beyond the compiler settings and the shared-output-directory trap.
- **Event sources other than HTTP and Step Functions**, such as SQS with partial-batch response, schedules and EventBridge rules. The handler side is covered, while the event-source and IAM configuration is not.
- **Datastores other than PostgreSQL.**
- **The ORM and the test runner for a new service.** These are open team decisions, not coverage gaps.
- **HTTP API operations.** The access-logging, stage-throttling and packaged-template guidance is written for REST API.
- **Scaling beyond one stack**: when to split a service and how to shape configuration across several of them.
- **Multi-account deployment.**

## Source

- [`plugins/tsh-stack-serverless/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-serverless/README.md)
- [`plugins/tsh-stack-serverless/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-serverless/.claude-plugin/plugin.json)
