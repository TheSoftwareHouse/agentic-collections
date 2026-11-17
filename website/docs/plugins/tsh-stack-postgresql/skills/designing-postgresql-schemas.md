---
title: Designing PostgreSQL Schemas
sidebar_label: designing-postgresql-schemas
sidebar_position: 3
description: Designs and reviews PostgreSQL tables at the database level, whatever ORM maps them, with types, keys and constraints that keep bad data out.
sources:
  - plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas/
sources_hash: "147d237a72bebc6af3d6671c7e748c9b43e6a5e149b49c66c9da0ee14667f5b4"
---

# Designing PostgreSQL Schemas

**Plugin:** [`tsh-stack-postgresql`](/docs/plugins/tsh-stack-postgresql/)  
**Invoke:** `/tsh-stack-postgresql:designing-postgresql-schemas`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`migrating-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas) and [`optimizing-postgresql-queries`](/docs/plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries) hand table and column design to it. The `reviewing-code` skill in `tsh-product-engineering` loads the database engine's skill for a schema migration or a new query shape, which are the other two skills of this plugin, not this one.

The schema is the one place a rule holds for every writer: every service, script, migration and console session. The skill designs and reviews tables so that the database enforces the invariants that must hold for every row, on PostgreSQL 14 to 18. On another engine such as MySQL, MariaDB or SQL Server, it says it does not apply and loads that engine's skill when one is installed, or stops; below version 14 it stops and says the version is unsupported.

Use it when creating tables for a new feature, reviewing an entity or schema change, or deciding how to store a kind of data. A convention the project already follows outranks the skill's defaults. When the schema is generated from an ORM's entities, the ORM's own skill owns how to express a choice in that ORM; this skill owns what the resulting table should be. A table that already holds data changes through [`migrating-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas).

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Data types** | Primary keys (`bigint` identity, UUIDv7 with `uuidv7()` on 18 or from the application, and the cost of random UUIDv4), text, numbers and money, time (`timestamptz`, `date`, local times with a zone column), booleans and status values (`CHECK`, lookup table or enum), `jsonb`, arrays, ranges and generated columns |
| **Keys and constraints** | Foreign keys with an index on the referencing column, choosing `ON DELETE`, `CHECK` constraints, unique and partial unique indexes, `NULLS NOT DISTINCT`, exclusion constraints, deferrable constraints, naming, and which rules stay in the application |
| **Schema patterns** | Soft delete or archive, multi-tenancy models and tenant-scoped keys, row-level security and its pitfalls, audit columns, optimistic locking, status history, polymorphic relations, flexible attributes, and when partitioning earns its cost |

## How it works

1. **Read the domain and the existing schema**, with the conventions already in place.
2. **List the invariants** in plain language, each to become a type, a `NOT NULL`, a key or a constraint.
3. **Choose types**, then **apply the patterns** the design needs, deciding deletion and tenancy before the table holds data.
4. **Write the DDL**, or the ORM entities that generate it, and read the generated DDL back for ORM defaults that are findings.
5. **Name the indexes the known queries need**, and hand over the DDL with the invariants it enforces and those left to the application.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Make a column `NOT NULL` unless absence is a real, distinct state of the data |
| MUST | Store points in time as `timestamptz`, and money as `numeric` or integer minor units with the currency beside it, never a floating-point type or `money` |
| MUST | Declare a foreign key for every reference to another table's row, choose its `ON DELETE` deliberately, and index the referencing column |
| MUST | Enforce invariants that must hold for every row with constraints, not only in application validation, and use identity columns rather than `serial` |
| NEVER | Store several values in one delimited column, or a reference without a foreign key |
| NEVER | Use `jsonb` for attributes that are queried, joined, constrained or present on every row |
| NEVER | Introduce a second naming, key, timestamp or collation convention into a schema that already has one |

## References

| Reference | Load when |
| :-- | :-- |
| Data types | Choosing a column type or primary key |
| Keys and constraints | Adding a reference, a uniqueness rule or any invariant |
| Schema patterns | Deletion, tenancy, history, concurrency, flexible attributes or table size is part of the design |

## Related skills

- [`migrating-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas) ships a design change to a table that already holds data.
- [`optimizing-postgresql-queries`](/docs/plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries) tunes indexes and queries beyond those the design names.

## Source

[`plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas/SKILL.md)
