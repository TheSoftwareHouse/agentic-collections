# Changelog

All notable changes to `tsh-stack-mysql` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

## [0.1.0] - 2026-11-17

Initial release: the database layer under every ORM, for MySQL 8.0, 8.4 and 9.7 with
InnoDB, Aurora MySQL 3 and Aurora MySQL 8.4 included. Behaviour the skills rely on was checked against
MySQL 8.0.46, 8.4.13 and 9.7.4.

### Added

- **`migrating-mysql-schemas`.** Writes and reviews migrations that run against a
  live table: the algorithm each `ALTER` gets (`INSTANT`, `INPLACE`, `COPY`) and
  whether it blocks writes, `ALGORITHM` and `LOCK` stated so a table copy fails
  instead of running, `lock_wait_timeout` so a migration waiting for the metadata
  lock does not queue every query behind it, and replica lag from long DDL. Recipes
  for indexes, foreign keys (with the orphan check MySQL skips), `NOT NULL`, `CHECK`,
  renames, type changes including `INT` to `BIGINT` keys, and drops; when to use
  gh-ost or pt-online-schema-change, and the pre-checks their `INSERT IGNORE` row copy needs; batched backfills; and how Laravel, Doctrine,
  TypeORM, Prisma, Rails, Django, Alembic, Knex, Flyway and Liquibase handle MySQL's
  non-transactional DDL.
- **`optimizing-mysql-queries`.** Finds the queries that cost the most time in the
  `performance_schema` digests and the slow query log, reads `EXPLAIN` (whose default
  format is a tree on 9.7) and `EXPLAIN ANALYZE`, explains misestimates with
  statistics and histograms, chooses indexes around the clustered primary key, and
  fixes the query shapes that defeat them, including keyset pagination written as a
  row constructor, which MySQL scans from the start of the index.
- **`designing-mysql-schemas`.** Column types (`DATETIME` over `TIMESTAMP` for its 2038 limit, with UTC as the server's default time zone and not only the application's,
  money, `BIGINT` and `BINARY(16)` UUID keys, `JSON`), `utf8mb4` and the collation
  that decides which values are duplicates, strict `sql_mode`, foreign keys and their
  limits (cascades missing from the 8.x binary log), `CHECK` and unique constraints,
  uniqueness on live rows only, and the patterns: soft delete, multi-tenancy without
  row-level security, audit columns, optimistic locking, status history,
  polymorphic relations and partitioning.
