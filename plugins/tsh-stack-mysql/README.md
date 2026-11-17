# TSH Stack: MySQL

TSH practices for MySQL 8.0, 8.4 and 9.7 with InnoDB, Aurora MySQL included, at the
level of the database itself rather than any ORM: schema migrations that run against
live traffic without blocking it or stalling replicas, slow queries found and fixed
from evidence, and table design that keeps bad data out.

This is a **stack** plugin, not a discipline plugin. Install it into the projects
that use MySQL, at `project` scope, so it travels with the repo — the repo already
knows which database it runs on. Your discipline plugin (`tsh-product-engineering`
and friends) travels with **you**, at `user` scope, and so does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-mysql@tsh-agentic-collections
```

If you added the marketplace before this plugin existed, refresh it first with
`/plugin marketplace update tsh-agentic-collections`.

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `migrating-mysql-schemas` | `/tsh-stack-mysql:migrating-mysql-schemas` | Migrations against a live table: which algorithm each `ALTER` gets and whether it blocks writes, the metadata lock queue and `lock_wait_timeout`, replica lag, recipes for indexes, foreign keys, `NOT NULL`, renames, type changes and drops, gh-ost and pt-online-schema-change for what MySQL cannot do online, batched backfills, and how each common migration tool handles MySQL's non-transactional DDL |
| `optimizing-mysql-queries` | `/tsh-stack-mysql:optimizing-mysql-queries` | Finding the costly queries in `performance_schema` and the slow query log, reading `EXPLAIN` and `EXPLAIN ANALYZE`, statistics and histograms, choosing indexes, and fixing the query shapes that defeat them |
| `designing-mysql-schemas` | `/tsh-stack-mysql:designing-mysql-schemas` | Column types, keys, character sets and collations, strict `sql_mode`, foreign keys and constraints, and patterns for soft delete, multi-tenancy without row-level security, audit columns, optimistic locking, history and partitioning |

All three are model-invocable — Claude loads them when the work matches their
description, so you don't have to remember to type the command.

They hand work to each other: a design ships through a migration, and an index a
slow query needs ships through a migration too. Because they are in the same
plugin, those links always resolve.

The behaviour the skills rely on (which `ALTER` operations run online, the metadata
lock queue, collation rules, plan shapes) was checked against MySQL 8.0.46, 8.4.13
and 9.7.4 in Docker when the plugin was written.

## How it sits next to the ORM skills

The stack plugins for application code carry their ORM's mechanics: TypeORM in
`tsh-stack-nodejs`, Doctrine in `tsh-stack-php`, SQLAlchemy and SQLModel in
`tsh-stack-python`. This plugin carries what MySQL does with the SQL those ORMs
produce. For a migration written in Doctrine, Claude loads this plugin's migration
skill, which carries the tool mechanics a safe migration needs (non-transactional
DDL, adding `ALGORITHM` and `LOCK`, recording an out-of-band change), and then loads
the ORM's own skill, when one is installed, for how the migration is written.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates
arrive with `/plugin update`.

## Not covered

Deliberate gaps, so they read as scope rather than oversight:

- **Running the database**: provisioning, server parameters, backups, replication,
  failover and upgrades. Managed instances belong to the cloud plugins
  (`tsh-stack-aws`, `tsh-stack-gcp`, `tsh-stack-azure`) and to
  `tsh-platform-engineering`.
- **MariaDB, PostgreSQL and other engines.** Each engine is its own stack plugin;
  MariaDB's online DDL and optimizer have diverged from MySQL's, so these skills stop
  on it rather than give advice that may be wrong.
- **MySQL 5.7 and earlier**, and storage engines other than InnoDB.
- **PlanetScale and Vitess workflows.** Their deploy requests replace the migration
  recipes; query and schema advice still applies.

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
- **Behaviour claims are checked on a real server.** When adding one, run it on the
  supported versions and say which ones in the reference.
