---
title: Deploying to Kubernetes
sidebar_label: Deploying to Kubernetes
sidebar_position: 3
description: Configures Kubernetes workloads to a production standard - workload type, requests and limits, probes, PodDisruptionBudgets, scaling, Helm and Kustomize, ingress, and non-root security contexts.
sources:
  - plugins/tsh-platform-engineering/skills/deploying-to-kubernetes/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
sources_hash: "6051e3fb7444239b5691f2f2e2845a3a20c375f5db329e99333c4f66b4ee1e30"
---

# Deploying to Kubernetes

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:deploying-to-kubernetes`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer), [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor)

Configures Kubernetes workloads to a production standard. The premise is that Kubernetes defaults are not production defaults: a manifest with no requests, no probes and no disruption budget deploys successfully and then behaves badly under the conditions it was deployed for.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file (sections 2, 3 and 5): raw manifests, Helm or Kustomize, the API versions the cluster serves, and whether a GitOps controller owns the cluster. The project's existing packaging is matched; adding a Helm chart to a Kustomize repository is a finding. |
| **Workload type** | Deployment for stateless apps, StatefulSet for stable identity or ordered startup, DaemonSet for node-level agents, Job for one-off tasks, CronJob for scheduled ones. A StatefulSet only when stable network identity or per-replica storage is genuinely required. |
| **Resources and QoS** | Requests on every container, a memory limit always, and CPU limits as a deliberate decision because throttling shows up as tail latency. Production workloads are Guaranteed or Burstable, never BestEffort. A 1:2 request-to-limit ratio is a reasonable starting point for memory. |
| **Probes** | Readiness on anything that serves traffic and may check dependencies. Liveness checks the process only, never its dependencies. Startup probes for slow starters. |
| **Resilience** | At least two replicas and a PodDisruptionBudget in production. `maxUnavailable: 1` is the safe default for three or more replicas, and `minAvailable` equal to the replica count blocks drains. Preferred pod anti-affinity or topology spread constraints, not required rules that can leave pods `Pending`. |
| **Scaling** | HPA for CPU or memory, and for custom metrics through the Prometheus adapter. KEDA for message queues and external events and the only option that scales to zero. VPA for right-sizing requests, usually in `Off` mode. HPA and VPA are not pointed at the same workload on CPU or memory. |
| **Packaging** | Helm chart layout and `values.yaml` conventions (no committed image tag, name helpers, safe defaults), or Kustomize `base/` and `overlays/`. Whichever the project already uses; Helm for distribution to other teams, Kustomize for an internal app with a few environments. |
| **Ingress and networking** | Controller choice (ingress-nginx, AWS Load Balancer Controller, Traefik, a Gateway API implementation, or a mesh gateway), TLS with cert-manager, `ingressClassName`, controller-specific annotations, default-deny network policies that need an enforcing CNI, and ClusterIP as the default service type. |
| **Security context** | Non-root, `allowPrivilegeEscalation: false`, dropped capabilities, `seccompProfile` set to `RuntimeDefault`, and `readOnlyRootFilesystem: true` with an `emptyDir` mount where the app writes. |
| **Rules** | Requests on every container, a readiness probe, pinned image tags, non-root in production, two replicas and a PDB in production, and server-side validation. Never put secret values in a ConfigMap, manifest or committed values file, and never `kubectl apply` directly against a cluster a GitOps controller owns. |

## How it works

1. **Discover** packaging, cluster API versions and whether GitOps owns the cluster, from the shared context file.
2. **Choose the workload type.**
3. **Configure resources.** Requests come from measured usage where available, an estimate is labelled as one, and the request-to-limit ratio is set deliberately.
4. **Add probes**: readiness always, startup for slow starters, liveness checking the app itself.
5. **Add resilience**: replicas, PDB, anti-affinity or topology spread.
6. **Add scaling** if the load varies.
7. **Harden** with a security context, and network policies where the cluster enforces them.
8. **Package** to the project's convention.
9. **Validate** with `kubectl apply --dry-run=server` and `helm template`, and `kubeconform` where the project has it. Client-side dry-run does not catch admission failures.

## References

| Reference | Load when |
| :-- | :-- |
| `workload-configuration.md` | Writing or reviewing any workload manifest. Read before writing one: resources, QoS, all three probe types, PDB, anti-affinity and security context. |
| `scaling.md` | The workload needs to scale, or scales badly. HPA with behavior tuning, KEDA, VPA, and a note that pod autoscaling only helps if nodes exist. |
| `helm-and-kustomize.md` | Packaging a workload, or changing a chart or overlay. |
| `ingress-and-networking.md` | Exposing a service outside the cluster. |

## Related skills

- [Implementing Observability](/docs/plugins/tsh-platform-engineering/skills/implementing-observability) - cluster and workload monitoring.
- [Implementing CI/CD Pipelines](/docs/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines) - how the manifests get deployed.
- [Managing Secrets](/docs/plugins/tsh-platform-engineering/skills/managing-secrets) - in-cluster secret delivery.
- [Implementing Terraform Modules](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules) - provisioning the cluster itself.

## Source

- [`plugins/tsh-platform-engineering/skills/deploying-to-kubernetes/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/deploying-to-kubernetes/SKILL.md)
- [`plugins/tsh-platform-engineering/skills/deploying-to-kubernetes/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-platform-engineering/skills/deploying-to-kubernetes/references)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
