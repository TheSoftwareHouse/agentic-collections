# Online DDL and locks

Use this reference for every migration on a table that holds data. It answers the
three questions that decide whether an `ALTER TABLE` is safe on MySQL: does it copy
the table while blocking writes, how long does it wait for and hold the metadata
lock, and how far will replicas fall behind.

## The three algorithms

| Algorithm | What happens | Writes during the run |
| :-- | :-- | :-- |
| `INSTANT` | Only the data dictionary changes. Takes about as long as the metadata lock. | Allowed |
| `INPLACE` | InnoDB does the work inside the engine. Some operations only change metadata; others **rebuild** the table internally, which takes time and disk proportional to its size. | Allowed with `LOCK=NONE`, when the operation supports it |
| `COPY` | MySQL creates a new table and copies every row into it. | **Blocked** for the whole copy: `COPY` needs at least `LOCK=SHARED` |

Without an `ALGORITHM` clause MySQL picks the fastest algorithm the operation
supports and falls back to `COPY` without saying so. With `ALGORITHM=INSTANT` or
`ALGORITHM=INPLACE, LOCK=NONE` it refuses with an error instead, which is what a
migration on a busy table wants:

```sql
ALTER TABLE orders MODIFY amount BIGINT, ALGORITHM=INPLACE, LOCK=NONE;
-- ERROR 1846: ALGORITHM=INPLACE is not supported. Reason: Cannot change column type INPLACE. Try ALGORITHM=COPY.
```

## What each operation needs

Checked on MySQL 8.0.46, 8.4.13 and 9.7.4. "Copy" means the operation blocks writes
for as long as it runs. `INSTANT` takes no `LOCK` clause: `ALGORITHM=INSTANT, LOCK=NONE`
fails with `ERROR 1221`.

| Operation | Request | Rebuilds | Notes |
| :-- | :-- | :-- | :-- |
| Add a column (nullable, or `NOT NULL` with a `DEFAULT`) | `INSTANT` | No | Any position on `8.0.29+`; only last before that. Not instant on tables with a `FULLTEXT` index or `ROW_FORMAT=COMPRESSED` (for `FULLTEXT`, see below) |
| Drop a column | `INSTANT` on `8.0.29+` | No | Before 8.0.29: `INPLACE`, rebuilds |
| Rename a column | `INSTANT` on `8.0.28+` | No | `INPLACE` when another table's foreign key references it. Breaks running code: see the recipes |
| Set or drop a column default | `INSTANT` | No | |
| Append a member to the end of an `ENUM` or `SET` | `INSTANT` | No | Reordering or removing members is copy, and so is growing the storage size: an `ENUM` past 255 members, a `SET` past 8, 16, 24 or 32 |
| Add a `VIRTUAL` generated column | `INSTANT` | No | A `STORED` one is copy |
| Add a secondary or unique index | `INPLACE, LOCK=NONE` | No | Takes time proportional to the table; a unique index fails at the end if duplicates exist or arrive during the build |
| Add an index on an expression | Two statements: `VIRTUAL` column `INSTANT`, then index it `INPLACE, LOCK=NONE` | No | A functional index `((lower(email)))` in one statement needs `LOCK=SHARED`, so it blocks writes |
| Drop, rename, or make an index invisible or visible | `INPLACE, LOCK=NONE` | No | Metadata only; `INSTANT` is refused for visibility |
| Widen a `VARCHAR` within the same length-prefix size | `INPLACE, LOCK=NONE` | No | Up to 255 bytes uses a 1-byte prefix, beyond that 2. In `utf8mb4` (4 bytes a character) `VARCHAR(63)` is 252 bytes and `VARCHAR(64)` is 256, so crossing that line is copy. Shrinking is copy |
| Make a column `NOT NULL` | `INPLACE, LOCK=NONE` | **Yes** | Fails on the first `NULL` it finds (strict mode). Backfill first |
| Make a column nullable | `INPLACE, LOCK=NONE` | **Yes** | |
| Change a column's type (`INT` to `BIGINT`, `VARCHAR` to `TEXT`) | **`COPY` only** | Yes | See the recipes and the online schema change tools |
| Change a column's character set or collation | `INPLACE, LOCK=NONE` when the column is not indexed, the source is not `latin1` and the column stays within its length-prefix size; otherwise **`COPY`** | No, when in place | The copy cases are refused in place with `ERROR 1846`, so stating the clauses sorts them. `utf8mb3` to `utf8mb4` grows each character from 3 to 4 bytes: `VARCHAR(80)` goes from 240 to 320 bytes and crosses the 255-byte line. `INSTANT` is refused |
| Add a foreign key | **`COPY`**, unless `foreign_key_checks=0` in the session: then `INPLACE, LOCK=NONE` | No | With checks off, existing rows are **not** validated. Check for orphans first. Takes the metadata lock on the **referenced table too** |
| Drop a foreign key | `INPLACE, LOCK=NONE` | No | Also locks the referenced table's metadata briefly |
| Add a `CHECK` constraint | **`COPY` only** | Yes | `ALTER CHECK ... NOT ENFORCED` and `DROP CHECK` are `INSTANT`; turning one back to `ENFORCED` is copy again |
| Add or replace the primary key | `INPLACE, LOCK=NONE` | **Yes** | Dropping it without adding another is copy |
| `OPTIMIZE TABLE`, `ALTER TABLE ... FORCE` | `INPLACE` | **Yes** | Resets the instant row-version counter |
| Convert the table's character set (`CONVERT TO CHARACTER SET`) | `INPLACE, LOCK=NONE` when every text column meets the conditions in the row above; otherwise **`COPY`** | Yes on 8.0; no on 8.4 and 9.7 | Checked converting from `utf8mb3` |
| Rename a table | `INSTANT` | No | |

