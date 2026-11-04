---
title: 'TSH Stack: AWS'
sidebar_label: Overview
sidebar_position: 1
description: AWS Terraform module patterns with Well-Architected defaults and an evidence-based cost and tagging audit of a live account.
sources:
  - plugins/tsh-stack-aws/.claude-plugin/plugin.json
  - plugins/tsh-stack-aws/README.md
  - plugins/tsh-stack-aws/.mcp.json
sources_hash: "a1c19e2aa15e20fb1d73627d0b7fcb62739d654e07e24c1fe253b1585056dfcb"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: AWS

AWS-specific infrastructure guidance: Terraform module patterns with Well-Architected defaults, and
a full evidence-based cost and tagging audit of a live account.

Install it alongside [tsh-platform-engineering](/docs/plugins/tsh-platform-engineering/), which
carries the cloud-agnostic half: module structure, state, pipelines, Kubernetes, observability,
secrets and the cost framework.

## Scope and installation

Install at **project scope**. The plugin belongs to an AWS repository, not to a person: a repository
has one cloud, while an engineer works across several. For the install commands, see
[Installation](/docs/getting-started/installation).

## What it covers

- **Terraform resource patterns.** VPC, EKS, RDS, S3, ALB, Lambda and security groups, with
  encryption, IAM and tagging defaults and provider pinning.
- **Cost and tag audit.** Infrastructure code first, then the live account through read-only API
  calls, drift and shadow resources, per-service waste checks, Cost Explorer attribution and a saved
  report.

## Components

<PluginComponents plugin="tsh-stack-aws" />

The plugin ships no agents.

## MCP servers

The plugin bundles one server, `aws-documentation`, the AWS Labs documentation server. It supplies
current instance families, pricing tiers and regional availability, and it is read-only. It is a
Python package launched with `uvx`, so it needs `uv` installed; without `uv` that one server fails
to start and everything else keeps working.

Terraform AWS provider documentation comes from `context7`, which `tsh-core` bundles. For both
servers, see the [integrations pages](/docs/integrations/aws-documentation) and
[Context7](/docs/integrations/context7).

**No write-capable AWS API server is bundled.** Live account state is read through the `aws` CLI with
`describe`, `list` and `get` verbs only, so your own permission rules apply to every call.

## Where the line falls

| This plugin                            | tsh-platform-engineering                                           |
| :------------------------------------- | :----------------------------------------------------------------- |
| AWS resource patterns and defaults     | Terraform module structure, variables, state, Terragrunt, Terratest |
| AWS service inventory and waste checks | The cost framework: pricing models, tiering, tagging governance     |
| AWS cost report                        | Pipelines, Kubernetes, observability, secrets                       |
| —                                      | Cross-cloud service comparison and multi-cloud topology             |

Neither plugin file-links the other, because a path across plugins is not stable across install
modes. Both stand alone, and the model routes on descriptions.

## Related

- [Plugin overview](/docs/plugins/)
- [Changelog](/docs/changelog/tsh-stack-aws)
