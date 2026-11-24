---
name: designing-postgresql-schemas
description: "Designs and reviews PostgreSQL tables at the database level, whatever ORM maps them: column types (timestamptz, numeric or integer minor units for money, text over varchar(n), identity or UUIDv7 keys, jsonb), keys and constraints that keep bad data out (NOT NULL, CHECK, foreign keys and their ON DELETE, unique and exclusion constraints), and the recurring patterns: soft delete, multi-tenancy with row-level security, audit columns, optimistic locking, status history, partitioning. Use when creating tables for a new feature, reviewing an entity or schema change, or deciding how to store a kind of data."
when_to_use: "Trigger on: designing PostgreSQL tables for a feature, choosing a column type or primary key, storing money, time, status values or flexible attributes, deciding between an enum, a CHECK constraint and a lookup table, adding foreign keys and choosing ON DELETE, soft delete versus archiving, multi-tenant data isolation, row-level security, deciding whether to partition a table, polymorphic relations, or reviewing an entity, model or PostgreSQL schema for data-integrity gaps. Shipping the change to a live table is migrating-postgresql-schemas; a slow query is optimizing-postgresql-queries."
---

# Designing PostgreSQL Schemas

The schema is the one place a rule holds for every writer: every service, script,
migration and console session. Constraints the database enforces cannot be forgotten
by a code path; rules kept only in application code eventually are.

## Version Baseline

PostgreSQL 14 to 18; 14 reached end of life in November 2026. Some choices depend on
the version (`uuidv7()` and virtual generated columns are 18+). Check
`SELECT version();` or the project's pinned image and every environment that runs
it, including local and CI. Below 14, stop and say the project is on an unsupported
version; continue only when asked.

**PostgreSQL only.** If the project's database is MySQL, MariaDB, SQL Server or
another engine, say this skill does not apply: types, constraints and their defaults differ by engine.
Load that engine's skill for the same work when one is available in this session;
otherwise stop. Name none that is absent.

## Applicability and Precedence

Read the existing schema and its conventions first: naming, key type, timestamp
columns, collation, how tenancy and deletion are already handled. **A convention the project
already follows outranks this skill's defaults**; a second convention beside the
first is a finding, not an improvement. When the schema is generated from an ORM's
entities, the ORM's own skill owns how to express a choice in that ORM; this skill
owns what the resulting table should be.

This skill does not ship the change. A table that already holds data changes through
`migrating-postgresql-schemas`.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Make a column `NOT NULL` unless absence is a real, distinct state of the data. |
| MUST | Store points in time as `timestamptz`. `timestamp` without time zone is for wall-clock values with no zone, such as a store's opening hour. |
| MUST | Store money as `numeric` with an explicit scale, or as an integer count of the smallest unit, with the currency stored beside it. Never `real`, `double precision` or `money`. |
| MUST | Declare a foreign key for every reference to another table's row, choose its `ON DELETE` deliberately, and index the referencing column. |
| MUST | Enforce invariants that must hold for every row with constraints (`CHECK`, `UNIQUE`, exclusion), not only in application validation. |
| MUST | Use `GENERATED ... AS IDENTITY` for integer keys, not `serial`. |
| NEVER | Store several values in one delimited text column, or a reference in a column with no foreign key because "it could point at several tables". |
| NEVER | Reach for `jsonb` for attributes that are queried, joined, constrained or present on every row. Those are columns. |
| NEVER | Introduce a second naming, key, timestamp or collation convention into a schema that already has one. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Data types](./references/data-types.md) | Choosing a column type or primary key | Text, numbers and money, time, keys (identity, UUIDv4, UUIDv7), booleans and status values, `jsonb`, arrays, ranges |
| [Keys and constraints](./references/keys-and-constraints.md) | Adding a reference, a uniqueness rule or any invariant | Foreign keys and `ON DELETE`, `CHECK`, unique and partial unique, exclusion, deferrable constraints, naming |
| [Schema patterns](./references/schema-patterns.md) | Deletion, tenancy, history, concurrency, flexible attributes or table size is part of the design | Soft delete versus archive, multi-tenancy and RLS, audit columns, optimistic locking, status history, polymorphic relations, partitioning |

Read [data-types.md](./references/data-types.md) before choosing a primary key: it is
the hardest choice to change later.

## Procedure

1. **Read the domain and the existing schema.** The entities, their lifecycles, who
   writes them, and the conventions already in place.
2. **List the invariants** in plain language: what must always be true of each row
   and between rows ("an order line belongs to exactly one order", "one active
   subscription per customer"). Each becomes a type, a `NOT NULL`, a key or a
   constraint, from [keys-and-constraints.md](./references/keys-and-constraints.md).
3. **Choose types** with [data-types.md](./references/data-types.md).
4. **Apply the patterns** the design needs, from
   [schema-patterns.md](./references/schema-patterns.md). Decide deletion and
   tenancy now: they are expensive to add to a populated schema.
5. **Write the DDL**, or the ORM entities that generate it, and read the generated
   DDL back: an ORM default (nullable columns, `varchar(255)`, `timestamp` without
   zone, missing foreign key indexes) is a finding like any other.
6. **Name the indexes the known queries need** (foreign keys, the main list and
   lookup queries). Further tuning belongs to `optimizing-postgresql-queries`.
7. **Hand over** the DDL with the invariants it enforces, and the ones left to the
   application, with the reason.

## Reporting a review

List each finding with the table and column, the invariant or risk, and the
corrected DDL. Lead with what lets bad data in (a missing constraint or key, a lossy
type), then what will be expensive to change later (key type, tenancy, deletion
model), then naming and style. Say plainly when the schema is sound.
