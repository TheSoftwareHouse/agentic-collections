# Choosing indexes

Use this reference when an index is proposed, or a scan should be using one. Every
index costs: each write updates it, it competes for the buffer pool, and it is built
online but slowly on a large table. Justify each one with the query it serves.

## How InnoDB stores a table

- The table **is** its primary key: rows are stored in a B-tree ordered by it (the
  clustered index). A lookup by primary key reads the row directly.
- Every secondary index stores the indexed columns **plus the primary key**. A lookup
  through it finds the primary key, then reads the row from the clustered index.
- So a long primary key (a `CHAR(36)` UUID) is copied into every secondary index, and
  a random one scatters inserts across the clustered index. Both are design choices
  for `designing-mysql-schemas`.
- And an index on `(a)` already **covers** `SELECT id FROM t WHERE a = ?`: the
  primary key is in it.

## Composite indexes: column order

An index on `(a, b, c)` serves conditions on `a`, on `a` and `b`, and on all three,
read from the left. It does not serve a condition on `b` alone (except an occasional
skip scan).

Order the columns:

1. **Columns compared with `=`** (or a short `IN` list) first. Among them, order by
   what other queries can share, then by selectivity.
2. **Then one range or sort column.** The lookup stops using the index after the
   first range (`>`, `<`, `BETWEEN`, `LIKE 'x%'`): in `(status, created_at, total)`,
   `WHERE status = ? AND created_at > ? AND total = ?` uses `status` and
   `created_at` for the lookup, and checks `total` in the index without seeking on
   it (`Using index condition`).
3. **For `ORDER BY ... LIMIT`**, the equality columns followed by the sort columns
   in the sort's order lets MySQL read the first rows in order and stop, with no
   sort: `WHERE status = ? ORDER BY created_at DESC LIMIT 20` on
   `(status, created_at)`. Mixed directions (`ORDER BY a ASC, b DESC`) need a
   matching descending index part, supported from 8.0.

Check `key_len` in the plan to see how many columns a lookup actually used.

## Covering indexes

When every column the query reads is in the index (plus the primary key, which is
always there), MySQL never reads the table: `Using index`. For a hot query, adding
one or two selected columns to the end of an index can remove most of its cost.
Each added column widens the index for every write, so cover the queries that run
most, not every query.

## Kinds of index

| Kind | Use for | Notes |
| :-- | :-- | :-- |
| B-tree | Equality, ranges, sorting, prefix `LIKE 'abc%'` | The default and almost always the answer |
| Prefix (`col(20)`) | Long `VARCHAR` or `TEXT` columns that must be indexed | Cannot cover a query or serve `ORDER BY`; pick a length that keeps it selective |
| Functional (`((LOWER(email)))`, `8.0.13+`) | A condition on an expression that cannot be rewritten | The query must use the exact expression. Adding one in a single statement blocks writes; ship it as an indexed `VIRTUAL` column |
| Multi-valued (`8.0.17+`) | Membership in a JSON array: `MEMBER OF`, `JSON_CONTAINS`, `JSON_OVERLAPS` | `INDEX ((CAST(doc->'$.tags' AS CHAR(32) ARRAY)))` |
| `FULLTEXT` | Word search in text | `MATCH ... AGAINST`; its own relevance rules and stopwords. A table with one cannot add or drop columns instantly, and every table rebuild on it is a full copy that blocks writes |
| Unique | Enforcing uniqueness; also an index | Multiple `NULL`s are allowed. Collation decides what counts as equal |

MySQL has **no partial indexes**. Put the condition's column first in a composite
index instead (`(status, created_at)` for queries on open orders). A uniqueness rule
that applies to some rows only has its own pattern, a unique index over a generated
column, owned by `designing-mysql-schemas`.

## When an index is not used

- **Low selectivity.** For a value matching a large share of rows, a scan beats
  thousands of random row lookups, and the optimizer is usually right to scan.
  Covering the query changes that.
- **The query shape hides the column**: a function, a cast, a collation mismatch, an
  `OR`. See [query-anti-patterns.md](./query-anti-patterns.md).
- **The estimate is wrong**: see
  [reading-query-plans.md](./reading-query-plans.md#when-the-estimate-is-wrong).

## Unused and redundant indexes

```sql
SELECT * FROM sys.schema_unused_indexes WHERE object_schema = DATABASE();
SELECT table_name, redundant_index_name, dominant_index_name
FROM sys.schema_redundant_indexes WHERE table_schema = DATABASE();
```

- "Unused" means not used **since the server last started**, and only on this
  server: a replica that serves reports may use what the primary does not. Check the
  uptime and every server that takes reads.
- An index whose columns are a left prefix of another's, `(a)` beside `(a, b)`, is
  usually redundant. Not when it is unique: it then enforces a rule the longer
  index does not.
- Remove one in steps: make it invisible, watch a release, then drop it, each through
  `migrating-mysql-schemas`.

## Limits

At most 64 secondary indexes per table, and 3,072 bytes per index key with the
default `DYNAMIC` row format: a `utf8mb4` `VARCHAR(768)` at most, fully indexed.
