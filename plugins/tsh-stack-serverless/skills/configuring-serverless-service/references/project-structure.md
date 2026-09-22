# Project structure

Use this reference when laying out a serverless service, adding a file to one,
or reviewing where something was put. This is how a TSH serverless service is
shaped — a convention to follow when building, not a tree for a generator to
emit.

```
<service-root>/
├── serverless.ts                  # the root service definition (see below)
├── tsconfig.json                  # owned by configuring-typescript-for-serverless
├── config/
│   ├── env.ts                     # loads and validates process.env once, before
│   │                              #   anything else reads it
│   ├── stage.ts                   # derives the deploying stage from argv/CLI,
│   │                              #   never from an ambient variable alone
│   ├── naming.ts                  # <service>-<stage>- prefixing, and the
│   │                              #   CloudFormation logical-id derivation rule
│   ├── iam.ts                     # execution-role definitions, split by
│   │                              #   capability (see iam-and-secrets.md)
│   ├── secrets.ts                 # secret containers and their identifiers —
│   │                              #   never a value (see iam-and-secrets.md)
│   ├── concurrency.ts             # the reservedConcurrency requirement and its
│   │                              #   per-stage exemption for local emulation
│   ├── vpc.ts                     # opt-in VPC config, only when a function
│   │                              #   must reach something private
│   └── workflows.ts               # defineWorkflow(<dir>): derives the state
│                                  #   machine, log group, ARN reference and
│                                  #   stack output from the directory name
├── functions/
│   ├── health/                    # GET /health with any HTTP layer: SELECT 1,
│   │                              #   answers only ok | unavailable
│   └── <function-name>/
│       ├── function.ts            # typed function definition: runtime config,
│       │                          #   the execution role it uses, its
│       │                          #   reservedConcurrency, its event source
│       ├── handler.ts             # middleware chain, then thin orchestration
│       ├── service.ts             # business logic; every dependency a parameter
│       ├── service.spec.ts        # unit tests for the service, with fakes
│       └── event.schema.ts        # one schema for the whole event, type inferred
├── shared/                        # follows implementing-lambda-functions
│   ├── middleware/                # request context, pre-configured middy wrappers
│   ├── errors/                    # AppError -> HttpError -> domain errors
│   └── logger/                    # structured JSON logger carrying the request id
├── workflows/                     # only when the service orchestrates
│   └── <workflow-name>/           #   one directory per workflow
│       ├── workflow.asl.yml       # declarative state machine: Retry, Catch and
│       │                          #   TimeoutSeconds per step-functions-workflows.md
│       └── <step-name>/           # one directory per Task state — same shape as a
│           ├── function.ts        #   function under functions/, never mixed in
│           ├── handler.ts         #   there; the task chain, not the HTTP one
│           ├── service.ts
│           ├── service.spec.ts
│           └── event.schema.ts
├── scripts/
│   └── check-packaged-template.*  # the packaging-time assertions from
│                                  #   packaging-and-template-checks.md, under
│                                  #   whatever name and language fit the
│                                  #   project's own tooling
├── test/
│   └── integration/               # real-database tests, one per repository,
│       └── <repo>.integration.spec.ts  # excluded from test:unit
├── docs/
│   └── decisions/                 # framework, bundler-and-ORM, gateway — see
│                                  #   tsh-core:managing-decision-records
├── CLAUDE.md                      # see tsh-core:managing-claude-context
├── AGENTS.md                      # the short entry point CLAUDE.md expands on
├── eslint.config.*                # ESLint flat config with Prettier; lint-staged
│                                  #   and commitlint configured alongside
├── .npmrc                         # engine-strict=true — see local-development.md
├── .nvmrc                         # the runtime's Node major, for nvm use
├── .env.dist                      # every variable config/ reads, with a safe
│                                  #   placeholder — never a real value
└── docker-compose.yaml            # when the service has a database: the
                                   #   local instance offline runs against, plus a
                                   #   database browser behind a `tools` profile
```

## What each top-level piece is responsible for

**`serverless.ts`.** The root service definition, in TypeScript — not
`serverless.yml`, for the reasons in
[`library-policy.md`](./library-policy.md):
provider config, the assembled list of function definitions, and the
resources this service creates directly (execution roles, secret
containers). It imports from `config/` rather than inlining logic, so the
service definition itself stays a plain assembly of pieces that are each
independently readable. See
[`service-and-stage-configuration.md`](./service-and-stage-configuration.md).

**`config/`.** Everything that would otherwise be duplicated across every
function definition, or that needs its own focused reasoning: naming,
IAM, secrets, concurrency, VPC. Each concern gets its own file so a change
to one (say, widening what counts as "requires VPC") never touches the
files that implement the others.

**`functions/<name>/function.ts`.** The deployable definition of one
function: which execution role it runs under, its event source (an HTTP
route, a queue, a schedule), and its `reservedConcurrency`. This file is
the seam between this skill and `implementing-lambda-functions` — it names
the handler module but does not contain handler logic.

**`functions/<name>/handler.ts`, `service.ts`, `event.schema.ts`,
`service.spec.ts`, and `shared/`.** The application layer of the same
function, written alongside it and obeying
`implementing-lambda-functions` rather than this skill: the middleware chain
and its registration order, the pure service with dependencies as parameters,
the single event schema, the error hierarchy and the logger. The seam decides
whose rules a file obeys, not where it sits.

**`workflows/`.** Present when the service orchestrates anything. Each workflow
directory is one state machine, defined declaratively in `workflow.asl.yml`,
and **every step it invokes is a
directory inside it** — `function.ts`, `handler.ts` on the task chain,
`service.ts`, `event.schema.ts`, `service.spec.ts` — never an entry under
`functions/` beside the HTTP endpoints. The service definition registers the
whole workflow with one `defineWorkflow("<directory>")` line from
`config/workflows.ts`, which derives the state machine, its log group, the ARN
reference a caller needs and the stack output from the directory name and the
ASL file. See [`step-functions-workflows.md`](./step-functions-workflows.md).

**`scripts/`.** Whatever build-time checks this project runs against the
packaged template. The name, language and runner are a project choice —
nothing here is a fixed artifact to copy. What each check must assert is
in [`packaging-and-template-checks.md`](./packaging-and-template-checks.md).

**`test/integration/`.** One file per real repository, run against the local
database and excluded from the unit run. This is what keeps every
`FakeOrdersRepository`-style fake honest — see the testing reference in
`implementing-lambda-functions`.

**`docs/decisions/`, `CLAUDE.md`, `AGENTS.md`.** The project's memory. Not this
plugin's concern — `tsh-core` owns both formats — but a serverless repository
wants them for the same reason any repository does, and the choices this
reference implies (the framework, the bundler-and-ORM pairing, the gateway) are
exactly what a decision record is for.
