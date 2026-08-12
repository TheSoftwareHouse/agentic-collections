# NestJS 11 Review Checklist

Use this reference to review a NestJS 11 API change against the skill's vertical-slice, CQRS, TypeORM 0.3, contract, security, and gateway boundaries.

## Review Workflow

- [ ] Identify the changed artifacts and select only the applicable groups below.
- [ ] Apply every `[BLOCKER]` and `[HIGH]` check before reviewing lower-severity defaults.
- [ ] Inspect both dependency graphs independently; do not infer one from the other.
- [ ] Record each finding with its location, severity, violated rule, and owning reference.
- [ ] Confirm the relevant tests prove the changed seam, then apply the output rules at the end.

## Table of Contents

- [Module Checks](#module-checks)
- [Dependency Graph Checks](#dependency-graph-checks)
- [Controller Checks](#controller-checks)
- [Command and Query Handler Checks](#command-and-query-handler-checks)
- [Port and Cross-Feature Interaction Checks](#port-and-cross-feature-interaction-checks)
- [TypeORM Entity, Repository, and Migration Checks](#typeorm-entity-repository-and-migration-checks)
- [DTO and Error Contract Checks](#dto-and-error-contract-checks)
- [Test Checks](#test-checks)
- [Configuration and Security Checks](#configuration-and-security-checks)
- [Gateway Checks](#gateway-checks)
- [Output Rules](#output-rules)

## Module Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|A feature MUST keep its controller, handlers, domain rules, and persistence adapter inside its vertical slice; reject application-wide technical folders that erase ownership.|[`nestjs-foundation-and-vertical-slices.md`](./nestjs-foundation-and-vertical-slices.md)|
|[HIGH]|`CqrsModule` MUST be registered once at a stable application or platform boundary, while command, query, event-handler, and saga providers remain local to their owning feature.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[HIGH]|`TypeOrmModule.forRootAsync()` and process-wide configuration MUST stay at the composition boundary; a feature MUST use `forFeature()` only for entities it owns.|[`nestjs-foundation-and-vertical-slices.md`](./nestjs-foundation-and-vertical-slices.md); [`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[HIGH]|Feature modules MUST NOT import one another merely to reach internal services, handlers, repositories, or entities.|[`nestjs-foundation-and-vertical-slices.md`](./nestjs-foundation-and-vertical-slices.md); [`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[MEDIUM]|A shared-kernel module MUST contain only neutral, stable contracts with multiple independent consumers; NEVER accept a catch-all `common` module or a `SharedModule` that imports every feature.|[`nestjs-foundation-and-vertical-slices.md`](./nestjs-foundation-and-vertical-slices.md)|
|[MEDIUM]|All `@nestjs/*` packages MUST remain on one compatible NestJS 11 release line, with the selected compiler and Node.js constraints verified in the target repository.|[`nestjs-foundation-and-vertical-slices.md`](./nestjs-foundation-and-vertical-slices.md)|

## Dependency Graph Checks

Passing one check does not imply passing the other. These are separate checks with separate evidence.

### Nest runtime module/DI graph check

- [ ] Walk every `@Module({ imports, providers, exports })` edge and constructor injection; confirm the Nest runtime module/provider graph is acyclic.
- [ ] Reject any `forwardRef()` between feature modules or providers; it hides the reciprocal ownership instead of removing the cycle.
- [ ] Confirm each cross-feature dependency consumes an exported runtime token through a one-way process/orchestration slice above the participant features.
- [ ] Confirm every exported token resolves to a provider and that an interface is not being used as a DI token; interfaces disappear at runtime.

**Owning reference:** [`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md).

### TypeScript compile-time value graph check

- [ ] Walk runtime imports of classes, constants, decorator metadata, and barrel re-exports; reject cycles in the TypeScript value graph.
- [ ] Confirm contracts used only as types use `import type`, and no feature-internal barrel crosses a feature boundary.
- [ ] Keep runtime token values as value imports when decorators or DI require them; replacing an import with `import type` is not a Nest graph fix.

**Owning reference:** [`nestjs-foundation-and-vertical-slices.md`](./nestjs-foundation-and-vertical-slices.md); [`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md).

## Controller Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|A controller MUST map HTTP input/output only and dispatch state changes through `CommandBus.execute()` and reads through `QueryBus.execute()`.|[`nestjs-rest-api-layer.md`](./nestjs-rest-api-layer.md)|
|[HIGH]|A controller MUST NOT orchestrate business operations, transactions, retries, compensations, or cross-feature workflows, and MUST NOT call repositories or handlers directly.|[`nestjs-rest-api-layer.md`](./nestjs-rest-api-layer.md)|
|[HIGH]|Request and response DTOs MUST belong to the owning feature's `api/` area; a response DTO MUST NEVER be a TypeORM entity.|[`nestjs-rest-api-layer.md`](./nestjs-rest-api-layer.md)|
|[MEDIUM]|Any Express `Request`/`Response` use MUST be a narrow controller-only HTTP exception; those types MUST NEVER reach commands, queries, handlers, domain objects, ports, or repositories.|[`nestjs-rest-api-layer.md`](./nestjs-rest-api-layer.md)|
|[MEDIUM]|Check resource naming, create status and `Location`, `PUT`/`DELETE` idempotency, and the selected URL/versioning, OpenAPI, and pagination decisions.|[`nestjs-rest-api-layer.md`](./nestjs-rest-api-layer.md)|
|[LOW]|Middleware, guards, interceptors, pipes, and filters MUST each retain their assigned pipeline responsibility rather than hiding application orchestration.|[`nestjs-rest-api-layer.md`](./nestjs-rest-api-layer.md)|

## Command and Query Handler Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Handlers MUST declare capabilities through constructor-injected ports or explicit application services; dependencies must be visible and resolvable from the module graph.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[HIGH]|Handlers MUST NOT use `ModuleRef` as a service locator or dynamic lookup to evade a missing dependency direction.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[HIGH]|A state-changing command handler MUST own or explicitly participate in the transaction boundary and MUST NOT publish a non-durable external side effect before commit.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md); [`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[HIGH]|A query handler MUST NOT insert, update, delete, publish a state-changing event, enqueue a command, mutate shared state, or return an unbounded persistence entity.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[MEDIUM]|Sagas MUST be limited to genuine asynchronous process management with documented failure, retry, idempotency, compensation, timeout, and recovery behavior.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[LOW]|CQRS MUST remain proportional: it does not require event sourcing, a distributed broker, microservices, a generic repository abstraction, DDD aggregates for simple CRUD, or a separate denormalized read model.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|

## Port and Cross-Feature Interaction Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|A cross-feature capability MUST be focused and application-oriented, not a CRUD-shaped convenience API or a feature-internal service export.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[HIGH]|The DI token MUST be a runtime value, such as a `Symbol`; an interface alone MUST NEVER be used as the Nest injection token.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md); [`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[HIGH]|The owning module MUST bind and export the narrow token, not a TypeORM repository, entity, or concrete internal class by default.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[HIGH]|Cross-feature orchestration MUST live in a dedicated process slice that depends one way on participant ports; participant features MUST NOT import each other to coordinate.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[MEDIUM]|A synchronous read MUST use a narrow read port or maintained local read model; NEVER import a peer feature's entity or repository.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|
|[HIGH]|An integration event that must survive rollback, process failure, or an external boundary MUST use an outbox row in the same transaction, with retries and idempotent consumers.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md); [`nestjs-testing.md`](./nestjs-testing.md)|
|[MEDIUM]|An in-process event MUST be treated as eventually consistent; correctness MUST NOT depend on listener ordering or pretend that `EventBus` is a transactional outbox.|[`nestjs-cqrs-and-module-boundaries.md`](./nestjs-cqrs-and-module-boundaries.md)|

## TypeORM Entity, Repository, and Migration Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|The change MUST use TypeORM 0.3 `DataSource`-era APIs; reject legacy `Connection`, `getConnection()`, `getManager()`, `getCustomRepository()`, and `@EntityRepository()` patterns.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[HIGH]|Entities MUST remain in the owning feature's `infrastructure/` area and MUST NEVER be exported as a cross-feature contract or serialized directly as an API response.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md); [`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[HIGH]|Repository adapters MUST implement feature-owned ports and use the transaction-scoped manager or repository for every operation inside a transaction.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[HIGH]|Migrations MUST be reviewed by hand, applied forward-only in shared environments, and used instead of schema auto-synchronization; `synchronize` MUST NOT be the delivery mechanism outside disposable local experiments.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[MEDIUM]|Relation loading MUST be deliberate and bounded; reject unverified relation access inside loops and check collection queries for N+1 behavior.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|
|[HIGH]|User-controlled query values MUST be parameterized and identifiers/operators MUST use an allowlist; NEVER interpolate input into SQL or raw query fragments.|[`nestjs-typeorm-persistence.md`](./nestjs-typeorm-persistence.md)|

## DTO and Error Contract Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|The selected validation/serialization stack MUST be consistent for one DTO boundary; NEVER mix class-validator/class-transformer and Zod processing for the same contract; see [`nestjs-validation-with-zod.md`](./nestjs-validation-with-zod.md) for the stricter per-slice boundary rule.|[`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[HIGH]|The global validation boundary MUST use the selected mass-assignment defense, including `whitelist` and `forbidNonWhitelisted` where the documented Nest stack supports them.|[`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[HIGH]|Nested objects and every array element MUST be validated explicitly before application handlers run.|[`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[HIGH]|The public error contract MUST expose a stable code, human-safe message, correlation identifier, and bounded details while NEVER exposing stack traces, ORM text, internal identifiers, secrets, or raw exception messages.|[`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[HIGH]|One exception boundary MUST normalize validation and domain failures to one public shape; controllers and handlers MUST NOT invent competing envelopes.|[`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[MEDIUM]|Response mapping MUST explicitly exclude sensitive fields and define date and `null` behavior; TypeORM entities MUST NEVER be serialized directly.|[`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|

## Test Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Handler unit tests MUST instantiate handlers without a Nest container and use doubles at owned ports to prove behavior and non-mutating queries.|[`nestjs-testing.md`](./nestjs-testing.md)|
|[HIGH]|Module wiring tests MUST compile the intended module graph and resolve every exported token; direct handler construction is not wiring evidence.|[`nestjs-testing.md`](./nestjs-testing.md)|
|[HIGH]|HTTP integration tests MUST exercise the Express pipeline, DTO rejection, status mapping, and safe error shape at the public boundary.|[`nestjs-testing.md`](./nestjs-testing.md)|
|[HIGH]|Persistence tests MUST use a real supported database engine and rollback or truncate between tests; an in-memory substitute MUST NOT support claims about SQL, constraints, locking, or transactions.|[`nestjs-testing.md`](./nestjs-testing.md)|
|[HIGH]|Event/outbox tests MUST assert the outbox row commits and rolls back with the state change in the same transaction.|[`nestjs-testing.md`](./nestjs-testing.md)|
|[MEDIUM]|Builders MUST return fresh data; tests MUST arrange cross-feature state through exported ports or the public API, never peer internals.|[`nestjs-testing.md`](./nestjs-testing.md)|
|[LOW]|Full browser E2E coverage and Playwright organization belong to `tsh-e2e-testing`; do not relabel an HTTP integration test as full E2E.|[`nestjs-testing.md`](./nestjs-testing.md)|

## Configuration and Security Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Typed configuration MUST be validated before startup accepts traffic, and invalid required values MUST fail fast; slices MUST receive injected configuration rather than read `process.env` ad hoc.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|
|[BLOCKER]|Secrets MUST NEVER appear in source, committed configuration, fixtures, examples, logs, traces, metrics, exception messages, or HTTP responses.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|
|[HIGH]|Authentication and authorization MUST use the repository's guard/decorator/application seams; authorization decisions MUST NEVER belong in a repository.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|
|[HIGH]|Rate limiting and payload-size limits MUST be enforced at the Express edge, including alternate parser paths where applicable.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|
|[MEDIUM]|Correlation identifiers MUST propagate from the request edge through commands, queries, events, outbox records, and outgoing integrations without becoming credentials or business data.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|
|[HIGH]|Structured logging MUST use an explicit, tested allowlist/redaction policy for personal fields, credentials, nested payloads, error causes, and metadata.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|
|[MEDIUM]|Liveness and readiness MUST be composed at the platform boundary with bounded timeouts; optional dependencies MUST NOT make readiness fail unless the service contract requires them.|[`nestjs-configuration-security-and-observability.md`](./nestjs-configuration-security-and-observability.md)|

## Gateway Checks

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|The selected gateway adapter MUST match the client protocol and the documented feature needs; the adapter MUST be chosen consistently at the composition root, not opportunistically per gateway.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)|
|[HIGH]|The package baseline MUST match the adapter: `@nestjs/websockets` plus `@nestjs/platform-socket.io` for Socket.IO, or `@nestjs/platform-ws` plus `ws` (and `@types/ws` when directly typing `ws` values) for native WebSockets.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)|
|[HIGH]|Gateway payload DTOs MUST be validated exactly like HTTP DTOs, including nested and array values where applicable.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md); [`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md)|
|[HIGH]|A gateway MUST map messages to `CommandBus`/`QueryBus` and MUST NOT own business orchestration, cross-feature coordination, or persistence decisions.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)|
|[HIGH]|A gateway MUST live in its owning feature's `api/` folder and MUST NEVER accept Express `Request`/`Response`, a TypeORM entity, or a peer repository.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)|
|[MEDIUM]|Authentication MUST occur at the connection handshake and authorization MUST be checked per message when the action or resource requires it; do not assume an HTTP session authorizes WebSocket messages.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)|
|[MEDIUM]|Rooms, subscriptions, reconnects, duplicate messages, ordering, and horizontal fan-out MUST have an explicit protocol or infrastructure design; local connection state is insufficient for load-balanced delivery.|[`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)|

## Output Rules

- Group findings by severity first: `[BLOCKER]`, `[HIGH]`, `[MEDIUM]`, then `[LOW]`.
- Within each severity group, group findings by artifact type: module, dependency graph, controller, handler, port/cross-feature interaction, persistence, DTO/error contract, tests, configuration/security, and gateway.
- For every finding, cite the concrete location, quote or name the violated check, explain the impact, and name the owning reference file.
- Report a passing lower-severity choice only when it explains why a nearby pattern is acceptable; do not bury actionable findings among confirmations.
- If a local exception is intentional, record its narrow reason, owner, expiry or migration condition where applicable, and the reference rule it qualifies; do not silently waive a `[BLOCKER]` or `[HIGH]` rule.
