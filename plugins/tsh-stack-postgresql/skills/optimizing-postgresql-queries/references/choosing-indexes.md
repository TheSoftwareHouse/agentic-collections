# Choosing indexes

Use this reference when an index is proposed, or a scan should use one and does not.
An index is chosen for a query, from its plan. Every index also costs every write to
the table, so the case for one includes that cost.

## Contents

- [B-tree, the default](#b-tree-the-default)
- [Composite column order](#composite-column-order)
- [Partial indexes](#partial-indexes)
- [Covering indexes and index-only scans](#covering-indexes-and-index-only-scans)
- [Expression indexes](#expression-indexes)
- [GIN, GiST and BRIN](#gin-gist-and-brin)
- [What an index costs](#what-an-index-costs)
- [Unused and duplicate indexes](#unused-and-duplicate-indexes)

## B-tree, the default

`CREATE INDEX` builds a B-tree. It serves `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`,
`IN`, `IS NULL`, `ORDER BY` and prefix `LIKE 'abc%'` (the last only with the `C`
collation or a `text_pattern_ops` index).

PostgreSQL indexes primary keys and unique constraints automatically. It does **not**
index the referencing side of a foreign key; add that index whenever the parent row
is deleted or its key updated, or when the child is joined or filtered by it.

## Composite column order

For an index on `(a, b, c)`:

- **Equality columns first, then the range or sort column.** For
  `WHERE tenant_id = $1 AND status = $2 AND created_at > $3 ORDER BY created_at`,
  index `(tenant_id, status, created_at)`. The scan goes straight to the matching
  range and returns rows already ordered.
- **A leading column must be constrained** for the index to narrow the scan. A query
  on `b` alone cannot use `(a, b)` efficiently on 17 and earlier. On 18, B-tree skip
  scan can use it when `a` has few distinct values; check the plan rather than
  assuming it.
- **Sort direction matters only for mixed orders.** `ORDER BY a ASC, b DESC` needs an
  index on `(a ASC, b DESC)`; a single direction is read either way.
- **One composite index often replaces several single-column ones.** The planner can
  combine single-column indexes with a bitmap `AND`, but a matching composite index is
  usually much cheaper.

## Partial indexes

```sql
CREATE INDEX CONCURRENTLY orders_pending_created_at_idx
  ON orders (created_at) WHERE status = 'pending';
```

Indexes only the rows the hot query reads. It is smaller and cheaper to maintain, and
the right choice when queries always filter on one value of a skewed column (open
orders, unprocessed jobs, `deleted_at IS NULL`). The query's `WHERE` must imply the
index predicate, written the same way, or the planner will not use it. With a
parameter (`status = $1`) the planner uses the index while it plans with the bound
value, which is the normal case. Under a generic plan (`plan_cache_mode =
force_generic_plan`, or when the planner switches to one) it cannot prove the
parameter matches and falls back to another path. Check the plan the application
gets, not only the one from `psql` with a literal.

A partial unique index enforces uniqueness on a subset:
`CREATE UNIQUE INDEX ... ON users (email) WHERE deleted_at IS NULL`.

## Covering indexes and index-only scans

```sql
CREATE INDEX CONCURRENTLY orders_customer_id_idx
  ON orders (customer_id) INCLUDE (status, total);
```

`INCLUDE` columns are stored in the index but not searched. A query that reads only
`customer_id`, `status` and `total` is answered from the index alone. It only pays
off when the visibility map is current: `Heap Fetches` in the plan should be near
zero, which depends on vacuum keeping up.

## Expression indexes

`WHERE lower(email) = $1` cannot use an index on `email`. Either index the expression:

```sql
CREATE UNIQUE INDEX CONCURRENTLY users_lower_email_idx ON users (lower(email));
```

or store the normalised value (a `citext` column, or a generated column). The query
must use exactly the indexed expression.

## GIN, GiST and BRIN

| Index | Use for | Note |
| :-- | :-- | :-- |
| GIN on `jsonb` | `@>` containment, `?` key existence | default `jsonb_ops` supports more operators; `jsonb_path_ops` is smaller and supports `@>` and jsonpath matches only |
| GIN on arrays | `@>`, `&&`, `= ANY` rewritten as `@>` | |
| GIN on `tsvector` | full-text search with `@@` | store the `tsvector` as a generated column declared `STORED`: on 18 the default is `VIRTUAL`, which cannot be indexed |
| GIN with `pg_trgm` (`gin_trgm_ops`) | `LIKE '%term%'`, `ILIKE`, similarity | needs the `pg_trgm` extension |
| GiST | ranges, exclusion constraints, geometry (PostGIS), nearest-neighbour | |
| BRIN | very large tables whose rows are physically ordered by the column, such as an append-only `created_at` | tiny, but only useful when the correlation holds |

GIN indexes are expensive to update. On write-heavy tables, check the write cost
(see below) and the `fastupdate` behaviour before adding one.

## What an index costs

- **Every insert writes to every index**, and so does every update that changes an
  indexed column.
- **Updates lose HOT.** An update that changes no indexed column can be a heap-only
  tuple update, which writes no index at all. Indexing a frequently updated column
  (a `status`, an `updated_at`) turns every such update into index writes too.
- **Disk and cache.** Indexes compete with table data for memory.
- **Build and maintenance.** Each index is another `CREATE INDEX CONCURRENTLY` to ship
  and another object to bloat.

So: an index for the hot query, yes; an index on every column "in case", no.

## Unused and duplicate indexes

```sql
SELECT s.relname AS table_name, s.indexrelname AS index_name,
       s.idx_scan, pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0
  AND NOT i.indisunique
  AND NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conindid = s.indexrelid)
ORDER BY pg_relation_size(s.indexrelid) DESC;
```

Before proposing to drop one:

- `idx_scan` counts since the last statistics reset, and **per server**: an index
  unused on the primary may serve every query on a read replica. Check each.
- An index may serve a monthly job that has not run since the reset.
- Indexes backing constraints (unique, primary key, exclusion) are excluded above.
- **An index on a foreign key's referencing column often shows `idx_scan = 0`** and is
  still needed: dropping it makes the next delete of a parent row scan the child
  table.

An index on `(a)` next to one on `(a, b)` is usually redundant: the composite serves
queries on `a` alone. Not always: the single-column one is smaller, and a unique
index on `(a)` enforces something the composite does not.

Dropping goes through a migration (`DROP INDEX CONCURRENTLY`).
