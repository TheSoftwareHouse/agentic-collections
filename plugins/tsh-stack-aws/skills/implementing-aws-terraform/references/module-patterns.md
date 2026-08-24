# AWS Terraform module patterns

What each module should contain. Structure and interface conventions are generic and
belong to `implementing-terraform-modules`; this is the AWS-specific content.

## VPC

- VPC with public and private subnets across the availability zones in use
- Internet Gateway, and NAT gateways sized to the environment — one per AZ in
  production, `single_nat_gateway = true` below it
- Route tables and associations
- Network ACLs where a subnet-level boundary is genuinely required; security groups
  are the usual answer
- VPC Flow Logs, with a retention period
- **Gateway VPC endpoints for S3 and DynamoDB.** Free, and they take that traffic off
  the NAT gateway entirely — the single highest-value line in most VPC modules
- Interface endpoints for the AWS services the workload actually calls

Plan the CIDR before writing anything. Resizing a VPC in place is not possible, and
overlapping ranges block every future peering or transit-gateway attachment.

## EKS

- Cluster with managed node groups
- **EKS Pod Identity** for workload IAM — preferred since 2023 — or IRSA on older
  clusters. Both beat node-level instance profiles, which grant every pod on the node
  the same permissions
- Node AMI `amazon-linux-2023`, with the release version pinned via the SSM parameter
  `/aws/service/eks/optimized-ami/{version}/amazon-linux-2023/x86_64/standard/recommended/release_version`
- Cluster autoscaler, or Karpenter where node shapes vary
- VPC CNI configuration, including prefix delegation if pod density matters — the
  default IP-per-pod allocation exhausts subnet addresses faster than teams expect
- Control-plane logging enabled, with retention
- Spot node pools for anything fault-tolerant

Pin the Kubernetes version explicitly and treat upgrades as their own change. An
unpinned cluster version drifts on managed upgrades.

## RDS

- Instance or Aurora cluster, with the engine version pinned
- Automated backups with a retention period, and `deletion_protection` in production
- Read replicas where read load justifies them
- Parameter groups and subnet groups owned by the module, not shared by accident
- Security group allowing only the application's security group as a source, never a
  CIDR
- Multi-AZ in production, single-AZ below
- `storage_encrypted = true`, `performance_insights_enabled` where useful
- `gp3` storage rather than `gp2`

Never put the master password in a variable default or a committed `.tfvars`. Use a
managed secret and read it as a data source, or let RDS manage it.

## S3

- Versioning enabled, with a noncurrent-version expiry — versioning without expiry
  grows without bound and is a common cost finding
- Server-side encryption, KMS for non-public data
- **Block Public Access at the bucket and the account level**
- Bucket policy denying unencrypted transport (`aws:SecureTransport`)
- Lifecycle rules transitioning to Standard-IA, Glacier and Deep Archive by access
  pattern, and aborting incomplete multipart uploads
- Replication only where a stated requirement calls for it
- Access logging where the data is sensitive

## ALB

- Application Load Balancer with target groups per service
- Listener rules, HTTP redirecting to HTTPS
- ACM certificate, with a modern TLS policy
- Access logs to S3, with a lifecycle rule
- Health checks that hit an endpoint proving the app works, not a static 200
- Deletion protection in production

## Lambda

- Function with an execution role scoped to exactly what it calls
- CloudWatch log group created by the module, with retention — otherwise Lambda
  creates one with infinite retention that nobody notices
- Environment variables for configuration; secrets read at runtime from a secret store
- VPC configuration only when the function needs private resources: it adds cold-start
  latency and requires NAT for internet egress
- Memory sized from measured duration — on Lambda, more memory often costs less
- Reserved concurrency where a downstream dependency needs protection

## Security groups

- Reusable rule sets with descriptions on every rule; an undescribed rule is
  undeletable in practice because nobody knows what it was for
- **Source another security group, not a CIDR**, for internal traffic
- Egress narrowed where the compliance posture requires it, rather than the default
  allow-all
- Dynamic rule creation from a variable, so environments differ by data not by code
- Never `0.0.0.0/0` on 22, 3389, or a database port
