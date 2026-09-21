# Step Functions workflows

Use this reference when the bootstrap's orchestration answer is Step Functions,
when adding a task to a state machine, or when a task function throws an error
the state machine is supposed to react to.

## Table of Contents

- [One function per step](#one-function-per-step)
- [Layout: one directory per workflow, one per step](#layout-one-directory-per-workflow-one-per-step)
- [Retries and error handling live in the state machine](#retries-and-error-handling-live-in-the-state-machine)
- [TimeoutSeconds below the function timeout](#timeoutseconds-below-the-function-timeout)
- [Error names are string literals](#error-names-are-string-literals)
- [The shape every generated task takes](#the-shape-every-generated-task-takes)

## One function per step

Each `Task` state invokes one function that does one thing. A step that
branches internally on "which phase am I in" is two steps hiding in one, and
its retries, timeout and error matching become impossible to reason about
because they apply to both halves at once.

## Layout: one directory per workflow, one per step

A workflow is a directory, and every step is a directory inside it — not an
entry under `functions/` beside the HTTP endpoints:

```
workflows/<workflow-name>/
├── workflow.asl.yml          # the state machine, declarative
└── <step-name>/              # one per Task state
    ├── function.ts           # deploy definition: task role, timeout, reservedConcurrency
    ├── handler.ts            # the task chain — no HTTP middleware
    ├── service.ts
    ├── service.spec.ts
    └── event.schema.ts
```

Two things follow from the split. The state machine stays **declarative** —
YAML that reads as a state diagram, not TypeScript that assembles one — and a
step's Lambda is referenced from it by a placeholder the loader resolves to the
step's *derived* logical id (`{{fn:<step>}}`, or a `!GetAtt <id>.Arn` tag the
loader rewrites), never by an id typed by hand. And the service definition
registers a workflow with **one line** — `defineWorkflow("<directory>")` — a
helper that derives the state machine key, its logical id, the ARN reference a
starter function needs, the log group, the stack output, `tracingConfig` and
the `ERROR`-level logging with `includeExecutionData: false`, all from the
directory name and the ASL file. Adding a workflow is a directory plus one
line; adding a step is a directory plus one state in the YAML. A single
`workflow.ts` that hand-assembles definition, log group and state machine
config is the shape to refactor away from: it hides the diagram inside code and
duplicates what the helper derives.

Steps use the task chain from `implementing-lambda-functions` — request
context, logger, schema validation, no HTTP middleware — and a dedicated task
execution role, so the permissions a step needs never leak into an endpoint's
role.

## Retries and error handling live in the state machine

`Retry` and `Catch` belong on the `Task` state, never inside the task's code.
A task that retries itself *and* is retried by the orchestrator multiplies
attempts — three internal tries under three orchestrator tries is nine calls
to a downstream that was already failing. Task code makes exactly one attempt,
throws on failure, and lets the state machine decide. That also puts every
retry policy in one file a reviewer can read end to end.

Because the orchestrator may re-run a task after a timeout it could not
confirm, every task is **idempotent**: re-running it with the same input must
not reserve the stock twice or charge the card twice.

## `TimeoutSeconds` below the function timeout

Give every `Task` state a `TimeoutSeconds` lower than the invoked function's
own timeout. The orchestrator then owns the timeout decision: the failure
surfaces as `States.Timeout`, an error `Retry` and `Catch` can name — instead
of as the Lambda runtime's own kill, which reaches the state machine as an
opaque `Lambda.Unknown` with no retry policy of its own.

## Error names are string literals

The state machine matches a thrown error by its `name`, transported as a
string — never by class identity. A class name is not a stable string: bundlers
rename classes under minification, and a `Catch` on `"InventoryError"` silently
stops matching the moment `minify` is switched on, with no build error
anywhere. Set `name` explicitly, as a literal, in the error's constructor, and
match that same literal in `ErrorEquals`. The handler-side rule and code shape
are in
[`validation-and-errors.md`](${CLAUDE_PLUGIN_ROOT}/skills/implementing-lambda-functions/references/validation-and-errors.md).

## The shape every generated task takes

```yaml
ReserveInventory:
  Type: Task
  Resource: "{{fn:reserveInventory}}"
  TimeoutSeconds: 25              # the function's own timeout is 30
  Retry:
    - ErrorEquals:                # transient, worth another attempt
        - Lambda.ServiceException
        - Lambda.AWSLambdaException
        - Lambda.SdkClientException
        - Lambda.TooManyRequestsException
        - States.Timeout
      IntervalSeconds: 2
      MaxAttempts: 3
      BackoffRate: 2
  Catch:
    - ErrorEquals: ["InventoryError"]   # the literal the handler sets as `name`
      ResultPath: "$.error"
      Next: OrderFailed
    - ErrorEquals: ["States.ALL"]
      ResultPath: "$.error"
      Next: OrderFailed
  Next: CapturePayment

OrderFailed:
  Type: Fail
  Error: OrderFulfillmentFailed
  Cause: A step failed after retries; see $.error in the execution history
```

Domain errors — a business rule that failed — are **not** retried: retrying
"out of stock" three times changes nothing. They go straight to `Catch`. Only
the transient Lambda-side errors and the orchestrator's own timeout are worth
another attempt.

`ResultPath: "$.error"` keeps the original input alongside the error instead
of replacing it, so the `Fail` state — and anyone reading the execution
history — can still see which order failed.

| Severity | Rule |
| --- | --- |
| MUST | One function per `Task` state. |
| MUST | One directory per workflow, one directory per step inside it; a step never lives under `functions/`. |
| MUST | Keep the state machine declarative in `workflow.asl.yml`, referencing steps by placeholders the loader resolves to derived logical ids. |
| MUST | Register a workflow with a single `defineWorkflow(<directory>)` call that derives everything else; never hand-assemble state machine, log group and output. |
| MUST | Put `Retry` and `Catch` on the `Task` state; task code makes exactly one attempt and throws. |
| MUST | Set `TimeoutSeconds` on every `Task`, below the invoked function's own timeout. |
| MUST | Match errors by a `name` the handler sets as a string literal; never rely on a class name surviving the bundler. |
| NEVER | Retry a domain error — a failed business rule is a `Catch`, not a `Retry`. |
| MUST | Keep every task idempotent; a retried or re-run task with the same input produces the same outcome, once. |

## Sources

AWS Step Functions Developer Guide, verified 2026-09-18:

- [Handle Lambda service exceptions](https://docs.aws.amazon.com/step-functions/latest/dg/bp-lambda-serviceexception.html) — the four `Lambda.*` errors worth a `Retry`
- [Error handling in Step Functions workflows](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html) — `Retry`, `Catch`, `ResultPath`, `States.Timeout`, `States.ALL`

The rule that error names are string literals is TSH's own, drawn from the bundling
failure it prevents. The AWS pages document how a name is matched, not that a bundler may
rename it.
