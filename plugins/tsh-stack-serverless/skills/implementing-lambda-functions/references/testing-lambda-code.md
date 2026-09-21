# Testing Lambda Code

Use this reference when adding or reviewing tests for a handler or a service.
It describes what makes each layer testable and what a test at that layer must
actually prove — not which test runner or assertion library to use. Discover
and follow the repository's existing choice; nothing here depends on which one
it is.

## Table of Contents

- [Two layers, two kinds of test](#two-layers-two-kinds-of-test)
- [Testing the service with fakes](#testing-the-service-with-fakes)
- [Testing the handler and the middleware chain](#testing-the-handler-and-the-middleware-chain)
- [What a test must not do](#what-a-test-must-not-do)

## Two layers, two kinds of test

The handler/service split in
[`handler-and-service-split.md`](./handler-and-service-split.md) exists
largely to make this section possible: the service is pure business logic and
gets a fast unit test, while the handler is mostly wiring plus the middleware
chain, and is worth testing directly only when the chain's own behavior is
what changed.

| Layer | What a test proves | When it's worth writing |
| --- | --- | --- |
| Service | The business logic produces the right result and the right thrown error for a given input and given fakes | Every service, as the default and cheapest test |
| Handler + middleware chain | Validation, CORS, error mapping, and response shaping behave correctly end to end | Only when the change touches the chain itself, not every handler |

## Testing the service with fakes

Because the service takes every dependency as a parameter (see
[`handler-and-service-split.md`](./handler-and-service-split.md)), a test
supplies a fake implementation of each one directly — a fake repository, a
fake client — rather than reaching into a module and replacing an internal
with a mock. Fakes over module-internal stubbing is the point of the parameter
convention: the test exercises exactly the function's declared contract, and
nothing about how the module happens to be wired internally.

```ts
// The kind of fake a service test supplies, independent of the assertion
// library or test runner in use.
const fakeRepository = {
  list: async () => ({ items: [widgetFixture], total: 1 }),
};

const result = await listWidgets(fakeRepository, { page: "1" });
// assert result shape, not the internals of fakeRepository
```

A service test needs no Lambda runtime, no real database, and no HTTP layer —
that independence is the return on keeping the service pure.

## Testing the handler and the middleware chain

Write a handler-level test when the middleware chain itself is part of the
behavior under test: a validation failure must produce the right error shape,
CORS headers must appear on both success and error responses, a malformed
event must be rejected before the service is ever called. These are exactly
the behaviors that live in middleware configuration rather than in the
service, so a service-level test cannot exercise them.

Invoke the exported handler (the one wrapped by the middleware chain, not the
inner business function) with a representative event and assert on the full
response: status code, headers, and body. This is the only way to prove the
registration-order rule in
[`middleware-chain.md`](./middleware-chain.md) actually holds for a given
handler — for example, that an error response still carries the CORS headers
a downstream client depends on.

If the deployment tooling discovers function entry points by pattern-matching
handler file names, check where a sibling test file can live without being
picked up as a second candidate entry point; some bundlers glob for a handler
file's name and would treat a co-located spec file as another handler unless
it is placed elsewhere.

## What a test must not do

- Assert against a real database, queue, or third-party API from a service
  test — that is what fakes are for. Save real infrastructure for a smaller
  number of handler-level or integration tests that exist specifically to
  prove the fakes have not drifted from reality.
- Stub a module import to replace an internal dependency instead of passing a
  fake as a parameter. If a test needs to reach into a module to replace
  something, that is a signal the function under test still imports
  infrastructure directly rather than receiving it as a parameter.
- Treat a passing handler-level test as proof the service logic is correct, or
  vice versa. The two layers prove different things; neither substitutes for
  the other.
