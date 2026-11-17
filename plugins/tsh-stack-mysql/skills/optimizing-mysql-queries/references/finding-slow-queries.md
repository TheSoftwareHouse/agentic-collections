# Finding slow queries

Use this reference when no specific query is known yet, or several candidates need
ranking. The goal is the query that costs the most total time, not the one that is
slowest once.

## Statement digests

`performance_schema` is on by default and groups statements by their normalized
text (a digest, with literals replaced by `?`). Rank by total time:

```sql
SELECT LEFT(DIGEST_TEXT, 120)               AS query,
       COUNT_STAR                           AS calls,
       ROUND(SUM_TIMER_WAIT / 1e12, 1)      AS total_s,
       ROUND(AVG_TIMER_WAIT / 1e9, 2)       AS mean_ms,
       ROUND(QUANTILE_95 / 1e9, 2)          AS p95_ms,
       SUM_ROWS_EXAMINED                    AS rows_examined,
       SUM_ROWS_SENT                        AS rows_sent,
       SUM_NO_INDEX_USED                    AS no_index_used,
       SUM_CREATED_TMP_DISK_TABLES          AS tmp_disk_tables,
       QUERY_SAMPLE_TEXT                    AS sample
FROM performance_schema.events_statements_summary_by_digest
WHERE SCHEMA_NAME = DATABASE()
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 20;
```

Timers are in picoseconds, hence the divisions. Read, in order:

- **`total_s`**: where the database spends its time. Optimise from the top.
- **`calls` with a low `mean_ms`**: a cheap query run very often, usually an N+1
  loop in the application. The fix is in the code, not the index.
- **`rows_examined` far above `rows_sent`**: the query reads many rows to return
  few, the clearest sign of a missing or unusable index.
- **`no_index_used`** and **`tmp_disk_tables`**: full scans, and sorts or groupings
  that spilled to disk.
- **`sample`**: one real statement with its literals, ready for `EXPLAIN`.

The `sys` schema has the same data formatted: `sys.statement_analysis`,
`sys.statements_with_full_table_scans`, `sys.statements_with_sorting` and
`sys.statements_with_temp_tables`.

Caveats:

- The table holds a limited number of digests (`performance_schema_digests_size`,
  10,000 by default) and is emptied on restart. Note the uptime
  (`SHOW GLOBAL STATUS LIKE 'Uptime'`) so a total is read against its window.
- Time spent **waiting** counts. A statement queued behind a metadata or row lock
  shows a high time with few rows examined; look for lock waits before indexes.
- Emptying it (`TRUNCATE TABLE performance_schema.events_statements_summary_by_digest`)
  to measure a window resets it for everyone. Ask first on a shared server.

## The slow query log

Logs each statement slower than `long_query_time` (10 s by default). Useful when
digests are not available or the full statement text is needed. Settings that
matter, changed by whoever owns the server:

- `slow_query_log = ON` and a `long_query_time` that catches the queries in question
  (0.5 to 1 s is common for web traffic);
- `log_slow_extra = ON` (8.0.14+) adds rows examined, sort and temporary-table
  details to each entry.

Summarise a log with `pt-query-digest slow.log`, which ranks by total time like the
digest table does.

## Managed services

On Amazon RDS and Aurora, Performance Insights (and CloudWatch Database Insights)
shows the top statements by load, and the slow query log can be published to
CloudWatch Logs. On Google Cloud SQL, Query Insights; on Azure Database for MySQL,
Query Performance Insight. These read the same `performance_schema` data; use
whichever the team already watches.

## Application side

APM traces (Datadog, New Relic, OpenTelemetry) tie a query to the endpoint that
issues it and show how many times one request runs it, which the database cannot
see. An ORM's query log in development shows the SQL an endpoint actually sends.

## What to hand to the next step

For each candidate: the SQL with real parameter values, calls per minute, total and
mean time, and rows examined per row sent. Then read its plan with
[reading-query-plans.md](./reading-query-plans.md).
