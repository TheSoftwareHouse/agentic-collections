# Zero-downtime recipes

Use this reference when a migration adds a constraint or index to a populated table,
or renames, retypes or drops a column that running code uses. Each recipe lists the
steps as separate migrations; "deploy" marks where application code ships between
them. Lock names are explained in [lock-levels.md](./lock-levels.md).

## Contents

- [Add a column](#add-a-column)
- [Add an index](#add-an-index)
- [Add NOT NULL to an existing column](#add-not-null-to-an-existing-column)
- [Add a foreign key](#add-a-foreign-key)
- [Add a unique constraint or primary key](#add-a-unique-constraint-or-primary-key)
- [Add a CHECK constraint](#add-a-check-constraint)
- [Rename a column](#rename-a-column)
- [Change a column's type](#change-a-columns-type)
- [Drop a column or table](#drop-a-column-or-table)
- [Add or remove an enum value](#add-or-remove-an-enum-value)

## Add a column

Nullable, or with a constant default: one statement, brief lock, safe as is with
`lock_timeout`. A volatile default (`now()` is stable and fine; `clock_timestamp()`,
`gen_random_uuid()`, `random()` are volatile) rewrites the table. Instead:

1. Add the column nullable, with no default.
2. Set the default: `ALTER TABLE t ALTER COLUMN c SET DEFAULT gen_random_uuid();`
   (affects new rows only, brief).
3. Backfill existing rows in batches ([backfilling-data.md](./backfilling-data.md)).
4. Add `NOT NULL` with the recipe below, if needed.

## Add an index

```sql
-- its own migration, outside a transaction
CREATE INDEX CONCURRENTLY IF NOT EXISTS orders_customer_id_idx ON orders (customer_id);
```

- `CONCURRENTLY` cannot run inside a transaction block. Turn off the migration
  tool's transaction for this migration: [migration-tools.md](./migration-tools.md).
- One concurrent statement per migration. Several in one multi-statement string fail
  on some drivers, and a failure halfway leaves the rest unknown.
- It scans the table twice and waits, between and after the scans, for transactions
  holding older snapshots to finish: long transactions on **any** table of the
  database stall it, not only on this one. Expect it to take longer than a plain
  `CREATE INDEX`, and check for long transactions first.
- **A failed or cancelled build leaves an `INVALID` index** that still slows writes.
  Find and drop it before retrying:

  ```sql
  SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
  DROP INDEX CONCURRENTLY IF EXISTS orders_customer_id_idx;
  ```

  `IF NOT EXISTS` alone would skip the retry and keep the invalid index. The query
  also lists an index that is still being built concurrently and the `ON ONLY` parent
  index of a partitioned table (below), which is invalid by design until every
  partition is attached: drop neither.
- **A failed `UNIQUE` build still enforces uniqueness.** Its invalid index keeps
  rejecting duplicate writes, so drop it promptly.

**Partitioned table.** `CREATE INDEX CONCURRENTLY` on a partitioned parent is not
supported. Create the parent index with `ON ONLY` (it starts invalid), build each
partition's index concurrently, then attach each one; the parent index becomes
valid when every partition has an attached index:

```sql
-- migration 1
CREATE INDEX events_created_at_idx ON ONLY events (created_at);
-- one non-transactional migration per partition
CREATE INDEX CONCURRENTLY events_2026_11_created_at_idx ON events_2026_11 (created_at);
-- after all partitions: one migration
ALTER INDEX events_created_at_idx ATTACH PARTITION events_2026_11_created_at_idx;
```

## Add NOT NULL to an existing column

Backfill the nulls first. Then, on any version from 12:

```sql
ALTER TABLE orders ADD CONSTRAINT orders_status_not_null
  CHECK (status IS NOT NULL) NOT VALID;               -- brief
ALTER TABLE orders VALIDATE CONSTRAINT orders_status_not_null;  -- scan, no blocking
ALTER TABLE orders ALTER COLUMN status SET NOT NULL;   -- brief: the valid CHECK proves it
ALTER TABLE orders DROP CONSTRAINT orders_status_not_null;      -- brief
```

Give each statement its own migration. The `ADD` must be committed before the
`VALIDATE`. `SET NOT NULL` wants `lock_timeout` and `VALIDATE` does not; sharing a
transaction would also repeat the validation scan whenever `SET NOT NULL` times out.

On 18 and later, a not-null constraint can itself be added as `NOT VALID` and
validated without blocking:

```sql
ALTER TABLE orders ADD CONSTRAINT orders_status_not_null NOT NULL status NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT orders_status_not_null;
```

Prefer the `CHECK` recipe when the project might still run on 17 or earlier
anywhere: local Docker images and CI often lag production.

## Add a foreign key

```sql
ALTER TABLE order_lines ADD CONSTRAINT order_lines_order_id_fkey
  FOREIGN KEY (order_id) REFERENCES orders (id) NOT VALID;       -- brief, both tables
ALTER TABLE order_lines VALIDATE CONSTRAINT order_lines_order_id_fkey;  -- scan, no blocking
```

- The `ADD` still takes `SHARE ROW EXCLUSIVE` on **both** tables, so set
  `lock_timeout`. The referenced table is often the busier one.
- Index the referencing column (`order_lines.order_id`), concurrently, in an earlier
  migration. PostgreSQL does not create it, and without it every `DELETE` or key
  `UPDATE` on `orders` scans `order_lines`.
- `NOT VALID` still enforces the constraint on new writes. Rows that violate it make
  `VALIDATE` fail; clean them up first and re-run.

## Add a unique constraint or primary key

```sql
CREATE UNIQUE INDEX CONCURRENTLY users_email_key_idx ON users (email);   -- own migration
ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE USING INDEX users_email_key_idx;
```

The second statement only attaches the existing index, brief. It renames the index to
the constraint name. `USING INDEX` is not supported on partitioned tables. For a primary key, use `PRIMARY KEY USING INDEX`; the columns
must be `NOT NULL` first (recipe above), or the `ADD` scans the table to check them.

Duplicates make the index build fail and leave an invalid index: find them first with
`GROUP BY ... HAVING count(*) > 1`.

## Add a CHECK constraint

`ADD CONSTRAINT ... CHECK (...) NOT VALID`, then `VALIDATE CONSTRAINT` in a separate
migration, as for `NOT NULL` above.

## Rename a column

A rename is brief for the database and immediate breakage for every running instance
of the old code. With rolling deploys, old and new code run together. Expand and
contract:

1. Add the new column (nullable).
2. Deploy code that writes both columns and still reads the old one. A trigger that
   copies old to new is the alternative when not every writer is your code.
3. Backfill the new column from the old one in batches.
4. Deploy code that reads the new column.
5. Deploy code that stops writing the old column; remove the trigger.
6. Drop the old column (see below).

For a small table where a short failure window is acceptable and agreed, the single
`RENAME` is a legitimate choice. Say that it is a choice, not that it is safe.

## Change a column's type

Binary-coercible changes (`varchar(n)` to `text`, to a longer `varchar`) are brief.
Everything else rewrites the table under `ACCESS EXCLUSIVE`, so use the rename
recipe with a column of the new type, converting in the backfill.

`integer` primary key to `bigint`, the most common case, for `orders.id` referenced
by `order_lines.order_id`:

1. Add `id_new bigint`; a trigger sets `id_new = id` on insert and update.
2. Backfill `id_new` in batches.
3. `CREATE UNIQUE INDEX CONCURRENTLY` on `id_new`.
4. Make `id_new` `NOT NULL` with the recipe above.
5. Convert every referencing column to `bigint` with this same recipe
   (`order_lines.order_id_new`), and give each one a **second foreign key** to the new
   column: `FOREIGN KEY (order_id_new) REFERENCES orders (id_new) NOT VALID`, then
   `VALIDATE`. It depends on the unique index from step 3, so it survives the swap
   and there is never a moment without enforcement.
6. Swap, in one short transaction with `lock_timeout`:
   1. drop the old foreign keys that reference `orders (id)`. The primary key cannot
      be dropped while they depend on it, and `CASCADE` would drop them silently;
   2. drop the old primary key and `ADD CONSTRAINT orders_pkey PRIMARY KEY USING INDEX`
      on the index from step 3;
   3. rename `id` to `id_old` and `id_new` to `id`;
   4. move the generator. A `serial` sequence is itself `AS integer` and would still
      stop at 2,147,483,647: `ALTER COLUMN id_old DROP DEFAULT` (or the old column
      keeps drawing from the sequence), `ALTER SEQUENCE orders_id_seq AS bigint;`,
      `ALTER SEQUENCE orders_id_seq OWNED BY orders.id;`, and set the new column's
      default to `nextval('orders_id_seq')`. An identity column cannot be moved:
      `ALTER COLUMN id_old DROP IDENTITY`, then
      `ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (START WITH <max(id) + 1>)`;
   5. release the old column, after the generator has moved, or every insert fails
      on it: `ALTER COLUMN id_old DROP NOT NULL`;
   6. drop the trigger.
7. Swap each referencing column the same way (rename, release the old column).
8. Drop the `_old` columns once no code reads them.

This sequence was run end to end on PostgreSQL 14 and 18, for `serial` and identity
keys. Rehearse it on a copy of the project's schema all the same: a dependency the
example does not have (a view, another trigger, a replication publication) shows up
only when run.

Plan it before the `integer` runs out: `SELECT max(id) FROM t` against 2,147,483,647.

## Drop a column or table

1. Deploy code that no longer reads or writes it. ORMs that select every mapped
   column need the column removed from the model or marked ignored first.
2. Then drop it, with `lock_timeout`. The drop is brief; disk space returns as rows
   are rewritten by later updates and vacuum. Dropping a table, or a column that
   carries a foreign key, also takes `ACCESS EXCLUSIVE` on the referenced table.

Dropping first and deploying second fails every query the old code still runs.

## Add or remove an enum value

`ALTER TYPE status ADD VALUE 'refunded';` is brief. On 12 and later it may run in a
transaction block, but the new value cannot be used until that transaction commits,
so do not insert it in the same migration.

PostgreSQL can rename an enum value (`ALTER TYPE ... RENAME VALUE`) but cannot remove
or reorder one. That takes a new type and a
column type change (rename recipe). A value set that changes often belongs in a
`CHECK` constraint or a lookup table instead; see
[data-types.md in designing-postgresql-schemas](../../designing-postgresql-schemas/references/data-types.md#booleans-and-status-values).
