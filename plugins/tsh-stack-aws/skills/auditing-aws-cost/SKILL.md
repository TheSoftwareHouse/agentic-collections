---
name: auditing-aws-cost
description: "Runs an exhaustive evidence-based AWS cost and tagging audit: reads Terraform or CloudFormation first, then validates against the live account with read-only API calls, finds drift and shadow resources, walks every service family for waste and right-sizing, checks tag compliance, and attributes measured spend from Cost Explorer. Produces a saved, presentation-ready report. Use for a FinOps or cost review of an AWS account."
when_to_use: "Trigger on: 'audit our AWS costs', an AWS bill that jumped, a FinOps or cost-optimization review of an account or region, right-sizing EC2 or RDS, finding unattached EBS volumes, unassociated Elastic IPs, orphaned snapshots or idle load balancers, NAT gateway spend, AWS tag compliance, reserved instances or Savings Plans versus on-demand, S3 lifecycle and storage classes, or Cost Explorer analysis."
---

# Auditing AWS Cost

Read the code, then check reality, then diff the two. The findings that matter most are
usually the ones with no infrastructure code behind them at all.

## Applicability and Precedence

The account's own tagging convention outranks the standard below — reconcile to its
keys and report the difference rather than introducing a second scheme.

Verify current instance families, pricing tiers and regional availability against AWS
documentation before recommending any specific size. **This is mandatory**: these
change every few months, and a recommendation for an instance type unavailable in the
customer's region wastes the whole finding.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run read-only. `describe-*`, `list-*`, `get-*` only. Produce remediation as code for the user to apply; never apply it. |
| MUST | Base right-sizing on utilization metrics or live API data. A recommendation with no observed utilization behind it is a guess and must be labelled as one. |
| MUST | Separate measured spend from estimate. Only Cost Explorer gives measured cost; anything derived from instance type and runtime hours is an estimate and the report says so. |
| MUST | Warn explicitly before proposing any change to a resource tagged as production. |
| MUST | Save the report file before presenting results, then state its path. |
| NEVER | Propose deleting a resource whose purpose you have not established. An unattached volume may be the only copy of something. |
| NEVER | Present a code-only audit as though it reflected the live account. If credentials do not resolve, say so in the executive summary. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Service inventory](./references/service-inventory.md) | Always — this is the checklist the audit walks | Every service family, what to check in each, AWS-specific waste patterns |
| [Report format](./references/report-format.md) | Producing the report | The exact required structure and formatting rules |

## Data sources, in order

1. **The `aws` CLI via Bash**, read-only verbs. Confirm the account first with
   `aws sts get-caller-identity`, and the region.
2. **Cost Explorer** — `aws ce get-cost-and-usage`, grouped by service and by tag. The
   only source of measured spend.
3. **Compute Optimizer** —
   `aws compute-optimizer get-ec2-instance-recommendations` for utilization-backed
   right-sizing. Trusted Advisor where the support tier includes it.
4. **The `aws-documentation` MCP server** — current instance families, pricing tiers,
   regional availability. Mandatory before recommending a specific type.
5. **`context7`** — Terraform AWS provider docs for any remediation code.

## Pricing model

| Workload | Purchase option | Saving |
| :-- | :-- | :-- |
| Steady-state, 24/7 | Reserved Instances or Savings Plans | 30–72% |
| Variable or bursty | On-Demand with auto-scaling | baseline |
| Fault-tolerant batch | Spot | up to 90% |
| Event-driven | Lambda | per-use |

Reserved or committed capacity pays off above roughly 70% sustained utilization; below
that, on-demand plus auto-scaling usually wins.

## Storage tiering

| Access pattern | Class |
| :-- | :-- |
| Frequent | S3 Standard |
| Infrequent, 30+ days | S3 Standard-IA |
| Rare, 90+ days | S3 Glacier |
| Archive, 365+ days | S3 Deep Archive |

Always pair a class with a lifecycle policy that transitions automatically. A
hand-picked class decays as soon as access patterns change.

## Mandatory tags

Every resource carries all five, keys in `PascalCase`:

| Key | Example | Purpose |
| :-- | :-- | :-- |
| `CostCenter` | `cc-102` | Chargeback |
| `Environment` | `dev`, `staging`, `prod` | Deployment stage |
| `Service` | `auth-api` | The workload |
| `Owner` | `platform-team` | Responsible team |
| `DataClass` | `public`, `confidential`, `pii` | Security classification |

Also check: `ModelID` and `TrainingJobId` on GPU instances and SageMaker endpoints;
`DataClass` on every storage and database resource without exception; and `Schedule` on
anything tagged `Environment: dev` running 24/7 — a development resource with no
schedule is the most common cheap win.

Read tags with `aws resourcegroupstaggingapi get-resources`, which covers most services
in one call.

## Procedure

```text
Audit progress:
- [ ] 1. Scope confirmed (account, region, service focus)
- [ ] 2. Infrastructure code analysed
- [ ] 3. Live state inventoried
- [ ] 4. Drift and shadow resources identified
- [ ] 5. Waste and right-sizing found
- [ ] 6. Tag compliance checked
- [ ] 7. Cost attributed, savings estimated
- [ ] 8. Report saved, then presented
```

1. **Confirm scope.** Account or profile, region or all regions, service focus. Default
   to exhaustive. Ask if the account is not identifiable.
2. **Read the infrastructure code first.** Find Terraform (`*.tf`, `terragrunt.hcl`) and
   CloudFormation (`AWSTemplateFormatVersion`). Extract everything that drives cost:
   `instance_type`, `allocated_storage`, `volume_size`, `desired_count`, `engine`,
   `multi_az`. Note anti-patterns — hardcoded sizes, missing lifecycle policies,
   over-provisioned module defaults, unused outputs.
3. **Inventory live state** with the checklist in
   [service-inventory.md](./references/service-inventory.md).
4. **Diff code against reality.** Three findings: in code but absent from AWS, in AWS
   but absent from code (**shadow resources**), and configuration drift.
5. **Find waste** — the inventory names the specific checks per service.
6. **Check tag compliance** against the table above.
7. **Attribute cost.** Cost Explorer for measured spend; estimate from type and runtime
   hours otherwise and label it. For each opportunity give a **Golden Path**
   (balanced), **Cost-Optimized Path** (maximum saving) and **Velocity Path** (highest
   performance).
8. **Save the report, then present it** — see
   [report-format.md](./references/report-format.md).

The audit is analysis-only. Generate remediation Terraform only after the user names
which opportunities to implement, and show a diff before writing to any existing file.

## Related

Cloud-agnostic cost framework, tagging governance and provisioning checklists live in
`optimizing-cloud-cost` in the `tsh-platform-engineering` plugin. Provisioning patterns
are [implementing AWS Terraform](../implementing-aws-terraform/SKILL.md) in this plugin.
