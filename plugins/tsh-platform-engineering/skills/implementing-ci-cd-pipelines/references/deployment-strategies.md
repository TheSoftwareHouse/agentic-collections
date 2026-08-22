# Deployment strategies

Pick on two questions: how fast must a rollback be, and can two versions serve
traffic at once? Everything else follows.

## Rolling

Replace instances in batches, old and new serving simultaneously.

- **Rollback** — slow: another rolling pass back to the previous version.
- **Requires** — backward-compatible changes, since both versions serve traffic.
- **Cost** — no extra capacity beyond the surge setting.
- **Watch** — a failing new version can consume the whole rollout before anyone
  notices. Health checks and a `maxUnavailable` that preserves capacity are what make
  this safe.

Default for stateless services with compatible changes.

## Blue-green

Two complete environments; traffic switches at the router or load balancer.

- **Rollback** — instant: switch traffic back.
- **Requires** — double capacity during the switch, and a plan for stateful
  dependencies.
- **Cost** — highest, briefly.

**The database question is why this strategy exists.** With one shared database, the
schema must satisfy both versions during the switch, so migrations become expand →
migrate → contract across separate releases: add the new column, deploy code writing
both, backfill, switch, then drop the old column in a later release. A migration that
breaks the old version turns instant rollback into no rollback.

## Canary

Route a small traffic share to the new version, widen it as metrics hold.

- **Rollback** — instant: route the share back to zero.
- **Requires** — traffic splitting (ingress, service mesh, or load-balancer weights)
  and metrics good enough to judge a subset.
- **Cost** — one extra replica set.

Only meaningful with enough traffic for a percentage slice to be statistically
readable, and with an explicit promotion rule — error rate and latency thresholds,
and a time to hold at each step. A canary nobody defined a promotion rule for is a
rolling deploy with extra steps.

## Recreate

Stop the old version, start the new one.

- **Rollback** — slow, and with downtime.
- **Requires** — accepted downtime.
- **Use** — development and test environments, or a change genuinely incompatible with
  running two versions, such as an exclusive lock or a one-way migration.

Never the default for production.

## Choosing

| Question | Answer | Strategy |
| :-- | :-- | :-- |
| Can two versions serve traffic together? | No | Blue-green or recreate |
| Must rollback be instant? | Yes | Blue-green or canary |
| Is there enough traffic to read a percentage slice? | Yes | Canary |
| Stateless, compatible, ordinary release? | Yes | Rolling |
| Non-production? | Yes | Recreate is fine |

## What every strategy needs

- **Health checks that mean something.** A readiness probe hitting a static endpoint
  reports healthy while the application cannot reach its database.
- **A documented rollback.** Written down, with the command, before the deploy runs.
- **An abort condition.** The metric and threshold that stops the rollout, decided in
  advance rather than during the incident.
- **Migrations decoupled from deploys.** Expand-migrate-contract, so any version in
  flight can serve any state of the schema.
