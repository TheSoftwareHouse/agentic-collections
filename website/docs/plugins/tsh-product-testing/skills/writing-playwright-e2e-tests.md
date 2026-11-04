---
title: Writing Playwright E2E Tests
sidebar_label: writing-playwright-e2e-tests
sidebar_position: 2
description: TSH's standard for Playwright end-to-end tests, from mapping acceptance criteria to scenarios to a bounded debug loop and flake detection.
sources:
  - plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/SKILL.md
  - plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/references/
sources_hash: "35911081db896299feae5bff6f6e6afdafce8abebe594b4736e0be3db01ab391"
---

# Writing Playwright E2E Tests

**Plugin:** [`tsh-product-testing`](/docs/plugins/tsh-product-testing/)  
**Invoke:** `/tsh-product-testing:writing-playwright-e2e-tests` (Claude also loads it when the work matches its description)  
**Used by:** [`e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer), which lists it in its `skills` frontmatter

TSH's standard for Playwright end-to-end tests: mapping acceptance criteria to scenarios, Page Object structure, user-visible locators, auto-waiting instead of manual timeouts, unique test data for parallel runs, mocking only external boundaries, and a bounded debug loop with explicit iteration limits and flake detection. A test earns its place by catching a real bug and never crying wolf, so the skill aims at tests that are reliable, maintainable, fast (parallel-safe) and meaningful.

The project's existing test conventions outrank this skill. Before writing anything it establishes them: `playwright.config.ts`, existing Page Objects, the locator strategy and any `data-testid` convention, fixtures and setup files, the test scripts in `package.json` and the Playwright version. When a `*.plan.md` exists, its Technical Context is the primary source.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Criteria to scenarios** | A table of acceptance criterion, scenario type (Happy, Error or Edge) and test name is produced before any code. Every criterion maps to at least one test, mocked boundaries and Page Objects to create are listed |
| **Naming** | `should <behavior> when <condition>`, because the name is the failure message read in CI output |
| **Locators** | Priority order `getByRole`, `getByLabel`, `getByText`, then `getByTestId` only where no user-visible locator is feasible. Never CSS classes, XPath or structural chains |
| **Page Objects** | Getters return locators and do not act, methods wrap multi-step flows, no assertions inside the Page Object, and the project's existing shape wins over the skill's |
| **Waiting** | Auto-waiting assertions only. `waitForTimeout()` and `waitForLoadState('networkidle')` are forbidden; wait for a specific element or response |
| **Test data** | Unique per run, for example `test-${Date.now()}-${test.info().parallelIndex}`; no test depends on another test's state; credentials come from environment variables |
| **Mocking** | Only genuinely external third-party boundaries, each listed in the coverage table. Mocking the application's own API is forbidden |
| **Language** | The language version under test is pinned before the first locator, because accessible names change with locale |
| **Live exploration** | Every locator is confirmed against the running app with the Playwright CLI before the first test run |
| **Debug loop** | Run, inspect the real page state, fix one thing, repeat, with hard iteration limits |
| **Stability and CI** | 3+ consecutive headless passes, no `.only`, base URL from `process.env.BASE_URL` (or the project's convention) rather than hardcoded, viewport set explicitly rather than inherited from a local default, no hardcoded credentials, and a pass when run in parallel |

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Use user-visible locators; `getByTestId` only where none is feasible |
| MUST | Rely on auto-waiting assertions |
| MUST | Generate unique test data per run |
| MUST | Pin the language version before any locator. When the app serves more than one language and the plan, config and existing tests do not settle it, ask the user before the first locator; choosing silently and disclosing it does not satisfy the rule |
| MUST | Confirm every locator with the Playwright CLI before the first test run, using the commands in the skill's CLI reference. Skipping is allowed only when the dev server is unreachable and must be named in the report. A test that drives no browser has nothing to confirm |
| MUST | Verify a new or fixed test with 3+ consecutive headless passes |
| MUST | Read credentials from environment variables; never hardcode, commit or print them |
| MUST | Mark a test that fails because the application is broken as `test.fixme('BUG: <description>')` and report the bug |
| NEVER | Use `waitForTimeout()` or `waitForLoadState('networkidle')`, CSS class or XPath selectors, or tests that depend on each other's state |
| NEVER | Mock the application's own API to make a test pass |

## How it works

1. Establish context: project conventions and the plan's Technical Context.
2. Map criteria to scenarios using the table.
3. Explore the running app with the Playwright CLI to confirm locators. The snapshot is the accessibility tree that `getByRole` resolves against. A preflight checks that the CLI is installed; in the main conversation the skill asks whether to install it or wait, and a subagent that cannot ask reports the missing prerequisite. The dev server must be running.
4. Write Page Objects, then tests, in the project's existing shape.
5. Run and iterate under the bounded loop.
6. Confirm stability with 3+ consecutive headless passes.
7. Check CI readiness and report.

Playwright API detail is looked up with `context7` against the version in `package.json`, using the library ID `/microsoft/playwright.dev` directly. `context7` is bundled by [`tsh-core`](/docs/plugins/tsh-core/).

### Iteration limits

| Limit | Threshold | Action on reaching it |
| :-- | :-- | :-- |
| Per test | 5 iterations | Mark `test.fixme()` with what was tried, move on |
| Per suite | 15 iterations | Stop entirely and report |
| Flake detection | 3 runs with a mixed pass/fail result | Stop fixing, investigate the race |
| Stability gate | 3+ consecutive passes | Below this, the test is not done |

The skill calls these hard stops, not guidance. A failing test is either a wrong test or a real bug, and deciding which is the whole job: when the application contradicts the acceptance criterion, the test stays and the bug is reported.

### Output

The report is an `E2E Test Summary` with a coverage table, results per file, issues (`BUG` and `FLAKY`) and files. Two lines are contract fields that must appear verbatim with real values: `Locators confirmed against the running app` and `Language pinned by`.

## References

| Reference | Loaded when |
| :-- | :-- |
| Locators, data and mocking | Writing any test or Page Object |
| Debugging and the verification loop | A test is failing, flaky, or newly written and unverified. The skill says to read it before starting a fix loop |
| Exploring with the Playwright CLI | Confirming locators against the running app, or inspecting live page state in the debug loop |

The CLI reference covers the availability preflight, named sessions that are always closed, snapshots, executing a candidate locator against the live page, and `console` and `requests` diagnostics. See the [Playwright CLI integration](/docs/integrations/playwright-cli) for the tool.

## Related skills

- [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility): the accessibility tree that role-based locators depend on is the same one an audit examines.

## Source

[`plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/SKILL.md)
