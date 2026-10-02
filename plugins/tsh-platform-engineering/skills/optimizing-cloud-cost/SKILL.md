---
name: optimizing-cloud-cost
description: "The cloud-agnostic cost framework TSH provisions against: matching a workload to a pricing model (reserved, committed-use, spot, serverless), storage tiering with lifecycle policies, the mandatory cost-allocation tag set and how to enforce it, right-sizing method, and the cost-impact estimate every infrastructure proposal carries. Use when sizing new infrastructure, estimating the cost of a change, or setting up tagging and budget governance — not for auditing a specific account, which is the cloud-specific skill's job."
when_to_use: "Trigger on: estimating the cost impact of an infrastructure change, choosing between on-demand, reserved or committed capacity and spot, whether a workload should be serverless on cost grounds, storage class and lifecycle policy design, defining or enforcing cost-allocation tags, budget alerts and anomaly detection, scheduling non-production workloads off, or the general question of how to make infrastructure cheaper. Auditing a live account is `auditing-aws-cost`, `auditing-gcp-cost` or `auditing-azure-cost` in the cloud's own plugin."
---

# Optimizing Cloud Cost

The framework applied when provisioning, and when estimating what a change will cost.
Decisions here are cloud-agnostic: which pricing model fits a workload shape, which
storage tier fits an access pattern, what every resource must be tagged with.

**Auditing a live account is a different job**, and a cloud-specific one — it needs that
provider's service families, CLI verbs and billing API. Where the cloud's plugin is
installed, `auditing-aws-cost`, `auditing-gcp-cost` or `auditing-azure-cost` owns that. This skill still
carries what a proposal needs without them.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first. A
project's own tagging convention outranks the standard in
[tagging standards](./references/tagging-standards.md) — reconcile to the project's keys
and report the difference rather than introducing a second scheme.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Every infrastructure proposal carries a cost impact estimate. If projected spend rises more than 10%, open the response with `⚠️ FINOPS ALERT: High Cost Impact`. |
| MUST | Base right-sizing on utilization metrics. A recommendation with no observed utilization behind it is a guess and must be labelled as one. |
| MUST | Verify current instance families, machine types and pricing tiers against provider documentation before recommending a specific size — these change every few months and a stale recommendation costs money. |
| MUST | Pair every storage tier choice with a lifecycle policy. A hand-picked tier decays the moment access patterns change. |
| MUST | Apply cost-allocation tags at provisioning time, enforced in infrastructure code rather than by hand. |
| NEVER | Report an estimated saving as if it were measured. Say which it is. |
| NEVER | Propose deleting a resource whose purpose you have not established. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Tagging standards](./references/tagging-standards.md) | Provisioning anything, or setting up cost governance | The mandatory tag set, workload-specific tags, the GCP label dialect, enforcement patterns |

## Pricing Model Decision

| Workload | AWS | Azure | GCP | Saving |
| :-- | :-- | :-- | :-- | :-- |
| Steady-state, 24/7 | Reserved Instances / Savings Plans | Reserved VMs | Committed Use | 30–72% |
| Variable or bursty | On-Demand plus auto-scaling | Pay-as-you-go | On-Demand | baseline |
| Fault-tolerant batch | Spot | Spot VMs | Spot VMs | up to 90% |
| Event-driven | Lambda | Functions | Cloud Run / Functions | per-use |

Reserved or committed capacity pays off above roughly 70% sustained utilization. Below
that, on-demand plus auto-scaling usually wins.

## Storage Tiering Decision

| Access pattern | AWS | Azure | GCP |
| :-- | :-- | :-- | :-- |
| Frequent | S3 Standard | Hot | Standard |
| Infrequent, 30+ days | S3 Standard-IA | Cool | Nearline |
| Rare, 90+ days | S3 Glacier | Cold | Coldline |
| Archive, 365+ days | S3 Deep Archive | Archive | Archive |

Check the minimum storage duration per tier before designing the transition — deleting
early from a cold tier still bills the remainder, so an aggressive lifecycle rule on
short-lived data costs more than leaving it hot.

## Right-sizing method

1. **Get utilization**, not opinion — the provider's recommender or optimizer service,
   or metrics over a period long enough to include the peak.
2. **Size to the peak the workload must serve**, not the average, then let auto-scaling
   handle the rest.
3. **Change one dimension at a time.** Family, then size. A simultaneous move to a new
   generation and a smaller size makes a regression impossible to attribute.
4. **Re-measure after the change.** A right-sizing exercise with no follow-up
   measurement is a guess that was written down.

Current-generation instance families are usually the cheapest single win: same
performance, lower price, at the cost of a rebuild where the architecture changes.

## Cost-impact estimate

Every proposal states, at minimum:

- **New monthly run-rate** for resources being added, itemized.
- **The delta** against current spend, as a percentage.
- **What is estimated versus measured**, explicitly.
- **The line items people forget**: NAT and egress data processing, cross-zone and
  cross-region transfer, load balancers billing hourly while idle, log ingestion,
  managed-service per-hour charges on non-production environments, and orphaned storage.

## Provisioning Checklist

- [ ] Cost-allocation tags on every resource, injected by the module
- [ ] Right-sized against utilization metrics
- [ ] Reserved or committed capacity for sustained workloads above ~70% utilization
- [ ] Spot or preemptible for fault-tolerant batch
- [ ] Storage lifecycle policies configured
- [ ] Budget alerts at 50%, 80%, 100%
- [ ] Cost anomaly detection enabled
- [ ] Auto-scaling for variable workloads
- [ ] Non-production scheduled off outside business hours

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| Over-provision "just in case" | Right-size on metrics; scale up when metrics say so |
| On-demand for steady workloads | Reserved or committed capacity |
| Everything in the hot tier | Lifecycle policies |
| Skip tagging | Tag at provisioning time, enforced in IaC |
| Review cost monthly | Review weekly, alert on anomalies |
| Non-production running 24/7 | Schedule it off |
| Quote a saving with no baseline | State current spend, then the delta |

## Related skills in this plugin

- [Implementing Terraform modules](../implementing-terraform-modules/SKILL.md) — where
  sizing decisions become code
- [Designing multi-cloud architecture](../designing-multi-cloud-architecture/SKILL.md) —
  cross-cloud service and cost comparison
