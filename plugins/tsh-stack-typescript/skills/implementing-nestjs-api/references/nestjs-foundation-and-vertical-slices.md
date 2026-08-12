# NestJS 11 Foundation and Vertical Slices

Use this reference when bootstrapping or reorganizing a NestJS 11 REST service around vertical feature slices.

## Table of Contents

- [Baseline](#baseline)
- [Composition Root](#composition-root)
- [Compiler and Package Constraints](#compiler-and-package-constraints)
- [Vertical Feature Slices](#vertical-feature-slices)
- [Dependency Direction](#dependency-direction)
- [Shared-Kernel Boundary](#shared-kernel-boundary)
- [Decision Points](#decision-points)
- [Verification Sources](#verification-sources)

## Baseline

The target baseline is NestJS 11 with TypeScript and `@nestjs/platform-express`. Use Nest's Express adapter as a transport detail; feature application and domain code must depend on Nest abstractions or domain contracts, not Express request/response objects.

| Concern | Baseline rule | Constraint to verify |
| --- | --- | --- |
| Framework | Use one compatible NestJS 11 release line for the application. | Verify the selected release and peer-dependency compatibility before pinning exact minor or patch versions. |
| HTTP adapter | Use `@nestjs/platform-express` and the default Express adapter unless the target application requires another adapter. | Verify the adapter version is aligned with the selected NestJS 11 line. |
| Runtime | Use Node.js 20 or above. | Verify the selected NestJS 11 release documentation and the target repository's supported active-LTS policy; do not invent a fixed Node minor. |
| CQRS | Register `CqrsModule` at a stable application/platform boundary when CQRS is used. | Verify the `@nestjs/cqrs` release is compatible with the selected NestJS 11 line. |
| TypeScript | Enable strict type checking and preserve type-only boundaries. | Verify the exact compiler and decorator settings supported by the selected NestJS release. |

NestJS 11 package compatibility is a release-line constraint, not permission to mix arbitrary `@nestjs/*` versions. Keep the framework packages, including `@nestjs/core`, `@nestjs/platform-express`, and any optional Nest packages, on one compatible Nest 11 line. Confirm the exact package peer ranges from the selected release before installation or upgrade.

## Composition Root

`NestFactory.create()` belongs in the application entry point and is the composition root. It creates the Nest application from the root module, where platform concerns and feature modules are assembled.

```ts
const app = await NestFactory.create(AppModule);
await app.listen(port);
```

The root module or a stable platform module should compose:

- the Express platform adapter and edge middleware;
- global pipes, filters, interceptors, and guards;
- configuration and infrastructure modules;
- `TypeOrmModule.forRootAsync()` or the equivalent database composition boundary;
- `CqrsModule` when the application uses `@nestjs/cqrs`; and
- feature modules and explicit process/orchestration modules.

A feature module owns its controllers, application handlers, domain rules, infrastructure adapters, and feature-local providers. A feature slice must not own process-wide bootstrap configuration. Keep `forRootAsync()` calls for database, configuration, and other process-level infrastructure at the composition boundary so feature modules remain reusable and dependency direction remains visible.

Do not use the composition root to hide feature coupling. Imports should describe the actual one-way runtime graph; a broad root import list is acceptable, while reciprocal feature imports are not.

## Compiler and Package Constraints

Before implementation, inspect the target repository's `tsconfig` files and package manager configuration. Verify, rather than assume, the following:

- strict compiler checking is enabled, including the repository's chosen settings for nullability, unused code, module resolution, and import consistency;
- the decorator and metadata compiler configuration is supported by the selected NestJS 11 release and its TypeScript version;
- the selected module and target settings preserve the runtime behavior required by Nest decorators and the chosen Node.js baseline;
- all `@nestjs/*` packages resolve to one compatible NestJS 11 release line;
- `@nestjs/platform-express` is installed when Express is the intended adapter; and
- Node.js 20 or above is declared and enforced consistently across local development, CI, and deployment.

Do not copy a compiler flag set from another project without checking its interaction with the target repository's TypeScript version and Nest release. Do not present an exact Nest minor, patch, TypeScript, or Node minor as a universal requirement when the official compatibility information has not been verified.

Use `import type` for contracts that have no runtime value. If a contract is used as a decorator or dependency-injection value, it needs a runtime token and must not be reduced to a type-only import.

## Vertical Feature Slices

A feature is the default unit of ownership. Keep HTTP, application/CQRS, domain, and persistence concerns together instead of creating application-wide `controllers/`, `services/`, `entities/`, or `repositories/` folders.

A representative slice is:

The feature root is `src/features/`.

```text
src/
├── main.ts                         # NestFactory.create() and process bootstrap
├── app.module.ts                   # composition root module
├── platform/                       # process-wide configuration and adapters
├── shared-kernel/                  # intentionally small neutral contracts
└── features/
    ├── orders/
    │   ├── orders.module.ts
    │   ├── api/                    # controllers and request/response DTOs
    │   ├── application/
    │   │   ├── commands/           # command classes and handlers
    │   │   ├── queries/            # query classes and handlers
    │   │   ├── events/             # local event handlers, when needed
    │   │   └── ports/              # application capabilities owned by orders
    │   ├── domain/                 # rules, value objects, aggregates, events
    │   └── infrastructure/         # TypeORM mappings and repository adapters
    └── inventory/
        └── ...
```

Adapt names to established repository conventions, but preserve ownership. A slice should expose a narrow application capability, not its persistence model. Request and response DTOs belong in the owning feature's `api/` area; TypeORM entities remain infrastructure details.

Keep handler provider arrays and feature-specific module registration local to the owning slice. The composition root may import many independent feature modules, but a feature should not import a peer merely to reach that peer's internal service, repository, entity, or handler.

## Dependency Direction

Use this default direction:

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

The arrows represent dependency ownership, not necessarily call timing. Controllers map transport input and dispatch use cases. Application handlers coordinate a feature through ports. Infrastructure implements those ports. A cross-feature workflow belongs in a dedicated process/orchestration slice that depends one way on participant capabilities.

Use narrow runtime tokens for injected ports. Export the token and its owning capability, not a TypeORM repository, entity, or feature-internal service. If a workflow needs another feature's data, prefer a focused read port or an explicitly maintained local read model over importing the peer's persistence types.

Keep both dependency graphs acyclic:

1. The TypeScript value graph covers runtime imports, decorator metadata, constants, and barrel re-exports. Keep value imports acyclic and use `import type` only for type-only contracts.
2. The Nest runtime graph covers module imports, provider tokens, and constructor injection. Keep module and provider dependencies acyclic and compose cross-feature workflows above their participant features.

Changing a value import to `import type` can fix a compile-time cycle while leaving a Nest dependency-injection cycle unchanged. Inspect both graphs when diagnosing a cycle.

## Shared-Kernel Boundary

The shared kernel is a small, stable ownership boundary for contracts that are genuinely neutral and used by multiple features. Suitable contents include:

- shared identifiers and immutable value types;
- narrow port interfaces and their runtime injection tokens;
- minimal cross-feature event contracts; and
- universally applicable abstractions with no feature ownership.

It must not contain feature services, feature-specific DTOs, TypeORM entities, repositories, mutable aggregate state, or orchestration that belongs to one workflow. Shared contracts describe capabilities or immutable facts; they do not expose another feature's persistence model.

Do not create a catch-all `common` module. Do not create a `SharedModule` that imports or exports every feature. Either pattern hides ownership and recreates coupling at a different location. A shared-kernel module may depend only on neutral contracts and stable platform primitives; it must not become a registry of feature implementations.

Before adding a shared-kernel item, identify at least two independent consumers and confirm that neither consumer owns the concept. If the item serves one feature or one workflow, keep it in that feature or orchestration slice instead.

## Decision Points

Resolve these choices from the target repository's instructions and established conventions before introducing a new shared-kernel boundary:

| Decision | Acceptable approach | Selection rule |
| --- | --- | --- |
| Name | Use an established local name; otherwise use `shared-kernel`, `contracts`, or an equivalent name that communicates neutral ownership. | Preserve the repository's existing terminology and avoid renaming an established boundary without a migration reason. |
| Location | Place neutral contracts under the repository's existing platform/shared area or at `src/shared-kernel/` when the feature tree is the established structure. | Choose one stable location that is easy to import without causing feature-to-feature ownership. |
| Admission rule | Require multiple independent consumers, stable semantics, and no feature-specific persistence or orchestration. | Reject additions that merely shorten an import or conceal a feature dependency. |
| Module shape | Use a small module only when Nest registration is needed; keep pure types and tokens free of unnecessary module imports. | Do not add a module wrapper that imports feature modules or exports their implementations. |

## Verification Sources

These details are sensitive to framework and compiler releases. Verify them against the selected target versions and repository policy before implementation:

- [NestJS first steps and `NestFactory.create()`](https://docs.nestjs.com/first-steps)
- [NestJS modules and module composition](https://docs.nestjs.com/modules)
- [NestJS migration guide](https://docs.nestjs.com/migration-guide)
- [NestJS database integration](https://docs.nestjs.com/techniques/database)
- [NestJS CQRS recipe](https://docs.nestjs.com/recipes/cqrs)
- [TypeScript module theory and runtime imports](https://www.typescriptlang.org/docs/handbook/modules/theory.html)

The official documentation is the source for release compatibility, supported compiler/decorator configuration, and current registration APIs. This reference intentionally does not invent exact minor or patch pins.
