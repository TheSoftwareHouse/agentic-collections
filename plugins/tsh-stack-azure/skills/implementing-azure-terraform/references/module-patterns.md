# Azure Terraform module patterns

What each module should contain. Structure and interface conventions are generic and
belong to `implementing-terraform-modules`; this is the Azure-specific content.

## VNet

- Virtual Network with a planned address space — size it before writing anything;
  Azure allows adding address space but not renumbering in place
- Subnets with address prefixes, and **an NSG per subnet** rather than one shared NSG
- Route tables where forced tunnelling or a network appliance is in play
- **Delegated subnets** for the PaaS services that require them — Flexible Server, App
  Service VNet integration, Container Apps. A delegated subnet cannot host anything
  else, so plan it as its own range
- Private DNS zones plus VNet links for every private endpoint you intend to create.
  A private endpoint without its DNS zone resolves to the public IP and the failure
  looks like a firewall problem
- DDoS protection plan where the workload is internet-facing and the tier justifies it
- VNet peering support, remembering that peering bills for traffic **in both
  directions**

## AKS

- Cluster with a **system node pool** (control-plane workloads only, tainted) and one or
  more **user node pools** for applications
- **Workload Identity** — `workload_identity_enabled = true`, which requires
  `oidc_issuer_enabled = true`. AAD pod identity is deprecated; do not use it
- Azure CNI or kubenet. Azure CNI consumes a VNet IP per pod, so the subnet must be
  sized for maximum pod count — use CNI Overlay where address space is tight
- Private cluster where the control plane should not be internet-reachable
- Entra ID integration with Kubernetes RBAC, rather than local admin credentials
- Cluster autoscaler per node pool, with min and max set deliberately
- Azure Monitor for Containers, with cost-conscious collection — full container-log
  collection on a busy cluster is one of the larger Log Analytics bills
- Spot node pools for fault-tolerant workloads

The cluster's SKU tier is a cost decision: Free has no uptime SLA, Standard buys one.
Pick deliberately rather than defaulting.

## Azure Database for PostgreSQL / MySQL

- **Flexible Server** — Single Server is retired
- High availability zone-redundant in production, same-zone or none below it
- Automated backups with a retention period, and geo-redundant backup only where a
  cross-region recovery objective requires it
- **Private DNS zone plus VNet integration** on a delegated subnet. Note that a
  Flexible Server's networking mode is fixed at creation: switching between public
  access and VNet integration requires a rebuild
- Firewall rules only in the public-access mode, and never `0.0.0.0`
- Server parameters set explicitly rather than left at defaults
- Read replicas where read load justifies them
- Maintenance window set to the application's quiet hours

Never put the administrator password in a variable default or a committed `.tfvars`.
Read it from Key Vault as a data source.

## Blob Storage

- Storage account with the **redundancy tier chosen deliberately** — LRS, ZRS, GRS or
  GZRS. This is one of the largest silent cost multipliers on Azure: GRS is roughly
  double LRS, and it is frequently selected for data that has no cross-region
  requirement
- Access tier by pattern: Hot, Cool, Cold, Archive
- Lifecycle management policies transitioning by age, and deleting incomplete uploads
- Soft delete and versioning, with a policy expiring old versions — versioning with no
  expiry grows without bound
- **Private endpoint**, with public network access disabled
- Customer-managed keys where the data classification requires it
- `min_tls_version` at the current floor, and shared-key access disabled in favour of
  Entra ID
- Static website hosting only where that is genuinely the purpose

## Application Gateway and WAF

- Application Gateway v2, with autoscaling bounds rather than a fixed instance count
- WAF policy with the OWASP ruleset, **deployed in detection mode first** — prevention
  mode from the start blocks legitimate traffic and the cause is not obvious from the
  application side
- TLS termination using certificates from Key Vault, referenced by identity rather than
  uploaded
- Backend pools, HTTP settings, and health probes that hit an endpoint proving the app
  works rather than a static 200
- Note the fixed hourly cost plus capacity units: an Application Gateway in front of a
  low-traffic service is often more expensive than the service

## Key Vault

- RBAC authorization model rather than legacy access policies
- Secrets, keys and certificates separated by purpose, with distinct RBAC assignments
- **Soft delete and purge protection**, both enabled. Purge protection cannot be
  disabled once on — that is the point, and it is what makes CMEK safe
- Private endpoint, with network ACLs defaulting to deny
- Diagnostic logging to Log Analytics, since vault access is an audit trail
- One vault per environment boundary, not one per application, so rotation and access
  review stay manageable

## Azure Container Registry

- SKU by need: Basic, Standard, or Premium for geo-replication and private endpoints
- Geo-replication only on Premium, and only where pull latency or egress justifies it
- Private endpoint on Premium
- **Retention policy for untagged manifests** — without it, image layers accumulate
  indefinitely and storage overage is a recurring finding
- Webhook integrations where a downstream deploy is triggered by a push

## Service Bus

- Namespace SKU by need: Standard, or Premium for private endpoints, larger messages
  and predictable throughput
- Queues with **dead-letter settings** — without a dead-letter destination a
  permanently failing message redelivers until it expires
- Topics and subscriptions with filters defined explicitly
- Message TTL and lock duration matched to real processing time
- Private endpoint on Premium

Premium bills a fixed hourly rate per messaging unit whether or not messages flow;
Standard bills per operation. For low, spiky volume, Standard is usually cheaper.
