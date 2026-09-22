# TSH Stack: Serverless

TSH practices for AWS Lambda services on OSLS v4, Node.js 22+ — what we
recommend and when, which libraries we use and which we avoid: compiler and bundler configuration, handler
implementation, and the deployable service definition.

This is a **stack** plugin, not a discipline plugin. Install it into the
projects that deploy to Lambda, at `project` scope, so it travels with the
repo — the repo already knows what it deploys to. Your discipline plugin
(`tsh-product-engineering` and friends) travels with **you**, at `user`
scope, and so does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-serverless@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `configuring-typescript-for-serverless` | `/tsh-stack-serverless:configuring-typescript-for-serverless` | Node runtime and TypeScript version to target, the `tsconfig.json` baseline for bundler-emitted ESM handler code, and choosing esbuild versus webpack with `ts-loader` |
| `implementing-lambda-functions` | `/tsh-stack-serverless:implementing-lambda-functions` | The thin-handler and pure-service split, middy middleware chain ordering, event validation against one schema, the `AppError` → `HttpError` hierarchy, structured logging, init-phase work, testing, and a review checklist |
| `configuring-serverless-service` | `/tsh-stack-serverless:configuring-serverless-service` | Service and stage configuration, per-function definitions, least-privilege IAM, per-function reserved concurrency, opt-in VPC attachment, the library policy — what we use, what we avoid, and the two choices the team has not settled — how a serverless project is structured, service and stage configuration, least-privilege IAM, per-function reserved concurrency, opt-in VPC, secrets resolved at runtime, packaged-template checks, API Gateway access logs and stage throttling, local development with `serverless-offline`, and Step Functions task rules |

All three are model-invocable — Claude loads them when the work matches
their description, so you don't have to remember to type the command.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates
arrive with `/plugin update`.

## Choices this plugin has an opinion on

Where this plugin takes a position, and where it deliberately does not. The
full policy — including what we avoid and why — is in
`configuring-serverless-service`'s `library-policy.md`.

**Settled:** OSLS v4 over Serverless Framework (v3 is end of life, v4 a
different product), the service configuration in TypeScript rather than
`serverless.yml`, middy 7, zod, PostgreSQL, Secrets Manager, Step Functions
with the definition in ASL. **Not settled:** the ORM for a new service, and
the test runner — the plugin says so and tells the model to ask rather than
pick.

Three of those decisions change which of this plugin's other rules still
apply, so none of them is silent about what it costs.

- **The bundler and the ORM are one choice, not two** — whichever ORM the team
  settles on. esbuild cannot emit
  `emitDecoratorMetadata` and never will — the emit needs TypeScript's type
  system, which esbuild deliberately does not have. Pair it with a
  decorator-based ORM and entities compile with **no build error** while the
  metadata is silently dropped, surfacing at runtime as a missing or
  wrongly-guessed column type. So the two are decided together: webpack with
  `ts-loader` for a decorator-based ORM, esbuild for a decorator-free one, or
  esbuild behind a compiler pass when a decorator ORM is non-negotiable.
  `configuring-typescript-for-serverless` carries the full trade-off table.

- **REST API is what the operational guidance covers end to end.** Access
  logging, stage throttling and the packaged-template checks are written
  against it, and it is what the source boilerplate runs. HTTP API is cheaper
  per request, lower latency and ships a built-in JWT authorizer — but it has
  **no X-Ray tracing at all**, no execution logs, no WAF, no API keys or
  per-client throttling, no resource policies or private endpoints, and no
  caching. Reach for HTTP API when the API is consumed by your own frontend
  behind JWT and none of that list matters; reach for REST when any of it
  does — in practice WAF decides it for anything public. Note that gateway
  request validation is a weaker argument here than it looks: this plugin
  already requires the handler to validate the whole event against one schema,
  so the gateway's copy saves a billed invocation, not a class of bug.

