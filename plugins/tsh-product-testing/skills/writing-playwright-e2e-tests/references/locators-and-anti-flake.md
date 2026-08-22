# Locators, test data and mocking

Most E2E flake traces back to one of three things: a locator coupled to markup, a wait
that races the application, or shared state between tests. This file covers all three.

## Locator priority

Work down this list and stop at the first that fits:

1. **`getByRole`** — `page.getByRole('button', { name: 'Submit' })`. Matches what
   assistive technology exposes, so it survives markup refactors and doubles as a weak
   accessibility check: if `getByRole` cannot find your button, a screen reader cannot
   either.
2. **`getByLabel`** — form fields, via their visible label.
3. **`getByText`** — static content and non-interactive assertions.
4. **`getByTestId`** — only where no user-visible locator is feasible: a canvas, an
   icon-only control with no accessible name, a list row identified by nothing visible.

Never `.class-name`, never XPath, never structural chains like
`div > div:nth-child(3)`. Those break on a harmless refactor and pass on a broken page.

```typescript
// couples to implementation, breaks on restyle
await page.locator('.submit-btn-primary').click();

// matches what the user sees
await page.getByRole('button', { name: 'Submit' }).click();
```

Prefer `getByTestId` over a brittle chain when the accessible name is genuinely absent
— but treat a missing accessible name as a finding worth reporting, not just a
locator inconvenience.

## Page Objects

```typescript
export class FeaturePage {
  constructor(readonly page: Page) {}

  get submitButton() {
    return this.page.getByRole('button', { name: 'Submit' });
  }

  async navigate() {
    await this.page.goto('/feature');
  }
}
```

Conventions that keep them useful:

- **Getters return locators, they do not act.** A getter that clicks hides the action
  from the test, and the test is what should read as the scenario.
- **Methods for multi-step flows** — `login(email, password)`, not one method per click.
- **No assertions inside the Page Object.** Assertions belong in the test, where the
  failure message means something.
- **Match the project's existing shape** even where it differs from this. One
  convention beats a better one applied inconsistently.

## Waiting

Playwright's assertions auto-wait and auto-retry. Use them and nothing else.

```typescript
// races the app; passes locally, fails in CI
await page.waitForTimeout(2000);
expect(await page.getByText('Saved').isVisible()).toBe(true);

// waits for the actual condition, up to the configured timeout
await expect(page.getByText('Saved')).toBeVisible();
```

Two forbidden waits, and why:

- **`waitForTimeout()`** — encodes a guess about machine speed. A CI runner under load
  is slower than a laptop, so the guess fails exactly where it matters.
- **`waitForLoadState('networkidle')`** — never settles on a page with polling,
  websockets, or analytics beacons, and settles too early on a page that fetches after
  first paint.

When you must wait on a network round-trip, wait for the specific response:

```typescript
const response = page.waitForResponse(r => r.url().includes('/api/orders') && r.ok());
await page.getByRole('button', { name: 'Place order' }).click();
await response;
```

## Test data and isolation

Every test creates its own data, with a unique key, so the suite is parallel-safe:

```typescript
const id = `test-${Date.now()}-${test.info().parallelIndex}`;
```

`parallelIndex` matters — timestamps alone collide between workers starting in the same
millisecond, which produces a flake that only appears under parallelism and is
miserable to diagnose.

Rules:

- **No test depends on another test's state.** Ordering is not guaranteed, and it is
  the first thing to break when someone adds `--shard`.
- **Clean up what you create**, or make the data disposable by construction.
- **Credentials from `process.env`**, never literals, never committed, never logged.

## Mocking

**Mock only genuinely external third-party boundaries** — a payment provider, an email
service, a partner API you do not control.

```typescript
await page.route('**/api/external/**', route =>
  route.fulfill({ status: 200, body: '{}' })
);
```

Mocking the application's own API turns an end-to-end test into a UI unit test with
extra steps: it will keep passing after the backend breaks, which is the exact failure
E2E exists to catch.

Legitimate reasons to mock, all about the *third party*: non-determinism, cost per
call, rate limits, and unreachability from CI. "It was failing" is not one of them —
a failing call against your own stack is the test working.

Document each mock in the coverage table so a reviewer can see what was not exercised
for real.
