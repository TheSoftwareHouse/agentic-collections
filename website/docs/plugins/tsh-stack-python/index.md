---
title: 'TSH Stack: Python'
sidebar_label: Overview
sidebar_position: 0
description: TSH conventions for modern Python 3.12+, covering general implementation and review practices and data modelling with Pydantic v2, dataclasses, SQLModel and SQLAlchemy 2.0.
sources:
  - plugins/tsh-stack-python/.claude-plugin/plugin.json
  - plugins/tsh-stack-python/README.md
sources_hash: "58e9b751ee36db203fc69dce929f99c04ef97ebc06256dde30361f3f45556e07"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: Python

`tsh-stack-python` carries TSH's conventions for modern Python 3.12+: general implementation and review practices, and data modelling with Pydantic v2, dataclasses, SQLModel and SQLAlchemy 2.0.

## Who installs it and where

Install it at **project scope**, into the projects that run on Python, so it travels with the repository: the repository already knows what it runs on. Your discipline plugin (for example [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)) and [`tsh-core`](/docs/plugins/tsh-core/) travel with you at user scope. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here.

Once installed, skills are invoked as `/tsh-stack-python:<skill>`. Release notes are on the [changelog page](/docs/changelog/tsh-stack-python).

## What it ships

<PluginComponents plugin="tsh-stack-python" />

Both skills are model-invocable: Claude loads them when the work matches their description, so you do not have to type the command.

The two are designed to work together. [`writing-modern-python`](/docs/plugins/tsh-stack-python/skills/writing-modern-python) delegates dataclass, Pydantic, ORM and serialization decisions to [`writing-data-models`](/docs/plugins/tsh-stack-python/skills/writing-data-models) and links to it directly. Because they ship in the same plugin, that link always resolves.

## Scope

The routing question for this plugin is whether the guidance would change if the project switched language or framework. If yes, it belongs here. If it would change when the reader switched job, it belongs in a discipline plugin instead.

## MCP servers, hooks and agents

This plugin ships no agents, no `.mcp.json` and no hooks.

## Not covered yet

The plugin README lists these gaps as deliberate scope:

- **Pandas**: DataFrame manipulation, dtypes and vectorized workflows have no skill of their own yet.
- **Pandera**: DataFrame schema validation has no skill of its own yet.
- **Web framework guidance**: FastAPI, Django and Flask have no skill of their own. `writing-data-models` covers the Pydantic and SQLModel layer underneath them.

## Source

- [`plugins/tsh-stack-python/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-python/README.md)
- [`plugins/tsh-stack-python/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-python/.claude-plugin/plugin.json)
