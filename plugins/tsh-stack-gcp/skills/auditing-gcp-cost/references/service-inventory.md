# GCP service inventory

The checklist a GCP cost audit walks, service family by service family. The workflow and
data sources are in the parent [SKILL.md](../SKILL.md).

Walk every family unless the user narrowed the scope. The findings that recur most are
at the bottom, under networking and operations — not in compute, where people look
first.

## Per-service inventory

### Compute

- **Compute Engine** — machine type and generation, committed-use vs on-demand,
  sustained-use discount already applied, CPU and memory utilization
- **Managed instance groups** — min/max/target size, whether target sits at max
- **Cloud Run** — CPU allocation (always-on vs request-based — always-on on a
  low-traffic service is a common overspend), min instances above zero, concurrency
- **Cloud Functions** — memory, timeout, min instances
- **GKE** — Autopilot vs Standard, node pool machine types, Spot VM node pools for
  fault-tolerant workloads, cluster autoscaler bounds

`e2` machine types are the cheapest general-purpose option; `n1` is previous
generation and should move to `n2` or `e2`. Spot VMs on GKE node pools carry up to
91% saving for anything that tolerates preemption.

### Storage

- **Persistent Disks** — type (`pd-standard`, `pd-balanced`, `pd-ssd`, `pd-extreme`),
  size vs used, **unattached disks**
- **Cloud Storage** — lifecycle policies, class distribution across
  Standard/Nearline/Coldline/Archive, versioning with no noncurrent expiry, retention
  policies
- **Filestore** — tier and capacity against actual use
- **Snapshots** — orphaned snapshots and snapshot schedules with no retention limit

`pd-ssd` where `pd-balanced` would serve is the most common storage finding.

### Databases

- **Cloud SQL** — tier and machine type, HA enabled on non-production, storage type,
  disk autoresize with no cap, backup retention
- **AlloyDB** — instance count and machine type
- **Firestore** — document reads, writes and deletes billed per operation, stored data and backups; Native vs Datastore mode
- **Bigtable** — node count, SSD vs HDD storage
- **Memorystore** — tier and memory size against actual use

### Networking

- **Cloud NAT** — hourly plus per-GB data processing; Private Google Access removes
  Google-API traffic from NAT entirely
- **Static external IPs** — reserved but unattached addresses bill hourly
- **Load balancers** — idle or near-zero-traffic forwarding rules
- **Cloud CDN** — cache hit ratio against origin egress
- **Interconnect and VPN** — provisioned capacity vs utilization
- **Data transfer** — inter-zone, cross-region, internet egress

### Containers, serverless, AI/ML

- **Artifact Registry** — cleanup policies, image accumulation
- **API Gateway / Apigee** — tier against traffic
- **Workflows** — execution volume
- **Vertex AI** — endpoint machine type, auto-scaling, endpoints left deployed with
  no prediction traffic
- **GPUs and TPUs** — type (T4, L4, A100, H100) and utilization; an idle accelerator
  is the most expensive idle resource in any project

### Security and operations

- **VPC firewall rules** — `0.0.0.0/0` ingress, especially ports 22 and 3389. A
  security finding, reported regardless of cost impact.
- **Cloud KMS** — unused keys and their rotation policy
- **Cloud Logging** — retention settings, exclusions, routing sinks; ingestion is the
  cost driver, so exclusions matter more than retention
- **Pub/Sub** — unused topics and subscriptions, message retention duration
- **Secret Manager** — unused secrets, each billing per version per month

## Label compliance

Read labels with `gcloud asset search-all-resources --format=json` for project-wide
coverage in one call, and check against the mandatory label table in the parent
[SKILL.md](../SKILL.md).

## GCP-specific anti-patterns

| Finding | Correction |
| :-- | :-- |
| `pd-ssd` for general workloads | `pd-balanced` |
| `n1` machine types | `e2` or `n2` |
| Cloud Run with always-on CPU on low traffic | Request-based CPU allocation |
| GKE Standard with hand-managed node pools for a simple workload | Autopilot |
| On-demand GKE nodes for batch | Spot VM node pool |
| Cloud NAT carrying Google API traffic | Private Google Access |
| HA Cloud SQL in staging | Single-zone outside production |
| Logging with no exclusions | Exclude high-volume low-value log lines at ingestion |
| Committed use discounts unused on steady workloads | 1-year or 3-year commitment |
