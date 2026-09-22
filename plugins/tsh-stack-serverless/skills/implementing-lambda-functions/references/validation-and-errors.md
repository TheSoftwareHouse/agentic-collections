# Validation and Errors

Use this reference when validating an event at the boundary, or mapping a
thrown error to an HTTP response.

## Table of Contents

- [One schema per function](#one-schema-per-function)
- [The schema library is zod](#the-schema-library-is-zod)
- [The error hierarchy](#the-error-hierarchy)
- [Exposed vs masked](#exposed-vs-masked)
- [What the validation middleware does not replace](#what-the-validation-middleware-does-not-replace)

## One schema per function

A function validates its entire event — path parameters, query string,
headers, body, whichever the trigger has — against **one schema**. The
payload type is *inferred* from that schema, never written by hand a second
time as a separate interface or type alias.

```ts
export const createWidgetSchema = /* the repository's schema library */ {
  body: {
    /* ... */
  },
};

// Inferred, not hand-written: this type and the schema can never drift apart.
export type CreateWidgetPayload = InferredType<typeof createWidgetSchema>;
```

Writing the type by hand alongside the schema is the failure mode this rule
prevents: the two are edited independently, and nothing forces them to agree
after the first edit. A validator that infers the type structurally cannot
drift from what it validates.

The validation middleware (see [`middleware-chain.md`](./middleware-chain.md))
runs the schema before the handler body executes. A handler must not receive
an event it has not already validated.

## The schema library is zod

**zod** is settled — see the library policy in
`configuring-serverless-service`. Use it for every function in a service; two
schema libraries in one service is a maintenance cost with no offsetting
benefit.

A repository already standardised on something else keeps what it has: local
convention outranks this default, and migrating a validation library is its own
task, never a side effect of adding an endpoint. What does not change either
way is the rule above — one schema for the whole event, with the payload type
inferred from it.

## The error hierarchy

Domain and HTTP errors form a small hierarchy, general enough to sit on top of
any thrown-error convention a repository already has:

```text
AppError            -- base: carries a message and an optional cause
  HttpError          -- carries a status code and whether the message is safe to expose
    NotFoundError     -- 404
    ValidationError   -- 400, carries field-level validation failures
    ... project-specific subclasses as needed
```

- `AppError` is the root. It exists so every thrown application error shares
  one ancestor a catch-all handler can recognize.
- `HttpError` adds the two things the error-rendering middleware needs: the
  HTTP status to respond with, and whether the message is safe to send to the
  client.
- Concrete subclasses (`NotFoundError`, `ValidationError`, and whatever else
  the domain needs) fix the status code and message shape for one specific
  failure so call sites throw a meaningful type instead of constructing
  `HttpError` inline every time.

Every class in the hierarchy sets `name` explicitly, as a string literal, in
its constructor:

```ts
export class InventoryError extends AppError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "InventoryError"; // a literal — never this.constructor.name
  }
}
```

`name` is the only part of an error that leaves the process as a string — it is
what a Step Functions `Catch`, a log query or an alarm matches on.
`this.constructor.name` is not stable: a bundler renames classes under
minification, and every match on the old name silently stops working with no
build error. Derive nothing from the class; state the name.

A service throws these; it never returns an error object or a discriminated
"result" shape for a failure the caller must remember to check. The
error-rendering middleware — registered after CORS and security headers, see
[`middleware-chain.md`](./middleware-chain.md) — is what turns a thrown error
into the actual HTTP response.

## Exposed vs masked

Only 4xx errors are safe to render verbatim to the client — they describe a
problem the caller can fix (bad input, missing resource). 5xx errors are
**masked**: the client receives a generic message, while the real message,
stack, and cause are logged server-side under the request id (see
[`logging-and-observability.md`](./logging-and-observability.md)).

The reasoning is the same as any public error contract: a 5xx message risks
leaking internal detail (a stack trace, an ORM error string, a file path) that
is only safe in a log a client cannot read. Do not special-case a 5xx to expose
"just this once" because the message looked harmless in isolation — a
regression risk this rule is built to remove entirely, not to negotiate about
per call site.

## What the validation middleware does not replace

Event-boundary validation checks shape: types, required fields, formats. It
does not enforce business invariants — those still belong in the service, and
should throw the same error types when they fail. A payload can be
structurally valid and still violate a rule only the service can know about
(a referenced resource that does not exist, a state transition that is not
allowed).
