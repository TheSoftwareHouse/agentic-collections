---
name: auditing-azure-cost
description: "Runs an exhaustive evidence-based Azure cost and tagging audit: reads Terraform or Bicep first, then inventories the live subscription with Resource Graph and read-only az calls, finds drift and shadow resources, walks every service family for waste and right-sizing, checks tag compliance against Azure's non-inheriting tag model, and attributes measured spend from Cost Management. Produces a saved, presentation-ready report. Use for a FinOps or cost review of an Azure subscription."
when_to_use: "Trigger on: 'audit our Azure costs', an Azure bill that jumped, a FinOps or cost review of a subscription or resource group, right-sizing VMs or SQL Database, finding unattached managed disks, unassociated public IPs, orphaned NICs and snapshots or idle gateways, App Service Plans running with no apps, Log Analytics ingestion spend, storage redundancy or access-tier review, Cosmos DB RU/s provisioning, reservation and savings-plan coverage, Azure Hybrid Benefit licensing, or Azure tag compliance."
---

# Auditing Azure Cost

Read the code, then check reality, then diff the two. Two Azure traps this audit always
checks: **disks bill by provisioned performance tier, not bytes used**, and **tags do not
inherit from a resource group**, so cost allocation silently under-reports.

## Applicability and Precedence

The subscription's own tagging convention outranks the standard below — reconcile to its
keys and report the difference rather than introducing a second scheme.

Verify current VM sizes, pricing tiers and regional availability with `context7` before
recommending a specific size. **This is mandatory** — Azure regional availability varies
more than the other majors, and a size unavailable in the customer's region wastes the
finding.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run read-only. `az ... list`, `show`, `graph query`, and Cost Management queries only. Produce remediation as code for the user to apply; never apply it. |
| MUST | Base right-sizing on utilization metrics or Azure Advisor output. A recommendation with no observed utilization behind it is a guess and must be labelled as one. |
| MUST | Separate measured spend from estimate. Only Cost Management gives measured cost; anything derived from SKU and runtime hours is an estimate and the report says so. |
| MUST | Check reservation and savings-plan **utilization**, not just coverage. An under-used reservation is money already spent and is a finding in its own right. |
| MUST | Warn before proposing any change to a resource tagged as production or carrying a `CanNotDelete` lock, and save the report file before presenting results. |
| NEVER | Propose deleting a resource whose purpose you have not established. An unattached disk may be the only copy of something. |
| NEVER | Present a code-only audit as though it reflected the live subscription. If access does not resolve, say so in the executive summary. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Service inventory](./references/service-inventory.md) | Always — this is the checklist the audit walks | Every service family, what to check in each, blob tiering and redundancy, Azure-specific waste patterns |
| [Report format](./references/report-format.md) | Producing the report | The exact required structure and formatting rules |

## Data sources, in order

1. **Azure Resource Graph** — `az graph query` is the primary inventory tool: one KQL
   query returns every resource with its type, location, SKU and tags, far faster and
   more completely than iterating `az` per service. Confirm the subscription first with
   `az account show`.
2. **Cost Management** — `az costmanagement query`, grouped by service, resource group
   and tag. The only source of measured spend; a cost export to storage gives longer
   history than the API's default window.
3. **Azure Advisor** — `az advisor recommendation list --category Cost`.
4. **Reservations and savings plans** — `az reservations reservation-order list` plus the
   utilization APIs, to check coverage *and* whether what is bought is being used.
5. **`context7`** — current VM sizes, pricing tiers, regional availability, and
   `azurerm` provider docs for remediation code.

## Pricing model

| Workload | Purchase option | Saving |
| :-- | :-- | :-- |
| Steady-state, known VM family | Reserved VM Instances, 1 or 3 year | up to ~72% |
| Steady-state, flexible across families | Azure Savings Plan for compute | up to ~65% |
| Variable or bursty | Pay-as-you-go with autoscaling | baseline |
| Fault-tolerant batch | Spot VMs | up to ~90% |
| Event-driven | Functions, Consumption plan | per-use |

**Azure Hybrid Benefit is the lever people miss.** Windows Server and SQL Server licences
with Software Assurance can be applied to Azure VMs and SQL, removing the licence
component from the compute rate — often a larger saving than right-sizing on a
Windows-heavy estate. Always check whether it is applied. Reserved capacity also exists
for SQL Database, Cosmos DB and storage, and is routinely left unbought.

## Mandatory tags

Every resource carries all five, keys in `PascalCase`:

| Key | Example | Purpose |
| :-- | :-- | :-- |
| `CostCenter` | `cc-102` | Chargeback |
| `Environment` | `dev`, `staging`, `prod` | Deployment stage |
| `Service` | `auth-api` | The workload |
| `Owner` | `platform-team` | Responsible team |
| `DataClass` | `public`, `confidential`, `pii` | Security classification |

**Tags do not inherit from a resource group**, so check resources individually: a tagged
group full of untagged resources passes a naive check and contributes nothing to cost
allocation. Some resource types accept no tags — list those separately rather than as
failures.

Also check `DataClass` on every storage and database resource, and `Schedule` on anything
tagged `Environment: dev` running 24/7 — the most common cheap win. Read tags
subscription-wide with one Resource Graph query.

## Procedure

```text
Audit progress:
- [ ] 1. Scope confirmed
- [ ] 2. Infrastructure code analysed
- [ ] 3. Live state inventoried via Resource Graph
- [ ] 4. Drift and shadow resources identified
- [ ] 5. Waste and right-sizing found
- [ ] 6. Tag compliance checked
- [ ] 7. Cost attributed, commitment coverage reviewed
- [ ] 8. Report saved, then presented
```

1. **Confirm scope.** Subscription, resource groups, region, service focus. Default to
   exhaustive; ask if the subscription is not identifiable.
2. **Read the infrastructure code first.** Terraform (`*.tf`, `terragrunt.hcl`) and Bicep
   or ARM (`*.bicep`, `azuredeploy.json`). Extract what drives cost: VM `size`, disk
   `storage_account_type` and tier, `sku_name`, `account_replication_type`, node counts,
   `capacity`. Note anti-patterns — hardcoded SKUs, missing lifecycle policies,
   over-provisioned defaults, GRS where LRS would serve.
3. **Inventory live state** with Resource Graph, then walk
   [service-inventory.md](./references/service-inventory.md).
4. **Diff code against reality**: in code but absent from Azure, in Azure but absent from
   code (**shadow resources**), and configuration drift.
5. **Find waste** — the inventory names the checks per service.
6. **Check tag compliance** resource by resource.
7. **Attribute cost.** Cost Management for measured spend; otherwise estimate from SKU
   and runtime hours and label it. Review reservation and savings-plan utilization, and
   whether Hybrid Benefit is applied. Give each opportunity a **Golden Path** (balanced),
   **Cost-Optimized Path** (maximum saving) and **Velocity Path** (performance).
8. **Save the report, then present it** — see
   [report-format.md](./references/report-format.md).

The audit is analysis-only. Generate remediation Terraform only after the user names
which opportunities to implement, and show a diff before writing to any existing file.

## Related

The cloud-agnostic cost framework and tagging governance live in `optimizing-cloud-cost`
in the `tsh-platform-engineering` plugin. Provisioning patterns are
[implementing Azure Terraform](../implementing-azure-terraform/SKILL.md) here.
