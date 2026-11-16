# TSH Stack: PostgreSQL

TSH practices for PostgreSQL 14 to 18, at the level of the database itself rather
than any ORM: schema migrations that run against live traffic, slow queries found
and fixed from evidence, and table design that keeps bad data out.

This is a **stack** plugin, not a discipline plugin. Install it into the projects
that use PostgreSQL, at `project` scope, so it travels with the repo — the repo
already knows which database it runs on. Your discipline plugin
(`tsh-product-engineering` and friends) travels with **you**, at `user` scope, and so
does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-postgresql@tsh-agentic-collections
```

If you added the marketplace before this plugin existed, refresh it first with
`/plugin marketplace update tsh-agentic-collections`.

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `migrating-postgresql-schemas` | `/tsh-stack-postgresql:migrating-postgresql-schemas` | Migrations against a live table: the lock each statement takes, `lock_timeout` and retries, zero-downtime recipes for indexes, constraints, renames, type changes and drops, batched backfills, and running a migration outside a transaction in each common tool |
| `optimizing-postgresql-queries` | `/tsh-stack-postgresql:optimizing-postgresql-queries` | Finding the costly queries with `pg_stat_statements`, reading `EXPLAIN (ANALYZE, BUFFERS)`, choosing indexes, and fixing the query shapes that defeat them |
| `designing-postgresql-schemas` | `/tsh-stack-postgresql:designing-postgresql-schemas` | Column types and keys, foreign keys and constraints, and patterns for soft delete, multi-tenancy with row-level security, audit columns, optimistic locking, history and partitioning |

All three are model-invocable — Claude loads them when the work matches their
description, so you don't have to remember to type the command.

They hand work to each other: a design ships through a migration, and an index a
slow query needs ships through a migration too. Because they are in the same
plugin, those links always resolve.

## How it sits next to the ORM skills

The stack plugins for application code carry their ORM's mechanics: TypeORM in
`tsh-stack-nodejs`, Doctrine in `tsh-stack-php`, SQLAlchemy and SQLModel in
`tsh-stack-python`. This plugin carries what PostgreSQL does with the SQL those
ORMs produce. For a migration written in TypeORM, Claude loads this plugin's migration skill
first. It carries the one tool mechanic a safe migration needs (running outside a
transaction, per tool) and then loads the ORM's own skill, when one is installed,
for how the migration is written.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates
arrive with `/plugin update`.

## Not covered

Deliberate gaps, so they read as scope rather than oversight:

- **Running the database**: provisioning, server parameters, backups, replication,
  failover and upgrades. Managed instances belong to the cloud plugins
  (`tsh-stack-aws`, `tsh-stack-gcp`, `tsh-stack-azure`) and to
  `tsh-platform-engineering`.
- **MySQL, MariaDB and other engines.** Each engine is its own stack plugin; the
  advice here depends on PostgreSQL's lock modes and planner.
- **Extensions beyond the common ones** (PostGIS, TimescaleDB, pgvector) have no
  skill of their own.

## Scope

The routing question for this plugin is *would this guidance change if the project
switched database engine?* If yes, it belongs here. If it would change with the
ORM or language, it belongs in that stack's plugin; if it would change when the
**reader** switched job, in a discipline plugin.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change
never reaches them.

- **Skill names carry no version.** Version differences go in the skill's Version
  Baseline and are marked where a recipe depends on them.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed.
