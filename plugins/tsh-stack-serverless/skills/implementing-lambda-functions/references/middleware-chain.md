# Middleware Chain

Use this reference when ordering middy middleware in a handler, or deciding
what to drop for a non-HTTP trigger.

## Table of Contents

- [How middy runs the chain](#how-middy-runs-the-chain)
- [The registration order, and why](#the-registration-order-and-why)
- [CORS credentials, never with a wildcard origin](#cors-credentials-never-with-a-wildcard-origin)
- [Non-HTTP triggers](#non-http-triggers)
- [Adding a new middleware](#adding-a-new-middleware)

## How middy runs the chain

middy composes middleware in three phases per invocation: `before`, `after`,
and `onError`. The key asymmetry that drives every ordering decision in this
skill:

- `before` handlers run in **registration order** — first registered, first to
  run.
- `after` and `onError` handlers run in **reverse registration order** — first
  registered, **last** to run.

A middleware registered early therefore wraps everything registered after it:
its `before` runs first, and its `after`/`onError` runs last, after every later
middleware has had its own chance to run first.

## The registration order, and why

```ts
import middy from "@middy/core";
import httpErrorHandler from "@middy/http-error-handler";
import httpHeaderNormalizer from "@middy/http-header-normalizer";
import httpEventNormalizer from "@middy/http-event-normalizer";
import httpCors from "@middy/http-cors";
import httpSecurityHeaders from "@middy/http-security-headers";
import inputOutputLogger from "@middy/input-output-logger";

export const handle = middy()
  .use(requestContext()) // your own middleware: attaches the request id, not a middy package
  .use(inputOutputLogger()) // early => its after/onError run late and see the final response
  .use(httpHeaderNormalizer())
  .use(httpEventNormalizer())
  // Add a body parser here only for endpoints that accept a request body.
  .use(httpCors()) // decorates a response; its onError skips when none exists yet
  .use(httpSecurityHeaders())
  .use(httpErrorHandler()) // AFTER cors/security => its onError runs BEFORE theirs and builds the response they decorate
  .use(queryParser()) // your own middleware, only if the schema validates queryStringParameters
  .use(schemaValidator(mySchema)) // your own wrapper around @middy/validator
  .handler(lambdaHandler);
```

`httpErrorHandler`, `httpCors`, `httpSecurityHeaders`, and `inputOutputLogger` are the
published middy exports; projects commonly wrap each in a pre-configured local variant
(for example `httpErrorHandlerConfigured`) that pins the project's own options, so
expect to see that suffix in real code. `requestContext`, `queryParser`, and
`schemaValidator` above are illustrative names for middleware a project writes itself —
middy ships no package under those names.

**The error-rendering middleware is registered after CORS and security
headers — so that its `onError` runs *before* theirs.** This is the opposite of
the intuitive "register it first so it wraps everything", and the reason is in
middy's own source (`@middy/http-cors` and `@middy/http-security-headers`,
verified on 7.9.2): both `onError` hooks begin with
`if (request.response === undefined) return`. They decorate an existing
response; they never create one. `onError` runs in reverse registration order,
so an error renderer registered *first* runs *last* — after CORS and security
headers have already looked, found no response, and skipped. The error goes out
with a status and a body and **no CORS headers**, and the browser reports a
CORS failure that hides the real 400.

Registered *after* them, the renderer's `onError` runs first, sets
`request.response` without returning it — which is exactly what
`@middy/http-error-handler` does, so middy's loop continues — and the CORS and
security-header hooks then find a response and decorate it. This is the one
piece of middy ordering that is easy to get backwards, and the inversion is
invisible on every 200.

The rest of the order follows from what each middleware needs already done:

1. **Request context** — establishes the request id before anything logs.
2. **Input/output logger** — registered early so its `after`/`onError` run late
   and observe the final, decorated response; it needs the request id.
3. **Header/event normalizers** — a consistent event shape before anything
   downstream inspects headers, query string, or path parameters.
4. **Body parser** (endpoints that accept a body only) — needs the normalized
   event.
5. **CORS** and **security headers** — decorate the response; their `onError`
   only acts once a response exists.
6. **Error renderer** — after CORS and security headers, so its `onError` runs
   before theirs and builds the response they decorate.
7. **Query parser** (only if the schema validates `queryStringParameters`) and
   the **schema validator** — validate last, on the final event shape.

A handler-level test that throws from the handler and asserts
`Access-Control-Allow-Origin` on the **error** response is the only thing that
proves this order holds. A test on the 200 path proves nothing about it — which
is how an inverted chain ships and stays shipped.

## CORS credentials, never with a wildcard origin

**[BLOCKER]** CORS credentials must never be enabled together with a wildcard
origin. `httpCors` configured with `credentials: true` and no explicit allow-list
reflects the incoming request's `Origin` header back verbatim as
`Access-Control-Allow-Origin`, rather than serving a literal `*` — that is what lets
`credentials: true` pass browser validation at all. The combination means the
middleware effectively allows every origin while also telling the browser to send
cookies and the `Authorization` header, so any site can call the API from a victim's
browser and read back an authenticated response.

Configure `httpCors` with an explicit origin allow-list whenever `credentials: true`
is set, and never pair `credentials: true` with `origin: "*"` or a matcher that
accepts every value.

## Non-HTTP triggers

For a trigger with no HTTP semantics — SQS, EventBridge, S3, a direct
invocation — drop every HTTP-specific entry: header/event normalizers, the CORS
middleware, security headers, and the body parser. Keep what still applies
regardless of trigger: the error handler (adapted to the trigger's own error
contract, such as a partial-batch-failure response for SQS), request context,
the input/output logger, and event validation against a schema shaped for that
trigger's payload.

The registration-order principle is unchanged: whatever plays the error
handler's role for the trigger is registered after anything that decorates a
response, for the same reason — and where the trigger has no response to
decorate, its only job is to log and let the error propagate.

For a Step Functions task the error handler's contract is to let the error
propagate with a stable `name` — the state machine matches on that string, so
it must be the literal the error class sets (see
[`validation-and-errors.md`](./validation-and-errors.md)), never a class name
the bundler may rename. The state-machine side — `Retry`, `Catch`,
`TimeoutSeconds` — is in
`${CLAUDE_PLUGIN_ROOT}/skills/configuring-serverless-service/references/step-functions-workflows.md`.

## Adding a new middleware

Before adding a middleware, ask two questions:

1. What does it read from the event or response that an earlier middleware
   must have already produced?
2. What does something later need it to have already attached?

Insert it at the point in the chain where both answers hold. A middleware
inserted without checking either question is the most common way this chain
silently breaks — it still runs, but reads a raw value a normalizer would have
fixed, or attaches a header too late for the error path to include it.

## Sources

Verified against package source 2026-09-21 — `@middy/http-cors` 7.9.2,
`@middy/http-security-headers` 7.9.2, `@middy/http-error-handler` 7.x:

- [middy — http-error-handler](https://middy.js.org/docs/middlewares/http-error-handler)
- [middy — http-cors](https://middy.js.org/docs/middlewares/http-cors)

The `if (request.response === undefined) return` guard in the CORS and
security-header `onError` hooks is what the registration order depends on. It is
present in middy 7; read the installed major's source before assuming the same of
an older or newer one.
