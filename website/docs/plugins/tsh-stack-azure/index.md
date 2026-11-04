---
title: 'TSH Stack: Azure'
sidebar_label: Overview
sidebar_position: 1
description: Azure Terraform module patterns with Well-Architected defaults and an evidence-based cost and tagging audit of a live subscription.
sources:
  - plugins/tsh-stack-azure/.claude-plugin/plugin.json
  - plugins/tsh-stack-azure/README.md
sources_hash: "73584c08dd0af34e1c540a5c904eab99c03b57ff8e15bb52575f3a42aa3b5254"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: Azure

Azure-specific infrastructure guidance: Terraform module patterns with Well-Architected defaults,
and a full evidence-based cost and tagging audit of a live subscription.

Install it alongside [tsh-platform-engineering](/docs/plugins/tsh-platform-engineering/), which
carries the cloud-agnostic half: module structure, state, pipelines, Kubernetes, observability,
secrets and the cost framework.

## Scope and installation

Install at **project scope**. The plugin belongs to an Azure repository, not to a person: a
repository has one cloud, while an engineer works across several. For the install commands, see
[Installation](/docs/getting-started/installation).

## What it covers

- **Terraform resource patterns.** VNet with per-subnet NSGs, AKS with Workload Identity and Entra
  RBAC, Flexible Server on private DNS, Blob Storage redundancy, Application Gateway with WAF, Key
  Vault with purge protection, ACR and Service Bus.
- **Cost and tag audit.** Infrastructure code first, then Resource Graph, drift and shadow
  resources, per-service waste checks, Cost Management attribution, reservation utilization and a
  saved report.

## Components

<PluginComponents plugin="tsh-stack-azure" />

The plugin ships no agents.

## MCP servers

None bundled. Terraform `azurerm` provider documentation, VM sizes and pricing tiers come from
`context7`, which `tsh-core` bundles; see [Context7](/docs/integrations/context7).

**No Azure control-plane MCP server is bundled.** Microsoft's `@azure/mcp` is still pre-release and
write-capable, so live subscription state is read through the `az` CLI (`list`, `show` and
`graph query`), where your own permission rules apply to every call. If you want the server, add it
to `.mcp.json` yourself; the skills' read-only-verb restriction applies either way.

## Azure traps the skills catch

- **Managed disks bill by provisioned performance tier, not bytes used.** A P30 costs the same at
  5 GB as at 1 TB, so an oversized tier on a small disk is invisible to any check that only looks at
  capacity.
- **Tags do not inherit from a resource group.** A tagged resource group full of untagged resources
  passes a naive compliance check and contributes nothing to cost allocation.
- **An App Service Plan bills whether or not it hosts a running app**, so stopping the app does not
  stop the bill.

## Where the line falls

| This plugin                              | tsh-platform-engineering                                            |
| :--------------------------------------- | :------------------------------------------------------------------ |
| Azure resource patterns and defaults     | Terraform module structure, variables, state, Terragrunt, Terratest |
| Azure service inventory and waste checks | The cost framework: pricing models, tiering, tagging governance     |
| Azure cost report                        | Pipelines, Kubernetes, observability, secrets                       |
| —                                        | Cross-cloud service comparison and multi-cloud topology             |

Neither plugin file-links the other, because a path across plugins is not stable across install
modes. Both stand alone, and the model routes on descriptions.

## Related

- [Plugin overview](/docs/plugins/)
- [Changelog](/docs/changelog/tsh-stack-azure)
