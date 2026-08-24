# TSH Stack: AWS

AWS-specific infrastructure guidance: Terraform module patterns with Well-Architected
defaults, and a full evidence-based cost and tagging audit of a live account.

Install this alongside [`tsh-platform-engineering`](../tsh-platform-engineering), which
carries the cloud-agnostic half — module structure, state, pipelines, Kubernetes,
observability, secrets, and the cost framework.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-aws@tsh-agentic-collections
```

Install at **project scope** — this belongs to an AWS repository, not to a person.
A repository has one cloud; an engineer works across several.

### Prerequisite

The `aws-documentation` MCP server is a Python package launched with `uvx`. Without
`uv` that one server fails to start and everything else works:

```shell
brew install uv          # or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

## What's in it

| Skill | Use for |
| :-- | :-- |
| `implementing-aws-terraform` | VPC, EKS, RDS, S3, ALB, Lambda and security-group patterns; encryption, IAM and tagging defaults; provider pinning |
| `auditing-aws-cost` | Full cost and tag audit — IaC then live API, drift and shadow resources, per-service waste checks, Cost Explorer attribution, saved report |

Invoked as `/tsh-stack-aws:<skill>`.

### Bundled MCP servers

`context7` for Terraform AWS provider documentation, and the AWS Labs
`aws-documentation` server for current instance families, pricing tiers and regional
availability. Both read-only.

**No write-capable AWS API server is bundled.** Live account state is read through the
`aws` CLI with `describe`, `list` and `get` verbs only, so your own permission rules
apply to every call.

## Where the line falls

| This plugin | `tsh-platform-engineering` |
| :-- | :-- |
| AWS resource patterns and defaults | Terraform module structure, variables, state, Terragrunt, Terratest |
| AWS service inventory and waste checks | The cost framework: pricing models, tiering, tagging governance |
| AWS cost report | Pipelines, Kubernetes, observability, secrets |
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
