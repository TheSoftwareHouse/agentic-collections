---
name: migrating-postgresql-schemas
description: "Writes and reviews PostgreSQL schema migrations that run against a live database without stopping traffic: the lock each DDL statement takes and what it blocks, lock_timeout so a migration waits instead of queueing everyone behind it, expand-and-contract for renames and type changes, NOT VALID constraints validated separately, indexes built CONCURRENTLY outside a transaction, and batched backfills. Use when a migration adds, changes or drops a column, index or constraint on a table that already holds production data, or when reviewing a migration an ORM generated."
when_to_use: "Trigger on: adding a column, index, foreign key, unique or NOT NULL constraint to an existing PostgreSQL table, renaming a column or table, changing a column type, dropping a column, backfilling or rewriting rows in a large table, a PostgreSQL migration that hung, timed out or caused an outage, reviewing a TypeORM, Prisma, Doctrine, Alembic, Django, Knex, Laravel, Rails or Flyway migration that targets PostgreSQL, or planning a schema change that must ship with zero downtime. How to shape the schema in the first place is designing-postgresql-schemas; a slow query is optimizing-postgresql-queries."
---

# Migrating PostgreSQL Schemas

A migration that is correct SQL can still take production down. What decides it is
the lock each statement takes, how long it holds it, and what is queued behind it.
This skill makes those three things explicit before a migration ships.

## Version Baseline

PostgreSQL 14 to 18; 14 reached end of life in November 2026. Run `SELECT version();`
or read the version pinned in the project (Docker image, Terraform, managed-service
config) before choosing a recipe: several differ by major version, and the references
mark a recipe with the first version it works on (`12+`, `18+`). Below 14, stop and
say the project is on an unsupported version; continue only when asked, and then
only with recipes whose mark the version satisfies.

**PostgreSQL only.** If the project's database is MySQL, MariaDB, SQL Server or
another engine, say this skill does not apply: lock modes and online DDL differ by engine. Load that engine's skill when one is available in this session; otherwise stop. Name none that is absent.

## Applicability and Precedence

Read the project's migration tool and its conventions first: where migrations live,
how they run in CI and at deploy, and whether each one runs in a transaction. The
ORM or framework skill installed for the project owns the tool's mechanics; this
skill owns what the generated SQL does to a live database. A project rule
(for example "every migration is reviewed by the DBA") outranks this skill.

This skill does not provision databases, tune server parameters, or run
migrations against a shared or production environment.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Name the lock every statement takes and what it blocks, from [lock-levels.md](./references/lock-levels.md), before calling a migration safe. |
| MUST | Set `lock_timeout` (a few seconds) on any migration that takes `ACCESS EXCLUSIVE` or `SHARE ROW EXCLUSIVE` on a table with traffic, so it fails and retries instead of blocking every query queued behind it. Not on `CREATE INDEX CONCURRENTLY` or `VALIDATE CONSTRAINT`, whose locks do not block traffic. |
| MUST | Keep every `ACCESS EXCLUSIVE` statement in a transaction that commits right after it. Locks are held until commit, so a scan, backfill or index build later in the same transaction turns a brief lock into an outage. |
| MUST | Build indexes on populated tables with `CREATE INDEX CONCURRENTLY`, outside a transaction, one statement per migration, and check for an `INVALID` index after a failure. |
| MUST | Add foreign keys and `CHECK` constraints to populated tables as `NOT VALID`, then `VALIDATE CONSTRAINT` in a separate step. |
| MUST | Rename or retype a column used by running code through expand-and-contract across deploys, never in one statement. |
| MUST | Backfill large tables in bounded batches outside the schema migration, never one `UPDATE` over the whole table. |
| MUST | Ship the code that stops reading a column before the migration that drops it. |
| MUST | When the migration is written with an ORM or framework that has its own skill available in this session (a NestJS, Symfony or Python stack skill, for example), load that skill too, before writing the migration file. This skill owns what the SQL does to the database; that one owns how the tool writes and runs it. Name none that is absent. |
| MUST | When asked to review a whole change or its merge readiness (a pull request or a diff that also changes application code), not only the migration, load the general code-review skill too when one is available in this session (`reviewing-code`, for example). This skill judges the migration; that one judges the rest of the change and merge readiness. Name none that is absent. |
| NEVER | Run a migration against production, staging or any shared database yourself. Hand over the SQL and the order of steps. |
| NEVER | Let a deploy retry a failed non-transactional migration automatically. The tool's state (and any invalid index) needs resolving first. |
| NEVER | Call a migration safe on a table whose size and traffic you do not know. Ask, or state the assumption in the review. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Lock levels](./references/lock-levels.md) | Any migration on a table with data, every time | Which lock each DDL takes, what it blocks, rewrites, the lock queue, `lock_timeout` and retries |
| [Zero-downtime recipes](./references/zero-downtime-recipes.md) | Adding a constraint or index, renaming, retyping or dropping a column | Step-by-step expand-and-contract recipes, version differences |
| [Backfilling data](./references/backfilling-data.md) | Rows must be updated, copied or deleted as part of the change | Batching, ordering, bulk deletes, vacuum, replication lag, resumability |
| [Migration tools](./references/migration-tools.md) | The migration is written with an ORM or migration runner | Turning off the per-migration transaction, what generators emit, review points per tool |

Read [lock-levels.md](./references/lock-levels.md) before judging any migration, and
[zero-downtime-recipes.md](./references/zero-downtime-recipes.md) before writing one
that touches an existing column.

## Procedure

1. **Establish the target.** PostgreSQL major version, the table's row count and
   size (`pg_total_relation_size`), its write rate, and whether a long transaction
   or replica lag is normal there. If you cannot read them, ask; a 1,000-row table
   and a 200-million-row table need different migrations.
2. **Read the migration as SQL.** For an ORM, read the generated SQL, not the model
   diff. Note whether the runner wraps it in a transaction.
3. **Classify each statement** with [lock-levels.md](./references/lock-levels.md):
   lock taken, whether it rewrites or scans the table, and how long it holds the lock.
4. **Replace every unsafe statement** with its recipe from
   [zero-downtime-recipes.md](./references/zero-downtime-recipes.md), split into
   migrations that can each run on their own, and order them against the code
   deploys they depend on.
5. **Plan the data change** with [backfilling-data.md](./references/backfilling-data.md)
   when rows have to change.
6. **Add `lock_timeout`** and a retry for the statements that need it.
7. **Write the rollback** for each step, or state that a step is one-way and why.
8. **Hand over** the migration files and a deploy order: which migration, which code
   release, in what sequence, and what to check between steps.

## Reporting a review

For each statement: the lock it takes, the risk on this table, and the safe
replacement. Lead with anything that takes `ACCESS EXCLUSIVE` for longer than a
moment on a table with traffic. Say plainly when the migration is safe as written.
