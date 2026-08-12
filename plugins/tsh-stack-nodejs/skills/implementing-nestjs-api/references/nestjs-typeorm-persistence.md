# NestJS 11 TypeORM 0.3 Persistence

Use this reference when implementing or reviewing TypeORM 0.3 entities, repositories, transactions, migrations, relation loading, or persistence boundaries in a NestJS 11 feature slice.

## Table of Contents

- [Baseline](#baseline)
- [Composition and Registration](#composition-and-registration)
- [CLI DataSource](#cli-datasource)
- [Feature Persistence Boundaries](#feature-persistence-boundaries)
- [Repository Adapters and Ports](#repository-adapters-and-ports)
- [Transactions and Handler Ownership](#transactions-and-handler-ownership)
- [Queries, Relations, and N+1](#queries-relations-and-n1)
- [Migrations and Schema Change](#migrations-and-schema-change)
- [Concurrency and Locking](#concurrency-and-locking)
- [Parameterized Queries](#parameterized-queries)
- [Decision Points](#decision-points)
- [Verification Sources](#verification-sources)

## Baseline

The persistence baseline is **TypeORM 0.3** with NestJS 11 and its `DataSource`-era APIs. Confirm the exact TypeORM driver and compatible package versions in the target repository; this reference does not select a database vendor.

| Concern | TypeORM 0.3 baseline | Boundary rule |
| --- | --- | --- |
| Runtime connection | Configure a `DataSource` through Nest's TypeORM integration. | Keep process-wide database configuration at the composition boundary. |
| Root registration | Use `TypeOrmModule.forRootAsync()` for configuration that is loaded or validated at startup. | Do not configure a root connection inside an owning feature slice. |
| Feature registration | Use `TypeOrmModule.forFeature([FeatureEntity])` in the feature module that owns the entity. | Do not register another feature's entities in the current feature merely to reach its data. |
| Repository access | Inject a typed `Repository<Entity>` with `@InjectRepository(Entity)` where the adapter owns it. | Keep the repository behind a feature port; it is not a feature API or response type. |
| CLI metadata | Export a CLI-readable `DataSource` from a dedicated configuration file. | The CLI configuration must resolve the same entities and migrations as the selected deployment path. |

Use the TypeORM 0.3 names and APIs consistently: `DataSource`, `EntityManager`, `Repository`, `dataSource.transaction(...)`, and the current migration commands. Do not copy examples written for TypeORM 0.2 without checking their API generation.

## Composition and Registration

`TypeOrmModule.forRootAsync()` belongs at the application or stable platform composition boundary. It may use an injected configuration service, a validated configuration object, and a factory that returns the TypeORM options. The root module composes the database once; feature modules opt into their owned repositories with `forFeature()`.

```ts
@Module({
  imports: [
    ConfigModule,
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (config: DatabaseConfig) => config.typeorm,
      inject: [DATABASE_CONFIG],
    }),
    OrdersModule,
  ],
})
export class AppModule {}
```

The snippet illustrates the composition seam only. Preserve the repository's configuration abstraction and driver options. Do not read `process.env` ad hoc in an entity, repository adapter, command handler, or feature module.

An owning feature registers only its own mappings and adapter providers:

```ts
@Module({
  imports: [TypeOrmModule.forFeature([OrderEntity])],
  providers: [OrderRepositoryAdapter],
  exports: [ORDER_REPOSITORY_PORT],
})
export class OrdersModule {}
```

The exact provider binding is repository-specific, but the direction is fixed: the feature owns the entity and adapter, and consumers depend on the exported port token. A feature MUST NOT export `Repository<OrderEntity>`, `OrderEntity`, or a generic persistence service as its public capability.

### Removed TypeORM 0.2 patterns

The following are explicitly rejected in a TypeORM 0.3 implementation:

- legacy `Connection` configuration or `getConnection()`/`getManager()` access;
- `getCustomRepository()` and the TypeORM 0.2 custom-repository style;
- `@EntityRepository()` custom repository declarations intended for the 0.2 API;
- treating a Nest-injected repository as a replacement for an owning feature port; and
- copying a 0.2 migration or connection example without translating it to `DataSource` APIs.

Do not solve a design problem by reviving a removed connection or custom-repository pattern. If a repository needs extra behavior, implement a feature-owned adapter around the injected 0.3 `Repository` and bind that adapter to the port token.

## CLI DataSource

TypeORM CLI commands need a concrete `DataSource` export. Keep that export in a dedicated configuration file, separate from the Nest module declaration when the CLI cannot load the application module safely. The file should resolve the target entities, migration files, naming strategy, driver options, and configuration values without opening a second unrelated connection contract.

```ts
// typeorm.config.ts — illustrative shape, not a universal path
export default new DataSource({
  type: databaseConfig.type,
  url: databaseConfig.url,
  entities: [OrderEntity],
  migrations: ['dist/database/migrations/*.js'],
  synchronize: false,
});
```

Point the TypeORM 0.3 CLI at this file with its `-d`/`--dataSource` option. The project must document the migration generation, execution, and inspection commands and their working directory. The CLI DataSource and `forRootAsync()` options should agree on entity discovery and migration locations; divergence can make a migration appear successful while the application uses a different schema.

Avoid embedding secrets in this file. Resolve configuration through the target repository's validated configuration mechanism or an environment boundary that is safe for local and CI execution. Do not make a CLI-only naming strategy, timezone, or driver choice that differs silently from runtime.

## Feature Persistence Boundaries

Place a TypeORM entity mapping inside the owning feature's `infrastructure/` folder. The entity describes persistence shape, indexes, relation metadata, and database-specific concerns; it is not the domain contract.

```text
src/features/orders/
├── application/
│   └── ports/                 # OrderRepositoryPort and other capabilities
├── domain/                    # business rules and value objects
└── infrastructure/
    ├── persistence/
    │   ├── order.entity.ts
    │   └── order.repository-adapter.ts
    └── migrations/            # only when migrations are feature-owned by convention
```

Ownership rules:

- An entity is a persistence detail, never a cross-feature contract.
- A TypeORM entity MUST NOT be returned as a response DTO or serialized directly into an API response.
- A feature API MUST NOT export another feature's entity, repository, relation object, or persistence query builder.
- Commands and queries exchange bounded application results, domain values, or feature-owned response DTOs, not unbounded persistence entities.
- Cross-feature reads use a focused query/read port or a maintained local read model; they do not import a peer's entity or repository.
- Map persistence records to domain/application results explicitly, excluding internal relation state, audit fields, and sensitive columns.

This boundary prevents schema changes from silently becoming API changes and keeps a feature free to change its database mapping without breaking peer modules.

## Repository Adapters and Ports

Define a focused repository port at the application or domain boundary. The port should express the capability a use case needs, not reproduce the entire TypeORM repository API or expose CRUD convenience methods to every caller.

```ts
export const ORDER_REPOSITORY_PORT = Symbol('orders.repository');

export interface OrderRepositoryPort {
  findById(id: OrderId): Promise<OrderRecord | null>;
  save(order: OrderRecord): Promise<void>;
}
```

The infrastructure adapter implements that port using an injected TypeORM 0.3 repository:

```ts
@Injectable()
export class OrderRepositoryAdapter implements OrderRepositoryPort {
  constructor(
    @InjectRepository(OrderEntity)
    private readonly repository: Repository<OrderEntity>,
  ) {}
}
```

Bind the adapter to the runtime token in the owning feature module and export only the token:

```ts
providers: [
  OrderRepositoryAdapter,
  { provide: ORDER_REPOSITORY_PORT, useExisting: OrderRepositoryAdapter },
],
exports: [ORDER_REPOSITORY_PORT],
```

The token is a runtime value; an interface alone cannot be a Nest injection token. Consumers use `@Inject(ORDER_REPOSITORY_PORT)` and import the port type with `import type` when it has no runtime use. Never export the concrete TypeORM repository or entity to make injection convenient.

For transaction-aware operations, define the port's transaction semantics explicitly. The adapter may receive a transaction-scoped manager, use a unit-of-work callback, or expose a method whose implementation is selected by the repository convention. Do not silently mix the global injected repository with a transaction-scoped manager and assume both participate in the same transaction.

## Transactions and Handler Ownership

A command handler that changes state owns or participates in the transaction boundary. The handler, or an application transaction coordinator it explicitly invokes, must make the state change and its required persistence operations part of one defined transaction scope.

```ts
await this.dataSource.transaction(async (manager) => {
  const orders = manager.getRepository(OrderEntity);
  // Load, validate, change, and persist within this transaction scope.
});
```

Use the transaction-scoped `EntityManager` or repositories derived from it for all database work inside the callback. Do not call an adapter backed by the default manager for one step and a transaction manager for another unless the boundary explicitly guarantees the intended behavior.

Transaction rules:

- Keep transaction ownership visible at the command/application boundary; controllers do not open transactions.
- Keep domain decisions and port calls inside the scope required for the command's consistency guarantee.
- Do not publish a non-durable external side effect before the database transaction commits.
- Persist an outbox record in the same transaction as the state change when an integration event must survive rollback or process failure.
- Treat in-process event delivery as non-transactional unless the target repository has an explicit, tested coordination mechanism.
- Translate transaction conflicts and constraint failures at the application boundary; never expose raw ORM errors in an API response.

A query handler is read-only by contract: it MUST NOT insert, update, delete, publish a state-changing event, enqueue a command, or mutate a shared cache as an implicit side effect. A query may use a read-specific projection or optimized SQL, but the result must be bounded and mapped to a read DTO or application record.

## Queries, Relations, and N+1

Design relation loading from the use case's response shape. Loading every relation by default creates hidden work and makes query cost unpredictable; loading relations one record at a time creates the N+1 problem.

Prefer one deliberate query or a bounded batch strategy:

- select only the columns needed for the application result;
- use TypeORM 0.3 find options with explicit `relations` when the relation set is small and stable;
- use `QueryBuilder` joins such as `leftJoinAndSelect` when a single query needs a known relation graph;
- batch related identifiers and hydrate them once when a collection needs a separate relation query;
- use a dedicated read port or projection for a complex read rather than importing another feature's entity; and
- verify generated SQL and query counts for collection endpoints and nested response shapes.

Do not place a relation access inside a loop without proving that it is already loaded or batched. Avoid enabling lazy relations as a blanket N+1 solution; if the target repository uses lazy loading, make the query cost explicit and test the resulting access pattern. Pagination, stable ordering, and relation joins must respect the target database's performance and correctness characteristics.

## Migrations and Schema Change

Use migrations as the shared-environment schema history. A generated migration is a starting point, not an approval: review its SQL and metadata by hand for data loss, locking, nullability, defaults, index cost, foreign-key ordering, and rollback or forward-correction behavior.

Migration discipline:

- Set `synchronize: false` in shared, CI, staging, and production environments. Schema auto-synchronization is permitted only for explicitly local experiments and MUST NOT be the delivery mechanism.
- Generate migrations from the agreed TypeORM 0.3 CLI DataSource, then inspect and amend the generated file before review.
- Apply migrations in a controlled, forward-only sequence in shared environments. Do not edit an already-applied migration; add a corrective migration for a later change.
- Separate expanding changes from destructive changes when existing clients or deployments need a transition period.
- Make data backfills, defaults, index creation, and constraint validation explicit rather than hiding them in entity metadata.
- Keep migration filenames, directories, and commands consistent with the selected repository convention.
- Verify that application startup does not silently run schema mutation outside the approved migration process.

A local developer may use `synchronize` for a disposable experiment only when the database is explicitly disposable and the setting cannot reach a shared environment. The default and all committed deployment configuration remain migration-driven.

## Concurrency and Locking

Choose a concurrency strategy based on contention, transaction duration, and the business meaning of a stale write. Do not add a lock merely because an entity has a relation, and do not assume a version column protects operations that bypass the normal update path.

| Strategy | Use when | Trade-offs and required checks |
| --- | --- | --- |
| Optimistic versioning | Conflicts are uncommon and a caller can retry or report a conflict. | Add and update a version value such as `@VersionColumn`; detect a stale write and map it to the repository's conflict response. Keep the version in the command's concurrency contract. |
| Explicit pessimistic locking | A short transaction must serialize competing changes to the same rows. | Use a transaction-scoped query and an explicitly supported lock mode such as `pessimistic_write`; verify vendor support, lock duration, deadlock behavior, and timeout handling. |
| Application invariant without a lock | The operation is naturally idempotent or a database constraint is the authoritative guard. | Encode the invariant with a unique/check constraint or atomic update and test duplicate/concurrent attempts. Do not claim a read-then-write sequence is atomic without evidence. |

Optimistic locking is usually simpler and avoids holding database locks across application work, but it requires conflict handling. Explicit locking can provide stronger serialization for a narrow critical section, but it increases waiting and deadlock risk. Keep locks inside a short command transaction and never hold them while calling an external service.

## Parameterized Queries

All user-controlled values must be bound as parameters. TypeORM `QueryBuilder` accepts named parameters and a parameter object; it must not receive string-interpolated route, query, or body input.

```ts
return this.repository
  .createQueryBuilder('order')
  .where('order.customerId = :customerId', { customerId })
  .andWhere('order.status = :status', { status })
  .getMany();
```

Rules:

- Bind values through repository methods, find options, or query-builder parameters.
- Validate and constrain sort fields, selected columns, relation names, and operators against an allowlist; parameter binding does not make identifiers safe.
- Do not concatenate user input into SQL, a `where` expression, an `ORDER BY` identifier, or a raw fragment.
- If raw SQL is necessary, keep the SQL static and bind every value through the driver-supported parameter mechanism.
- Test injection-shaped input at the application boundary and verify the generated query remains parameterized.

Parameterized construction protects query values, but it does not replace authorization, validation, row-ownership checks, or least-privilege database credentials.

## Decision Points

Resolve these choices from the target repository's instructions, deployment model, and established database conventions. Record the selected option before adding a new persistence path; do not turn one project's choice into a TSH-wide TypeORM standard.

| Decision | Acceptable approaches | Selection consequence |
| --- | --- | --- |
| Database vendor and driver | The repository's supported relational vendor and its compatible TypeORM driver | Pin compatible driver/package versions, verify supported column and lock behavior, and use the same vendor in integration tests where behavior matters. |
| Migration command and location | The established package script or TypeORM 0.3 CLI invocation, with migrations beside a database area or under feature infrastructure | Keep one CLI `DataSource` source of truth, document the working directory and `-d`/`--dataSource` usage, and ensure runtime and CLI discover the same files. |
| Naming strategy | The existing TypeORM naming strategy or an explicitly configured project strategy | Apply it consistently to entity metadata, generated migrations, and manually reviewed SQL; changing it may rename existing columns or tables. |
| Timestamp and time-zone policy | The vendor/repository's explicit UTC instant policy, timezone-aware columns, or a documented normalized representation | Choose column types and serialization rules together; test daylight-saving boundaries and make API date behavior explicit rather than relying on process-local time. |
| Test database | A real supported database service, disposable container, or repository-approved isolated database schema | Match production-relevant SQL and locking behavior, isolate test data with rollback/truncation, and document startup/cleanup ownership. Do not use an in-memory substitute when it cannot represent the selected database semantics. |

Once resolved, keep the vendor, driver, migration path, naming strategy, time policy, and test database coherent across `forRootAsync()`, the CLI DataSource, migrations, application configuration, and tests. If the repository has no convention, make the choice explicit in its project-level design rather than hiding it in an adapter.

## Verification Sources

Verify version-sensitive details against the selected TypeORM and NestJS documentation before implementation or upgrade:

- [NestJS database integration and `forRootAsync()`/`forFeature()`](https://docs.nestjs.com/techniques/database)
- [TypeORM data source options](https://typeorm.io/docs/data-source/data-source-options/)
- [TypeORM repository API](https://typeorm.io/docs/working-with-entity-manager/working-with-repository/)
- [TypeORM migrations](https://typeorm.io/docs/advanced-topics/migrations/)
- [TypeORM transactions](https://typeorm.io/docs/advanced-topics/transactions/)
- [TypeORM select query builder and parameters](https://typeorm.io/docs/query-builder/select-query-builder/)
- [TypeORM performance and query optimization](https://typeorm.io/docs/advanced-topics/performance-optimizing/)
- [TypeORM locking](https://typeorm.io/docs/working-with-entity-manager/find-options/)
