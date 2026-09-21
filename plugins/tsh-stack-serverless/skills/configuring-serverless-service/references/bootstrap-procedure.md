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

**Every option that switches off part of this plugin's guidance says so in its
own description.** An answer here does not only shape the generated files — it
decides which of this plugin's rules still apply afterwards, and an option
whose consequences are silent produces a service that builds, looks right and
sits outside everything the plugin can check. Three defects of exactly this
shape have already shipped and been fixed: a bundler chosen without its ORM, a
gateway chosen without its operations, an orchestration answer chosen without
its retry rules. When an option below carries a gap, the description names it
in one sentence, in plain terms — *"this plugin does not cover X yet"* — so the
user chooses it knowingly rather than discovering it at the first incident.

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
     magnitude slower. **Say plainly that this plugin does not cover the
     webpack configuration itself**: it carries the compiler settings the
     pairing needs (the decorator flags) and the one operational trap
     (`package` and `offline` share the bundler's output directory — see
     [`local-development.md`](./local-development.md)), but the
     `serverless-webpack` setup and the webpack config are the team's to
     write.
   - **esbuild + TypeORM through a tsc/swc pass** — only when TypeORM is
     non-negotiable and build speed still matters; reintroduces a per-file
     compiler pass, the compromise option rather than a free win, and the
     plugin or compiler pass that produces the metadata is not configured for
     you either.
2. **HTTP layer** — offer three options, trade-off in the description.
   Neither gateway is a house default; state what each costs, including the
   coverage gap in the second:
   - **REST API** — what this plugin's operational guidance covers end to
     end: access logging, stage throttling and the packaged-template checks
     are all written against it, and it is what the source boilerplate runs.
     It also has what only it offers — request and response validation at the
     gateway, usage plans and API keys, WAF and resource policies, response
     caching. Costs more per request than HTTP API.
   - **HTTP API** — markedly cheaper per request, lower latency, a built-in
     JWT authorizer, fewer knobs. What it gives up is operational, and worth
     naming: **no X-Ray tracing at all**, no execution logs, no WAF, no API
     keys or per-client throttling, no resource policies or private endpoints,
     no caching, no request validation or body transformation at the gateway.
     **Say plainly that this plugin does not cover its operations yet**:
     access logging and throttling go through `apigatewayv2`, not the
     `provider.logs.restApi` block and the `apigateway update-stage` call this
     guidance describes. Choosing it is fine; the
     user must know they are outside what the plugin can check.
   - **No endpoints** — the service is triggered only by queues, schedules,
     or a state machine. The handler side is covered: the task chain and what
     to drop from the middleware chain for a non-HTTP trigger. **The event
     source itself is not** — an SQS queue with its partial-batch response, a
     schedule, an EventBridge rule and the IAM those need are outside what
     this plugin configures today; say so.
3. **Persistence target** — PostgreSQL, none, or other. The ORM is already
   settled by question 1; this only decides whether a database exists at all.
   PostgreSQL is what the connection-budget arithmetic, the secret shape and
   the local `docker-compose.yaml` in this plugin assume. **For anything else
   — another relational engine, DynamoDB — say that this plugin's persistence
   guidance does not transfer**: a connection-per-invocation budget is
   meaningless for a request-per-call datastore, and the secret container
   shape is Postgres-flavoured. Generate what the user asks for, and tell them
   which rules stop applying.
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
and a `docker-compose.yaml` when a database was chosen. Any HTTP layer also
gets `functions/health/`: a `GET /health` that runs a short `SELECT 1` against
the chosen database (a plain 200 when there is none) and answers only `ok` or
`unavailable` — never the failure detail, because a monitor reads it, not a
developer. Install the toolchain baseline as well — ESLint (flat config) with
Prettier, `lint-staged` on a pre-commit hook, `commitlint` with the
conventional config — and wire the `verify` gate in the shape given in
[`packaging-and-template-checks.md`](./packaging-and-template-checks.md).

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

**Every real repository gets an integration test.** The services are tested
with fakes; the one module that actually speaks SQL — the repository behind
those fakes — is tested against the local database from `docker-compose.yaml`,
in `test/integration/<repository>.integration.spec.ts`, excluded from
`test:unit` and run by `test:integration` and by `verify`. Without it the fake
and the real thing drift apart with nothing to catch it. The shape is in
`${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/references/testing-lambda-code.md`.

**Step 4 — Wire the rules above.** Every generated function declares
`reservedConcurrency`; every generated IAM statement is scoped per
[`iam-and-secrets.md`](./iam-and-secrets.md); a chosen database
target produces a secret container per that same reference, never a literal
value; VPC attachment is left off unless the user asked for it.

**Step 5 — Wire the verify gate.** Generate the checks in
[`packaging-and-template-checks.md`](./packaging-and-template-checks.md) as
scripts and compose `verify` exactly as that reference's *The verify gate*
section lays out — source checks, then the packaged artifact, including
executing it. Tell the user it is the gate, locally and in CI, and that a
subset of it is not "verified".

**Step 6 — Leave the project its memory.** The bootstrap has just made the
decisions a new team member will ask about first; write them where the next
session — human or model — will find them. Invoke
`/tsh-core:managing-claude-context` to seed `CLAUDE.md` (and the short
`AGENTS.md` it expands on) with what this starter obeys: the layout, the rules
from this plugin's rule tables, the `verify` gate. Invoke
`/tsh-core:managing-decision-records` to record the bootstrap answers as the
first decision records — `0001` the bundler-and-ORM pairing with the reasoning
from `bundler-tradeoffs.md`, `0002` the HTTP layer, `0003` OSLS over the
end-of-life Serverless Framework v3, and `0004` orchestration when chosen.
Both skills ship in `tsh-core`, which may be assumed installed; if either is
unavailable, write the files by hand in the same shape rather than skipping
them. A starter without `CLAUDE.md` is one the next session has to rediscover
from scratch.

| Severity | Rule |
| --- | --- |
| MUST | Ask the four questions in one `AskUserQuestion` call, bundler and ORM as a single paired option. |
| MUST | Name, in the option's own description, every part of this plugin's guidance that the option switches off. An option with a silent gap is a defect, not a shorter question. |
| MUST | Generate the handler layer for every function; a 501 placeholder is not a generated function. |
| MUST | Install the framework as OSLS; never start a new service on Serverless Framework v3. |
| MUST | Resolve every dependency version from the registry at generation time; never write a version from memory. |
| MUST | Register `serverless-offline` in `plugins` and ship `.env.dist`; a starter that cannot run locally is not complete. |
| MUST | Generate `functions/health/` with any HTTP layer; it answers only `ok` or `unavailable`. |
| MUST | Generate an integration test against the local database for every real repository; a repository covered only through its fake is untested. |
| MUST | Compose `verify` per `packaging-and-template-checks.md`: lint and audit on the source, then load and execute the packaged artifact. |
| MUST | Close by seeding `CLAUDE.md` and the first decision records through `tsh-core`; a starter with no project memory is not done. |
