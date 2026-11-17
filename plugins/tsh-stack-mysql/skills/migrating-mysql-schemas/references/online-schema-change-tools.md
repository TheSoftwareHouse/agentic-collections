# Online schema change tools

Use this reference when an operation needs `ALGORITHM=COPY` on a table with traffic,
or when an in-place rebuild or index build would lag binlog replicas longer than the
system can bear. Both tools below build a copy of the table with the change applied,
copy rows in small throttled chunks while keeping the copy current, then swap the
two tables in a brief rename.

**Check the tool's documentation for the installed version.** Flags and limitations
change between releases; the points below are the ones a migration review depends
on. Running either tool against a shared or production database is an operator's
job: hand over the exact command and its dry run, do not run it.

## Which one

| | gh-ost | pt-online-schema-change |
| :-- | :-- | :-- |
| How it keeps the copy current | Reads the binary log | Triggers on the original table |
| Extra load on the source | Low: no triggers in the write path | Every write also writes the copy, inside the same transaction |
| Foreign keys | **Not supported** on either side: refuses tables that have or are referenced by one | Supported, with `--alter-foreign-keys-method` for tables referenced by others |
| Existing triggers on the table | Supported from v1.1.8 with `--include-triggers`; not before (its limitations page may still say "not supported") | Supported on 5.7+ with `--preserve-triggers` |
| Needs | Row-based binlog with full row images, a primary or unique key with no `NULL`s | A primary or unique key |
| Throttling | Replica lag, load, flag files; pausable and controllable while running | Replica lag (`--max-lag`), load (`--max-load`, `--critical-load`), chunk time; pausable with `--pause-file` |
| Cut-over | Postponable until an operator releases it (`--postpone-cut-over-flag-file`) | Immediately after the copy |

Prefer gh-ost when the table has no foreign keys and the binlog is available, and
pt-online-schema-change otherwise. If the project already uses one, use that one.

## What both need from the migration

- **A primary key, or a unique key on non-null columns.** They copy by it. A table
  without one needs a key first.
- **Disk for a second copy** of the table and its indexes.
- **The metadata lock at the end.** The swap is a `RENAME TABLE`, which waits for the
  metadata lock like any DDL (see [online-ddl-and-locks.md](./online-ddl-and-locks.md)).
  A long transaction at cut-over delays it; both tools time the wait out and retry.
  pt-online-schema-change also takes the lock to create and drop its triggers, and
  by default sets `lock_wait_timeout=60` for itself: pass
  `--set-vars lock_wait_timeout=5` (with `--tries` for retries) so a long transaction
  cannot queue traffic for a minute.
- **A rehearsal first**, then the real run with `--execute`, with the rehearsal's
  output in the review: `--dry-run` for pt-online-schema-change; gh-ost does nothing
  until it is given `--execute`, so a run without it is the rehearsal.
- **Constraint names change.** Both build their copy with `CREATE TABLE ... LIKE`,
  which gives named `CHECK` constraints generated names (`..._chk_1`), and
  pt-online-schema-change also renames foreign keys (below). Rename them back
  afterwards if migrations refer to them by name.
- **Recording the change in the migration tool**, which never ran it. See
  [migration-tools.md](./migration-tools.md#changes-made-outside-the-tool).

## gh-ost

```shell
gh-ost \
  --host=<replica-or-primary> --database=shop --table=orders \
  --alter="MODIFY amount BIGINT NOT NULL" \
  --max-lag-millis=1500 --chunk-size=1000 \
  --postpone-cut-over-flag-file=/tmp/ghost.postpone \
  --assume-rbr --verbose            # rehearsal: nothing happens without --execute
```

- It connects to a replica by default to read the binlog. With no replica, or on a
  managed service, it runs against the primary with `--allow-on-master`.
- On RDS, run it with `--assume-rbr` and `binlog_format=ROW`, and keep binlogs
  retained long enough for the whole run.
- On Aurora, binary logging is off unless the cluster parameter group turns it on
  (`binlog_format=ROW`), which takes a writer restart; and the gh-ost RDS notes say to
  set `aurora_enable_repl_bin_log_filtering` to `0` for the run, or cut-over can
  hang. Read gh-ost's `doc/rds.md` for the installed version first.
- An `ENUM` column in the key it copies by slows it down badly.

## pt-online-schema-change

```shell
pt-online-schema-change \
  --alter "ADD CONSTRAINT orders_amount_ck CHECK (amount >= 0)" \
  --max-lag 2 --chunk-time 0.5 \
  --alter-foreign-keys-method auto \
  --set-vars lock_wait_timeout=5 \
  D=shop,t=orders --dry-run
```

- The triggers add work to every write on the table for the whole run; size the run
  for the busiest hour it will overlap.
- **Foreign keys change name.** On the new table each foreign key's name gains or
  loses a leading underscore. Migrations or code that refer to a constraint by name
  must expect that.
- `--alter-foreign-keys-method` decides how child tables that reference the altered
  table are repointed at the new one: `rebuild_constraints` alters each child table
  (a copy, if a child is large), `drop_swap` briefly leaves the table missing and
  disables foreign key checks for the swap. `auto` picks between them; read the
  choice it reports in the dry run.

## Managed platforms

PlanetScale and Vitess run schema changes through their own deploy-request workflow,
which does this copy for you; follow it instead of these tools. gh-ost has platform
flags for Azure Database for MySQL (`--azure`) and Google Cloud SQL (`--gcp`, which its
flag reference ties to first-generation instances): check its docs for the platform.
pt-online-schema-change on RDS or Aurora needs `log_bin_trust_function_creators=1`
in the parameter group, or creating its triggers fails without `SUPER`.
