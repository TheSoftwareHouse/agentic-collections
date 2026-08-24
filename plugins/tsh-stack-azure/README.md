# TSH Stack: Azure

Azure-specific infrastructure guidance: Terraform module patterns with Well-Architected
defaults, and a full evidence-based cost and tagging audit of a live subscription.

Install this alongside [`tsh-platform-engineering`](../tsh-platform-engineering), which
carries the cloud-agnostic half — module structure, state, pipelines, Kubernetes,
observability, secrets, and the cost framework.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-azure@tsh-agentic-collections
```

Install at **project scope** — this belongs to an Azure repository, not to a person.
A repository has one cloud; an engineer works across several.

## What's in it

| Skill | Use for |
| :-- | :-- |
| `implementing-azure-terraform` | VNet with per-subnet NSGs, AKS with Workload Identity and Entra RBAC, Flexible Server on private DNS, Blob Storage redundancy, Application Gateway with WAF, Key Vault with purge protection, ACR, Service Bus |
| `auditing-azure-cost` | Full cost and tag audit — IaC then Resource Graph, drift and shadow resources, per-service waste checks, Cost Management attribution, reservation utilization, saved report |

Invoked as `/tsh-stack-azure:<skill>`.

### Bundled MCP servers

`context7` only, for Terraform `azurerm` provider documentation, VM sizes and pricing
tiers. It is read-only.

**No Azure control-plane MCP server is bundled.** Microsoft's `@azure/mcp` is still
pre-release and write-capable, so live subscription state is read through the `az` CLI —
`list`, `show` and `graph query` — where your own permission rules apply to every call.
If you want the server, add it to `.mcp.json` yourself; the skills' read-only-verb
restriction applies either way.

## Two Azure traps the skills exist to catch

- **Managed disks bill by provisioned performance tier, not bytes used.** A P30 costs
  the same at 5 GB as at 1 TB, so an oversized tier on a small disk is invisible to any
  check that only looks at capacity.
- **Tags do not inherit from a resource group.** A tagged resource group full of
  untagged resources passes a naive compliance check and contributes nothing to cost
  allocation.

A third worth knowing: **an App Service Plan bills whether or not it hosts a running
app**, so stopping the app does not stop the bill.

## Where the line falls

| This plugin | `tsh-platform-engineering` |
| :-- | :-- |
| Azure resource patterns and defaults | Terraform module structure, variables, state, Terragrunt, Terratest |
| Azure service inventory and waste checks | The cost framework: pricing models, tiering, tagging governance |
| Azure cost report | Pipelines, Kubernetes, observability, secrets |
| — | Cross-cloud service comparison and multi-cloud topology |

Neither plugin file-links the other — a path across plugins is not stable across
install modes. Both stand alone, and the model routes on descriptions.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, starting from
[`templates/SKILL.md`](../../templates/SKILL.md). Read
[`CLAUDE.md`](../../CLAUDE.md) and
[`.claude/rules/stack-plugin-conventions.md`](../../.claude/rules/stack-plugin-conventions.md)
first — the second one carries the rule for what belongs here versus in the discipline
plugin.
