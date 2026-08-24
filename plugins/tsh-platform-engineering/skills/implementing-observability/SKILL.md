---
name: implementing-observability
description: "Implements metrics, logs, traces and alerting to a standard that supports an on-call rotation: choosing a stack (Prometheus/Grafana, Loki, Tempo or Jaeger, CloudWatch, Datadog, OpenTelemetry), RED and USE metrics, SLOs with error budgets, alerts that fire on user-visible symptoms and link to runbooks, and structured logging with trace correlation. Use when adding monitoring to a service, defining SLOs, writing alert rules, or fixing an alerting setup that pages too often."
when_to_use: "Trigger on: adding monitoring, metrics, logging or tracing to a service or cluster, choosing between Prometheus, CloudWatch, Datadog or OpenTelemetry, defining SLOs, SLIs or error budgets, writing or tuning Prometheus alert rules, alert fatigue and noisy pages, building a Grafana dashboard, distributed tracing across services, structured or JSON logging and trace-ID propagation, log retention and cost, or an incident that showed the team could not see what happened."
---

# Implementing Observability

The test of an observability setup is whether someone woken at 3am can tell what is
broken and what to do about it. Dashboards nobody opens and alerts nobody can act on
both fail that test while looking like coverage.

## Applicability and Precedence

Read `${CLAUDE_PLUGIN_ROOT}/shared/discovering-infrastructure-context.md` first —
section 5 detects the stack already in place. **Extend the existing stack.** A second
metrics system means two places to look during an incident, which is worse than one
imperfect place.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Alert on user-visible symptoms, not on causes. A CPU threshold that pages nobody about a working service is how alert fatigue starts, and fatigue is what makes the real page get ignored. |
| MUST | Give every alert an owner, a severity, and a runbook link. An alert with no documented response is not actionable, and unactionable alerts get muted. |
| MUST | Propagate trace context across every service boundary. A trace that stops at the first hop cannot answer the question traces exist for. |
| MUST | Exclude PII, secrets, tokens and full request bodies from logs. Logs are widely readable, retained, and shipped to third parties. |
| MUST | Set a retention policy on every log stream and metric series. Unbounded retention is an unbounded bill and, for personal data, a compliance problem. |
| MUST | Emit structured logs with a consistent field set. Free-text logs cannot be queried when it matters. |
| NEVER | Define an SLO without an error budget, or set a target of 100%. A budget nobody can spend is a target nobody can make decisions against. |
| NEVER | Leave debug-level logging on in production as a default. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Choosing a stack](./references/choosing-a-stack.md) | No stack exists, or one is being replaced or extended | Metrics, logging and tracing options by scenario; the Kubernetes OpenTelemetry topology |
| [Metrics and SLOs](./references/metrics-and-slos.md) | Deciding what to measure, or defining SLOs | RED and USE methods, SLI queries, SLO and error-budget definition |
| [Alerting](./references/alerting.md) | Writing or tuning alert rules | Severity levels, alert quality rules, Prometheus rule template, runbook expectations |
| [Structured logging](./references/structured-logging.md) | Implementing or fixing logging | JSON format, required fields, trace correlation, what must never be logged |

Read [alerting.md](./references/alerting.md) before writing any alert rule — the
symptom-versus-cause distinction is the whole difference between a useful rotation and
an ignored one.

## The three pillars

| Pillar | Answers | Common tools |
| :-- | :-- | :-- |
| Metrics | Is it broken, and how badly? | Prometheus, CloudWatch, Datadog, Grafana |
| Logs | What exactly happened in this one case? | Loki, ELK, CloudWatch Logs, Splunk |
| Traces | Where in the request path did it go wrong? | Tempo, Jaeger, X-Ray, Datadog APM |

They are complementary, and the value comes from correlation: an alert fires on a
metric, the trace shows which hop is slow, the logs for that `trace_id` say why. A
setup where the three cannot be joined by a shared identifier is three setups.

## Procedure

1. **Discover** — the shared context file. Identify what already exists and extend it.
2. **Choose the stack** where nothing exists — see
   [choosing-a-stack.md](./references/choosing-a-stack.md).
3. **Instrument** — OpenTelemetry SDK or auto-instrumentation, so the backend stays
   replaceable.
4. **Configure collection** — collectors, exporters, storage, and retention.
5. **Define SLOs** — SLIs, targets, error budgets. See
   [metrics-and-slos.md](./references/metrics-and-slos.md).
6. **Write alerts** from the SLOs, each with a runbook. See
   [alerting.md](./references/alerting.md).
7. **Build dashboards** — one per service, answering "is this healthy" without
   scrolling.
8. **Write the runbooks.** An alert delivered without its runbook is unfinished work.

## Checklist

- [ ] Services emit metrics, logs and traces
- [ ] Trace IDs propagated across every service boundary
- [ ] Logs structured, with a consistent field set
- [ ] Logs, metrics and traces correlatable by a shared identifier
- [ ] SLOs defined with error budgets
- [ ] Every alert actionable, owned, and linked to a runbook
- [ ] Dashboards show service health at a glance
- [ ] Retention configured for logs and metrics
- [ ] PII and secrets excluded from logs
- [ ] On-call rotation defined for critical alerts

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| Alert on every threshold | Alert on user-impacting symptoms |
| Debug logging in production | Appropriate levels, raisable on demand |
| Unstructured messages | Structured JSON |
| Drop trace context at a boundary | Propagate it everywhere |
| Dashboards with fifty panels | One focused dashboard per service |
| Alerts without runbooks | Every alert links to its response |
| Keep logs forever | Retention driven by need and compliance |
| Measure only infrastructure | Measure what users experience |

## Related skills in this plugin

- [Deploying to Kubernetes](../deploying-to-kubernetes/SKILL.md) — cluster-level
  collection and workload metrics
- [Implementing CI/CD pipelines](../implementing-ci-cd-pipelines/SKILL.md) —
  deployment markers and pipeline visibility
- [Managing secrets](../managing-secrets/SKILL.md) — credentials for observability
  backends
- [Optimizing cloud cost](../optimizing-cloud-cost/SKILL.md) — log ingestion and
  metric cardinality are real line items
