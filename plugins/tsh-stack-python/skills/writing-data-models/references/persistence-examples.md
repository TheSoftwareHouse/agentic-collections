# Data Modeling Examples: Serialization, Persistence, and Performance

Compact Python 3.12 and Pydantic v2 examples for the serialization, SQL
bridging, and performance rule groups. Boundary, typing, and validation
examples live in [`modeling-examples.md`](./modeling-examples.md).

## Contents

- [4. Serialization and File I/O](#4-serialization-and-file-io)
- [5. SQLModel and SQLAlchemy Bridging](#5-sqlmodel-and-sqlalchemy-bridging)
- [6. Performance and Constraints](#6-performance-and-constraints)

## 4. Serialization and File I/O

Use Pydantic’s JSON methods for complete models and JSON-mode data for YAML.

```python
from pydantic import BaseModel, ValidationError


class ImportBatch(BaseModel):
    users: list[Account]


batch = ImportBatch.model_validate_json(raw_json)
json_text = batch.model_dump_json()
```

```python
import yaml


with open("config.yaml", encoding="utf-8") as stream:
    config = ImportBatch.model_validate(yaml.safe_load(stream))

with open("config.yaml", "w", encoding="utf-8") as stream:
    yaml.safe_dump(config.model_dump(mode="json"), stream)
```

Use the standard `json` module for arbitrary or mixed JSON structures, not complete Pydantic models. Convert validation errors to useful file paths.

```python
def validation_paths(error: ValidationError) -> list[str]:
    paths: list[str] = []
    for item in error.errors(include_url=False):
        path = ""
        for part in item["loc"]:
            path += f"[{part}]" if isinstance(part, int) else ("." if path else "") + str(part)
        paths.append(path)
    return paths
```

## 5. SQLModel and SQLAlchemy Bridging

Prefer SQLModel to share fields between database models (`table=True`) and API schemas (`table=False`). Keep Create, Read, and Update schemas distinct.

```python
from typing import Literal
from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field

# 1. Shared Base (table=False by default)
class UserBase(SQLModel):
    email: str
    role: Literal["admin", "user"]

# 2. Persistence Model
class User(UserBase, table=True):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin', 'user')"),)

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

# 3. Read Schema
class UserRead(UserBase):
    id: int
```

Auto-incrementing primary keys in SQLModel must use id: int | None = Field(default=None, primary_key=True) to satisfy Pydantic constructors. Use Literal with a CheckConstraint instead of Python Enums to avoid database migration complexity.

When querying SQLModel objects, use session.exec() instead of SQLAlchemy's session.execute().
```python
from sqlmodel import Session, select

def get_users(session: Session) -> list[User]:
    # SQLModel uses .exec() directly
    return session.exec(select(User)).all()
```

When bridging raw SQLAlchemy 2.0 ORM objects (without SQLModel), use from_attributes=True on the Pydantic schema and eagerly load serialized relationships to avoid N+1 queries.
```python
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class ProjectOrm(Base):
    __tablename__ = "projects"

    project_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))


class UserOrm(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    projects: Mapped[list[ProjectOrm]] = relationship()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


# Eagerly load the relationship before serialization
statement = select(UserOrm).options(selectinload(UserOrm.projects))
```

Avoid exposing Session objects outside persistence/application layers.
```python
from dataclasses import dataclass
from sqlalchemy.orm import Session

# Avoid: persistence concerns leak into the domain service.
@dataclass(frozen=True)
class DomainUserService:
    session: Session
```

## 6. Performance and Constraints

Freeze data that should not change and use slots for heavily instantiated internal models.

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Coordinate:
    latitude: float
    longitude: float
```

Avoid `slots=True` when dynamic attributes, multiple inheritance, or mocking and dependency injection require a normal instance dictionary.

Apply strict mode selectively to contracts where coercion is forbidden.

```python
from pydantic import BaseModel, ConfigDict


class InternalIdentifier(BaseModel):
    model_config = ConfigDict(strict=True)

    value: int
```

Do not apply blanket strictness when transport contracts intentionally accept harmless coercions such as `"123"` to `int`.

Use `model_copy(update={...})` instead of Pydantic v1's `model.copy(update={...})`.

```python
updated = payload.model_copy(update={"value": 456})
```

Use `model_construct()` only for provably trusted data that has already passed validation.

```python
trusted = InternalIdentifier.model_construct(value=123)
```

`model_construct()` bypasses all validators and conversions; any performance benefit is secondary to its trusted-data precondition.
