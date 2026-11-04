---
title: auditing-gcp-cost
sidebar_label: auditing-gcp-cost
sidebar_position: 1
description: Evidence-based GCP cost and labelling audit that reads infrastructure code, validates it against the live project read-only, and saves a report.
sources:
  - plugins/tsh-stack-gcp/skills/auditing-gcp-cost/SKILL.md
  - plugins/tsh-stack-gcp/skills/auditing-gcp-cost/references/
sources_hash: "8756591857208d7685f6bf8e0223bc1840fd70c09be4c12f641fdb4f755eee38"
---

# auditing-gcp-cost

**Plugin:** [tsh-stack-gcp](/docs/plugins/tsh-stack-gcp/)  
**Invoke:** `/tsh-stack-gcp:auditing-gcp-cost`. Claude also loads it when the work matches its
description.  
**Used by:** the [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor)
agent, which uses it for the per-service inventory and the report format where the plugin is
installed, and the [optimizing-cloud-cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost)
skill, which names it as the owner of live-project auditing where this plugin is installed.

Runs an exhaustive, evidence-based GCP cost and labelling audit. It reads Terraform first, then
validates against the live project with read-only `gcloud` calls, finds drift and shadow resources,
walks every service family for waste and right-sizing, checks label compliance, and attributes
measured spend from the BigQuery billing export. It produces a saved, presentation-ready report.

The skill's method is to read the code, then check reality, then diff the two. The findings that
matter most are usually the ones with no infrastructure code behind them at all.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Run read-only: `list`, `describe`, `get` only. The bundled `gcp-gcloud` server can run mutating `gcloud` commands; an audit never does. |
| MUST | Base right-sizing on utilization metrics or Recommender output. A recommendation with no observed utilization is a guess and is labelled as one. |
| MUST | Separate measured spend from estimate. Only the BigQuery billing export gives measured cost; anything derived from machine type and runtime hours is an estimate and the report says so. |
| MUST | Warn explicitly before proposing any change to a resource labelled as production. |
| MUST | Save the report file before presenting results, then state its path. |
| NEVER | Propose deleting a resource whose purpose has not been established. |
| NEVER | Present a code-only audit as though it reflected the live project. If access does not resolve, say so in the executive summary. |

The project's own labelling convention outranks the standard below: the skill reconciles to its keys
and reports the difference. Verifying current machine types, pricing tiers and regional availability
with `context7` before recommending a specific size is mandatory.

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Data sources, in order** | The `gcp-gcloud` MCP server restricted to `list`, `describe` and `get`, after confirming the active project with `gcloud config get-value project`, with the `gcloud` CLI through Bash as the fallback; `gcp-storage` for buckets, lifecycle policies and storage classes; `gcp-observability` for logging and monitoring configuration, including retention and exclusions; the BigQuery billing export, the only source of measured spend; Recommender for utilization-backed right-sizing and idle resources; `context7` for current machine types, pricing tiers and Terraform Google provider docs. |
| **Service inventory** | Compute, storage, databases, networking, containers, serverless and AI/ML, and security and operations. The reference states that the recurring findings are under networking and operations rather than compute. |
| **Anti-patterns** | A table of findings and corrections, for example `pd-ssd` to `pd-balanced`, `n1` machine types to `e2` or `n2`, Cloud NAT carrying Google API traffic to Private Google Access, logging with no exclusions. |
| **Pricing model** | Steady-state 24/7 workloads on committed use discounts (1 or 3 year), variable workloads on On-Demand with autoscaling plus sustained-use discount, fault-tolerant batch on Spot VMs, event-driven on Cloud Run or Cloud Functions. Because sustained-use discounts apply automatically on Compute Engine, the comparison is committed-use against already-discounted on-demand. |
| **Storage tiering** | Standard, Nearline (30+ days), Coldline (90+ days) and Archive (365+ days) by access pattern, paired with a lifecycle rule and with the minimum storage duration of each class in mind. |
| **Mandatory labels** | Five labels, lowercase letters, numbers, dashes and underscores only: `cost_center`, `environment`, `service`, `owner`, `data_class`. It also checks `model_id` and `training_job_id` on GPU instances and Vertex AI endpoints, `data_class` on every storage and database resource, and `schedule` on anything labelled `environment: dev` running 24/7. Labels are read with `gcloud asset search-all-resources --format=json`. |
| **Report** | Saved as `gcp-cost-audit-<project>-<region>-YYYY-MM-DD.md` in a fixed structure: executive summary, IaC versus live drift, optimization opportunities, label compliance, critical security findings, summary, recommended action order. |

## How it works

1. **Confirm scope.** Project ID, region or all regions, service focus. The default is exhaustive;
   the skill asks if the project is not identifiable.
2. **Read the infrastructure code first.** Terraform (`*.tf`, `terragrunt.hcl`). Remaining Deployment
   Manager templates are treated as a migration finding, not as a source. Extract what drives cost,
   such as `machine_type`, `disk_size_gb`, `disk_type`, `tier`, `availability_type` and node counts,
   and note anti-patterns.
3. **Inventory live state** with the service inventory checklist.
4. **Diff code against reality.** Three kinds of finding: in code but absent from GCP, in GCP but
   absent from code (shadow resources), and configuration drift.
5. **Find waste.** The inventory names the specific checks per service.
6. **Check label compliance** against the mandatory labels.
7. **Attribute cost.** The billing export for measured spend, otherwise an estimate from machine type
   and runtime hours, labelled as such. Without an export the report must say so. For each
   opportunity the skill gives a Golden Path (balanced), a Cost-Optimized Path (maximum saving) and a
   Velocity Path (highest performance).
8. **Save the report, then present it.**

After presenting, the skill asks exactly one follow-up question: whether to generate Terraform code
to implement the optimizations. The audit itself is analysis-only. It generates remediation
Terraform only after the user names which opportunities to implement, and shows a diff before
writing to any existing file.

## Related skills

- [implementing-gcp-terraform](/docs/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform), the
  provisioning patterns in this plugin.
- [optimizing-cloud-cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost) in
  tsh-platform-engineering, the cloud-agnostic cost framework, labelling governance and provisioning
  checklists.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-gcp/skills/auditing-gcp-cost/SKILL.md)
- [`references/service-inventory.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-gcp/skills/auditing-gcp-cost/references/service-inventory.md)
- [`references/report-format.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-gcp/skills/auditing-gcp-cost/references/report-format.md)
