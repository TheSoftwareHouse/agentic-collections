---
name: implementing-lambda-functions
description: "Implements and reviews AWS Lambda handlers in TypeScript: the thin-handler and pure-service split, middleware chain ordering, schema validation at the event boundary, the error hierarchy that maps to HTTP responses, structured logging with the request id, and what belongs in the init phase. Use when writing a Lambda handler, adding an endpoint, or reviewing a serverless function change."
when_to_use: "Trigger on: writing or restructuring a Lambda handler, adding an API Gateway endpoint, ordering middy middleware, validating an event with a schema, mapping a thrown error to an HTTP status, cold-start and init-phase work, logging from a Lambda, or reviewing a serverless function for testability and security."
---

# Implementing Lambda Functions

Implementation and review guidance for the handler layer of an AWS Lambda service:
the split between the handler and the service it calls, the middy middleware
chain, event validation, the error hierarchy, structured logging, and what a
handler may safely assume has already run by the time it executes. It says
nothing about how the function is deployed — see
[`configuring-serverless-service`](${CLAUDE_PLUGIN_ROOT}/skills/configuring-serverless-service/SKILL.md)
for that.

## Version Baseline

This skill targets AWS Lambda functions deployed with **OSLS v4 or Serverless
Framework v3**, on **Node.js 24** (`nodejs24.x`; `nodejs22.x` stays in range until its
2027-04-30 deprecation, never for a new service), with **middy** as the middleware framework
the chain-ordering guidance assumes. A new service starts on OSLS — Serverless
Framework v3 is end of life; `configuring-serverless-service` carries the
reasoning.

Read the target repository's `package.json` before applying anything here. If it
is on a materially different runtime or middleware framework, **stop and say
so** — the middleware-order and chain guidance below does not transfer as-is.

## Applicability and Precedence

Discover the target repository's existing handler shape, validation library, and
error types first. Those local conventions outrank this skill's defaults; apply
this skill where they are silent, and record any deliberate deviation rather
than silently mixing conventions.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Keep the handler thin: resolve dependencies, call the service, shape the response. The service takes every dependency — repositories, clients, config — as a parameter; it never imports infrastructure at module scope. |
| MUST | Register the error-rendering middleware **after** the CORS and security-header middleware — never first. middy runs `onError` in reverse registration order, and in middy 7 the CORS and security-header hooks skip when no response exists yet, so the renderer must run *before* them to build the response they decorate. Registered first, it runs last and every error response leaves without CORS headers. Prove the order with a handler-level test asserting `Access-Control-Allow-Origin` on an error response. |
| MUST | Validate the whole event against one schema at the boundary, and infer the payload type from that schema. Never hand-write the type a second time. |
| NEVER | Enable CORS credentials together with a wildcard origin. The CORS middleware reflects the request's `Origin` header, so with `credentials: true` and no allow-list any site can read an authenticated response. |
| NEVER | Log request bodies, authorization headers, or cookies — neither in application code nor by weakening the input/output logging middleware's redaction. |
| MUST | Do expensive, reusable setup — config parsing, client construction — at module scope during the init phase, and never repeat it inside the handler. A warm container must reuse what init already built, not re-run it. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Handler and service split](./references/handler-and-service-split.md) | Writing a handler, or splitting business logic out of one | Thin-handler responsibilities, the pure-service contract, init-phase work, parameter-based dependencies |
| [Middleware chain](./references/middleware-chain.md) | Ordering middy middleware, or adapting the chain for a non-HTTP trigger | Registration order and its consequence, which middleware to drop for SQS/EventBridge triggers |
| [Validation and errors](./references/validation-and-errors.md) | Validating an event, or mapping a thrown error to a response | Event schema and inferred types, the `AppError` → `HttpError` hierarchy, 4xx exposed vs 5xx masked |
| [Logging and observability](./references/logging-and-observability.md) | Adding or reviewing log statements | Structured JSON logging, the request id, what must never be logged |
| [Testing Lambda code](./references/testing-lambda-code.md) | Adding or reviewing tests for a handler or service | Testing services with fakes, when the middleware chain itself is the behavior under test |
| [Review checklist](./references/review-checklist.md) | Reviewing an existing serverless function change | Severity-tagged checks across handlers, services, middleware, validation, and logging |

## Implementation Procedure

Copy and track this checklist while implementing a change:

```text
Implementation progress:
- [ ] Step 1: Discover local conventions (validation library, error types, test runner)
- [ ] Step 2: Load the references relevant to the change
- [ ] Step 3: Write the schema, then the service, then the handler
- [ ] Step 4: Order the middleware chain
- [ ] Step 5: Add logging and tests
- [ ] Step 6: Review the result
```

**Step 1 — Discover local conventions.** Read the repository's existing
functions before introducing anything different. The validation library (zod)
and the shape of a log line are settled in the library policy that
`configuring-serverless-service` carries; the **test runner is deliberately
not** — follow what the repository uses, and ask rather than introduce one
where there is none. A repository already standardised on something else keeps
it: local convention outranks a default, and swapping a library is its own
task.

**Step 2 — Load relevant references.** Read
[`handler-and-service-split.md`](./references/handler-and-service-split.md)
before writing any handler, and
[`middleware-chain.md`](./references/middleware-chain.md) before touching the
chain.

**Step 3 — Write inside-out.** Define the event schema first, then the pure
service against that inferred type, then the handler that wires them together.
A service written before its schema tends to invent its own shape instead.

**Step 4 — Order the middleware.** Apply the registration-order rule above, and
drop the HTTP-specific entries for a non-HTTP trigger — see
[`middleware-chain.md`](./references/middleware-chain.md).

**Step 5 — Add safeguards.** Add structured logging per
[`logging-and-observability.md`](./references/logging-and-observability.md) and
tests per [`testing-lambda-code.md`](./references/testing-lambda-code.md).

**Step 6 — Review.** Use the
[review checklist](./references/review-checklist.md) and report findings by
severity.

## Review Procedure

For review, load [the review checklist](./references/review-checklist.md),
apply only the checks relevant to the changed artifacts, and report findings
grouped by severity with the reference that owns each violated rule.

## Related Skills

Ship in this same plugin, so both are always available alongside this skill:

- [`configuring-typescript-for-serverless`](${CLAUDE_PLUGIN_ROOT}/skills/configuring-typescript-for-serverless/SKILL.md)
  — the compiler and bundler baseline this guidance assumes, including why the
  bundler alone cannot catch a type error.
- [`configuring-serverless-service`](${CLAUDE_PLUGIN_ROOT}/skills/configuring-serverless-service/SKILL.md)
  — how the function this skill implements gets deployed: IAM, concurrency,
  secrets, and the packaged template.
