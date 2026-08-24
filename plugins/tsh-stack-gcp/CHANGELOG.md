# Changelog

All notable changes to `tsh-stack-gcp` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-22

Initial release. Carries the GCP-specific half of TSH's infrastructure guidance, split
out of `tsh-platform-engineering` so that a GCP repository installs GCP content and
nothing else.

### Added

- **`implementing-gcp-terraform`** — VPC with secondary IP ranges, private GKE with
  Workload Identity, Dataplane V2 and Cilium network policy, Cloud SQL on private IP
  with PITR, Cloud Storage with uniform bucket-level access and CMEK, Cloud Run with
  direct VPC egress, Pub/Sub with dead-letter topics, Secret Manager, Cloud Armor;
  Architecture Framework defaults and provider pinning.
- **`auditing-gcp-cost`** — the complete audit: scope, infrastructure code, live
  read-only inventory, drift and shadow-resource detection, per-service waste checks,
  label compliance, billing-export attribution, and a saved presentation-ready report.
- **`.mcp.json`** with `context7` and the three Google Cloud MCP servers.

### Notes on the split

- **Each skill here stands alone.** A path into another plugin is not stable across
  install modes, so nothing file-links `tsh-platform-engineering`; the audit skill
  therefore carries its own procedure and report format rather than borrowing them.
  The audit workflow reads similarly to its AWS counterpart by design — the two diverge
  in data sources (BigQuery billing export rather than Cost Explorer), service families,
  the label dialect, and report identifiers, which is where the substance is.
- **Descriptions carry the routing.** `optimizing-cloud-cost` in the discipline plugin
  describes the cloud-agnostic framework; `auditing-gcp-cost` describes an audit of a
  specific GCP project. No delegation instruction connects them, matching how
  `implementing-nestjs-api` and `reviewing-code` already coexist.
