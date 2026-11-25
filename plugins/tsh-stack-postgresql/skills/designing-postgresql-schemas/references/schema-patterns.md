# Schema patterns

Use this reference when deletion, tenancy, history, concurrent edits, flexible
attributes or table size is part of the design. Each of these is cheap to decide
before the table holds data and expensive afterwards.

## Contents

- [Soft delete or archive](#soft-delete-or-archive)
- [Multi-tenancy](#multi-tenancy)
- [Row-level security](#row-level-security)
- [Audit columns](#audit-columns)
- [Optimistic locking](#optimistic-locking)
- [Status history](#status-history)
- [Polymorphic relations](#polymorphic-relations)
- [Flexible attributes](#flexible-attributes)
- [Partitioning](#partitioning)

## Soft delete or archive

A `deleted_at timestamptz` column keeps rows that users deleted. It costs on every
query: each one must filter `deleted_at IS NULL`, unique rules must become partial
unique indexes, and foreign keys still see the "deleted" row.

Choose by why rows are kept:

| Need | Design |
| :-- | :-- |
| undo for a short time, or the row is still referenced | `deleted_at`, partial unique indexes `WHERE deleted_at IS NULL`, and a partial index for the hot queries |
| keep a record for audit or law, never shown again | move the row to an archive table (same columns, plus `deleted_at` and `deleted_by`) and delete it from the live table |
| personal data that must actually be erased | delete it, or anonymise in place; a soft-deleted row is not erased |

Whatever is chosen, apply it consistently per table and say which tables use it.

## Multi-tenancy

| Model | Isolation | Cost |
| :-- | :-- | :-- |
| shared tables, `tenant_id` on every tenant-owned table | by query discipline, plus RLS | one schema, one migration path; a missing filter leaks data |
| schema per tenant | by `search_path` | migrations run once per tenant; thousands of schemas strain the catalog and tooling |
| database per tenant | by connection | strongest isolation, most operational work |

For shared tables:

- `tenant_id NOT NULL` on every tenant-owned table, including child tables, so a
  query never needs a join to know the tenant.
- Unique constraints include it: `UNIQUE (tenant_id, email)`.
- Foreign keys include it, `(tenant_id, customer_id)` referencing `(tenant_id, id)`,
  which makes a cross-tenant reference impossible
  ([keys-and-constraints.md](./keys-and-constraints.md#foreign-keys)).
- Indexes lead with it: `(tenant_id, created_at)`.
- Row-level security as the backstop, below.

## Row-level security

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
CREATE POLICY orders_tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::bigint)
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::bigint);
```

The application sets `app.tenant_id` at the start of every transaction, after
`BEGIN`, with `set_config('app.tenant_id', $1, true)`. `SET LOCAL` does the same but
cannot take a bind parameter, and outside a transaction block it only warns and does
nothing.

- **Table owners and superusers bypass RLS.** `FORCE ROW LEVEL SECURITY` applies it to
  the owner; the application must still connect as a role that is neither superuser
  nor `BYPASSRLS`.
- **Migrations and backfills are subject to the policy under `FORCE`** when they run
  as the table owner without `BYPASSRLS`. Run them as a role with `BYPASSRLS`, or set
  the tenant.
- **A missing tenant is an error with this policy**, which is the safe failure. On a
  connection that never set it: `unrecognized configuration parameter`. On a pooled
  connection that set it in an earlier transaction, the value is an empty string
  afterwards, and the cast fails: `invalid input syntax for type bigint: ""`.
  `current_setting('app.tenant_id', true)` alone does not turn that into "no rows",
  because of the empty string. If returning no rows is wanted instead, write
  `NULLIF(current_setting('app.tenant_id', true), '')::bigint`.
- **`SET` without `LOCAL` leaks** the tenant to the next user of a pooled connection.
- **Policies cost planning and execution time**; keep the expression simple and the
  `tenant_id` column indexed.
- RLS is the backstop for a forgotten `WHERE`, not a replacement for scoping queries.

## Audit columns

`created_at timestamptz NOT NULL DEFAULT now()` and `updated_at timestamptz NOT NULL DEFAULT now()`
on tables users edit. `updated_at` needs a trigger or disciplined application code;
an ORM's automatic timestamp misses updates made in SQL. `now()` is the transaction's
start time, so all rows written in one transaction share it.

Who changed what is a separate need. `created_by` and `updated_by` columns answer
"who last"; a full change history needs an audit table written by a trigger or by the
application, and is a design decision of its own.

## Optimistic locking

Two users edit the same record; the second save silently overwrites the first. A
`version integer NOT NULL DEFAULT 0` column prevents it:

```sql
UPDATE documents SET body = $1, version = version + 1
WHERE id = $2 AND version = $3;   -- 0 rows updated: someone else saved first
```

The application treats 0 updated rows as a conflict and tells the user. Most ORMs
support this column natively. Always increment the version in the same `UPDATE`, and
do not use `updated_at` as the version: a client that holds it at millisecond
precision never matches the stored microseconds, and a writer that bypasses the ORM
or trigger leaves it unchanged, so its save goes undetected.

## Status history

When the path through statuses matters (when was it paid, who cancelled it, how long
did it wait), keep a history table beside the current status:

```sql
CREATE TABLE order_status_changes (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id    bigint NOT NULL REFERENCES orders (id),
  from_status text,
  to_status   text NOT NULL,
  changed_at  timestamptz NOT NULL DEFAULT now(),
  changed_by  bigint REFERENCES users (id)
);
CREATE INDEX order_status_changes_order_id_idx ON order_status_changes (order_id, changed_at);
```

The current status stays on `orders` for cheap queries. Write both in one transaction.

## Polymorphic relations

`commentable_type text, commentable_id bigint` cannot have a foreign key, so it
admits references to rows that do not exist. Alternatives, in order of preference:

1. **One nullable foreign key per target, exactly one set:**
   `post_id bigint REFERENCES posts, photo_id bigint REFERENCES photos,
   CHECK (num_nonnulls(post_id, photo_id) = 1)`. Fits a handful of targets.
2. **A join table per target** (`post_comments`, `photo_comments`).
3. **A shared parent table** that every target references (`commentables`), with
   comments referencing it.

If the project already uses the polymorphic pattern through its ORM, keep it and add
a periodic integrity check; do not mix approaches.

## Flexible attributes

Per-tenant or per-category attributes tempt two designs:

- **Entity-attribute-value** (`attribute_name`, `attribute_value text` rows): no
  types, no constraints, every read is a pivot. Avoid.
- **A `jsonb` column** for the variable part, with real columns for everything
  queried or constrained: the usual answer. See
  [data-types.md](./data-types.md#jsonb).

## Partitioning

Declarative partitioning splits one logical table into partitions by a key, usually
time. It earns its complexity when:

- old data is dropped or archived on a schedule: dropping a partition replaces a huge
  `DELETE`;
- the table is very large (hundreds of millions of rows, or more than fits in memory
  by a wide margin) and most queries hit a recent range;
- maintenance (vacuum, reindex) on the whole table takes too long.

It costs:

- every primary key and unique constraint must include the partition key;
- queries that do not filter on the partition key read every partition;
- partitions must be created ahead of time (a scheduled job or `pg_partman`);
- many partitions slow planning.

Partition when one of the reasons holds, not in anticipation. Turning a populated
table into a partitioned one is a copy-and-switch migration
([backfilling-data.md in migrating-postgresql-schemas](../../migrating-postgresql-schemas/references/backfilling-data.md#copying-into-a-new-table)).
