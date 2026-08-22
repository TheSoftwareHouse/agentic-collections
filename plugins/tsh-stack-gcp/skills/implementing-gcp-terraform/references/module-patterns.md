# GCP Terraform module patterns

What each module should contain. Structure and interface conventions are generic and
belong to `implementing-terraform-modules`; this is the GCP-specific content.

## VPC

- **Custom-mode VPC.** Auto-mode creates a subnet in every region with fixed
  overlapping ranges, which blocks peering forever and cannot be undone in place
- Subnets with **secondary IP ranges for GKE pods and services** — size these before
  creating the cluster; a pod range that is too small caps cluster size and cannot be
  expanded afterwards
- Cloud Router and Cloud NAT for private-subnet egress
- Firewall rules, ingress and egress, sourced by service account or network tag rather
  than by CIDR where possible
- VPC peering or Shared VPC support
- **Private Google Access per subnet**, so calls to Google APIs bypass Cloud NAT
  entirely — the highest-value line in most GCP VPC modules, both for cost and for
  egress posture

## GKE

- Standard or Autopilot. Autopilot unless the workload needs node-level control:
  DaemonSets, specific machine shapes, or GPU topologies
- **Private cluster** with authorized networks for the control plane
- **Workload Identity** — `workload_identity_config { workload_pool = "PROJECT_ID.svc.id.goog" }`
- Node pools with autoscaling, and Spot VM pools for fault-tolerant work
- Binary Authorization where supply-chain control is required
- Shielded nodes
- **Dataplane V2** — `datapath_provider = "ADVANCED_DATAPATH"`
- Cilium cluster-wide network policy — `enable_cilium_clusterwide_network_policy = true`,
  which requires `ADVANCED_DATAPATH`
- In-transit encryption —
  `in_transit_encryption_config = "IN_TRANSIT_ENCRYPTION_INTER_NODE_TRANSPARENT"`
- Cloud Monitoring and Logging integration, with log exclusions configured

Pin the cluster version and treat upgrades as their own change. Release channels
auto-upgrade, which is usually right but should be a decision rather than a surprise.

## Cloud SQL

- PostgreSQL or MySQL, with the version pinned
- Regional HA in production, zonal below it
- Automated backups **and point-in-time recovery** — backups alone lose everything
  since the last one
- **Private IP** via VPC peering with `servicenetworking.googleapis.com`
- SSL enforced
- Database flags set explicitly rather than left at defaults
- Read replicas where read load justifies them
- Maintenance window set to the application's quiet hours
- `deletion_protection` in production
- Disk autoresize with a **cap** — uncapped autoresize turns a runaway query into an
  unbounded bill, and disk size cannot be reduced afterwards

## Cloud Storage

- Storage class chosen by access pattern — `STANDARD`, `NEARLINE`, `COLDLINE`, `ARCHIVE`
- **Uniform bucket-level access**, disabling ACLs
- Versioning, with a lifecycle rule expiring noncurrent versions
- Lifecycle rules transitioning by age, and aborting incomplete multipart uploads
- Retention policy where compliance requires it — note it is irreversible once locked
- CMEK with Cloud KMS for sensitive data
- Pub/Sub notifications where downstream processing is event-driven
- Access logging to a separate audit bucket

## Cloud Run

- Service or job, with concurrency and resource limits set
- **Direct VPC egress** for private access. The Serverless VPC Access connector is
  legacy: it costs per instance and adds a hop
- IAM invoker bindings — never `allUsers` unless the service is genuinely public
- Secrets injected from Secret Manager, not environment literals
- **CPU allocation deliberate**: request-based for low traffic, always-on only where a
  background thread or in-memory cache genuinely needs it. Always-on CPU on a
  low-traffic service is the most common GCP overspend
- `min_instances` above zero only where cold start is unacceptable
- Traffic splitting for canary and blue-green releases

## Pub/Sub

- Topic with CMEK where the payload is sensitive
- Subscription, push or pull, with the acknowledgement deadline matched to real
  processing time
- **Dead-letter topic on every subscription.** Without one, a permanently failing
  message redelivers until it expires, consuming quota and burying real traffic
- Message retention set explicitly
- IAM bindings scoped to publisher and subscriber roles separately

## Secret Manager

- Secret with automatic replication, or user-managed replication where data residency
  requires it
- Versions, with the previous version disabled rather than destroyed during rotation
- IAM bindings granting `secretAccessor` to exactly the consuming service account
- Rotation schedule with a Pub/Sub notification

## Cloud Armor

- Security policy, global or regional to match the load balancer
- IP allowlist and denylist rules
- **Preconfigured WAF rules (OWASP CRS)**, deployed in preview mode first — enforcing
  them straight away blocks legitimate traffic and the cause is not obvious
- Rate-based limiting
- Threat-intelligence integration where the tier includes it
