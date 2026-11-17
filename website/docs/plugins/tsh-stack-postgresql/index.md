---
title: 'TSH Stack: PostgreSQL'
sidebar_label: Overview
sidebar_position: 0
description: TSH practices for PostgreSQL 14 to 18, beneath whatever ORM a project uses, covering live-table schema migrations, slow-query diagnosis and table design.
sources:
  - plugins/tsh-stack-postgresql/.claude-plugin/plugin.json
  - plugins/tsh-stack-postgresql/README.md
sources_hash: "5ad8ba1914ff73e3303e209bfdfb70e7c17d2ecaaaf573813b22e8b748ec5e11"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: PostgreSQL

`tsh-stack-postgresql` carries TSH's practices for PostgreSQL 14 to 18 at the level of the database itself rather than any ORM: schema migrations that run against live traffic, slow queries found and fixed from evidence, and table design that keeps bad data out.

## Who installs it and where

Install it at **project scope**, into the projects that use PostgreSQL, so it travels with the repository: the repository already knows which database it runs on. Your discipline plugin (for example [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)) and [`tsh-core`](/docs/plugins/tsh-core/) travel with you at user scope. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here. If you added the marketplace before this plugin existed, refresh it first with `/plugin marketplace update tsh-agentic-collections`.

Once installed, skills are invoked as `/tsh-stack-postgresql:<skill>`. Release notes are on the [changelog page](/docs/changelog/tsh-stack-postgresql).

## What it ships

<PluginComponents plugin="tsh-stack-postgresql" />

All three skills are model-invocable: Claude loads them when the work matches their description, so you do not have to type the command. They hand work to each other: a design ships through a migration, and an index a slow query needs ships through a migration too.

## How it sits next to the ORM skills

The stack plugins for application code carry their ORM's mechanics: TypeORM in [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/), Doctrine in [`tsh-stack-php`](/docs/plugins/tsh-stack-php/), SQLAlchemy and SQLModel in [`tsh-stack-python`](/docs/plugins/tsh-stack-python/). This plugin carries what PostgreSQL does with the SQL those ORMs produce. For a migration written in TypeORM, Claude loads this plugin's migration skill first. It carries the one tool mechanic a safe migration needs (running outside a transaction, per tool) and then loads the ORM's own skill, when one is installed, for how the migration is written.

## Scope

The routing question for this plugin is whether the guidance would change if the project switched database engine. If yes, it belongs here. If it would change with the ORM or language, it belongs in that stack's plugin; if it would change when the reader switched job, in a discipline plugin.

## MCP servers, hooks and agents

This plugin ships no agents, no `.mcp.json` and no hooks.

## Not covered

The plugin README lists these gaps as deliberate scope:

- **Running the database**: provisioning, server parameters, backups, replication, failover and upgrades. Managed instances belong to the cloud plugins and to `tsh-platform-engineering`.
- **MySQL, MariaDB and other engines**: each engine is its own stack plugin, because the advice depends on PostgreSQL's lock modes and planner.
- **Extensions beyond the common ones** (PostGIS, TimescaleDB, pgvector) have no skill of their own.

## Source

- [`plugins/tsh-stack-postgresql/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-postgresql/README.md)
- [`plugins/tsh-stack-postgresql/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-postgresql/.claude-plugin/plugin.json)
