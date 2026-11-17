# Keys and constraints

Use this reference when adding a reference between tables, a uniqueness rule, or any
invariant the data must keep. Behaviour quoted below was checked on MySQL 8.0.46,
8.4.13 and 9.7.4.

## Strict mode comes first

Every constraint below assumes `sql_mode` includes `STRICT_TRANS_TABLES`, which is
the default. Without it, MySQL stores a truncated string, a zero date, an
out-of-range number clamped to the limit, or an empty string for an unknown `ENUM`
value, and only warns. With it, all of those are errors:

```sql
SELECT @@GLOBAL.sql_mode, @@SESSION.sql_mode;
```

Check the session too: frameworks set it on connect (Laravel's `strict` connection
option, for example), and a managed service's parameter group can differ from local
Docker. Keep `NO_ZERO_DATE`, `NO_ZERO_IN_DATE`, `ERROR_FOR_DIVISION_BY_ZERO` and
`ONLY_FULL_GROUP_BY`, all in the default.

## Foreign keys

```sql
CREATE TABLE order_lines (
  id         BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id   BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  CONSTRAINT order_lines_order_fk   FOREIGN KEY (order_id)   REFERENCES orders (id)   ON DELETE CASCADE,
  CONSTRAINT order_lines_product_fk FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
);
```

- **Types must match exactly**, signedness and, for strings, character set and
  collation included; otherwise the foreign key is rejected.
- **The referencing column needs an index**; InnoDB creates one if none exists, named
  after the constraint. A composite index that starts with the column serves too.
- **Choose `ON DELETE`** for what the domain means:

| Action | Use when |
| :-- | :-- |
| `RESTRICT` / `NO ACTION` (the same in MySQL, checked at once) | The child must not outlive the parent, and deleting a parent that still has children is a mistake. The default |
| `CASCADE` | The child is part of the parent (order lines of an order). Deletes the whole tree in one transaction: on a large tree, a long one. Never on a record with legal or financial weight (invoices, payments, audit entries) |
| `SET NULL` | The link is optional and the child stands alone. The column must be nullable |
- **Cascades are invisible to triggers**, and on 8.0 and 8.4 to the binary log: the
  child rows a cascade deletes are not logged as row events, so change data capture
  (Debezium, DMS) and anything else reading the binlog never sees them. On 9.7 they
  are logged. If a consumer must see child deletions on 8.x, delete children
  explicitly in the application.
- **No deferrable constraints.** Each row is checked as it is written, so rows that
  reference each other in a cycle need one nullable link filled in afterwards.
- `foreign_key_checks = 0` disables checking for the session: for restoring dumps
  and for the online foreign key recipe in `migrating-mysql-schemas`, never in
  application code.

## CHECK constraints

Enforced from 8.0.16; on earlier 8.0 minors they are parsed and **silently ignored**.

```sql
CONSTRAINT orders_total_ck   CHECK (total >= 0),
CONSTRAINT orders_period_ck  CHECK (ends_at IS NULL OR ends_at > starts_at),
CONSTRAINT payments_target_ck CHECK ((order_id IS NULL) + (invoice_id IS NULL) = 1)
```

A `CHECK` passes when its expression is `NULL`: `CHECK (total >= 0)` accepts a
`NULL` total, so pair it with `NOT NULL` where absence is not allowed. Limits:

- one row only: no subqueries, no other tables, no non-deterministic functions such
  as `NOW()`, no `AUTO_INCREMENT` column;
- not on a column that a foreign key action modifies (`ON DELETE SET NULL`,
  `ON UPDATE CASCADE`): the table is rejected with `ERROR 3823`. `RESTRICT` and
  `ON DELETE CASCADE` are fine;
- **adding one to a populated table copies the table**; there is no `NOT VALID`.
  Put `CHECK` constraints in the `CREATE TABLE`.

## Unique keys

- A unique key allows any number of `NULL`s.
- **The collation decides what is a duplicate.** Under the default
  `utf8mb4_0900_ai_ci`, `Anna` and `anna` collide, and so do `anna` and `ánna`. See
  [data-types.md](./data-types.md#character-sets-and-collations).
- Uniqueness across a composite (`UNIQUE (customer_id, code)`) is a key on those
  columns in that order; it also serves queries on `customer_id`.

### Unique on some rows only

MySQL has no partial unique index. Index a generated column that is `NULL` for rows
the rule does not cover, since `NULL`s never collide:

```sql
CREATE TABLE subscriptions (
  id          BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  deleted_at  DATETIME(3) NULL,
  active_flag TINYINT AS (IF(deleted_at IS NULL, 1, NULL)) VIRTUAL,
  CONSTRAINT subscriptions_one_active_uq UNIQUE (customer_id, active_flag)
);
-- any number of deleted rows per customer, at most one live one
```

## Naming

- Name every constraint and index explicitly (`orders_customer_fk`,
  `orders_total_ck`). Generated names (`orders_ibfk_1`, `orders_chk_1`) depend on
  creation order and make later migrations fragile.
- Foreign key and `CHECK` names are unique per **schema**, not per table: prefix them
  with the table name.
- Use lowercase `snake_case` table names. Whether names are case-sensitive depends on
  `lower_case_table_names`, which differs between Linux (sensitive), macOS and
  Windows defaults and is fixed when the server is initialised; lowercase names work
  everywhere.
