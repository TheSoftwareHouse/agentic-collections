---
title: Managing Secrets
sidebar_label: Managing Secrets
sidebar_position: 5
description: Chooses and implements a secrets management approach for cloud and Kubernetes workloads - secret store selection, OIDC federation for CI/CD instead of long-lived keys, rotation policy, and audit logging.
sources:
  - plugins/tsh-platform-engineering/skills/managing-secrets/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
sources_hash: "e7308bffd3d7cc5d1e9bca01e331e9f3ac94990f9397c7d39d1341bed4d4d0cb"
---

# Managing Secrets

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:managing-secrets`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer), [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor), which audits secret handling against this skill's checklist

Picks the secret store that matches the deployment shape, then federates credentials instead of copying them. The failure it exists to prevent is a long-lived cloud access key pasted into CI settings, which no rotation policy ever reaches.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file; sections 3 and 4 detect the cloud provider and any secrets tooling already in place. An existing pattern in the repository outranks the decision matrix, and is extended instead of adding a second mechanism. |
| **Solution matrix** | Single cloud with simple apps: the cloud-native store (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager). Multi-cloud or hybrid: HashiCorp Vault. GitOps with Kubernetes: Sealed Secrets, or External Secrets Operator when the source of truth is a cloud store. Local development and small teams: SOPS with age or GPG. CI/CD to cloud: OIDC federation, with no stored key at all. |
| **CI/CD federation** | GitHub Actions to AWS, Azure and GCP through OIDC (`aws-actions/configure-aws-credentials`, `azure/login`, `google-github-actions/auth`). GitLab CI to AWS or GCP through OIDC with the job JWT. Bitbucket Pipelines to AWS through OIDC (`oidc: true`) with a web-identity role. Vault with JWT or OIDC auth from any platform. Current syntax is looked up with `context7` against the pinned version. |
| **Rotation** | A rotation policy for every credential the change introduces, with an explicit interval of 30 to 90 days stated as a number, and what performs the rotation. |
| **Placement** | No secrets in ConfigMaps, plain environment blocks in IaC, pipeline logs or anything committed. A `.env.example` with placeholders is committed, never a `.env` with real values. |
| **Access and audit** | Audit logging enabled on the secret store and least-privilege access to it. Break-glass access for an incident is documented. |
| **Separation** | Separate secret values per environment. |
| **Verification** | A secret is verified by reference or by the consuming service starting, never by printing, echoing or logging its value. Secret scanning in CI with gitleaks or trufflehog. |

## How it works

1. **Discover** the cloud, the CI platform and any secrets tooling already present.
2. **Choose** by the decision matrix, or extend the existing mechanism.
3. **Look up syntax** with `context7` for the pinned provider or action version.
4. **Implement**: store the secret, grant least-privilege read access to exactly the consuming principal, and reference it from the workload.
5. **Set rotation** with an interval, and say what rotates it.
6. **Enable auditing** on the store.
7. **Document break-glass**: who can reach the secret in an incident, and how.
8. **Verify** that the consumer starts and the secret is absent from every log, manifest and state file the change touches.

The skill has no `references/` files; everything is in `SKILL.md`.

## Related skills

- [Implementing CI/CD Pipelines](/docs/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines) - where the OIDC wiring actually lands.
- [Implementing Terraform Modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules) - IaC secret resource patterns and state hygiene.
- [Deploying to Kubernetes](/docs/plugins/tsh-platform-engineering/skills/deploying-to-kubernetes) - in-cluster secret delivery.

## Source

- [`plugins/tsh-platform-engineering/skills/managing-secrets/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/managing-secrets/SKILL.md)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
