---
title: Implementing Terraform Modules
sidebar_label: Implementing Terraform Modules
sidebar_position: 1
description: Writes and reviews reusable Terraform modules for AWS, Azure and GCP - file layout, variable validation, outputs, provider pinning, remote state with locking, Terraform versus Terragrunt, and Terratest.
sources:
  - plugins/tsh-platform-engineering/skills/implementing-terraform-modules/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
  - plugins/tsh-stack-aws/skills/implementing-aws-terraform/SKILL.md
  - plugins/tsh-stack-gcp/skills/implementing-gcp-terraform/SKILL.md
  - plugins/tsh-stack-azure/skills/implementing-azure-terraform/SKILL.md
sources_hash: "50e1c5dc5ee74213711d02d21ee3f5ec39e9ce2a16b3c336a435cde2b7f79778"
---

# Implementing Terraform Modules

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:implementing-terraform-modules`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer), [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor). Also named by the cloud plugin skills [`implementing-aws-terraform`](/docs/plugins/tsh-stack-aws/skills/implementing-aws-terraform), [`implementing-gcp-terraform`](/docs/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform) and [`implementing-azure-terraform`](/docs/plugins/tsh-stack-azure/skills/implementing-azure-terraform) as the home of generic Terraform mechanics.

Treats a module as an interface before it is a set of resources: the variables, outputs and version constraints are what every consumer inherits. This is the module-structure layer, loaded alongside the cloud provider's own resource patterns and not instead of them.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file (sections 2 and 3: dialect and pinned versions). A `*.plan.md` Technical Context is the primary source when one exists. The project's existing module conventions outrank everything in the skill; a second convention introduced alongside the first is a finding. |
| **Module interface** | Semantic versioning on published modules. Every variable typed and described, with a `validation` block where a bad value is expensive. Every attribute a consumer could need exported as an output. `locals` for computed values, `count` or `for_each` for conditional and repeated resources, and an `examples/complete/` that actually runs. |
| **Module layout** | `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`, `examples/complete/` and `tests/module_test.go`. A shared module library is grouped by provider, then by component. |
| **State and providers** | Remote state with locking before anything is applied. Provider versions pinned in `versions.tf` with the lock file committed. Starting-point constraints are `aws ~> 6.0`, `azurerm ~> 4.0` and `google ~> 5.0`, to be verified against the project's pins with `context7`. |
| **Terraform or Terragrunt** | Plain Terraform for a single environment or region, two or three environments in one region, or any existing project not already on Terragrunt. Terragrunt for four or more environments, multi-region, a monorepo of independent stacks, strict environment parity, multi-account AWS, or greenfield with known growth. Never migrate mid-project as a side effect of another change. |
| **Testing** | Terratest with `examples/complete/` as the fixture and `tests/module_test.go` running `InitAndApply` with a deferred `Destroy`. Always `t.Parallel()`, `terraform.WithDefaultRetryableErrors`, a fixture path from `runtime.Caller(0)`, cost-reducing flags, a plan-only variant for pull requests, a dedicated test account and `-timeout 30m` in CI. Assertions target the module's interface, not generated resource names. |
| **Cost and tags** | A cost estimate for new resources, opening with `⚠️ FINOPS ALERT: High Cost Impact` if projected spend rises more than 10%. The project's mandatory tags on every taggable resource, merged so consumers can add their own. |
| **Safety** | Never `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action; apply instructions are delivered instead. No secrets in variable defaults or committed `.tfvars`. No manual console changes. |

## How it works

1. **Discover** the dialect, provider versions, state backend and environment layout from the shared context file and the plan's Technical Context.
2. **Confirm state.** A remote backend with locking comes first; if it is missing, that is the first change.
3. **Choose Terraform or Terragrunt** using the decision criteria above.
4. **Look up current syntax** with `context7` for the pinned provider version.
5. **Write the module** to the standard layout, loading the cloud-specific reference for resource patterns.
6. **Validate** with `terraform fmt -check`, `terraform validate` and `terraform plan -out=tfplan`, plus `tflint`, and `tfsec` or `checkov` where the project has them.
7. **Estimate cost** for new resources.
8. **Deliver apply instructions** without applying.

The output is a Terraform Implementation Summary: current state, proposed configuration, a variables table, state backend, cost estimate, apply instructions and files changed.

## References

| Reference | Load when |
| :-- | :-- |
| `module-structure.md` | Creating a module or reviewing its shape. Covers the standard layout and a worked AWS VPC module. |
| `terragrunt.md` | More than three environments, multi-region, multi-account, or `terragrunt.hcl` present. Covers the Terragrunt layout (root `terragrunt.hcl`, `_envcommon/`, `env.hcl`) and its cautions: `run-all apply` applies everything it resolves, and dependency blocks need foundational stacks applied first. |
| `testing-modules.md` | Adding or reviewing module tests. |

## Cloud-specific patterns live elsewhere

Resource families, service defaults and anti-patterns for each provider are in the cloud plugin's own skill: [`implementing-aws-terraform`](/docs/plugins/tsh-stack-aws/skills/implementing-aws-terraform) in [`tsh-stack-aws`](/docs/plugins/tsh-stack-aws/), [`implementing-gcp-terraform`](/docs/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform) in [`tsh-stack-gcp`](/docs/plugins/tsh-stack-gcp/), and [`implementing-azure-terraform`](/docs/plugins/tsh-stack-azure/skills/implementing-azure-terraform) in [`tsh-stack-azure`](/docs/plugins/tsh-stack-azure/). Use them where the repository's cloud plugin is installed.

## Related skills

- [Implementing CI/CD Pipelines](/docs/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines) - running plan and apply safely in a pipeline.
- [Managing Secrets](/docs/plugins/tsh-platform-engineering/skills/managing-secrets) - credentials and state hygiene.
- [Optimizing Cloud Cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost) - sizing and pricing model.
- [Designing Multi-Cloud Architecture](/docs/plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture) - service selection before provisioning.

## Source

- [`plugins/tsh-platform-engineering/skills/implementing-terraform-modules/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/implementing-terraform-modules/SKILL.md)
- [`plugins/tsh-platform-engineering/skills/implementing-terraform-modules/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-platform-engineering/skills/implementing-terraform-modules/references)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
