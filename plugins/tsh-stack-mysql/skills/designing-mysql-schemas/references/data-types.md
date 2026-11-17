# Data types

Use this reference when choosing a column type, a primary key, a character set or a
collation. Behaviour quoted below was checked on MySQL 8.0.46, 8.4.13 and 9.7.4 with
the default strict `sql_mode`.

## Text

- **`VARCHAR(n)`** counts characters, not bytes. Give it a real limit from the domain.
  Three byte limits make the number matter in `utf8mb4` (4 bytes a character):
  an index key holds at most 3,072 bytes (`VARCHAR(768)` fully indexed); all
  `VARCHAR` columns of a row share 65,535 bytes; and a column whose maximum is up to
  255 bytes has a 1-byte length prefix, more than that a 2-byte one, so widening
  across that line later copies the table (`VARCHAR(63)` to `VARCHAR(64)` in
  `utf8mb4`).
- **`TEXT`** (and `MEDIUMTEXT`) for unbounded text. It can be indexed only by a
  prefix, and takes a default only as an expression (`8.0.13+`).
- **`CHAR(n)`** for codes of fixed length, such as ISO country codes.
- **`VARBINARY`/`BINARY`** for bytes: hashes, tokens, binary UUIDs.

## Character sets and collations

**Use `utf8mb4`.** `utf8` is still an alias for `utf8mb3` (with a warning that it will
change), which stores at most 3 bytes a character and rejects emoji and some CJK
characters.

The **collation** decides which strings are equal, which decides what a unique key
rejects. The default, `utf8mb4_0900_ai_ci`, is accent-insensitive and
case-insensitive:

| Insert after `anna@x.pl` | Result under `utf8mb4_0900_ai_ci` |
| :-- | :-- |
| `Anna@x.pl` | Duplicate key |
| `ánna@x.pl` | Duplicate key |
| `anna@x.pl ` (trailing space) | Accepted: the `0900` collations do not ignore trailing spaces |

Also `'ß' = 'ss'` is true. Choose per column:

| Values | Collation |
| :-- | :-- |
| Names, titles, free text people search and sort | `utf8mb4_0900_ai_ci`, or a language-specific one (`utf8mb4_pl_0900_ai_ci`) when sort order matters to users |
| Emails, usernames: case-insensitive but accents distinct | `utf8mb4_0900_as_ci` |
| Tokens, codes, hashes, external IDs, anything case-sensitive | `utf8mb4_0900_bin`, or `VARBINARY`. Not `utf8mb4_bin`, which ignores trailing spaces |

Collations are inherited server, then schema, then table, then column, and a
connection or ORM can set its own. A table created years ago may be
`utf8mb4_general_ci` or `utf8mb4_unicode_ci` (which ignore trailing spaces) beside
new `0900` tables. **Columns that are joined or compared must have the same
character set and collation**, or the comparison fails with "Illegal mix of
collations" or stops using the index. Changing a populated column's collation copies
the table, so decide now.

## Numbers and money

- **`INT`** stops at 2,147,483,647 (signed); **`BIGINT`** at about 9.2 × 10^18.
  `UNSIGNED` doubles the range; whichever the schema uses, both sides of a foreign
  key must match exactly, signedness included, or the foreign key is rejected.
- **`DECIMAL(p, s)`** is exact; use it for money with an explicit scale
  (`DECIMAL(19, 4)`), or store a `BIGINT` count of minor units. Keep the currency in
  its own column. `UNSIGNED` on `DECIMAL` is deprecated: use `CHECK (amount >= 0)`.
- **`FLOAT`/`DOUBLE`** are approximate: measurements, never money. `FLOAT(M,D)` is
  deprecated.
- Display widths (`INT(11)`) are deprecated and mean nothing.

## Time

| Type | Stores | Range |
| :-- | :-- | :-- |
| `DATETIME(fsp)` | The value as given, no time zone | Years 1000 to 9999 |
| `TIMESTAMP(fsp)` | UTC, converted from and to the session `time_zone` | **1970 to 2038-01-19 03:14:07 UTC** |
| `DATE`, `TIME` | Calendar dates, times of day | |

