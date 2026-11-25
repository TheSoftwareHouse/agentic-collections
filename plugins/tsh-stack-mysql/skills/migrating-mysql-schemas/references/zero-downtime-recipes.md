# Zero-downtime recipes

Use this reference when a migration adds an index or constraint, or renames, retypes
or drops a column on a table with traffic. Each recipe is a sequence of migrations
and deploys; each migration holds one DDL statement and starts with
`SET SESSION lock_wait_timeout = 5;` (left out below for brevity).

The algorithm each step gets is in [online-ddl-and-locks.md](./online-ddl-and-locks.md).
A step marked **tool** needs an online schema change tool on a large table, from
[online-schema-change-tools.md](./online-schema-change-tools.md), or an agreed
maintenance window on a small one.

## Add a column

```sql
ALTER TABLE orders ADD COLUMN channel VARCHAR(32) NULL, ALGORITHM=INSTANT;
-- or, with a value for existing rows:
ALTER TABLE orders ADD COLUMN channel VARCHAR(32) NOT NULL DEFAULT 'web', ALGORITHM=INSTANT;
```

Instant on any position from 8.0.29 (only as the last column before that). A
`DEFAULT` that should differ per row is a nullable column plus a backfill, not a
default.

## Add an index

```sql
ALTER TABLE orders ADD INDEX orders_customer_id_idx (customer_id), ALGORITHM=INPLACE, LOCK=NONE;
```

Writes continue, but the build takes time proportional to the table, and binlog
replicas replay it afterwards for as long again. On a large table whose replicas
serve reads, use a tool instead. For a unique index, check for duplicates first
(`SELECT k, COUNT(*) FROM t GROUP BY k HAVING COUNT(*) > 1 LIMIT 10`): a duplicate
that exists or arrives during the build fails it at the end, after all the work.

For an index on an expression, add a `VIRTUAL` generated column and index it, in two
migrations; a functional index in one statement blocks writes:

```sql
ALTER TABLE users ADD COLUMN email_lower VARCHAR(255) AS (LOWER(email)) VIRTUAL, ALGORITHM=INSTANT;
ALTER TABLE users ADD INDEX users_email_lower_idx (email_lower), ALGORITHM=INPLACE, LOCK=NONE;
```

## Add a foreign key

With `foreign_key_checks` on, adding a foreign key copies the table. With it off for
the session, it is in place and online, and does **not** check existing rows. So
check them yourself, right before:

```sql
-- 1. must return 0 rows; fix or delete orphans first
SELECT o.id, o.customer_id
FROM orders o LEFT JOIN customers c ON c.id = o.customer_id
WHERE o.customer_id IS NOT NULL AND c.id IS NULL
LIMIT 10;

-- 2. the referencing column needs an index; add it first as above if missing
-- 3. one migration, one session
SET SESSION foreign_key_checks = 0;
ALTER TABLE orders ADD CONSTRAINT orders_customer_fk
  FOREIGN KEY (customer_id) REFERENCES customers (id), ALGORITHM=INPLACE, LOCK=NONE;
SET SESSION foreign_key_checks = 1;
```

The `ALTER` takes the metadata lock on `customers` as well as `orders`, so a long
transaction on either table blocks it, and queues the queries on both. Run the
orphan query again after the migration: a row written between the check and the
`ALTER` is not validated either. New writes after it are. The migration is done only
when that second run returns nothing; if it finds rows, repair them (point them at
an existing parent, null the column, or delete them, as the data owner decides) and
run it again. Never set
`foreign_key_checks` globally. gh-ost cannot migrate tables that have foreign keys,
so a table with one is later limited to native DDL or pt-online-schema-change.

## Make a column NOT NULL

1. Deploy code that always writes the column.
2. Backfill the existing `NULL`s in batches ([backfilling-data.md](./backfilling-data.md))
   and verify `SELECT COUNT(*) FROM t WHERE c IS NULL` is 0.
3. Migrate: `ALTER TABLE t MODIFY c <same type> NOT NULL, ALGORITHM=INPLACE, LOCK=NONE;`

The `MODIFY` must repeat the column's whole definition (type, charset, default,
comment), or those change too. Step 3 also depends on strict mode in the migration's
own session: check `SELECT @@SESSION.sql_mode` includes `STRICT_TRANS_TABLES` (the
default, but a driver or migration tool can override it). Without it the in-place
`ALTER` is refused (`ERROR 1846`), and a `COPY` stores `0` or `''` for each remaining
`NULL` with only a warning. Step 3 rebuilds the table: on a large one it is a tool
step for the replica lag, not for locks. A `NULL` written between steps 2 and 3 fails
it; step 1 prevents that.

## Add a CHECK constraint

