# Finding slow queries

Use this reference when no specific query is known yet, or several candidates need
ranking. The query worth fixing is the one that costs the most total time, which is
often not the slowest single run.

## pg_stat_statements

The extension records every normalised statement with its call count and timings.
It needs `pg_stat_statements` in `shared_preload_libraries` (a server restart) and
`CREATE EXTENSION pg_stat_statements;` in the database. Managed services (RDS, Cloud
SQL, Azure Database for PostgreSQL) ship it; check whether it is enabled before
asking for it.

```sql
-- where the database spends its time
SELECT calls,
       round(total_exec_time)::bigint             AS total_ms,
       round(mean_exec_time::numeric, 1)          AS mean_ms,
       rows / nullif(calls, 0)                     AS rows_per_call,
       round(100.0 * shared_blks_read
             / nullif(shared_blks_hit + shared_blks_read, 0), 1) AS pct_read_from_disk,
       left(query, 120)                            AS query
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY total_exec_time DESC
LIMIT 20;
```

The view covers every database of the server; the `WHERE` keeps this one. Read it as:

- **Top by `total_ms`:** where the time goes. Fix these first.
- **High `calls` with small `mean_ms`:** a loop. Look for N+1 in the application
  rather than at the query ([query-anti-patterns.md](./query-anti-patterns.md#n1)).
- **High `rows_per_call`:** the query returns more than anything displays. Look for
  missing `LIMIT`, `SELECT *` or filtering in the application.
- **High `pct_read_from_disk`:** the working set does not fit in memory, or the query
  reads far more than it needs.

Timing columns are `total_exec_time` and `mean_exec_time` on 13 and later. Statistics
accumulate since the last `pg_stat_statements_reset()`, so compare snapshots, or reset
before a measured run on a non-shared database.

The normalised text replaces literals with `$1`, `$2`. To get a plan you need real
values: from the application log, the APM trace, or by picking typical values.

## The slow-query log

`log_min_duration_statement = 500` (milliseconds) logs every statement slower than
that with its duration and parameters. It is cheap and catches the long tail that
averages hide. On a managed service it is a parameter-group or flag setting, which
is an infrastructure change: propose it, do not apply it.

## auto_explain

The `auto_explain` module logs the plan of every statement slower than
`auto_explain.log_min_duration`. With `auto_explain.log_analyze = on` it logs actual
row counts and timings too, at a measurable cost on every statement; keep
`log_analyze` for a bounded investigation. It is the way to see the plan production
actually chose, with production's statistics and parameter values.

## From the application side

- **APM traces** (Datadog, New Relic, OpenTelemetry spans) show the query inside the
  request, with its count per request. Ten identical queries in one trace is N+1.
- **ORM query logging** in development shows the SQL the ORM generates. Turn it on
  while reproducing; the SQL is often not what the code suggests.
- **Locks, not queries.** A query that is slow only sometimes may be waiting on a
  lock. `pg_stat_activity.wait_event_type = 'Lock'` while it runs says so, and that
  is a contention problem, not a plan problem.

## Checking the statistics are current

A plan built on stale statistics misestimates rows. After bulk loads or large
deletes, or when a table's estimates are far off:

```sql
SELECT relname, n_live_tup, n_mod_since_analyze, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_mod_since_analyze DESC
LIMIT 20;
```

A large `n_mod_since_analyze` relative to `n_live_tup` means the planner is working
from old numbers. `ANALYZE table_name;` is cheap and safe to run.
