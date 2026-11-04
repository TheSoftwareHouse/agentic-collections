---
title: implementing-aws-terraform
sidebar_label: implementing-aws-terraform
sidebar_position: 2
description: AWS-specific Terraform patterns and Well-Architected defaults for VPC, EKS, RDS, S3, ALB, Lambda and security groups, with the AWS provider version to pin.
sources:
  - plugins/tsh-stack-aws/skills/implementing-aws-terraform/SKILL.md
  - plugins/tsh-stack-aws/skills/implementing-aws-terraform/references/
sources_hash: "bc9a302774d1fa9e9fd6cfc3a733b5ffea18b051c2ae36e256d47afdf9863e9e"
---

# implementing-aws-terraform

**Plugin:** [tsh-stack-aws](/docs/plugins/tsh-stack-aws/)  
**Invoke:** `/tsh-stack-aws:implementing-aws-terraform`. Claude also loads it when the work matches
its description.  
**Used by:** the [implementing-terraform-modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules)
skill, which leaves cloud-specific resource patterns to it where the repository's cloud plugin is
installed.

AWS resource patterns and the defaults TSH provisions them with. Module structure (file layout,
variable validation, state, testing, Terragrunt) is generic and not repeated here; this skill covers
what goes inside AWS modules.

The project's existing modules outrank these patterns. The skill reads `versions.tf` and
`.terraform.lock.hcl` for the pinned provider version before consulting any documentation, because
AWS provider resource arguments change between majors. It also verifies current instance families,
EKS versions and service availability in the target region against AWS documentation before naming a
specific size or version.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Run `terraform plan` and read the output before proposing any change. |
| MUST | Encrypt at rest by default (S3, EBS, RDS, EFS) and prefer a customer-managed KMS key where the data is not public. |
| MUST | Use least-privilege IAM. A wildcard `Action` or `Resource` needs a stated reason. |
| MUST | Apply the project's mandatory tags to every taggable resource, merged so consumers can add their own. |
| MUST | Include a cost estimate for new resources. NAT gateways, provisioned IOPS and idle load balancers are the usual surprises. |
| NEVER | Run `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Open a security group to `0.0.0.0/0` on an administrative or database port. |
| NEVER | Make console changes the code does not capture. |

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Provider** | `hashicorp/aws` with the example constraint `~> 6.0`. The current major is confirmed with `context7` for a greenfield project; otherwise the project's existing pin is matched. |
| **VPC** | Public and private subnets across the availability zones in use, NAT gateways sized to the environment, gateway VPC endpoints for S3 and DynamoDB, VPC Flow Logs with retention. The CIDR is planned before anything is written. |
| **EKS** | Managed node groups, EKS Pod Identity (or IRSA on older clusters) over node-level instance profiles, `amazon-linux-2023` nodes with the release version pinned through an SSM parameter, an explicitly pinned Kubernetes version. |
| **RDS** | Pinned engine version, automated backups, `deletion_protection` in production, access allowed only from the application's security group, `storage_encrypted = true`, `gp3` storage, no master password in a variable default. |
| **S3** | Versioning with a noncurrent-version expiry, server-side encryption, Block Public Access at the bucket and account level, a policy denying unencrypted transport, lifecycle rules. |
| **ALB** | Target groups per service, HTTP redirecting to HTTPS, an ACM certificate, access logs to S3, health checks that prove the app works. |
| **Lambda** | An execution role scoped to what the function calls, a module-created log group with retention, VPC configuration only when the function needs private resources, memory sized from measured duration. |
| **Security groups** | Reusable rule sets with a description on every rule, another security group rather than a CIDR as the source for internal traffic, never `0.0.0.0/0` on 22, 3389 or a database port. |
| **Well-Architected defaults** | Encryption by default, least-privilege IAM, tagging injected by the module, logging and monitoring, backups with a stated restore procedure, VPC endpoints over NAT for AWS-service traffic, GuardDuty and Security Hub at the account level, Multi-AZ for production datastores and single-AZ below. |
| **Anti-patterns** | A table of what not to do and what to do instead, for example long-lived IAM user access keys to roles and OIDC federation from CI, and a hardcoded AMI ID to an SSM parameter. |

## How it works

1. **Establish context.** Provider pin, existing module conventions, state backend, environment
   layout and the tagging convention already in use.
2. **Confirm remote state with locking exists.** If not, that is the first change.
3. **Look up current syntax** with `context7` for the pinned provider version, and current instance
   families and regional availability with the AWS documentation server.
4. **Write the module** following the resource patterns and the defaults.
5. **Validate.** `terraform fmt -check`, `terraform validate`, `terraform plan -out=tfplan`, then
   `tflint` and `tfsec` or `checkov` where the project has them.
6. **Estimate cost**, calling out NAT gateways, provisioned IOPS, idle load balancers and cross-AZ
   transfer.
7. **Deliver apply instructions.** The skill does not apply.

## Related skills

- [auditing-aws-cost](/docs/plugins/tsh-stack-aws/skills/auditing-aws-cost), which audits an
  existing account for cost and tag compliance.
- [implementing-terraform-modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules)
  in tsh-platform-engineering: module file layout, variable validation, state backends, Terragrunt
  and Terratest.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-aws/skills/implementing-aws-terraform/SKILL.md)
- [`references/module-patterns.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-aws/skills/implementing-aws-terraform/references/module-patterns.md)
