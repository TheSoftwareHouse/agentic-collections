---
title: 'TSH Stack: GCP'
sidebar_label: Overview
sidebar_position: 1
description: GCP Terraform module patterns with Architecture Framework defaults and an evidence-based cost and labelling audit of a live project.
sources:
  - plugins/tsh-stack-gcp/.claude-plugin/plugin.json
  - plugins/tsh-stack-gcp/README.md
  - plugins/tsh-stack-gcp/.mcp.json
sources_hash: "a28dd5f231486b25289ba1af3cda1990f153d6a4ed16408cf7ae457cc15b7aaf"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: GCP

GCP-specific infrastructure guidance: Terraform module patterns with Architecture Framework
defaults, and a full evidence-based cost and labelling audit of a live project.

Install it alongside [tsh-platform-engineering](/docs/plugins/tsh-platform-engineering/), which
carries the cloud-agnostic half: module structure, state, pipelines, Kubernetes, observability,
secrets and the cost framework.

## Scope and installation

Install at **project scope**. The plugin belongs to a GCP repository, not to a person: a repository
has one cloud, while an engineer works across several. For the install commands, see
[Installation](/docs/getting-started/installation).

## What it covers

- **Terraform resource patterns.** VPC with secondary ranges, GKE with Workload Identity and
  Dataplane V2, Cloud SQL on private IP, Cloud Storage, Cloud Run, Pub/Sub, Secret Manager and Cloud
  Armor.
- **Cost and label audit.** Infrastructure code first, then the live project through read-only
  calls, drift and shadow resources, per-service waste checks, billing-export attribution and a
  saved report.

## Components

<PluginComponents plugin="tsh-stack-gcp" />

The plugin ships no agents.

## MCP servers

The plugin bundles three servers in `.mcp.json`, each launched with `npx -y`:

| Server              | Purpose                                  | Can mutate    |
| :------------------ | :--------------------------------------- | :------------ |
| `gcp-gcloud`        | Live project state through `gcloud`      | **Yes**       |
| `gcp-observability` | Monitoring and logging configuration     | Read-oriented |
| `gcp-storage`       | Cloud Storage bucket inspection          | Read-oriented |

See the [GCP integrations page](/docs/integrations/gcp) for the servers themselves. Terraform Google
provider docs, machine types and pricing tiers come from `context7`, which `tsh-core` bundles; see
[Context7](/docs/integrations/context7).

Because each server is launched with `npx -y`, it needs Node.js with `npx` on the `PATH`. The
plugin itself says nothing about credentials; the servers' own
[READMEs](https://github.com/googleapis/gcloud-mcp#readme) ask for Node.js 20 or newer, the gcloud CLI installed and signed in, and
Application Default Credentials for the observability server:

```shell
gcloud auth login
gcloud auth application-default login
```

**`gcp-gcloud` can run mutating `gcloud` commands.** Nothing in this plugin does: both skills are
restricted to `list`, `describe` and `get`. That restriction is an instruction, not a technical
guarantee. If you need a hard boundary, drop the server from `.mcp.json` and let the skills fall back
to the `gcloud` CLI through Bash, where your own permission rules apply.

## Where the line falls

| This plugin                            | tsh-platform-engineering                                            |
| :------------------------------------- | :------------------------------------------------------------------ |
| GCP resource patterns and defaults     | Terraform module structure, variables, state, Terragrunt, Terratest |
| GCP service inventory and waste checks | The cost framework: pricing models, tiering, labelling governance   |
| GCP cost report                        | Pipelines, Kubernetes, observability, secrets                       |
| —                                      | Cross-cloud service comparison and multi-cloud topology             |

Neither plugin file-links the other, because a path across plugins is not stable across install
modes. Both stand alone, and the model routes on descriptions.

## Related

- [Plugin overview](/docs/plugins/)
- [Changelog](/docs/changelog/tsh-stack-gcp)
