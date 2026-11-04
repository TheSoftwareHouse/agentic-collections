---
title: Implementing Observability
sidebar_label: Implementing Observability
sidebar_position: 4
description: Implements metrics, logs, traces and alerting to a standard that supports an on-call rotation - stack choice, RED and USE metrics, SLOs with error budgets, symptom-based alerts with runbooks, and structured logging.
sources:
  - plugins/tsh-platform-engineering/skills/implementing-observability/
  - plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md
sources_hash: "920c622e3001f869087464d4ed412a38ddc4fe13790d9043253ad31b4e3a5681"
---

# Implementing Observability

**Plugin:** [TSH Platform Engineering](/docs/plugins/tsh-platform-engineering/)  
**Invoke:** `/tsh-platform-engineering:implementing-observability`, or loaded automatically when a request matches its description  
**Used by:** [devops-engineer](/docs/plugins/tsh-platform-engineering/agents/devops-engineer)

Implements metrics, logs, traces and alerting. The skill's test is whether someone woken at 3am can tell what is broken and what to do about it; dashboards nobody opens and alerts nobody can act on both fail it while looking like coverage.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | Reads the shared context file; section 5 detects the stack already in place. The existing stack is extended, since a second metrics system means two places to look during an incident. |
| **Three pillars** | Metrics (is it broken, and how badly), logs (what happened in this one case) and traces (where in the request path it went wrong). The value comes from joining them through a shared identifier. |
| **Stack choice** | Only where nothing exists. Prometheus with Grafana, CloudWatch, Datadog or New Relic for metrics. Loki, CloudWatch Logs, ELK, Datadog Logs or Splunk for logs. Tempo, Jaeger, X-Ray or Datadog APM for traces. Instrument with OpenTelemetry whichever backend is chosen, so the backend stays replaceable. |
| **Kubernetes topology** | Applications export over OTLP to an OpenTelemetry Collector, which fans out to Prometheus, Loki and Tempo or Jaeger, with Grafana on top. The collector runs as a DaemonSet, a Deployment gateway, or both. |
| **Metrics** | RED (rate, errors, duration) for services and USE (utilization, saturation, errors) for resources. Latency is a histogram, never an average. Metric labels use bounded dimensions only, because unbounded labels such as user IDs or raw URL paths take a metrics backend down. |
| **SLOs** | SLIs measured from what users experience, a target below 100%, an explicit error budget and an agreed error-budget policy (healthy, low, exhausted) published with the SLO. An untouched budget is reported as over-investment in reliability. |
| **Alerting** | Alerts fire on user-visible symptoms. Every alert has an owner, a severity and a runbook link. Severities are Critical (page on-call), Warning (hours) and Info (business hours), with different routing. Error-budget burn alerts use a fast window and a slow window. Prometheus rules use `for:`, a ratio and `runbook_url`. |
| **Runbooks** | Written together with the alert: what it means, what users experience, first checks, known causes, escalation, and how to verify recovery. |
| **Structured logging** | JSON with `timestamp`, `level`, `service`, `trace_id` and a stable `message`, with variable data in fields. Trace context is injected through the OpenTelemetry logging integration. Levels are runtime-adjustable. |
| **Never logged** | Passwords, tokens, API keys, session identifiers, full request or response bodies on personal or payment data, card numbers, national identifiers, health data and authorization headers. Redaction at the collector is a second layer. |
| **Retention and cost** | A retention policy per log stream and metric series. Cost controls set up front: metric cardinality, log exclusions at the collector, trace sampling (head or tail) and retention per signal. |

## How it works

1. **Discover** what already exists from the shared context file, and extend it.
2. **Choose the stack** where nothing exists.
3. **Instrument** with the OpenTelemetry SDK or auto-instrumentation, then add manual spans for the business operations that matter.
4. **Configure collection**: collectors, exporters, storage and retention.
5. **Define SLOs**: SLIs, targets and error budgets.
6. **Write alerts** from the SLOs, each with a runbook.
7. **Build dashboards**, one per service, answering "is this healthy" without scrolling.
8. **Write the runbooks.** An alert delivered without its runbook is unfinished work.

## References

| Reference | Load when |
| :-- | :-- |
| `choosing-a-stack.md` | No stack exists, or one is being replaced or extended. |
| `metrics-and-slos.md` | Deciding what to measure, or defining SLOs. |
| `alerting.md` | Writing or tuning alert rules. It is read before writing any alert rule, and it also lists what to look for when reviewing an existing setup with alert fatigue. |
| `structured-logging.md` | Implementing or fixing logging. |

## Related skills

- [Deploying to Kubernetes](/docs/plugins/tsh-platform-engineering/skills/deploying-to-kubernetes) - cluster-level collection and workload metrics.
- [Implementing CI/CD Pipelines](/docs/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines) - deployment markers and pipeline visibility.
- [Managing Secrets](/docs/plugins/tsh-platform-engineering/skills/managing-secrets) - credentials for observability backends.
- [Optimizing Cloud Cost](/docs/plugins/tsh-platform-engineering/skills/optimizing-cloud-cost) - log ingestion and metric cardinality are real line items.

## Source

- [`plugins/tsh-platform-engineering/skills/implementing-observability/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/skills/implementing-observability/SKILL.md)
- [`plugins/tsh-platform-engineering/skills/implementing-observability/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-platform-engineering/skills/implementing-observability/references)
- [`plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-platform-engineering/shared/discovering-infrastructure-context.md)
