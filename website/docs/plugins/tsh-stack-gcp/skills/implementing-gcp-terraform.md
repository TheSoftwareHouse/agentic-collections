---
title: implementing-gcp-terraform
sidebar_label: implementing-gcp-terraform
sidebar_position: 2
description: GCP-specific Terraform patterns and Architecture Framework defaults for VPC, GKE, Cloud SQL, Cloud Storage, Cloud Run, Pub/Sub, Secret Manager and Cloud Armor, with the Google provider version to pin.
sources:
  - plugins/tsh-stack-gcp/skills/implementing-gcp-terraform/SKILL.md
  - plugins/tsh-stack-gcp/skills/implementing-gcp-terraform/references/
sources_hash: "c561e30551286d436653a4df3b0d8bc47b116a2b88ad69cfc4f8b17dc1518824"
---

# implementing-gcp-terraform

**Plugin:** [tsh-stack-gcp](/docs/plugins/tsh-stack-gcp/)  
**Invoke:** `/tsh-stack-gcp:implementing-gcp-terraform`. Claude also loads it when the work matches
its description.  
**Used by:** the [implementing-terraform-modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules)
skill, which leaves cloud-specific resource patterns to it where the repository's cloud plugin is
installed.

GCP resource patterns and the defaults TSH provisions them with. Module structure (file layout,
variable validation, state, testing, Terragrunt) is generic and not repeated here; this skill covers
what goes inside GCP modules.

The project's existing modules outrank these patterns. The skill reads `versions.tf` and
`.terraform.lock.hcl` for the pinned provider version first, because the Google provider changes
resource arguments between majors and the `google-beta` provider is a separate pin. It also verifies
current machine types, GKE versions and regional availability with `context7` before naming a
specific size.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Run `terraform plan` and read the output before proposing any change. |
| MUST | Enable the APIs a module needs with `google_project_service`. |
| MUST | Use Workload Identity for workload authentication. Service-account keys need an explicit recorded reason. |
| MUST | Use private IP for every data service. A Cloud SQL instance on a public IP is a finding regardless of its authorized networks. |
| MUST | Apply the project's mandatory labels to every labelable resource. GCP labels are lowercase with underscores. |
| MUST | Include a cost estimate. Cloud NAT data processing, always-on Cloud Run CPU and `pd-ssd` are the usual surprises. |
| NEVER | Run `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Open a firewall rule to `0.0.0.0/0` on an administrative or database port. |
| NEVER | Use an auto-mode VPC. |

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Provider** | `hashicorp/google` with the example constraint `~> 5.0`. The current major is confirmed with `context7` for a greenfield project; otherwise the project's existing pin is matched. A beta-only resource pins `google-beta` separately. |
| **VPC** | Custom-mode VPC, subnets with secondary IP ranges for GKE pods and services sized before the cluster is created, Cloud Router and Cloud NAT, firewall rules sourced by service account or network tag where possible, Private Google Access per subnet. |
| **GKE** | Autopilot unless the workload needs node-level control, a private cluster with authorized networks, Workload Identity, Dataplane V2 (`datapath_provider = "ADVANCED_DATAPATH"`), Cilium cluster-wide network policy, in-transit encryption, Spot VM pools for fault-tolerant work, shielded nodes, a pinned cluster version. |
| **Cloud SQL** | PostgreSQL or MySQL with a pinned version, regional HA in production, automated backups and point-in-time recovery, private IP through VPC peering with `servicenetworking.googleapis.com`, SSL enforced, `deletion_protection` in production, disk autoresize with a cap. |
| **Cloud Storage** | Storage class by access pattern, uniform bucket-level access, versioning with a lifecycle rule expiring noncurrent versions, retention policy where compliance requires it, CMEK for sensitive data. |
| **Cloud Run** | Direct VPC egress rather than the legacy Serverless VPC Access connector, IAM invoker bindings, secrets from Secret Manager, deliberate CPU allocation, `min_instances` above zero only where cold start is unacceptable, traffic splitting. |
| **Pub/Sub** | A dead-letter topic on every subscription, acknowledgement deadline matched to real processing time, explicit message retention, separate publisher and subscriber IAM bindings, CMEK for sensitive payloads. |
| **Secret Manager** | Automatic or user-managed replication, previous version disabled rather than destroyed during rotation, `secretAccessor` granted to exactly the consuming service account, a rotation schedule. |
| **Cloud Armor** | A security policy matching the load balancer, allowlist and denylist rules, preconfigured OWASP CRS rules deployed in preview mode first, rate-based limiting. |
| **Architecture Framework defaults** | Workload Identity everywhere, private IP for all data services, CMEK for sensitive workloads, uniform bucket-level access, custom-mode VPC, Private Google Access, organization policies as code with `google_org_policy_policy`, VPC Service Controls for sensitive data, the five labels in lowercase, regional HA for production datastores and zonal below. |
| **Anti-patterns** | A table of what not to do and what to do instead, for example service-account keys to Workload Identity, ACLs on buckets to uniform bucket-level access, VPC Connector for Cloud Run egress to direct VPC egress. |

## How it works

1. **Establish context.** Provider pin, existing module conventions, state backend (GCS), project
   and environment layout, and the labelling convention in use.
2. **Confirm remote state with locking exists.** If not, that is the first change.
3. **Enable required APIs** with `google_project_service` in the module.
4. **Look up current syntax** with `context7` for the pinned provider version.
5. **Write the module** following the resource patterns and the defaults.
6. **Validate.** `terraform fmt -check`, `terraform validate`, `terraform plan -out=tfplan`, then
   `tflint` and `tfsec` or `checkov` where present.
7. **Estimate cost**, calling out Cloud NAT data processing, always-on Cloud Run CPU, `pd-ssd` versus
   `pd-balanced`, and inter-zone transfer.
8. **Deliver apply instructions.** The skill does not apply.

## Related skills

- [auditing-gcp-cost](/docs/plugins/tsh-stack-gcp/skills/auditing-gcp-cost), which audits an
  existing project for cost and label compliance.
- [implementing-terraform-modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules)
  in tsh-platform-engineering: module file layout, variable validation, state backends, Terragrunt
  and Terratest.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform/SKILL.md)
- [`references/module-patterns.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform/references/module-patterns.md)
