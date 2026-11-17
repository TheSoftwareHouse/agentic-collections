---
name: optimizing-mysql-queries
description: "Diagnoses slow MySQL and Aurora MySQL queries from evidence: performance_schema statement digests, sys views and the slow query log ranked by total time and rows examined, EXPLAIN access types, key_len and Extra notes such as Using filesort and Using temporary, EXPLAIN ANALYZE actual rows per loop, InnoDB index statistics and histograms, indexes chosen around the clustered primary key, and the query shapes MySQL cannot index: OFFSET pages, keyset conditions written as row constructors, DATE() on a DATETIME, a VARCHAR compared with a number, joins across utf8mb3 and utf8mb4. Use when an endpoint, report or job is slow because of a MySQL query, or someone proposes FORCE INDEX or a new index."
when_to_use: "Trigger on: a slow MySQL endpoint or job, EXPLAIN or EXPLAIN ANALYZE output from MySQL pasted for explanation, type ALL or Using filesort or Using temporary, an index that exists but is not used, deciding which index to add, rows examined far above rows sent, pt-query-digest or Performance Insights top SQL, N+1 queries from Eloquent, Doctrine or TypeORM against MySQL, deep pagination getting slower, a MySQL query that became slow after data grew, or reviewing a change that adds a query to a hot path on MySQL. Shipping the index is migrating-mysql-schemas; table design is designing-mysql-schemas."
---

# Optimizing MySQL Queries

A slow query is fixed by evidence, not by adding indexes until it improves. Measure
which queries cost the most time, read their actual plans, change one thing, and
measure again.

## Version Baseline

MySQL 8.0, 8.4 LTS and 9.7 LTS with InnoDB, including Amazon Aurora MySQL 3
(8.0-compatible) and Aurora MySQL 8.4 (treat as 8.4). Community 8.0 reached end of
life in April 2026; Aurora MySQL 3 has standard support to April 2028. Plan output and optimizer features depend on the
minor: `EXPLAIN FORMAT=TREE` is `8.0.16+`, `EXPLAIN ANALYZE` and hash joins `8.0.18+`.
Run `SELECT VERSION();` before reasoning about a plan. Below 8.0, stop and say the
version is unsupported; continue only when asked.

**MySQL only.** If the database is MariaDB, PostgreSQL, SQL Server or another engine,
say this skill does not apply and stop: plan output, index types, statistics and
instrumentation differ by engine, and MariaDB's optimizer has diverged from MySQL's.
When a skill for that engine is available in this session, load it instead; name
none that is absent.

## Applicability and Precedence

Read how the project issues queries first: ORM, query builder or raw SQL, and where
query logging and metrics already exist. The ORM's own skill owns how to express the
fix in that ORM; this skill owns what the database does with the SQL. An existing
indexing or performance convention in the project outranks this skill.

This skill does not change server configuration or run anything that writes to a
shared or production database. `EXPLAIN ANALYZE` executes the query: on production,
run it only for a `SELECT`, and only when the person responsible agrees.
`ANALYZE TABLE` and `UPDATE HISTOGRAM` write statistics: on a shared or production
server, hand them over like an index, do not run them.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Start from measured time: the `performance_schema` statement digests, the slow query log, APM traces or a timed reproduction. A query that is slow once is not the one to optimise if another runs 10,000 times a minute. |
| MUST | Read the plan with `EXPLAIN ANALYZE` (or `EXPLAIN FORMAT=TREE` where it cannot run) on realistic data before proposing a fix. A plan on an empty development database proves nothing. |
| MUST | Compare estimated and actual rows at every step, and rows examined with rows returned. An estimate off by 10x or more, or a query that examines 1,000 rows per row it returns, is the first thing to explain. |
| MUST | Measure again after the change and report before and after numbers. |
| MUST | When asked to review a whole change or its merge readiness (a pull request or a diff that also changes application code), not only the query, load the general code-review skill too when one is available in this session (`reviewing-code`, for example). This skill covers the query; that one covers the rest of the change. Name none that is absent. |
| MUST | Justify every new index with the query it serves and the plan that uses it, and account for its cost on writes and memory. |
| MUST | Treat `FORCE INDEX`, `USE INDEX` and optimizer hints as a last resort: only after statistics and the query shape are fixed, with a comment naming the plan they prevent. They outlive the data distribution they were written for. |
| NEVER | Run a write (`INSERT`, `UPDATE`, `DELETE`) to measure it against a shared database. Use a copy, or plain `EXPLAIN`, which does not execute. |
| NEVER | Create or drop an index on a production table outside a migration. Hand the index to `migrating-mysql-schemas` so it ships online and with the replica lag accounted for. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Finding slow queries](./references/finding-slow-queries.md) | No specific query is known yet, or you need to rank candidates | Statement digests, `sys` views, the slow query log, managed-service tools, what to read first |
| [Reading query plans](./references/reading-query-plans.md) | A plan is in front of you, every time | `EXPLAIN` columns, access types, `Extra`, tree and `ANALYZE` output, statistics and histograms |
| [Choosing indexes](./references/choosing-indexes.md) | An index is proposed or a scan should use one | The clustered primary key, composite column order, covering, prefix, functional, multi-valued and full-text indexes, unused and redundant indexes |
| [Query anti-patterns](./references/query-anti-patterns.md) | The plan is reasonable but the query shape is wrong | N+1, `OFFSET` and keyset pagination, functions on columns, implicit casts and collations, `OR`, `COUNT(*)`, locking reads |

Read [reading-query-plans.md](./references/reading-query-plans.md) before explaining
any plan.

## Procedure

1. **Find the query.** From the report or with
   [finding-slow-queries.md](./references/finding-slow-queries.md): its SQL with real
   parameter values, how often it runs, its total and mean time, and rows examined
   against rows sent.
2. **Reproduce the plan** on data of production size and shape with `EXPLAIN ANALYZE`.
   If only production has such data, use plain `EXPLAIN` there and say the plan is
   estimated.
3. **Locate the cost** with [reading-query-plans.md](./references/reading-query-plans.md):
   the step where actual time and rows accumulate, and any step whose estimate is far
   off.
4. **Fix the cause, in this order:** stale statistics (`ANALYZE TABLE`, a histogram),
   a query shape that defeats indexes
   ([query-anti-patterns.md](./references/query-anti-patterns.md)), a missing or wrong
   index ([choosing-indexes.md](./references/choosing-indexes.md)), then schema
   changes. Each later fix costs more to ship and to keep.
5. **Measure again** with the same parameters and data. Keep the change only if the
   number moved.
6. **Ship it.** An index or schema change goes through a migration with
   `migrating-mysql-schemas`; a query change through the normal code path.

## Reporting

Report the query, how often it runs, the plan step that dominates and why, the
change, and the time and rows examined before and after. When the database is not
the bottleneck (the time is in the application, the network or the connection pool),
say so and stop.
