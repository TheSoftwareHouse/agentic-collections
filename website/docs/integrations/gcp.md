---
title: GCP
sidebar_label: GCP
sidebar_position: 6
description: The three Google Cloud MCP servers bundled with tsh-stack-gcp — gcp-gcloud, gcp-observability and gcp-storage — what each does, which can mutate, and who uses them.
sources:
  - plugins/tsh-stack-gcp/.mcp.json
  - plugins/tsh-stack-gcp/README.md
  - plugins/tsh-stack-gcp/skills/auditing-gcp-cost/SKILL.md
  - plugins/tsh-platform-engineering/README.md
  - plugins/tsh-platform-engineering/agents/devops-engineer.md
  - plugins/tsh-platform-engineering/agents/infrastructure-auditor.md
sources_hash: "1023cbf77d73ca2c4fadeaa71b41ce9faf7d5872b908d93da08f9fe59785d16a"
---

# GCP

`tsh-stack-gcp` bundles three Google Cloud MCP servers. All three are `stdio` servers
launched with `npx -y`.

| Server | npm package | Purpose | Can mutate |
| :-- | :-- | :-- | :-- |
| `gcp-gcloud` | `@google-cloud/gcloud-mcp` | Live project state through `gcloud` | **Yes** |
| `gcp-observability` | `@google-cloud/observability-mcp` | Monitoring and logging configuration | Read-oriented |
| `gcp-storage` | `@google-cloud/storage-mcp` | Cloud Storage bucket inspection | Read-oriented |

Bundled by [`tsh-stack-gcp`](/docs/plugins/tsh-stack-gcp/), which installs at project
scope. Cloud servers ship with the cloud's own plugin, so no cloud server appears in a
repository that does not install that plugin.

Neither the plugin's `.mcp.json` nor its README names prerequisites. The servers' own
[READMEs](https://github.com/googleapis/gcloud-mcp#readme) do: Node.js 20 or newer and the gcloud CLI on the machine, signed in with
`gcloud auth login`. `observability-mcp` also needs Application Default Credentials, set with
`gcloud auth application-default login`. The servers act with your own Google Cloud
permissions.

## `gcp-gcloud` can mutate

`gcp-gcloud` can run mutating `gcloud` commands. Nothing in this plugin does: both
skills are restricted to `list`, `describe` and `get`. That restriction is an
instruction, not a technical guarantee. If you need a hard boundary, drop the server
from `.mcp.json` and let the skills fall back to the `gcloud` CLI through Bash, where
your own permission rules apply.

## What uses them

| Component | How it uses the servers |
| :-- | :-- |
| [`auditing-gcp-cost`](/docs/plugins/tsh-stack-gcp/skills/auditing-gcp-cost) | `gcp-gcloud` first, restricted to `list`, `describe` and `get`, with the `gcloud` CLI as fallback when the server is unavailable; `gcp-storage` for bucket inventory, lifecycle policies and storage classes; `gcp-observability` for logging and monitoring configuration, including retention and exclusions |
| [`devops-engineer`](/docs/plugins/tsh-platform-engineering/agents/devops-engineer) | May use a cloud server that can mutate, such as `gcp-gcloud`, only for `list`, `describe` and `get` |
| [`infrastructure-auditor`](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor) | Uses `gcp-gcloud` for inventory only; the read-only restriction covers MCP servers as much as shell commands |

[`implementing-gcp-terraform`](/docs/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform)
and `auditing-gcp-cost` get Terraform Google provider documentation, machine types
and pricing tiers from [Context7](/docs/integrations/context7), which `tsh-core`
bundles.
