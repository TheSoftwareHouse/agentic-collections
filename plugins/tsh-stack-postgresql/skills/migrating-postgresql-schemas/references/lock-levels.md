# Lock levels

Use this reference to judge any migration on a table that holds data. Every DDL
statement takes a table lock; the question is which one, for how long, and what
waits behind it.

## Contents

- [The lock modes that matter](#the-lock-modes-that-matter)
- [What each statement takes](#what-each-statement-takes)
- [The lock queue](#the-lock-queue)
- [lock_timeout and retries](#lock_timeout-and-retries)
- [Seeing who blocks whom](#seeing-who-blocks-whom)

## The lock modes that matter

Weakest to strongest. A mode blocks every statement whose lock conflicts with it.

| Mode | Taken by | Blocks reads | Blocks writes |
| :-- | :-- | :-- | :-- |
| `ACCESS SHARE` | `SELECT` | no | no |
| `ROW EXCLUSIVE` | `INSERT`, `UPDATE`, `DELETE`, `MERGE` | no | no |
| `SHARE UPDATE EXCLUSIVE` | `VACUUM`, `ANALYZE`, `CREATE INDEX CONCURRENTLY`, `VALIDATE CONSTRAINT` | no | no |
| `SHARE` | `CREATE INDEX` (not concurrent) | no | **yes** |
| `SHARE ROW EXCLUSIVE` | `ADD FOREIGN KEY`, `CREATE TRIGGER` | no | **yes** |
| `ACCESS EXCLUSIVE` | most `ALTER TABLE` forms, `DROP`, `TRUNCATE`, `VACUUM FULL`, `RENAME` | **yes** | **yes** |

`SHARE UPDATE EXCLUSIVE` conflicts with itself, so two concurrent index builds, or an
index build and a manual `VACUUM`, on the same table wait for each other.

## What each statement takes

"Brief" means the lock is held only to change the catalog: milliseconds once it is
granted. "Scan" means the table is read while the lock is held. "Rewrite" means the
table and its indexes are copied while the lock is held: minutes to hours on a large
table, with everything blocked.

| Statement | Lock | Duration |
| :-- | :-- | :-- |
| `ADD COLUMN` nullable, or with a constant default | `ACCESS EXCLUSIVE` | brief |
| `ADD COLUMN` with a volatile default (`clock_timestamp()`, `gen_random_uuid()`), a stored generated column, an identity column, or a domain with constraints | `ACCESS EXCLUSIVE` | **rewrite** |
| `ADD COLUMN ... GENERATED ALWAYS AS (...) VIRTUAL` (18+) | `ACCESS EXCLUSIVE` | brief |
| `DROP COLUMN` | `ACCESS EXCLUSIVE` | brief (the space is reclaimed later) |
| `ALTER COLUMN SET DEFAULT` / `DROP DEFAULT` | `ACCESS EXCLUSIVE` | brief |
| `ALTER COLUMN DROP NOT NULL` | `ACCESS EXCLUSIVE` | brief |
| `ALTER COLUMN SET NOT NULL` | `ACCESS EXCLUSIVE` | **scan**, skipped when a valid `CHECK (col IS NOT NULL)` exists (12+). On 18, when an invalid not-null constraint exists, it validates it: a scan under this lock |
| `ALTER COLUMN TYPE` | `ACCESS EXCLUSIVE` | **rewrite** and index rebuild, except binary-coercible changes |
| `ALTER COLUMN TYPE` binary-coercible: `varchar(n)` to `text` or to a longer `varchar` | `ACCESS EXCLUSIVE` | brief, indexes kept |
| `ADD CONSTRAINT ... CHECK` | `ACCESS EXCLUSIVE` | **scan** |
| `ADD CONSTRAINT ... CHECK ... NOT VALID` | `ACCESS EXCLUSIVE` | brief |
| `ADD CONSTRAINT ... FOREIGN KEY` | `SHARE ROW EXCLUSIVE` on **both** tables | **scan** |
| `ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID` | `SHARE ROW EXCLUSIVE` on both tables | brief |
| `VALIDATE CONSTRAINT` | `SHARE UPDATE EXCLUSIVE` (plus `ROW SHARE` on the referenced table for a foreign key) | scan, reads and writes continue |
| `ADD CONSTRAINT ... NOT NULL col NOT VALID` (18+) | `ACCESS EXCLUSIVE` | brief |
| `ADD PRIMARY KEY` / `ADD UNIQUE` | `ACCESS EXCLUSIVE` | **index build** |
| `ADD CONSTRAINT ... UNIQUE USING INDEX idx` | `ACCESS EXCLUSIVE` | brief, when `idx` already exists and is valid |
| `CREATE INDEX` | `SHARE` | **whole build**, writes blocked |
| `CREATE INDEX CONCURRENTLY` | `SHARE UPDATE EXCLUSIVE` | whole build, reads and writes continue |
| `DROP INDEX` | `ACCESS EXCLUSIVE` | brief, but waits for every query using the table |
| `DROP INDEX CONCURRENTLY` | `SHARE UPDATE EXCLUSIVE` | waits for running transactions |
| `REINDEX` | `SHARE` on the table and `ACCESS EXCLUSIVE` on the index | whole rebuild; blocks writes and, because planning locks every index of the table, virtually all reads. Never on a live table |
| `REINDEX CONCURRENTLY` (12+) | `SHARE UPDATE EXCLUSIVE` | whole rebuild, reads and writes continue |
| `RENAME COLUMN` / `RENAME TO` | `ACCESS EXCLUSIVE` | brief once granted, but every later query from code that uses the old name fails |
| `CREATE TRIGGER`, `ENABLE` / `DISABLE TRIGGER` | `SHARE ROW EXCLUSIVE` | brief |
| `ATTACH PARTITION` | `SHARE UPDATE EXCLUSIVE` on the parent, `ACCESS EXCLUSIVE` on the attached table and on the default partition | scan of the attached table (skipped with a matching valid `CHECK`) and of the default partition; builds any missing partition index under the lock, so create matching indexes on the table `CONCURRENTLY` first |
| `DETACH PARTITION ... CONCURRENTLY` (14+) | `SHARE UPDATE EXCLUSIVE`, then `ACCESS EXCLUSIVE` on the partition only | not in a transaction block, not with a default partition |
| `VACUUM FULL`, `CLUSTER` | `ACCESS EXCLUSIVE` | **rewrite**: never on a live table |
| `TRUNCATE` | `ACCESS EXCLUSIVE` | brief |

When one `ALTER TABLE` carries several subcommands, it takes the strongest lock any
of them needs, and a rewrite by one of them rewrites for all.

**Inside a transaction, every lock is held until `COMMIT`.** "Brief" means brief only
when the transaction commits right after the statement. Most migration tools wrap a
migration in one transaction, so an `ADD COLUMN` followed by an `UPDATE`, a plain
`CREATE INDEX` or a `VALIDATE` in the same migration keeps `ACCESS EXCLUSIVE` for the
whole run: a full outage on that table. Never follow an `ACCESS EXCLUSIVE` statement
with a scan, a backfill or an index build in the same transaction. A transaction that
alters several tables holds all their locks together and can deadlock with
application traffic; one table per migration avoids it.

**Dropping a table or a foreign key also locks the referenced table.** `DROP TABLE order_lines`
and `ALTER TABLE order_lines DROP CONSTRAINT order_lines_order_id_fkey` both take
`ACCESS EXCLUSIVE` on `orders` as well. Set `lock_timeout` for them as for the busy
table itself.

Source: the `ALTER TABLE`, `CREATE INDEX` and explicit-locking chapters of the
PostgreSQL 18 documentation. Version notes are given in brackets above; anything
without a note holds on 14 to 18.

## The lock queue

**A brief lock is only brief once it is granted.** Lock requests on a table queue in
order. An `ALTER TABLE` that needs `ACCESS EXCLUSIVE` waits for every transaction
already holding any lock on the table, including a plain `SELECT` inside a
transaction left open by a report, a console session or a stuck worker. While it
waits, every new query on the table, reads included, queues **behind it**.

The result is the classic outage: a migration that would take 5 ms waits 4 minutes
for one long transaction, and the application's connection pool fills with blocked
queries for those 4 minutes.

**Anti-wraparound autovacuum does not give way.** A normal autovacuum cancels itself
when DDL needs the table; one running to prevent transaction ID wraparound (its
`pg_stat_activity.query` ends with `(to prevent wraparound)`) does not, and the DDL
waits behind it. Check for it before the migration and wait it out.

Before a migration on a busy table, check for long transactions and wraparound
vacuums:

```sql
SELECT pid, now() - xact_start AS open_for, state, left(query, 80) AS query
FROM pg_stat_activity
WHERE xact_start < now() - interval '1 minute'
   OR query LIKE 'autovacuum:%(to prevent wraparound)'
ORDER BY xact_start;
```

## lock_timeout and retries

`lock_timeout` bounds how long a statement waits **for** a lock. Set it for the
migration's session or transaction, never globally:

```sql
SET lock_timeout = '3s';
ALTER TABLE orders ADD COLUMN shipped_at timestamptz;
```

On timeout the statement fails with `canceling statement due to lock timeout` and
releases its place in the queue, so traffic continues. The migration then retries,
a few times with a pause, and fails the deploy if it never gets the lock. A failed
migration is a page; a migration that blocks the table is an outage.

- Choose the timeout from what the application tolerates: a request that waits
  3 seconds on a lock is slow; one that waits a minute has timed out anyway.
- **Not for `CREATE INDEX CONCURRENTLY` or `VALIDATE CONSTRAINT`.** Their lock does
  not conflict with reads or writes, they are meant to run long, and a timeout that
  cancels a concurrent build leaves an `INVALID` index behind, every retry again on a
  busy database. Leave `lock_timeout` and `statement_timeout` unset (or long) for
  them; cleaning up after a failure is in
  [zero-downtime-recipes.md](./zero-downtime-recipes.md#add-an-index).
- `statement_timeout` bounds the whole statement and is a different control.
- Most migration tools run every migration in one transaction. `SET LOCAL lock_timeout`
  inside it applies to that transaction only. Check how the tool runs SQL in
  [migration-tools.md](./migration-tools.md).

## Seeing who blocks whom

During an incident, or while a migration waits:

```sql
SELECT a.pid,
       pg_blocking_pids(a.pid) AS blocked_by,
       now() - a.query_start   AS waiting_for,
       a.wait_event_type,
       left(a.query, 80)       AS query
FROM pg_stat_activity a
WHERE cardinality(pg_blocking_pids(a.pid)) > 0;
```

Cancelling the migration (`pg_cancel_backend(pid)`) releases the queue. Terminating
the blocker is a decision for whoever owns that session, not for the migration.
