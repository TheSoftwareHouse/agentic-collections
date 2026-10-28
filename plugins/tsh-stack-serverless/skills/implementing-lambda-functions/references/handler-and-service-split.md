# Handler and Service Split

Use this reference when writing a Lambda handler or pulling business logic out
of one. The split exists so the business logic can be unit-tested without a
Lambda runtime, a database, or a mocked module system.

## Table of Contents

- [The handler](#the-handler)
- [The service](#the-service)
- [The init phase](#the-init-phase)
- [What goes wrong when the split is skipped](#what-goes-wrong-when-the-split-is-skipped)

## The handler

A handler has exactly three jobs, in this order:

1. **Resolve dependencies** — pull the already-initialised clients and
   repositories it needs (see [The init phase](#the-init-phase)) and read the
   validated event.
2. **Call the service** — pass the dependencies and the event data in as
   parameters. The handler contains no business logic itself.
3. **Shape the response** — wrap the service's return value in the response
   helper the repository's HTTP layer expects, with the right status code.

A handler that grows a conditional, a loop over business data, or a second
network call beyond dependency resolution has stopped being thin. Move that
code into the service.

Export the handler function itself under one stable, conventional name
(`handler` or `handle`), used identically in every function, so the deployment
configuration can reference it without guessing.

## The service

The service is a plain function. It takes every dependency it needs —
repositories, HTTP clients, configuration values — as a **parameter**, never as
a module-level import of an infrastructure client.

```ts
// Good: every dependency arrives as a parameter.
export const listWidgets = async (
  repository: WidgetRepository,
  query: ListWidgetsQuery,
): Promise<PaginatedResult<Widget>> => {
  /* ... */
};

// Bad: the service reaches for infrastructure itself, which means a unit
// test of listWidgets can no longer avoid a real database or a module mock.
import { getDataSource } from "../shared/db.js";
export const listWidgets = async (query: ListWidgetsQuery) => {
  const dataSource = await getDataSource();
  /* ... */
};
```

This is what [`testing-lambda-code.md`](./testing-lambda-code.md) depends on: a
service built this way is tested with fakes passed as arguments, never by
stubbing module internals.

A service throws domain errors — see
[`validation-and-errors.md`](./validation-and-errors.md) — rather than
returning an error shape. It returns only the data its handler needs, not an
entire persistence entity.

## The init phase

Code at module scope in a handler file runs once per execution environment,
during the **init phase**, when the container has full CPU and no invocation is
yet in flight. Code inside the handler function runs on every invocation,
including every warm one.

Put here, at module scope:

- Parsing and validating configuration from environment variables.
- Constructing SDK clients and other objects that are expensive to build and
  safe to reuse across invocations.
- Any other setup that is both reusable and idempotent to skip on a warm
  invocation.

```ts
// Resolved once per execution environment, during the init phase.
const config = createConfig(process.env);

export const lambdaHandler = async (event: Event) => {
  // Safe to call on every invocation: memoised setup returns the same
  // reusable instance instead of building it again.
  const client = await getReusableClient();
  /* ... */
};
```

Never repeat that setup inside the handler body. The general shape of the bug
this guards against: a cold container builds and initialises some expensive,
reusable resource; the *next* invocation reuses the same warm container and
calls the same initialisation again, and the resource rejects a second
initialisation attempt outright — or silently duplicates it instead. Either way
every warm invocation now fails or wastes work that init already did. The
handler must ask a memoised accessor for the resource, never build or
initialise it itself.

**A memoised accessor must forget a rejection.** The obvious shape —
`clientPromise ??= build()` — caches whatever `build()` returns, including a
rejected promise. One transient failure during init (a secrets-store timeout, a
DNS blip) then becomes the permanent answer for every warm invocation of that
execution environment, until Lambda happens to recycle it. Clear the memo on
rejection so the next invocation retries:

```ts
let clientPromise: Promise<Client> | undefined;

export const getClient = (): Promise<Client> => {
  clientPromise ??= build().catch((error) => {
    clientPromise = undefined; // the next invocation tries again
    throw error;
  });
  return clientPromise;
};
```

This general rule is the full extent of what this skill states about
connection lifecycle. The database-specific version of it — pool sizing against
reserved concurrency, one connection per execution environment — is a separate,
persistence-focused skill; this skill only fixes where the general rule lives.

## What goes wrong when the split is skipped

- A service that imports infrastructure directly cannot be unit-tested without
  either a real dependency or a module-level mock, which then diverges from
  what production actually does.
- A handler with business logic inline duplicates that logic the moment a
  second trigger (a scheduled event, a queue) needs the same behavior, because
  there is no service to call from the second handler.
- Setup repeated inside the handler body defeats the whole purpose of the init
  phase: the container pays the expensive cost on every invocation instead of
  once.
