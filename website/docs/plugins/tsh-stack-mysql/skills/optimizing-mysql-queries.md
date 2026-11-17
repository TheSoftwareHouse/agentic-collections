---
title: Optimizing MySQL Queries
sidebar_label: optimizing-mysql-queries
sidebar_position: 2
description: Finds and fixes slow MySQL queries from evidence, from performance_schema digests and EXPLAIN ANALYZE to the index or query change that fixes them.
sources:
  - plugins/tsh-stack-mysql/skills/optimizing-mysql-queries/
sources_hash: "d25353cbbff96566b68106668c062dfff14eb557f615fa2ca418201fba78c03e"
---

# Optimizing MySQL Queries

**Plugin:** [`tsh-stack-mysql`](/docs/plugins/tsh-stack-mysql/)  
**Invoke:** `/tsh-stack-mysql:optimizing-mysql-queries`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`migrating-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/migrating-mysql-schemas) and [`designing-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/designing-mysql-schemas) point slow-query work at it. The `reviewing-code` skill in `tsh-product-engineering` loads whichever stack skill is available in the session for the change under review, but names no plugin.

A slow query is fixed by evidence, not by adding indexes until it improves. The skill measures which queries cost the most time, reads their actual plans, changes one thing and measures again, on MySQL 8.0, 8.4 and 9.7, Aurora MySQL 3 and Aurora MySQL 8.4 included. On MariaDB or another engine it says it does not apply and stops; below 8.0 it stops and says the version is unsupported.

Use it when an endpoint or job is slow because of a MySQL query, when a plan needs explaining, or when someone proposes adding an index. The ORM's own skill owns how to express the fix in that ORM; this skill owns what the database does with the SQL. It changes no server configuration and writes nothing to a shared or production database, and it runs `EXPLAIN ANALYZE`, which executes the query, on production only for a `SELECT` and only with the agreement of the person responsible.

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Finding slow queries** | `performance_schema` statement digests ranked by total time, rows examined against rows sent, the `sys` views, the slow query log and `pt-query-digest`, managed-service tools, APM traces |
| **Reading query plans** | The three `EXPLAIN` formats and which one 9.7 prints by default, every column of the table format and its `Extra` notes, `EXPLAIN ANALYZE` estimates against actuals per loop, statistics sampling, histograms, index dives and the optimizer trace |
| **Choosing indexes** | The clustered primary key and what it means for secondary indexes, composite column order, covering indexes, prefix, functional, multi-valued and full-text indexes, no partial indexes, unused and redundant indexes |
| **Query anti-patterns** | N+1, `OFFSET` pagination and keyset pagination written out rather than as a row constructor (measured: 172,809 rows read against 10), functions on columns, implicit casts, character-set and collation mismatches in joins, `OR`, `COUNT(*)`, large `IN` lists, locking reads without an index |

## How it works

1. **Find the query**, with real parameter values, how often it runs, its total and mean time, and rows examined per row sent.
2. **Reproduce the plan** with `EXPLAIN ANALYZE` on data of production size and shape.
3. **Locate the cost:** the step where actual time and rows accumulate, and any step whose estimate is far off.
4. **Fix the cause, cheapest first:** statistics, then the query's shape, then an index, then the schema.
5. **Measure again** with the same parameters and data, and keep the change only if the number moved.
6. **Ship it:** an index or schema change through a migration, a query change through the normal code path.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Start from measured time, not from the query that happens to be noticed |
| MUST | Read the plan on realistic data before proposing a fix, and compare estimated and actual rows, and rows examined with rows returned |
| MUST | Measure again after the change and report before and after numbers |
| MUST | Justify every new index with the query it serves and the plan that uses it, and account for its cost on writes and memory |
| MUST | Treat `FORCE INDEX` and optimizer hints as a last resort, with a comment naming the plan they prevent |
| MUST | When asked to review a whole change or its merge readiness, not only the query, load the general code-review skill too when one is available |
| NEVER | Run a write against a shared database to measure it |
| NEVER | Create or drop an index on a production table outside a migration |

## References

| Reference | Load when |
| :-- | :-- |
| Finding slow queries | No specific query is known yet, or candidates need ranking |
| Reading query plans | A plan is in front of you, every time |
| Choosing indexes | An index is proposed or a scan should use one |
| Query anti-patterns | The plan is reasonable but the query shape is wrong |

## Related skills

- [`migrating-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/migrating-mysql-schemas) ships the index or schema change this skill recommends.
- [`designing-mysql-schemas`](/docs/plugins/tsh-stack-mysql/skills/designing-mysql-schemas) owns table and column design, including character sets and collations.

## Source

[`plugins/tsh-stack-mysql/skills/optimizing-mysql-queries/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-mysql/skills/optimizing-mysql-queries/SKILL.md)
