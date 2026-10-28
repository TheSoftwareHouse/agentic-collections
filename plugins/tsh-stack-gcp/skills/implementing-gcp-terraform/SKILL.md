---
name: implementing-gcp-terraform
description: "GCP-specific Terraform patterns and Architecture Framework defaults: custom-mode VPC with secondary ranges for GKE, private clusters with Workload Identity and Dataplane V2, Cloud SQL on private IP, Cloud Storage with uniform bucket-level access, Cloud Run with direct VPC egress, Pub/Sub, Secret Manager and Cloud Armor, plus CMEK and the provider version to pin. Use when provisioning GCP infrastructure with Terraform or reviewing GCP infrastructure code."
when_to_use: "Trigger on: writing or reviewing Terraform for GCP resources, `provider \"google\"` in a project, designing a VPC with secondary IP ranges, standing up GKE Standard or Autopilot with Workload Identity, Cloud SQL with private IP and HA, Cloud Storage buckets with lifecycle rules and CMEK, Cloud Run services with traffic splitting, Pub/Sub topics and dead-letter subscriptions, Cloud Armor WAF policies, enabling project services, or choosing the Google provider version constraint."
---

# Implementing GCP Terraform

GCP resource patterns and the defaults TSH provisions them with. Module *structure* —
file layout, variable validation, state, testing, Terragrunt — is generic and is not
repeated here; this skill is what goes inside GCP modules.

## Applicability and Precedence

The project's existing modules outrank these patterns. Read `versions.tf` and
`.terraform.lock.hcl` for the pinned provider version first, and search with that
version — the Google provider changes resource arguments between majors, and the
`google-beta` provider is a separate pin.

Verify current machine types, GKE versions and regional availability with `context7`
before naming a specific size. Availability differs by region and is a common
late-stage surprise.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run `terraform plan` and read the output before proposing any change. |
| MUST | Enable the APIs a module needs with `google_project_service`. A module that assumes an enabled API fails on a fresh project with an error that does not name the cause. |
| MUST | Use **Workload Identity** for workload authentication. Service-account keys are long-lived credentials in a file and need an explicit recorded reason. |
| MUST | Use private IP for every data service. A Cloud SQL instance on a public IP is a finding regardless of its authorized networks. |
| MUST | Apply the project's mandatory labels to every labelable resource. GCP labels are lowercase with underscores. |
| MUST | Include a cost estimate. Cloud NAT data processing, always-on Cloud Run CPU and `pd-ssd` are the usual surprises. |
| NEVER | Run `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Open a firewall rule to `0.0.0.0/0` on an administrative port — 22, 3389, or a database port. |
| NEVER | Use auto-mode VPC. It creates a subnet in every region with overlapping ranges you cannot change. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Module patterns](./references/module-patterns.md) | Provisioning any of these resource families | VPC, GKE, Cloud SQL, Cloud Storage, Cloud Run, Pub/Sub, Secret Manager, Cloud Armor |

## Provider

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
```

Confirm the current major with `context7` for a greenfield project; match the project's
existing pin otherwise. Where a resource is beta-only, pin `google-beta` separately
rather than moving the whole project onto it.

## Architecture Framework defaults

Apply these unless the project documents a reason not to:

1. **Workload Identity everywhere**, never service-account keys.
2. **Private IP for all data services**, via VPC peering with
   `servicenetworking.googleapis.com`.
3. **CMEK with Cloud KMS** for sensitive workloads.
4. **Uniform bucket-level access** on every Cloud Storage bucket — ACLs are legacy and
   make access review impossible.
5. **Custom-mode VPC**, with subnet ranges planned before anything is written.
6. **Private Google Access** per subnet, so Google-API traffic never touches Cloud NAT.
7. **Organization policies as code** with `google_org_policy_policy`.
8. **VPC Service Controls** for projects handling sensitive data.
9. **Labels on everything** — the Core 5 in GCP's lowercase dialect: `cost_center`,
    `environment`, `service`, `owner`, `data_class`.
10. **Regional HA for production** datastores, zonal below it.

## Procedure

1. **Establish context** — provider pin, existing module conventions, state backend
   (GCS), project and environment layout, labelling convention in use.
2. **Confirm remote state with locking** exists. If not, that is the first change.
3. **Enable required APIs** with `google_project_service` in the module.
4. **Look up current syntax** with `context7` for the pinned provider version.
5. **Write the module**, following
   [module-patterns.md](./references/module-patterns.md) and the defaults above.
6. **Validate** — `terraform fmt -check`, `terraform validate`,
   `terraform plan -out=tfplan`, then `tflint` and `tfsec` or `checkov` where present.
7. **Estimate cost**, calling out Cloud NAT data processing, always-on Cloud Run CPU,
   `pd-ssd` versus `pd-balanced`, and inter-zone transfer.
8. **Deliver apply instructions.** Do not apply.

## GCP-specific anti-patterns

| Don't | Do |
| :-- | :-- |
| Auto-mode VPC | Custom-mode, with planned ranges |
| Service-account keys | Workload Identity |
| Public IP on Cloud SQL | Private IP via VPC peering |
| ACLs on buckets | Uniform bucket-level access |
| `pd-ssd` for general workloads | `pd-balanced` |
| `n1` machine types | `e2` or `n2` |
| Cloud Run with always-on CPU on low traffic | Request-based CPU allocation |
| VPC Connector for Cloud Run egress | Direct VPC egress — the connector is legacy |
| On-demand GKE nodes for batch | Spot VM node pool |
| Cloud NAT carrying Google-API traffic | Private Google Access |
| GKE Standard with hand-managed pools for a simple workload | Autopilot |
| Logging with no exclusions | Exclude high-volume low-value lines at ingestion |

## Related

Generic Terraform mechanics — module file layout, variable validation, state backends,
Terragrunt, Terratest — live in `implementing-terraform-modules` in the
`tsh-platform-engineering` plugin. Auditing an existing project for cost and label
compliance is [auditing GCP cost](../auditing-gcp-cost/SKILL.md) in this plugin.
