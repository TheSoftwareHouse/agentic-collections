# Multi-cloud decision framework and cross-cutting concerns

## Decision Framework

Use the following decision tree to select the appropriate pattern:

```
Is DR / HA across providers required?
  └─ Yes → Pattern 1 (Single Provider + DR) or Pattern 3 (Geo Distribution)

Is the primary goal to use best cloud services per domain?
  └─ Yes → Pattern 2 (Best-of-Breed)

Is vendor lock-in the primary concern?
  └─ Yes → Pattern 4 (Cloud-Agnostic Abstraction)

Is workload bursty with on-prem baseline?
  └─ Yes → Pattern 5 (Cloud Bursting)

Is analytics / BI the primary cross-cloud integration point?
  └─ Yes → Pattern 6 (Data Mesh)
```

---

## Cross-Cutting Concerns

### Identity & Access Management

- Use federated identity (OIDC / SAML) across providers
- Centralise in Microsoft Entra ID (formerly Azure AD) or Okta when enterprise M365 is in use
- Apply least-privilege on all cloud accounts via IaC

### Networking

- Use private connectivity (AWS PrivateLink, Azure Private Link, GCP Private Service Connect) between clouds where possible
- VPN or dedicated interconnects (AWS Direct Connect + Azure ExpressRoute) for high-throughput or low-latency paths
- Zero-trust networking model: no implicit trust between cloud segments

### Observability

- Collect metrics, logs, and traces using OpenTelemetry
- Ship to a neutral SIEM / APM (Datadog, Grafana Cloud, Elastic)
- Avoid cloud-native logging silos (CloudWatch, Azure Monitor, Cloud Logging) as the *only* sink

### Security & Compliance

- Centralised CSPM (Wiz, Prisma Cloud, Lacework) across all cloud accounts
- Unified policy engine (OPA) deployed via CI/CD
- Automated compliance scanning in all pipelines
- Shared responsibility model documented per provider

### Cost Management

- Tag all resources with `environment`, `team`, `cost-centre`, and `project`
- Use a cross-cloud FinOps platform (CloudHealth, Apptio Cloudability, FOCUS standard)
- Set budget alerts in each cloud; roll up to a central dashboard
- Review reserved/committed usage quarterly

---

## Related references

- [Multi-cloud patterns](./patterns.md) — the six patterns this framework selects between
- [Service comparison](./service-comparison.md) — provider service equivalents
- [Optimizing cloud cost](../../optimizing-cloud-cost/SKILL.md) — cross-cloud cost work
