---
name: optimizing-postgresql-queries
description: "Finds and fixes slow PostgreSQL queries from evidence: pg_stat_statements to find what actually costs time, EXPLAIN (ANALYZE, BUFFERS) read node by node, estimate-versus-actual row counts and stale statistics, choosing the index that fits the query (composite column order, partial, covering, GIN, BRIN), and the query shapes that defeat an index: N+1 loops, OFFSET pagination, functions on indexed columns, OR across columns, implicit casts. Use when an endpoint or job is slow because of the database, a query plan needs explaining, or someone proposes adding an index."
when_to_use: "Trigger on: a slow endpoint, report or background job traced to a query, a query plan or EXPLAIN output pasted for explanation, a sequential scan on a large table, deciding which index to add or whether an existing one is used, N+1 queries from an ORM, deep pagination getting slower, high database CPU or I/O, pg_stat_statements, auto_explain or PostgreSQL log output, a query that was fast and became slow, or reviewing a change that adds a query to a hot path. A migration that adds the index safely is migrating-postgresql-schemas; table and column design is designing-postgresql-schemas."
---

# Optimizing PostgreSQL Queries

A slow query is fixed by evidence, not by adding indexes until it improves. Measure
which queries cost the most time, read their actual plans, change one thing, and
measure again.

## Version Baseline

PostgreSQL 14 to 18; 14 reached end of life in November 2026. Plans and features
differ by version (18 adds skip scan on multicolumn B-tree indexes and shows buffer
counts by default in `EXPLAIN ANALYZE`). Check `SELECT version();` before reasoning
about a plan. Below 14, stop and say the project is on an unsupported version;
continue only when asked.

**PostgreSQL only.** If the project's database is MySQL, MariaDB, SQL Server or
another engine, say this skill does not apply and stop: plan output, index types and statistics views differ by engine. When a skill for that engine is available in this session, load it instead; name none that is absent.

## Applicability and Precedence

Read how the project issues queries first: ORM, query builder or raw SQL, and where
query logging and metrics already exist. The ORM's own skill owns how to express the
fix in that ORM; this skill owns what the database does with the SQL. An existing
indexing or performance convention in the project outranks this skill.

This skill does not change server configuration or run anything that writes to a
shared or production database. `EXPLAIN ANALYZE` executes the statement: on
production, run it only for `SELECT`, and only when the person responsible agrees.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Start from measured time: `pg_stat_statements`, the slow-query log, APM traces or a timed reproduction. A query that is slow once is not the one to optimise if another runs 10,000 times a minute. |
| MUST | Read the actual plan with `EXPLAIN (ANALYZE, BUFFERS)` on realistic data before proposing a fix. A plan on an empty development database proves nothing. |
| MUST | Compare estimated and actual rows at every node. An estimate off by 10x or more is the first thing to explain. |
| MUST | Measure again after the change and report before and after numbers. |
| MUST | Justify every new index with the query it serves and the plan that uses it, and account for its cost on writes. |
| NEVER | Run `EXPLAIN ANALYZE` on an `INSERT`, `UPDATE` or `DELETE` against a shared database. Even rolled back it takes row locks, fires triggers and advances sequences; use a copy, or plain `EXPLAIN`. |
| NEVER | Create an index on a production table outside a migration. Hand the index to `migrating-postgresql-schemas` so it ships `CONCURRENTLY`. |
| NEVER | Turn off planner methods (`enable_seqscan = off`) or add hints as a fix. They are diagnostic tools only. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Finding slow queries](./references/finding-slow-queries.md) | No specific query is known yet, or you need to rank candidates | `pg_stat_statements`, the slow-query log, `auto_explain`, what to read first |
| [Reading query plans](./references/reading-query-plans.md) | A plan is in front of you, every time | Node types, estimates versus actuals, buffers, loops, the usual culprits |
| [Choosing indexes](./references/choosing-indexes.md) | An index is proposed or a scan should use one | B-tree column order, partial, covering, expression, GIN, BRIN, unused and duplicate indexes |
| [Query anti-patterns](./references/query-anti-patterns.md) | The plan is reasonable but the query shape is wrong | N+1, OFFSET pagination, functions on columns, OR, implicit casts, `count(*)`, `SELECT *` |

Read [reading-query-plans.md](./references/reading-query-plans.md) before explaining
any plan.

## Procedure

1. **Find the query.** From the report or with
   [finding-slow-queries.md](./references/finding-slow-queries.md): its SQL with real
   parameter values, how often it runs, and its total and mean time.
2. **Reproduce the plan** on data of production size and shape:
   `EXPLAIN (ANALYZE, BUFFERS)` (on 18, `BUFFERS` is included by default). If only
   production has such data, use plain `EXPLAIN` there and say the plan is estimated.
3. **Locate the cost** with [reading-query-plans.md](./references/reading-query-plans.md):
   the node where actual time accumulates, and any node whose estimate is far off.
4. **Fix the cause, in this order:** stale statistics (`ANALYZE`), a query shape that
   defeats indexes ([query-anti-patterns.md](./references/query-anti-patterns.md)),
   a missing or wrong index ([choosing-indexes.md](./references/choosing-indexes.md)),
   then schema changes. Each later fix costs more to ship and to keep.
5. **Measure again** with the same parameters and data. Keep the change only if the
   number moved.
6. **Ship it.** An index or schema change goes through a migration with
   `migrating-postgresql-schemas`; a query change through the normal code path.

## Reporting

Report the query, how often it runs, the plan node that dominates and why, the
change, and the time before and after. When the database is not the bottleneck
(the time is in the application, the network or the connection pool), say so and stop.
