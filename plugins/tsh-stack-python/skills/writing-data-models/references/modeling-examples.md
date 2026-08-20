# Data Modeling Examples: Boundaries, Types, and Validation

Compact Python 3.12 and Pydantic v2 examples for the boundary, typing, and
validation rule groups. Serialization, persistence, and performance examples
live in [`persistence-examples.md`](./persistence-examples.md).

## Contents

- [1. Boundaries and Mapping](#1-boundaries-and-mapping)
- [2. Types and Configuration](#2-types-and-configuration)
- [3. Validation, Aliasing, and Adapters](#3-validation-aliasing-and-adapters)

## 1. Boundaries and Mapping

Use Pydantic at the edge. When a domain layer exists, reserve a dataclass domain model for cases where it adds real behavior, invariants, or aggregation beyond the edge model — do not mirror a Pydantic model's fields into an identical dataclass just so it "is a dataclass".

```python
from dataclasses import dataclass

from pydantic import BaseModel


# Antipattern: identical dataclass mirror, no added behavior or invariants
class UserPayload(BaseModel):
    user_id: int
    display_name: str


@dataclass(frozen=True)
class User:                # adds nothing over UserPayload
    user_id: int
    display_name: str


def to_domain(payload: UserPayload) -> User:
    return User(user_id=payload.user_id, display_name=payload.display_name)
```

If no downstream needs domain behavior, use `UserPayload` directly instead of introducing a parallel type and a trivial mapping function.

```python
def greet(user: UserPayload) -> str:
    return f"Hello, {user.display_name}!"
```

A dataclass domain model earns its place when it adds behavior, invariants, or aggregates data the edge model doesn't have.

```python
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class OrderSummary:
    order: Order
    customer: Customer
    total_with_tax: Decimal

    @classmethod
    def build(cls, order: Order, customer: Customer, tax_rate: Decimal) -> Self:
        return cls(order=order, customer=customer, total_with_tax=order.total * (1 + tax_rate))
```

`OrderSummary` combines data from multiple sources and computes a derived value — that's genuine domain behavior, unlike a field-for-field copy of a single edge model.

Keep ORM persistence models separate from domain entities and group related results.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Page[T]:
    items: tuple[T, ...]
    total: int


@dataclass(frozen=True)
class NotificationService:
    sender: object
```

`frozen=True` prevents attribute reassignment and communicates shallow immutable intent; it does not deeply freeze referenced dependencies.

Prefer named result types over bare tuples.

```python
from decimal import Decimal


@dataclass(frozen=True)
class UserStatistics:
    total: int
    average: Decimal


statistics = UserStatistics(total=total, average=average)
```

Prefer `UserStatistics(total=..., average=...)` over returning a bare tuple such as `(total, average)`.

Use a frozen Pydantic model when the boundary model itself must be immutable.

```python
from pydantic import BaseModel, ConfigDict


class ImmutablePayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: int
```

## 2. Types and Configuration

Use reusable `Annotated` constraints, domain-appropriate scalar types, and timezone-aware datetimes internally; prefer UTC for storage and computation, while presentation layers can localize.

```python
from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl

PositiveAmount = Annotated[Decimal, Field(gt=Decimal("0"))]


class Account(BaseModel):
    account_id: UUID
    email: EmailStr
    homepage: HttpUrl
    balance: PositiveAmount
    created_at: datetime
```

`UUID` is a standard-library type. `EmailStr` and `HttpUrl` are Pydantic types; `EmailStr` requires the optional `email-validator` dependency.

Use `pydantic-settings` for configuration, `SecretStr` for secrets, and cache reused settings.

```python
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        extra="ignore",
        frozen=True,
    )

    database_url: str
    api_key: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Do not blindly choose `extra="ignore"`; use `"forbid"` for strict configuration contracts and `"ignore"` when forward compatibility is desired.

## 3. Validation, Aliasing, and Adapters

Use field validators for single-field rules and model validators for cross-field dependencies.

```python
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic import field_validator


class PasswordChange(BaseModel):
    current: str
    replacement: str = Field(min_length=12)

    @field_validator("replacement")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("replacement cannot be blank")
        return value

    @model_validator(mode="after")
    def differs_from_current(self) -> "PasswordChange":
        if self.current == self.replacement:
            raise ValueError("replacement must differ")
        return self
```

Map snake_case fields to camelCase at the JSON boundary without polluting Python names.

```python
from pydantic import AliasGenerator
from pydantic.alias_generators import to_camel


class UserResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )

    user_id: int
    display_name: str
```

Use generic responses, computed fields, and adapters for standalone collections.

```python
from pydantic import BaseModel, computed_field, TypeAdapter


class Page[T](BaseModel):
    items: list[T]
    total: int


class Product(BaseModel):
    name: str
    price: Decimal

    @computed_field
    @property
    def label(self) -> str:
        return f"{self.name}: {self.price}"


emails = TypeAdapter(list[EmailStr]).validate_python(["a@example.com"])
```
