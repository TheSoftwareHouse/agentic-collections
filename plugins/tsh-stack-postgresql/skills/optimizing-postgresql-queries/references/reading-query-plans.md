# Reading query plans

Use this reference whenever a plan is in front of you. Read it from the innermost
nodes outwards, and look for the node where actual time accumulates.

## Getting a plan worth reading

```sql
EXPLAIN (ANALYZE, BUFFERS, SETTINGS) SELECT ...;
```

- `ANALYZE` **runs the statement** and reports actual rows, loops and time per node.
  Without it every number is an estimate.
- `BUFFERS` reports pages read from cache (`shared hit`) and from disk or the OS
  (`shared read`). On 18 it is included with `ANALYZE` by default.
- `SETTINGS` lists planner settings that differ from the defaults, which explains
  plans that differ between environments.
- For a data-changing statement on a non-shared database:
  `BEGIN; EXPLAIN (ANALYZE, BUFFERS) UPDATE ...; ROLLBACK;`. The rollback undoes the
  rows, not the row locks held meanwhile, the triggers fired or the sequence values used.
- Run it twice. The first run may read from disk what the second finds in cache; say
  which one you report.

Data shape decides the plan. A plan from a development database with 200 rows says
nothing about production with 20 million.

## The line that matters

```text
Index Scan using orders_customer_id_idx on orders  (cost=0.43..812.10 rows=210 width=96)
                                                   (actual time=0.03..41.20 rows=19840 loops=1)
  Buffers: shared hit=1204 read=18611
```

| Field | Meaning |
| :-- | :-- |
| `cost=a..b` | planner's estimate in arbitrary units: startup..total. Compare costs only within one plan. |
| `rows=` (first) | estimated rows per loop |
| `actual time=a..b` | milliseconds to the first row and to the last row, **per loop** |
| `rows=` (actual) | actual rows per loop |
| `loops=` | how many times the node ran. Total time is roughly `actual time × loops`. |
| `Buffers: shared hit / read` | 8 kB pages from cache / not from cache |

The example estimated 210 rows and got 19,840: the plan was chosen for a different
query than the one that ran. That is the finding, before anything about indexes.

On 18 the output changes slightly: actual rows are printed with decimals
(`rows=9.00`, an average over loops), index scans add an `Index Searches` line, and
buffer counts, including those of planning, appear without asking for `BUFFERS`.

## Estimates versus actuals

A factor of 10 or more between estimated and actual rows means the planner chose
blind. Causes, in order of likelihood:

1. **Stale statistics.** `ANALYZE` the table and re-run.
2. **Correlated columns.** `WHERE country = 'PL' AND city = 'Warsaw'` multiplies two
   selectivities as if independent. `CREATE STATISTICS ... (dependencies) ON country, city FROM t;`
   then `ANALYZE` teaches the planner the correlation.
3. **Skewed values** beyond the default 100 most-common values:
   `ALTER TABLE t ALTER COLUMN c SET STATISTICS 1000;` then `ANALYZE`.
4. **Expressions and functions** in `WHERE` that the planner cannot estimate: see
   [query-anti-patterns.md](./query-anti-patterns.md#functions-on-indexed-columns).
5. **Generic plans for prepared statements.** After five executions a prepared
   statement may switch to a plan built without parameter values. A query fast in
   `psql` and slow from the application is often this. `plan_cache_mode` controls it.

## Node types

| Node | Means | Suspicious when |
| :-- | :-- | :-- |
| `Seq Scan` | reads the whole table | the table is large and the filter keeps few rows (`Rows Removed by Filter` is large) |
| `Index Scan` | walks an index, then fetches each row | many rows with high `read` buffers: random I/O |
| `Index Only Scan` | answers from the index alone | `Heap Fetches` is high: the visibility map is stale, vacuum is behind |
| `Bitmap Index Scan` + `Bitmap Heap Scan` | collects matching row locations, reads them in page order | `Recheck Cond` removes many rows, or `lossy` blocks appear (`work_mem` too small for the bitmap) |
| `Nested Loop` | for each outer row, runs the inner side | the inner side runs thousands of loops, each with a scan |
| `Hash Join` | builds a hash of one side | `Batches` above 1: the hash spilled to disk |
| `Merge Join` | merges two sorted inputs | an explicit `Sort` feeds it on a large input |
| `Sort` | sorts rows | `Sort Method: external merge  Disk:` spilled; or the sort serves an `ORDER BY ... LIMIT` an index could provide |
| `Aggregate` / `HashAggregate` | groups rows | spills to disk (`Disk Usage`) |
| `Memoize` | caches inner results of a nested loop | rarely a problem; low hit ratio wastes memory |
| `Gather` | collects parallel workers | `Workers Launched` lower than planned: the server is out of worker slots |

A `Seq Scan` is not a bug in itself. Reading a whole small table, or most of a large
one, is cheaper sequentially than through an index.

## The usual culprits

- **A nested loop with a large inner loop count.** `loops=50000` on an index scan,
  each fast, adds up to the whole query time. Usually a misestimate on the outer side
  made the planner expect few rows.
- **A filter applied after the scan.** `Rows Removed by Filter: 4,000,000` under a
  `Seq Scan` or an `Index Scan` means the index (if any) does not cover the filter.
- **Sort for `ORDER BY ... LIMIT`.** Sorting a million rows to return 20 is fixed by
  an index in the order of the `ORDER BY`, so the scan can stop after 20 rows.
- **Spills to disk.** Hash, sort or aggregate nodes using disk point at `work_mem`
  for this query or at reading more rows than needed. Raising `work_mem` globally is
  a server change; `SET LOCAL work_mem` in one transaction is a targeted test.
- **High `read` buffers on a repeated query.** The data is not staying in cache.
  Either the query reads far more pages than its result needs (fix the access path)
  or the working set exceeds memory (infrastructure).
- **Planning time larger than execution time.** Many partitions or many joins. Shown
  as `Planning Time` at the end of the output.

## Tools

Plain text is the source of truth. For long plans, a visualiser such as
explain.dalibo.com helps reading, but **do not paste a production plan into a public
tool** without the owner's agreement: plans contain table names, literal values and
sometimes data.
