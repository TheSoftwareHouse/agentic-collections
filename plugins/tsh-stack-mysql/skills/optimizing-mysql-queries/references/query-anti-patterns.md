# Query anti-patterns

Use this reference when the plan is reasonable for the query as written, but the
query is shaped so no index can help. Each entry names the shape, how it shows in the
plan, and the rewrite. The plans quoted were produced on MySQL 8.0.46 and 9.7.4.

## N+1 queries

One query for a list, then one more per row (`SELECT * FROM customers WHERE id = ?`
fifty times). Each is fast; together they cost round trips and connection time. In
the digest table they show as a very high call count with a tiny mean.

Fix in the application: fetch the related rows in one query (`WHERE id IN (...)`, a
join, or the ORM's eager loading for that relation), and check the SQL the ORM
actually sends.

## OFFSET pagination

`ORDER BY created_at DESC LIMIT 20 OFFSET 100000` reads and discards 100,000 rows
before returning 20, and every later page is slower.

Use keyset pagination: remember the last row's sort key and continue after it, with
an index on the sort columns, the primary key last to break ties.

**Write the keyset condition out; do not use a row constructor.** On a 200,000-row
table with an index on `(created_at, id)`, fetching 10 rows after a point:

| Condition | Plan | Rows read |
| :-- | :-- | :-- |
| `WHERE (created_at, id) > (?, ?)` | Index scan from the start of the index, then a filter | 172,809 |
| `WHERE created_at > ? OR (created_at = ? AND id > ?)` | Index range scan starting at the point | 10 |

MySQL does not turn the row-constructor comparison into a range, so it reads the
index from the beginning until it finds the page. For descending order, flip the
comparisons and order both columns `DESC`.

## Functions and arithmetic on an indexed column

`WHERE DATE(created_at) = '2026-01-03'`, `WHERE YEAR(created_at) = 2026`,
`WHERE LOWER(email) = ?`, `WHERE amount * 100 > ?` hide the column from its index:
the plan shows a `Filter: (cast(created_at as date) = ...)` over a full scan.

Rewrite as a range on the bare column:
`WHERE created_at >= '2026-01-03' AND created_at < '2026-01-04'`. When the
expression cannot be rewritten (case-insensitive matching under a case-sensitive
collation), index the expression, as an indexed `VIRTUAL` column.

## Implicit type conversion

A string column compared with a number is converted row by row, and the index on it
is not used: `WHERE code = 1` on a `VARCHAR` column scans the table, while
`WHERE code = '1'` is an index lookup. The opposite (a numeric column compared with a
string literal) converts the literal once and is fine. Bind parameters with the
column's type; ORMs and drivers that send every parameter as a string are a common
source, and so is a JavaScript number used for a `VARCHAR` identifier.

## Joining columns with different character sets or collations

A join between a `utf8mb3` and a `utf8mb4` column, or between two collations,
converts one side, and the index on the converted side cannot be used for the
lookup. On 9.7, joining a `utf8mb4` table to a `utf8mb3` one with the filter on the
`utf8mb4` side made the optimizer read all 5,000 rows of the other table instead of
9: it could only use the index in one direction. Make the join columns' character set
and collation identical, a schema change for `designing-mysql-schemas`. Compare with
`SHOW CREATE TABLE`; the table default and the column can differ.

## OR across different columns

`WHERE customer_id = ? OR status = ?` cannot use one index for both. MySQL sometimes
merges two indexes (`Using union(...)` in the plan, type `index_merge`), often it
scans. Rewrite as a `UNION` of two indexed queries (`UNION ALL` when they cannot
overlap) when the plan shows a scan and both conditions are selective.

## Leading wildcards

`LIKE '%smith'` cannot use a B-tree index; `LIKE 'smith%'` can. For word search, use
a `FULLTEXT` index or a search engine; for suffix search, index the reversed string
in a generated column.

## COUNT(*) on a large table

InnoDB keeps no stored row count: `SELECT COUNT(*) FROM t` reads an entire index,
every time. For a total shown in a UI, use an approximate count
(`information_schema.TABLES.TABLE_ROWS` is an estimate, cached), a counter
maintained by the application, or show "more than 1,000" with `LIMIT 1001`. Whether
an approximate number is acceptable is a product decision: ask.

## NOT IN with a subquery that can return NULL

`WHERE id NOT IN (SELECT customer_id FROM orders)` returns no rows at all as soon as
the subquery yields one `NULL`. Use `NOT EXISTS`, which also plans as an anti-join.

## ORDER BY RAND()

Generates a random value for every row and sorts them all. Pick random primary keys
in the application, or sample with a random range of the primary key.

## Large IN lists

Beyond `eq_range_index_dive_limit` (200) values, the optimizer stops estimating
each value from the index and uses averages; on skewed data the plan can flip to a
scan. Batch the list, or join to a temporary table of the values.

## Locking reads without an index

`SELECT ... FOR UPDATE` and `UPDATE`/`DELETE` lock every index record they **scan**,
not only the rows they change, and under `REPEATABLE READ` the gaps between them
too. With no usable index on the `WHERE`, that is the whole table: other writers
wait, and deadlocks multiply. Every locking statement on a hot table needs an index
that narrows its scan to the rows it means.

## SELECT *

Reads every column, including large `TEXT` and `JSON` ones stored off-page, and
rules out a covering index. Select the columns the code uses, at least on hot paths.
