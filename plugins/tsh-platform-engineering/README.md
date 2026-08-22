# TSH Platform Engineering

Infrastructure, CI/CD and deployment: Terraform modules, pipelines with OIDC and plan
gates, production-shaped Kubernetes workloads, observability with SLOs, secrets
management, and evidence-based cloud cost audits.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-platform-engineering@tsh-agentic-collections
```

### Prerequisite for the AWS documentation server

The bundled `aws-documentation` MCP server is a Python package launched with `uvx`. If
you do not have `uv`, that one server fails to start and the rest work normally:

```shell
brew install uv          # or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

The four other servers use `npx` and need nothing extra.

## What's in it

### Skills

| Skill | Use for |
| :-- | :-- |
| `implementing-terraform-modules` | Module structure, provider pinning, remote state, Terraform vs Terragrunt, Terratest |
| `implementing-ci-cd-pipelines` | Pipeline stages, deployment strategies, OIDC federation, IaC plan-and-apply gates |
| `deploying-to-kubernetes` | Workload configuration, probes, QoS, PDBs, scaling, Helm and Kustomize, ingress |
| `implementing-observability` | Metrics, logs, traces, SLOs with error budgets, alerts that link to runbooks |
| `managing-secrets` | Secret store selection, OIDC instead of stored keys, rotation, audit logging |
| `optimizing-cloud-cost` | The cost framework — pricing models, storage tiering, tagging governance, cost-impact estimates |
| `designing-multi-cloud-architecture` | Provider service mapping, the six multi-cloud patterns, migration phasing |

Invoked as `/tsh-platform-engineering:<skill>`.

### Agents

| Agent | Use for |
| :-- | :-- |
| `devops-engineer` | Building and validating infrastructure changes — never applying them |
| `infrastructure-auditor` | Read-only security, cost and practice audit returning ranked findings |

Invoked as `@tsh-platform-engineering:<agent>`.

### Bundled MCP servers

`context7` only, for provider, Kubernetes, Helm and CI platform documentation. It is
read-only.

**Cloud documentation and live-state servers ship with the cloud's own plugin** —
`aws-documentation` in `tsh-stack-aws`, the three Google Cloud servers in
`tsh-stack-gcp`, `context7` alone in `tsh-stack-azure`. A GCP repository therefore never
starts an AWS server, and no cloud server appears in a repository with no cloud plugin
installed.

## Pairs with a cloud plugin

This plugin is the cloud-agnostic half. Install it at **user scope** — it travels with
you across clients — and install the repository's cloud at **project scope**:

```shell
/plugin install tsh-stack-aws@tsh-agentic-collections     # or
/plugin install tsh-stack-gcp@tsh-agentic-collections     # or
/plugin install tsh-stack-azure@tsh-agentic-collections
```

| Here | In the cloud plugin |
| :-- | :-- |
| Terraform module structure, variables, state, Terragrunt, Terratest | That cloud's resource patterns and service defaults |
| The cost framework: pricing models, tiering, tagging governance | That cloud's service inventory, waste checks and cost report |
| Pipelines, Kubernetes, observability, secrets | — |
| Cross-cloud comparison and multi-cloud topology | — |

All three major clouds have a plugin. Nothing cloud-specific remains here.

Neither side file-links the other — a path across plugins is not stable across install
modes. Each stands alone and the model routes on descriptions.

## Assumes tsh-core

This plugin references `/tsh-core:managing-decision-records` and
`/tsh-core:writing-technical-documents` by name. Both degrade to a missing command
rather than an error if `tsh-core` is absent, but install it — it depends on nothing:

```shell
/plugin install tsh-core@tsh-agentic-collections
```

## Conventions this plugin holds to

- **Nothing here applies infrastructure.** Every skill and both agents validate with
  `plan`, `validate`, `--dry-run=server` or `template`, and hand apply instructions to
  a human. The `devops-engineer` agent carries an explicit mutation lock.
- **Every proposal carries a cost estimate**, and flags a projected increase above 10%.
- **The project's existing conventions win** over any default here. Each skill starts
  from `shared/discovering-infrastructure-context.md`, which is also where the
  greenfield questions live.

## Shared context

`shared/discovering-infrastructure-context.md` is loaded by every skill in this plugin
via `${CLAUDE_PLUGIN_ROOT}`. It detects the CI platform, IaC dialect, cloud provider,
pinned versions, policy and secrets tooling, and GitOps controller — so that detection
logic lives in one place rather than being duplicated across seven skills.

## Contributing

Add an agent as `agents/<agent-name>.md`, a skill as `skills/<skill-name>/SKILL.md`.
Start from [`templates/agent.md`](../../templates/agent.md) or
[`templates/SKILL.md`](../../templates/SKILL.md), and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.
