---
title: Optimizing Cloud Cost
sidebar_label: Optimizing Cloud Cost
sidebar_position: 6
description: The cloud-agnostic cost framework TSH provisions against - pricing models, storage tiering, right-sizing, cost-allocation tags, and the cost-impact estimate every infrastructure proposal carries.
sources:
  - plugins/tsh-platform-engineering/skills/optimizing-cloud-cost/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
  - plugins/tsh-stack-aws/skills/auditing-aws-cost/SKILL.md
  - plugins/tsh-stack-gcp/skills/auditing-gcp-cost/SKILL.md
  - plugins/tsh-stack-azure/skills/auditing-azure-cost/SKILL.md
sources_hash: "7fbdd2c77af83b4c46cead04d47744cc044df811e7204a3ff8453e0c95ae18bb"
---

# Optimizing Cloud Cost

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:optimizing-cloud-cost`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer), [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor). Also named by [`auditing-aws-cost`](/docs/plugins/tsh-stack-aws/skills/auditing-aws-cost), [`auditing-gcp-cost`](/docs/plugins/tsh-stack-gcp/skills/auditing-gcp-cost) and [`auditing-azure-cost`](/docs/plugins/tsh-stack-azure/skills/auditing-azure-cost) as the home of the cost framework and tagging governance.

The framework applied when provisioning and when estimating what a change will cost: which pricing model fits a workload shape, which storage tier fits an access pattern, and what every resource must be tagged with.

**It does not audit a live account.** That job is cloud-specific, because it needs the provider's service families, CLI verbs and billing API. Where the cloud's plugin is installed, `auditing-aws-cost` ([`tsh-stack-aws`](/docs/plugins/tsh-stack-aws/)), `auditing-gcp-cost` ([`tsh-stack-gcp`](/docs/plugins/tsh-stack-gcp/)) or `auditing-azure-cost` ([`tsh-stack-azure`](/docs/plugins/tsh-stack-azure/)) owns it.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file. A project's own tagging convention outranks the standard in the skill; the project's keys are used and the difference is reported. |
| **Pricing models** | Steady-state 24/7 workloads: reserved or committed capacity (30 to 72% saving). Variable or bursty: on-demand plus auto-scaling. Fault-tolerant batch: spot (up to 90%). Event-driven: serverless. Reserved or committed capacity pays off above roughly 70% sustained utilization. |
| **Storage tiering** | Hot, infrequent (30+ days), rare (90+ days) and archive (365+ days) tiers mapped across AWS, Azure and GCP, always paired with a lifecycle policy. Minimum storage duration per tier is checked first, because deleting early from a cold tier still bills the remainder. |
| **Right-sizing** | Based on observed utilization, sized to the peak the workload must serve, one dimension at a time (family, then size), and re-measured afterwards. A recommendation with no utilization behind it is labelled a guess. |
| **Cost-impact estimate** | New monthly run-rate itemized, the delta against current spend as a percentage, what is estimated versus measured, and the line items people forget: NAT and egress processing, cross-zone and cross-region transfer, idle load balancers, log ingestion, non-production managed-service charges and orphaned storage. Above a 10% projected increase the response opens with `⚠️ FINOPS ALERT: High Cost Impact`. |
| **Tagging** | The mandatory Core 5 tags: `CostCenter`, `Environment`, `Service`, `Owner` and `DataClass`, with `DataClass` mandatory on all storage and database resources. GCP uses a lowercase label dialect (`cost_center`, `data_class`). Workload tags exist for AI and ML (`ModelID`, `TrainingJobId`, `InferenceType`) and for lifecycle (`Schedule`, `Temporary`, `TTL`). Enforcement is preventive through organization-level policy, injected by IaC modules, with detective and corrective controls as fallbacks. |
| **Provisioning checklist** | Tags injected by the module, right-sizing on metrics, reserved capacity for sustained load, spot for batch, lifecycle policies, budget alerts at 50%, 80% and 100%, cost anomaly detection, auto-scaling and non-production scheduled off outside business hours. |
| **Rules** | Every proposal carries a cost estimate. Current instance families, machine types and pricing are verified against provider documentation before a size is recommended. Never report an estimated saving as measured, and never propose deleting a resource whose purpose is not established. |

Automated deletion of untagged resources is described as a policy decision for the account owner; the skill says to propose it and never implement it unasked.

## How it works

The skill has no numbered procedure. It is applied as a framework while provisioning: choose the pricing model and storage tier, right-size on measured utilization, tag at provisioning time, and state the cost-impact estimate with its estimated-versus-measured split.

## References

| Reference | Load when |
| :-- | :-- |
| `tagging-standards.md` | Provisioning anything, or setting up cost governance. Covers the mandatory tag set, workload-specific tags, the GCP label dialect, the compliance checks and the enforcement patterns. |

## Related skills

- [Implementing Terraform Modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules) - where sizing decisions become code.
- [Designing Multi-Cloud Architecture](/docs/plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture) - cross-cloud service and cost comparison.

## Source

- [`plugins/tsh-platform-engineering/skills/optimizing-cloud-cost/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost/SKILL.md)
- [`plugins/tsh-platform-engineering/skills/optimizing-cloud-cost/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost/references)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
