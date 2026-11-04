---
title: Configuring a Serverless Service
sidebar_label: configuring-serverless-service
sidebar_position: 3
description: TSH practices for defining an AWS Lambda service on OSLS, covering the library policy, project structure, stage configuration, least-privilege IAM, reserved concurrency, opt-in VPC, secrets resolved at runtime, and checks over the packaged template.
sources:
  - plugins/tsh-stack-serverless/skills/configuring-serverless-service/
sources_hash: "d16d7e4f84fb82cf7a7815dc6de8745d7c74d3fc55c807b1b9c050c1353482b6"
---

# Configuring a Serverless Service

**Plugin:** [`tsh-stack-serverless`](/docs/plugins/tsh-stack-serverless/)  
**Invoke:** `/tsh-stack-serverless:configuring-serverless-service`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions) and [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) link to it as the owner of the deployable service definition and the library policy. The security checklist of [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) names Lambda IAM among the stack-specific defenses that live in the installed stack skill.

The skill owns the deployable service definition: service and stage configuration, per-function definitions, the execution role, reserved concurrency, VPC attachment, secrets, and what to assert over the packaged CloudFormation template. It does not own what happens inside a handler, which is [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions), nor the compiler and bundler that produce the deployed artifact, which is [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless).

Use it when starting or changing an OSLS service, editing `serverless.ts`, adding a function definition, choosing an ORM, bundler, test runner or any dependency for a serverless service, laying out a project, scoping an IAM statement for a Lambda execution role, setting `reservedConcurrency`, attaching a function to a VPC, passing a secret to a function, naming CloudFormation resources, or checking a packaged template before deploying.

Local conventions and an existing account topology outrank the skill's defaults. In a repository that has nothing yet, the skill is the convention to build to.

## Version baseline

The skill targets AWS Lambda through OSLS v4 or Serverless Framework v3, Node.js 24 (`nodejs24.x` on `arm64`; `nodejs22.x` stays in range until its 2027-04-30 deprecation, but never for a new service). The two frameworks are not equals: a new service installs OSLS as `"serverless": "npm:osls@^4"`, never Serverless Framework v3. v3 reached end of life at the close of 2024, with no security fixes, a runtime schema and type package that stop at `nodejs20.x`, and AWS SDK v2 pinned underneath. It stays in range only so an existing v3 project still gets this guidance. Serverless Framework v4 is a different product line with its own licensing and a built-in bundler, and outside the range, so the skill stops and says so instead of applying its guidance.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Library policy** | Settled choices: OSLS v4, `serverless.ts`, middy 7, zod, Node 24 on `arm64`, PostgreSQL, Secrets Manager, Step Functions in ASL, structured JSON logging. Avoided: Serverless Framework v3 and v4, `serverless.yml`, Prisma, managed IAM policies, secrets in `environment`, retries inside workflow tasks, `console.*`. Versions are resolved from the registry, never from memory |
| **Open choices** | The ORM for a greenfield service (TSH runs TypeORM 0.3 today and has stated the intent to move to something lighter) and the test runner. The skill asks rather than picks, and never migrates an existing service as a side effect |
| **Toolchain every service carries** | ESLint flat config with Prettier, lint-staged on a hook, commitlint with the conventional config, all inside the `verify` gate |
| **Project structure** | `serverless.ts`, `config/` split by concern, `functions/<name>/` with `function.ts`, `handler.ts`, `service.ts` and `event.schema.ts`, `shared/`, `workflows/`, `scripts/`, `test/integration/`, `docs/decisions/` and `.env.dist` |
| **Service and stage configuration** | A typed configuration file, no setting written at its own default, stage derived from the deploy invocation, `<service>-<stage>-` resource prefix and tags, timeouts tied to the caller, a `GET /health` endpoint that answers only `ok` or `unavailable`, API Gateway access logs, X-Ray tracing, and the pipeline contract |
| **IAM** | Roles split by capability, no managed policies, every statement names concrete actions and resources. The wildcard carve-out is a named set: X-Ray write actions, CloudWatch Logs delivery actions, and the ENI actions for VPC attachment |
| **Secrets** | The stack owns the secret's container and a human owns the value. A function receives an identifier (`<SOMETHING>_SECRET_ID`), resolves the value at runtime in the init phase, and its role reads exactly one secret |
| **Reserved concurrency** | Every deployed function declares its own, as an account-wide blast-radius control and, for database-backed functions, as the connection budget. The budget belongs to the database, not the service. Only local emulation is exempt |
| **VPC** | Opt-in through a single explicit switch, because attaching by default breaks a clean checkout and adds NAT cost. A missing id fails at packaging time |
| **Packaged-template checks** | No wildcard IAM in any role, concurrency on every deployed function, no dangling logical-id reference, malformed-configuration checks, executing the packaged artifact, the `verify` gate, and the 500-resource CloudFormation limit |
| **Local development** | `serverless-offline` installed and registered, a `local` stage that exists only for emulation, `.env.dist` as the contract, a local PostgreSQL through `docker-compose.yaml`, and a database browser behind a Compose profile |
| **Step Functions** | One function per task, one directory per workflow and per step, `Retry` and `Catch` in the state machine, `TimeoutSeconds` below the function timeout, error names as string literals, and idempotent tasks |

