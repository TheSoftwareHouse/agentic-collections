# AWS service inventory

The checklist an AWS cost audit walks, service family by service family. The workflow
and data sources are in the parent [SKILL.md](../SKILL.md).

Walk every family unless the user narrowed the scope. The findings that recur most are
at the bottom, under networking and operations — not in compute, where people look
first.

## Per-service inventory

### Compute

- **EC2** — instance type and generation, purchase type (on-demand vs reserved vs
  spot), CPU and memory utilization, instances stopped but with attached storage
- **Auto Scaling groups** — min/max/desired, whether desired sits pinned at max
- **Lambda** — memory allocation vs actual use, timeout, provisioned concurrency
  left enabled on low-traffic functions
- **ECS / EKS** — task CPU and memory allocation vs use, node group instance types,
  Fargate vs EC2 launch type
- **Batch** — compute environment sizing, spot usage

Older instance generations are the single most common finding: `m5` → `m7g` is
typically 20–40% cheaper for the same performance, at the cost of an ARM rebuild.

### Storage

- **EBS** — volume type (`gp2` → `gp3` is almost always a saving), size vs used,
  provisioned IOPS actually consumed, **unattached volumes**
- **S3** — lifecycle policies present, storage class distribution, versioning with
  no expiry on noncurrent versions, incomplete multipart uploads
- **EFS** — throughput mode, infrequent-access lifecycle
- **Snapshots** — orphaned snapshots whose source volume is gone

### Databases

- **RDS** — instance class and generation, Multi-AZ on non-production, storage type,
  allocated vs used storage, backup retention
- **Aurora** — instance count, Serverless v2 min/max ACU
- **DynamoDB** — provisioned vs on-demand against actual traffic, unused GSIs
- **ElastiCache** — node type, cluster mode, actual memory used

### Networking

Networking is where unexplained spend usually hides:

- **NAT Gateways** — hourly cost plus per-GB processing; VPC endpoints for S3 and
  DynamoDB frequently pay for themselves within a month
- **Elastic IPs** — unassociated addresses bill hourly
- **Load balancers** — idle or near-zero-request ALBs and NLBs
- **CloudFront** — price class, cache hit ratio
- **Data transfer** — cross-AZ, cross-region, internet egress

### Containers, serverless, AI/ML

- **ECR** — lifecycle policies, untagged image accumulation
- **API Gateway** — endpoint type, caching enabled and sized
- **Step Functions** — standard vs express against execution volume
- **SageMaker** — endpoint instance type, auto-scaling, endpoints left running with
  no invocations
- **Bedrock** — model choice against token volume
- **GPU instances** — utilization; an idle GPU is the most expensive idle resource in
  any account

### Security and operations

- **Security groups** — `0.0.0.0/0` ingress, especially ports 22 and 3389. A security
  finding, reported in the report's security section regardless of cost impact.
- **KMS** — keys with no recent usage, each billing monthly
- **CloudWatch Logs** — log groups with no retention policy, which grow forever
- **SNS / SQS** — unused topics and queues
- **Secrets Manager** — unused secrets, each billing monthly

## Tag compliance

Read tags with `aws resourcegroupstaggingapi get-resources`, which covers most services
in one call, and check against the mandatory tag table in the parent
[SKILL.md](../SKILL.md).

## AWS-specific anti-patterns

| Finding | Correction |
| :-- | :-- |
| `gp2` volumes | `gp3` — cheaper and faster at the same size |
| Previous-generation instances | Current generation, Graviton where the workload rebuilds |
| NAT Gateway carrying S3 traffic | Gateway VPC endpoint |
| Multi-AZ RDS in staging | Single-AZ outside production |
| Log groups with no retention | Explicit retention per environment |
| Provisioned concurrency on low-traffic Lambda | Remove it |
| DynamoDB provisioned at peak | On-demand, or auto-scaling |
