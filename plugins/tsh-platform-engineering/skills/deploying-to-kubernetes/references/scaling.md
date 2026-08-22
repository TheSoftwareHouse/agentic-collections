# Scaling Kubernetes workloads

## Which mechanism

| Driver | Mechanism |
| :-- | :-- |
| CPU utilization | HPA |
| Memory utilization | HPA |
| Queue depth, request rate, any custom metric | HPA with the Prometheus adapter |
| Message queues, external events, scale-to-zero | KEDA |
| Right-sizing requests and limits themselves | VPA |

HPA changes the number of pods; VPA changes the size of each pod. **Do not point both
at the same workload on CPU or memory** — they fight, and the result is oscillation.
VPA in recommendation-only mode alongside HPA is safe and genuinely useful for
setting requests.

## HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
```

Details that decide whether it works:

- **HPA requires resource requests.** Utilization is a percentage *of the request*, so
  a container with no CPU request cannot be scaled on CPU at all.
- **`minReplicas: 2` minimum** for anything serving traffic — scaling from one replica
  means a cold start is on the critical path.
- **`stabilizationWindowSeconds` on scaleDown** prevents flapping. The default scale-up
  is deliberately fast and scale-down deliberately slow; keep that asymmetry.
- **70% CPU** is a reasonable target. Higher leaves no headroom for the scale-up delay
  itself; much lower wastes capacity.
- **The HPA target must not be managed by a fixed `replicas` value** in the same
  manifest — a GitOps controller will reconcile the replica count back and undo every
  scaling decision. Omit `replicas` from a Deployment that an HPA owns.

## KEDA

For event-driven work, and the only option that scales to zero. Scalers exist for SQS,
Pub/Sub, Kafka, RabbitMQ, Azure Service Bus, cron, and many more.

Use it when the signal that should drive scaling is not a resource metric — queue
depth is the canonical case, since CPU on a consumer says nothing about backlog.

Scale-to-zero has a cold-start cost on the first message. Acceptable for batch, rarely
for anything user-facing.

## VPA

Three modes: `Off` (recommendations only), `Initial` (applies at pod creation), and
`Auto` (evicts pods to resize them).

`Off` is where most projects should stay: read the recommendations and set requests
deliberately in the manifest. `Auto` evicting pods to resize them surprises people,
and interacts badly with PDBs and with HPA.

## Cluster-level

Pod autoscaling only helps if nodes exist. Pair workload scaling with a cluster
autoscaler or Karpenter, and check that `maxReplicas` is actually schedulable — an HPA
that scales to 10 pods on a cluster with room for 4 just produces six `Pending` pods
and no capacity.
