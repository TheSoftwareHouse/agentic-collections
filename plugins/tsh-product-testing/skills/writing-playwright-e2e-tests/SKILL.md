---
name: writing-playwright-e2e-tests
description: "TSH's standard for Playwright end-to-end tests: mapping acceptance criteria to scenarios, Page Object structure, user-visible locators, auto-waiting instead of manual timeouts, unique test data for parallel runs, mocking only external boundaries, and a bounded debug loop with explicit iteration limits and flake detection. Use when writing, debugging, reviewing or de-flaking E2E tests."
when_to_use: "Trigger on: writing E2E or Playwright tests for a feature or acceptance criteria, a flaky test that passes sometimes, a test failing on a timeout or a locator that cannot be found, creating or refactoring Page Objects, deciding what to mock in an E2E test, making a suite CI-ready or headless-safe, reviewing E2E tests before merge, or a plan task whose Definition of Done includes end-to-end coverage."
---

# Writing Playwright E2E Tests

A test earns its place by catching a real bug and never crying wolf. Four properties
carry that: reliable (never flaky), maintainable (Page Objects), fast (parallel-safe),
and meaningful (asserts what a user would notice).

## Applicability and Precedence

**The project's existing test conventions outrank this skill.** Before writing
anything, establish them:

- `playwright.config.ts` — projects, base URL, retries, reporters, viewport
- Existing Page Objects — the directory (`pages/`, `pom/`, `e2e/pages/`) and whether
  they use getters, methods, or fixtures
- Locator strategy already in use, and any `data-testid` convention
- Fixtures and setup files — auth state, seeding, per-test isolation
- The test scripts in `package.json`, and the Playwright version to search docs against

When a `*.plan.md` exists, its Technical Context section is the primary source — it
records conventions already discovered, so do not re-derive them.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Use user-visible locators — `getByRole`, `getByLabel`, `getByText`. `getByTestId` only where no user-visible locator is feasible. |
| MUST | Rely on Playwright's auto-waiting assertions. A test that needs a manual delay to pass is a test that will fail in CI. |
| MUST | Generate unique test data per run so tests are parallel-safe — e.g. `test-${Date.now()}-${test.info().parallelIndex}`. |
| MUST | Pin the language version under test before writing any locator — accessible names change with locale, so `getByRole` against the wrong language tests nothing. When the app serves more than one language and neither the plan, the Playwright config nor existing tests settle it, ask the user which version the tests target. Choosing silently and disclosing the choice in the report does not satisfy this rule — the question comes before the first locator. |
| MUST | Confirm every locator against the running app with the Playwright CLI before the first test run — source code is not evidence of the rendered accessibility tree. Load [playwright-cli-exploration.md](./references/playwright-cli-exploration.md) first and use its commands; never an improvised browser script, which skips the preflight and leaves scratch files in the repository. A test that drives no browser (pure API scenarios) has no locators and nothing to confirm. Skipping is allowed only when the dev server is unreachable, and must be named in the report. |
| MUST | Verify a new or fixed test with **3+ consecutive passes in headless mode** before reporting it done. One green run proves nothing about flake. |
| MUST | Read credentials from environment variables. Never hardcode them, never commit them, never print them. |
| MUST | Mark a test that fails because the *application* is broken as `test.fixme('BUG: <description>')` and report the bug. Never bend the test to make a real defect pass. |
| NEVER | Use `waitForTimeout()`, or `waitForLoadState('networkidle')` — both are flake sources. Wait for a specific element or response instead. |
| NEVER | Use CSS class or XPath selectors that couple the test to implementation detail. |
| NEVER | Let one test depend on state another test left behind. |
| NEVER | Mock the application's own API to make a test pass. Mock only genuinely external third-party boundaries. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Locators, data and mocking](./references/locators-and-anti-flake.md) | Writing any test or Page Object | Locator priority with examples, auto-waiting, test data isolation, what may and may not be mocked |
| [Debugging and the verification loop](./references/debugging-and-verification-loop.md) | A test is failing, flaky, or newly written and unverified | The bounded debug loop, iteration limits, per-error recovery, flake detection, CI readiness |
| [Exploring with the Playwright CLI](./references/playwright-cli-exploration.md) | Confirming locators against the running app, or inspecting live page state in the debug loop | Availability preflight, session hygiene, page snapshots, executing a candidate locator, diagnostics |

