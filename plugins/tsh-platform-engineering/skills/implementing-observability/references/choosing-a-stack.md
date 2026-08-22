# Choosing an observability stack

Extend what exists. These tables are for a greenfield choice or a deliberate
replacement.

## Metrics

| Scenario | Choice |
| :-- | :-- |
| Kubernetes-native, cost-sensitive | Prometheus with Grafana |
| AWS-native, simple | CloudWatch Metrics |
| Multi-cloud, enterprise support required | Datadog or New Relic |
| OpenTelemetry-first | Prometheus with an OTLP receiver |

## Logging

| Scenario | Choice |
| :-- | :-- |
| Kubernetes, cost-sensitive | Loki with Grafana |
| AWS-native | CloudWatch Logs |
| High volume, complex queries | Elasticsearch / ELK |
| Multi-cloud, managed | Datadog Logs or Splunk |

Logging is usually the largest observability cost, and ingestion drives it more than
retention. Exclusions at the collector are the highest-leverage control.

## Tracing

| Scenario | Choice |
| :-- | :-- |
| Kubernetes, open source | Tempo or Jaeger |
| AWS-native | X-Ray |
| Multi-cloud, correlated with metrics and logs | Datadog APM |
| Backend not yet decided | OpenTelemetry, exporting anywhere |

## Instrument with OpenTelemetry regardless

Whatever the backend, instrument with OpenTelemetry. It is the one decision that keeps
the backend replaceable — vendor SDKs make a later migration a re-instrumentation
project across every service.

Auto-instrumentation gets useful traces with no code change and is the right starting
point. Add manual spans afterwards for the business operations that matter, which are
the ones auto-instrumentation cannot name.

## Kubernetes topology

```text
┌─────────────────────────────────────────────────────┐
│                   Applications                      │
│  (OpenTelemetry SDK or auto-instrumentation)         │
└──────────────────────┬──────────────────────────────┘
                       │ OTLP
                       ▼
┌─────────────────────────────────────────────────────┐
│            OpenTelemetry Collector                  │
│  (receive, process, filter, export)                 │
└───────┬─────────────────┬─────────────────┬─────────┘
        │                 │                 │
        ▼                 ▼                 ▼
   Prometheus          Loki             Tempo/Jaeger
   (metrics)          (logs)            (traces)
        │                 │                 │
        └────────────────┬┴─────────────────┘
                         ▼
                      Grafana
```

The collector is the part worth insisting on. With it, sampling, redaction, relabelling
and backend changes are config in one place. Without it, every one of those is a
redeploy of every service.

Run it as a DaemonSet for node-local collection, or a Deployment for a gateway that
handles tail sampling and egress to a vendor. Both together is common: agent per node,
gateway per cluster.

## Cost controls to set up front

- **Metric cardinality.** A label with unbounded values — user ID, request ID, full
  URL path — multiplies series count without limit. This is the usual cause of a
  Prometheus falling over.
- **Log exclusions at the collector**, dropping health-check and readiness log lines
  before ingestion.
- **Trace sampling.** Head sampling is cheap and simple; tail sampling keeps the
  interesting traces (errors, slow requests) and needs a gateway collector.
- **Retention per signal**, not one global setting. Traces rarely need more than days,
  metrics often need a year of downsampled history.