There is no online path: adding `CHECK` is copy on every supported version, and
there is no equivalent of PostgreSQL's `NOT VALID`. On a large table, add it through a
tool, which applies the `ALTER` clause to its own copy of the table (confirm with the
tool's dry run that it accepts it), or keep the rule in the application and say so
in the hand-over. Check that no existing row violates it first
(`SELECT COUNT(*) FROM t WHERE NOT (<predicate>)` must be 0): native DDL fails at the
end of the copy, but a tool may silently drop those rows, and gh-ost does unless it
runs with `--panic-on-warnings` (see
[online-schema-change-tools.md](./online-schema-change-tools.md#what-both-need-from-the-migration)).

## Rename a column

Running code reads the old name until the deploy finishes, so the rename itself
(instant on 8.0.28+) breaks it. Expand and contract:

1. Add the new column, nullable and with no default (instant).
2. Deploy code that writes both columns and reads the old one. Confirm every writer
   runs it (workers, scripts, old instances) before step 3; a write to the old
   column alone after its row was backfilled is lost at step 4.
3. Backfill the new column from the old one in batches.
4. Check that the two columns agree on every row
   ([backfilling-data.md](./backfilling-data.md)), then deploy code that reads the new
   column, still writing both.
5. Deploy code that stops writing the old column.
6. Drop the old column in a later release.

When a short window of errors is acceptable, and only then, a single
`RENAME COLUMN` deployed together with code that tolerates both names is simpler;
say which was chosen and why.

## Change a column's type, including INT to BIGINT keys

A type change is copy. Either run it through a tool, or expand and contract:

1. Add the new column with the new type, nullable and with no default (instant).
2. Deploy code that writes both, and confirm every writer runs it.
3. Backfill in batches.
4. Check that the columns agree on every row, then switch reads, then writes, to the
   new column; drop the old one in a later release.

Expand and contract does not work for an `AUTO_INCREMENT` primary key: a table has
one `AUTO_INCREMENT` column and it must be the key, so the new column cannot take
over generating ids. Widen a key in place, through a tool or a window, as below.

An `INT` primary key that is running out (2,147,483,647 signed) is the case that
cannot wait: the table rejects inserts when it is exhausted. Check how close it is:

```sql
SET SESSION information_schema_stats_expiry = 0;  -- the value is cached for a day otherwise
SELECT AUTO_INCREMENT / 2147483647 AS used        -- 4294967295 for INT UNSIGNED
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'orders';
```

Read the counter, not `MAX(id)`: failed and rolled-back inserts,
`INSERT ... ON DUPLICATE KEY UPDATE`, bulk inserts and an explicit `AUTO_INCREMENT=`
consume values without leaving a row, so `MAX(id)` can look empty while the next
insert takes the last value.

When other tables reference the key, the two sides of a foreign key must have the
same type at every moment, even with `foreign_key_checks=0`, so neither side can be
widened first (`ERROR 3780`), and gh-ost refuses tables with foreign keys. The order:

1. Drop the foreign keys that reference the key (in place, `LOCK=NONE`).
2. Widen each referencing column, then the key itself: copy operations, each a tool
   run or a window on a large table.
3. Re-add the foreign keys with the foreign key recipe above, orphan check included.

**Between steps 1 and 3 the database enforces nothing**, and that window lasts as
long as all the copies together: hours or days on large tables. Inserts can
reference missing parents, and `ON DELETE CASCADE` and `SET NULL` stop happening, so
deleting a parent leaves its children behind. Before step 1, deploy code that does
what the foreign keys did (delete or null the children itself, or refuse to delete
parents), keep it until step 3, and treat a non-empty orphan check in step 3 as
data to repair, not to skip. Say this in the hand-over; it is the risk of the
change. Plan it while there is headroom.

## Drop a column

1. Deploy code that no longer reads or writes it. With an ORM, remove it from the
   entity or model first: many select every mapped column.
2. Let that release run long enough that no old instance remains.
3. Migrate: `ALTER TABLE t DROP COLUMN c, ALGORITHM=INSTANT;` (8.0.29+; before that,
   `INPLACE, LOCK=NONE`, which rebuilds). A column that is part of an index is
   refused as `INSTANT` on every version and needs `INPLACE, LOCK=NONE`, a rebuild:
   a tool step on a large table.

Dropping a column is one-way: only a restore brings the data back.

## Drop an index

Make it invisible first, watch the queries it served for a release, then drop it:

```sql
ALTER TABLE orders ALTER INDEX orders_status_idx INVISIBLE, ALGORITHM=INPLACE, LOCK=NONE;
-- later, if nothing got slower:
ALTER TABLE orders DROP INDEX orders_status_idx, ALGORITHM=INPLACE, LOCK=NONE;
```

Making it visible again is a metadata-only change, quick once it has the metadata
lock; rebuilding a dropped index is not. An invisible index is still maintained on
every write, and a unique one still enforces uniqueness.

## Add or change a primary key

Rebuilds the table in place with `LOCK=NONE`. Every secondary index carries the
primary key, so they are all rebuilt too: a tool step on a large table.