Read [debugging-and-verification-loop.md](./references/debugging-and-verification-loop.md)
before starting a fix loop — the iteration limits exist to stop an unbounded chase, and
that is the failure mode this skill most often prevents.

## Map criteria to scenarios first

Before writing a line, produce this table:

| Acceptance criterion | Scenario type | Test name |
| :-- | :-- | :-- |
| *from the plan, ticket, or prompt* | Happy / Error / Edge | `should <behavior> when <condition>` |

Then confirm:

- [ ] Every criterion maps to at least one test
- [ ] External boundaries needing a mock are listed
- [ ] Page Objects to create or extend are listed

Coverage is judged against this table, so an unmapped criterion is a gap you name
rather than discover at review.

## Naming

`should <behavior> when <condition>` — `should display an error when login fails`. The
name is the failure message a colleague reads in CI output at 9am; it should say what
broke without opening the file.

## Procedure

1. **Establish context** — the section above, plus the plan's Technical Context.
2. **Map criteria to scenarios** using the table.
3. **Explore the running app** to confirm locators before committing to them, using
   the Playwright CLI per
   [playwright-cli-exploration.md](./references/playwright-cli-exploration.md). Its
   page snapshot is the accessibility tree, which is exactly the view `getByRole`
   resolves against — so what you see there is what your locator will match — and a
   candidate locator string can be executed against the live page before it enters a
   test. Run the reference's availability preflight first; when the CLI is missing
   and you can ask, offer to install it or to wait — the user chooses, never you.
   The first snapshot also shows which language the page rendered in — pin the
   language version under test and confirm they match before reading any accessible
   names. Requires the dev server running.
4. **Write Page Objects, then tests**, following the project's existing shape.
5. **Run and iterate** under the bounded loop in
   [debugging-and-verification-loop.md](./references/debugging-and-verification-loop.md).
6. **Confirm stability** — 3+ consecutive headless passes.
7. **Check CI readiness** and report.

Look up Playwright API detail with `context7` against the version in `package.json`.
For Playwright specifically, query the library ID `/microsoft/playwright.dev` directly
rather than resolving it first.

## Output

```markdown
## E2E Test Summary

### Coverage
| Criterion | Test | Status |
|---|---|---|

Coverage: X/Y
Locators confirmed against the running app: <playwright-cli session | n/a — API-only | skipped: reason>
Language pinned by: <prompt | Playwright config | existing tests | user answer | n/a>

### Results
| File | Pass | Fail | Flaky | Headless |
|---|---|---|---|---|

### Issues
- BUG: <description> → `test.fixme()`, needs an application fix
- FLAKY: <description> → what was tried, what is still suspected

### Files
```

The `Locators confirmed against the running app` and `Language pinned by` lines are
contract fields — include them verbatim with real values. Stating the same facts in
prose does not replace them; they exist so compliance is auditable at a glance.

Report honestly. A suite with two `test.fixme()` markers and a named bug is a better
outcome than a green suite that asserts nothing.

## Anti-Patterns

| Don't | Do |
| :-- | :-- |
| `waitForTimeout(2000)` | Assert on the element or response you are waiting for |
| `.btn-primary`, XPath | `getByRole('button', { name: 'Submit' })` |
| Shared fixture data across tests | Unique data per test run |
| Mock your own API to go green | Mock third-party boundaries only |
| Weaken an assertion to pass | `test.fixme()` and report the bug |
| One green run means done | 3+ consecutive headless passes |
| A test per UI element | A test per user-visible behavior |
| Helpers and Page Objects for tests not yet needed | Only what the current scope requires |

## Related skills in this plugin

- [Auditing accessibility](../auditing-accessibility/SKILL.md) — the accessibility tree
  your role-based locators depend on is the same one an audit examines
