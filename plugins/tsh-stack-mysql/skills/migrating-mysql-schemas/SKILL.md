---
name: migrating-mysql-schemas
description: "Writes and reviews MySQL and Aurora MySQL schema changes on populated InnoDB tables: which ALTER TABLE operations run INSTANT, INPLACE or COPY, ALGORITHM and LOCK=NONE clauses that make MySQL refuse a write-blocking table copy, the metadata lock an ALTER waits for while every query queues behind it, lock_wait_timeout, binlog replica lag from long DDL, gh-ost or pt-online-schema-change for what MySQL cannot change online, foreign keys added with foreign_key_checks off, non-transactional DDL in migration tools, and batched backfills. Use when a MySQL migration adds, changes or drops a column, index or constraint on a table with production data, or when reviewing one an ORM generated."
when_to_use: "Trigger on: an ALTER TABLE on a large MySQL table, adding an index, foreign key, CHECK or NOT NULL to an existing MySQL table, widening an INT key to BIGINT, renaming or dropping a column in MySQL, a migration stuck on 'Waiting for table metadata lock', an ALTER that froze writes or left replicas behind, choosing between native online DDL, gh-ost and pt-online-schema-change, 'There is no active transaction' from Doctrine, or reviewing a Laravel, Doctrine, TypeORM, Prisma, Rails, Django, Alembic, Knex, Flyway or Liquibase migration that targets MySQL. Table design is designing-mysql-schemas; a slow query is optimizing-mysql-queries."
---

# Migrating MySQL Schemas

A migration that is correct SQL can still take production down. On MySQL three things
decide it: the metadata lock every `ALTER TABLE` waits for, whether the statement
copies the table while blocking writes, and how long replicas take to replay it.
This skill makes all three explicit before a migration ships.

## Version Baseline

MySQL 8.0, 8.4 LTS and 9.7 LTS with InnoDB, including Amazon Aurora MySQL 3
(8.0-compatible) and Aurora MySQL 8.4 (treat as 8.4). Community 8.0 reached end of
life in April 2026; Aurora MySQL 3 has standard support to April 2028. Run `SELECT VERSION();` (on Aurora also
`SELECT AURORA_VERSION();`) before choosing a recipe: several need an 8.0 minor,
marked `8.0.29+` in the references, and 8.0.29 itself was withdrawn for an
instant-DDL defect. An innovation release (9.0 to 9.6) is short-lived: say so,
and check each version-marked behaviour against that release's notes rather than
assuming 8.4 or 9.7. Below 8.0, stop and say the version is unsupported; continue only
when asked.

**MySQL only.** If the database is MariaDB, PostgreSQL, SQL Server or another engine,
say this skill does not apply and stop: online DDL, its algorithms and their limits
differ by engine, and MariaDB's have diverged from MySQL's. When a skill for that
engine is available in this session, load it instead; name none that is absent. On PlanetScale or Vitess,
the platform's own schema-change workflow replaces the migration recipes here.

## Applicability and Precedence

