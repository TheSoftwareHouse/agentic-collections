# Workload configuration

Requests, probes and disruption budgets are where a manifest stops being a
description and starts being an operational contract.

## Resources and QoS

```yaml
resources:
  requests:    # the scheduler places on these
    memory: "256Mi"
    cpu: "100m"
  limits:      # the kubelet enforces these
    memory: "512Mi"
    cpu: "500m"
```

- **Always set requests.** They are what scheduling uses; without them the scheduler
  cannot reason about the pod and it lands in the lowest QoS class.
- **Always set a memory limit.** Memory is incompressible — a container without a limit
  can take the whole node down with it. Exceeding the limit kills only that container.
- **CPU limits are a real decision, not a default.** CPU is compressible, so a limit
  throttles rather than kills. Throttling presents as unexplained tail latency, which
  is much harder to diagnose than a slow pod. Set one when a noisy neighbour must be
  contained; leave it off when latency matters more than isolation.
- **1:2 request-to-limit** is a reasonable starting ratio for memory.

### QoS classes

| Class | Condition | Eviction order |
| :-- | :-- | :-- |
| Guaranteed | requests equal limits, every container | Last |
| Burstable | requests below limits | Middle |
| BestEffort | no requests or limits | First |

Production workloads are Guaranteed or Burstable, never BestEffort. Guaranteed for
anything whose eviction causes an incident; Burstable for the rest.

## Probes

```yaml
livenessProbe:      # failing restarts the container
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:     # failing removes the pod from the Service
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3

startupProbe:       # holds liveness off until startup finishes
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

The distinction that matters:

- **Readiness** answers "should traffic come here?" — so it *may* check dependencies.
  A pod that cannot reach its database should leave the load-balancer pool.
- **Liveness** answers "is this process wedged?" — so it must **not** check
  dependencies. A liveness probe that fails on a database blip restarts every replica
  simultaneously, turning a dependency wobble into a full outage.
- **Startup** exists so slow-booting apps don't need a long `initialDelaySeconds` on
  liveness, which would otherwise delay detection of a genuine hang for the whole
  lifetime of the pod.

## PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2        # or maxUnavailable: 1
  selector:
    matchLabels:
      app: api
```

Required for production. Without it, a node drain — cluster upgrade, autoscaler
consolidation, spot reclaim — can evict every replica at once.

`minAvailable` equal to the replica count blocks drains entirely and will stall a
cluster upgrade. Leave headroom: `maxUnavailable: 1` is the safe default for a
deployment of three or more.

## Spreading replicas

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: api
          topologyKey: kubernetes.io/hostname
```

`preferred` rather than `required`: a required rule that cannot be satisfied leaves
pods `Pending` forever, which is worse than co-located replicas. Use
`topology.kubernetes.io/zone` as the key for zone-level spread, and prefer
`topologySpreadConstraints` on newer clusters for finer control.

## Security context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
```

`readOnlyRootFilesystem: true` requires an `emptyDir` mount anywhere the app writes —
usually `/tmp`. Add the mount rather than dropping the setting.
