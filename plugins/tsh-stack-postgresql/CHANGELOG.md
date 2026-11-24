# Changelog

All notable changes to `tsh-stack-postgresql` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

## [0.2.0] - 2026-11-24

### Added

- **Deleting in bulk**, in `backfilling-data.md`, which now also loads when rows
  must be deleted; `migrating-postgresql-schemas` triggers on purging rows from a
  large table, and its batching rule covers `DELETE` as well as `UPDATE`. A batch
  locks its candidates with `FOR UPDATE`, so a row that a concurrent update moves out
  of the filter is not deleted, bounds the key walk with a `max(id)` taken once, and
  needs every referencing column indexed. The race and the fix were checked on
  PostgreSQL 16.
- Never `updated_at` as the optimistic locking version; collation among the
  conventions to read first and not to duplicate; a full connection pool checked as
  a database symptom (a lock queue, `idle in transaction`) before the database is
  called innocent. These came from comparing this plugin with the MySQL one.

### Changed

- **Handover to another engine's skill.** On MySQL, MariaDB or another engine, each
  skill still says it does not apply, and now loads that engine's skill for the same
  work when one is installed instead of only stopping.
- **Triggers name the engine where they were generic**: schema design, migrations on
  an existing table, a migration that hung, and log output, where "slow-query-log"
  became "auto_explain or PostgreSQL log output". The slow-endpoint trigger stays
  generic: naming the engine there cost one run in nine on a prompt that does not
  name it. All seven routing cases that load this plugin passed (3 of 3 each; the
  slow-query case 6 of 6 after that trigger was reverted), and the migration cases
  passed again after the purge trigger was added.

## [0.1.1] - 2026-11-16

### Fixed

- **`migrating-postgresql-schemas` loads the code review for a whole pull request.**
  Asked to review a pull request that includes a migration, Claude sometimes loaded
  only this skill and judged the migration without the rest of the change. A new rule
  loads the general code-review skill too (`reviewing-code`, when installed) when the
  whole change or its merge readiness is under review, not only the migration. With
  the matching rule in `tsh-product-engineering` 0.12.1, a four-turn probe on Sonnet
  loaded both in 6 of 6 runs, up from 3 of 6, and a question about the migration
  alone did not load `reviewing-code` (6 of 6). Six runs is a small sample; both
  probes are manual checks in the repository's `evals/README.md`.

## [0.1.0] - 2026-11-13

Initial release: the database layer under every ORM, for PostgreSQL 14 to 18.

### Added

- **`migrating-postgresql-schemas`.** Writes and reviews migrations that run against
  a live table: the lock each statement takes and what it blocks, `lock_timeout` so a
  migration fails and retries instead of queueing all traffic behind it, and recipes
  for adding indexes, foreign keys, `NOT NULL`, unique and `CHECK` constraints,
  renaming, retyping and dropping columns without downtime. Includes batched
  backfills and how to run a migration outside a transaction in TypeORM, Prisma,
  Doctrine, Alembic, Django, Knex, Laravel, Rails, Flyway and Liquibase, and why only
  a transactional migration may be retried automatically.
- **`optimizing-postgresql-queries`.** Finds the queries that cost the most time with
  `pg_stat_statements`, reads `EXPLAIN (ANALYZE, BUFFERS)` node by node, explains
  misestimates, chooses indexes for a query (composite order, partial, covering,
  expression, GIN, BRIN), and fixes the query shapes that defeat indexes: N+1,
  `OFFSET` pagination, functions on columns, `OR`, implicit casts.
- **`designing-postgresql-schemas`.** Column types (time, money, keys including
  UUIDv7, `jsonb`), foreign keys and `ON DELETE`, `CHECK`, unique and exclusion
  constraints, and the recurring patterns: soft delete, multi-tenancy with row-level
  security, audit columns, optimistic locking, status history, polymorphic relations
  and partitioning.
