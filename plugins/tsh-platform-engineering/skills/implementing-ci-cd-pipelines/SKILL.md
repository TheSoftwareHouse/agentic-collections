---
name: implementing-ci-cd-pipelines
description: "Designs and implements CI/CD pipelines on GitHub Actions, GitLab CI, Bitbucket Pipelines, Azure Pipelines or Jenkins: stage structure and caching, deployment strategy (rolling, blue-green, canary), OIDC federation for cloud credentials instead of stored keys, monorepo affected-only builds, and the plan-artifact and approval gates an infrastructure-as-code pipeline requires. Use when creating or changing a pipeline, wiring deployment or cloud authentication, or reviewing pipeline changes."
when_to_use: "Trigger on: creating or modifying a workflow or pipeline file, adding a deploy stage, choosing between rolling, blue-green and canary deployment, setting up OIDC so CI can reach AWS, Azure or GCP, speeding up a slow pipeline with caching or affected-only builds in an Nx or Turborepo monorepo, adding a Terraform plan-and-apply pipeline with approval gates, GitOps promotion between environments, or reviewing a pull request that touches CI configuration."
---

# Implementing CI/CD Pipelines

Match the project's platform and existing structure before adding anything. Two
pipelines built to different conventions in one repository cost more than either
saves.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first —
section 1 detects the platform. When a `*.plan.md` exists, its Technical Context
section is the primary source; do not re-discover what it already records.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Use OIDC federation for cloud authentication on any platform that supports it. A stored long-lived cloud access key requires an explicit recorded reason. |
| MUST | Pin every action, image and tool version. `@latest` or `:latest` in a pipeline makes builds non-reproducible and turns an upstream release into an outage. |
| MUST | Gate production deployment behind environment protection with required reviewers. |
| MUST | Look up platform syntax against the version the project pins, with `context7`. Action input names change between majors and a stale snippet fails at runtime, not at review. |
| MUST | Document the rollback procedure for any deployment stage you add. A deploy with no stated rollback is not finished. |
| NEVER | Echo, print, or write a secret into pipeline output or an artifact. |
| NEVER | Skip or disable tests to make a pipeline pass. Report the failure instead. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Deployment strategies](./references/deployment-strategies.md) | Adding or changing how a release reaches an environment | Rolling, blue-green, canary, recreate — mechanics, rollback, database-migration interaction |
| [IaC pipelines](./references/iac-pipelines.md) | The pipeline runs Terraform, Terragrunt, or any other IaC tool | Plan/apply split, plan artifacts, remote state, security scanning, OIDC wiring, approval gates |

Read [iac-pipelines.md](./references/iac-pipelines.md) before writing any pipeline
that runs `terraform` — the plan-artifact rule there is the difference between
applying what was reviewed and applying something else.

## Pipeline structure

```text
Lint → Test → Build → Deploy (staging) → Deploy (production)
                ↓
        Artifacts & caching
```

Each stage independent and cacheable. A stage that cannot run on its own cannot be
retried on its own.

## Deployment strategy

| Strategy | Use when | Rollback | Risk |
| :-- | :-- | :-- | :-- |
| Rolling | Stateless, tolerates mixed versions in flight | Slow | Low |
| Blue-green | Instant rollback needed, or database migrations involved | Instant | Low |
| Canary | High traffic, gradual validation wanted | Instant | Very low |
| Recreate | Dev and test only, or a genuinely breaking change | Slow | High |

Mechanics in [deployment-strategies.md](./references/deployment-strategies.md).

## Credentials

| Scenario | Approach |
| :-- | :-- |
| AWS, Azure or GCP from GitHub Actions or GitLab CI | OIDC federation |
| AWS from Bitbucket Pipelines | Repository variables plus assume-role |
| Multi-cloud | Vault with CI/CD auth |
| Small team, single platform | Platform-native secret store |

Implementation detail lives in
[managing secrets](../managing-secrets/SKILL.md).

## Monorepo builds

| Tool | Detected by | Approach |
| :-- | :-- | :-- |
| Nx | `nx.json` | `nx affected --target=build` |
| Turborepo | `turbo.json` | `turbo run build --filter=...[origin/main]` |
| Neither | — | Path filtering in the CI config |

## Procedure

1. **Discover** — read the shared context file and the plan's Technical Context.
   Identify the platform, branching strategy, and deployment targets.
2. **Look up syntax** for the pinned platform version with `context7`.
3. **Choose the deployment strategy** from the table above.
4. **Configure credentials** — OIDC first.
5. **Implement** the stages, with caching and pinned versions.
6. **Validate** before delivering: lint the config, and run the pipeline in dry-run or
   plan mode. For IaC pipelines, walk the checklist in
   [iac-pipelines.md](./references/iac-pipelines.md) — this is not optional.

## Checklist

- [ ] Secrets in the platform secret store, never in the config
- [ ] Dependency caching configured
- [ ] Branch protection on the default branch
- [ ] Required reviewers on the production environment
- [ ] Rollback procedure documented
- [ ] All versions pinned
- [ ] Artifact verified before deploy
- [ ] Pipeline validated in dry-run

## Output

Report the change as:

```markdown
## CI/CD Pipeline Summary

### Current state
### Proposed pipeline
- Platform, stages, deployment strategy

### Required setup
| Secret / Variable | Purpose | Where to configure |

### How to validate
### Files changed
```

Anything the user must configure outside the repository — a secret, an environment,
a cloud trust policy — belongs in **Required setup**. A pipeline that cannot run
until someone sets an unnamed variable is a broken delivery.

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| Secrets in config or logs | Platform secret store, referenced |
| `latest` tags and unpinned actions | Pinned versions everywhere |
| Skip tests for a quick fix | Fix the test or report the failure |
| Deploy without verifying the artifact | Verify, then deploy |
| Direct pushes to the default branch | Branch protection |
| One monolithic job | Independent, cacheable, retryable stages |

## Related skills in this plugin

- [Managing secrets](../managing-secrets/SKILL.md) — OIDC and secret store wiring
- [Implementing Terraform modules](../implementing-terraform-modules/SKILL.md) — what
  an IaC pipeline runs
- [Deploying to Kubernetes](../deploying-to-kubernetes/SKILL.md) — the deploy target
