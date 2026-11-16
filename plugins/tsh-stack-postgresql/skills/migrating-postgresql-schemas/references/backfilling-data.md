# Backfilling data

Use this reference when existing rows must be updated or copied as part of a schema
change: filling a new column, converting values, splitting or merging columns.

## Why not one UPDATE

`UPDATE big_table SET c = ...` over the whole table:

- holds row locks on every updated row until commit, so concurrent writes to those
  rows wait for the whole run;
- writes a new version of every row, roughly doubling the table on disk. Vacuum later
  makes that space reusable but does not shrink the file; batching lets vacuum reuse
  space between batches and keeps the growth down;
- produces WAL for the whole table at once, which replicas must replay, so read
  replicas fall behind;
- cannot be resumed: a failure at 90% rolls back all of it.

## Batch it

Update a bounded set of rows per transaction, keyed on an indexed column, and commit
between batches:

```sql
-- one batch; repeat until it updates 0 rows
WITH batch AS (
  SELECT id FROM orders
  WHERE id > :last_id AND status_code IS NULL
  ORDER BY id
  LIMIT 5000
)
UPDATE orders o
SET status_code = lookup_status_code(o.status)
FROM batch
WHERE o.id = batch.id
RETURNING o.id;
```

- **Walk the primary key** (`id > :last_id ORDER BY id`), keeping the highest `id`
  from `RETURNING` as the next `:last_id`. It finds each batch with an index range
  scan. `OFFSET` gets slower with every batch.
- **Size batches by time, not rows.** Aim for well under a second per batch; start
  around 1,000 to 10,000 rows and adjust from the measured duration.
- **Pause between batches** when replicas lag or the primary is busy. Check
  `pg_stat_replication.replay_lag` on the primary.
- **Make it resumable and idempotent.** The `WHERE ... IS NULL` (or a comparison with
  the target value) skips rows already done, so a restart repeats nothing.
- **Run it outside the schema migration.** A backfill inside the migration tool's
  transaction is the one big `UPDATE` again, and worse: if the same migration altered
  the table first, its `ACCESS EXCLUSIVE` lock is held for the whole backfill, a full
  outage of the table. Use a separate script or job that the deploy runs after the
  migration, or a background worker in the application.
- **Mind triggers.** A trigger on the table fires for every backfilled row. That may
  be what you want (a dual-write trigger) or not (an audit log, an outbox).

New rows written during the backfill must already be correct: deploy the code (or
trigger) that writes the new column before the backfill starts, so the backfill only
has to catch up on old rows.

## After the backfill

- Run `ANALYZE` on the table so the planner sees the new column's values.
- Vacuum reclaims the old row versions. Autovacuum normally handles it; on a very
  large backfill check `pg_stat_user_tables.n_dead_tup` and whether autovacuum is
  keeping up, and say so in the hand-over rather than running `VACUUM FULL`, which
  takes `ACCESS EXCLUSIVE`.
- Verify before the next step relies on it: `SELECT count(*) FROM t WHERE c IS NULL`
  must be 0 before `NOT NULL` is added.

## Copying into a new table

When a change is easier as a new table (a re-partitioning, a split), the same rules
apply: copy in key-ordered batches, keep the new table current with a trigger or
dual writes during the copy, verify counts, then switch reads in a deploy. Logical
replication is the tool for copying a very large or very busy table between
databases; it is an infrastructure decision, not a migration.
