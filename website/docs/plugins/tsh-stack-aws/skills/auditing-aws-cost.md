---
title: auditing-aws-cost
sidebar_label: auditing-aws-cost
sidebar_position: 1
description: Evidence-based AWS cost and tagging audit that reads infrastructure code, validates it against the live account read-only, and saves a report.
sources:
  - plugins/tsh-stack-aws/skills/auditing-aws-cost/SKILL.md
  - plugins/tsh-stack-aws/skills/auditing-aws-cost/references/
sources_hash: "ef0f32889d8e1d19ff5aec91563e8ce09f54f3672e44641197ea7fdc2754df29"
---

# auditing-aws-cost

**Plugin:** [tsh-stack-aws](/docs/plugins/tsh-stack-aws/)  
**Invoke:** `/tsh-stack-aws:auditing-aws-cost`. Claude also loads it when the work matches its
description.  
**Used by:** the [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor)
agent, which uses it for the per-service inventory and the report format where the plugin is
installed, and the [optimizing-cloud-cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost)
skill, which names it as the owner of live-account auditing where this plugin is installed.

Runs an exhaustive, evidence-based AWS cost and tagging audit. It reads Terraform or CloudFormation
first, then validates against the live account with read-only API calls, finds drift and shadow
resources, walks every service family for waste and right-sizing, checks tag compliance, and
attributes measured spend from Cost Explorer. It produces a saved, presentation-ready report.

The skill's method is to read the code, then check reality, then diff the two. The findings that
matter most are usually the ones with no infrastructure code behind them at all.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Run read-only: `describe-*`, `list-*`, `get-*` only. Remediation is produced as code for the user to apply, never applied. |
| MUST | Base right-sizing on utilization metrics or live API data. A recommendation with no observed utilization is a guess and is labelled as one. |
| MUST | Separate measured spend from estimate. Only Cost Explorer gives measured cost; anything derived from instance type and runtime hours is an estimate and the report says so. |
| MUST | Warn explicitly before proposing any change to a resource tagged as production. |
| MUST | Save the report file before presenting results, then state its path. |
| NEVER | Propose deleting a resource whose purpose has not been established. |
| NEVER | Present a code-only audit as though it reflected the live account. If credentials do not resolve, say so in the executive summary. |

The account's own tagging convention outranks the standard below: the skill reconciles to its keys
and reports the difference. Verifying current instance families, pricing tiers and regional
availability against AWS documentation before recommending a specific size is mandatory.

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Data sources, in order** | The `aws` CLI with read-only verbs, after confirming the account with `aws sts get-caller-identity`; Cost Explorer (`aws ce get-cost-and-usage`), the only source of measured spend; Compute Optimizer for utilization-backed right-sizing, and Trusted Advisor where the support tier includes it; the `aws-documentation` MCP server before recommending a type; `context7` for Terraform AWS provider docs used in remediation code. |
| **Service inventory** | Compute, storage, databases, networking, containers, serverless and AI/ML, and security and operations. The reference states that the recurring findings are under networking and operations rather than compute. |
| **Anti-patterns** | A table of findings and corrections, for example `gp2` volumes to `gp3`, previous-generation instances to current generation, a NAT gateway carrying S3 traffic to a gateway VPC endpoint, log groups with no retention. |
| **Pricing model** | Steady-state 24/7 workloads on Reserved Instances or Savings Plans, variable workloads on On-Demand with auto-scaling, fault-tolerant batch on Spot, event-driven on Lambda. Committed capacity pays off above roughly 70% sustained utilization. |
| **Storage tiering** | S3 Standard, Standard-IA (30+ days), Glacier (90+ days) and Deep Archive (365+ days) by access pattern, always paired with a lifecycle policy. |
| **Mandatory tags** | Five tags in `PascalCase`: `CostCenter`, `Environment`, `Service`, `Owner`, `DataClass`. It also checks `ModelID` and `TrainingJobId` on GPU instances and SageMaker endpoints, `DataClass` on every storage and database resource, and `Schedule` on anything tagged `Environment: dev` running 24/7. Tags are read with `aws resourcegroupstaggingapi get-resources`. |
| **Report** | Saved as `aws-cost-audit-<profile>-<region>-YYYY-MM-DD.md` in a fixed structure: executive summary, IaC versus live drift, optimization opportunities, tag compliance, critical security findings, summary, recommended action order. |

## How it works

1. **Confirm scope.** Account or profile, region or all regions, service focus. The default is
   exhaustive; the skill asks if the account is not identifiable.
2. **Read the infrastructure code first.** Terraform (`*.tf`, `terragrunt.hcl`) and CloudFormation.
   Extract what drives cost, such as `instance_type`, `allocated_storage`, `volume_size`,
   `desired_count`, `engine` and `multi_az`, and note anti-patterns.
3. **Inventory live state** with the service inventory checklist.
4. **Diff code against reality.** Three kinds of finding: in code but absent from AWS, in AWS but
   absent from code (shadow resources), and configuration drift.
5. **Find waste.** The inventory names the specific checks per service.
6. **Check tag compliance** against the mandatory tags.
7. **Attribute cost.** Cost Explorer for measured spend, otherwise an estimate labelled as such. For
   each opportunity the skill gives a Golden Path (balanced), a Cost-Optimized Path (maximum saving)
   and a Velocity Path (highest performance).
8. **Save the report, then present it.**

After presenting, the skill asks exactly one follow-up question: whether to generate Terraform code
to implement the optimizations. The audit itself is analysis-only. It generates remediation
Terraform only after the user names which opportunities to implement, and shows a diff before
writing to any existing file.

## Related skills

- [implementing-aws-terraform](/docs/plugins/tsh-stack-aws/skills/implementing-aws-terraform), the
  provisioning patterns in this plugin.
- [optimizing-cloud-cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost) in
  tsh-platform-engineering, the cloud-agnostic cost framework, tagging governance and provisioning
  checklists.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-aws/skills/auditing-aws-cost/SKILL.md)
- [`references/service-inventory.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-aws/skills/auditing-aws-cost/references/service-inventory.md)
- [`references/report-format.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-aws/skills/auditing-aws-cost/references/report-format.md)
