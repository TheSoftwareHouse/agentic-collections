# Migration tools

Use this reference when the migration is written with an ORM or a migration runner.
Most tools wrap each migration in a transaction, which breaks `CONCURRENTLY`, and
most generate SQL from a model diff that knows nothing about locks.

**Check the mechanism against the version the project pins.** These options change
between majors. Where the table says "verify", the mechanism was not confirmed
against the tool's current documentation; read it with `context7` or the tool's docs
before relying on it.

## Running a migration outside a transaction

| Tool | How to run one migration without a transaction |
| :-- | :-- |
| TypeORM | `transaction = false` on the migration class, with `migrationsTransactionMode` (or the CLI's `--transaction`) set to `each` or `none`. Under the default `all`, a migration that sets `transaction` makes the run fail with `ForbiddenTransactionModeOverrideError`. `migration:revert` opens a transaction unless the mode is `none`, whatever the flag says, so a `down()` with `DROP INDEX CONCURRENTLY` fails under `each`. |
| Prisma Migrate | Generated migrations never use `CONCURRENTLY`. Prisma 7.4 and later accept a hand-edited `migration.sql` holding only the `CREATE INDEX CONCURRENTLY` statement; verify it on a copy of the database. On earlier versions, and where a run is one transaction, apply the statement with `prisma db execute` outside the run, then `prisma migrate resolve --applied <migration>`. |
| Doctrine Migrations | `isTransactional(): bool` returning `false` on the migration class, with the `all_or_nothing` option off, since it wraps several migrations in one transaction: verify how the two interact in the pinned version. |
| Alembic | Wrap the statement in `with op.get_context().autocommit_block():`. It commits whatever the migration did before the block; use `transaction_per_migration=True` so that is only this migration's work. |
| Django | `atomic = False` on the `Migration` class. `django.contrib.postgres.operations` has `AddIndexConcurrently` and `RemoveIndexConcurrently`, and `AddConstraintNotValid` with `ValidateConstraint`, which belong in two separate migrations. |
| Knex | `exports.config = { transaction: false };` in the migration file. |
| Laravel | `public $withinTransaction = false;` on the migration class. The base class declares it `public`; a `protected` override is a fatal error. |
| Rails (Active Record) | `disable_ddl_transaction!` in the migration, and `algorithm: :concurrently` on `add_index`. |
| Flyway | `executeInTransaction=false` in the migration's script configuration file (`V<n>__<name>.sql.conf`). Flyway also detects non-transactional PostgreSQL statements itself, governed by the `mixed` setting. |
| Liquibase | `runInTransaction="false"` on the changeset. |

Whatever the tool, put exactly one concurrent statement in that migration.

## Setting lock_timeout

Put it at the top of the migration's SQL so it travels with the migration:
`SET LOCAL lock_timeout = '3s';` in a transactional migration, `SET lock_timeout = '3s';`
in a non-transactional one. **Not in a migration that runs `CREATE INDEX CONCURRENTLY`
or `VALIDATE CONSTRAINT`**: their lock does not block traffic, and a timeout leaves an
invalid index (see [lock-levels.md](./lock-levels.md#lock_timeout-and-retries)). A connection-level setting
in the tool's configuration also works, but hides the decision from the review.

Retrying on timeout is the deploy's job, and it is only safe for a **transactional**
migration: the failure rolled everything back, the migration is not recorded, and a
retry of the runner starts from it.

A failed **non-transactional** migration needs a person before the next deploy.
Prisma blocks `migrate deploy` until `prisma migrate resolve` is run, Flyway records
the failure until `flyway repair`, Liquibase's changelog table can be left
inconsistent, and a failed concurrent index build leaves an invalid index that
`IF NOT EXISTS` would then skip. Resolve the tool's state and drop the invalid index
first; say so in the hand-over.

## What generators get wrong

Review the generated SQL for these before it ships:

| Generated | Problem | Replace with |
| :-- | :-- | :-- |
| `CREATE INDEX` on an existing table | blocks writes for the whole build | `CREATE INDEX CONCURRENTLY` in its own non-transactional migration |
| `ADD CONSTRAINT ... FOREIGN KEY` | scans while blocking writes on both tables | `NOT VALID`, then `VALIDATE` |
| `ALTER COLUMN ... SET NOT NULL` | scans under `ACCESS EXCLUSIVE` | the `CHECK ... NOT VALID` recipe |
| a column rename emitted as `DROP COLUMN` plus `ADD COLUMN` | **data loss** | a rename, or the expand-and-contract recipe |
| `ALTER COLUMN TYPE` | rewrite under `ACCESS EXCLUSIVE` | the new-column recipe |
| a `DROP COLUMN` in the same release as the model change | old instances still select it | drop in a later release |
| several unrelated changes in one migration | one failure rolls back the safe parts with the unsafe | one concern per migration |

Recipes are in [zero-downtime-recipes.md](./zero-downtime-recipes.md).

The rename-as-drop is the one to look for first. A schema diff sees a missing column
and a new one, not a rename, so generators can emit it for a renamed field, and on a
populated table it deletes the column's data.

## Data migrations inside schema migrations

Tools make it easy to run an `UPDATE` inside a migration. On a small table it is
fine. On a large one it is the unbatched backfill described in
[backfilling-data.md](./backfilling-data.md), inside the migration's transaction.
Move it to a separate batched job.

## Rollbacks

`down` methods are rarely run and often wrong. For each step, state what undoes it:

- adding a column, index or constraint: drop it;
- a backfill: usually nothing; the old column is still there until the contract step;
- dropping a column: nothing undoes it short of a restore. That is why it comes last,
  after the code that stopped using it has run in production for a while.
