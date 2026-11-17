# Reading query plans

Use this reference whenever a plan is in front of you. MySQL prints plans in three
formats; read the one that answers the question.

| Command | Executes the query | Shows | Version |
| :-- | :-- | :-- | :-- |
| `EXPLAIN FORMAT=TRADITIONAL` | No | One row per table: access type, index, estimated rows, `Extra` | all |
| `EXPLAIN FORMAT=TREE` | No | The iterator tree with estimated cost and rows per step | `8.0.16+` |
| `EXPLAIN ANALYZE` | **Yes** | The tree with actual time, rows and loops per step | `8.0.18+` |

Plain `EXPLAIN` uses the server's `explain_format`: the table on 8.0 and 8.4, the
**tree on 9.7**. Name the format when asking someone to paste a plan.
`EXPLAIN ANALYZE` runs the query in full and discards the rows; for a single-table
`UPDATE` or `DELETE` it prints `<not executable by iterator executor>` and does
nothing, so writes are read with plain `EXPLAIN`.

## The table format, column by column

```text
| table | type   | key               | key_len | ref             | rows  | filtered | Extra               |
| o     | ref    | od_status_created | 42      | const           | 99830 |   100.00 | Backward index scan |
| c     | eq_ref | PRIMARY           | 4       | t.o.customer_id |     1 |   100.00 | NULL                |
```

- **Rows in order** are the join order: the first table is read, and for each of its
  rows the next is looked up.
- **`type`**, best to worst: `const` (one row by primary or unique key), `eq_ref`
  (one row per outer row by a unique key), `ref` (all rows matching one value of a
  non-unique index), `range` (an index range), `index` (the **whole index**, in
  order), `ALL` (the **whole table**). `index` and `ALL` on a large table are the
  first suspects.
- **`key`** is the index used; `possible_keys` the ones considered. A `NULL` key with
  candidates listed means the optimizer judged them worse than a scan: check the
  estimate.
- **`key_len`** is how many bytes of the index the lookup uses, which shows how many
  columns of a composite index it reaches. Above, 42 is `status VARCHAR(10)` in
  `utf8mb4` (40 bytes plus a 2-byte length; nullable columns add 1 byte); a query
  that also used `created_at DATETIME` would show 47.
- **`rows`** is the estimate of rows read per lookup, and **`filtered`** the share
  expected to survive the `WHERE`. Rows read for a table is roughly the product of
  `rows` down the join order.
- **`Extra`** carries most of the diagnosis:

| Extra | Meaning |
| :-- | :-- |
| `Using index` | Covering: answered from the index alone, no row lookups |
| `Using index condition` | Index condition pushdown: parts of the `WHERE` checked in the index before fetching rows |
| `Using where` | Rows filtered after they were read; fine on a few, a cost on many |
| `Using filesort` | A sort the index order did not provide. Cheap on a few rows, expensive on many |
| `Using temporary` | An internal temporary table, usually for `GROUP BY`, `DISTINCT` or a `UNION`; it can spill to disk |
| `Backward index scan` | The index read in reverse for `ORDER BY ... DESC`; normal |
| `Using join buffer (hash join)` | A hash join (`8.0.18+`): no index on the join column, the inner table is read once into memory |
| `Using index for skip scan` | The first column of a composite index is skipped (`8.0.13+`); works only in narrow cases |
| `Impossible WHERE` | The condition can never be true; often a type or literal mistake |

## The tree and EXPLAIN ANALYZE

```text
-> Limit: 20 row(s)  (cost=45380 rows=20) (actual time=0.696..0.712 rows=20 loops=1)
    -> Nested loop inner join  (cost=45380 rows=99830) (actual time=0.693..0.708 rows=20 loops=1)
        -> Index lookup on o using od_status_created (status = 'new') (reverse)  (cost=10440 rows=99830) (actual time=... rows=20 loops=1)
        -> Single-row index lookup on c using PRIMARY (id = o.customer_id)  (cost=0.25 rows=1) (actual time=... rows=1 loops=20)
```

- Read from the innermost, most indented step outwards; the top step produces the
  result.
- `(cost=... rows=...)` is the estimate; `(actual time=first..last rows=N loops=L)`
  what happened. Time is in milliseconds **per loop**, and `rows` is the average per
  loop: total rows from a step is `rows × loops`, total time about `last × loops`.
- **Compare estimated and actual rows at every step.** Here the estimate for `o` is
  99,830 rows, but `LIMIT 20` stopped after 20: the index order matched the
  `ORDER BY`, so the plan is good despite the large estimate. A step that estimates
  10 rows and reads 170,000 is the one to explain.
- The step where `actual time` jumps is where the cost is. A step with high `loops`
  multiplies everything beneath it.
- `Filter:` above a scan is the `WHERE` applied after reading: compare rows going in
  with rows coming out.

## When the estimate is wrong

InnoDB estimates from sampled index pages and **index dives**:

- **Stale or coarse statistics.** Persistent statistics sample 20 pages by default
  (`innodb_stats_persistent_sample_pages`) and refresh after about 10% of the rows
  change. On skewed data that misses. `ANALYZE TABLE t` refreshes them quickly; on
  8.0 before 8.0.24 it could make new queries wait behind a running long query on
  that table, so run it outside the busiest hour there.
- **Columns without an index have no statistics** beyond defaults. A filter on one
  is guessed (often 10% or 33%, the `filtered` column shows the guess). A
  **histogram** fixes that without the write cost of an index:
  `ANALYZE TABLE od UPDATE HISTOGRAM ON total WITH 32 BUCKETS;` (`total` has no index). The optimizer uses
  histograms for columns it cannot dive into; it does not use them for a column whose
  index it can dive into.
- **Long `IN` lists.** Up to `eq_range_index_dive_limit` values (200) the optimizer
  dives into the index for each one; beyond that it uses averages, and a skewed
  column is misestimated.
- **Correlated columns.** Estimates multiply selectivities as if columns were
  independent (`country = 'PL' AND city = 'Kraków'`), so they come out too low.

## Why an index was not used

`EXPLAIN` shows the choice, not the reason. The optimizer trace shows the cost of
each alternative, on a copy or with the owner's consent:

```sql
SET optimizer_trace = 'enabled=on';
SELECT ...;   -- the query
SELECT TRACE FROM information_schema.OPTIMIZER_TRACE;
SET optimizer_trace = 'enabled=off';
```

The usual reasons are in [query-anti-patterns.md](./query-anti-patterns.md): a
function or cast on the column, a collation mismatch, an `OR`, a leading wildcard,
or a range on an earlier column of the composite index.
