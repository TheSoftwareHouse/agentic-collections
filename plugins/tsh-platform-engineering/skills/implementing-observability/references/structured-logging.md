# Structured logging

A log line is data, not prose. Free-text messages cannot be filtered, aggregated, or
joined to a trace, which is exactly what is needed during an incident.

## Format

```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "level": "error",
  "message": "Payment processing failed",
  "service": "payment-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "error": {
    "type": "PaymentGatewayError",
    "message": "Connection timeout"
  },
  "context": {
    "payment_id": "pay-123",
    "amount": 99.99
  }
}
```

## Required fields

| Field | Purpose |
| :-- | :-- |
| `timestamp` | Time-based queries; ISO 8601 with a timezone, always UTC |
| `level` | Filtering — debug, info, warn, error |
| `service` | Which service emitted it |
| `trace_id` | Correlation with traces and with other services' logs |
| `message` | Human-readable, and **stable** — see below |

Keep `message` constant for a given event and put the variables in fields. `"Payment
processing failed"` with `payment_id` in context can be counted and grouped;
`"Payment pay-123 failed"` produces a distinct string every time and cannot be
aggregated at all.

## Trace correlation

`trace_id` on every line is what turns three separate tools into one investigation:
alert fires on a metric, trace shows the slow hop, logs filtered by that `trace_id`
say why. Without it, correlating means guessing by timestamp.

Use the OpenTelemetry logging integration so the active trace context is injected
automatically. Passing a trace ID by hand through call layers is forgotten at exactly
the boundary that matters.

## Levels

| Level | Use for |
| :-- | :-- |
| `error` | Something failed that needs someone to know |
| `warn` | Recovered, degraded, or approaching a limit |
| `info` | Significant state changes — startup, shutdown, config loaded |
| `debug` | Detail for development; off in production by default |

Per-request `info` logging in a high-traffic service is a cost problem and a
signal-to-noise problem. That is what traces are for.

Make the level runtime-adjustable so debug can be raised during an investigation
without a redeploy.

## Never log

- Passwords, tokens, API keys, session identifiers
- Full request or response bodies on anything handling personal or payment data
- Card numbers, national identifiers, health data
- Authorization headers — including in the "log the whole request for debugging" case,
  which is where they usually leak

Redact at the collector as a second layer, since an application-level mistake is
inevitable. The collector is also where to enforce it consistently across services.

Personal data in logs inherits the retention of the log stream, which is usually far
longer than any lawful basis for keeping it — a compliance problem, not just hygiene.

## Retention

Set it per stream, driven by what the logs are for:

- **Application logs** — days to a few weeks covers debugging.
- **Audit and security logs** — driven by the compliance requirement, and stored
  separately with tighter access.
- **Access logs** — high volume; sample or aggregate rather than keeping every line.

Unbounded retention is the default in too many setups, and it is both a growing bill
and a growing liability.
