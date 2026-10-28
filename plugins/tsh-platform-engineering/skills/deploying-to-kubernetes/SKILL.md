---
name: deploying-to-kubernetes
description: "Configures Kubernetes workloads to a production standard: choosing between Deployment, StatefulSet, DaemonSet and Job, resource requests and limits and the QoS class they produce, readiness/liveness/startup probes, PodDisruptionBudgets and anti-affinity, HPA/KEDA/VPA scaling, Helm chart and Kustomize overlay structure, ingress, and non-root security contexts. Use when deploying an application to a cluster, writing or reviewing manifests or charts, or adding scaling and resilience to an existing workload."
when_to_use: "Trigger on: writing or changing a Deployment, StatefulSet, DaemonSet, Job or CronJob, creating or modifying a Helm chart or Kustomize overlay, setting resource requests and limits, configuring probes, adding autoscaling with HPA or KEDA, PodDisruptionBudget or anti-affinity for high availability, ingress and TLS, pod security context hardening, CrashLoopBackOff or OOMKilled or eviction troubleshooting, or reviewing Kubernetes manifests before merge."
---

# Deploying to Kubernetes

The defaults Kubernetes gives you are not production defaults. A manifest with no
requests, no probes and no disruption budget will deploy successfully and then behave
badly under exactly the conditions you deployed it for.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first —
sections 2, 3 and 5 identify whether the project uses raw manifests, Helm or
Kustomize, the API versions its cluster serves, and whether a GitOps controller owns
the cluster. **Match the project's existing packaging.** Adding a Helm chart to a
Kustomize repository is a finding, not a delivery.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Set resource requests on every container. Without them the scheduler places blind and the pod lands in BestEffort QoS, first to be evicted. |
| MUST | Configure a readiness probe on anything that serves traffic. Without one, traffic reaches a pod that is not ready and the deploy looks successful while requests fail. |
| MUST | Pin image tags to a version or digest. `latest` makes the running version unknowable and a rollback meaningless. |
| MUST | Run as non-root with `allowPrivilegeEscalation: false` and dropped capabilities in production. |
| MUST | Give production workloads at least two replicas and a PodDisruptionBudget, so a node drain cannot take the service down. |
| MUST | Validate before delivering — `kubectl apply --dry-run=server`, and `helm template` for charts. Client-side dry-run does not catch admission failures. |
| NEVER | Put secret values in a ConfigMap, a manifest, or a committed values file. |
| NEVER | `kubectl apply` directly against a cluster a GitOps controller owns — the controller reverts it and the drift hides the real change. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Workload configuration](./references/workload-configuration.md) | Writing or reviewing any workload manifest | Resources and QoS classes, all three probe types, PDB, anti-affinity, security context |
| [Scaling](./references/scaling.md) | The workload needs to scale, or scales badly | HPA with behavior tuning, KEDA for event-driven, VPA, and which to use |
| [Helm and Kustomize](./references/helm-and-kustomize.md) | Packaging a workload, or changing a chart or overlay | Chart layout, values conventions, environment overrides, overlay structure |
| [Ingress and networking](./references/ingress-and-networking.md) | Exposing a service outside the cluster | Controller choice, ingress with TLS, network policies |

Read [workload-configuration.md](./references/workload-configuration.md) before
writing any manifest — requests, probes and QoS are where production behavior is
decided.

## Workload type

| Type | Use for |
| :-- | :-- |
| Deployment | Stateless apps, web servers, APIs |
| StatefulSet | Databases and anything needing stable identity or ordered startup |
| DaemonSet | Node-level agents — log shippers, metrics agents |
| Job | One-off tasks and batch processing |
| CronJob | Scheduled recurring tasks |

Reach for a StatefulSet only when stable network identity or per-replica storage is
genuinely required. A Deployment with a persistent volume covers more cases than
people expect, and is far simpler to operate.

## Procedure

1. **Discover** — the shared context file. Establish packaging, cluster API versions,
   and whether GitOps owns the cluster.
2. **Choose the workload type** from the table above.
3. **Configure resources** — requests from profiling or measured usage where
   available; state plainly when a value is an estimate, and set the request:limit
   ratio deliberately. See
   [workload-configuration.md](./references/workload-configuration.md).
4. **Add probes** — readiness always; startup for slow starters; liveness checking the
   app itself, never its dependencies.
5. **Add resilience** — replicas, PDB, anti-affinity or topology spread.
6. **Add scaling** if the load varies — see [scaling.md](./references/scaling.md).
7. **Harden** — security context, and network policies where the cluster enforces them.
8. **Package** to the project's convention — see
   [helm-and-kustomize.md](./references/helm-and-kustomize.md).
9. **Validate** — `kubectl apply --dry-run=server`, `helm template`, and `kubeconform`
   where the project has it (`kubeval` is archived).

## Checklist

- [ ] Resource requests set; limits set for memory
- [ ] Readiness probe configured; liveness and startup where appropriate
- [ ] At least two replicas in production
- [ ] PodDisruptionBudget for production workloads
- [ ] Pod anti-affinity or topology spread constraints
- [ ] HPA or KEDA where load varies
- [ ] Non-root security context with dropped capabilities
- [ ] Image tag pinned; pull policy appropriate
- [ ] Labels consistent — `app`, `version`, `environment`
- [ ] Namespace isolation per environment
- [ ] Secrets referenced from a secret store, never inline
- [ ] Manifests validated server-side

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| `latest` image tag | Pin a version or digest |
| No resource requests | Always set requests |
| Single replica in production | Two or more, with a PDB |
| Run as root | Non-root, minimal capabilities |
| No readiness probe | Probe, so traffic arrives only when ready |
| `kubectl apply` into a GitOps cluster | Commit; let the controller reconcile |
| Values hardcoded in manifests | Helm values or Kustomize overlays |
| Liveness probe that checks the database | Liveness checks the process; readiness checks dependencies |
| CPU limits set reflexively | Set them knowingly — throttling looks like a latency bug |

## Related skills in this plugin

- [Implementing observability](../implementing-observability/SKILL.md) — cluster and
  workload monitoring
- [Implementing CI/CD pipelines](../implementing-ci-cd-pipelines/SKILL.md) — how the
  manifests get deployed
- [Managing secrets](../managing-secrets/SKILL.md) — in-cluster secret delivery
- [Implementing Terraform modules](../implementing-terraform-modules/SKILL.md) —
  provisioning the cluster itself
