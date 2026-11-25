---
name: designing-mysql-schemas
description: "MySQL and InnoDB table design beneath any ORM: strict sql_mode, utf8mb4 and the collation that decides which strings a unique key treats as duplicates, DATETIME in UTC instead of TIMESTAMP and its 2038 limit, DECIMAL money, BIGINT AUTO_INCREMENT or BINARY(16) UUID keys, ENUM against lookup tables, JSON with generated columns, foreign keys whose cascades the 8.x binlog never records, CHECK constraints that only a CREATE TABLE adds cheaply, and tenant isolation without row-level security. Use when creating MySQL tables for a new feature, reviewing an entity or schema for a MySQL or Aurora MySQL database, or deciding how to store a kind of data there."
when_to_use: "Trigger on: sketching MySQL tables for a feature, picking a column type, character set, collation or primary key, 'Anna' and 'anna' colliding in a unique key, emoji rejected by a utf8 column, TIMESTAMP versus DATETIME, extending an ENUM, where tenant_id goes, one live row per customer alongside soft-deleted ones, partitioning a MySQL table, or auditing a Doctrine, Eloquent, TypeORM or Prisma model that targets MySQL for integrity gaps. Altering a populated table is migrating-mysql-schemas; a slow query is optimizing-mysql-queries."
---

# Designing MySQL Schemas

The schema is the one place a rule holds for every writer: every service, script,
migration and console session. Constraints the database enforces cannot be forgotten
by a code path; rules kept only in application code eventually are. On MySQL two
settings decide whether the schema's rules hold at all: strict `sql_mode` and the
collation.

## Version Baseline

MySQL 8.0, 8.4 LTS and 9.7 LTS with InnoDB, including Amazon Aurora MySQL 3
(8.0-compatible) and Aurora MySQL 8.4 (treat as 8.4). Community 8.0 reached end of
life in April 2026; Aurora MySQL 3 has standard support to April 2028. Some features need an 8.0 minor: `CHECK` constraints
are enforced from 8.0.16 (parsed and ignored before), expression defaults and
functional indexes from 8.0.13, multi-valued JSON indexes from 8.0.17. Check
`SELECT VERSION();` and every environment that runs the schema, including local and
CI. Below 8.0, stop and say the version is unsupported; continue only when asked.

**MySQL only.** If the database is MariaDB, PostgreSQL, SQL Server or another engine,
say this skill does not apply and stop: types, collations, constraints and their
defaults differ by engine, and MariaDB's have diverged from MySQL's. When a skill
for that engine is available in this session, load it instead; name none that is
absent.

## Applicability and Precedence

Read the existing schema and its conventions first: naming, key type, timestamp
columns, character set and collation, how tenancy and deletion are already handled.
**A convention the project already follows outranks this skill's defaults**; a second
convention beside the first is a finding, not an improvement. When the schema is
generated from an ORM's entities, the ORM's own skill owns how to express a choice in
that ORM; this skill owns what the resulting table should be.

This skill does not ship the change. A table that already holds data changes through
`migrating-mysql-schemas`.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Confirm `sql_mode` includes `STRICT_TRANS_TABLES` (or `STRICT_ALL_TABLES`) in every environment. Without it MySQL truncates and coerces invalid values with a warning instead of rejecting them, and types and `ENUM`s stop protecting anything. |
| MUST | Use `utf8mb4` for text, never `utf8` or `utf8mb3`, and choose each text column's collation deliberately: the default `utf8mb4_0900_ai_ci` treats `Anna`, `anna` and `ánna` as equal, in unique keys too. |
| MUST | Give every table an explicit primary key; prefer `BIGINT` (`UNSIGNED` if the project does) `AUTO_INCREMENT` or a time-ordered UUID stored as `BINARY(16)`. |
| MUST | Make a column `NOT NULL` unless absence is a real, distinct state of the data. |
| MUST | Store points in time as `DATETIME(3)` or `DATETIME(6)` in UTC, not `TIMESTAMP`, whose range ends in January 2038. `DATETIME` stores the session's wall-clock value, so set the server's default `time_zone` to `+00:00` (the parameter group on RDS and Aurora), not only the application connection's. |
| MUST | Store money as `DECIMAL` with an explicit scale, or as a `BIGINT` count of the smallest unit, with the currency stored beside it. Never `FLOAT` or `DOUBLE`. |
| MUST | Declare a foreign key for every reference to another table's row, choose its `ON DELETE` deliberately, and give both columns identical types and signedness. |
| MUST | Enforce invariants that must hold for every row with constraints (`CHECK`, `UNIQUE`, foreign keys), not only in application validation. |
| MUST | When asked to review a whole change or its merge readiness (a pull request or a diff that also changes application code), not only the schema, load the general code-review skill too when one is available in this session (`reviewing-code`, for example). This skill covers the schema; that one covers the rest of the change. Name none that is absent. |
| NEVER | Store several values in one delimited text column, or a reference in a column with no foreign key because "it could point at several tables". |
| NEVER | Reach for `JSON` for attributes that are queried, joined, constrained or present on every row. Those are columns. |
| NEVER | Introduce a second naming, key, timestamp or collation convention into a schema that already has one. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Data types](./references/data-types.md) | Choosing a column type, primary key, character set or collation | Text, character sets and collations, numbers and money, time, keys (`AUTO_INCREMENT`, UUIDs), booleans and status values, `JSON`, generated columns |
| [Keys and constraints](./references/keys-and-constraints.md) | Adding a reference, a uniqueness rule or any invariant | Foreign keys and `ON DELETE`, `CHECK` and its limits, unique keys and `NULL`, uniqueness on some rows only, `sql_mode`, naming |
| [Schema patterns](./references/schema-patterns.md) | Deletion, tenancy, history, concurrency, flexible attributes or table size is part of the design | Soft delete versus archive, multi-tenancy without RLS, audit columns, optimistic locking, status history, polymorphic relations, partitioning |

Read [data-types.md](./references/data-types.md) before choosing a primary key or a
collation: they are the hardest choices to change later.

## Procedure

1. **Read the domain and the existing schema.** The entities, their lifecycles, who
   writes them, and the conventions already in place, including `sql_mode` and the
   server, schema and table default collations.
2. **List the invariants** in plain language: what must always be true of each row
   and between rows ("an order line belongs to exactly one order", "one active
   subscription per customer"). Each becomes a type, a `NOT NULL`, a key or a
   constraint, from [keys-and-constraints.md](./references/keys-and-constraints.md).
3. **Choose types and collations** with [data-types.md](./references/data-types.md).
4. **Apply the patterns** the design needs, from
   [schema-patterns.md](./references/schema-patterns.md). Decide deletion and
   tenancy now: they are expensive to add to a populated schema.
5. **Write the DDL**, or the ORM entities that generate it, and read the generated
   DDL back with `SHOW CREATE TABLE`: an ORM default (nullable columns,
   `VARCHAR(255)` everywhere, `TIMESTAMP`, `utf8mb3`, a collation that differs from
   the joined table's) is a finding like any other.
6. **Name the indexes the known queries need** (foreign keys get one automatically;
   the main list and lookup queries). Further tuning belongs to
   `optimizing-mysql-queries`.
7. **Hand over** the DDL with the invariants it enforces, and the ones left to the
   application, with the reason.

## Reporting a review

List each finding with the table and column, the invariant or risk, and the
corrected DDL. Lead with what lets bad data in (non-strict mode, a missing
constraint or key, a lossy type, a collation that merges values that must differ),
then what will be expensive to change later (key type, collation, tenancy, deletion
model), then naming and style. Say plainly when the schema is sound.
