# The verification document

Use this reference when drafting the final verification phase's functional half. The
document lives next to the plan at
`specifications/<task-id>/<task-name>.verification.md` and is executed by the
`feature-verifier` subagent, which has no conversation history — everything it needs
must be in the file.

## Authoring rules

- **Draft it at planning time, with the user.** Propose the candidate checks —
  browser walkthrough, API calls, database state, log checks, data seeding — and ask
  which to include, before implementation starts. The user's answer decides the
  document's scope; do not add scenarios they declined.
- **One scenario per user-observable acceptance criterion**, roughly. The plan's
  Acceptance Criteria section is the raw material; a criterion nobody can observe
  from outside the code belongs to the code review, not here.
- **Commands verbatim from the plan's Technical Context.** Never assume the stack,
  the ports, or the package manager.
- **Every endpoint, table, and fixture a scenario names is traceable to source.**
  The verifier stops on a failed precondition, so one invented artifact deadlocks
  the whole phase — trace routes to the controllers and tables to the migrations
  before the document ships.
- **A committed E2E suite is scenario zero.** The code-review delegation excludes
  E2E, so this document is the one place the suite runs.
- **No credential values, ever.** Name where credentials come from; never write them
  into the document, the plan, or a report.

## Building blocks

### Header

Plan path, ticket ID, and the app (or apps) under verification. Anyone opening the
file cold can trace what it verifies.

### Environment

What must be running before any scenario starts: the pinned dev server URL, the
verbatim start or attach commands, required containers and services, and where
credentials come from (a named env file, a secrets manager entry — never values).
The verifier treats the URL as pinned: it never switches ports or starts a
different server.

When a scenario runs a committed suite against a persistent local store — a Docker
volume, a dev database — state the clean-baseline expectation and the sanctioned way
to establish it: the reset command the user approved at planning time, or an
instruction to report the baseline's state and stop. The verifier never invents a
reset, so a document silent here turns stale local state into a blocked run.
Prefer a scratch database or schema on the same instance over a destructive
reset — create it, verify against it, drop it — and reserve volume resets for
what the user explicitly authorized. State which database writes scenarios *may*
make, not only which are forbidden: a verifier that needs a seeding `UPDATE` and
finds only prohibitions has to stop.

### Seeding *(optional)*

Verbatim commands that put the database or fixtures into the state the scenarios
assume, plus the expected post-seed state so the verifier can confirm the seed took.
Include only when scenarios need data that a fresh environment lacks.

### Scenarios

Numbered, executed in order. Each carries a tag, preconditions, exact steps, the
expected observable result, and the evidence the report must contain:

| Tag | Steps state | Evidence required |
| --- | --- | --- |
| `[E2E]` | The suite command, verbatim | The command's pass/fail output |
| `[BROWSER]` | URLs to visit, elements to interact with, states to reach | A screenshot per step that is **examined** — accessibility snapshots and click-throughs are navigation, not verification |
| `[API]` | Request method, path, headers, body | A real request's recorded status and the response fields that prove the behavior |
| `[DB]` | The exact query to run | The rows returned, compared to the expected state |
| `[LOGS]` | The container/service and the log pattern to search | The matching log lines |

A scenario may mix tags — seed data `[DB]`, trigger the feature `[API]`, then confirm
the UI shows it `[BROWSER]` — as long as each step names its evidence.

### Pass criteria and report shape

One line per scenario stating what "pass" means, and the report the verifier returns:
per-scenario pass/fail with the evidence above, then blockers. A clean run is stated
plainly.

### Boundaries

Standing rules for the verifier, restated so the document is self-contained: never
fix code, never bypass or fake authentication, never switch servers or ports,
capture each command's full output on its first run — a scenario is never re-run
to recover lost or truncated output — and stop and report on a missing
precondition instead of improvising one.

## Worked example

For the CSV-export plan in [the plan example](./plan-example.md):

```markdown
# CSV export — Verification

Plan: specifications/PROJ-482/csv-export.plan.md · Ticket: PROJ-482
App: reports web app + API (single dev server)

## Environment

- Dev server: http://localhost:3000 (pinned) — start: `pnpm dev`
- Postgres via `docker compose up -d db`
- Login: test account from `.env.local` (see README) — never recorded in reports

## Seeding

- `pnpm db:seed -- --fixture reports-mixed` — expect 25 reports, 8 with status=open

## Scenarios

### 0. [E2E] Committed suite

- Run `pnpm test:e2e` — expect all specs green.

### 1. [API] Filtered export matches the filter

- `GET /reports/export?status=open` with the session cookie.
- Expect: 200, `content-type: text/csv`, 8 data rows, header row first.
- Evidence: status, headers, and row count from the real response.

### 2. [BROWSER] Export button downloads the filtered list

- Visit `/reports`, apply filter status=open, click **Export**.
- Expect: a download of `reports-<date>.csv`; the button reflects the active filter.
- Evidence: examined screenshot of the filtered list with the button, plus the
  download confirmation.

### 3. [API] Empty result is a header-only CSV

- `GET /reports/export?status=archived` (fixture has none).
- Expect: 200 with exactly one header row — not an error.

## Pass criteria

All scenarios pass. Report per scenario with evidence; blockers verbatim.

## Boundaries

Never fix code. Never bypass login — use the test account. Server URL is pinned.
```
