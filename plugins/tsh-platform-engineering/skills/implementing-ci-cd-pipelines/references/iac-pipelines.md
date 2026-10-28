# Infrastructure-as-code pipelines

An IaC pipeline has one property an application pipeline does not: the thing it
applies must be exactly the thing that was reviewed. Everything below serves that.

## Structure

```text
Lint (fmt) → Validate → Security scan → Plan → [Manual approval] → Apply
                                          ↓
                                   Save plan artifact
                                          ↓
                                   PR comment with diff
```

**Never use local state in CI.** Configure a remote backend before the pipeline runs
at all. A pipeline that initializes local state produces a plan against an empty
world and will happily propose recreating your entire infrastructure.

## Required elements

| Element | Implementation | Why |
| :-- | :-- | :-- |
| Cloud credentials | OIDC — e.g. `aws-actions/configure-aws-credentials@v4` | No long-lived secrets |
| State backend | S3, GCS, or Azure Blob | Persistent state, concurrency protection |
| State locking | The backend's native locking — S3 via `use_lockfile = true` (Terraform ≥ 1.10), GCS and Azure Blob lock natively; DynamoDB locking is deprecated since Terraform 1.11 | Two concurrent applies corrupt state |
| Plan artifact | `terraform plan -out=tfplan`, uploaded | Apply matches the reviewed plan |
| PR comment | `actions/github-script` or a plan commenter | Reviewers see the diff before merge |
| Security scan | `tfsec`, `checkov`, or `trivy config` | Misconfiguration caught before apply |
| Production guard | Protected environment with required reviewers | Human approval before infrastructure changes |
| Cache | `.terraform` directory cached between runs | Faster init, fewer provider API calls |

## The plan artifact pattern

This is the load-bearing part. Apply must consume the reviewed plan, not regenerate
it — state can change between plan and apply, and a regenerated plan can differ from
what a human approved.

```yaml
plan:
  steps:
    - run: terraform plan -out=tfplan
    - uses: actions/upload-artifact@v4
      with:
        name: tfplan
        path: tfplan

apply:
  needs: plan
  steps:
    - uses: actions/download-artifact@v4
      with:
        name: tfplan
    - run: terraform apply tfplan
```

## OIDC to AWS from GitHub Actions

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
      aws-region: ${{ vars.AWS_REGION }}
```

The `id-token: write` permission is what makes OIDC work; without it the step fails
with an unhelpful credentials error. Verify the current input names for the action
major the project pins — they have changed between versions.

For Azure use `azure/login` with a federated credential, and for GCP
`google-github-actions/auth` with Workload Identity Federation. Both need the same
`id-token: write` permission.

## Environment protection

```yaml
apply:
  runs-on: ubuntu-latest
  needs: plan
  environment: production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

The `environment:` key is only a gate if the environment has required reviewers
configured in repository settings — Settings → Environments → production → Required
reviewers. The workflow file alone does not create the gate, so say so when handing
over: this is a **Required setup** item.

## Anti-patterns

| Don't | Do |
| :-- | :-- |
| `apply -auto-approve` with no protected environment | Approval gate on the apply job |
| `terraform init` in every job with no cache | Cache `.terraform` |
| No remote backend | Remote state with locking, configured first |
| Regenerate the plan in the apply job | Consume the uploaded plan artifact |
| Skip security scanning | `tfsec` or `checkov` before plan |
| Unpinned provider versions | Constraints in `versions.tf`, lock file committed |
| Plan output only in job logs | Posted as a PR comment |
| Apply on any branch | Apply only from the default branch, on push |

## Checklist

Walk this before delivering any IaC pipeline:

- [ ] Remote state backend configured (S3 / GCS / Azure Blob)
- [ ] State locking enabled
- [ ] OIDC federation for cloud credentials
- [ ] Security scanning in the pipeline
- [ ] Plan artifact saved and reused by apply
- [ ] Plan diff posted as a PR comment
- [ ] Protected environment with required reviewers on apply
- [ ] Provider versions pinned in `versions.tf`, lock file committed
- [ ] `.terraform` cached between runs
- [ ] Apply restricted to the default branch
