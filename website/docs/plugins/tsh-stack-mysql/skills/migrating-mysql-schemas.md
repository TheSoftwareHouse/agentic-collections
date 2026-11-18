---
title: Migrating MySQL Schemas
sidebar_label: migrating-mysql-schemas
sidebar_position: 1
description: Writes and reviews MySQL schema migrations that run against a live InnoDB table without blocking writes or stalling replicas.
sources:
  - plugins/tsh-stack-mysql/skills/migrating-mysql-schemas/
sources_hash: "9ca67cc00167208cef95d2070c03e039e9c57c10c51e5372c9fbb265826d03a8"
---

# Migrating MySQL Schemas

**Plugin:** [`tsh-stack-mysql`](/docs/plugins/tsh-stack-mysql/)  
**Invoke:** `/tsh-stack-mysql:migrating-mysql-schemas`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`designing-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/designing-mysql-schemas) hands it every change to a table that already holds data, and [`optimizing-mysql-queries`](/docs/plugins/tsh-stack-mysql/skills/optimizing-mysql-queries) hands it the index a slow query needs. The `reviewing-code` skill in `tsh-product-engineering` loads whichever stack skill is available in the session for the change under review, but names no plugin; this skill loads `reviewing-code` in turn when the whole change or its merge readiness is under review, not only the migration.

A migration that is correct SQL can still take production down. On MySQL three things decide it: the metadata lock every `ALTER TABLE` waits for, whether the statement copies the table while blocking writes, and how long binlog replicas take to replay it. The skill makes those three explicit before a migration ships, for MySQL 8.0, 8.4 and 9.7, Aurora MySQL 3 and Aurora MySQL 8.4 included. On MariaDB or another engine it says it does not apply and stops; below 8.0 it stops and says the version is unsupported.

Use it when a migration adds, changes or drops a column, index or constraint on a table that already holds production data, when a migration hung on a metadata lock or left replicas lagging, or when reviewing a migration an ORM generated. The ORM's own skill owns the tool's mechanics; this skill owns what the SQL does to a live database. It never runs a migration or an online schema change tool against a production, staging or shared database: it hands over the SQL, the commands and the order of steps.

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Online DDL and locks** | Which algorithm (`INSTANT`, `INPLACE`, `COPY`) each common `ALTER` gets and whether it blocks writes, checked on 8.0, 8.4 and 9.7; `ALGORITHM` and `LOCK` stated so a table copy fails instead of running; the instant row-version budget; what a rebuild costs; the metadata lock queue, on the referenced table too for a foreign key, and `lock_wait_timeout` at the start and the end of a build; replica lag; queries to find blockers |
| **Zero-downtime recipes** | Columns added and dropped instantly, indexes built online (expression indexes in two steps), foreign keys added in place with an explicit orphan check, `NOT NULL` after a backfill, `CHECK` constraints with no online path, renames and type changes through expand-and-contract, `INT` to `BIGINT` keys that other tables reference, indexes dropped after a release as invisible |
| **Online schema change tools** | gh-ost and pt-online-schema-change compared: foreign keys, triggers, binlog needs, throttling and cut-over; RDS and Aurora notes; PlanetScale and Vitess |
| **Backfills** | Closed primary-key ranges in small transactions, gap locks and undo history, pausing on replica lag, outside the schema migration, bulk deletes |
| **Migration tools** | MySQL's non-transactional DDL in Laravel, Doctrine, TypeORM, Prisma, Rails, Django, Alembic, Knex, Flyway and Liquibase; how each carries `ALGORITHM`, `LOCK` and `lock_wait_timeout`; how each records a change made outside it; what generators get wrong |

## How it works

1. **Establish the target:** MySQL version, the table's size and write rate, the replica topology, whether long transactions are normal there, and which online schema change tool is available.
2. **Read the migration as SQL**, not as the model diff.
3. **Classify each statement** by algorithm, rebuild and whether it permits writes.
4. **Replace every unsafe statement** with its recipe or route it to an online schema change tool, one DDL statement per migration, ordered against the code deploys they depend on.
5. **Plan the data change** as a batched backfill when rows have to change.
6. **Add `lock_wait_timeout`, `ALGORITHM` and `LOCK`**, write the rollback for each step, and hand over the files with a deploy order.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Name the algorithm, rebuild and write blocking of every statement before calling a migration safe |
| MUST | State `ALGORITHM` and `LOCK` on every `ALTER TABLE` against a populated table, so MySQL refuses instead of silently copying the table |
| MUST | Set `lock_wait_timeout` to a few seconds before any DDL on a table with traffic; the default is a year, and the wait happens at the start and again at the end |
| MUST | Treat an operation that needs a table copy on a large busy table as work for an online schema change tool or an agreed maintenance window |
| MUST | Account for replica lag before a long in-place build |
| MUST | Put one DDL statement in each migration, because MySQL commits implicitly after each one |
| MUST | Check for orphan rows before adding a foreign key with `foreign_key_checks=0`, set for that session only |
| MUST | Rename or retype a column used by running code through expand-and-contract, and ship the code that stops reading a column before the migration that drops it |
| MUST | Backfill large tables in bounded batches outside the schema migration |
| MUST | When the migration is written with an ORM or framework that has its own skill available in the session, load that skill too, before writing the migration file |
| MUST | When asked to review a whole change or its merge readiness, not only the migration, load the general code-review skill too when one is available |
| NEVER | Run a migration against production, staging or any shared database, or call a migration safe on a table whose size, traffic and replica topology are unknown |
| NEVER | Let a deploy retry a failed migration automatically, except a one-statement migration that timed out on the metadata lock and applied nothing |

## References

| Reference | Load when |
| :-- | :-- |
| Online DDL and locks | Any migration on a table with data, every time |
| Zero-downtime recipes | Adding an index or constraint, renaming, retyping or dropping a column |
| Online schema change tools | An operation needs a table copy, or an in-place build would lag replicas too long |
| Backfilling data | Rows must be updated or copied as part of the change |
| Migration tools | The migration is written with an ORM or migration runner |

## Related skills

- [`designing-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/designing-mysql-schemas) decides what the table should be; this skill ships the change to a table that already holds data.
- [`optimizing-mysql-queries`](/docs/plugins/tsh-stack-mysql/skills/optimizing-mysql-queries) hands the index a slow query needs to this skill, so it ships online.

## Source

[`plugins/tsh-stack-mysql/skills/migrating-mysql-schemas/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-mysql/skills/migrating-mysql-schemas/SKILL.md)
