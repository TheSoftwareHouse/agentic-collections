---
name: configuring-serverless-service
description: "TSH practices for defining an AWS Lambda service on OSLS: which libraries we use and which we avoid, how a serverless project is structured, service and stage configuration, least-privilege IAM without wildcard resources, per-function reserved concurrency, opt-in VPC attachment, secrets passed by identifier and resolved at runtime, and assertions over the packaged CloudFormation template. Use when creating or changing serverless.ts, adding a function, or choosing a dependency."
when_to_use: "Trigger on: starting or changing an OSLS service, editing serverless.ts, adding a function definition, choosing an ORM, bundler, test runner or any dependency for a serverless service, laying out a serverless project, scoping an IAM statement for a Lambda execution role, setting reservedConcurrency, attaching a function to a VPC, passing a secret to a function, naming CloudFormation resources, or checking a packaged template before deploying."
---

# Configuring a serverless service

Owns the **deployable service definition**: service and stage configuration,
per-function definitions, the execution role, reserved concurrency, VPC
attachment, secrets, and what to assert over the packaged CloudFormation
template. It does not own what happens inside a handler — that is
[`implementing-lambda-functions`](${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/SKILL.md) —
nor the compiler and bundler that produce the deployed artifact — that is
[`configuring-typescript-for-serverless`](${CLAUDE_PLUGIN_ROOT}/skills/configuring-typescript-for-serverless/SKILL.md).

## Applicability and Precedence

Read the project's existing `serverless.ts` and `config/` (or equivalent)
before proposing anything. Local conventions and an existing account topology
outrank this skill's defaults; apply this guidance where the project is silent,
and in a repository that has nothing yet it is the convention to build to.

## Version Baseline

This skill targets **AWS Lambda through OSLS v4 or Serverless Framework v3,
Node.js 24** (`nodejs24.x` on `arm64`; `nodejs22.x` stays in range until its
2027-04-30 deprecation, never for a new service). The two frameworks are not equals: **a new service installs OSLS** —
`"serverless": "npm:osls@^4"` — never Serverless Framework v3. v3 reached end
of life at the close of 2024: no security fixes, a runtime schema and type
package that stop at `nodejs20.x`, and AWS SDK v2 pinned underneath. It stays
in range so an existing v3 project still gets this guidance, not so a new one
starts on it. Before applying anything here, read the project's `package.json`
for the installed `serverless` or `osls` major and engine range. Outside that
range — Serverless Framework v4 is a different product line, with its own
licensing and a built-in bundler — stop and say so rather than applying this
skill's guidance as if it still applied.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| NEVER | Put a secret value in a function's `environment`. The value is stored verbatim in the CloudFormation template and readable by anyone who can read the stack or call `lambda:GetFunctionConfiguration`. Pass an identifier instead, and resolve the value at runtime from a secrets store. |
| NEVER | Write an IAM statement with `Resource: "*"` or a wildcard `Action`. Scope every statement to this service. The exception is the narrow, named set of actions AWS itself defines no resource type for — X-Ray's write actions, CloudWatch Logs' delivery actions, and the ENI actions Lambda needs for VPC attachment — list those explicitly with the reason, never match them with a pattern. Without that carve-out the rule reads as unsatisfiable and gets abandoned outright. |
| MUST | Give every deployed function its own `reservedConcurrency`. A function without one draws on the account's unreserved pool, so one endpoint under load starves every other function in the account — and, for anything database-backed, can open more connections than the pool budget assumes. |
| NEVER | Reference a CloudFormation resource by a logical id you wrote by hand. Derive it with the framework's own rule (non-alphanumeric characters replaced, first character upper-cased). A hand-written id packages cleanly and fails minutes into a deploy with an unresolved reference. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Service and stage configuration](./references/service-and-stage-configuration.md) | Editing provider-level config, stages, environment defaults, the health endpoint, access logs or throttling | Stage derivation, timeouts, tags, per-stage environment values, the health endpoint contract, access logging, stage throttling, tracing, the pipeline contract |
| [IAM and secrets](./references/iam-and-secrets.md) | Writing or reviewing an IAM statement, or passing a secret to a function | Least-privilege statement shape, the wildcard carve-out, secret containers vs secret values |
| [Concurrency and VPC](./references/concurrency-and-vpc.md) | Setting `reservedConcurrency`, or deciding whether a function needs a VPC | The starvation and connection-budget argument, VPC as opt-in and its cost |
| [Packaging and template checks](./references/packaging-and-template-checks.md) | Adding or reviewing a check that runs against the packaged template | What to assert over the packaged CloudFormation template, and why packaging time is the last cheap moment to catch it |
| [Library policy](./references/library-policy.md) | Choosing or reviewing any dependency, pinning a version, or hitting a choice the team has not settled | What TSH uses, what it avoids and why, the two open questions, resolving versions from the registry, the lint and commit toolchain |
| [Project structure](./references/project-structure.md) | Laying out a service, adding a file, or reviewing where something was put | How a TSH serverless service is shaped and what each file is responsible for |
| [Local development](./references/local-development.md) | Setting up or fixing how the service runs on a developer's machine | `serverless-offline` as dependency **and** plugin, the `local` stage, `.env.dist`, a local database |
| [Step Functions workflows](./references/step-functions-workflows.md) | The service orchestrates anything, adding a task to a state machine, or a task's error must be caught by the state machine | One function per task, `Retry` and `Catch` in the state machine, `TimeoutSeconds` below the function timeout, error names as string literals |

## Procedure

**Step 1 — Read the ground truth.** The service definition, `config/`, and the
packaged template from the last successful package if one exists. Note which
execution role each function uses and which stage names actually deploy. In a
repository with none of that yet, read
[`project-structure.md`](./references/project-structure.md) and
[`library-policy.md`](./references/library-policy.md) instead — they are the
conventions a new service follows, and following them is what makes the result
look like every other TSH serverless service.

**Step 2 — Load what the work touches.** Choosing a dependency →
[`library-policy.md`](./references/library-policy.md). Adding a function →
[`service-and-stage-configuration.md`](./references/service-and-stage-configuration.md)
and [`concurrency-and-vpc.md`](./references/concurrency-and-vpc.md). A new
permission or secret → [`iam-and-secrets.md`](./references/iam-and-secrets.md).
A state machine task →
[`step-functions-workflows.md`](./references/step-functions-workflows.md).
Running it on a developer machine →
[`local-development.md`](./references/local-development.md).

**Step 3 — Apply the rules.** Every function declares `reservedConcurrency` and
an execution role built from scoped statements; a secret is a container plus an
identifier, never a value; a CloudFormation reference is derived, never typed by
hand; an HTTP service has a health endpoint that answers only `ok` or
`unavailable`; every real repository has an integration test against the local
database.

**Step 4 — Package and check.** Package for the target stage and run the
assertions from
[`packaging-and-template-checks.md`](./references/packaging-and-template-checks.md),
including executing the packaged artifact. Work that packages but fails a check
is not done.

**On a choice the team has not settled** — the greenfield ORM, the test runner —
ask rather than pick: in the main conversation with `AskUserQuestion`, as a
subagent by reporting the blocker to the caller. See
[`library-policy.md`](./references/library-policy.md).

## Review Procedure

Review the **packaged template**, not only the diff — plugins generate roles and
resources the diff never shows. Apply the four Non-negotiable Rules to every role
and function in it, check each state machine task's `TimeoutSeconds` against its
function's timeout, and report findings by severity with the reference that owns
each violated rule.

## Related Skills

- [`implementing-lambda-functions`](${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/SKILL.md) —
  the handler code that runs inside a function this skill defines.
- [`configuring-typescript-for-serverless`](${CLAUDE_PLUGIN_ROOT}/skills/configuring-typescript-for-serverless/SKILL.md) —
  the compiler and bundler that produce the artifact this skill packages and
  deploys; owns the full bundler-and-ORM pairing reasoning.
