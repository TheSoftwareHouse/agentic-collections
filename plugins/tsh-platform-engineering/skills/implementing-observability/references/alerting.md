# Alerting

An alert has one job: cause the right person to do the right thing. Everything below
follows from that.

## Severity

| Severity | Response | Example |
| :-- | :-- | :-- |
| Critical | Page on-call immediately | Service down, data-loss risk, SLO budget burning fast |
| Warning | Investigate within hours | Error rate elevated, disk at 80% |
| Info | Review in business hours | Deployment completed, scaling event |

Only Critical wakes anyone. If everything is critical, nothing is — and the routing
must actually differ per severity, or the levels are decoration.

## Quality rules

- **Actionable** — a documented response exists. If the response is "look at it and
  see", it is not an alert yet.
- **Symptom, not cause** — alert on what users experience. High CPU on a service
  meeting its latency target is not an incident; requests failing is, whatever the CPU
  is doing. Cause-based alerts fire during harmless conditions and stay silent during
  novel failures.
- **Unique** — one incident, one page. A failure that fires nine alerts buries the
  informative one.
- **Timely** — early enough to act, late enough to be real. That is what `for:` is for.

## Prometheus rule template

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m])) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 1%)"
          runbook_url: "https://runbooks.example.com/high-error-rate"
```

Every element is load-bearing:

- **`for: 5m`** — the alert must persist before firing. Without it, any single scrape
  blip pages someone.
- **A ratio, not a count.** Ten errors is meaningless without knowing whether there
  were a hundred requests or a million.
- **`{{ $value }}` in the description** — the responder should know how bad it is
  before opening a dashboard.
- **`runbook_url`** — non-negotiable. An alert without one is unfinished.

## Error-budget burn alerts

Better than static thresholds for anything with an SLO: alert on the *rate* the budget
is being consumed, not on an instantaneous value.

Two windows, both required to fire, is the standard pattern:

- **Fast burn** — a short window with a high multiple of the budget rate. Catches
  sharp outages quickly, pages immediately.
- **Slow burn** — a long window with a low multiple. Catches the steady degradation
  that never trips a static threshold but eats the month's budget.

This is what stops the two classic failures: paging on a two-minute blip that consumed
nothing, and silently burning the entire budget at just under the threshold.

## Runbooks

Every alert links to one, and each contains:

1. What this alert means, in one sentence.
2. What the user is experiencing right now.
3. First checks, as concrete commands or dashboard links.
4. Known causes and their fixes.
5. How to escalate, and to whom.
6. How to verify recovery.

Write the runbook when the alert is written. Written after the first page, it is
written by whoever was least prepared to write it.

## Reviewing an existing setup

Alert fatigue is the usual reason to be here. Look for:

- Alerts that fired and were resolved with no action — delete or re-tune them.
- Alerts that fire together — consolidate to the one closest to user impact.
- Cause-based alerts on infrastructure metrics with no symptom link.
- Alerts with no runbook, no owner, or a routing destination nobody reads.
- Missing coverage: a past incident that no alert would have caught.

Deleting a noisy alert is a real improvement. Muting it is not — a muted alert is a
gap that still looks like coverage.
