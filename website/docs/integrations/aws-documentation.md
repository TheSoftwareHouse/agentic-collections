---
title: AWS Documentation
sidebar_label: AWS Documentation
sidebar_position: 5
description: The read-only AWS Labs documentation MCP server bundled with tsh-stack-aws, launched with uvx — what it is for, what it needs and what is deliberately not bundled.
sources:
  - plugins/tsh-stack-aws/.mcp.json
  - plugins/tsh-stack-aws/README.md
  - plugins/tsh-stack-aws/skills/auditing-aws-cost/SKILL.md
  - plugins/tsh-platform-engineering/README.md
sources_hash: "c415d522975a346ec818e7a5edda718289db3a229b90a00e37c675cdc4b370b1"
---

# AWS Documentation

The AWS Labs `aws-documentation` server, for current instance families, pricing tiers
and regional availability. It is read-only.

| | |
| :-- | :-- |
| Server name | `aws-documentation` |
| Bundled by | [`tsh-stack-aws`](/docs/plugins/tsh-stack-aws/) |
| Transport | `stdio`, launched as `uvx awslabs.aws-documentation-mcp-server@latest` |
| Prerequisite | `uv` |

## Prerequisite: `uv`

The server is a Python package launched with `uvx`. Without `uv`, that one server
fails to start and everything else works. The plugin README suggests:

```shell
brew install uv          # or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

## What uses it

[`auditing-aws-cost`](/docs/plugins/tsh-stack-aws/skills/auditing-aws-cost) lists it as
a data source for current instance families, pricing tiers and regional availability,
and makes it mandatory before recommending a specific instance type. Terraform AWS
provider documentation comes from [Context7](/docs/integrations/context7), which
`tsh-core` bundles.

## Where it is installed

`tsh-stack-aws` installs at project scope, because it belongs to an AWS repository,
not to a person. Cloud servers ship with the cloud's own plugin, so a GCP repository
never starts this server.

## What is not bundled

**No write-capable AWS API server is bundled.** Live account state is read through the
`aws` CLI with `describe`, `list` and `get` verbs only, so your own permission rules
apply to every call.
