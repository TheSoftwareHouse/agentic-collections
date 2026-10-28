# NestJS Testing

Use this reference when writing or reviewing tests for NestJS 11 CQRS feature slices, their Express boundary, TypeORM persistence, or event delivery seams.

## Table of Contents

- [NestJS Testing](#nestjs-testing)
  - [Table of Contents](#table-of-contents)
  - [Testing boundary](#testing-boundary)
  - [Test layers](#test-layers)
  - [Handler unit tests](#handler-unit-tests)
  - [Module wiring tests](#module-wiring-tests)
  - [Controller and HTTP integration tests](#controller-and-http-integration-tests)
  - [Repository and persistence tests](#repository-and-persistence-tests)
  - [Event and outbox assertions](#event-and-outbox-assertions)
  - [Test data and feature boundaries](#test-data-and-feature-boundaries)
  - [Delegated end-to-end coverage](#delegated-end-to-end-coverage)
  - [Decision Points](#decision-points)

## Testing boundary

Tests should follow the same boundaries as the application. Keep the test strategy runner-agnostic: the project may use any compatible runner, but each layer must prove a specific architectural seam rather than merely increase line coverage.

- Test behavior through the narrowest boundary that can prove it.
- Use real Nest wiring where dependency registration is the subject of the test.
- Use a real database engine where SQL, constraints, transactions, locking, or driver behavior is the subject of the test.
- Keep test doubles at owned ports, not at private implementation details of a peer feature.
- Treat validation, error mapping, event publication, and transaction coordination as observable contracts.

## Test layers

| Layer | Runner-agnostic arrangement | What it must prove |
| --- | --- | --- |
| Handler unit | Instantiate a command or query handler directly and inject doubles for its owned ports. Do not create a Nest container. | Application behavior, branching, port calls, mapped results, and the rule that queries do not mutate state. |
| Module wiring | Build and compile a Nest testing module using the target module graph, then resolve the module and its exported tokens. | The DI graph resolves, handler providers are registered, and every exported token binds to a usable provider. |
| Controller/HTTP integration | Start a Nest application with the Express adapter and send requests through the HTTP pipeline. | Controller-to-bus mapping, DTO transformation, validation rejection, status mapping, and the public error shape. |
| Repository/persistence | Run against a real supported database engine with the project's migrations and repository adapters. | SQL, mappings, constraints, relations, transaction behavior, and database-specific semantics; an in-memory substitute is insufficient for these claims. |
| Event/outbox boundary | Observe the published-event boundary and inspect persistence in the transaction scope that performs the state change. | Events are published at the intended boundary, and an outbox row commits or rolls back with the state change in the same transaction. |

A test may combine adjacent layers when that is the only way to prove a seam, but it must state which layer's claim it is making. Do not turn a handler unit test into an accidental module or database test, or call a container-backed test a unit test merely because its assertions are small.

## Handler unit tests

Handler unit tests should be fast, isolated, and independent of Nest bootstrap. Construct the handler with explicit port doubles and invoke its `execute` behavior through the command or query input expected by the handler.

They should prove:

- valid input produces the bounded application result or domain outcome expected by the use case;
- invalid or conflicting domain conditions are mapped to the expected semantic exception or result;
- required ports are called with the correct capability-level arguments;
- failure from a port is handled or propagated according to the application contract;
- commands do not return unbounded TypeORM entities; and
- query handlers do not write, publish a state-changing event, enqueue a command, or mutate shared state as an implicit side effect.

Use small fakes, spies, or stubs that implement the port contract. A double should make the interaction visible without reproducing TypeORM, Nest DI, or another feature's internal service. If the test needs provider metadata, module imports, a pipe, or a database, move it to the layer that owns that concern.

## Module wiring tests

Module wiring tests use Nest's testing-module facility because the subject is the provider graph, not handler logic. Keep the arrangement focused on the module under test and its explicitly allowed dependencies.

A wiring test should:

1. build the target module with the same provider tokens and imports used by the application;
2. compile the testing module and fail on an unresolved constructor dependency;
3. resolve each handler or provider whose registration is part of the module contract;
4. resolve every token listed in the module's `exports`, including port tokens consumed by another feature; and
5. assert that each exported token resolves to the intended capability without exposing a TypeORM repository, entity, or private feature service.

Use test doubles only for external infrastructure that is outside the wiring claim. Do not replace the module graph with a direct handler construction and then call the result a wiring test. A successful compile proves registration and resolution, not business correctness; pair it with handler and boundary tests.

When a cross-feature process module is involved, compile the process module with participant modules arranged in the intended one-way direction. The test should make a reciprocal feature import or an unresolved token visible rather than hiding it with dynamic lookups.

## Controller and HTTP integration tests

Controller/HTTP integration tests exercise the Nest application through `@nestjs/platform-express`. They should use the real controller, global or module-scoped validation pipeline, exception filters, interceptors, and bus boundary selected by the target project.

Cover at least:

- a valid request reaches the expected command or query bus dispatch and returns the documented status and response DTO;
- an unexpected property is rejected when the global policy uses `whitelist` and `forbidNonWhitelisted`;
- malformed nested objects, arrays, parameters, and query values are rejected at the HTTP boundary;
- a domain failure maps to the documented status and stable machine-readable error code;
- validation failures from the relevant rejection paths use one consistent public error shape;
- error responses contain no stack trace, ORM text, internal identifier, or sensitive field; and
- the controller does not access a repository, peer-feature internal, or Express `Request`/`Response` below the transport boundary.

These tests prove HTTP behavior, not the full business workflow. Stub or isolate the bus/application seam when the purpose is controller mapping, and use the handler or persistence layers for deeper behavior. Add public API contract assertions when the target project requires them; the exact mandate remains a decision point below.

## Repository and persistence tests

Repository and persistence tests run against a real database engine supported by the target project. A memory-only substitute does not prove TypeORM SQL generation, column types, constraints, migrations, transaction isolation, locking, relation behavior, or vendor-specific semantics.

The integration database may be disposable, but it must be real. Apply the same migration model used by the application, or explicitly document the approved schema setup when migrations are not the subject of a particular test. Keep the driver and relevant database version aligned with the target project's supported deployment baseline.

Isolate each test by one of these repository-approved mechanisms:

- begin a transaction for the test and roll it back during teardown;
- use a transaction-aware fixture boundary that guarantees rollback even on failure; or
- truncate the affected tables between tests, resetting identity and respecting foreign-key ordering as required by the engine.

Do not rely on test order, a shared mutable database state, or an in-memory substitute. Test both commit and rollback paths for state changes that have transactional behavior. Include constraints, relation loading, query filtering, pagination boundaries, concurrent/conflicting writes, and migration effects when those behaviors are part of the feature contract.

Keep repository assertions at the persistence boundary: verify stored values, mapped application records, generated effects, and transaction outcomes. Do not assert that a TypeORM entity is an API response, and do not import a peer feature's entity or repository to arrange another feature's state.

## Event and outbox assertions

Assert events at the boundary where the application promises publication, not by reaching into a private handler array or assuming a particular listener execution order.

| Behavior | Assertion boundary | Required proof |
| --- | --- | --- |
| Local domain event | The selected in-process event publication seam | The event has the expected minimal payload and is published after the relevant state transition. Repeat handling is safe when retries are possible. |
| Cross-feature in-process event | The event bus or feature event contract | The receiving feature can react independently; the test does not rely on listener ordering for correctness or claim durability from `EventBus` alone. |
| Integration event | The outbox repository/table and asynchronous publisher boundary | The outbox row is written in the same transaction as the state change, is present after commit, and is absent after rollback; delivery can be retried idempotently. |

For a command that changes state and creates an outbox record, verify the atomic boundary explicitly: commit both the state change and outbox row, then force a failure before commit and verify that neither remains. A publisher test may verify delivery and retry behavior separately, but it must not substitute for the same-transaction assertion.

If aggregate-style publication is used, assert the public publication seam after the aggregate records its event and commits it. Do not make tests depend on private event arrays or a framework listener's incidental call order. If the event is intentionally non-durable, record that expectation rather than asserting broker-like guarantees.

## Test data and feature boundaries

Prefer builders that create fresh, explicit test data for each test. A builder may provide valid defaults, but each test should override only the fields relevant to its scenario and should receive a new object or entity instance.

- Builders MUST NOT return shared mutable fixtures.
- Avoid module-level objects that one test can mutate for the next test.
- Keep invalid and boundary values explicit at the call site or through named builder options.
- Build domain inputs, API DTOs, and persistence records separately when their contracts differ.
- Do not use a peer feature's private entity, repository, handler, or service to arrange state.
- Arrange cross-feature state through the peer's exported application port or public HTTP/API contract.

This preserves the same ownership rules as production code. A test that reaches through a peer's internals can pass while the public seam is broken and can make a later module refactor appear to be a behavior regression.

## Delegated end-to-end coverage

Full end-to-end coverage, Playwright usage, and e2e suite organization are QA's work and outside this skill. This reference does not restate browser workflows, Page Objects, environment orchestration, authentication setup, or suite-level E2E conventions. A scenario that must cross the deployed application boundary or exercise a complete user flow belongs in the project's E2E suite, not here.

The HTTP integration layer here remains responsible for the Nest/Express contract and can be run without a browser. Do not label a controller integration test as full E2E merely because it sends an HTTP request.

## Decision Points

Resolve these choices from the target repository's instructions, existing scripts, deployment model, and established testing conventions. Record the selection before adding a new test path; do not turn one project's choice into a TSH-wide standard.

| Decision | Acceptable approaches | Selection consequence |
| --- | --- | --- |
| Test runner | The repository's established JavaScript/TypeScript runner and assertion library, or a compatible runner selected for the project | Keep test lifecycle, mocking, watch mode, coverage, and CI commands consistent. The layers and proof obligations above do not depend on a particular runner. |
| Integration database/container policy | A real local database, a disposable database container, or an isolated schema/database managed by the repository's test environment | Use a real engine matching production-relevant behavior, define startup/cleanup ownership, and guarantee rollback or truncation isolation. Do not choose an in-memory substitute when it cannot represent the required semantics. |
| Test file naming and location | The repository's feature-local convention, a dedicated `test/` tree, or another documented unit/integration split | Keep tests discoverable by the selected runner and colocated with the boundary they verify when that is the local convention. Name the layer unambiguously. |
| Public API contract tests | Mandatory contract assertions for every public API, contract tests for selected stable endpoints, or no separate contract suite where HTTP integration assertions are the documented contract | Preserve the project's compatibility and release policy. Where contract tests are mandatory, assert status, response DTO, validation rejection, and safe error shape without coupling to framework internals. |

Regardless of these selections, retain the distinct proof obligations: direct handler units have no Nest container, wiring tests resolve the DI graph and exports, HTTP tests exercise Express and validation/error behavior, persistence tests use a real database engine, and event/outbox tests verify their correct transaction boundary.
