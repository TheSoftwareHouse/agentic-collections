# Azure service inventory

The checklist an Azure cost audit walks, service family by service family. The workflow
and data sources are in the parent [SKILL.md](../SKILL.md).

Walk every family unless the user narrowed the scope. Start with a single Resource Graph
query for the whole estate, then drill in — iterating `az` per service misses resources
in resource groups nobody remembers.

```kusto
Resources
| project name, type, location, resourceGroup, sku, tags
| order by type asc
```

## Compute

- **Virtual machines** — size and generation, utilization from Advisor, purchase type
  (pay-as-you-go vs reserved vs spot), **whether Azure Hybrid Benefit is applied** on
  Windows and SQL images
- **Deallocated VMs** — compute stops billing, but attached disks and reserved public
  IPs do not. A "shut down to save money" VM often still bills most of its cost
- **VM Scale Sets** — min, max and current capacity; whether capacity sits pinned at max
- **Availability sets and zones** — a spread that forces a larger SKU than needed
- **App Service Plans** — the classic Azure finding: **a plan bills whether or not it
  hosts a running app.** Stopping the app does not stop the bill, and a plan whose apps
  were deleted keeps charging. Check for plans with zero apps, and for oversized tiers
  on low-traffic sites
- **Functions** — Consumption vs Premium vs App Service plan; a Premium plan on a
  low-invocation function is pure overhead
- **Container Apps** — min replicas above zero, and the always-allocated CPU setting
- **AKS** — cluster SKU tier (Free vs Standard uptime SLA), node pool sizes and
  autoscaler bounds, spot pools for fault-tolerant work, and system pools oversized for
  what they actually run

## Storage

- **Managed disks** — this is the Azure-specific trap: **disks bill by provisioned
  performance tier, not by bytes used.** A P30 costs the same at 5 GB as at 1 TB, so
  check tier against both size *and* observed IOPS. Premium SSD where Standard SSD or
  Premium SSD v2 would serve is a routine finding
- **Unattached disks** — bill in full, forever, and accumulate after every VM rebuild
- **Snapshots** — orphaned snapshots whose source disk is gone; incremental vs full
- **Storage accounts** — see the tiering and redundancy section below
- **File shares** — Premium provisions capacity up front; Standard bills what is used

### Blob tiering and redundancy

| Access pattern | Blob tier |
| :-- | :-- |
| Frequent | Hot |
| Infrequent, 30+ days | Cool |
| Rare, 90+ days | Cold |
| Archive, 365+ days | Archive |

Pair every tier with a lifecycle policy, and check the **minimum retention period** —
deleting or rehydrating early still bills the remainder, so an aggressive policy on
short-lived data costs more than leaving it Hot.

**Redundancy is the bigger lever**: LRS to GZRS spans roughly a factor of two, and GRS on
data with no cross-region recovery objective is among the most common findings. Check
`account_replication_type` on every account against a stated recovery objective.

Also check: versioning and soft delete without an expiry policy, containers with no
lifecycle rule at all, and incomplete uploads left uncleaned.

## Databases

- **Azure SQL Database** — DTU vs vCore model, tier and size against utilization,
  **serverless auto-pause** for intermittent workloads, elastic pools where many small
  databases share capacity, and reserved capacity on steady vCore workloads
- **SQL Managed Instance** — sized generously by default; check vCores and storage
- **PostgreSQL / MySQL Flexible Server** — tier and size, HA on non-production, storage
  autogrow with no cap, backup retention beyond the recovery objective
- **Cosmos DB** — **provisioned RU/s versus autoscale versus serverless.** Provisioned
  throughput sized for peak is one of the largest single overspends on Azure; autoscale
  bills a fraction of peak, serverless suits spiky low volume. Also check unused
  secondary regions and multi-region writes nobody uses
- **Redis Cache** — tier and memory against actual working set

## Networking

Where unexplained Azure spend usually hides — most of these bill a fixed hourly rate
regardless of traffic:

- **NAT Gateway, VPN Gateway, ExpressRoute, Azure Bastion, Application Gateway,
  Firewall** — all hourly, all frequently provisioned for an environment that no longer
  exists. An Application Gateway in front of a low-traffic service commonly costs more
  than the service
- **Public IPs** — unassociated Standard IPs bill hourly; Basic is retiring
- **Load balancers** — Standard bills per rule plus data; check for idle ones
- **VNet peering** — bills for traffic **in both directions**, which surprises people
  designing hub-and-spoke
- **Bandwidth** — cross-region, cross-zone, and internet egress
- **Private endpoints** — each bills hourly; a proliferation across environments adds up

## Operations and security

- **Log Analytics** — usually the largest non-compute line. Ingestion drives cost more
  than retention, so check: per-table retention, **commitment tiers** (a large
  pay-as-you-go workspace is paying list price unnecessarily), the Basic Logs tier for
  high-volume low-value tables, and AKS container-log collection scope
- **Application Insights** — sampling rate; unsampled telemetry on a busy app is
  expensive
- **Recovery Services vaults** — backup retention beyond the stated objective, and
  policies still protecting deleted resources
- **Key Vault** — operation volume on Premium (HSM) keys where Standard would serve
- **Container Registry** — SKU, geo-replication nobody uses, and **untagged manifests
  with no retention policy**
- **Service Bus / Event Hubs** — Premium messaging units idle; Standard namespaces with
  no traffic
- **Defender for Cloud** — per-resource plans enabled on resource types that do not need
  them

## Security findings

Report these regardless of cost impact:

- NSG rules allowing `Internet` or `*` on 22, 3389, or a database port
- Storage accounts with public network access enabled, or anonymous blob access
- PaaS data services reachable from the public internet
- Key Vaults without purge protection
- Service principals with long-lived secrets where Managed Identity would serve

## Governance

- **Orphaned resources** — NICs with no VM, disks with no owner, empty App Service
  Plans, snapshots with no source
- **Resource locks** — note `CanNotDelete` locks before proposing any removal
- **Tag compliance** — resource by resource, because Azure does not inherit from the
  resource group
- **Reservation and savings-plan utilization** — under-used commitments are money already
  spent; report utilization percentage, not just whether a reservation exists
- **Dev/Test subscription pricing** — available for non-production and frequently unused
