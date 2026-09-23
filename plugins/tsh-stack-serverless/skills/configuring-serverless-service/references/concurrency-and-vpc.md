# Reserved concurrency and VPC attachment

Use this reference when setting a function's `reservedConcurrency`, sizing the database connection budget, or deciding whether a function needs VPC attachment.

## Table of Contents

- [Reserved concurrency is mandatory, not a tuning knob](#reserved-concurrency-is-mandatory-not-a-tuning-knob)
- [VPC attachment is opt-in](#vpc-attachment-is-opt-in)

Two independent per-function decisions that both trade a small amount of
configuration for a large reduction in blast radius.

## Reserved concurrency is mandatory, not a tuning knob

Every deployed function declares its own reserved concurrency. This is not
about performance — it is the blast-radius control for the whole account.

**Without a reserved limit, a function draws on the account's unreserved
concurrency pool** — the capacity every function without a reservation shares.
A single endpoint that gets hit hard (a retry storm from a misbehaving
client, a bug in a caller, a traffic spike) can consume that entire shared
pool, and every other function in the account — including ones with nothing
to do with the incident — starts throttling. A limit that is merely *low* is
a performance problem; a limit that is *absent* is an incident that spreads
outside the function that caused it.

**For anything database-backed, the same number is also a connection
budget.** Each concurrent Lambda invocation typically holds its own
connection (or its own small pool) open to the database. Reserved
concurrency multiplied by the per-invocation pool size is the maximum number
of connections that function can open at once. Add that figure up across
every database-backed function plus anything else that connects (a migration
runner, a background job) and check the total against the database's
`max_connections` — not against any single function's comfort level. A
function with generous reserved concurrency and a database with a modest
connection ceiling will exhaust the database long before it exhausts its own
Lambda limit.

**The budget belongs to the database, not to the service.** That arithmetic is
only complete while one service owns the database outright. The moment a second
service connects to the same instance — because the first was split, or because
a neighbouring service reuses it — each one totals its own functions, each
concludes it fits, and both assertions pass while the database runs out of
connections. Declare the ceiling once in a module the connecting services share,
give each service a named allocation, and have each assert against its own
allocation rather than against `max_connections`. Count everything that
connects, including migration runners and anything scheduled.

**Setting the limit to `0` is also the kill switch for one function** —
useful during an incident, or to disable a function without removing it.

**Treat "declared but missing" as a packaging-time failure, not a code
review nit.** A function definition added without a concurrency value is easy
to miss in review and impossible to notice at runtime until the account is
already under load from somewhere else. See
[`packaging-and-template-checks.md`](./packaging-and-template-checks.md) for
asserting this over every function actually being deployed, not just the
ones a person remembered to check.

**Exempt local emulation only.** A concurrency limit is a deploy-time
concept; local emulators (`serverless-offline` or equivalent) have no
concurrency control to set, and requiring the value there would break a
fresh clone before it ever reaches AWS. Scope the requirement to "every stage
that actually deploys," and make that scoping explicit in whatever enforces
it, so the exemption cannot silently widen to cover a real stage.

## VPC attachment is opt-in

Attaching every function to a VPC by default causes two concrete problems:

1. **It breaks a clean checkout.** A VPC-attached function needs real
   subnet and security-group ids. A new or freshly cloned service has none, so `package`/`deploy` fails before there is even an AWS
   account behind it — and the same failure hits CI on every pull request.
2. **It is not free.** A VPC-attached Lambda has no route to the public
   internet without a NAT Gateway — a fixed monthly cost plus per-GB data
   processing. Plenty of services only call public AWS endpoints or public
   APIs and gain nothing from VPC attachment; forcing it on them is pure
   cost.

**Default every function to no VPC.** Turn it on only for the functions that
need to reach something private — most commonly a database with no public
endpoint. Make it a single, explicit switch (an environment flag plus the
network ids it requires) rather than a per-function scattering of subnet
lists, and fail fast — at packaging time, not at deploy time — when the
switch is on but an id is missing. A half-configured VPC should never reach
AWS.

**The execution role needs the minimum ENI permissions**
(`ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`,
`ec2:DeleteNetworkInterface`, and the IP-assignment actions) only for
functions that are actually attached — see the wildcard carve-out in
[`iam-and-secrets.md`](./iam-and-secrets.md) for why these specific actions
are allowed `Resource: "*"`. Add them conditionally, not unconditionally, so
a service that never turns VPC on never carries permissions it does not use.
