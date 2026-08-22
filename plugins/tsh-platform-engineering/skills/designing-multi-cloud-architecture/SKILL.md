---
name: designing-multi-cloud-architecture
description: "Selects cloud services and a multi-cloud topology using an explicit decision framework: which of the six multi-cloud patterns fits the actual driver, how AWS, Azure and GCP services map onto each other, where a cloud-agnostic abstraction pays for itself and where it costs more than lock-in, and how to phase a migration. Use when choosing cloud services for a workload, planning a cross-cloud or DR topology, or evaluating a move between providers."
when_to_use: "Trigger on: selecting a cloud provider or service for a workload, 'what's the AWS equivalent of' a GCP or Azure service, designing disaster recovery in a second cloud, avoiding or evaluating vendor lock-in, data-sovereignty-driven regional topology, planning a migration between providers, cloud bursting, or deciding whether to abstract over providers with Kubernetes and Terraform."
---

# Designing Multi-Cloud Architecture

Start from the driver, not the pattern. Multi-cloud has a real operational cost —
two control planes, two skill sets, egress between them — so a topology that no
stated requirement forces is a liability rather than a hedge.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first. A
provider already in production, or a decision record in `docs/decisions/`, settles
the question — do not re-open a recorded provider choice as part of an unrelated
change.

Conversely, a topology or provider choice made here **is** a decision record: it is
expensive to reverse, and the reasoning is what a future reader needs. Propose
recording it with `/tsh-core:managing-decision-records` once the choice is made.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Name the driver — disaster recovery, compliance or data sovereignty, best-of-breed capability, or cost — before proposing a multi-cloud topology. No driver means single-cloud. |
| MUST | Cost every design, including cross-cloud data transfer. Egress between providers is the line item that turns a sensible-looking topology into an expensive one. |
| MUST | Present portability as a trade-off with its price, never as a free property. Abstraction costs managed-service capability and engineering time. |
| MUST | Verify service availability in the specific target regions before designing around a service — regional availability differs and is a common late-stage surprise. |
| NEVER | Design cross-cloud failover without saying how it is tested. Untested failover is documentation, not resilience. |
| NEVER | Duplicate a workload into a second cloud without a stated reason for that specific workload. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Decision framework](./references/decision-framework.md) | Choosing between topologies, or handling identity, networking, observability and cost across clouds | Pattern selection criteria, cross-cutting concerns every pattern shares |
| [Multi-cloud patterns](./references/patterns.md) | A pattern has been selected and needs designing | Six patterns in full — DR, best-of-breed, geographic, agnostic abstraction, bursting, data mesh |
| [Service comparison](./references/service-comparison.md) | Mapping a service to its equivalent in another provider | Compute, storage, database, networking, security, messaging, AI/ML, analytics, observability equivalents |

Read [decision-framework.md](./references/decision-framework.md) before proposing any
topology — selecting a pattern by familiarity is the failure this skill exists to
prevent.

## The six patterns

| Pattern | Driver it serves |
| :-- | :-- |
| Single provider with DR | Recovery objectives a single provider cannot meet |
| Best-of-breed (polycloud) | A capability genuinely better on another provider |
| Geographic distribution | Latency, or data sovereignty |
| Cloud-agnostic abstraction | Portability as a hard requirement, usually contractual |
| Cloud bursting | Sustained baseline plus rare, large peaks |
| Data mesh / analytics on best provider | Analytics or ML capability, with a bounded data flow |

Full designs in [patterns.md](./references/patterns.md).

## Service selection

Common equivalents, with the full matrix in
[service-comparison.md](./references/service-comparison.md):

| Purpose | AWS | Azure | GCP |
| :-- | :-- | :-- | :-- |
| IaaS VMs | EC2 | Virtual Machines | Compute Engine |
| Managed containers | Fargate / ECS | Container Apps | Cloud Run |
| Kubernetes | EKS | AKS | GKE |
| Serverless functions | Lambda | Functions | Cloud Functions |
| Object storage | S3 | Blob Storage | Cloud Storage |
| Managed SQL | RDS | SQL Database | Cloud SQL |
| NoSQL | DynamoDB | Cosmos DB | Firestore |
| Cache | ElastiCache | Cache for Redis | Memorystore |

Verify the current generation and regional availability with `context7` before
committing to any specific service or tier.

## Cloud-agnostic building blocks

Where portability is the actual requirement, these carry across providers: Kubernetes
for compute, PostgreSQL or MySQL for relational data, Kafka for streaming, Redis for
cache, S3-compatible APIs for objects, Prometheus and Grafana for observability,
Istio or Linkerd for service mesh, Terraform for provisioning.

The trade-off is explicit: portable choices give up managed-service capability and
add operational work. Take it only when portability is required, not by default.

## Procedure

1. **Establish the driver.** DR, compliance, capability, or cost — named, and tied to
   a requirement. No driver → single cloud, and say so.
2. **Select the pattern** using [decision-framework.md](./references/decision-framework.md).
3. **Map services** with [service-comparison.md](./references/service-comparison.md),
   verifying current tiers and regional availability.
4. **Choose the abstraction level** — Kubernetes, Terraform, both, or neither — and
   state what it costs.
5. **Design cross-cloud networking** — VPN or interconnect, address planning, and the
   egress cost that follows from where data lives relative to where it is processed.
6. **Federate identity** to a single source of truth. Two independent identity systems
   is the failure mode that outlives the project.
7. **Unify observability** so one query answers a question about either cloud.
8. **Plan the phases** — assessment, pilot with one workload, incremental migration
   with a dual-run period, then optimization.
9. **Define and schedule failover tests.**

## Checklist

- [ ] Multi-cloud driver documented, per workload
- [ ] Pattern selected against the framework, not by familiarity
- [ ] Service equivalents mapped and regional availability verified
- [ ] Abstraction level chosen, with its cost stated
- [ ] Cross-cloud networking designed and secured
- [ ] Identity federated to one source of truth
- [ ] Unified monitoring and logging
- [ ] Cost allocation across providers, including egress
- [ ] Failover procedure documented and its test scheduled
- [ ] Team competent in every provider in the design

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| Adopt multi-cloud as a hedge with no driver | Name the requirement, or stay single-cloud |
| Use proprietary services where portability is required | Choose agnostic building blocks, knowingly |
| Duplicate everything across clouds | Be deliberate about what runs where |
| Manage each cloud with its own tooling | One IaC and one observability surface |
| Ignore inter-cloud transfer cost | Design to keep processing next to data |
| Claim failover works because it is configured | Test it on a schedule |

## Related skills in this plugin

- [Implementing Terraform modules](../implementing-terraform-modules/SKILL.md) — the
  provisioning layer for any of these patterns
- [Optimizing cloud cost](../optimizing-cloud-cost/SKILL.md) — pricing models and
  cross-cloud cost tracking
- [Deploying to Kubernetes](../deploying-to-kubernetes/SKILL.md) — the agnostic
  compute layer in practice
