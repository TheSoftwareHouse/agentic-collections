# Changelog

All notable changes to `tsh-stack-aws` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-22

Initial release. Carries the AWS-specific half of TSH's infrastructure guidance, split
out of `tsh-platform-engineering` so that an AWS repository installs AWS content and
nothing else.

### Added

- **`implementing-aws-terraform`** — VPC, EKS, RDS, S3, ALB, Lambda and security-group
  module patterns, Well-Architected defaults for encryption, IAM, logging and backups,
  provider pinning, and AWS-specific anti-patterns.
- **`auditing-aws-cost`** — the complete audit: scope, infrastructure code, live
  read-only inventory, drift and shadow-resource detection, per-service waste checks,
  tag compliance, Cost Explorer attribution, and a saved presentation-ready report.
- **`.mcp.json`** with `context7` and the AWS Labs `aws-documentation` server, both
  read-only.

### Notes on the split

- **Each skill here stands alone.** A path into another plugin is not stable across
  install modes, so nothing file-links `tsh-platform-engineering`; the audit skill
  therefore carries its own procedure and report format rather than borrowing them.
  The audit workflow reads similarly to its GCP counterpart by design — the two
  diverge in data sources, service families and report identifiers, which is where the
  substance is.
- **Descriptions carry the routing.** `optimizing-cloud-cost` in the discipline plugin
  describes the cloud-agnostic framework; `auditing-aws-cost` describes an audit of a
  specific AWS account. No delegation instruction connects them, matching how
  `implementing-nestjs-api` and `reviewing-code` already coexist.
