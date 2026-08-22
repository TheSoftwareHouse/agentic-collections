---
name: implementing-azure-terraform
description: "Azure-specific Terraform patterns and Well-Architected defaults: VNet with per-subnet NSGs, AKS with Workload Identity and Entra ID RBAC, PostgreSQL and MySQL Flexible Server on private DNS, Blob Storage with the right redundancy tier, Application Gateway with a WAF policy, Key Vault with purge protection, ACR and Service Bus, plus Managed Identity over service principals and the azurerm provider version to pin. Use when provisioning Azure infrastructure with Terraform or reviewing Azure infrastructure code."
when_to_use: "Trigger on: writing or reviewing Terraform for Azure resources, `provider \"azurerm\"` in a project, designing a VNet and subnet layout with NSGs, standing up AKS with node pools and workload identity, Azure Database for PostgreSQL or MySQL Flexible Server, storage accounts and redundancy choice, Application Gateway or WAF policies, Key Vault with private endpoints, Azure Container Registry, Service Bus queues and topics, resource group layout, or choosing the azurerm provider version constraint."
---

# Implementing Azure Terraform

Azure resource patterns and the defaults TSH provisions them with. Module *structure* —
file layout, variable validation, state, testing, Terragrunt — is generic and is not
repeated here; this skill is what goes inside Azure modules.

## Applicability and Precedence

The project's existing modules outrank these patterns. Read `versions.tf` and
`.terraform.lock.hcl` for the pinned provider version first, and search with that
version — `azurerm` 4.x renamed and restructured a large number of resource arguments,
so a 3.x snippet frequently fails to plan.

Verify current VM sizes, AKS versions and regional availability with `context7` before
naming a specific size. Azure regional availability varies more than the other major
providers, and a size unavailable in the customer's region is a wasted recommendation.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run `terraform plan` and read the output before proposing any change. |
| MUST | Use **Managed Identity** for service-to-service authentication. A service principal with a password is a long-lived credential and needs an explicit recorded reason. |
| MUST | Enable diagnostic settings on every resource that emits logs, routed to Log Analytics — and set retention, because ingestion is the cost driver. |
| MUST | Enable soft delete **and purge protection** on Key Vault. Without purge protection a deleted vault and its keys are unrecoverable, which breaks CMEK-encrypted data permanently. |
| MUST | Prefer private endpoints over public access for PaaS data services. |
| MUST | Apply the project's mandatory tags to every taggable resource. Azure does **not** inherit tags from a resource group — see the tagging note below. |
| MUST | Include a cost estimate. Fixed hourly costs — Application Gateway, NAT Gateway, VPN Gateway, Bastion — and premium disk tiers are the usual surprises. |
| NEVER | Run `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Open an NSG rule to `Internet` or `*` on an administrative port — 22, 3389, or a database port. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Module patterns](./references/module-patterns.md) | Provisioning any of these resource families | VNet, AKS, Flexible Server, Blob Storage, Application Gateway, Key Vault, ACR, Service Bus |

## Provider

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```

The `features {}` block is mandatory and easy to forget — omitting it fails at
initialization with an error that does not say so plainly. Confirm the current major
with `context7` for a greenfield project; match the project's existing pin otherwise.

## Tags are not inherited

This is the Azure-specific trap worth knowing before you write a module: **tags applied
to a resource group do not flow to the resources inside it.** Every resource must be
tagged individually, and a handful of resource types accept no tags at all.

Consequences for module design:

- Take a `tags` map as a variable and apply it to every taggable resource, merged with
  any module-specific tags.
- Never rely on the resource group for cost allocation — an untagged VM inside a tagged
  resource group is invisible to cost reporting by tag.
- Azure Policy can enforce or inherit tags at scale; propose it rather than assuming
  discipline holds.

## Well-Architected defaults

Apply these unless the project documents a reason not to:

1. **Managed Identity everywhere**, never service principal passwords.
2. **Private endpoints** for PaaS data services, with the matching private DNS zone.
3. **Diagnostic settings to Log Analytics**, with explicit retention.
4. **Resource locks** (`CanNotDelete`) on production data resources and their vaults.
5. **Azure Policy as code** via `azurerm_policy_assignment`.
6. **Customer-managed keys** for sensitive data, held in a purge-protected Key Vault.
7. **One resource group per environment or module boundary**, so lifecycle and
   permissions align with the thing being deployed.
8. **Zone-redundant HA for production** datastores, same-zone or none below it.
9. **Entra ID RBAC** rather than access policies on Key Vault, and rather than local
   accounts on data services.

## Procedure

1. **Establish context** — provider pin, resource group layout, existing module
   conventions, state backend (Azure Blob), tagging convention in use.
2. **Confirm remote state with locking** exists. If not, that is the first change.
3. **Look up current syntax** with `context7` for the pinned `azurerm` version, paying
   attention to 3.x-to-4.x argument renames.
4. **Write the module**, following
   [module-patterns.md](./references/module-patterns.md) and the defaults above.
5. **Validate** — `terraform fmt -check`, `terraform validate`,
   `terraform plan -out=tfplan`, then `tflint` and `tfsec` or `checkov` where present.
6. **Estimate cost**, calling out fixed hourly gateway costs, disk performance tiers,
   storage redundancy, and Log Analytics ingestion explicitly.
7. **Deliver apply instructions.** Do not apply.

## Azure-specific anti-patterns

| Don't | Do |
| :-- | :-- |
| Service principal with a password | Managed Identity |
| AAD pod identity | Workload Identity — pod identity is deprecated |
| Tag the resource group and assume inheritance | Tag every resource; enforce with Policy |
| Public access on a PaaS data service | Private endpoint plus private DNS zone |
| Key Vault without purge protection | Soft delete **and** purge protection |
| GRS redundancy by default | LRS or ZRS unless cross-region durability is required |
| Premium SSD for general workloads | Standard SSD, or Premium SSD v2 where IOPS are needed |
| Oversized disk tier for a small disk | Right-size the tier — disks bill by provisioned tier, not by bytes used |
| Basic public IP | Standard — Basic is retiring |
| App Service Plan left running with no apps | Delete the plan; stopping the app does not stop the bill |
| Log Analytics with no retention or exclusions | Explicit retention, and exclusions at ingestion |
| Cosmos DB provisioned at peak RU/s | Autoscale, or serverless for spiky workloads |

## Related

Generic Terraform mechanics — module file layout, variable validation, state backends,
Terragrunt, Terratest — live in `implementing-terraform-modules` in the
`tsh-platform-engineering` plugin. Auditing an existing subscription for cost and tag
compliance is [auditing Azure cost](../auditing-azure-cost/SKILL.md) in this plugin.
