# Keys and constraints

Use this reference when adding a reference to another table, a uniqueness rule, or
any invariant that must hold for every row. Each constraint here is a rule no code
path can skip.

## Contents

- [Foreign keys](#foreign-keys)
- [Choosing ON DELETE](#choosing-on-delete)
- [CHECK constraints](#check-constraints)
- [Unique constraints](#unique-constraints)
- [Exclusion constraints](#exclusion-constraints)
- [Deferrable constraints](#deferrable-constraints)
- [Naming](#naming)
- [What stays in the application](#what-stays-in-the-application)

## Foreign keys

Every column that holds another row's key gets a foreign key. Without it, deletes
and bugs leave references to rows that no longer exist, and nothing reports it.

- **Index the referencing column.** PostgreSQL does not. Without the index, deleting
  or re-keying a parent row scans the whole child table, under a lock.
- **Make it `NOT NULL`** unless the relationship is optional.
- **Match types exactly.** A `bigint` referencing an `integer` key works, but joins
  and indexes behave better with identical types.
- **Multi-tenant schemas:** a composite foreign key `(tenant_id, customer_id)`
  referencing `customers (tenant_id, id)` makes a cross-tenant reference impossible.
  It needs a unique constraint on `customers (tenant_id, id)`.
- On 18 and later a foreign key can be declared `NOT ENFORCED`. That documents a
  relationship without checking it, which is the situation foreign keys exist to
  prevent; do not use it to silence a failing constraint.

## Choosing ON DELETE

| Action | Means | Choose when |
| :-- | :-- | :-- |
| `NO ACTION` / `RESTRICT` (default) | the parent cannot be deleted while children exist | the children are records in their own right: orders of a customer, payments of an invoice |
| `CASCADE` | deleting the parent deletes the children | the children are parts of the parent and meaningless alone: lines of an order, items of a cart |
| `SET NULL` | children lose the reference | the reference is optional and the child survives: `assigned_to` on a ticket |
| `SET DEFAULT` | children get the column default | rare |

`CASCADE` chains: deleting one customer can delete orders, their lines, their
payments and the payments' refunds in one statement. Trace the chain before choosing
it, and never put it on a reference to a record with legal or financial weight.
`RESTRICT` checks immediately and refuses even when the end state would be valid;
`NO ACTION` checks at the end of the statement, or at commit when deferred.

## CHECK constraints

A `CHECK` states a rule about one row:

```sql
CHECK (quantity > 0)
CHECK (ends_at > starts_at)
CHECK (status IN ('pending', 'paid', 'cancelled'))
CHECK (num_nonnulls(card_id, bank_account_id) = 1)   -- exactly one of two
CHECK ((status = 'cancelled') = (cancelled_at IS NOT NULL))
```

- The expression must depend only on the row. A `CHECK` calling a function that reads
  other tables is not re-checked when those tables change; use a foreign key or a
  trigger.
- A `CHECK` passes when its expression is `NULL`. `CHECK (price > 0)` accepts a
  `NULL` price; add `NOT NULL` when that is wrong.
- Name them, so the error a user or a log sees says which rule failed.

## Unique constraints

- `UNIQUE (email)` for a global rule, `UNIQUE (tenant_id, email)` for a per-tenant one.
- `NULL`s are distinct by default: two rows with a `NULL` email both pass. On 15 and
  later, `UNIQUE NULLS NOT DISTINCT` treats them as equal when that is the rule.
- **A rule on a subset** ("one active subscription per customer", "unique email among
  rows that are not deleted") is a partial unique index:

  ```sql
  CREATE UNIQUE INDEX subscriptions_one_active_per_customer
    ON subscriptions (customer_id) WHERE status = 'active';
  ```

- **Case-insensitive uniqueness** is a unique index on `lower(email)` or a `citext`
  column. A plain unique index on `email` admits `Ola@x.pl` and `ola@x.pl`.
- Uniqueness checked in application code ("select, then insert if absent") races
  under concurrency. The constraint is what makes it true; the application turns its
  error into a friendly message.

## Exclusion constraints

An exclusion constraint generalises uniqueness to "no two rows overlap":

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE bookings ADD CONSTRAINT bookings_no_overlap
  EXCLUDE USING gist (room_id WITH =, during WITH &&);
```

It is the reliable way to forbid double bookings, overlapping price periods or
overlapping assignments. On 18 and later, temporal primary key and unique
constraints (`WITHOUT OVERLAPS`) express some of the same rules declaratively.

## Deferrable constraints

`DEFERRABLE INITIALLY DEFERRED` checks a constraint at commit instead of per
statement. It is needed for circular references and for swapping unique values
between rows in one transaction. Use it where one of those applies, not by default:
deferred checks report the error at commit, far from the statement that caused it.

## Naming

Follow the schema's existing convention. Without one, a common scheme:

| Object | Pattern | Example |
| :-- | :-- | :-- |
| table | plural snake_case | `order_lines` |
| primary key | `<table>_pkey` (the default) | `orders_pkey` |
| foreign key | `<table>_<column>_fkey` (the default) | `order_lines_order_id_fkey` |
| unique | `<table>_<columns>_key` | `users_email_key` |
| check | `<table>_<rule>_check` | `bookings_ends_after_starts_check` |
| index | `<table>_<columns>_idx` | `orders_customer_id_created_at_idx` |

Explicit names matter for constraints a migration will later drop or validate:
generated names differ between environments when an ORM or a person created them
differently.

## What stays in the application

Rules that span many rows over time (a credit limit across all of a customer's open
orders), depend on external systems, or change with business configuration are
enforced in the application, inside a transaction with the right isolation or an
explicit lock. Say in the design which rules those are, so nobody assumes the
database holds them.
