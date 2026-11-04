---
title: implementing-azure-terraform
sidebar_label: implementing-azure-terraform
sidebar_position: 2
description: Azure-specific Terraform patterns and Well-Architected defaults for VNet, AKS, Flexible Server, Blob Storage, Application Gateway, Key Vault, ACR and Service Bus, with the azurerm provider version to pin.
sources:
  - plugins/tsh-stack-azure/skills/implementing-azure-terraform/SKILL.md
  - plugins/tsh-stack-azure/skills/implementing-azure-terraform/references/
sources_hash: "29cdda86926fbaeea2fa003e30c67391607db790fdcc1df44eb5ff23031e604c"
---

# implementing-azure-terraform

**Plugin:** [tsh-stack-azure](/docs/plugins/tsh-stack-azure/)  
**Invoke:** `/tsh-stack-azure:implementing-azure-terraform`. Claude also loads it when the work
matches its description.  
**Used by:** the [implementing-terraform-modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules)
skill, which leaves cloud-specific resource patterns to it where the repository's cloud plugin is
installed.

Azure resource patterns and the defaults TSH provisions them with. Module structure (file layout,
variable validation, state, testing, Terragrunt) is generic and not repeated here; this skill covers
what goes inside Azure modules.

The project's existing modules outrank these patterns. The skill reads `versions.tf` and
`.terraform.lock.hcl` for the pinned provider version first, because `azurerm` 4.x renamed and
restructured a large number of resource arguments, so a 3.x snippet frequently fails to plan. It also
verifies current VM sizes, AKS versions and regional availability with `context7` before naming a
specific size.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Run `terraform plan` and read the output before proposing any change. |
| MUST | Use Managed Identity for service-to-service authentication. A service principal with a password needs an explicit recorded reason. |
| MUST | Enable diagnostic settings on every resource that emits logs, routed to Log Analytics, and set retention. |
| MUST | Enable soft delete and purge protection on Key Vault. |
| MUST | Prefer private endpoints over public access for PaaS data services. |
| MUST | Apply the project's mandatory tags to every taggable resource, because Azure does not inherit tags from a resource group. |
| MUST | Include a cost estimate. Fixed hourly costs (Application Gateway, NAT Gateway, VPN Gateway, Bastion) and premium disk tiers are the usual surprises. |
| NEVER | Run `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Open an NSG rule to `Internet` or `*` on an administrative or database port. |

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Provider** | `hashicorp/azurerm` with the example constraint `~> 4.0` and the mandatory `features {}` block, which fails at initialization with an unclear error when omitted. The current major is confirmed with `context7` for a greenfield project; otherwise the project's existing pin is matched. |
| **Tags are not inherited** | Modules take a `tags` map as a variable and apply it to every taggable resource, merged with module-specific tags. The resource group is never relied on for cost allocation, and Azure Policy is proposed to enforce or inherit tags at scale. |
| **VNet** | A planned address space, an NSG per subnet rather than one shared NSG, delegated subnets for PaaS services that require them, private DNS zones with VNet links for every private endpoint. |
| **AKS** | A tainted system node pool plus user node pools, Workload Identity (`workload_identity_enabled = true`, which requires `oidc_issuer_enabled = true`), Azure CNI or kubenet (with Azure CNI the subnet is sized for maximum pod count, or CNI Overlay is used where address space is tight), Entra ID integration with Kubernetes RBAC, an explicit choice of SKU tier. |
| **PostgreSQL and MySQL** | Flexible Server (Single Server is retired), zone-redundant HA in production, a private DNS zone with VNet integration on a delegated subnet, networking mode fixed at creation, no administrator password in a variable default. |
| **Blob Storage** | Redundancy tier chosen deliberately (LRS, ZRS, GRS or GZRS), access tier by pattern, lifecycle policies, soft delete and versioning with an expiry policy, a private endpoint with public network access disabled. |
| **Application Gateway and WAF** | Application Gateway v2 with autoscaling bounds, a WAF policy with the OWASP ruleset deployed in detection mode first, TLS certificates from Key Vault, health probes that prove the app works. |
| **Key Vault** | The RBAC authorization model, soft delete and purge protection both enabled, a private endpoint with network ACLs defaulting to deny, diagnostic logging to Log Analytics, one vault per environment boundary. |
| **Azure Container Registry** | SKU by need (Basic, Standard or Premium), geo-replication only on Premium, a retention policy for untagged manifests. |
| **Service Bus** | Namespace SKU by need, dead-letter settings on queues, explicit topic and subscription filters, message TTL and lock duration matched to real processing time. |
| **Well-Architected defaults** | Managed Identity everywhere, private endpoints with the matching private DNS zone, diagnostic settings to Log Analytics, `CanNotDelete` locks on production data resources, Azure Policy as code through the scope-specific assignment resources, customer-managed keys in a purge-protected Key Vault, one resource group per environment or module boundary, zone-redundant HA for production datastores, Entra ID RBAC on Key Vault and data services. |
| **Anti-patterns** | A table of what not to do and what to do instead, for example a service principal with a password to Managed Identity, AAD pod identity (deprecated) to Workload Identity, and GRS by default to LRS or ZRS unless cross-region durability is required. |

## How it works

1. **Establish context.** Provider pin, resource group layout, existing module conventions, state
   backend (Azure Blob) and the tagging convention in use.
2. **Confirm remote state with locking exists.** If not, that is the first change.
3. **Look up current syntax** with `context7` for the pinned `azurerm` version, paying attention to
   3.x-to-4.x argument renames.
4. **Write the module** following the resource patterns and the defaults.
5. **Validate.** `terraform fmt -check`, `terraform validate`, `terraform plan -out=tfplan`, then
   `tflint` and `tfsec` or `checkov` where present.
6. **Estimate cost**, calling out fixed hourly gateway costs, disk performance tiers, storage
   redundancy and Log Analytics ingestion.
7. **Deliver apply instructions.** The skill does not apply.

## Related skills

- [auditing-azure-cost](/docs/plugins/tsh-stack-azure/skills/auditing-azure-cost), which audits an
  existing subscription for cost and tag compliance.
- [implementing-terraform-modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules)
  in tsh-platform-engineering: module file layout, variable validation, state backends, Terragrunt
  and Terratest.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-azure/skills/implementing-azure-terraform/SKILL.md)
- [`references/module-patterns.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-azure/skills/implementing-azure-terraform/references/module-patterns.md)
