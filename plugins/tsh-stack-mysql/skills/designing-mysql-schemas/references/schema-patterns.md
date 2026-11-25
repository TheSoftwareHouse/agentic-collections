# Schema patterns

Use this reference when deletion, tenancy, history, concurrency, flexible attributes
or table size is part of the design. Each pattern is cheap to choose at the start
and expensive to add to a populated schema.

## Soft delete or archive

**Soft delete** (`deleted_at DATETIME(3) NULL`) keeps rows in place and hides them in
queries.

- Every query, join and report must filter on it; an ORM's global scope or filter
  (Laravel's `SoftDeletes`, a Doctrine filter) helps, raw SQL and reporting tools do
  not use it.
- Unique keys must ignore deleted rows: the generated-column pattern in
  [keys-and-constraints.md](./keys-and-constraints.md#unique-on-some-rows-only).
- Foreign keys do not know a parent is "deleted": children of a soft-deleted parent
  stay valid.
- Indexes serving live-row queries should include `deleted_at`, or the live rows
  share the index with all the dead ones.

**Archive** (move rows to an `orders_archive` table, or delete them after export)
keeps the live table small and every query simple. Prefer it when deleted rows are
kept for audit or legal reasons rather than undeletion.

Choose by why rows are kept:

| Need | Design |
| :-- | :-- |
| Undo for a short time, or the row is still referenced | `deleted_at`, uniqueness on live rows through the generated column, `deleted_at` in the hot indexes |
| Keep a record for audit or law, never shown again | Move the row to an archive table and delete it from the live one |
| Personal data that must actually be erased | Delete it, or anonymise it in place; a soft-deleted row is not erased |

Apply the choice consistently per table and say which tables use it.

## Multi-tenancy

MySQL has **no row-level security**: nothing in the database stops a query that
forgets its tenant filter. The options:

| Model | Isolation | Cost |
| :-- | :-- | :-- |
| A database (schema) per tenant | Strong: grants per schema, per-tenant backup and restore | Migrations run once per tenant; thousands of schemas strain tooling and the table cache |
| Shared tables with `tenant_id` | Only as good as the application's filtering | One schema to migrate; all tenants share indexes and load |

For shared tables:

- `tenant_id NOT NULL` on every tenant-owned table, including children that could
  derive it through a join; it makes filtering and partition-like access cheap.
- `tenant_id` first in unique keys (`UNIQUE (tenant_id, email)`) and in the indexes
  of tenant-scoped queries.
- **Composite foreign keys that include `tenant_id`**, so a row cannot reference
  another tenant's row:

```sql
ALTER TABLE customers ADD CONSTRAINT customers_tenant_id_uq UNIQUE (tenant_id, id);
-- in orders:
CONSTRAINT orders_customer_fk FOREIGN KEY (tenant_id, customer_id)
  REFERENCES customers (tenant_id, id)
-- inserting an order for tenant 1 that points at tenant 2's customer now fails
```

  A composite foreign key like this cannot be `ON DELETE SET NULL`: it would null
  `tenant_id`, which is `NOT NULL`, and MySQL rejects the table (`ERROR 1830`). For
  an optional link, make only the link column nullable (`customer_id BIGINT NULL`)
  and keep the default `RESTRICT`: a row whose `customer_id` is `NULL` is not
  checked, so the application clears the link before it deletes the parent.

- One place in the application applies the tenant filter (a repository base class,
  an ORM global scope or filter), and tests prove that a query for one tenant cannot
  return another's rows.

## Audit columns

```sql
created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
```

`ON UPDATE` fires only when the row actually changes: an `UPDATE` that sets the same
values leaves `updated_at` alone. Who made the change (`created_by`, `updated_by`)
comes from the application. A full history of changes needs a history table, written
by the application or by triggers; triggers do not fire for foreign key cascades
(on 9.7, only in a session with `enable_cascade_triggers = ON`).

## Optimistic locking

```sql
version INT NOT NULL DEFAULT 0
-- update:
UPDATE orders SET status = ?, version = version + 1 WHERE id = ? AND version = ?;
-- 1 row affected: success; 0: someone else changed it first
```

Always increment the version. MySQL reports **changed** rows, not matched rows, by
default: an update that writes identical values reports 0, and some drivers switch
to matched rows (`CLIENT_FOUND_ROWS`). The increment makes the count mean the same
under both. Do not use `updated_at` as the version: it is skipped when nothing
changes and can collide within its precision.

## Status history

Keep the current status on the entity for queries, and append every transition to a
history table in the same transaction:

```sql
CREATE TABLE order_status_history (
  id         BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id   BIGINT NOT NULL,
  status     VARCHAR(32) NOT NULL,
  changed_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  changed_by BIGINT NULL,  -- with a foreign key to users where the schema has one
  CONSTRAINT order_status_history_order_fk FOREIGN KEY (order_id) REFERENCES orders (id),
  INDEX order_status_history_order_idx (order_id, changed_at)
);
```

Rows are only inserted, never updated.

## Polymorphic relations

A `commentable_type` plus `commentable_id` pair cannot have a foreign key, so nothing
stops it pointing at a row that does not exist. Prefer one nullable foreign key
column per target, with a `CHECK` that exactly one is set:

```sql
order_id   BIGINT NULL,
invoice_id BIGINT NULL,
CONSTRAINT comments_order_fk   FOREIGN KEY (order_id)   REFERENCES orders (id)   ON DELETE CASCADE,
CONSTRAINT comments_invoice_fk FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE,
CONSTRAINT comments_target_ck  CHECK ((order_id IS NULL) + (invoice_id IS NULL) = 1)
```

The `CHECK` cannot be combined with `ON DELETE SET NULL` on those columns (MySQL
rejects the table); `CASCADE` and `RESTRICT` work. With many target types, a
separate link table per target is cleaner. When an ORM already uses the
type-and-id pattern and the project accepts it, keep it consistent and say what it
leaves unenforced.

## Partitioning

Partitioning splits one table into several by a key, usually time. On MySQL:

- **Partitioned InnoDB tables cannot have foreign keys**, in either direction.
- Every unique key, the primary key included, must contain the partitioning column.
- A query that does not filter on the partitioning column searches every partition,
  so most queries do not get faster.

Its one strong use is **retention of a large, append-only table**: dropping a month
is `ALTER TABLE events DROP PARTITION p2026_01`, quick, instead of a long batched
`DELETE`. It still takes the metadata lock, so schedule the monthly partition
maintenance like any migration. Below hundreds of millions of rows, or without a
retention need, an index on the time column is enough. Partitioning a table that
already holds data copies it: decide before it grows.

## Flexible attributes

Attributes that differ per row or per tenant go in a `JSON` column, with the paths
that are queried extracted into indexed generated columns
([data-types.md](./data-types.md#json)). Avoid an entity-attribute-value table
(`entity_id, name, value`): every value is a string, nothing can be constrained, and
reading one entity takes a join per attribute.
