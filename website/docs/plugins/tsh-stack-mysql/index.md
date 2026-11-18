---
title: 'TSH Stack: MySQL'
sidebar_label: Overview
sidebar_position: 0
description: TSH practices for MySQL 8.0, 8.4 and 9.7 with InnoDB, beneath whatever ORM a project uses, covering online schema migrations, slow-query diagnosis and table design.
sources:
  - plugins/tsh-stack-mysql/.claude-plugin/plugin.json
  - plugins/tsh-stack-mysql/README.md
sources_hash: "f8d82ec93cf97b7a4273b3256f20de0ce1d970106185a13e7012e3bb0c052655"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: MySQL

`tsh-stack-mysql` carries TSH's practices for MySQL 8.0, 8.4 and 9.7 with InnoDB, Aurora MySQL 3 and Aurora MySQL 8.4 included, at the level of the database itself rather than any ORM: schema migrations that run against live traffic without blocking it or stalling replicas, slow queries found and fixed from evidence, and table design that keeps bad data out. The behaviour the skills rely on was checked against MySQL 8.0.46, 8.4.13 and 9.7.4 when the plugin was written.

## Who installs it and where

Install it at **project scope**, into the projects that use MySQL, so it travels with the repository: the repository already knows which database it runs on. Your discipline plugin (for example [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)) and [`tsh-core`](/docs/plugins/tsh-core/) travel with you at user scope. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here. If you added the marketplace before this plugin existed, refresh it first with `/plugin marketplace update tsh-agentic-collections`.

Once installed, skills are invoked as `/tsh-stack-mysql:<skill>`. Release notes are on the [changelog page](/docs/changelog/tsh-stack-mysql).

## What it ships

<PluginComponents plugin="tsh-stack-mysql" />

All three skills are model-invocable: Claude loads them when the work matches their description, so you do not have to type the command. They hand work to each other: a design ships through a migration, and an index a slow query needs ships through a migration too.

## How it sits next to the ORM skills

The stack plugins for application code carry their ORM's mechanics: TypeORM in [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/), Doctrine in [`tsh-stack-php`](/docs/plugins/tsh-stack-php/), SQLAlchemy and SQLModel in [`tsh-stack-python`](/docs/plugins/tsh-stack-python/). This plugin carries what MySQL does with the SQL those ORMs produce. For a migration written in Doctrine, Claude loads this plugin's migration skill, which carries the tool mechanics a safe migration needs (non-transactional DDL, adding `ALGORITHM` and `LOCK`, recording a change made outside the tool), and then loads the ORM's own skill, when one is installed, for how the migration is written.

## Scope

The routing question for this plugin is whether the guidance would change if the project switched database engine. If yes, it belongs here. If it would change with the ORM or language, it belongs in that stack's plugin; if it would change when the reader switched job, in a discipline plugin.

## MCP servers, hooks and agents

This plugin ships no agents, no `.mcp.json` and no hooks.

## Not covered

The plugin README lists these gaps as deliberate scope:

- **Running the database**: provisioning, server parameters, backups, replication, failover and upgrades. Managed instances belong to the cloud plugins and to `tsh-platform-engineering`.
- **MariaDB, PostgreSQL and other engines**: each engine is its own stack plugin. MariaDB's online DDL and optimizer have diverged from MySQL's, so the skills stop on it.
- **MySQL 5.7 and earlier**, and storage engines other than InnoDB.
- **PlanetScale and Vitess workflows**: their deploy requests replace the migration recipes; query and schema advice still applies.

## Source

- [`plugins/tsh-stack-mysql/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-mysql/README.md)
- [`plugins/tsh-stack-mysql/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-mysql/.claude-plugin/plugin.json)
