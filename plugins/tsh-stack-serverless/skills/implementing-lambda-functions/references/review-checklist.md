# Serverless Function Review Checklist

Use this reference to review a Lambda handler change against this skill's
handler/service, middleware, validation, error, and logging rules.

## Review Workflow

- [ ] Identify which files changed (handler, service, schema, middleware) and
      select only the applicable groups below.
- [ ] Apply every `[BLOCKER]` and `[HIGH]` check before reviewing lower
      severities.
- [ ] Confirm the middleware chain's registration order by reading it, not by
      assuming it is unchanged.
- [ ] Record each finding with its location, severity, violated rule, and
      owning reference.

## Table of Contents

- [Handler and Service Checks](#handler-and-service-checks)
- [Middleware Chain Checks](#middleware-chain-checks)
- [Validation and Error Checks](#validation-and-error-checks)
- [Logging Checks](#logging-checks)
- [Test Checks](#test-checks)
- [Output Rules](#output-rules)

## Handler and Service Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|The handler MUST only resolve dependencies, call the service, and shape the response; it MUST NOT contain business logic, a loop over domain data, or branching beyond dependency resolution.|[`handler-and-service-split.md`](./handler-and-service-split.md)|
|[HIGH]|The service MUST take every dependency — repositories, clients, config — as a parameter; it MUST NOT import an infrastructure client or a reusable resource accessor at module scope.|[`handler-and-service-split.md`](./handler-and-service-split.md)|
|[HIGH]|Expensive, reusable setup MUST happen at module scope during the init phase; the handler body MUST NOT re-run or re-initialise it on every invocation.|[`handler-and-service-split.md`](./handler-and-service-split.md)|
|[HIGH]|A memoised async accessor — a client, a connection, a resolved secret — MUST clear its memo when the promise rejects; otherwise one transient failure during init poisons every warm invocation of that execution environment.|[`handler-and-service-split.md`](./handler-and-service-split.md)|
|[MEDIUM]|The service MUST return only the data its caller needs, not an entire persistence entity or an unbounded result.|[`handler-and-service-split.md`](./handler-and-service-split.md)|

## Middleware Chain Checks

|Severity|Check|Owning reference|
|---|---|---|
|[BLOCKER]|The error-rendering middleware MUST be registered after the CORS and security-header middleware — never first — so its `onError` runs before theirs and builds the response they decorate; registered first, every error response leaves without CORS headers.|[`middleware-chain.md`](./middleware-chain.md)|
|[HIGH]|A middleware that reads a normalized value (headers, query string, event shape) MUST be registered after the normalizer that produces it.|[`middleware-chain.md`](./middleware-chain.md)|
|[HIGH]|For a non-HTTP trigger, HTTP-specific middleware (CORS, security headers, header/event normalizers, body parser) MUST be dropped rather than left in place unused.|[`middleware-chain.md`](./middleware-chain.md)|
|[BLOCKER]|CORS credentials MUST NEVER be enabled together with a wildcard origin.|[`middleware-chain.md`](./middleware-chain.md)|

## Validation and Error Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|The event MUST be validated against exactly one schema covering the whole event; the payload type MUST be inferred from that schema, never hand-written separately.|[`validation-and-errors.md`](./validation-and-errors.md)|
|[HIGH]|A service MUST throw a typed error (an `AppError`/`HttpError` subclass or the repository's equivalent) rather than return an error shape or a result the caller must remember to check.|[`validation-and-errors.md`](./validation-and-errors.md)|
|[HIGH]|A 5xx response MUST mask the underlying message, stack, and cause from the client; only 4xx responses MUST render their message verbatim.|[`validation-and-errors.md`](./validation-and-errors.md)|
|[HIGH]|Every error class MUST set `name` as a string literal in its constructor; deriving it from the class (`constructor.name`) is a finding, because bundler minification renames classes and silently breaks every match on the old name.|[`validation-and-errors.md`](./validation-and-errors.md)|
|[MEDIUM]|A business invariant a schema cannot express (existence of a referenced resource, an allowed state transition) MUST be enforced in the service, not assumed to be covered by event-boundary validation.|[`validation-and-errors.md`](./validation-and-errors.md)|

## Logging Checks

|Severity|Check|Owning reference|
|---|---|---|
|[BLOCKER]|Request bodies, authorization headers, and cookies MUST NEVER be logged, in application code or in a logging middleware's configuration.|[`logging-and-observability.md`](./logging-and-observability.md)|
|[HIGH]|Every log line MUST carry the request id set once near the front of the middleware chain.|[`logging-and-observability.md`](./logging-and-observability.md)|
|[MEDIUM]|An `Error` MUST be passed to the logger as its own argument, not interpolated into a message string, so the stack is preserved.|[`logging-and-observability.md`](./logging-and-observability.md)|
|[MEDIUM]|Application code MUST route through the repository's structured logger; direct `console.*` calls outside test and tooling scripts are a finding.|[`logging-and-observability.md`](./logging-and-observability.md)|

## Test Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|A service test MUST supply fakes as parameters rather than stubbing a module-level import.|[`testing-lambda-code.md`](./testing-lambda-code.md)|
|[HIGH]|Every real repository MUST have an integration test against the local database under `test/integration/`, excluded from the unit run; a repository covered only through its fake is untested.|[`testing-lambda-code.md`](./testing-lambda-code.md)|
|[HIGH]|A change to the middleware chain MUST be covered by a handler-level test that asserts the full response — status, headers, and body — including `Access-Control-Allow-Origin` on an **error** response, the only assertion that proves the registration order.|[`testing-lambda-code.md`](./testing-lambda-code.md)|
|[MEDIUM]|A service test MUST NOT assert against a real database, queue, or third-party API.|[`testing-lambda-code.md`](./testing-lambda-code.md)|

## Output Rules

- Report every finding with its severity, file, and the rule it violates.
- Trace each finding to the reference above that owns the violated rule.
- State plainly when a change has no findings; do not pad a clean review with
  speculative concerns.
