# Data Modeling Review Checklist

Use this checklist to review Python 3.12+, Pydantic v2, dataclass, and SQLAlchemy 2.0 data-modeling changes.

## 1. Architectural Boundaries and Mapping

- [ ] Pydantic `BaseModel` is used at system boundaries such as API payloads, database schema serialization, and configuration.
- [ ] When a domain layer exists, `@dataclass` is used for internal domain entities where domain behavior and invariants belong.
- [ ] Domain dataclasses are not created merely to mirror a Pydantic model's fields one-to-one; a trivial mapping function with no added behavior, invariants, or aggregation is a signal to reuse the Pydantic model directly instead.
- [ ] ORM models remain persistence models, not domain models.
- [ ] ORM objects are mapped explicitly to domain dataclasses at repository boundaries.
- [ ] Related returns use named value objects or result types instead of large tuples.
- [ ] Redundant DTOs are avoided unless a real architectural boundary requires them.
- [ ] Dependency-injected stateless services prefer `@dataclass(frozen=True)` without `slots=True`.
- [ ] `frozen=True` is described as shallow immutability: it prevents attribute reassignment and signals immutable intent, but does not deeply freeze dependencies.
- [ ] Standard classes are used only when a service explicitly requires state accumulation.

## 2. Modern Pydantic v2 Syntax

- [ ] No Pydantic v1 `orm_mode`, `.from_orm()`, `json_encoders`, or `.copy(` on Pydantic models remains; use `model_copy(update={...})`.
- [ ] Reusable constraints and field metadata use `Annotated` where that improves clarity.
- [ ] Trivial field configuration uses readable `Field()` defaults when appropriate.
- [ ] `EmailStr` and `HttpUrl` are used where their validation is required.
- [ ] `UUID` is identified as the standard-library type, not as a Pydantic-specific type.
- [ ] Ensure the `email-validator` dependency is available when using `EmailStr`.
- [ ] `Decimal`, not `float`, is used for money and financial data.
- [ ] Timezone-aware datetimes are used internally; UTC is preferred for storage and computation, and presentation layers can localize.
- [ ] `pydantic-settings` is used for application configuration.
- [ ] `SecretStr` is used for secrets.
- [ ] Settings use an appropriate `env_prefix`.
- [ ] `extra="ignore"` is not chosen blindly; use `"forbid"` for strict configuration contracts and `"ignore"` when forward compatibility is desired.
- [ ] Reused settings are cached with `functools.lru_cache` where appropriate.

## 3. Complex Validation, Aliasing, and Adapters

- [ ] `@field_validator` handles single-field logic.
- [ ] `@model_validator` is reserved for cross-field dependencies.
- [ ] `alias_generator`, `validation_alias`, and `serialization_alias` map wire naming conventions without polluting Python field names.
- [ ] Pydantic v2 generic models are used to avoid duplicating response or container shapes.
- [ ] `@computed_field` is used for dynamic properties that should participate in serialization.
- [ ] `TypeAdapter` validates standalone types and collections outside a `BaseModel`.
- [ ] `strict=True` is applied selectively to contracts where coercion must be forbidden.
- [ ] Blanket strict mode is avoided because it can reject harmless or desirable transport-edge coercions such as `"123"` to `int`.
- [ ] Discriminated Unions are used for polymorphic nested models, and `SerializeAsAny` is used when composing with base classes to ensure subclass fields are serialized.

## 4. Serialization and File I/O

- [ ] `model_validate_json()` is used when validating complete Pydantic models from JSON.
- [ ] `model_dump_json()` is used when serializing complete Pydantic models to JSON.
- [ ] The standard `json` module is reserved for arbitrary or mixed JSON structures.
- [ ] YAML output uses `model_dump(mode="json")` so it contains basic primitives rather than Pydantic-specific tags.
- [ ] YAML loading and dumping uses a suitable YAML library with explicit file encoding.
- [ ] Validation errors use `e.errors(include_url=False)` for user-facing reporting.
- [ ] Nested error locations are converted to useful dot-notation and index paths such as `users[0].email`.
- [ ] File validation failures identify the relevant field path without leaking unnecessary internal details.

## 5. SQLModel and SQLAlchemy 2.0 Bridging

- [ ] Create, Read, and Update payloads have distinct schemas.
- [ ] Read schemas set `model_config = ConfigDict(from_attributes=True)` when validating ORM instances.
- [ ] Single ORM instances are bridged with `ReadSchema.model_validate(db_instance)`.
- [ ] ORM collections are validated with `TypeAdapter(list[ReadSchema]).validate_python(db_instances)`.
- [ ] Relationships required during serialization are eagerly loaded in the SQLAlchemy query.
- [ ] `selectinload()`, `joinedload()`, or `contains_eager()` is chosen according to the query shape.
- [ ] Serialization does not trigger an N+1 query pattern.
- [ ] Persistence concerns are not silently introduced into domain models.
- [ ] SQLAlchemy `Session` objects are not exposed outside persistence/application layers or injected into domain services.
- [ ] SQLModel base classes (`table=False`) are used to share fields with persistence models (`table=True`) and API schemas without duplication.
- [ ] SQLModel auto-incrementing primary keys correctly use `id: int | None = Field(default=None, primary_key=True)` to satisfy Pydantic constructors.
- [ ] `Literal` combined with a `CheckConstraint` is preferred over Python `Enum`s in SQLModel models to avoid database migration complexity.
- [ ] `session.exec()` is used for SQLModel queries instead of SQLAlchemy's `session.execute()`.

## 6. Performance and Constraints

- [ ] `ConfigDict(frozen=True)` or `@dataclass(frozen=True)` is used for data that should not change after instantiation.
- [ ] `slots=True` is used for heavily instantiated internal models when memory reduction is useful.
- [ ] Slots are avoided where dynamic attributes, multiple inheritance, mocking, or dependency injection requires a normal instance dictionary.
- [ ] Strict mode is selective and tied to a specific contract requirement.
- [ ] `model_construct()` is used only with data from a provably trusted source.
- [ ] Reviewers recognize `model_construct()` as a validation bypass that skips all validators and conversions.
- [ ] `model_construct()` is not justified merely as a speed optimization; performance benefit is secondary.
- [ ] Frozen models are not assumed to deeply freeze mutable referenced objects or dependencies.
- [ ] Model choices preserve the required validation, serialization, memory, and query behavior of the consuming boundary.
