# Exploring with the Playwright CLI

The subset of [`playwright-cli`](https://www.npmjs.com/package/@playwright/cli) this
skill uses: confirming locators against the running app before they enter a test, and
inspecting live page state inside the debug loop. Full docs: `playwright-cli --help`.

Why a snapshot settles a locator: it renders the page's accessibility tree — roles
and accessible names — which is exactly the view `getByRole` resolves against. What
the snapshot shows is what the locator will match.

## Availability preflight

Run once, before the first exploration:

```bash
playwright-cli --version                    # global install?
npx --no-install playwright-cli --version   # project-local install?
```

When only the local install answers, prefix every command below with `npx `. When
neither answers, what happens next depends on where you are running:

- **In the main conversation**, ask the user (AskUserQuestion) whether to install it
  for them — `npm install -g @playwright/cli@latest` — or to wait while they install
  it themselves, then re-run the preflight. Their choice, always: never install
  without asking. Offer the global install only — a project-local install writes a
  dependency into the repository under test just to gain an exploration tool.
- **As a subagent**, which cannot ask: report the missing prerequisite and say which
  confirmations were skipped.

Either way, do not guess locators blind: without the snapshot, a wrong locator costs
debug-loop iterations instead of a one-command check.

## Sessions

Always a named session, always closed when done:

```bash
playwright-cli open -s e2e-explore
playwright-cli goto "http://localhost:3000/login" -s e2e-explore
playwright-cli close -s e2e-explore
```

The session keeps its logged-in state while it stays open, so one real sign-in serves
the whole exploration. Treat the URL you were given as pinned — never switch ports or
start a different server.

## Pin the language first

The snapshot's accessible names are in whatever language the page rendered — and
`getByRole` locators are written from those names, so on a multilingual app the
language is a test input, not a detail. Before reading any names off a snapshot:

1. Establish which language version the tests target: the plan or delegation, the
   Playwright config (`locale`, per-project settings), or existing tests. When none
   of them settles it and you can ask, ask the user — never pick silently.
2. Confirm the rendered page matches: the first snapshot shows the actual language.
   If it differs, switch through the app's own mechanism — a language switcher, a URL
   prefix, the config's `locale` — and re-snapshot before confirming any locator.

A suite written against the wrong language is the expensive failure here: every
locator resolves during exploration, and none of it tests the version users get.

## Snapshot — the locator check

```bash
playwright-cli snapshot -s e2e-explore            # accessibility tree with refs (e1, e2, …)
playwright-cli snapshot "#main" -s e2e-explore    # scope to an element
```

Read the role and accessible name off the tree and write the locator from them. To
prove the exact locator, execute it:

```bash
playwright-cli click "getByRole('button', { name: 'Submit' })" -s e2e-explore
```

A locator string that fails here fails in the test — one command instead of one debug
iteration.

## Reaching the state under test

Interact using refs from the snapshot or Playwright locator strings:

```bash
playwright-cli click e15 -s e2e-explore
playwright-cli fill e5 "user@example.com" -s e2e-explore
playwright-cli fill e6 "$E2E_PASSWORD" --submit -s e2e-explore   # --submit presses Enter
playwright-cli press Escape -s e2e-explore
```

Sign in through the application's real login form with environment-supplied
credentials, exactly as the tests must — never seed cookies, tokens or storage to get
past it, and keep credential values out of commands echoed into reports.

## Diagnostics in the debug loop

```bash
playwright-cli console -s e2e-explore     # console messages
playwright-cli requests -s e2e-explore    # network requests
```

`console` distinguishes "the locator is wrong" from "the page crashed before
rendering"; `requests` shows whether the backend call the test waits on ever fired.

## Boundaries

Exploration follows the same rules as the tests: mock nothing of the application's
own API — `playwright-cli route` exists, but the mocking boundary in
[locators-and-anti-flake.md](./locators-and-anti-flake.md) still decides what may be
mocked — and nothing observed live replaces the stability gate: a locator confirmed
against the running page still needs its 3+ consecutive headless passes.
