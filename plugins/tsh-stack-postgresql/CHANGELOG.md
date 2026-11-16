# Changelog

All notable changes to `tsh-stack-postgresql` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

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
