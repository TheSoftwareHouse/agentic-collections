# Metrics and SLOs

## What to measure

### RED — for services

| Metric | Meaning | Example SLI |
| :-- | :-- | :-- |
| **R**ate | Requests per second | `rate(http_requests_total[5m])` |
| **E**rrors | Failing requests | `rate(http_requests_total{status=~"5.."}[5m])` |
| **D**uration | Latency distribution | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |

### USE — for resources

| Metric | Meaning | Example |
| :-- | :-- | :-- |
| **U**tilization | Share of time busy | CPU, memory usage |
| **S**aturation | Work queued and waiting | Pending pods, connection pool depth |
| **E**rrors | Error events | OOM kills, disk errors |

Saturation is the one usually missing and often the most predictive: utilization at
80% with an empty queue is fine, while utilization at 60% with a growing queue is an
incident forming.

Measure latency as a histogram, never an average. An average latency hides exactly the
tail that users notice; report p50, p95 and p99 and alert on the tail.

## SLO definition

```yaml
slo:
  name: api-availability
  description: "API returns successful responses"
  sli:
    metric: |
      sum(rate(http_requests_total{status!~"5.."}[5m]))
      /
      sum(rate(http_requests_total[5m]))
  target: 99.9%
  window: 30d
  error_budget: 0.1%   # ~43 minutes per 30 days
```

Rules that make an SLO useful rather than decorative:

- **Measure what the user experiences.** An SLI computed from internal service health
  can be green through an outage caused by the load balancer in front of it.
- **Never target 100%.** It leaves no budget, so every release becomes a risk nobody
  can quantify and the SLO stops informing decisions.
- **Pick the window deliberately.** 30 days rolling is the common default; a calendar
  month aligns with reporting but resets the budget on an arbitrary date.
- **The budget is meant to be spent.** An untouched error budget means over-investment
  in reliability relative to what was promised. That is a real finding, not a success.
- **Exclude what you do not control** from the SLI, and say so in the description.

## Error budget policy

The budget is only useful if something happens when it runs low. Agree the policy
before the SLO is published:

| Budget remaining | Response |
| :-- | :-- |
| Healthy | Ship normally |
| Low — under ~25% | Reliability work takes priority over features |
| Exhausted | Feature freeze until the budget recovers |

Without a policy the SLO is a dashboard, not a decision-making tool.

## Cardinality

Every distinct label-value combination is a separate time series. Labels with
unbounded values — user IDs, request IDs, raw URL paths, error messages — will take a
metrics backend down.

Keep the identifying detail in logs and traces, where it belongs, and label metrics
only with bounded dimensions: service, endpoint template, status class, environment,
region.
