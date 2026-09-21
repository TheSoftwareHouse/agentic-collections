# Logging and Observability

Use this reference when adding or reviewing log statements in a Lambda
function.

## Table of Contents

- [Structured logging](#structured-logging)
- [The request id](#the-request-id)
- [What must never be logged](#what-must-never-be-logged)
- [console is not a logger](#console-is-not-a-logger)

## Structured logging

Log structured JSON, not formatted strings. A structured line is queryable in
whatever log-aggregation tool reads CloudWatch, a formatted string is not.
Every line should carry, at minimum: a timestamp, the log level, the service
or application name, the deployment stage, the request id, and the message.

```ts
logger.info("Handling request", { widgetId });
logger.error("Failed to persist widget", error, { widgetId });
```

Pass an `Error` instance as its own argument rather than interpolating
`error.message` into the log message string — a logger configured to capture
stack traces only does so when it receives the `Error` object itself. An
interpolated message string discards the stack before the logger ever sees it.

Distinguish the deployment **stage** (dev, staging, production) from
`NODE_ENV`. A build tool commonly sets `NODE_ENV=production` for every
deployed stage regardless of which one it actually is, so logging `NODE_ENV`
as the environment mislabels every non-production deployment as production in
the logs.

## The request id

Every log line during one invocation must carry the same request id, so a
support engineer can pull every line for one request from an aggregation
query. Set it once, as early as possible in the middleware chain — a
`requestContext`-style middleware near the front of the chain (see
[`middleware-chain.md`](./middleware-chain.md)) is the right place — and read
it from wherever the logger emits a line, rather than threading it explicitly
through every function call.

## What must never be logged

Never log, at any level, in application code or in a logging middleware's
configuration:

- **Request bodies** — they routinely carry personal data or credential
  material the caller supplied.
- **Authorization headers** — a bearer token or API key logged once is
  compromised for as long as the log line exists.
- **Cookies** — session identifiers are as sensitive as the token they stand
  in for.

An input/output logging middleware commonly ships a default redaction list.
Verify what it actually redacts for the version in use rather than assuming —
redaction defaults have changed between middleware versions, and a repository
that pins an older version may not get the coverage a newer default provides.
Treat the three items above as a floor to enforce explicitly, not as something
the middleware is trusted to have covered.

## console is not a logger

Route every log statement through the repository's structured logger. Direct
`console.*` calls bypass the redaction, the request id enrichment, and the
structured-JSON formatting the logger provides — a repository that lints
against `console` outside test and tooling scripts is enforcing exactly this.
