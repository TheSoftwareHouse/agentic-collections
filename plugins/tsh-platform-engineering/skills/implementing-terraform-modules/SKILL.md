---
name: implementing-terraform-modules
description: "Writes and reviews reusable Terraform modules for AWS, Azure and GCP: the standard file layout and module interface, variable validation, provider pinning, remote state with locking, the Terraform-versus-Terragrunt decision, and Terratest coverage. Use when creating or changing infrastructure code, standardizing provisioning across environments, or reviewing a Terraform pull request."
when_to_use: "Trigger on: writing or modifying a Terraform module or root configuration, `*.tf` or `terragrunt.hcl` changes, structuring an infrastructure repository, choosing between Terraform workspaces and Terragrunt, configuring a remote state backend and locking, pinning provider versions, adding variable validation, testing infrastructure code with Terratest, or reviewing infrastructure-as-code for structure and safety."
---

# Implementing Terraform Modules

A module is an interface before it is a set of resources. Get the variables, outputs
and version constraints right and the resources follow; get them wrong and every
consumer inherits the mistake.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first —
sections 2 and 3 identify the dialect and the pinned versions. When a `*.plan.md`
exists, its Technical Context is the primary source. **The project's existing module
conventions outrank everything in this skill**; a second convention introduced
alongside the first is a finding, not a delivery.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run `terraform plan` and read the output before proposing any change. A change proposed without a plan is a guess. |
| MUST | Configure remote state with locking before anything is applied. Local state in a shared project loses work and cannot be recovered. |
| MUST | Pin provider versions in `versions.tf` and commit the lock file. |
| MUST | Give every variable a `description` and a `type`, and a `validation` block wherever a wrong value fails late or expensively. |
| MUST | Include a cost estimate for new resources. If projected spend rises more than 10%, open with `⚠️ FINOPS ALERT: High Cost Impact`. |
| MUST | Apply the project's mandatory tags to every taggable resource, merged so consumers can add their own. |
| NEVER | Run `apply`, `destroy`, or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Put a secret in a variable default, a committed `.tfvars`, or anything that reaches state as plaintext where it can be avoided. |
| NEVER | Make manual console changes or ad-hoc CLI mutations that the code does not capture. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Module structure](./references/module-structure.md) | Creating a module, or reviewing one's shape | Standard file layout, a complete worked VPC module, interface conventions |
| [Terragrunt](./references/terragrunt.md) | More than three environments, multi-region, multi-account, or `terragrunt.hcl` present | The Terraform-versus-Terragrunt decision and the Terragrunt directory pattern |
| [Testing modules](./references/testing-modules.md) | Adding or reviewing module tests | Terratest structure, required options, plan-only fast tests, cost and safety rules |

Read [module-structure.md](./references/module-structure.md) before creating a new
module — the file layout is what makes a module reviewable and reusable.

**Cloud-specific resource patterns are not here.** Each cloud has its own skill —
`implementing-aws-terraform`, `implementing-gcp-terraform`, `implementing-azure-terraform`
in `tsh-stack-aws`, `tsh-stack-gcp` and `tsh-stack-azure` — carrying that provider's
resource families, service defaults and anti-patterns. Use them where the repository's
cloud plugin is installed. What stays here is what holds whatever the provider is:
layout, interface, state, and testing.

## Module interface conventions

- **Semantic versioning** on published modules; consumers pin a constraint, not a
  branch.
- **Every variable** typed, described, and validated where a bad value is expensive.
- **Every attribute a consumer could need** exported as an output — composition is
  impossible otherwise, and adding an output later is a version bump for everyone.
- **`locals` for computed values**, not repeated expressions.
- **`count` or `for_each`** for conditional and repeated resources, not duplicated
  blocks.
- **`examples/complete/`** that actually runs, doubling as the test fixture.

Current provider constraints as a starting point, verified against the project's pins:
`aws ~> 6.0`, `azurerm ~> 4.0`, `google ~> 5.0`. Check with `context7` before relying
on these — they move.

## Procedure

1. **Discover** — the shared context file plus the plan's Technical Context. Identify
   the dialect, provider versions, state backend, and environment layout.
2. **Confirm state** — remote backend with locking configured. If not, that is the
   first change, before any resource.
3. **Choose Terraform or Terragrunt** using
   [terragrunt.md](./references/terragrunt.md). Never migrate an existing project
   mid-flight as a side effect of another change.
4. **Look up current syntax** with `context7` for the pinned provider version.
5. **Write the module** to [module-structure.md](./references/module-structure.md),
   loading the cloud-specific reference for resource patterns.
6. **Validate** — `terraform fmt -check`, `terraform validate`, then
   `terraform plan -out=tfplan`. Run `tflint`, and `tfsec` or `checkov` where the
   project has them.
7. **Estimate cost** for new resources.
8. **Deliver apply instructions** — do not apply.

## Output

```markdown
## Terraform Implementation Summary

### Current state
### Proposed configuration
- Provider, resources created or modified

### Variables
| Variable | Type | Required | Description |

### State backend
### Cost estimate
- Approximate monthly cost for new resources

### Apply instructions
1. `terraform init`
2. `terraform plan -out=tfplan`
3. Review the plan
4. `terraform apply tfplan`

### Files changed
```

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| Hardcode sizes and names in resources | Variables with defaults and validation |
| Local state | Remote backend with locking |
| Unpinned providers | Constraints in `versions.tf`, lock file committed |
| Undocumented variables | `description` and `type` on every one |
| One giant root module | Composable modules with clear interfaces |
| Copy a module to change one value | Parameterize it |
| Apply without a reviewed plan | Plan, review, then apply the saved plan |

## Related skills in this plugin

- [Implementing CI/CD pipelines](../implementing-ci-cd-pipelines/SKILL.md) — running
  plan and apply safely in a pipeline
- [Managing secrets](../managing-secrets/SKILL.md) — credentials and state hygiene
- [Optimizing cloud cost](../optimizing-cloud-cost/SKILL.md) — sizing and pricing model
- [Designing multi-cloud architecture](../designing-multi-cloud-architecture/SKILL.md) —
  service selection before provisioning
