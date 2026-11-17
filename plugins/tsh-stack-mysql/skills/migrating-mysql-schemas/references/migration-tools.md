# Migration tools

Use this reference when the migration is written with an ORM or a migration runner.
Most of them generate SQL from a model diff that knows nothing about online DDL, and
most of them pretend a migration is a transaction, which on MySQL it is not.

**Check the mechanism against the version the project pins.** Where a row says
"verify", the mechanism was not confirmed against the tool's current documentation;
read it with `context7` or the tool's docs before relying on it.

## DDL is not transactional

MySQL commits implicitly before and after every DDL statement. A migration with
three `ALTER`s that fails on the second has applied the first, and the tool has not
recorded the migration as run. The next run fails on "column already exists", or
worse, succeeds partly again. Hence the rule of one DDL statement per migration, and
no automatic retry of a failed one.

| Tool | Transactions on MySQL | What to do |
| :-- | :-- | :-- |
| Laravel | Never wraps a MySQL migration in a transaction (the MySQL schema grammar declares no schema transactions), whatever `$withinTransaction` says | Nothing to turn off |
| Doctrine Migrations | Wraps each migration by default. The implicit commit made older versions fail on PHP 8 with "There is no active transaction"; Migrations 3.x emits a deprecation instead | `isTransactional(): bool { return false; }` on the migration, or `transactional: false` in `doctrine_migrations.yaml` so new migrations default to it |
| TypeORM | `migrationsTransactionMode` `all` (default) or `each` opens a transaction that the first DDL statement commits | Keep one statement per migration; the mode does not protect anything here |
| Prisma Migrate | Each DDL statement in `migration.sql` commits on its own; a failure marks the migration failed and stops `migrate deploy` until resolved | Fix by hand, then `prisma migrate resolve --rolled-back <name>` or `--applied <name>` |
| Rails (Active Record) | Wraps a migration in a transaction only on adapters that support DDL transactions; the MySQL adapter does not | One change per migration |
| Django | The MySQL backend cannot roll back DDL; `atomic` does not change that | One operation per migration |
| Alembic | No transactional DDL on MySQL | One operation per revision |
| Knex | Wraps in a transaction that DDL commits | `exports.config = { transaction: false };` makes that explicit |
| Flyway | Records a failed migration as failed | `flyway repair` after fixing the schema by hand |
| Liquibase | A failed changeset can leave the changelog table and schema out of step | One change per changeset; fix by hand, then mark it run or not |

## Adding ALGORITHM, LOCK and lock_wait_timeout

Generators emit a bare `ALTER TABLE` or `CREATE INDEX`. Write the statement yourself
so it carries `ALGORITHM` and `LOCK` (`ALGORITHM=INSTANT` alone, since `INSTANT`
rejects a `LOCK` clause), and set the timeout first, in the same session:

| Tool | How |
| :-- | :-- |
| Laravel | `DB::statement('SET SESSION lock_wait_timeout = 5');` then `DB::statement('ALTER TABLE ... , ALGORITHM=INPLACE, LOCK=NONE');` instead of the `Schema` builder for that change |
| Doctrine | `$this->addSql(...)` for both statements; review the generated `up()` and replace its `ALTER` |
| TypeORM | `await queryRunner.query(...)` for both statements |
| Prisma | Edit the generated `migration.sql` before it is applied (`prisma migrate dev --create-only`), adding the `SET SESSION` line and the clauses |
| Rails | `add_index ..., algorithm: :inplace` emits `ALGORITHM = INPLACE`, but before Rails 8.2 there is no `lock:` option (check the pinned version): use `execute` for the statement when `LOCK=NONE` matters, and for the `SET SESSION` |
| Django | `migrations.RunSQL` with the statement, and `state_operations` so the model state still matches |
| Alembic | `op.execute(...)` for both statements |
| Knex | `knex.raw(...)` for both statements |
| Flyway, Liquibase | Write the SQL directly; in Liquibase a `sql` change |

The pool may hand each statement a different connection in some tools; `SET SESSION`
only helps if the `ALTER` runs on the same one. Where that cannot be guaranteed, put
both in one call where the driver allows several statements, or set
`lock_wait_timeout` on the migration connection in the tool's configuration and say
so in the review. The same goes for `foreign_key_checks = 0` in the foreign key
recipe, with one more risk: if the `ALTER` fails, the line that turns checks back on
never runs, and a pooled connection stays without foreign key checks. Run that
migration on a connection that is closed afterwards.

## Changes made outside the tool

A change run with gh-ost or pt-online-schema-change never passes through the
migration tool, which must still learn it happened, or its next schema diff will
generate the change again. Keep a migration file that describes the change, and mark
it applied instead of running it:

| Tool | Mark applied |
| :-- | :-- |
| Laravel | Insert the migration's name and batch into the `migrations` table |
| Doctrine | `bin/console doctrine:migrations:version '<class>' --add` |
| Prisma | `prisma migrate resolve --applied <name>` |
| Rails | Insert the version into `schema_migrations` |
| Django | `python manage.py migrate <app> <migration> --fake` |
| Alembic | `alembic stamp <revision>` |
| Flyway, Liquibase, TypeORM, Knex | Verify; each has its own history table |

## What generators get wrong

Review the generated SQL for these before it ships:

| Generated | Problem | Replace with |
| :-- | :-- | :-- |
| any `ALTER` without `ALGORITHM` (and `LOCK` for `INPLACE`) | silently copies the table if it has to | the same statement with the clauses |
| `CREATE INDEX` or `ADD INDEX` on a large table | online, but lags replicas for the whole build | the clauses above, or a tool run |
| `ADD CONSTRAINT ... FOREIGN KEY` | copies the table | the foreign key recipe |
| `MODIFY` that changes the type, or restates a column with a different length, charset or collation | copies the table; an ORM often emits it for a change you did not mean, such as a collation or `VARCHAR(255)` default | only what changed, or a tool run |
| a column rename emitted as `DROP COLUMN` plus `ADD COLUMN` | **data loss** | a rename, or the expand-and-contract recipe |
| a `DROP COLUMN` in the same release as the model change | old instances still select it | drop in a later release |
| several statements in one migration | a failure leaves it half applied | one statement per migration |

Recipes are in [zero-downtime-recipes.md](./zero-downtime-recipes.md).

The rename-as-drop is the one to look for first. A schema diff sees a missing column
and a new one, not a rename, so generators can emit it for a renamed field, and on a
populated table it deletes the column's data.

## Rollbacks

`down` methods are rarely run and often wrong. For each step, state what undoes it:

- adding a column, index or constraint: drop it, with the same clauses;
- a backfill: usually nothing; the old column is still there until the contract step;
- a tool run: another tool run in the other direction;
- dropping a column: nothing undoes it short of a restore. That is why it comes last,
  after the code that stopped using it has run in production for a while.
