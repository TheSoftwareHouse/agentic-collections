---
title: TSH Platform Engineering
sidebar_label: Overview
sidebar_position: 0
description: Infrastructure, CI/CD and deployment the TSH way - Terraform modules, pipelines with OIDC and plan gates, Kubernetes workloads, observability with SLOs, secrets management and cloud cost audits.
sources:
  - plugins/tsh-platform-engineering/.claude-plugin/plugin.json
  - plugins/tsh-platform-engineering/README.md
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
  - plugins/tsh-platform-engineering/agents/devops-engineer.md
  - plugins/tsh-platform-engineering/agents/infrastructure-auditor.md
  - plugins/tsh-product-engineering/skills/debugging-code/SKILL.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md
  - plugins/tsh-stack-serverless/README.md
sources_hash: "5adb01758d07955da6696a17f75cf0f881a6d73c4ec7b0e24025845711587be4"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Platform Engineering

`tsh-platform-engineering` is the discipline plugin for infrastructure, CI/CD and deployment: Terraform modules, pipelines with OIDC and plan gates, production-shaped Kubernetes workloads, observability with SLOs, secrets management, and evidence-based cloud cost audits.

It is the cloud-agnostic half of TSH's infrastructure guidance. Everything specific to one cloud lives in that cloud's own plugin (see [Pairs with a cloud plugin](#pairs-with-a-cloud-plugin)).

## Who installs it

A discipline plugin travels with you, so install it at **user** scope. Install the repository's cloud plugin at **project** scope. The install commands and the scope table are on the [Installation](/docs/getting-started/installation) page.

## What it ships

<PluginComponents plugin="tsh-platform-engineering" />

Skills are invoked as `/tsh-platform-engineering:<skill>` and agents as `@tsh-platform-engineering:<agent>`.

## Conventions the plugin holds to

- **Nothing here applies infrastructure.** Where a skill or agent validates a change it uses `plan`, `validate`, `--dry-run=server` or `template`, and apply instructions go to a human. The [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer) agent carries an explicit mutation lock.
- **Every proposal carries a cost estimate**, and flags a projected increase above 10%.
- **The project's existing conventions win** over any default in the plugin. Each skill starts from the shared context file described below, which is also where the greenfield questions live.

## Shared context

`shared/discovering-infrastructure-context.md` is read by every skill in the plugin and by both agents, via `${CLAUDE_PLUGIN_ROOT}`. It keeps the detection logic in one place instead of repeating it across seven skills.

| Section | What it detects |
| :-- | :-- |
| Precedence | Order of authority: project instructions (`CLAUDE.md`, `.claude/rules/`, decision records, `infrastructure/README.md`, `.devops/instructions.md`), then existing infrastructure code, then provider documentation resolved against the pinned versions. An `Accepted` decision record settles the question it covers. |
| 1. CI/CD platform | GitHub Actions, Bitbucket Pipelines, GitLab CI, Azure Pipelines or Jenkins, from the pipeline file present. |
| 2. IaC dialect | Terraform, Terragrunt, raw Kubernetes manifests, Helm, Kustomize, CloudFormation, AWS CDK, Azure Bicep or Pulumi. |
| 3. Cloud provider and pinned versions | `versions.tf`, `required_providers`, `Chart.yaml`, `provider` blocks and `.terraform.lock.hcl`. |
| 4. Policy, secrets and state | Policy-as-code and linting, SOPS, Sealed Secrets, External Secrets Operator, HashiCorp Vault, and the remote state backend. |
| 5. Observability and GitOps | Prometheus, OpenTelemetry, log shippers, ArgoCD and Flux. |
| 6. Greenfield | When nothing exists, three questions asked with `AskUserQuestion`: target cloud, primary workload, expected scale. If the user declines, the default is managed containers, stated as a default and not a decision. |

Before implementing, the file requires a statement of the platform, dialect, cloud, pinned versions and any project convention that overrides a plugin default.

## Pairs with a cloud plugin

| Here | In the cloud plugin |
| :-- | :-- |
| Terraform module structure, variables, state, Terragrunt, Terratest | That cloud's resource patterns and service defaults |
| The cost framework: pricing models, tiering, tagging governance | That cloud's service inventory, waste checks and cost report |
| Pipelines, Kubernetes, observability, secrets | - |
| Cross-cloud comparison and multi-cloud topology | - |

Each of the three major clouds has a plugin:

- [`tsh-stack-aws`](/docs/plugins/tsh-stack-aws/)
- [`tsh-stack-gcp`](/docs/plugins/tsh-stack-gcp/)
- [`tsh-stack-azure`](/docs/plugins/tsh-stack-azure/)

Neither side links to the other by file path, because a path across plugins is not stable across install modes. Each plugin stands alone and the model routes on descriptions.

## MCP servers and hooks

The plugin bundles no MCP servers and no hooks. Provider, Kubernetes, Helm and CI platform documentation comes from `context7`, which `tsh-core` bundles and which is read-only (see the [context7 integration](/docs/integrations/context7)).

Cloud documentation and live-state servers ship with the cloud's own plugin: `aws-documentation` in `tsh-stack-aws`, the three Google Cloud servers in `tsh-stack-gcp`, and none in `tsh-stack-azure`. A GCP repository therefore never starts an AWS server, and no cloud server appears in a repository with no cloud plugin installed.

## Assumes tsh-core

The plugin references `/tsh-core:managing-decision-records` and `/tsh-core:writing-technical-documents` by name. Both degrade to a missing command, not an error, if `tsh-core` is absent. Install [`tsh-core`](/docs/plugins/tsh-core/) anyway; it depends on nothing.

## Referenced from other plugins

- [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) in `tsh-product-engineering` excludes infrastructure and deployment faults, such as a misconfigured pipeline, cluster or cloud resource, and assigns them to this plugin.
- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) lists this plugin (CI, deployment) among those that may not be installed, and says to name the gap to the user.
- [`tsh-stack-serverless`](/docs/plugins/tsh-stack-serverless/) leaves the deploy pipeline itself (CI system, OIDC, the deploy role) to this plugin.

## Source

- [`plugins/tsh-platform-engineering/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/.claude-plugin/plugin.json)
- [`plugins/tsh-platform-engineering/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/README.md)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
