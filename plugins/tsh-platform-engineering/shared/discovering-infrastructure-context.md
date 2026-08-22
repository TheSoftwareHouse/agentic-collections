# Discovering infrastructure context

Establish what the project already does before changing any infrastructure. Every
skill in this plugin loads this file first; an implementation that ignores the
project's existing dialect is a finding, not a delivery.

Read it with `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md`.

## Precedence

Project conventions outrank this plugin's defaults. Where the two disagree, follow
the project and say so. Where the project is silent, apply the plugin default. Never
mix two conventions inside one file.

Order of authority:

1. **Project instructions** — `CLAUDE.md`, `.claude/rules/`, decision records under
   `docs/decisions/`, `infrastructure/README.md`, `.devops/instructions.md`. A recorded
   decision with status `Accepted` settles the question it covers; do not re-open one
   as a side effect of an unrelated change.
2. **Existing infrastructure code** — the dialect actually in the repository wins
   over any external best practice.
3. **Provider documentation** — for current API versions and syntax, resolved
   against the versions the project pins.

## 1. CI/CD platform

| Found | Platform |
| :-- | :-- |
| `.github/workflows/*.yml` | GitHub Actions |
| `bitbucket-pipelines.yml` | Bitbucket Pipelines |
| `.gitlab-ci.yml` | GitLab CI |
| `azure-pipelines.yml` | Azure Pipelines |
| `Jenkinsfile` | Jenkins |

## 2. IaC dialect

| Found | Dialect |
| :-- | :-- |
| `*.tf` | Terraform |
| `terragrunt.hcl` | Terragrunt |
| `k8s/*.yaml`, `kubernetes/` | Raw Kubernetes manifests |
| `Chart.yaml`, `helm/` | Helm |
| `kustomization.yaml` | Kustomize |
| `template.yaml` with `AWSTemplateFormatVersion` | CloudFormation |
| `cdk.json` | AWS CDK |
| `main.bicep` | Azure Bicep |
| `Pulumi.yaml` | Pulumi |

## 3. Cloud provider and pinned versions

Read the pins before consulting any documentation, and search with the version
number so the answer matches what the project runs:

- `versions.tf` or `required_providers` → Terraform and provider constraints
- `Chart.yaml` → chart and `apiVersion`, `kubeVersion` if present
- `provider "aws" | "azurerm" | "google"` → target cloud
- `.terraform.lock.hcl` → the versions actually resolved

## 4. Policy, secrets and state

- `*.rego`, `.checkov.yaml`, `.tflint.hcl` → policy-as-code and linting already in play
- `.sops.yaml`, `*.enc.yaml` → SOPS
- `sealed-secrets/`, `SealedSecret` resources → Bitnami Sealed Secrets
- `ExternalSecret` resources → External Secrets Operator
- `vault-config/`, `vault-agent` sidecars → HashiCorp Vault
- `backend "s3" | "gcs" | "azurerm"` blocks → remote state location and locking

## 5. Existing observability and GitOps

- `prometheus.yml`, `ServiceMonitor` → Prometheus
- `otel-collector-config.yaml` → OpenTelemetry
- `fluent-bit.conf`, `fluentd.conf` → log shipping
- `argocd/`, `Application` resources → ArgoCD
- `flux-system/`, `Kustomization` CRD → Flux

## 6. Greenfield — nothing found

When no infrastructure exists, gather three answers before proposing anything, using
`AskUserQuestion`:

- **Target cloud?** AWS / Azure / GCP / multi-cloud
- **Primary workload?** serverless / containers / Kubernetes / VMs
- **Expected scale?** small / medium / large

Do not select a stack silently. If the user declines to answer, default to
**managed containers** — the lowest-complexity production-ready option — and state
that this was a default, not a decision.

## Report what you found

Before implementing, state the platform, dialect, cloud, pinned versions, and any
project convention that overrides a plugin default. If discovery turned up nothing
for a category, say so rather than assuming the plugin default silently applies.