Read the project's migration tool and its conventions first: where migrations live,
how they run in CI and at deploy, and whether an online schema change tool (gh-ost,
pt-online-schema-change) is already installed and approved. The ORM or framework
skill installed for the project owns the tool's mechanics; this skill owns what the
SQL does to a live database. A project rule (for example "every migration is reviewed
by the DBA") outranks this skill.

This skill does not provision databases, tune server parameters, or run migrations
against a shared or production environment.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Name, for every statement, the algorithm it uses (`INSTANT`, `INPLACE`, `COPY`), whether it rebuilds the table and whether it permits concurrent writes, from [online-ddl-and-locks.md](./references/online-ddl-and-locks.md), before calling a migration safe. |
| MUST | State `ALGORITHM` and `LOCK` on every `ALTER TABLE` against a populated table (`ALGORITHM=INSTANT` alone, since `INSTANT` rejects any `LOCK` but `DEFAULT`; or `ALGORITHM=INPLACE, LOCK=NONE`). Without them MySQL silently falls back to a table copy that blocks writes; with them it refuses. |
| MUST | Run `SET SESSION lock_wait_timeout` to a few seconds before any DDL on a table with traffic. The default is a year; every `ALTER`, even an instant one, waits for an exclusive metadata lock on the table (and, for a foreign key, on the referenced table too), at the start and again at the end, and every query on the table queues behind it while it waits. |
| MUST | Treat an operation that needs `ALGORITHM=COPY` (a column type change, adding a `CHECK` constraint or a stored generated column, a character set conversion) on a large table with traffic as work for an online schema change tool or an agreed maintenance window (there, with `ALGORITHM=COPY` written out), never a plain migration. |
| MUST | Account for replica lag before running a long in-place build: a binlog replica starts the same `ALTER` only after the source commits it, and lags for its whole duration. Throttle with an online schema change tool when lag matters. |
| MUST | Put one DDL statement in each migration. MySQL commits implicitly after every DDL statement, so no tool can roll back a half-applied migration. |
| MUST | Check for orphan rows before adding a foreign key in place with `foreign_key_checks=0`, and set it for that session only: in that mode MySQL does not validate existing rows. |
| MUST | Rename or retype a column used by running code through expand-and-contract across deploys, and ship the code that stops reading a column before the migration that drops it. |
| MUST | Backfill large tables in bounded batches outside the schema migration, never one `UPDATE` over the whole table. |
| MUST | When the migration is written with an ORM or framework that has its own skill available in this session (a Symfony, NestJS or Python stack skill, for example), load that skill too, before writing the migration file. This skill owns what the SQL does to the database; that one owns how the tool writes and runs it. Name none that is absent. |
| MUST | When asked to review a whole change or its merge readiness (a pull request or a diff that also changes application code), not only the migration, load the general code-review skill too when one is available in this session (`reviewing-code`, for example). This skill covers the migration; that one covers the rest of the change. Name none that is absent. |
| NEVER | Run a migration against production, staging or any shared database yourself. Hand over the SQL, the tool command and the order of steps. |
| NEVER | Let a deploy retry a failed migration automatically, with one exception: a one-statement migration that failed with `ERROR 1205` (lock wait timeout) applied nothing and may be retried a few times with a pause. Any other failure can leave the schema and the tool's record of it disagreeing. |
| NEVER | Call a migration safe on a table whose size, traffic and replica topology you do not know. Ask, or state the assumption in the review. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Online DDL and locks](./references/online-ddl-and-locks.md) | Any migration on a table with data, every time | Algorithms and what each operation supports, the metadata lock queue, `lock_wait_timeout`, replica lag, finding blockers |
| [Zero-downtime recipes](./references/zero-downtime-recipes.md) | Adding an index or constraint, renaming, retyping or dropping a column | Step-by-step recipes, version differences, what has no online path |
| [Online schema change tools](./references/online-schema-change-tools.md) | An operation needs `COPY`, or an in-place build would lag replicas too long | gh-ost and pt-online-schema-change: requirements, foreign keys, throttling, cut-over, Aurora and RDS |
| [Backfilling data](./references/backfilling-data.md) | Rows must be updated or copied as part of the change | Batching by primary key, locks, undo history, replica lag, resumability |
| [Migration tools](./references/migration-tools.md) | The migration is written with an ORM or migration runner | Implicit commits per tool, adding `ALGORITHM` and `LOCK`, recording out-of-band changes, what generators emit |

Read [online-ddl-and-locks.md](./references/online-ddl-and-locks.md) before judging
any migration, and [zero-downtime-recipes.md](./references/zero-downtime-recipes.md)
before writing one that touches an existing column.

## Procedure

1. **Establish the target.** MySQL version, the table's row count and size
   (`information_schema.TABLES`, an estimate), its write rate, the replica topology
   (binlog replicas lag, Aurora replicas share storage), whether long transactions
   are normal there, and which online schema change tool is available. If you cannot
   read them, ask; a 1,000-row table and a 200-million-row table need different
   migrations.
2. **Read the migration as SQL.** For an ORM, read the generated SQL, not the model
   diff.
3. **Classify each statement** with
   [online-ddl-and-locks.md](./references/online-ddl-and-locks.md): algorithm,
   rebuild, concurrent writes, and how long it will run on this table.
4. **Replace every unsafe statement** with its recipe from
   [zero-downtime-recipes.md](./references/zero-downtime-recipes.md), or route it to
   [online-schema-change-tools.md](./references/online-schema-change-tools.md). Split
   into migrations of one statement each, ordered against the code deploys they
   depend on.
5. **Plan the data change** with [backfilling-data.md](./references/backfilling-data.md)
   when rows have to change.
6. **Add `lock_wait_timeout`, `ALGORITHM` and `LOCK`** to every statement that runs
   natively, with [migration-tools.md](./references/migration-tools.md) for how the
   tool carries them.
7. **Write the rollback** for each step, or state that a step is one-way and why.
8. **Hand over** the migration files and a deploy order: which migration or tool run,
   which code release, in what sequence, and what to check between steps.

## Reporting a review

For each statement: the algorithm and lock it gets, the risk on this table, and the
safe replacement. Lead with anything that copies the table or blocks writes on a
table with traffic, then anything that will lag replicas. Say plainly when the
migration is safe as written.
