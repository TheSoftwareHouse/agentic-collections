# Bootstrap procedure

Use this reference when bootstrapping a new serverless service from an empty or
near-empty repository. This **is** the procedure — `SKILL.md` points here and does
not restate it.

Read [`starter-service-layout.md`](./starter-service-layout.md)
before generating anything — it pins the file tree this procedure produces.

**Step 1 — Ask once.** Before writing a single file, ask with **one**
`AskUserQuestion` call carrying the four questions below, in this order —
each is a choice an empty repository cannot answer on its own, and no house
default exists to fall back to. *As a subagent, report the blocker to the
caller instead of asking; in the main conversation, ask the user.*

1. **Build and persistence stack** — paired, not two questions. Splitting
   this into a bundler question and an ORM question lets someone assemble
   esbuild with TypeORM unwarned, and that pair builds cleanly and fails at
   runtime with a missing or wrongly-guessed column type. Offer exactly these
   three options, trade-off in the description:
   - **esbuild + Drizzle ORM** — the natural fit for a greenfield service with
     no existing ORM investment; fast rebuilds, no decorators, nothing to
     silently omit.
   - **webpack + ts-loader + TypeORM** — for a team already invested in
     TypeORM, or porting an existing service; builds roughly an order of
     magnitude slower.
   - **esbuild + TypeORM through a tsc/swc pass** — only when TypeORM is
     non-negotiable and build speed still matters; reintroduces a per-file
     compiler pass, the compromise option rather than a free win.
2. **HTTP layer** — offer three options, trade-off in the description:
   - **HTTP API** — the fit for a plain JSON API: markedly cheaper per
     request, lower latency, a built-in JWT authorizer, fewer knobs.
   - **REST API** — when the service needs what only it offers: request and
     response validation and transformation at the gateway, usage plans and
     API keys, WAF and resource policies, response caching.
   - **No endpoints** — the service is triggered only by queues, schedules,
     or a state machine.
3. **Persistence target** — PostgreSQL, none, or other. The ORM is already
   settled by question 1; this only decides whether a database exists at all.
4. **Orchestration** — Step Functions, or none. When chosen, generate the
   state machine per
   [`step-functions-workflows.md`](./step-functions-workflows.md):
   one directory per step inside `workflows/<name>/`, a declarative
   `workflow.asl.yml` registered by one `defineWorkflow()` line, one function
   per `Task`, `TimeoutSeconds` below each function's timeout,
   `Retry` on the transient Lambda errors only, and `Catch` routing domain
   errors — matched by the string-literal `name` the handler sets — to a
   `Fail` state. `Map`, `Parallel` and compensation are a later skill; say so
   rather than inventing them.

For the reasoning behind the question-1 pairing — why esbuild cannot
implement `emitDecoratorMetadata`, and what each option costs — read
`${CLAUDE_PLUGIN_ROOT}/skills/configuring-typescript-for-serverless/references/bundler-tradeoffs.md`.
That file is the canonical explanation; do not restate its table here.

**Step 2 — Generate the layout.** Produce the file tree from
`starter-service-layout.md`, wired to the four answers: the chosen bundler
config, the HTTP layer's function definitions (or none), a database secret and
its execution-role statement only if a persistence target was chosen, and a
state machine definition — per
[`step-functions-workflows.md`](./step-functions-workflows.md) —
only if orchestration was chosen. Install the
framework as OSLS — `"serverless": "npm:osls@^4"` in `devDependencies` — never
Serverless Framework v3 (see Version Baseline). Include the local-development
pieces from [`local-development.md`](./local-development.md):
`serverless-offline` installed **and** registered in `plugins`, `.env.dist`,
and a `docker-compose.yaml` when a database was chosen.

**Every dependency version comes from the registry, not from memory.** Before
writing `package.json`, resolve the current version of each package with
`npm view <package> version` and write that — within the constraints the
guidance already sets: `@types/node` at the runtime's major, TypeScript pinned
exactly, the framework as `npm:osls@^4`. A remembered version is the version
from the model's training data, months to a year stale. The first real
bootstrap of this plugin wrote `drizzle-orm ^0.38` against a registry at
`0.45`, `zod ^3.24` against `4.6`, and TypeScript `5.7.2` against `7.0` — a
whole major behind on two of them, and nothing anywhere warned about it.

**Step 3 — Generate the handler layer.** This bootstrap owns the whole
starter, not only its service definition. Read
`${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/SKILL.md` and its
references now, and for **every** function generate `handler.ts` with the
middleware chain, `service.ts` taking its dependencies as parameters,
`event.schema.ts`, and `service.spec.ts` — plus a `shared/` directory holding
the middleware, the error hierarchy and the logger those handlers use — HTTP
endpoints under `functions/<name>/`, workflow steps under
`workflows/<workflow>/<step>/` with the task chain instead of the HTTP one. A
handler that returns 501 or throws "not implemented" is a placeholder, not a
generated function, and a bootstrap that leaves one behind is not done.

**Step 4 — Wire the rules above.** Every generated function declares
`reservedConcurrency`; every generated IAM statement is scoped per
[`iam-and-secrets.md`](./iam-and-secrets.md); a chosen database
target produces a secret container per that same reference, never a literal
value; VPC attachment is left off unless the user asked for it.

**Step 5 — Point at packaging checks.** Tell the user to add the checks in
[`packaging-and-template-checks.md`](./packaging-and-template-checks.md)
to their build, and to run a package step before the first deploy.

| Severity | Rule |
| --- | --- |
| MUST | Ask the four questions in one `AskUserQuestion` call, bundler and ORM as a single paired option. |
| MUST | Generate the handler layer for every function; a 501 placeholder is not a generated function. |
| MUST | Install the framework as OSLS; never start a new service on Serverless Framework v3. |
| MUST | Resolve every dependency version from the registry at generation time; never write a version from memory. |
| MUST | Register `serverless-offline` in `plugins` and ship `.env.dist`; a starter that cannot run locally is not complete. |
