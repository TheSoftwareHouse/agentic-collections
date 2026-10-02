# NestJS 11 REST API Layer

Use this reference when creating or reviewing NestJS controllers, REST contracts, DTO boundaries, or HTTP pipeline behavior.

## Table of Contents

- [Contract Boundary](#contract-boundary)
- [Controller Responsibilities](#controller-responsibilities)
- [DTO Ownership](#dto-ownership)
- [REST Semantics](#rest-semantics)
- [Express Edge Exception](#express-edge-exception)
- [Nest Pipeline Responsibility Mapping](#nest-pipeline-responsibility-mapping)
- [OpenAPI Contract Artifact](#openapi-contract-artifact)
- [Decision Points](#decision-points)
- [Review Checklist](#review-checklist)
- [Official References](#official-references)

## Contract Boundary

A controller is the feature's HTTP boundary. It translates route parameters, query values, headers, and request bodies into feature-owned application messages, dispatches those messages, and translates the result into the selected HTTP response. It is not an application-service replacement.

The default direction is:

```text
HTTP request
    -> feature controller and request DTO
    -> CommandBus.execute() or QueryBus.execute()
    -> feature application handler
    -> response DTO or explicit HTTP result
```

Keep transport concerns at the edge. Commands, queries, handlers, domain objects, and repositories must remain independent of Express request and response types.

## Controller Responsibilities

Controllers MUST perform HTTP mapping only:

- Bind route, query, header, and body values to feature-owned request DTOs.
- Let the Nest validation pipeline validate and transform inputs according to the repository convention.
- Use `CommandBus.execute()` for state-changing use cases such as create, update, or delete.
- Use `QueryBus.execute()` for reads and searches.
- Return a feature-owned response DTO, an explicit empty response, or a narrowly justified HTTP result.
- Declare the route's status, headers, and documented response contract where those are part of the API.

Controllers MUST NOT:

- Orchestrate multiple business operations, transactions, retries, compensations, or cross-feature workflows.
- Call a TypeORM repository, persistence adapter, command/query handler, or domain service directly to bypass the bus boundary.
- Reach into a peer feature's controller, entity, repository, handler, or other internal implementation.
- Resolve a peer feature through `ModuleRef`, a dynamic lookup, or a private import.
- Make authorization, persistence, or business-state decisions that belong in a guard or application handler.

When a request needs several feature capabilities, put the workflow in a dedicated application/process slice. The controller dispatches one command or query to that workflow; it does not become the workflow coordinator.

### Command and query dispatch

Commands and queries are messages, not service method names exposed through HTTP. Keep their inputs explicit and bounded. The handler owns application orchestration and returns an application result that the feature can map to a response DTO. A controller should not instantiate a handler or bus message with hidden request state.

```ts
@Post()
create(@Body() request: CreateOrderRequestDto) {
  return this.commandBus.execute(new CreateOrderCommand(request));
}

@Get(':id')
get(@Param('id') id: string) {
  return this.queryBus.execute(new GetOrderQuery(id));
}
```

The example shows the dispatch seam only; it does not prescribe a command constructor or response shape. Preserve the target repository's established conventions.

## DTO Ownership

Request and response DTOs belong to the owning feature's `api/` folder. Keep transport contracts close to the controller and feature vocabulary rather than placing all DTOs in a global application-wide directory.

A representative layout is:

```text
src/features/orders/api/
├── orders.controller.ts
├── create-order.request.dto.ts
├── get-order.request.dto.ts
└── order.response.dto.ts
```

Rules:

- Request DTOs describe accepted HTTP input, including explicit path, query, body, and header contracts.
- Response DTOs describe the public representation, not the persistence model.
- A response DTO MUST NEVER be a TypeORM entity, and a TypeORM entity must never be returned as an API response by accident.
- Map application results to response DTOs explicitly, excluding internal identifiers, relation state, audit data, and sensitive fields that are not part of the contract.
- Do not reuse a peer feature's request DTO as an internal command contract. Share a narrow immutable contract only when ownership and compatibility are explicit.
- Keep validation and OpenAPI metadata on the selected DTO/schema boundary consistently; do not mix incompatible validation/serialization approaches for the same contract.

## REST Semantics

Use resource-oriented names and stable nouns in URLs. Prefer plural resource collections such as `/orders` and identifiers such as `/orders/{orderId}`. Keep verbs in the path only when the operation is genuinely an action that cannot be represented as a resource transition.

| Operation | Typical method/status | Required semantic check |
| --- | --- | --- |
| Create a resource | `POST`; normally `201 Created` | Return the representation or an agreed empty body and provide a `Location` header for the created resource when a resource was created. |
| Replace a resource | `PUT`; commonly `200 OK` or `204 No Content` | Treat the operation as idempotent: repeating the same complete replacement has the same intended resource state. |
| Partially update | `PATCH`; project policy determines the response status | Define whether the patch format and retry behavior are safe for the operation; do not silently present a non-idempotent action as `PUT`. |
| Remove a resource | `DELETE`; commonly `204 No Content` | Treat deletion as idempotent at the resource-state level: repeating it must not recreate or mutate another resource. Define the not-found response policy. |
| Read a resource | `GET`; normally `200 OK` | Do not mutate state or trigger non-durable side effects from a read. |

Status codes and error responses must match the target API contract. At minimum, distinguish successful creation, successful retrieval/update, successful deletion, validation failure, authentication/authorization failure, missing resource, conflict, and unexpected failure. Do not use a successful status to hide a domain failure.

`POST` is not generally idempotent. If clients may retry a create or other state-changing request, use a repository-approved idempotency key or another explicit deduplication policy rather than assuming transport retries are safe. The key's scope, retention, replay response, and storage transaction belong to the target project contract.

The `Location` header should identify the canonical URL of the newly created resource. Generate it from the route/versioning convention rather than concatenating an untrusted host or request header. If the API intentionally returns an asynchronous operation resource instead, document that resource and its status semantics explicitly.

## Express Edge Exception

Nest's Express adapter is a transport detail. `Request` and `Response` may be touched inside a controller only for a concrete HTTP concern that Nest's normal return-value abstraction cannot express cleanly, such as streaming, a narrow middleware integration, or precise response-header handling.

This is a narrow exception, not a way to pass transport state downward:

- The controller may read or write the Express object for that one concern.
- Commands, queries, handlers, domain objects, repositories, ports, and peer features MUST NOT accept or return Express `Request`/`Response` types.
- Do not put Express objects in command payloads, query payloads, events, DTOs used below the controller, or persistence adapters.
- Prefer Nest abstractions such as decorators, guards, interceptors, pipes, filters, streams, and explicit headers before reaching for adapter-specific objects.

A controller that needs an Express object for streaming still dispatches domain/application work without passing that object into the handler. The adapter exception ends at the controller boundary.

## Nest Pipeline Responsibility Mapping

Choose the narrowest Nest extension point that owns the concern. Do not place cross-cutting logic in controllers merely because the controller sees the request first.

| Pipeline component | Owns | Must not become |
| --- | --- | --- |
| Middleware | Adapter-level request preprocessing, correlation bootstrap, raw body or library integration, and concerns that do not need route metadata | A substitute for authorization, DTO validation, or feature orchestration |
| Guards | Authentication and authorization decisions, including route metadata and access checks | A persistence layer or a place to run the use case |
| Interceptors | Cross-cutting execution behavior such as timing, response shaping where standardized, caching hooks, or tracing | A hidden business workflow or an accidental second error contract |
| Pipes | Input transformation and validation for route parameters, queries, bodies, and custom values | Authorization, persistence lookups, or domain orchestration |
| Exception filters | Mapping known exceptions and unhandled failures to the HTTP error contract, with safe logging/redaction | Business recovery, retries, or leaking stack traces and ORM details |

Keep the order and scope of global, controller, and route-level components consistent with the target repository. A component should have one clear responsibility and a test that proves its boundary behavior.

## OpenAPI Contract Artifact

When the API requires OpenAPI, use `@nestjs/swagger` decorators and bootstrap configuration to describe the same request, response, status, authentication, and parameter contract that the controller implements. The generated OpenAPI document is a contract artifact: review it, publish or version it according to repository policy, and treat breaking changes to it as API changes.

Document response DTOs rather than TypeORM entities. Ensure every documented status and response body is reachable from the implementation or explicitly represents an error filter's contract. Keep examples synthetic and free of credentials or internal identifiers. If the project uses a schema-first or another documentation approach, follow that established convention instead of generating a second competing contract.

## Decision Points

Resolve these choices from the target repository's existing API contract before adding a new endpoint. Do not introduce a TSH-wide default by copying one option into every service.

| Decision | Acceptable choices | Selection consequence |
| --- | --- | --- |
| URL prefix and versioning | No version prefix, URI versioning, header/media-type versioning, or the established gateway prefix | Apply one coherent strategy to routes, `Location` headers, OpenAPI servers/paths, and deprecation policy. Do not mix strategies across features without an explicit boundary. |
| OpenAPI exposure | No public document, internal-only document, checked-in/generated artifact, or published document | Decide who can access the document, how it is authenticated, whether it is generated in CI, and how breaking changes are reviewed. `@nestjs/swagger` is required when this is the selected Nest integration. |
| Pagination and filter envelope | The established collection envelope, cursor-based results, offset/page results, or an intentionally unpaginated bounded collection | Define metadata, stable ordering, limits, and filter encoding consistently. Generic pagination and data-grid conventions are outside this reference; follow the project's established envelope. |

Once selected, apply the decision consistently to new routes and response DTOs. Record exceptions at the owning API boundary rather than silently creating a second contract.

## Review Checklist

- [ ] The controller maps HTTP input and output only and dispatches through `CommandBus.execute()` or `QueryBus.execute()`.
- [ ] No controller contains business orchestration or calls a repository, handler, or peer-feature internal.
- [ ] Request and response DTOs are feature-owned under `api/`; no response is a TypeORM entity.
- [ ] Create semantics include `201 Created` and a canonical `Location` header where a resource is created.
- [ ] `PUT` and `DELETE` behavior is safe under repetition and documented for not-found/retry cases.
- [ ] Any Express `Request`/`Response` use is a concrete controller-only exception.
- [ ] Middleware, guards, interceptors, pipes, and filters each own the concern assigned to them.
- [ ] OpenAPI metadata, generated document, and implementation agree when OpenAPI is required.
- [ ] URL versioning, OpenAPI exposure, and collection pagination/filtering follow the repository's selected decision points.

## Official References

- [NestJS controllers](https://docs.nestjs.com/controllers)
- [NestJS CQRS recipe](https://docs.nestjs.com/recipes/cqrs)
- [NestJS request lifecycle](https://docs.nestjs.com/faq/request-lifecycle)
- [NestJS validation](https://docs.nestjs.com/techniques/validation)
- [NestJS OpenAPI introduction](https://docs.nestjs.com/openapi/introduction)
- [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
