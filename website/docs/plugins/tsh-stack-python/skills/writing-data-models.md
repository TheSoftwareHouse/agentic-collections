---
title: Writing Data Models
sidebar_label: writing-data-models
sidebar_position: 2
description: Governs implementation and review of Python data modelling with Pydantic v2, dataclasses, SQLModel, SQLAlchemy 2.0 bridging, serialization, and immutability and performance constraints.
sources:
  - plugins/tsh-stack-python/skills/writing-data-models/
sources_hash: "dddae18246537617ff2f5a14eebf3d4beaf46f0288d0276c45079385defa463a"
---

# Writing Data Models

**Plugin:** [`tsh-stack-python`](/docs/plugins/tsh-stack-python/)  
**Invoke:** `/tsh-stack-python:writing-data-models`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`writing-modern-python`](/docs/plugins/tsh-stack-python/skills/writing-modern-python) delegates dataclass, Pydantic, ORM and serialization decisions to it. The `reviewing-code` skill in `tsh-product-engineering` loads whichever stack skill is available in the session and names a Python stack skill among its examples, but names no plugin.

Implements or reviews Python data modelling, validation, serialization and persistence mappings, targeting Python 3.12 or newer, Pydantic v2, SQLModel and SQLAlchemy 2.0. The skill owns data modelling, validation, serialization and persistence mapping only. Cross-cutting Python concerns (typing, control flow, asyncio, exceptions, logging and tooling) go to [`writing-modern-python`](/docs/plugins/tsh-stack-python/skills/writing-modern-python).

Use it when defining or reviewing a Pydantic `BaseModel`, a domain dataclass, a SQLModel table or schema, `pydantic-settings` configuration, field or model validators, aliasing between wire and Python names, `TypeAdapter` usage, or a bridge between raw SQLAlchemy ORM objects and Pydantic schemas.

Local patterns outrank the skill's defaults. It applies where the repository is silent and records a deliberate deviation instead of silently mixing conventions.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Boundaries and mapping** | Pydantic `BaseModel` at system boundaries, and `@dataclass` for internal domain models that add real behavior, invariants or aggregation. A dataclass is never a field-for-field mirror of a Pydantic model. ORM models are persistence models, mapped explicitly at repository boundaries. Named result types over bare tuples |
| **Modern Pydantic v2 syntax** | `model_config`, `model_validate()` and `model_copy(update={...})` instead of `orm_mode`, `.from_orm()`, `json_encoders` and `.copy(`. `Annotated` constraints, `EmailStr` and `HttpUrl`, `Decimal` for money, timezone-aware datetimes with UTC for storage and computation, and `pydantic-settings` with `SecretStr`, an `env_prefix` and `functools.lru_cache` |
| **Validation, aliasing and adapters** | `@field_validator` for single-field rules, `@model_validator` for cross-field rules, alias generators for wire naming, discriminated unions for polymorphic nested models, `TypeAdapter` for standalone types, and `strict=True` applied selectively |
| **Serialization and file I/O** | `model_validate_json()` and `model_dump_json()` for complete models, `model_dump(mode="json")` before a YAML writer, and `e.errors(include_url=False)` converted to dot-notation paths for user-facing validation errors |
| **SQLModel and SQLAlchemy 2.0 bridging** | Shared base classes (`table=False`) with persistence models (`table=True`), distinct Create, Read and Update schemas, the exact primary-key form `id: int \| None = Field(default=None, primary_key=True)`, `session.exec(select(Model)).all()`, `from_attributes=True` for ORM instances, and eager loading to avoid N+1 queries |
| **Performance and constraints** | `frozen=True` is shallow immutability only, `slots=True` only where it does not fight DI or mocking, selective `strict=True`, and `model_construct()` reserved for provably trusted data because it bypasses every validator |

## How it works

1. **Establish boundaries.** Decide what is a Pydantic edge model, what (if anything) is a domain dataclass, and what is a persistence model. A domain dataclass earns its place only if it adds behavior, invariants or aggregation beyond the edge model.
2. **Apply modern Pydantic v2 syntax.**
3. **Design validation, aliasing and adapters.**
4. **Handle serialization and file I/O.**
5. **Architect SQLModel and SQLAlchemy persistence explicitly**, following the rules below for primary keys, querying and eager loading.
6. **Apply performance and constraints deliberately**: immutability, slots, selective strict mode, and `model_construct()` for trusted data only.
7. Before finishing a review, work through the review checklist in full.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Use Pydantic `BaseModel` at system boundaries, and reserve `@dataclass` for internal domain models that add real behavior |
| MUST | Treat ORM models as persistence models and map them explicitly to domain types at repository boundaries |
| NEVER | Use Pydantic v1 syntax: `orm_mode`, `.from_orm()`, `json_encoders` or `.copy(` |
| MUST | Use `Decimal`, not `float`, for money, and timezone-aware datetimes internally |
| NEVER | Apply blanket `strict=True` |
| MUST | Give SQLModel auto-incrementing primary keys the form `id: int \| None = Field(default=None, primary_key=True)` |
| NEVER | Mix SQLAlchemy `Mapped`, `mapped_column` or `relationship` into a SQLModel class |
| MUST | Query SQLModel objects with `session.exec(select(Model)).all()` and not `session.execute(...)` |
| NEVER | Expose a `Session` outside the persistence or application layer, or treat `model_construct()` as a speed-up for unvalidated data |
| MUST | Eagerly load relationships a serialization path traverses, and treat `frozen=True` as shallow immutability only |

## References

| Reference | Load when |
| :-- | :-- |
| Review checklist | Reviewing a data-modeling change, or before finishing an implementation. It has six groups: boundaries and mapping, modern Pydantic v2 syntax, validation and aliasing and adapters, serialization and file I/O, SQLModel and SQLAlchemy bridging, and performance and constraints |
| Modeling examples | Writing new model code, or when a boundary, typing or validation rule needs a concrete pattern |
| Persistence examples | Writing new model code, or when a serialization, persistence or performance rule needs a concrete pattern |

## Related skills

- [`writing-modern-python`](/docs/plugins/tsh-stack-python/skills/writing-modern-python) ships in the same plugin and owns typing, control flow, asyncio, exceptions, logging and tooling. Use it alongside this skill for concerns outside data modelling.
- Pandas and Pandera guidance is not covered by this plugin yet. The skill is scoped to domain, transport and persistence models, not DataFrame manipulation or DataFrame validation.

## Source

[`plugins/tsh-stack-python/skills/writing-data-models/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-python/skills/writing-data-models/SKILL.md)
