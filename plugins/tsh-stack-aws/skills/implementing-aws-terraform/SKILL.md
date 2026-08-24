---
name: implementing-aws-terraform
description: "AWS-specific Terraform patterns and Well-Architected defaults: VPC with public and private subnets, EKS with Pod Identity and pinned AMI release versions, RDS, S3, ALB, Lambda and reusable security groups, encryption and least-privilege IAM by default, and the AWS provider version to pin. Use when provisioning AWS infrastructure with Terraform or reviewing AWS infrastructure code."
when_to_use: "Trigger on: writing or reviewing Terraform for AWS resources, `provider \"aws\"` in a project, designing a VPC or subnet layout, standing up EKS with node groups and workload IAM, RDS or Aurora provisioning, S3 buckets with encryption and lifecycle rules, ALB and target groups, Lambda with an execution role, security group modules, or choosing the AWS provider version constraint."
---

# Implementing AWS Terraform

AWS resource patterns and the defaults TSH provisions them with. Module *structure* —
file layout, variable validation, state, testing, Terragrunt — is generic and is not
repeated here; this skill is what goes inside AWS modules.

## Applicability and Precedence

The project's existing modules outrank these patterns. Read `versions.tf` and
`.terraform.lock.hcl` for the pinned provider version before consulting any
documentation, and search with that version — AWS provider resource arguments change
between majors.

Verify current instance families, EKS versions and service availability in the target
region against AWS documentation before naming a specific size or version. These move
every few months, and a stale value fails at apply, not at review.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Run `terraform plan` and read the output before proposing any change. |
| MUST | Encrypt at rest by default — S3, EBS, RDS, EFS — and prefer a customer-managed KMS key where the data is not public. |
| MUST | Use least-privilege IAM. A wildcard `Action` or `Resource` needs a stated reason, and `*/*` needs a better one. |
| MUST | Apply the project's mandatory tags to every taggable resource, merged so consumers can add their own. |
| MUST | Include a cost estimate for new resources. NAT gateways, provisioned IOPS and idle load balancers are the usual surprises. |
| NEVER | Run `apply`, `destroy` or `-auto-approve` without explicit authorization for that specific action. Deliver apply instructions instead. |
| NEVER | Open a security group to `0.0.0.0/0` on an administrative port — 22, 3389, or a database port. |
| NEVER | Make console changes the code does not capture. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Module patterns](./references/module-patterns.md) | Provisioning any of these resource families | VPC, EKS, RDS, S3, ALB, Lambda, security groups — what each module should contain |

## Provider

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

Confirm the current major with `context7` against the Terraform AWS provider docs
before starting a greenfield project; match the project's existing pin otherwise.

## Well-Architected defaults

Apply these unless the project documents a reason not to:

1. **Encryption on by default**, KMS for anything non-public.
2. **Least-privilege IAM**, scoped to the specific resource ARNs.
3. **Consistent tagging**, injected by the module rather than by the caller.
4. **Logging and monitoring enabled** — VPC Flow Logs, ALB access logs, RDS logs,
   CloudWatch Logs with an explicit retention.
5. **Backups configured** with a retention period, and a stated restore procedure.
6. **PrivateLink and VPC endpoints** over NAT for AWS-service traffic. Gateway
   endpoints for S3 and DynamoDB are free and frequently pay for the whole exercise.
7. **GuardDuty and Security Hub** enabled at the account level.
8. **Multi-AZ for production** datastores, single-AZ below it.

## Procedure

1. **Establish context** — provider pin, existing module conventions, state backend,
   environment layout, tagging convention already in use.
2. **Confirm remote state with locking** exists. If not, that is the first change.
3. **Look up current syntax** with `context7` for the pinned provider version, and
   current instance families and regional availability with the AWS documentation
   server.
4. **Write the module**, following the resource patterns in
   [module-patterns.md](./references/module-patterns.md) and the defaults above.
5. **Validate** — `terraform fmt -check`, `terraform validate`,
   `terraform plan -out=tfplan`, then `tflint` and `tfsec` or `checkov` where the
   project has them.
6. **Estimate cost**, calling out NAT gateways, provisioned IOPS, idle load balancers
   and cross-AZ transfer explicitly.
7. **Deliver apply instructions.** Do not apply.

## AWS-specific anti-patterns

| Don't | Do |
| :-- | :-- |
| `gp2` volumes | `gp3` — cheaper and faster at the same size |
| Previous-generation instances | Current generation; Graviton where the workload rebuilds |
| NAT gateway carrying S3 or DynamoDB traffic | Gateway VPC endpoint |
| One NAT gateway per AZ in non-production | `single_nat_gateway = true` below production |
| IAM user with long-lived access keys | Roles, and OIDC federation from CI |
| Access keys in a Lambda environment variable | Execution role |
| Log groups with no retention | Explicit retention per environment |
| Multi-AZ RDS in staging | Single-AZ outside production |
| Public S3 bucket for private data | Bucket policy plus Block Public Access at the account level |
| Hardcoded AMI ID | SSM parameter for the recommended release version |

## Related

Generic Terraform mechanics — module file layout, variable validation, state backends,
Terragrunt, Terratest — live in `implementing-terraform-modules` in the
`tsh-platform-engineering` plugin. Auditing an existing account for cost and tag
compliance is [auditing AWS cost](../auditing-aws-cost/SKILL.md) in this plugin.
