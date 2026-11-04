---
title: auditing-azure-cost
sidebar_label: auditing-azure-cost
sidebar_position: 1
description: Evidence-based Azure cost and tagging audit driven by Resource Graph and Cost Management, read-only against the live subscription, with a saved report.
sources:
  - plugins/tsh-stack-azure/skills/auditing-azure-cost/SKILL.md
  - plugins/tsh-stack-azure/skills/auditing-azure-cost/references/
sources_hash: "b01a9bda6d06d7b8463a303d02a4e77bd5dfb951762dc7c64591717d35b5dad5"
---

# auditing-azure-cost

**Plugin:** [tsh-stack-azure](/docs/plugins/tsh-stack-azure/)  
**Invoke:** `/tsh-stack-azure:auditing-azure-cost`. Claude also loads it when the work matches its
description.  
**Used by:** the [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor)
agent, which uses it for the per-service inventory and the report format where the plugin is
installed, and the [optimizing-cloud-cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost)
skill, which names it as the owner of live-subscription auditing where this plugin is installed.

Runs an exhaustive, evidence-based Azure cost and tagging audit. It reads Terraform or Bicep first,
then inventories the live subscription with Resource Graph and read-only `az` calls, finds drift and
shadow resources, walks every service family for waste and right-sizing, checks tag compliance
against Azure's non-inheriting tag model, and attributes measured spend from Cost Management. It
produces a saved, presentation-ready report.

The skill's method is to read the code, then check reality, then diff the two. Two Azure traps it
always checks: disks bill by provisioned performance tier, not bytes used, and tags do not inherit
from a resource group, so cost allocation silently under-reports.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Run read-only: `az ... list`, `show`, `graph query` and Cost Management queries only. Remediation is produced as code for the user to apply, never applied. |
| MUST | Base right-sizing on utilization metrics or Azure Advisor output. A recommendation with no observed utilization is a guess and is labelled as one. |
| MUST | Separate measured spend from estimate. Only Cost Management gives measured cost; anything derived from SKU and runtime hours is an estimate and the report says so. |
| MUST | Check reservation and savings-plan utilization, not just coverage. An under-used reservation is a finding in its own right. |
| MUST | Warn before proposing any change to a resource tagged as production or carrying a `CanNotDelete` lock, and save the report file before presenting results. |
| NEVER | Propose deleting a resource whose purpose has not been established. |
| NEVER | Present a code-only audit as though it reflected the live subscription. If access does not resolve, say so in the executive summary. |

The subscription's own tagging convention outranks the standard below: the skill reconciles to its
keys and reports the difference. Verifying current VM sizes, pricing tiers and regional availability
with `context7` before recommending a specific size is mandatory.

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Data sources, in order** | Azure Resource Graph (`az graph query`) as the primary inventory tool, after confirming the subscription with `az account show`; Cost Management (`az costmanagement query`), the only source of measured spend; Azure Advisor (`az advisor recommendation list --category Cost`); reservations and savings plans through `az reservations reservation-order list` and the utilization APIs; `context7` for current VM sizes, pricing tiers, regional availability and `azurerm` provider docs. |
| **Service inventory** | Compute, storage (including blob tiering and redundancy), databases, networking, operations and security, security findings and governance. The reference starts from a single Resource Graph query for the whole estate, then drills in. |
| **Pricing model** | Reserved VM Instances for steady-state known VM families, Azure Savings Plan for compute where flexibility across families is needed, pay-as-you-go with autoscaling for variable load, Spot VMs for fault-tolerant batch, Functions on the Consumption plan for event-driven work. Azure Hybrid Benefit is named as the lever people miss, and reserved capacity for SQL Database, Cosmos DB and storage as routinely unbought. |
| **Blob tiering and redundancy** | Hot, Cool (30+ days), Cold (90+ days) and Archive (365+ days) by access pattern, paired with a lifecycle policy and the minimum retention period of each tier. Redundancy is called the bigger lever: `account_replication_type` is checked on every account against a stated recovery objective. |
| **Mandatory tags** | Five tags in `PascalCase`: `CostCenter`, `Environment`, `Service`, `Owner`, `DataClass`. Because tags do not inherit, resources are checked individually, and resource types that accept no tags are listed separately rather than as failures. It also checks `DataClass` on every storage and database resource and `Schedule` on anything tagged `Environment: dev` running 24/7. |
| **Report** | Saved as `azure-cost-audit-<subscription>-<region>-YYYY-MM-DD.md` in a fixed structure: executive summary, IaC versus live drift, optimization opportunities, tag compliance, critical security findings, summary (including reservation and savings-plan utilization and Hybrid Benefit coverage), recommended action order. |

## How it works

1. **Confirm scope.** Subscription, resource groups, region, service focus. The default is
   exhaustive; the skill asks if the subscription is not identifiable.
2. **Read the infrastructure code first.** Terraform (`*.tf`, `terragrunt.hcl`) and Bicep or ARM
   (`*.bicep`, `azuredeploy.json`). Extract what drives cost, such as VM `size`, disk
   `storage_account_type`, `sku_name`, `account_replication_type`, node counts and `capacity`, and
   note anti-patterns.
3. **Inventory live state** with Resource Graph, then walk the service inventory.
4. **Diff code against reality.** Three kinds of finding: in code but absent from Azure, in Azure but
   absent from code (shadow resources), and configuration drift.
5. **Find waste.** The inventory names the checks per service.
6. **Check tag compliance** resource by resource.
7. **Attribute cost.** Cost Management for measured spend, otherwise an estimate from SKU and runtime
   hours, labelled as such. Review reservation and savings-plan utilization and whether Hybrid
   Benefit is applied. Each opportunity gets a Golden Path (balanced), a Cost-Optimized Path (maximum
   saving) and a Velocity Path (performance).
8. **Save the report, then present it.**

After presenting, the skill asks exactly one follow-up question: whether to generate Terraform code
to implement the optimizations. The audit itself is analysis-only. It generates remediation
Terraform only after the user names which opportunities to implement, and shows a diff before
writing to any existing file.

## Related skills

- [implementing-azure-terraform](/docs/plugins/tsh-stack-azure/skills/implementing-azure-terraform),
  the provisioning patterns in this plugin.
- [optimizing-cloud-cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost) in
  tsh-platform-engineering, the cloud-agnostic cost framework and tagging governance.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-azure/skills/auditing-azure-cost/SKILL.md)
- [`references/service-inventory.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-azure/skills/auditing-azure-cost/references/service-inventory.md)
- [`references/report-format.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-azure/skills/auditing-azure-cost/references/report-format.md)
