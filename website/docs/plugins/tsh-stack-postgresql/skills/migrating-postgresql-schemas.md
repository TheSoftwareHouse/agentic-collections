---
title: Migrating PostgreSQL Schemas
sidebar_label: migrating-postgresql-schemas
sidebar_position: 1
description: Writes and reviews PostgreSQL schema migrations that run against a live database without stopping traffic.
sources:
  - plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas/
sources_hash: "2d3bbfcfe358f18ee89c00de5cb1216597a6030934eb534c1f6f180fb85b4410"
---

# Migrating PostgreSQL Schemas

**Plugin:** [`tsh-stack-postgresql`](/docs/plugins/tsh-stack-postgresql/)  
**Invoke:** `/tsh-stack-postgresql:migrating-postgresql-schemas`, and Claude also loads it when the work matches its description  
**Used by:** [`designing-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas) hands it every change to a table that already holds data, and [`optimizing-postgresql-queries`](/docs/plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries) hands it the index a slow query needs. In `tsh-product-engineering`, the `reviewing-code` skill and the `code-reviewer` agent load the database engine's skill that covers a change under review, which for a schema migration is this one; `creating-implementation-plans` loads it when a plan changes a table that holds data and names it for the implementers of those tasks; and this skill loads `reviewing-code` in turn when the whole change or its merge readiness is under review, not only the migration.

A migration that is correct SQL can still take production down. What decides it is the lock each statement takes, how long it holds it, and what is queued behind it. The skill makes those three things explicit before a migration ships, for PostgreSQL 14 to 18. On another engine such as MySQL, MariaDB or SQL Server, it says it does not apply, and loads that engine's skill when one is installed or stops otherwise; below version 14 it stops and says the version is unsupported.

Use it when a migration adds, changes or drops a column, index or constraint on a table that already holds production data, when a migration hung or caused an outage, or when reviewing a migration an ORM generated. The ORM's own skill owns the tool's mechanics; this skill owns what the generated SQL does to a live database. It never runs a migration against a production, staging or shared database: it hands over the SQL and the order of steps.

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Lock levels** | The lock each DDL statement takes and what it blocks, which statements rewrite or scan the table, locks held until commit, the referenced table locked by dropping a table or foreign key, the lock queue that turns a 5 ms change into an outage behind one long transaction or an anti-wraparound vacuum, and queries to find them and blockers |
| **`lock_timeout` and retries** | A migration that waits too long for its lock fails and retries instead of blocking every query queued behind it |
| **Zero-downtime recipes** | Indexes built `CONCURRENTLY` outside a transaction, including partitioned tables; `NOT NULL` through a `NOT VALID` check (or the 18+ form); foreign keys and `CHECK` constraints added `NOT VALID` and validated separately; unique constraints attached to a concurrently built index; renames, type changes (including `integer` to `bigint` keys) and drops through expand-and-contract across deploys |
| **Backfills** | Batches walked by primary key, sized by time, resumable and outside the schema migration, with replication lag and vacuum in mind |
| **Migration tools** | How to run one migration outside a transaction in TypeORM, Prisma, Doctrine, Alembic, Django, Knex, Laravel, Rails, Flyway and Liquibase, with each tool's caveats; why only a transactional migration may be retried automatically; what generators get wrong, starting with a rename emitted as a drop and an add |

## How it works

1. **Establish the target:** PostgreSQL version, the table's size and write rate, and whether long transactions are normal there.
2. **Read the migration as SQL**, including whether the runner wraps it in a transaction.
3. **Classify each statement** by the lock it takes and whether it rewrites or scans the table.
4. **Replace every unsafe statement** with its recipe, split into migrations that can run on their own, ordered against the code deploys they depend on.
5. **Plan the data change** as a batched backfill when rows have to change.
6. **Add `lock_timeout`** and a retry where needed, write the rollback for each step, and hand over the files with a deploy order.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Name the lock every statement takes and what it blocks before calling a migration safe |
| MUST | Set `lock_timeout` on any migration that takes `ACCESS EXCLUSIVE` or `SHARE ROW EXCLUSIVE` on a table with traffic, but not on concurrent index builds or constraint validation |
| MUST | Keep every `ACCESS EXCLUSIVE` statement in a transaction that commits right after it, because locks are held until commit |
| MUST | Build indexes on populated tables with `CREATE INDEX CONCURRENTLY`, outside a transaction, one statement per migration, and check for an `INVALID` index after a failure |
| MUST | Add foreign keys and `CHECK` constraints to populated tables as `NOT VALID`, then validate them in a separate step |
| MUST | Rename or retype a column used by running code through expand-and-contract, and ship the code that stops reading a column before the migration that drops it |
| MUST | Backfill large tables in bounded batches outside the schema migration |
| MUST | When the migration is written with an ORM or framework that has its own skill available in the session, load that skill too, before writing the migration file |
| MUST | When asked to review a whole change or its merge readiness, not only the migration, load the general code-review skill too when one is available |
| NEVER | Run a migration against production, staging or any shared database, or call a migration safe on a table whose size and traffic are unknown |
| NEVER | Let a deploy retry a failed non-transactional migration automatically |

## References

| Reference | Load when |
| :-- | :-- |
| Lock levels | Any migration on a table with data, every time |
| Zero-downtime recipes | Adding a constraint or index, renaming, retyping or dropping a column |
| Backfilling data | Rows must be updated or copied as part of the change |
| Migration tools | The migration is written with an ORM or migration runner |

## Related skills

- [`designing-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas) decides what the table should be; this skill ships the change to a table that already holds data.
- [`optimizing-postgresql-queries`](/docs/plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries) hands the index a slow query needs to this skill, so it ships concurrently.

## Source

[`plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas/SKILL.md)
