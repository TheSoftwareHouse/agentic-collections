# TSH Stack: Serverless

TSH conventions for AWS Lambda services built with OSLS v4 — or an existing
Serverless Framework v3 project — on Node.js 22+: compiler and bundler configuration, handler
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
| `configuring-serverless-service` | `/tsh-stack-serverless:configuring-serverless-service` | Service and stage configuration, per-function definitions, least-privilege IAM, per-function reserved concurrency, opt-in VPC attachment, secrets resolved at runtime, packaged-template checks, API Gateway access logs and stage throttling, local development with `serverless-offline`, Step Functions task rules — `Retry`, `Catch`, timeouts, error names as literals — and the bootstrap procedure that generates a complete starter — service definition and handler layer both — on OSLS |

All three are model-invocable — Claude loads them when the work matches
their description, so you don't have to remember to type the command.

The bundler and the ORM are **one paired choice**, not two: the bootstrap
procedure in `configuring-serverless-service` asks for both together in a
single question, because esbuild cannot emit `emitDecoratorMetadata` and
pairing it with a decorator-based ORM without a mitigation compiles clean and
fails at runtime, silently. `configuring-typescript-for-serverless` carries
the full trade-off table the bootstrap links to rather than restates.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates
arrive with `/plugin update`.

## Not covered yet

Deliberate gaps, so they read as scope rather than oversight:

- **Databases** — planned for v0.2 as `accessing-databases-from-lambda`:
  connection lifecycle per execution environment, pool size against reserved
  concurrency, and expand/contract migrations. It needs a Drizzle track and a
  TypeORM track rather than one neutral procedure, because the migration
  tooling differs between them, not only the entity syntax — which is why it
  did not ship with v0.1.0.
- **Step Functions beyond the basics** — the bootstrap already generates a
  state machine with one function per task, `Retry` on transient errors,
  `Catch` to a `Fail` state and `TimeoutSeconds` per step. `Map` and
  `Parallel`, compensation, and running a workflow locally with Step Functions
  Local are planned for v0.2 as `implementing-step-functions-workflows`.
- **Authentication** — the source material this plugin was derived from
  carries no example, and inventing one here would be guidance TSH has not
  agreed to.
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
