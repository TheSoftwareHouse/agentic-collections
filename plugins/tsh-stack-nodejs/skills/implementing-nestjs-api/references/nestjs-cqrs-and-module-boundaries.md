# NestJS 11 CQRS and Module Boundaries

Use this reference when adding CQRS, composing feature modules, coordinating features, publishing events, or diagnosing a dependency cycle.

## Table of Contents

- [Boundary Rule](#boundary-rule)
- [Default Dependency Direction](#default-dependency-direction)
- [CQRS Registration and Handler Ownership](#cqrs-registration-and-handler-ownership)
- [Constructor-Injected Ports](#constructor-injected-ports)
- [Cross-Feature Port Rules](#cross-feature-port-rules)
- [Events and Transaction Boundaries](#events-and-transaction-boundaries)
- [Sagas](#sagas)
- [Two Separate Dependency Graphs](#two-separate-dependency-graphs)
- [Cycle Resolution Procedure](#cycle-resolution-procedure)
- [Anti-patterns](#anti-patterns)
- [Proportionality](#proportionality)
- [Decision Points](#decision-points)
- [Official References](#official-references)

## Boundary Rule

`forwardRef()` is rejected as a feature-boundary solution. It resolves a Nest runtime DI/module cycle without removing the bidirectional ownership or execution dependency, so the design defect survives. NEVER wrap mutually importing feature modules or providers in `forwardRef()` to make an invalid direction appear valid.

Instead, make ownership directional. A feature may depend on neutral contracts, platform infrastructure, and explicitly exported capabilities of a lower-level feature. It must not require a peer feature to depend back on it. Cross-feature work belongs in a process/orchestration slice above the participants.

## Default Dependency Direction

Use this direction unless the target repository's established architecture gives a more specific, documented ownership rule:

```text
HTTP adapter/controller
        ↓
feature application layer (commands, queries, handlers)
        ↓
domain model and feature ports
        ↓
TypeORM persistence adapter / external adapters
        ↓
platform infrastructure

cross-feature process/orchestration module → exported feature ports
features → shared-kernel contracts and published events
```

The arrows describe dependency ownership, not necessarily synchronous timing. The application composition root imports platform modules, feature modules, and explicit process modules. A feature owns its controllers, handlers, domain rules, persistence adapters, and local providers. A process module coordinates participant capabilities without becoming a hidden peer-feature dependency.

A representative feature keeps ownership local:

```text
src/features/orders/
├── orders.module.ts
├── api/                     # controller and request/response DTOs
├── application/
│   ├── commands/            # commands and command handlers
│   ├── queries/             # queries and query handlers
│   ├── events/              # local event handlers, when needed
│   └── ports/               # application capabilities owned by orders
├── domain/                  # rules, value objects, aggregates, events
└── infrastructure/          # TypeORM mappings and repository adapters
```

Adapt names to local conventions, but do not replace feature ownership with application-wide `controllers/`, `services/`, `entities/`, or `repositories/` folders.

## CQRS Registration and Handler Ownership

Register `CqrsModule` once at a stable application or platform composition boundary. Do not create a separate bus per feature. Each owning feature registers its own command, query, event-handler, and saga providers in feature-local arrays and includes those arrays in its module's `providers`.

```ts
const commandHandlers = [CreateOrderHandler];
const queryHandlers = [GetOrderHandler];
const eventHandlers = [OrderPlacedHandler];

@Module({
        imports: [CqrsModule, OrdersModule],
})
export class AppModule {}

@Module({
  providers: [...commandHandlers, ...queryHandlers, ...eventHandlers],
})
export class OrdersModule {}
```

The exact `CqrsModule` import location follows the target repository's composition convention; the invariant is one stable registration boundary and local ownership of handlers. Controllers dispatch through `CommandBus.execute()` for state changes and `QueryBus.execute()` for reads. They do not orchestrate business operations.

## Constructor-Injected Ports

Handlers MUST declare their required capabilities as constructor-injected ports, adapters, or explicit application services. Dependencies must be visible in the constructor and resolvable from the owning module's provider graph.

`ModuleRef` MUST NOT be used as a service locator to hide a missing dependency direction, defer a peer lookup, or bypass a port. A dynamic lookup can suppress a compile-time signal while retaining the same runtime coupling. If a handler needs another feature, move the workflow to a process module or define a narrow exported port.

## Cross-Feature Port Rules

A feature's external API is a small, application-oriented capability surface. It does not expose TypeORM repositories, entities, generic internal services, or command handlers.

1. **Focus the capability.** Define the port at the consumer or domain boundary with a focused capability such as `reserve`/`release`, not CRUD-shaped convenience methods.
2. **Use a runtime token value.** Keep the DI token as a real value, such as a `Symbol`, in a neutral shared-contracts module or a carefully selected owning boundary. An interface alone disappears at runtime.
3. **Bind and export the token.** Bind the token to the owning feature's adapter/provider and export the token rather than the concrete class by default.
4. **Coordinate in one direction.** A dedicated orchestration/process module may import the participant modules and consume their exported ports. Neither participant imports the other merely to reach an internal handler or service.
5. **Read through a narrow seam.** For a synchronous decision, use a focused query/read port or a maintained local read model. Never import a peer's TypeORM entity or repository.
6. **Use events for eventual consistency.** Publish a fact/event and let the receiving feature react independently when synchronous consistency is unnecessary. Use an outbox or another durable delivery design when the boundary crosses a transaction or process.

A token and interface show the seam without prescribing a service implementation:

```ts
export const INVENTORY_PORT = Symbol('inventory.port');

export interface InventoryPort {
  reserve(input: ReserveInventoryInput): Promise<ReservationResult>;
}
```

The owning module binds and exports the runtime value. This is a provider shape, not a complete implementation:

```ts
providers: [{ provide: INVENTORY_PORT, useExisting: InventoryAdapter }],
exports: [INVENTORY_PORT],
```

When a consumer injects an interface-shaped port, it uses the runtime value explicitly:

```ts
constructor(@Inject(INVENTORY_PORT) private readonly inventory: InventoryPort) {}
```

The process module depends on the exported tokens of its participants. It returns an explicit application result, command, or event; it does not make feature internals public.

## Events and Transaction Boundaries

Use `EventBus` for in-process publication when the target repository selects that model. Aggregate-style publication uses `EventPublisher.mergeObjectContext()` and then `commit()` after the aggregate has recorded its events:

```ts
const context = this.publisher.mergeObjectContext(order);
// apply the domain operation and record events on the context
context.commit();
```

The snippet illustrates the publication seam only. `commit()` is not a substitute for a database commit, and `EventBus` does not automatically provide durable delivery or transaction coordination.

Keep event payloads minimal, versionable, and independent of foreign persistence models. Choose safeguards by event type:

| Event type | Suitable use | Required safeguard |
| --- | --- | --- |
| Local domain event | Same-process reaction within one feature after a state transition | Publish after the transition; make handlers safe for repeats when retries are possible. |
| Cross-feature in-process event | Decoupled reaction inside one modular monolith | Treat delivery as eventually consistent; document ordering, failure, and repeat behavior. Do not assume one TypeORM transaction wraps all handlers. |
| Integration event | Broker, external side effect, or business-critical downstream action | Write an outbox record in the same database transaction, publish asynchronously, and use idempotent consumers, retries, and monitoring. |

A command handler that changes state owns or participates in the transaction boundary. It MUST NOT publish a non-durable external side effect before the transaction commits. If strong synchronous consistency is required, make an explicit port call inside a defined transaction scope after reviewing transaction and resource implications; do not disguise that call as an event.

The outbox boundary is transactional: state change and outbox row commit together, then a publisher delivers the integration event. An in-process `EventBus` publication alone is not an outbox and must not be represented as durable integration delivery.

## Sagas

Use a saga only for genuine asynchronous process management: a multi-step process that reacts to events over time and needs explicit coordination. A saga is not a default wrapper for a simple command handler and is not a way to conceal a module cycle.

Before adding one, document:

- the triggering and resulting events;
- failure states and the retry policy;
- idempotency keys or deduplication behavior;
- compensation actions and their limits; and
- observability, timeout, and operator-recovery behavior.

Keep a saga's inputs and outputs as contracts. It may emit the next command or event, but each participant owns its own state and transaction. Do not assume saga steps share one transaction or execute exactly once.

## Two Separate Dependency Graphs

Check both graphs independently. Passing one check does not imply passing the other.

| Graph | Created by | Required check |
| --- | --- | --- |
| TypeScript compile-time/value graph | Runtime imports of classes, constants, decorator metadata, and barrel re-exports. Type-only imports do not emit runtime dependencies. | Walk runtime value imports and barrel re-exports. Keep value imports acyclic and use `import type` for contracts used only as types. Reject feature-internal barrels across feature boundaries. |
| Nest runtime module/DI graph | `@Module({ imports, providers, exports })`, provider tokens, and constructor injection. | Walk module imports and provider dependencies. Keep the runtime graph acyclic, export narrow tokens, and place cross-feature workflows above the participants. |

A TypeScript interface cannot serve as a Nest DI token because it disappears at runtime. Use `@Inject(PORT_TOKEN)` with a runtime token value for an interface-shaped port. Conversely, `import type` is valid only where no runtime value or decorator metadata is required. Replacing a runtime import with `import type` may fix the TypeScript value graph while leaving the Nest module/DI graph cyclic, so it is not a complete cycle fix.

## Cycle Resolution Procedure

When a cycle is reported, follow this order rather than adding a runtime indirection:

1. **Record the participants.** Name every module, provider, runtime import, token, and barrel involved; distinguish a compile-time/value symptom from a Nest bootstrap/DI symptom.
2. **Check the TypeScript value graph.** Walk class, constant, decorator-metadata, and barrel imports. Replace type-only edges with `import type` only when they have no runtime requirement, and remove feature-internal barrel edges.
3. **Check the Nest runtime graph separately.** Walk `@Module` imports, exports, provider bindings, and constructor injection. Identify the reciprocal feature ownership or provider dependency.
4. **Extract the capability.** Define a focused port and runtime token at the consumer/domain or neutral contract boundary. Do not export the peer's entity, repository, or internal service.
5. **Move coordination upward.** Create or use a process/orchestration slice that imports the participant modules one way and consumes their exported tokens.
6. **Choose the delivery boundary.** Use a direct port call for required synchronous consistency, an in-process event for acceptable eventual consistency, or a transactional outbox for durable integration delivery.
7. **Re-run both graph checks.** Confirm the TypeScript value graph and Nest runtime module/DI graph are each acyclic; do not accept a fix that only makes bootstrap succeed through `forwardRef()`.
8. **Test the seam.** Resolve the module wiring, exercise the port contract, and verify event/outbox transaction behavior and idempotency where applicable.

## Anti-patterns

Reject all nine patterns below:

1. Mutual `FeatureAModule`/`FeatureBModule` imports wrapped in `forwardRef()`.
2. Mutual service injection, including hiding it behind `ModuleRef.get()` or optional injection.
3. A controller in feature A directly invoking a command handler, service, or repository internal to feature B.
4. Exporting TypeORM repositories or entities as a feature's public API.
5. A global `SharedModule` that imports all features and then exports all providers.
6. Importing whole feature barrels merely for a command or event type, especially when the barrel exports modules or providers.
7. Treating events as synchronous RPC and relying on handler ordering for correctness.
8. Publishing a broker/external event before persistence commits, or assuming `EventBus` is a transactional outbox.
9. Query handlers that mutate state, commands that return unbounded persistence entities, or controllers that contain business orchestration.

## Proportionality

`@nestjs/cqrs` separates responsibilities; it does not mandate heavyweight distributed architecture. The target guidance therefore does **not** require:

- event sourcing;
- a distributed event broker;
- microservices;
- a generic repository abstraction;
- DDD aggregates for simple CRUD; or
- a separate denormalized read model or second database for every read.

It also does not invent product-wide policy for authentication, RBAC roles, database vendor or schema, API version, pagination envelope, logging vendor, or deployment topology. Those remain target-repository decisions. The skill does not replace feature-specific requirements or local conventions discovered before implementation. The target pattern rejects `forwardRef()` as an architectural escape hatch; any legacy exception would require a documented, time-bounded migration decision outside this pattern, never a usage recipe here.

## Decision Points

Resolve these choices from the target repository's instructions, requirements, and established conventions. Do not turn this table into a TSH-wide standard:

| Consistency/durability need | Preferred boundary | Required consequence |
| --- | --- | --- |
| The caller needs a result before completing the use case and the operation can share a defined transaction/resource scope | Focused synchronous port call from a process/application handler | Review transaction ownership, timeout, failure propagation, and whether both resources can actually participate safely. Keep the call behind an exported token. |
| A receiving feature may react later and loss is explicitly acceptable or separately handled | Cross-feature in-process event through `EventBus` | Document eventual consistency, ordering, retries, idempotency, and failure visibility. Do not rely on handler order for correctness. |
| The event must survive a transaction rollback, process crash, broker boundary, or external side effect | Transactional outbox plus asynchronous publisher | Persist the outbox record in the same transaction as the state change; implement retries, idempotent consumers, monitoring, and replay/operator handling. |

Select one boundary per interaction and record exceptions at the owning process or feature. A port call is not automatically stronger merely because it is synchronous, and an event is not durable merely because `EventBus` delivered it in-process. The target project's consistency, durability, transaction, and deployment requirements decide the choice.

## Official References

- [NestJS modules](https://docs.nestjs.com/modules)
- [NestJS CQRS recipe](https://docs.nestjs.com/recipes/cqrs)
- [NestJS events and sagas](https://docs.nestjs.com/recipes/cqrs)
- [TypeScript module theory](https://www.typescriptlang.org/docs/handbook/modules/theory.html)
- [TypeORM transactions](https://typeorm.io/docs/advanced-topics/transactions/)