- **PostgreSQL is the assumed datastore.** The connection-budget arithmetic,
  the secret's shape and the local `docker-compose.yaml` are all built around
  a connection-per-invocation relational database. Another engine works; a
  request-per-call datastore like DynamoDB makes most of that reasoning
  meaningless rather than merely different.

## Not covered yet

Deliberate gaps, so they read as scope rather than oversight:

- **Databases** — planned for v0.2 as `accessing-databases-from-lambda`:
  connection lifecycle per execution environment, pool size against reserved
  concurrency, and expand/contract migrations. It needs a Drizzle track and a
  TypeORM track rather than one neutral procedure, because the migration
  tooling differs between them, not only the entity syntax — which is why it
  did not ship with v0.1.0.
- **Step Functions beyond the basics** — the task rules are covered: one
  function per task, `Retry` on transient errors only, `Catch` to a `Fail`
  state, `TimeoutSeconds` per step, error names as string literals. `Map` and
  `Parallel`, compensation, and running a workflow locally with Step Functions
  Local are planned for v0.2 as `implementing-step-functions-workflows`.
- **Authentication** — the source material this plugin was derived from
  carries no example, and inventing one here would be guidance TSH has not
  agreed to.
- **The deploy pipeline itself** — `configuring-serverless-service` states what
  the pipeline must do (preflight, deploy then throttle, migrate from inside the
  network) and says to write that contract into the service's README.
  How to build it — CI system, OIDC, the deploy role — is `tsh-platform-engineering`.
- **Webpack configuration** — the bundler-and-ORM pairing covers
  webpack + `ts-loader` and the compiler settings it needs,
  but not the `serverless-webpack` setup or the webpack config itself.
- **Event sources other than HTTP and Step Functions** — SQS with its
  partial-batch response, schedules, EventBridge rules: the handler side is
  covered, the event-source and IAM configuration is not.
- **Datastores other than PostgreSQL** — the connection-budget arithmetic, the
  secret shape and the local database assume Postgres.
- **The ORM and the test runner for a new service** — not gaps in coverage but
  open team decisions; the library policy names them as such and requires
  asking rather than defaulting.
- **HTTP API operations** — the access-logging, stage-throttling and
  packaged-template guidance is written for REST API. The `apigatewayv2`
  equivalents are not covered; the guidance says so where it matters, so a
  service on HTTP API is not silently treated as covered.
- **Multi-account deployment** — this plugin owns one service's definition,
  not the account topology or pipeline that promotes it across accounts. That
  sits above what a single `serverless.yml` can express.

## Scope

**The seam with `tsh-stack-aws` runs in both directions.** Infrastructure
defined *by the service* — its functions, the execution role they run under,
API Gateway, Step Functions — belongs here, in
`configuring-serverless-service`. Infrastructure that outlives the service and
is managed with Terraform — VPC, RDS, networking — belongs in `tsh-stack-aws`.
A repo that runs Lambda behind a VPC and a managed database installs both
plugins; neither links to the other, because a path across plugins is not
guaranteed to resolve for whoever has only one installed.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change
never reaches them.

Three rules that bite hardest here:

- **Skill names carry no framework version.** `implementing-lambda-functions`,
  not `implementing-lambda-functions-v3`. Put the version in the
  `description` and in a **Version Baseline** block in `SKILL.md`.
- **Reference only files inside this plugin**, by relative path or
  `${CLAUDE_PLUGIN_ROOT}`. A skill cannot reliably read another plugin's
  files, because that plugin may not be installed — the failure is a silent
  dead link, not an error.
- **`configuring-typescript-for-serverless` has near-twins**:
  `configuring-typescript-for-nodejs` in `tsh-stack-nodejs` and
  `configuring-typescript-for-frontend` in `tsh-stack-frontend`. Version
  policy and the strictness ladder exist in all three, on purpose, because
  they cannot be linked across plugins. When you change the compiler baseline
  here, check whether the same fix is due in the other two — and let the
  target-specific parts, like the bundler-and-ORM pairing, stay different.
