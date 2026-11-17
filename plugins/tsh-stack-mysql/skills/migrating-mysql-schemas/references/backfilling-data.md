# Backfilling data

Use this reference when existing rows must be updated or copied as part of a schema
change: filling a new column, converting values, splitting or merging columns.

## Why not one UPDATE

`UPDATE big_table SET c = ...` over the whole table:

- holds a row lock on every row it changed until it commits, and, under the default
  `REPEATABLE READ`, locks the gaps between the index records it scanned, so inserts
  into those ranges wait too;
- keeps the old version of every row in the undo log until it commits, and makes
  every other transaction's reads walk further through it; the purge of that history
  lags behind for long after;
- is one transaction in the binary log, which every replica applies only after the
  source commits it, all at once;
- cannot be resumed: a failure at 90% rolls back all of it, and the rollback takes
  about as long as the work did.

## Batch it

Update a bounded range of the primary key per transaction, with autocommit, and walk
the key:

```sql
-- find the end of the next batch (an index range scan on the primary key)
SELECT id FROM orders WHERE id > :last_id ORDER BY id LIMIT 1 OFFSET 4999;
-- no row: the last batch runs from :last_id to the end of the table

UPDATE orders
SET status_code = CASE status WHEN 'paid' THEN 2 WHEN 'new' THEN 1 ELSE 0 END
WHERE id > :last_id AND id <= :batch_end
  AND status_code IS NULL;
-- next :last_id = :batch_end
```

- **Walk the primary key in closed ranges.** A range on the clustered primary key
  touches exactly those rows and locks only that range. `UPDATE ... LIMIT` without
  `ORDER BY` is unsafe for statement-based replication and re-scans done rows; a
  growing `OFFSET` gets slower with every batch.
- **Size batches by time, not rows.** Aim for well under a second per batch; start
  around 1,000 to 5,000 rows and adjust from the measured duration.
- **Pause between batches when replicas lag.** Check `Seconds_Behind_Source` in
  `SHOW REPLICA STATUS` (8.0.22+; `SHOW SLAVE STATUS` before) on each binlog replica,
  or the replica-lag metric of the managed service, and wait while it is above a
  threshold of a second or two.
- **Make it resumable and idempotent.** The `status_code IS NULL` (or a comparison
  with the target value) skips rows already done, so a restart repeats nothing.
- **Run it outside the schema migration.** MySQL DDL commits on its own, so a backfill
  in a migration file is not even atomic with the schema change; it is the one big
  `UPDATE` again, blocking the deploy for its whole run. Use a separate script or job
  that the deploy runs after the migration, or a background worker in the
  application.
- **Mind triggers and foreign key cascades.** A trigger fires for every backfilled
  row; a cascading foreign key changes child rows inside the same transaction.

New rows written during the backfill must already be correct: deploy the code that
writes the new column before the backfill starts, so the backfill only has to catch
up on old rows.

## Deleting in bulk

The same rules hold for deleting old rows: closed primary-key ranges, small batches,
pauses on replica lag. A huge `DELETE` also leaves the table file its old size; the
space is reused by new rows, and only a rebuild (`OPTIMIZE TABLE`, an in-place
rebuild with its own replica lag) returns it. For data removed by age, partitioning
by time and dropping whole partitions is cheaper, a design decision for
`designing-mysql-schemas`.

## After the backfill

- Run `ANALYZE TABLE` so the optimizer sees the new column's values. It is quick,
  but on 8.0 before 8.0.24 it could make new queries wait behind a running long
  query on that table; run it outside the busiest hour there.
- Watch the purge: `SELECT count FROM information_schema.INNODB_METRICS WHERE name =
  'trx_rseg_history_len';` should fall back towards its usual level.
- Verify before the next step relies on it: `SELECT COUNT(*) FROM t WHERE c IS NULL`
  must be 0 before `NOT NULL` is added.

## Copying into a new table

When a change is easier as a new table (a split, a new key), the same rules apply:
copy in key-ordered batches, keep the new table current with dual writes during the
copy, verify counts, then switch reads in a deploy. An online schema change tool does
this for a change to one table's definition.