Use **`DATETIME(3)` or `DATETIME(6)` holding UTC**, and set the connection's
`time_zone` to `+00:00` in the driver or ORM so `NOW()` and `CURRENT_TIMESTAMP` are
UTC too. `TIMESTAMP` rejects `2038-01-20` today, and its silent conversion through
the session time zone makes the stored value depend on connection settings.

- Pick the fractional precision the application keeps: 3 for JavaScript `Date`, 6
  for microseconds. MySQL **rounds** extra fractional digits rather than truncating:
  `'2026-12-31 23:59:59.6'` into a `DATETIME` is stored as `2027-01-01 00:00:00`
  (unless `sql_mode` includes `TIME_TRUNCATE_FRACTIONAL`).
- A literal with an offset (`'2026-01-01 10:00:00+02:00'`, `8.0.19+`) is converted to
  the session time zone on insert.
- Wall-clock values with no zone, such as a store's opening hour, are `TIME`, or a
  `DATETIME` documented as local. A future local event (an appointment at 9:00 in
  Warsaw) is the local `DATETIME` plus a column with the IANA zone name: the UTC
  instant changes if the zone's rules do.
- Audit defaults: `DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)`, and for
  `updated_at` add `ON UPDATE CURRENT_TIMESTAMP(3)`.

## Primary keys

- **`BIGINT AUTO_INCREMENT`** is the default. Values are unique, not dense: rollbacks
  and failed inserts leave gaps, and since 8.0 concurrent inserts are not numbered in
  commit order. The counter survives restarts from 8.0.
- **UUIDs** fit when IDs are generated outside the database or must not be
  guessable. The table is clustered by its primary key, and every secondary index
  carries it, so:
  - store them as **`BINARY(16)`**, never `CHAR(36)` (36 bytes, a 1-byte prefix, and
    a collation);
  - use a **time-ordered** UUID. Random UUIDv4 keys scatter inserts across the whole
    clustered index. MySQL has no UUIDv7 function, even on 9.7: generate it in the
    application and store it with `UUID_TO_BIN(?)`, read it with `BIN_TO_UUID(id)`.
    MySQL's own `UUID()` is version 1; `UUID_TO_BIN(UUID(), 1)` reorders it to sort
    by time.
- A common split: a `BIGINT` primary key internally, and a unique `BINARY(16)` public
  ID for URLs and APIs.
- Every table needs an explicit primary key. Without one InnoDB uses a hidden row ID,
  online schema change tools refuse the table, and replication of row changes slows
  down. Some managed services require one (`sql_require_primary_key`).

## Booleans and status values

- `BOOLEAN` is `TINYINT(1)` and accepts any value from -128 to 127: add
  `CHECK (flag IN (0, 1))`.
- For a status, choose by how the set of values changes:

| Option | Strength | Cost |
| :-- | :-- | :-- |
| `ENUM('new', 'paid')` | Compact; rejects unknown values in strict mode; appending a value at the end is instant | Reordering or removing values copies the table; sorts by declaration order, not alphabetically |
| `VARCHAR` with `CHECK (status IN (...))` | Readable, portable | Changing the list means adding a new `CHECK`, which copies the table |
| Lookup table with a foreign key | Values carry attributes (label, order, is-final) and change without DDL | A join, and a row per value to manage |

On MySQL, unlike PostgreSQL, an `ENUM` is usually the cheapest to extend; a lookup
table when values carry data or are edited by people.

## JSON

The `JSON` type validates documents and stores them in a binary form. Use it for
data the database stores but does not reason about: payloads, settings, per-tenant
extras. Attributes that are filtered, joined, constrained or present on every row are
columns. To index a JSON path, extract it into a generated column and index that, or
use a multi-valued index for arrays (`8.0.17+`). Defaults are expressions:
`doc JSON NOT NULL DEFAULT (JSON_OBJECT())`.

## Generated columns

`VIRTUAL` columns are computed on read, are instant to add and can be indexed: the
way to index an expression or a JSON path, and to express uniqueness on some rows
only ([keys-and-constraints.md](./keys-and-constraints.md)). `STORED` columns take
space and copy the table when added.
