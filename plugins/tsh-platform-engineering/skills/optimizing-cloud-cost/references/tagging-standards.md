# Cloud resource tagging standards

Tags are how cost becomes attributable. An untagged resource cannot be charged back,
cannot be found by its owner, and cannot be safely deleted — which is why untagged
resources accumulate rather than get cleaned up.

## Governance

- **Enforcement** — tag policies at the organization level (AWS Organizations Tag
  Policies, Azure Policy, GCP organization policy constraints).
- **Case** — keys in `PascalCase`, values in `lowercase-with-hyphens`, on AWS and
  Azure. GCP labels are lowercase-only: see the dialect table below.
- **IaC requirement** — every module injects the mandatory tags automatically. A tag
  applied by hand is a tag that will be missing on the next resource.

## Mandatory tags — the Core 5

Every resource carries all five. These are the canonical keys; where a project
already uses different ones, follow the project and report the difference.

| Key | Example | Purpose | FOCUS mapping |
| :-- | :-- | :-- | :-- |
| `CostCenter` | `cc-102` | Billing code for chargeback | Cost Center |
| `Environment` | `dev`, `staging`, `prod` | Deployment stage | Environment |
| `Service` | `auth-api`, `data-lake` | The specific workload | Service Name |
| `Owner` | `platform-team` | Team responsible | Resource Owner |
| `DataClass` | `public`, `confidential`, `pii` | Security classification | — |

`DataClass` is mandatory on all storage and database resources without exception —
it is what makes a data-handling audit possible at all.

## GCP label dialect

GCP labels permit only lowercase letters, numbers, dashes and underscores. The Core 5
map as:

| Tag key | GCP label |
| :-- | :-- |
| `CostCenter` | `cost_center` |
| `Environment` | `environment` |
| `Service` | `service` |
| `Owner` | `owner` |
| `DataClass` | `data_class` |

The same transformation applies to every workload tag below.

## Workload-specific tags

### AI and ML

| Key | Example | Purpose |
| :-- | :-- | :-- |
| `ModelID` | `llama-3-70b` | Spend per model |
| `TrainingJobId` | `job-2026-02-18-a` | Cost of a specific training run |
| `InferenceType` | `realtime`, `batch` | Separates latency-driven from throughput-driven spend |

Required on GPU instances and managed inference endpoints — SageMaker endpoints on
AWS, Vertex AI endpoints on GCP.

### Lifecycle and automation

| Key | Example | Purpose |
| :-- | :-- | :-- |
| `Schedule` | `business-hours-only` | Consumed by an instance scheduler to stop resources overnight |
| `Temporary` | `true` | Marks a resource that is not permanent; requires `TTL` |
| `TTL` | `2026-12-31` | Date the resource must be destroyed |

## Compliance checks

Walk these in order when checking tag compliance. A cloud-specific audit skill —
`auditing-aws-cost` or `auditing-gcp-cost` — carries the provider call that reads tags
project-wide; this is the standard those checks are made against:

1. **Core 5 present** on every discovered resource. Report each missing key by name,
   not as a count.
2. **`DataClass` present** on every storage and database resource.
3. **AI/ML tags present** on GPU instances and inference endpoints.
4. **`Schedule` present** on any resource tagged `Environment: dev` that is running
   24/7 — a development resource with no schedule is the most common cheap win.
5. **`TTL` present** wherever `Temporary: true`, and flag any `TTL` already past.

Report compliance as a percentage plus the resource-by-resource table, so the number
is auditable rather than asserted.

## Enforcement patterns

- **Preventive** — deny resource creation without mandatory tags via policy. The only
  approach that actually holds.
- **Detective** — scheduled job listing non-compliant resources, reported to the
  owning team.
- **Corrective** — quarantine or scheduled stop for persistently untagged resources.

Prefer preventive. A detective control with no owner produces a report nobody reads.

Automated deletion of untagged resources is a policy decision for the account owner,
not a default this plugin applies — propose it, never implement it unasked.
