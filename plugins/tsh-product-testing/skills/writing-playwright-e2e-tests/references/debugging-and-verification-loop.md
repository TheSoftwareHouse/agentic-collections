# Debugging and the verification loop

An unbounded fix loop is the main way E2E work consumes a day and delivers nothing. The
limits below are what make it terminate.

## The loop

```text
RUN → fails? → INSPECT the real page state → FIX one thing → REPEAT
```

Inspect before changing anything. A `playwright-cli snapshot` of the live page — see
[playwright-cli-exploration.md](./playwright-cli-exploration.md) — shows the
accessibility tree as it actually is, which is where "the locator is wrong" and "the
element genuinely is not there" become distinguishable. Guessing at a new locator
without looking is how a two-minute fix becomes fifteen iterations.

## Iteration limits

| Limit | Threshold | Action on reaching it |
| :-- | :-- | :-- |
| Per test | 5 iterations | Mark `test.fixme()` with what you tried, move on |
| Per suite | 15 iterations | Stop entirely and report |
| Flake detection | 3 runs with a mixed pass/fail result | Stop fixing, investigate the race |
| Stability gate | 3+ consecutive passes required | Below this, the test is not done |

These are hard stops, not guidance. Hitting one and reporting honestly is the correct
outcome — it surfaces a real problem, where a fifteen-attempt chase just hides it in a
longer transcript.

## Error recovery

| Error | Ordered response |
| :-- | :-- |
| Timeout | Confirm the element is expected to appear at all → check the locator against the snapshot → raise the timeout **once**, and only if the app is genuinely slow here |
| Element not found | Snapshot the page → try a different accessible locator → confirm the page actually loaded and did not redirect |
| Network failure | Retry once → confirm the backend is up → consider whether this is an external boundary worth mocking |
| Flaky | Replace any implicit wait with an explicit assertion → look for a race between navigation and assertion → run 5× to confirm the fix |
| Assertion mismatch | Compare against the acceptance criterion, not against current behavior. If the app is wrong, the test is right |
| Application bug | `test.fixme('BUG: <description>')` and report it |

The distinction that matters: **a failing test is either a wrong test or a real bug**,
and deciding which is the whole job. Weakening an assertion until it passes destroys
the value of having written it. When the app contradicts the acceptance criterion, the
test stays and the bug gets reported.

## Diagnosing flake

A test that passes sometimes is worse than one that always fails — it trains people to
re-run CI instead of reading it. Usual causes, in the order worth checking:

1. **Assertion racing navigation** — asserting on the old page before the new one
   commits. Assert on something only the new page has.
2. **Manual wait instead of an assertion** — see the forbidden waits in
   [locators-and-anti-flake.md](./locators-and-anti-flake.md).
3. **Shared test data** — collides only when workers overlap, so it appears under
   parallelism and vanishes when run alone. `parallelIndex` in the data key fixes it.
4. **Animation or transition** — the element exists but is not yet stable. Playwright
   waits for stability on actions; an assertion on a mid-transition value will not.
5. **Test order dependence** — passes in file order, fails when sharded. Run the single
   test in isolation to confirm.
6. **Real intermittent application bug** — the most valuable finding here. Do not
   paper over it; report it.

Confirm any flake fix with 5 consecutive runs, not one.

## CI readiness

Before reporting a suite done:

- [ ] Passes headless — `npx playwright test` with no `--headed`
- [ ] Passes 3+ consecutive times
- [ ] Base URL from `process.env.BASE_URL` (or the project's convention), not hardcoded
- [ ] No hardcoded credentials
- [ ] Viewport set explicitly rather than inherited from a local default
- [ ] No `.only` left in any file — it silently reduces the suite to one test
- [ ] Passes when run in parallel, not just serially
- [ ] Any `test.fixme()` is reported, with the bug it stands for

`.only` is worth its own check: it makes CI green while running almost nothing, and
nothing else in the pipeline will notice.
