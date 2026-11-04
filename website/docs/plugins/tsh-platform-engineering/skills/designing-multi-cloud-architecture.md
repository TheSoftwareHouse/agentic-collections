---
title: Designing Multi-Cloud Architecture
sidebar_label: Designing Multi-Cloud Architecture
sidebar_position: 7
description: Selects cloud services and a multi-cloud topology with an explicit decision framework - the six multi-cloud patterns, AWS, Azure and GCP service mapping, where abstraction pays for itself, and migration phasing.
sources:
  - plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
sources_hash: "ebccee9dc5ac1cf38dbd527b39bda4d92dcdd43b136afc5276083677af51cda0"
---

# Designing Multi-Cloud Architecture

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:designing-multi-cloud-architecture`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer)

Selects cloud services and a multi-cloud topology starting from the driver, not the pattern. Multi-cloud has a real operational cost (two control planes, two skill sets, egress between them), so a topology that no stated requirement forces is a liability rather than a hedge.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file. A provider already in production, or a decision record in `docs/decisions/`, settles the question. A topology or provider choice made with this skill is itself a decision record, so the skill proposes recording it with [`/tsh-core:managing-decision-records`](/docs/plugins/tsh-core/skills/managing-decision-records). |
| **Driver first** | The driver is named before any multi-cloud topology is proposed: disaster recovery, compliance or data sovereignty, best-of-breed capability, or cost. No driver means single-cloud. |
| **Six patterns** | Single provider with DR, best-of-breed (polycloud), geographic distribution, cloud-agnostic abstraction, cloud bursting, and data mesh or analytics on the best provider. A decision tree maps the driver to a pattern. |
| **Service mapping** | A matrix of equivalent services across AWS, Azure and GCP for compute, storage, database, networking, security and identity, messaging, developer tools, AI and ML, analytics, monitoring, and pricing models. Current generation and regional availability are verified with `context7` before committing to a service. |
| **Abstraction level** | Kubernetes, Terraform, both or neither, with the cost stated. Cloud-agnostic building blocks (Kubernetes, PostgreSQL or MySQL, Kafka, Redis, S3-compatible APIs, Prometheus and Grafana, Istio or Linkerd, Terraform) are taken only when portability is a requirement, because they give up managed-service capability and add operational work. |
| **Cross-cutting concerns** | Federated identity to one source of truth, private connectivity or VPN between clouds, observability through OpenTelemetry to a neutral backend, centralised posture and policy tooling, and cost management using the Core 5 tags from `optimizing-cloud-cost`. |
| **Rules** | Every design is costed including cross-cloud data transfer. Portability is presented as a trade-off with its price. Service availability is verified in the specific target regions. Cross-cloud failover is never designed without saying how it is tested, and a workload is never duplicated into a second cloud without a stated reason for that workload. |

## How it works

1. **Establish the driver**, tied to a requirement.
2. **Select the pattern** using the decision framework.
3. **Map services** with the service comparison, verifying tiers and regional availability.
4. **Choose the abstraction level** and state what it costs.
5. **Design cross-cloud networking**: VPN or interconnect, address planning, and the egress cost that follows from where data lives relative to where it is processed.
6. **Federate identity** to a single source of truth.
7. **Unify observability** so one query answers a question about either cloud.
8. **Plan the phases**: assessment, a pilot with one workload, incremental migration with a dual-run period, then optimization.
9. **Define and schedule failover tests.**

## References

| Reference | Load when |
| :-- | :-- |
| `decision-framework.md` | Choosing between topologies, or handling identity, networking, observability and cost across clouds. Read before proposing any topology. |
| `patterns.md` | A pattern has been selected and needs designing. Gives each of the six patterns in full: DR, best-of-breed, geographic distribution, cloud-agnostic abstraction, cloud bursting and data mesh. |
| `service-comparison.md` | Mapping a service to its equivalent in another provider. |

## Related skills

- [Implementing Terraform Modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules) - the provisioning layer for any of these patterns.
- [Optimizing Cloud Cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost) - pricing models and cross-cloud cost tracking.
- [Deploying to Kubernetes](/docs/plugins/tsh-platform-engineering/skills/deploying-to-kubernetes) - the agnostic compute layer in practice.

## Source

- [`plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture/SKILL.md)
- [`plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture/references)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
