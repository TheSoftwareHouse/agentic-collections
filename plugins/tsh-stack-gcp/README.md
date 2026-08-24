# TSH Stack: GCP

GCP-specific infrastructure guidance: Terraform module patterns with Architecture
Framework defaults, and a full evidence-based cost and labelling audit of a live
project.

Install this alongside [`tsh-platform-engineering`](../tsh-platform-engineering), which
carries the cloud-agnostic half — module structure, state, pipelines, Kubernetes,
observability, secrets, and the cost framework.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-gcp@tsh-agentic-collections
```

Install at **project scope** — this belongs to a GCP repository, not to a person.
A repository has one cloud; an engineer works across several.

## What's in it

| Skill | Use for |
| :-- | :-- |
| `implementing-gcp-terraform` | VPC with secondary ranges, GKE with Workload Identity and Dataplane V2, Cloud SQL on private IP, Cloud Storage, Cloud Run, Pub/Sub, Secret Manager, Cloud Armor |
| `auditing-gcp-cost` | Full cost and label audit — IaC then live API, drift and shadow resources, per-service waste checks, billing-export attribution, saved report |

Invoked as `/tsh-stack-gcp:<skill>`.

### Bundled MCP servers

| Server | Purpose | Can mutate |
| :-- | :-- | :-- |
| `context7` | Terraform Google provider docs, machine types, pricing tiers | No |
| `gcp-gcloud` | Live project state through `gcloud` | **Yes** |
| `gcp-observability` | Monitoring and logging configuration | Read-oriented |
| `gcp-storage` | Cloud Storage bucket inspection | Read-oriented |

**`gcp-gcloud` can run mutating `gcloud` commands.** Nothing in this plugin does — both
skills are restricted to `list`, `describe` and `get`. That restriction is an
instruction, not a technical guarantee; if you need a hard boundary, drop the server
from `.mcp.json` and let the skills fall back to the `gcloud` CLI through Bash, where
your own permission rules apply.

## Where the line falls

| This plugin | `tsh-platform-engineering` |
| :-- | :-- |
| GCP resource patterns and defaults | Terraform module structure, variables, state, Terragrunt, Terratest |
| GCP service inventory and waste checks | The cost framework: pricing models, tiering, labelling governance |
| GCP cost report | Pipelines, Kubernetes, observability, secrets |
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
