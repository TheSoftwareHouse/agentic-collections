# NestJS Validation, Errors, and Serialization

Use this reference when defining DTO validation, HTTP error behavior, or response serialization for a NestJS 11 API.

## Table of Contents

- [NestJS Validation, Errors, and Serialization](#nestjs-validation-errors-and-serialization)
  - [Table of Contents](#table-of-contents)
  - [Validation pipeline](#validation-pipeline)
    - [Nested objects and arrays](#nested-objects-and-arrays)
  - [Choosing one stack](#choosing-one-stack)
  - [Safe error contract](#safe-error-contract)
  - [Exception filter and domain-exception mapping](#exception-filter-and-domain-exception-mapping)
  - [Response serialization](#response-serialization)
  - [One validation-failure shape](#one-validation-failure-shape)
  - [Decision Points](#decision-points)
  - [Official documentation](#official-documentation)

## Validation pipeline

Install and configure one global validation boundary at bootstrap. The pipe is a security boundary, not merely a convenience for controller method signatures.

```ts
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }),
);
```

- `whitelist: true` removes properties that have no validation metadata.
- `forbidNonWhitelisted: true` rejects, rather than silently accepts, unexpected properties. Use both settings as the mass-assignment defense; do not rely on DTO typing alone.
- `transform: true` enables the selected request transformation behavior. Document which primitive conversions are expected and do not treat transformation as authorization or business validation.
- Keep the global policy consistent. A route-specific pipe may tighten behavior for a concrete boundary, but it must not create a second undocumented error shape or bypass the global mass-assignment defense.

### Nested objects and arrays

Nested and array values need explicit metadata in the chosen DTO/schema stack. A TypeScript interface or a reflected array type does not, by itself, validate each element.

For a class-validator/class-transformer project, nested class values use nested-type metadata and arrays validate each element. The representative shape is:

```ts
class AddressDto {
  @IsString()
  street!: string;
}

class CreateUserDto {
  @ValidateNested()
  @Type(() => AddressDto)
  address!: AddressDto;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => AddressDto)
  addresses!: AddressDto[];
}
```

The exact decorators depend on the selected stack, but the invariant does not: validate the object shape recursively, validate every array element, and test malformed nested values. Do not assume that `@IsArray()` validates the contents of an array.

Validation should complete before application handlers run. Commands, queries, and domain objects may enforce business invariants as a second boundary, but they must not depend on controller-only validation having happened.

## Choosing one stack

A project MUST choose exactly one validation and serialization stack for each API boundary and apply it consistently to request DTOs, response DTOs, transformation, and validation errors. Discover the target repository's established convention first; where no convention exists, record the choice before adding DTOs.

Acceptable examples include:

| Stack | Use consistently for | Trade-off |
| --- | --- | --- |
| `class-validator` + `class-transformer` with Nest pipes/interceptors | Decorator-based DTOs, nested metadata, transformation, and class-based response shaping | Integrates naturally with Nest, but decorator metadata and nested-type configuration require care |
| Zod | Acceptable schema-based validation and serialization stack; see [`nestjs-validation-with-zod.md`](./nestjs-validation-with-zod.md) for Zod-specific adoption policy and idioms | Selection remains subject to the repository's established convention and boundary contract |

NEVER mix these stacks across the same DTO boundary. Mixing a class-validator pipe with a Zod schema, or validating a request with one stack and serializing its response with another, causes duplicated or divergent rules: one layer can strip or transform a value while the other reports a different shape, and error details/status mapping become inconsistent. It can also leave a route without the selected stack's whitelist or schema guarantees. A stack switch is a deliberate boundary migration, not a per-controller shortcut.

The selected stack must define:

1. How request bodies, parameters, and query values are parsed and transformed.
2. How nested objects and every array element are validated.
3. How response DTOs exclude fields and represent dates and `null`.
4. How native validation failures are translated into the canonical error envelope.
5. Which pipe/interceptor/filter owns the integration, so the same DTO is not processed twice.

## Safe error contract

Expose a stable, machine-readable contract rather than framework exception internals. The exact envelope remains project-specific, but every error response MUST provide these safe fields:

| Field | Requirement |
| --- | --- |
| `code` | Stable machine-readable error code suitable for client branching; do not use a transient exception class name |
| `message` | Human-safe summary that explains the outcome without operational or persistence details |
| `correlationId` | Request or trace correlation identifier that support tooling can use to locate server-side logs |
| `details` | Optional bounded, field-level information for actionable client correction; never include raw exception objects |

The HTTP status, content type, and whether `details` is present are part of the documented API contract. The response MUST NOT contain stack traces, internal identifiers, SQL or ORM error text, database constraint names, file paths, secret material, or arbitrary exception messages. Log diagnostic context server-side under the correlation ID, subject to redaction; do not copy it into the client response.

Validation failures should identify invalid fields with safe paths and stable reason codes, such as `required`, `invalid_format`, or `unexpected_property`. Do not expose decorator names, schema internals, or a raw `ValidationError` tree as the public contract.

## Exception filter and domain-exception mapping

Keep exception translation in one application-wide place, normally a global exception filter (or the project's single equivalent). The filter is responsible for:

- mapping known domain exceptions to an allow-listed HTTP status and machine code;
- mapping validation exceptions to the canonical validation-failure shape;
- mapping framework and unknown exceptions to a generic safe response;
- attaching or preserving the correlation ID;
- logging the full diagnostic context once, with sensitive values redacted.

Domain exceptions should carry stable semantic information, not HTTP response objects. The filter owns the domain-to-HTTP mapping so controllers and handlers do not each invent status codes, envelopes, or message wording. A domain exception that has no explicit mapping falls into the safe unknown-error path; it must not leak its constructor arguments or persistence cause.

Do not scatter `try/catch` response shaping through controllers, handlers, repositories, and middleware. Local catches are appropriate only when a layer can recover or translate a dependency for its own domain; the final public mapping still belongs to the one filter boundary.

## Response serialization

Return explicit response DTOs or contract objects from controllers. A command or query handler may return an application result, but a controller-facing mapper must choose the public fields and shape.

- Sensitive fields such as passwords, credential material, reset tokens, authorization data, and private security metadata are excluded by construction. Do not rely on a serializer's default field discovery to protect them.
- NEVER serialize a TypeORM entity directly as an HTTP response. Entities contain persistence shape, relation behavior, and fields whose exposure can change when the schema changes. Map entities to response DTOs, including nested DTOs where needed.
- Define date behavior explicitly: choose the documented wire representation (commonly an ISO 8601 string) and apply it consistently to every response DTO. Do not let driver-specific date objects or locale formatting escape the boundary.
- Define `null` behavior explicitly: preserve meaningful nullable fields as `null`, or omit them only when the API contract says so. Do not mix omission and `null` based on incidental serializer behavior.
- Bound collection and nested response sizes. Do not return an unbounded persistence graph or lazy relation traversal from a command/query result.
- Keep serialization after application logic and before the response leaves the transport boundary. It must not alter domain state or be used to conceal an authorization decision.

A response mapper is also the right place to normalize enums, IDs, dates, and nullable values. Its output should be stable even if the owning entity gains a column or relation.

## One validation-failure shape

All validation failures MUST have one public shape, regardless of where rejection occurs:

- global request-pipe validation;
- parameter or query validation;
- nested-object or array-element validation;
- a schema parser or class-based DTO validator;
- an application-layer input guard that rejects an invalid command boundary.

The filter or canonical adapter normalizes each source into the same status policy, `code`, human-safe `message`, `correlationId`, and bounded field `details`. The `details` paths should use the public request contract, not a database column, entity property, or internal command name.

A typical abstract contract is:

```json
{
  "code": "VALIDATION_FAILED",
  "message": "One or more fields are invalid.",
  "correlationId": "request-correlation-id",
  "details": [
    { "path": "email", "reason": "invalid_format" }
  ]
}
```

The example is illustrative, not a TSH-wide envelope decision. Do not add a second validation response for a different controller, DTO library, or exception source. Contract tests should assert the shape and leakage exclusions without coupling clients to framework-specific wording.

## Decision Points

Resolve these choices from the target repository before implementation and record them at the owning boundary:

| Decision | Options to compare | Selection rule |
| --- | --- | --- |
| Validation/serialization stack | `class-validator` + `class-transformer`; Zod with the repository's Nest integration; another established local stack | Pick exactly one stack per API boundary and use it for parsing, validation, transformation, response shaping, and native-error normalization. Do not mix stacks across one DTO boundary. See [`nestjs-validation-with-zod.md`](./nestjs-validation-with-zod.md) for Zod-specific adoption and idiom rules. |
| Canonical error envelope | Existing repository contract; a versioned envelope containing the required safe fields; a documented compatibility wrapper | Preserve the established public contract. If none exists, choose and document one envelope with stable code, human-safe message, correlation ID, and bounded details, while never exposing stacks, internal IDs, or ORM text. |

Do not treat either decision as a reason to weaken the mandatory security rules or to return different validation shapes from different layers.

## Official documentation

- [NestJS validation](https://docs.nestjs.com/techniques/validation) — global pipes, transformation, and validation-pipe behavior.
- [NestJS exception filters](https://docs.nestjs.com/exception-filters) — exception-filter placement and response translation.
- [NestJS serialization](https://docs.nestjs.com/techniques/serialization) — response serialization and interceptor integration.
- [class-validator nested objects](https://github.com/typestack/class-validator#handling-nested-objects) — nested validation metadata.
- [class-transformer type metadata](https://github.com/typestack/class-transformer#working-with-nested-objects) — nested transformation metadata.
