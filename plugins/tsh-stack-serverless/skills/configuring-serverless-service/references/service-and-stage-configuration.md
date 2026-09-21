# Service and stage configuration

Use this reference when editing provider-level configuration, stages, tags, timeouts, environment defaults or API Gateway logging — or when choosing the framework itself.

## Table of Contents

- [OSLS, not Serverless Framework v3](#osls-not-serverless-framework-v3)
- [Prefer a typed configuration file over a static one](#prefer-a-typed-configuration-file-over-a-static-one)
- [Stage derivation](#stage-derivation)
- [Naming and tags](#naming-and-tags)
- [Timeouts](#timeouts)
- [Environment defaults](#environment-defaults)
- [API Gateway access logs and stage throttling](#api-gateway-access-logs-and-stage-throttling)
- [Tracing is on](#tracing-is-on)
- [What the pipeline must do](#what-the-pipeline-must-do)
- [CORS defaults belong to the handler layer](#cors-defaults-belong-to-the-handler-layer)

The provider-level configuration every function in the service inherits:
runtime, region, stage, tags, timeouts, and the environment defaults that
are not specific to any one function.

## OSLS, not Serverless Framework v3

A new service installs the framework as OSLS — `"serverless": "npm:osls@^4"`
in `devDependencies`, so the `serverless` binary and every plugin keep working
unchanged. Serverless Framework v3 reached end of life at the close of 2024. On
a Node 22 service that shows up immediately: its configuration schema flags
`nodejs22.x` as an unknown runtime on every package, `@serverless/typescript`
needs a cast for the same value, and it pins AWS SDK v2 — already in
maintenance mode — into every install. None of that is a warning to explain
away in a README; it is the framework telling you it stopped tracking AWS.

## Prefer a typed configuration file over a static one

Serverless Framework and OSLS both accept a `serverless.ts` (or `.js`) that
exports the configuration object, in addition to a static `serverless.yml`.
Where the framework version in use supports it, prefer the typed file: the
whole service configuration then passes through the same type checker as the
rest of the codebase, so a typo in a function key, an invalid runtime
string, or a malformed IAM statement shape fails compilation instead of
surfacing as an obscure deploy-time error. A static YAML file has no such
check.

Whichever form is in use, keep the configuration **concrete by the time the
framework reads it** — resolve environment variables and computed values in
your own code before they reach the configuration object, rather than
leaning on the framework's own variable-resolution syntax for anything
conditional. A value resolved in TypeScript is visible to the type checker
and to a plain `grep`; a value resolved by the framework's own templating
syntax is neither.

## Stage derivation

Read the stage from the deploy invocation (a CLI flag, or the same
convention the framework itself uses) rather than hard-coding it or reading
it from an ambient environment variable that could be stale. Every
stage-dependent value in this configuration — resource names, tags, whether
reserved concurrency is required at all — should derive from that one stage
value, so there is a single source of truth for "which stage is this."

## Naming and tags

Prefix every resource name this service creates with `<service>-<stage>-`.
This is what makes it possible to scope IAM statements to *this* service's
resources with one ARN pattern (see
[`iam-and-secrets.md`](./iam-and-secrets.md)) instead of a wildcard, and it
is what keeps two stages of the same service from colliding in the same
account.

Tag every resource this service creates with at minimum the service name,
the stage, and an owner — whatever your organization's cost-attribution
convention requires. Apply the same tag set at both the stack level and the
resource level; a tag applied only to the stack does not appear on every
resource a cost report queries.

## Timeouts

Set the function timeout to match what actually calls it, not to a generous
round number. A function behind a synchronous HTTP integration should time
out *below* whatever the caller's own timeout is — a Lambda that keeps
running after the caller has already given up wastes execution time paid
for by nobody. A function invoked asynchronously, or from a state machine
task with its own `TimeoutSeconds`, has more room, but that room should
still be a deliberate choice tied to what the function actually does, not a
copy-pasted default.

## Environment defaults

Put values every function needs — the service name, the stage, a log
level, a region — on the provider-level environment rather than repeating
them on every function definition. Reserve function-level environment
entries for values specific to that one function (a secret identifier, a
downstream resource's identifier). Never place a secret value at either
level — see the Non-negotiable Rules table in `SKILL.md` and
[`iam-and-secrets.md`](./iam-and-secrets.md).

## API Gateway access logs and stage throttling

**This section is written for a REST API.** The settings below — the
`provider.logs.restApi` block, `fullExecutionData`, `roleManagedExternally` —
and the throttling call further down are REST-specific. An HTTP API configures
both through `apigatewayv2` with a different access-log format and different
stage settings, which this plugin does not cover yet; treat the *reasoning*
here as transferable and verify every setting name against the v2
documentation before applying it. An HTTP API also has **no execution logging
and no X-Ray**, so its access log is the only gateway-side record there is —
which raises, not lowers, how much the format below matters.

Access logs are the only request-level trail a deployed API has — who called,
from where, how often, and whether the gateway or your code rejected it. A
handler's own log cannot see any of that. Turn them on for every deployed
stage, and hold three settings deliberately:

- **JSON format, every value quoted.** API Gateway substitutes an absent
  `$context` variable with the empty string, and one unquoted empty value makes
  the whole line invalid JSON that Logs Insights drops silently. Log the
  request id and extended request id, source IP, method, route template,
  status, integration status and latency, and the gateway's own error message.
  Never anything that can carry a payload — access logs have no body access,
  and the route *template* keeps the query string out.
- **Full execution data off.** The framework's default is *on*, which sets
  `dataTrace` on the stage and writes complete request and response bodies —
  credentials, personal data — to CloudWatch in plain text. Keep execution
  logging at `ERROR`: the gateway's view of an integration failure is the one
  thing your own logs cannot record.
- **The CloudWatch role is managed outside the stack.** Left to the framework,
  enabling access logs adds a custom-resource Lambda whose role carries
  `iam:CreateRole`, `iam:AttachRolePolicy` and `iam:PassRole` on `role/*` — an
  unscoped wildcard and a privilege-escalation primitive inside your own stack.
  The account-level API Gateway logging role is a one-time, per-account,
  per-region setting the account owner enters by hand; the deploy checks that it
  exists and fails with an actionable message when it does not.

**Stage throttling cannot be expressed in the service configuration.** The
framework exposes `throttle` only inside a usage plan, which applies to API-key
requests alone, and the stage itself is not a CloudFormation resource. Apply
the rate and burst limits from the deploy pipeline immediately after `deploy`
— `aws apigateway update-stage` — from validated variables (positive integers,
burst at or above rate), and **read the applied values back**. A stage deployed
by hand keeps the account default of 10 000 requests per second; the read-back
turns a silently ignored update into a failed deploy instead of an unprotected
endpoint that reports success.

Resolve the REST API's id from the deployed stack — the `ApiGatewayRestApi`
resource, through `describe-stack-resource` or a stack output — never by looking
the API up by name. The name is `<stage>-<service>` by default and
`<service>-<stage>` under `shouldStartNameWithService`, and a script that assumes
one form fails with "not found" the day someone flips the flag.

## Tracing is on

Enable X-Ray for every deployed stage: `tracing: { lambda: true, apiGateway: true }`
at provider level, and `tracingConfig: { enabled: true }` on every state machine.
**`apiGateway: true` applies to a REST API only** — API Gateway does not support
X-Ray on an HTTP API at all, so a service on HTTP API gets Lambda and state
machine traces with no gateway segment in front of them, and the trace starts at
the function rather than at the request. Set only `lambda: true` there, and know
that the gateway's own latency and its integration errors are invisible to
tracing; its access log is the only record.
A trace is the only view that joins the gateway, the function, the state machine
and the downstream call into one request; logs alone reconstruct it by hand, if
at all. This is what the `xray:*` entries in the wildcard carve-out exist for — a
carve-out for actions nothing uses is dead weight in the check. The cost is per
sampled trace, and the default sampling rule keeps it small.

## What the pipeline must do

Three obligations in this reference land on "the pipeline", and a service is
not deployable until something actually carries them. This is the contract;
how it is built — the CI system, OIDC to the account, the deploy role's
permissions — belongs to `tsh-platform-engineering`, referenced by name and
never assumed installed.

1. **Preflight.** Before deploying, check the account-level API Gateway
   CloudWatch logging role exists in the target region and fail with an
   actionable message when it does not; the stack deliberately does not manage
   it. Check the deploy role can read the stage's database secret only if a
   step of the pipeline genuinely needs the value — packaging never does.
2. **Deploy, then throttle.** Run `deploy` for the stage, then apply the
   stage's rate and burst limits and read them back, per the section above.
   A deploy whose throttle step is skipped ships an unprotected endpoint that
   reports success.
3. **Migrate from inside the network.** Run the database migrations against
   the stage's database from somewhere that can reach it — for a database with
   no public endpoint, that is a migration function inside the VPC, not a
   developer machine or a runner on the public internet. The expand phase runs
   before the application deploys; a contract phase is a separately approved
   run after an observation window.

Write the contract into the generated `README.md` under *Deploying*, as a
numbered list the pipeline author can tick off. A README that says "the
pipeline applies throttling" without saying that there is no pipeline yet is
how the account default of 10 000 requests per second reaches production.

## CORS defaults belong to the handler layer

Provider-level configuration is the wrong place to decide CORS behavior in
detail — allowed origins and whether credentials are permitted are an
event-boundary concern with a specific failure mode of their own. See
[`implementing-lambda-functions`](${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/SKILL.md)
for the rule against wildcard origins combined with credentials.

## Sources

Verified 2026-09-18:

- [What will happen with V3 apps on 1st Jan 2025 — serverless/serverless discussion](https://github.com/serverless/serverless/discussions/12899) — v3 receives no security fixes after 2024
- [Serverless Framework — Upgrading to v4](https://www.serverless.com/framework/docs/guides/upgrading-v4) — the licensing and bundler changes that make v4 a different product line
- [Serverless Framework — API Gateway events](https://www.serverless.com/framework/docs/providers/aws/events/apigateway) — the `logs` block: `fullExecutionData`, `roleManagedExternally`, access-log format

The OSLS alias (`npm:osls@^4`) and the runtime list the v3 schema stops at were checked
against the npm registry on the same date; both move.
