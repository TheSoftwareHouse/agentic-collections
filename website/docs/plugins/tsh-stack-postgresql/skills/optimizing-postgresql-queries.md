---
title: Optimizing PostgreSQL Queries
sidebar_label: optimizing-postgresql-queries
sidebar_position: 2
description: Finds and fixes slow PostgreSQL queries from evidence, from pg_stat_statements and EXPLAIN plans to the index or query change that fixes them.
sources:
  - plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries/
sources_hash: "47f69a8766f1908eb4addc2c500426db94472b807774d855e055466e36463134"
---

# Optimizing PostgreSQL Queries

**Plugin:** [`tsh-stack-postgresql`](/docs/plugins/tsh-stack-postgresql/)  
**Invoke:** `/tsh-stack-postgresql:optimizing-postgresql-queries`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`migrating-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas) and [`designing-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas) point slow-query work at it. The `reviewing-code` skill in `tsh-product-engineering` loads whichever stack skill is available in the session for the change under review, but names no plugin.

A slow query is fixed by evidence, not by adding indexes until it improves. The skill measures which queries cost the most time, reads their actual plans, changes one thing and measures again, on PostgreSQL 14 to 18. On another engine such as MySQL, MariaDB or SQL Server, it says it does not apply and stops; below version 14 it stops and says the version is unsupported.

Use it when an endpoint or job is slow because of the database, when a query plan needs explaining, or when someone proposes adding an index. The ORM's own skill owns how to express the fix in that ORM; this skill owns what the database does with the SQL. It changes no server configuration and writes nothing to a shared or production database, and it runs `EXPLAIN ANALYZE` on production only for a `SELECT` and only with the agreement of the person responsible.

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Finding slow queries** | `pg_stat_statements` ranked by total time, how to read call counts, rows per call and disk reads, the slow-query log, `auto_explain`, APM traces, and checking that statistics are current |
| **Reading query plans** | `EXPLAIN (ANALYZE, BUFFERS, SETTINGS)`, every field of a plan line, estimates against actuals and their causes (stale statistics, correlated columns, skew, generic plans), node types and when each is suspicious, and the usual culprits |
| **Choosing indexes** | B-tree composite column order (and skip scan on 18), partial, covering and expression indexes, GIN, GiST and BRIN, what an index costs on writes, and finding unused or duplicate indexes |
| **Query anti-patterns** | N+1, `OFFSET` pagination and keyset pagination, functions on indexed columns, `OR` across columns, implicit casts, `NOT IN` with a subquery, exact counts, reading more than is used, and long transactions |

## How it works

1. **Find the query**, with real parameter values, how often it runs and its total and mean time.
2. **Reproduce the plan** with `EXPLAIN (ANALYZE, BUFFERS)` on data of production size and shape.
3. **Locate the cost:** the node where actual time accumulates, and any node whose estimate is far off.
4. **Fix the cause, cheapest first:** statistics, then the query's shape, then an index, then the schema.
5. **Measure again** with the same parameters and data, and keep the change only if the number moved.
6. **Ship it:** an index or schema change through a migration, a query change through the normal code path.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Start from measured time, not from the query that happens to be noticed |
| MUST | Read the actual plan on realistic data before proposing a fix, and compare estimated and actual rows at every node |
| MUST | Measure again after the change and report before and after numbers |
| MUST | Justify every new index with the query it serves and the plan that uses it, and account for its cost on writes |
| NEVER | Run `EXPLAIN ANALYZE` on a data-changing statement against a shared database, because even rolled back it takes row locks, fires triggers and advances sequences |
| NEVER | Create an index on a production table outside a migration, or use planner switches and hints as a fix |

## References

| Reference | Load when |
| :-- | :-- |
| Finding slow queries | No specific query is known yet, or candidates need ranking |
| Reading query plans | A plan is in front of you, every time |
| Choosing indexes | An index is proposed or a scan should use one |
| Query anti-patterns | The plan is reasonable but the query shape is wrong |

## Related skills

- [`migrating-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/migrating-postgresql-schemas) ships the index or schema change this skill recommends.
- [`designing-postgresql-schemas`](/docs/plugins/tsh-stack-postgresql/skills/designing-postgresql-schemas) owns table and column design.

## Source

[`plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-postgresql/skills/optimizing-postgresql-queries/SKILL.md)