**Instant has a budget.** Each instant add or drop creates a row version, counted in
`information_schema.INNODB_TABLES.TOTAL_ROW_VERSIONS`. At the limit (64 on 8.0 and
8.4, 255 on 9.7) an explicit `ALGORITHM=INSTANT` fails with `ERROR 4092`, and an
`ALTER` without the clause rebuilds the table in place instead, which is why the
clause matters. Check the counter on a table that
has had many instant changes, and plan the rebuild (an `INPLACE` rebuild with
`LOCK=NONE`) as its own step.

**A `FULLTEXT` index rules out in-place rebuilds.** On a table with one, every
operation that rebuilds the table (adding or dropping a column, `NOT NULL`, `FORCE`)
is refused with `ALGORITHM=INPLACE` and needs `COPY`: on a large table, tool work.

**Avoid 8.0.29 for instant add and drop.** Oracle withdrew that release over a defect
that could corrupt tables with instantly added columns. On it, use `INPLACE` and
recommend 8.0.30 or later.

## What a rebuild costs

An `INPLACE` operation that rebuilds the table permits writes, but it still:

- reads and writes the whole table, needing free disk for a second copy plus the
  sort files for every index;
- records concurrent writes in an online log, sized by
  `innodb_online_alter_log_max_size` (128 MB by default). If the writes during the
  run exceed it, the `ALTER` fails at the very end and rolls back;
- runs for a time proportional to the table, and every binlog replica then runs it
  again (see below).

On a large, busy table, a rebuild is often better done with an online schema change
tool, which throttles and can be paused.

## The metadata lock queue

Every `ALTER TABLE`, including an instant one, needs an exclusive **metadata lock**
on the table, briefly at the start and again at the end to commit. Any transaction
that has touched the table holds a shared metadata lock until it commits or rolls
back: a long report, a batch job, or a connection a pool left idle inside a
transaction.

While the `ALTER` waits for its exclusive lock, every new query on the table queues
behind it, reads included, in state `Waiting for table metadata lock`. A change that
takes milliseconds becomes an outage that lasts as long as the oldest transaction.
On MySQL 8.0, 8.4 and 9.7, a plain `SELECT` waited behind an `ALTER ... ALGORITHM=INSTANT`
that was itself waiting for an open transaction, and ran the moment the `ALTER` gave
up.

`lock_wait_timeout` bounds that wait. Its default is 31,536,000 seconds, one year.
Set it in the migration's session:

```sql
SET SESSION lock_wait_timeout = 5;
ALTER TABLE orders ADD COLUMN note VARCHAR(255) NULL, ALGORITHM=INSTANT;
```

On timeout the statement fails with `ERROR 1205 (Lock wait timeout exceeded)` and
changes nothing; for a one-statement migration the deploy may retry a few times with
a pause, then fail and report.

**The timeout applies again at the end.** An in-place build needs the exclusive lock
once more to commit. A transaction that opens on the table during a 40-minute index
build and is still open when the build finishes makes the `ALTER` time out at its
last step, and all 40 minutes are discarded. Before a long build, make sure no long
transactions (reports, batch jobs) will run against the table near its end, or use an
online schema change tool, whose cut-over can be postponed until an operator
releases it.
Do not confuse it with `innodb_lock_wait_timeout`, which bounds **row** lock waits and
does nothing for DDL.

## Replica lag

With binlog replication, a replica receives an `ALTER` only after the source has
finished it, then runs it again, and replicated transactions behind it wait. A
40-minute index build on the source means about 40 minutes of lag on every binlog
replica. That applies to RDS read replicas, cross-region and external replicas, and
self-managed ones. Aurora replicas inside one cluster read the shared storage volume
and do not replay the `ALTER`; binlog replicas of an Aurora cluster still do.

If reads go to replicas, or failover depends on them being current, estimate the run
time first (on a copy of production-size data) and use an online schema change tool,
which copies in throttled chunks, when the lag is not acceptable.

## Finding what blocks a migration

An `ALTER` that adds or drops a foreign key can be waiting on the **referenced**
table, so look at both tables.

While a migration waits:

```sql
-- who holds the metadata lock the ALTER is waiting for
SELECT object_schema, object_name, waiting_pid, waiting_query,
       blocking_pid, sql_kill_blocking_connection
FROM sys.schema_table_lock_waits;

-- the oldest open transactions
SELECT trx_mysql_thread_id, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_s,
       LEFT(trx_query, 80) AS current_query
FROM information_schema.innodb_trx
ORDER BY trx_started
LIMIT 10;
```

`sys.schema_table_lock_waits` also lists the `ALTER` as blocking itself; ignore that
row. A transaction with `current_query` `NULL` is idle inside a transaction, usually
an application connection that never committed.

Cancelling the migration releases the queue. Killing the blocker is a decision for
whoever owns that session, not for the migration.
