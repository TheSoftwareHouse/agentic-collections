---
title: Implementing CI/CD Pipelines
sidebar_label: Implementing CI/CD Pipelines
sidebar_position: 2
description: Designs and implements CI/CD pipelines on GitHub Actions, GitLab CI, Bitbucket Pipelines, Azure Pipelines or Jenkins - stage structure, deployment strategy, OIDC credentials, monorepo builds, and IaC plan-and-apply gates.
sources:
  - plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
sources_hash: "ece5ef65c0d6e19b759b27900f50218495e705bf5e851177db0dd3ae794d9a5b"
---

# Implementing CI/CD Pipelines

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:implementing-ci-cd-pipelines`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer), [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor)

Designs and implements pipelines on GitHub Actions, GitLab CI, Bitbucket Pipelines, Azure Pipelines or Jenkins. It matches the project's platform and existing structure before adding anything, because two pipelines built to different conventions in one repository cost more than either saves.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file; section 1 detects the platform. When a `*.plan.md` exists, its Technical Context is the primary source and is not re-discovered. |
| **Pipeline structure** | Lint, Test, Build, Deploy (staging), Deploy (production), with artifacts and caching. Each stage is independent and cacheable, because a stage that cannot run on its own cannot be retried on its own. |
| **Deployment strategy** | Rolling for stateless services that tolerate mixed versions. Blue-green when instant rollback is needed or database migrations are involved. Canary for high traffic with gradual validation. Recreate for dev and test only, or a genuinely breaking change. |
| **Credentials** | OIDC federation for AWS, Azure or GCP from GitHub Actions or GitLab CI, and OIDC (`oidc: true` on the step, with a web-identity role) for AWS from Bitbucket Pipelines. Vault with CI/CD auth for multi-cloud, and the platform-native secret store for a small team on one platform. |
| **Monorepo builds** | Nx (detected by `nx.json`): `nx affected --target=build`. Turborepo (detected by `turbo.json`): `turbo run build --filter=...[origin/main]`. Otherwise, path filtering in the CI config. |
| **IaC pipelines** | Lint (fmt), Validate, Security scan, Plan, manual approval, Apply, with the plan saved as an artifact and posted as a PR comment. Apply consumes the reviewed plan artifact and does not regenerate it. Remote state with locking is configured before the pipeline runs, and apply runs only from the default branch on push. |
| **Rules** | OIDC wherever supported, with any stored long-lived cloud key needing a recorded reason. Every action, image and tool version pinned. Production deployment behind environment protection with required reviewers. Platform syntax checked with `context7` against the pinned version. A documented rollback for every deployment stage. Never echo a secret into output or an artifact, and never skip tests to make a pipeline pass. |

## How it works

1. **Discover** the platform, branching strategy and deployment targets from the shared context file and the plan's Technical Context.
2. **Look up syntax** for the pinned platform version with `context7`.
3. **Choose the deployment strategy.**
4. **Configure credentials**, OIDC first.
5. **Implement** the stages with caching and pinned versions.
6. **Validate** before delivering: lint the config and run the pipeline in dry-run or plan mode. For IaC pipelines the checklist in the IaC reference must be walked.

The output is a CI/CD Pipeline Summary: current state, proposed pipeline (platform, stages, deployment strategy), a **Required setup** table of secrets and variables with where to configure them, how to validate, and files changed. Anything the user must configure outside the repository, such as a secret, an environment or a cloud trust policy, belongs in Required setup.

## References

| Reference | Load when |
| :-- | :-- |
| `deployment-strategies.md` | Adding or changing how a release reaches an environment. Covers rolling, blue-green, canary and recreate: mechanics, rollback, and how each interacts with database migrations (expand, migrate, contract). |
| `iac-pipelines.md` | The pipeline runs Terraform, Terragrunt or any other IaC tool. Covers the plan/apply split, plan artifacts, remote state and locking, security scanning, OIDC wiring and approval gates. It must be read before writing any pipeline that runs `terraform`. |

State locking details in the IaC reference: S3 uses `use_lockfile = true` (Terraform 1.10 or later), GCS and Azure Blob lock natively, and DynamoDB locking is deprecated since Terraform 1.11. The `environment:` key is only a gate if required reviewers are configured in the repository settings, so that setup is reported as a Required setup item.

## Related skills

- [Managing Secrets](/docs/plugins/tsh-platform-engineering/skills/managing-secrets) - OIDC and secret store wiring.
- [Implementing Terraform Modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules) - what an IaC pipeline runs.
- [Deploying to Kubernetes](/docs/plugins/tsh-platform-engineering/skills/deploying-to-kubernetes) - the deploy target.

## Source

- [`plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines/SKILL.md)
- [`plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines/references)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
