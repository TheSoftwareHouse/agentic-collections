# Changelog

All notable changes to `tsh-stack-azure` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-10-02

### Fixed

- `implementing-azure-terraform` mandated `azurerm_policy_assignment`, a resource
  the pinned azurerm 4.x does not have — it was split into scope-specific
  `azurerm_<scope>_policy_assignment` resources in 3.0, so a plan failed on that
  line. The skill now names the three current resources.

## [0.1.0] - 2026-08-22

Initial release, completing the cloud family alongside `tsh-stack-aws` and
`tsh-stack-gcp`.

### Added

- **`implementing-azure-terraform`** — VNet with per-subnet NSGs and delegated subnets,
  AKS with Workload Identity and Entra ID RBAC, PostgreSQL and MySQL Flexible Server on
  private DNS, Blob Storage with deliberate redundancy, Application Gateway with a WAF
  policy in detection mode first, Key Vault with soft delete and purge protection, ACR
  and Service Bus. Carries the `features {}` requirement, the 3.x-to-4.x argument
  renames, and the tags-do-not-inherit rule that shapes every module's interface.
- **`auditing-azure-cost`** — the complete audit: scope, infrastructure code (Terraform
  and Bicep), live inventory via Azure Resource Graph, drift and shadow-resource
  detection, per-service waste checks, tag compliance against Azure's non-inheriting
  model, Cost Management attribution, reservation and savings-plan **utilization**, and
  a saved presentation-ready report.
- **`.mcp.json`** with `context7`.

### Provenance

`implementing-azure-terraform` is ported from the `azure-modules.md` reference that
previously sat in `tsh-platform-engineering`, expanded with the service defaults,
anti-patterns and traps that reference only implied.

**`auditing-azure-cost` is new.** `copilot-collections` shipped cost-analysis prompts
for AWS and GCP only, so there was no Azure counterpart to port — this was written to
match theirs, from Azure's own cost model rather than by transposing AWS's. The
substantive Azure-specific content is the provisioned-tier disk billing model, storage
redundancy as a cost multiplier, App Service Plans billing without apps, Cosmos DB
provisioned RU/s, Log Analytics commitment tiers, Azure Hybrid Benefit licensing, and
reservation utilization as distinct from coverage.

Because it is documentation-derived rather than validated against a live estate, the
skill makes verification against current Azure documentation a **MUST** before any
specific size or tier is recommended — the same gate its AWS and GCP siblings carry, and
the reason a stale or region-unavailable recommendation cannot reach a report unchecked.

### Notes on the split

- **Each skill here stands alone.** A path into another plugin is not stable across
  install modes, so nothing file-links `tsh-platform-engineering`; the audit skill
  carries its own procedure and report format. It reads similarly to its AWS and GCP
  counterparts by design — the divergence is in data sources (Resource Graph and Cost
  Management), service families, the tag-inheritance model, and report identifiers.
- **Descriptions carry the routing.** No delegation instruction connects this plugin to
  the discipline plugin, matching how `implementing-nestjs-api` and `reviewing-code`
  already coexist.
