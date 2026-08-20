---
name: writing-data-models
description: "Governs implementation and review of Python data modeling with Pydantic v2, dataclasses, SQLModel, SQLAlchemy 2.0 bridging, serialization, and immutability and performance constraints. Use when working with Pydantic BaseModel, dataclass, SQLModel (table=True/False), domain boundaries, pydantic-settings, TypeAdapter, or model_construct."
when_to_use: "Trigger on: defining or reviewing a Pydantic BaseModel, a domain dataclass, a SQLModel table or schema, pydantic-settings configuration, field or model validators, aliasing between wire and Python names, TypeAdapter usage, or a bridge between raw SQLAlchemy ORM objects and Pydantic schemas."
---

# Writing data models

Implement or review Python data modeling, validation, serialization, and
persistence mappings targeting Python >= 3.12, Pydantic v2, SQLModel, and
SQLAlchemy 2.0.

## Applicability and Precedence

Read the repository's own conventions first — local patterns outrank this
skill's defaults; apply this guidance where the repo is silent, and record a
deliberate deviation rather than silently mixing conventions.

Delegate cross-cutting Python concerns — typing, control flow, asyncio,
exceptions, logging, and tooling — to
[`writing-modern-python`](../writing-modern-python/SKILL.md), which ships in
this same plugin. This skill owns only data modeling, validation,
serialization, and persistence mapping.

## Non-negotiable Rules

| Severity | Rule |
| :-- | :-- |
| MUST | Use Pydantic `BaseModel` at system boundaries (API payloads, config, serialization). Reserve `@dataclass` for internal domain models that add real behavior, invariants, or aggregation — never as a field-for-field mirror of an existing Pydantic model. |
| MUST | Treat ORM models as persistence models, not domain models; map them explicitly to domain types at repository boundaries. |
| NEVER | Use Pydantic v1 syntax — `orm_mode`, `.from_orm()`, `json_encoders`, `.copy(`. Use `model_config`, `model_validate()`, and `model_copy(update={...})`. |
| MUST | Use `Decimal`, not `float`, for money. Use timezone-aware datetimes internally, UTC for storage and computation, and localize only at presentation. |
| NEVER | Apply blanket `strict=True`. Apply it selectively to contracts that must forbid coercion; transport edges often need harmless coercions such as `"123"` to `int`. |
| MUST | Give SQLModel auto-incrementing primary keys the exact form `id: int \| None = Field(default=None, primary_key=True)` to satisfy the Pydantic constructor. |
| NEVER | Mix SQLAlchemy `Mapped`, `mapped_column`, or `relationship` into a SQLModel class. SQLModel uses plain type hints, `sqlmodel.Field`, and `sqlmodel.Relationship` only. |
| MUST | Query SQLModel objects with `session.exec(select(Model)).all()`, not SQLAlchemy's `session.execute(select(Model)).scalars().all()`. |
| NEVER | Expose a SQLAlchemy/SQLModel `Session` outside the persistence or application layer — never inject one into a domain service. |
| MUST | Eagerly load relationships a serialization path traverses (`selectinload()`, `joinedload()`, or `contains_eager()`); an N+1 query is a defect, not a style preference. |
| NEVER | Treat `model_construct()` as a performance optimization on untrusted or unvalidated data. It bypasses every validator and conversion; use it only for provably trusted data. |
| MUST | Treat `frozen=True` (`ConfigDict` or `@dataclass`) as shallow immutability only — it blocks attribute reassignment, not mutation of referenced objects. |

## Reference Loading

| Reference | Load when | Covers |
| :-- | :-- | :-- |
| [Review checklist](./references/checklist.md) | Reviewing a data-modeling change, or before finishing an implementation | The full six-group checklist: boundaries and mapping, modern Pydantic v2 syntax, validation/aliasing/adapters, serialization and file I/O, SQLModel/SQLAlchemy bridging, performance and constraints |
| [Modeling examples](./references/modeling-examples.md) | Writing new model code, or when a boundary/typing/validation rule above needs a concrete pattern | Compact Python 3.12/Pydantic v2 code for boundaries and mapping, types and configuration, and validation/aliasing/adapters |
| [Persistence examples](./references/persistence-examples.md) | Writing new model code, or when a serialization/persistence/performance rule above needs a concrete pattern | Compact Python 3.12/Pydantic v2 code for serialization and file I/O, SQLModel/SQLAlchemy bridging, and performance and constraints |

## Procedure

1. **Establish boundaries.** Decide what is a Pydantic edge model, what (if
   anything) is a domain dataclass, and what is a persistence model. A domain
   dataclass earns its place only if it adds behavior, invariants, or
   aggregation beyond the edge model.
2. **Apply modern Pydantic v2 syntax.** `Annotated` constraints, stdlib
   `UUID`, `EmailStr`/`HttpUrl`, `Decimal` for money, timezone-aware
   datetimes, and `pydantic-settings` with `SecretStr` and an explicit
   `env_prefix`, cached with `functools.lru_cache`.
3. **Design validation, aliasing, and adapters.** `@field_validator` for
   single-field rules, `@model_validator` for cross-field rules, alias
   generators for wire-naming, Discriminated Unions for polymorphic nested
   models, and `TypeAdapter` for standalone types.
4. **Handle serialization and file I/O.** `model_validate_json()` /
   `model_dump_json()` for complete models, `model_dump(mode="json")` before
   handing data to a YAML writer, and `e.errors(include_url=False)` converted
   to dot-notation paths for user-facing validation errors.
5. **Architect SQLModel/SQLAlchemy persistence explicitly**, following the
   Non-negotiable Rules above for primary keys, querying, and eager loading.
6. **Apply performance and constraints deliberately** — immutability,
   `slots=True` only where it doesn't fight DI or mocking, selective
   `strict=True`, and `model_construct()` reserved for trusted data.
7. Before finishing a review, work through
   [`checklist.md`](./references/checklist.md) in full.

## Related Skills

- [`writing-modern-python`](../writing-modern-python/SKILL.md) — ships in
  this same plugin; owns typing, control flow, asyncio, exceptions, logging,
  and tooling. Use it alongside this skill for concerns outside data
  modeling.
- Pandas and Pandera guidance is not covered by this plugin yet — this skill
  is scoped to domain, transport, and persistence models, not DataFrame
  manipulation or DataFrame validation.
