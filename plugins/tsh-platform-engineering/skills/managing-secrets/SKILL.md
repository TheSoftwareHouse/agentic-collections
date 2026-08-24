---
name: managing-secrets
description: "Chooses and implements a secrets management approach for cloud and Kubernetes workloads: cloud-native secret stores versus Vault versus Sealed Secrets or External Secrets, OIDC federation for CI/CD instead of long-lived keys, rotation policy, and audit logging. Use when storing credentials, wiring pipeline authentication to a cloud provider, or auditing how a project handles secrets."
when_to_use: "Trigger on: storing application credentials, a pipeline that needs cloud credentials, replacing long-lived access keys with OIDC, secret rotation, GitOps-compatible secrets in Kubernetes, SOPS or Sealed Secrets or External Secrets Operator questions, a secret found committed to the repository, or auditing secret handling before a release."
---

# Managing Secrets

Pick the store that matches the deployment shape, then federate rather than copy
credentials. The recurring failure this skill prevents is a long-lived cloud access
key pasted into CI settings, which no rotation policy ever reaches.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first —
sections 3 and 4 detect the cloud provider and any secrets tooling already in place.
An existing pattern in the repository outranks the decision matrix below; extend it
rather than introducing a second mechanism alongside it.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Use OIDC federation for CI/CD to cloud authentication wherever the platform supports it. Long-lived access keys require an explicit, recorded reason. |
| MUST | Define a rotation policy for every credential the change introduces — 30–90 days for credentials, and state the number rather than "regularly". |
| MUST | Keep secrets out of ConfigMaps, plain environment blocks in IaC, pipeline logs, and anything committed. Reference the secret store instead. |
| MUST | Enable audit logging on the secret store, and least-privilege access to it. A store nobody can read the access log of is not managed. |
| MUST | Use separate secret values per environment. One value shared across staging and production makes every staging incident a production incident. |
| NEVER | Print, echo, or log a secret value to verify it — verify by reference or by the consuming service starting successfully. |
| NEVER | Commit a `.env` with real values. Commit `.env.example` with placeholders. |

## Solution Decision Matrix

| Scenario | Solution |
| :-- | :-- |
| Single cloud, simple apps | Cloud-native — AWS Secrets Manager, Azure Key Vault, GCP Secret Manager |
| Multi-cloud or hybrid | HashiCorp Vault |
| GitOps with Kubernetes | Sealed Secrets, or External Secrets Operator when the source of truth is a cloud store |
| Local dev, small teams | SOPS with age or GPG |
| CI/CD to cloud | OIDC federation — no stored key at all |

Detection for each of these is in the shared context file, section 4. Match what is
already there before applying this table.

## CI/CD Federation

| CI platform | Cloud | Approach |
| :-- | :-- | :-- |
| GitHub Actions | AWS | OIDC with `aws-actions/configure-aws-credentials` |
| GitHub Actions | Azure | OIDC with `azure/login` |
| GitHub Actions | GCP | OIDC with `google-github-actions/auth` |
| GitLab CI | AWS or GCP | OIDC with the job JWT |
| Bitbucket Pipelines | AWS | Repository variables plus assume-role |
| Any | Any | Vault with JWT/OIDC auth |

Look up the current syntax with `context7` against the action or provider version the
project pins — these integrations change their input names between majors.

## Procedure

1. **Discover** — read the shared context file; identify the cloud, the CI platform,
   and any secrets tooling already present.
2. **Choose** — apply the decision matrix, or extend the existing mechanism.
3. **Look up syntax** — `context7` for the pinned provider or action version.
4. **Implement** — store the secret, grant least-privilege read access to exactly the
   principal that consumes it, and reference it from the workload.
5. **Set rotation** — configure the policy, with an interval, and say what rotates it.
6. **Enable auditing** — access logging on the store.
7. **Document break-glass** — who can reach the secret in an incident, and how.
8. **Verify** — confirm the consumer starts and the secret is not present in any log,
   manifest, or state file the change touches.

## Checklist

- [ ] No secret in code, IaC literals, pipeline logs, ConfigMaps, or Terraform state
- [ ] Rotation policy defined with an explicit interval
- [ ] Least-privilege access to the secret store
- [ ] Audit logging enabled on secret access
- [ ] OIDC used for CI/CD, or the exception recorded
- [ ] Encrypted at rest and in transit
- [ ] Separate values per environment
- [ ] Break-glass procedure documented
- [ ] Secret scanning in CI — gitleaks or trufflehog

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| Hardcode secrets | Reference the secret store |
| Commit `.env` | Commit `.env.example` with placeholders |
| Share secrets over Slack or email | Grant access in the store |
| One secret across environments | One per environment |
| Long-lived CI credentials | OIDC with short-lived tokens |
| Secrets in ConfigMaps | Kubernetes Secrets, encrypted at rest |
| Secrets in Terraform variables committed as `.tfvars` | Data sources reading the store at plan time |

## Related skills in this plugin

- [Implementing CI/CD pipelines](../implementing-ci-cd-pipelines/SKILL.md) — where the
  OIDC wiring actually lands
- [Implementing Terraform modules](../implementing-terraform-modules/SKILL.md) — IaC
  secret resource patterns and state hygiene
- [Deploying to Kubernetes](../deploying-to-kubernetes/SKILL.md) — in-cluster secret
  delivery
