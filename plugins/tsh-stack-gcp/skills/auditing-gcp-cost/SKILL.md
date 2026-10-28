---
name: auditing-gcp-cost
description: "Runs an exhaustive evidence-based GCP cost and labelling audit: reads Terraform first, then validates against the live project with read-only gcloud calls, finds drift and shadow resources, walks every service family for waste and right-sizing, checks label compliance, and attributes measured spend from the BigQuery billing export. Produces a saved, presentation-ready report. Use for a FinOps or cost review of a GCP project."
when_to_use: "Trigger on: 'audit our GCP costs', a Google Cloud bill that jumped, a FinOps or cost-optimization review of a project, right-sizing Compute Engine or Cloud SQL, finding unattached persistent disks, reserved unused static IPs, orphaned snapshots or idle load balancers, Cloud NAT or Cloud Logging ingestion spend, GCP label compliance, committed use discounts versus on-demand, Cloud Storage class and lifecycle review, or GKE node pool and Cloud Run sizing."
---

# Auditing GCP Cost

Read the code, then check reality, then diff the two. The findings that matter most are
usually the ones with no infrastructure code behind them at all.

## Applicability and Precedence

The project's own labelling convention outranks the standard below — reconcile to its
keys and report the difference rather than introducing a second scheme.

Verify current machine types, pricing tiers and regional availability with `context7`
before recommending any specific size. **This is mandatory**: a recommendation for a
machine type unavailable in the customer's region wastes the whole finding.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run read-only. `list`, `describe`, `get` only. The bundled `gcp-gcloud` server can run mutating `gcloud` commands; an audit never does. |
| MUST | Base right-sizing on utilization metrics or Recommender output. A recommendation with no observed utilization behind it is a guess and must be labelled as one. |
| MUST | Separate measured spend from estimate. Only the BigQuery billing export gives measured cost; anything derived from machine type and runtime hours is an estimate and the report says so. |
| MUST | Warn explicitly before proposing any change to a resource labelled as production. |
| MUST | Save the report file before presenting results, then state its path. |
| NEVER | Propose deleting a resource whose purpose you have not established. An unattached disk may be the only copy of something. |
| NEVER | Present a code-only audit as though it reflected the live project. If access does not resolve, say so in the executive summary. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Service inventory](./references/service-inventory.md) | Always — this is the checklist the audit walks | Every service family, what to check in each, GCP-specific waste patterns |
| [Report format](./references/report-format.md) | Producing the report | The exact required structure and formatting rules |

## Data sources, in order

1. **`gcp-gcloud`** MCP server, restricted to `list`, `describe` and `get`. Confirm the
   active project first with `gcloud config get-value project`. Falls back to the
   `gcloud` CLI via Bash where the server is unavailable.
2. **`gcp-storage`** for bucket inventory, lifecycle policies and storage classes, and
   **`gcp-observability`** for logging and monitoring configuration — including
   retention and exclusions, usually the largest observability line item.
3. **BigQuery billing export** — the only source of measured spend. Query the export
   table if the project has one; `gcloud billing budgets list` shows what alerting
   exists. Without an export, cost is estimated and the report must say so.
4. **Recommender** — `gcloud recommender recommendations list` with
   `--recommender=google.compute.instance.MachineTypeRecommender` for utilization-backed
   right-sizing, plus the idle-resource recommenders for waste.
5. **`context7`** — current machine types, pricing tiers, and Terraform Google provider
   docs for remediation code.

## Pricing model

| Workload | Purchase option | Saving |
| :-- | :-- | :-- |
| Steady-state, 24/7 | Committed use discount, 1 or 3 year | 30–70% |
| Variable or bursty | On-demand with autoscaling, plus sustained-use discount | baseline |
| Fault-tolerant batch | Spot VMs | up to 91% |
| Event-driven | Cloud Run or Cloud Functions | per-use |

Sustained-use discounts apply automatically on Compute Engine, so the comparison is
committed-use versus already-discounted on-demand — not against list price.

## Storage tiering

| Access pattern | Class |
| :-- | :-- |
| Frequent | Standard |
| Infrequent, 30+ days | Nearline |
| Rare, 90+ days | Coldline |
| Archive, 365+ days | Archive |

Always pair a class with a lifecycle rule that transitions automatically. Note the
minimum storage duration per class — deleting from Coldline early still bills the
remainder.

## Mandatory labels

GCP labels permit only lowercase letters, numbers, dashes and underscores:

| Label | Example | Purpose |
| :-- | :-- | :-- |
| `cost_center` | `cc-102` | Chargeback |
| `environment` | `dev`, `staging`, `prod` | Deployment stage |
| `service` | `auth-api` | The workload |
| `owner` | `platform-team` | Responsible team |
| `data_class` | `public`, `confidential`, `pii` | Security classification |

Also check: `model_id` and `training_job_id` on GPU instances and Vertex AI endpoints;
`data_class` on every storage and database resource without exception; and `schedule` on
anything labelled `environment: dev` running 24/7 — a development resource with no
schedule is the most common cheap win.

Read labels project-wide with `gcloud asset search-all-resources --format=json`.

## Procedure

```text
Audit progress:
- [ ] 1. Scope confirmed (project, region, service focus)
- [ ] 2. Infrastructure code analysed
- [ ] 3. Live state inventoried
- [ ] 4. Drift and shadow resources identified
- [ ] 5. Waste and right-sizing found
- [ ] 6. Label compliance checked
- [ ] 7. Cost attributed, savings estimated
- [ ] 8. Report saved, then presented
```

1. **Confirm scope.** Project ID, region or all regions, service focus. Default to
   exhaustive. Ask if the project is not identifiable.
2. **Read the infrastructure code first.** Find Terraform (`*.tf`, `terragrunt.hcl`); Deployment
   Manager lost support on 2026-04-01 and is turned down after 2027-06-30, so treat
   any remaining templates as a migration finding, not a source. Extract everything that drives cost: `machine_type`,
   `disk_size_gb`, `disk_type`, `tier`, `availability_type`, node counts. Note
   anti-patterns — hardcoded machine types, missing lifecycle rules, over-provisioned
   module defaults, uncapped disk autoresize.
3. **Inventory live state** with the checklist in
   [service-inventory.md](./references/service-inventory.md).
4. **Diff code against reality.** Three findings: in code but absent from GCP, in GCP
   but absent from code (**shadow resources**), and configuration drift.
5. **Find waste** — the inventory names the specific checks per service.
6. **Check label compliance** against the table above.
7. **Attribute cost.** Billing export for measured spend; estimate from machine type and
   runtime hours otherwise and label it. For each opportunity give a **Golden Path**
   (balanced), **Cost-Optimized Path** (maximum saving) and **Velocity Path** (highest
   performance).
8. **Save the report, then present it** — see
   [report-format.md](./references/report-format.md).

The audit is analysis-only. Generate remediation Terraform only after the user names
which opportunities to implement, and show a diff before writing to any existing file.

## Related

Cloud-agnostic cost framework, labelling governance and provisioning checklists live in
`optimizing-cloud-cost` in the `tsh-platform-engineering` plugin. Provisioning patterns
are [implementing GCP Terraform](../implementing-gcp-terraform/SKILL.md) in this plugin.
