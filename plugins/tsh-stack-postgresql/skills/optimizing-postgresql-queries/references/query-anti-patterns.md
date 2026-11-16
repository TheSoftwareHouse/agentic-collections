# Query anti-patterns

Use this reference when the plan is reasonable for the query as written, but the
query asks the database for the wrong thing. Each pattern below has a shape you can
spot in the SQL and a fix that is usually cheaper than an index.

## Contents

- [N+1](#n1)
- [OFFSET pagination](#offset-pagination)
- [Functions on indexed columns](#functions-on-indexed-columns)
- [OR across columns](#or-across-columns)
- [Implicit casts](#implicit-casts)
- [NOT IN with a subquery](#not-in-with-a-subquery)
- [Exact counts](#exact-counts)
- [Reading more than is used](#reading-more-than-is-used)
- [Long transactions](#long-transactions)

## N+1

One query loads a list, then one query per item loads related rows. Each query is
fast; together they are hundreds of round trips. Signs: the same normalised statement
with a very high `calls` count in `pg_stat_statements`, or a repeated span in an APM
trace.

Fix in the application: load the related rows in one query (`WHERE order_id = ANY($1)`
or a join), using the ORM's eager-loading feature. The ORM's skill says how; the
evidence that it worked is the call count dropping.

## OFFSET pagination

`ORDER BY created_at DESC LIMIT 20 OFFSET 100000` reads and discards 100,000 rows to
return 20. Each page is slower than the last.

Keyset (seek) pagination remembers the last row of the previous page:

```sql
SELECT id, created_at, total
FROM orders
WHERE (created_at, id) < ($1, $2)       -- values from the last row shown
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

with an index on `(created_at, id)`. Every page costs the same. The `id` tie-breaker
makes the order total, so rows with equal `created_at` are neither skipped nor
repeated. It cannot jump to page 500; most interfaces do not need to.

## Functions on indexed columns

`WHERE date(created_at) = '2026-11-13'`, `WHERE lower(email) = $1`,
`WHERE created_at + interval '1 day' > now()`: the function hides the column from its
index, and the planner cannot estimate the selectivity.

Rewrite as a range on the bare column:

```sql
WHERE created_at >= '2026-11-13' AND created_at < '2026-11-14'
WHERE created_at > now() - interval '1 day'
```

When the function is essential (`lower(email)`), index the expression instead
([choosing-indexes.md](./choosing-indexes.md#expression-indexes)).

## OR across columns

`WHERE customer_id = $1 OR referrer_id = $1` often ends in a sequential scan, or a
bitmap OR of two indexes. When it is slow, split it:

```sql
SELECT ... WHERE customer_id = $1
UNION
SELECT ... WHERE referrer_id = $1;
```

Each branch uses its own index. Use `UNION ALL` when the branches cannot overlap.

`OR` on the **same** column (`status = 'a' OR status = 'b'`) is fine; write it as
`status IN ('a', 'b')`.

## Implicit casts

Comparing a column with a value of another type can wrap the column in a cast and
lose the index. The common case is a `numeric` parameter against a `bigint` or
`integer` column (a driver sending a JavaScript number or a decimal type): the plan
shows `Seq Scan ... Filter: ((id)::numeric = $1)`, with the cast on the column side.
Fix the parameter type in the application or cast the parameter, not the column.

## NOT IN with a subquery

`WHERE id NOT IN (SELECT order_id FROM refunds)` returns no rows at all if the
subquery yields a single `NULL`, and plans poorly on large inputs. Use:

```sql
WHERE NOT EXISTS (SELECT 1 FROM refunds r WHERE r.order_id = o.id)
```

## Exact counts

`SELECT count(*) FROM big_table WHERE ...` reads every matching row; PostgreSQL keeps
no row count. For a "1,234,567 results" label:

- show "more than N" by counting up to a cap: `SELECT count(*) FROM (SELECT 1 FROM t WHERE ... LIMIT 1001) s`;
- use the planner's estimate for a whole table: `SELECT reltuples FROM pg_class WHERE oid = 't'::regclass`;
- or keep a counter table maintained by the application.

Whether an approximate number is acceptable is a product decision; ask.

## Reading more than is used

- `SELECT *` fetches every column, including large `text` and `jsonb` stored out of
  line (TOAST), and prevents index-only scans. Select the columns the code uses.
- A missing `LIMIT` on a list endpoint returns everything the filter matches, and
  grows with the data.
- Filtering, sorting or aggregating in application code after fetching all rows
  moves the work to the slowest place to do it.

## Long transactions

A transaction left open (an `idle in transaction` session, a long report, a job that
holds a transaction across HTTP calls) keeps vacuum from removing dead rows anywhere
it could see them. Tables bloat, index-only scans start fetching the heap, and every
query slows a little. Find them with `pg_stat_activity` (`state = 'idle in transaction'`,
old `xact_start`) and fix the code that holds them. `idle_in_transaction_session_timeout`
is the server-side guard; setting it is an infrastructure decision.