## How it works

1. **Read the ground truth**: the service definition, `config/` and the packaged template from the last successful package if one exists. In a repository with none of that, read the project-structure and library-policy references instead.
2. **Load what the work touches.** A dependency goes to the library policy, a new function to the service configuration and concurrency references, a permission or secret to IAM and secrets, a state machine task to the Step Functions reference, and a developer-machine concern to local development.
3. **Apply the rules.** Every function declares `reservedConcurrency` and an execution role built from scoped statements, a secret is a container plus an identifier, a CloudFormation reference is derived, an HTTP service has a health endpoint, and every real repository has an integration test against the local database.
4. **Package and check.** Package for the target stage and run the assertions from the packaged-template reference, including executing the packaged artifact. Work that packages but fails a check is not done.

On a choice the team has not settled, such as the greenfield ORM or the test runner, the skill asks in the main conversation, and a subagent reports the blocker to its caller.

For review, the skill reviews the packaged template and not only the diff, because plugins generate roles and resources the diff never shows. It applies the four rules below to every role and function in it, checks each state machine task's `TimeoutSeconds` against its function's timeout, and reports findings by severity.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| NEVER | Put a secret value in a function's `environment`. Pass an identifier and resolve the value at runtime from a secrets store |
| NEVER | Write an IAM statement with `Resource: "*"` or a wildcard `Action`, except the narrow named set of actions AWS defines no resource type for, each listed explicitly with its reason |
| MUST | Give every deployed function its own `reservedConcurrency` |
| NEVER | Reference a CloudFormation resource by a logical id written by hand. Derive it with the framework's own rule |

## What the pipeline must do

The service configuration reference defines a contract that the deploy pipeline carries: preflight (check that the account-level API Gateway CloudWatch logging role exists in the target region), deploy then apply stage throttling and read the applied values back, and run database migrations from inside the network. The contract is written into the service's own `README.md` under *Deploying*. How the pipeline is built (the CI system, OIDC to the account, the deploy role) belongs to `tsh-platform-engineering`.

## References

| Reference | Load when |
| :-- | :-- |
| Service and stage configuration | Editing provider-level config, stages, environment defaults, the health endpoint, access logs or throttling |
| IAM and secrets | Writing or reviewing an IAM statement, or passing a secret to a function |
| Concurrency and VPC | Setting `reservedConcurrency`, or deciding whether a function needs a VPC |
| Packaging and template checks | Adding or reviewing a check that runs against the packaged template |
| Library policy | Choosing or reviewing any dependency, pinning a version, or hitting a choice the team has not settled |
| Project structure | Laying out a service, adding a file, or reviewing where something was put |
| Local development | Setting up or fixing how the service runs on a developer's machine |
| Step Functions workflows | The service orchestrates anything, adding a task to a state machine, or a task's error must be caught by the state machine |

## Related skills

- [`implementing-lambda-functions`](/docs/plugins/tsh-stack-serverless/skills/implementing-lambda-functions) covers the handler code that runs inside a function this skill defines.
- [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) covers the compiler and bundler that produce the artifact this skill packages and deploys, and owns the full bundler-and-ORM pairing reasoning.
- The project-structure reference points to [`managing-decision-records`](/docs/plugins/tsh-core/skills/managing-decision-records) and [`managing-claude-context`](/docs/plugins/tsh-core/skills/managing-claude-context) in `tsh-core` for a service's `docs/decisions/`, `CLAUDE.md` and `AGENTS.md`.

## Source

[`plugins/tsh-stack-serverless/skills/configuring-serverless-service/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-serverless/skills/configuring-serverless-service/SKILL.md)
