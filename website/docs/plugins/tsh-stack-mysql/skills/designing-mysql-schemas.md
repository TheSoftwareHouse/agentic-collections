---
title: Designing MySQL Schemas
sidebar_label: designing-mysql-schemas
sidebar_position: 3
description: Designs and reviews MySQL tables at the database level, whatever ORM maps them, with types, collations, keys and constraints that keep bad data out.
sources:
  - plugins/tsh-stack-mysql/skills/designing-mysql-schemas/
sources_hash: "0f40a5012bb6f7e469a986f45149d74ae7e80304d1c93c4e2dc7dbff3b386812"
---

# Designing MySQL Schemas

**Plugin:** [`tsh-stack-mysql`](/docs/plugins/tsh-stack-mysql/)  
**Invoke:** `/tsh-stack-mysql:designing-mysql-schemas`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`migrating-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/migrating-mysql-schemas) and [`optimizing-mysql-queries`](/docs/plugins/tsh-stack-mysql/skills/optimizing-mysql-queries) hand table and column design to it. The `reviewing-code` skill in `tsh-product-engineering` loads whichever stack skill is available in the session for the change under review, but names no plugin.

The schema is the one place a rule holds for every writer: every service, script, migration and console session. On MySQL two settings decide whether its rules hold at all: strict `sql_mode` and the collation. The skill designs and reviews tables so that the database enforces the invariants that must hold for every row, on MySQL 8.0, 8.4 and 9.7, Aurora MySQL 3 and Aurora MySQL 8.4 included. On MariaDB or another engine it says it does not apply and stops; below 8.0 it stops and says the version is unsupported.

Use it when creating tables for a new feature, reviewing an entity or schema change, or deciding how to store a kind of data. A convention the project already follows outranks the skill's defaults. When the schema is generated from an ORM's entities, the ORM's own skill owns how to express a choice in that ORM; this skill owns what the resulting table should be. A table that already holds data changes through [`migrating-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/migrating-mysql-schemas).

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Data types** | `VARCHAR` limits that matter in `utf8mb4`, `utf8mb4` over `utf8`, collations and which values they treat as duplicates, money, `DATETIME` in UTC over `TIMESTAMP` and its 2038 limit, fractional-second rounding, `BIGINT` and `BINARY(16)` UUID keys, booleans, `ENUM` against `CHECK` and lookup tables, `JSON`, generated columns |
| **Keys and constraints** | Strict `sql_mode` first, foreign keys and `ON DELETE`, cascades that triggers and the 8.x binary log do not see, `CHECK` and its limits, unique keys and `NULL`, uniqueness on some rows only through a generated column, naming |
| **Schema patterns** | Soft delete or archive, multi-tenancy without row-level security (composite foreign keys that include the tenant), audit columns, optimistic locking with MySQL's changed-rows count, status history, polymorphic relations, partitioning and its limits |

## How it works

1. **Read the domain and the existing schema**, including `sql_mode` and the default collations.
2. **List the invariants** in plain language; each becomes a type, a `NOT NULL`, a key or a constraint.
3. **Choose types and collations**, starting with the primary key.
4. **Apply the patterns** the design needs, deciding deletion and tenancy now.
5. **Write the DDL** or the ORM entities, and read the generated DDL back with `SHOW CREATE TABLE`.
6. **Name the indexes** the known queries need, and hand over the DDL with the invariants it enforces and those left to the application.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Confirm strict `sql_mode` in every environment |
| MUST | Use `utf8mb4`, and choose each text column's collation deliberately |
| MUST | Give every table an explicit primary key |
| MUST | Make a column `NOT NULL` unless absence is a real, distinct state |
| MUST | Store points in time as `DATETIME` in UTC, not `TIMESTAMP` |
| MUST | Store money as `DECIMAL` with an explicit scale, or as an integer count of the smallest unit, with the currency beside it |
| MUST | Declare a foreign key for every reference, choose its `ON DELETE` deliberately, and match both columns' types exactly |
| MUST | Enforce invariants with constraints, not only in application validation |
| MUST | When asked to review a whole change or its merge readiness, not only the schema, load the general code-review skill too when one is available |
| NEVER | Store several values in one delimited column, or a reference without a foreign key |
| NEVER | Use `JSON` for attributes that are queried, joined, constrained or present on every row |
| NEVER | Introduce a second naming, key, timestamp or collation convention into a schema that already has one |

## References

| Reference | Load when |
| :-- | :-- |
| Data types | Choosing a column type, primary key, character set or collation |
| Keys and constraints | Adding a reference, a uniqueness rule or any invariant |
| Schema patterns | Deletion, tenancy, history, concurrency, flexible attributes or table size is part of the design |

## Related skills

- [`migrating-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/migrating-mysql-schemas) ships the design to a table that already holds data.
- [`optimizing-mysql-queries`](/docs/plugins/tsh-stack-mysql/skills/optimizing-mysql-queries) takes over when a query on the table is slow.

## Source

[`plugins/tsh-stack-mysql/skills/designing-mysql-schemas/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-mysql/skills/designing-mysql-schemas/SKILL.md)
