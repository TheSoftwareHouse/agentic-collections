---
title: Capturing UI Evidence
sidebar_label: capturing-ui-evidence
sidebar_position: 1
description: The mechanical capture contract for UI verification, driving Playwright CLI against the pinned dev server URL to collect a full-page screenshot, computed styles and an accessibility snapshot.
sources:
  - plugins/tsh-product-engineering/skills/capturing-ui-evidence/
sources_hash: "34fe05de76e0da17f0141f4a05c97fb991f038f1bd80d4419b777565eab9446a"
---

# Capturing UI Evidence

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** no command (`user-invocable: false`). Claude or an agent loads it when the work matches its description: the [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) agent preloads it, and `disable-model-invocation` is not set.  
**Used by:** the [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) agent. [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) loads it to diagnose capture blockers and prepare auth inputs, [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui) points to it for how ACTUAL artifacts are collected, and [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) names it as the capture contract behind the UI gate.

The capture side of UI verification: mechanical evidence collection with the Playwright CLI, plus preparing the shared design reference when the caller supplies one. The three ACTUAL artifacts come purely from the running application, so capture runs with or without a design reference. The Figma export is a conditional extra step, not a prerequisite. Capture never judges whether the UI matches the design; that is the `ui-reviewer` agent, applying the [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui) standard.

If `playwright-cli` is not on PATH, the skill uses `npx playwright cli` (never `npx playwright-cli`, which fetches a deprecated package). If neither works, that is a blocker to escalate, with the fix `npm install -g @playwright/cli@latest`, never a reason to improvise another capture method. Local repository rules outrank the skill.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Pinned URL** | Only the caller-provided, user-confirmed full URL is used, unchanged. No discovery, inference, normalization, port swaps or launching another server. A delegation without a URL is an immediate blocker |
| **Explicit output paths** | Every artifact is written to the caller-provided iteration directory. The CLI's default `.playwright-cli/` location is wrong for these artifacts. Commands run from the repository root so that scratch directory stays git-ignored |
| **Three artifacts** | `actual.png`, `computed-styles.json` and `a11y-snapshot.yml` must all exist in the iteration directory. Even one missing artifact makes the verification invalid |
| **Full-page screenshot** | `actual.png` is captured with `fullPage: true`, never the viewport, and its pixel height is checked against the page's `scrollHeight` before success is reported |
| **Provable measurements** | `computed-styles.json` is a JSON object, never a string containing JSON or split across companion files. Each entry carries a `label`, the `selector`, a `textSample`, a `rect` and the computed values. The component root is resolved and proven, by text it is known to render, before anything is measured |
| **No null entries** | An entry that is `null` or carries an `error` is never shipped. The selector is fixed and the element re-measured. Selectors are CSS only, and text matching is done in JavaScript |
| **Right element** | Each measured element must be the element its label claims, scoped to the component under verification. The visible rendered box, the ancestor that paints the border or background, is measured as well as the inner control |
| **Locale** | The pinned locale, language and text direction is captured the way the caller specified, and what was actually captured is recorded. A different language than requested is a blocker |
| **Figma reference** | When a Figma URL and shared root are supplied, the shared `figma-expected.png` is exported or ensured through the Figma MCP before browser capture begins. It is written only at the verification root, never inside `iteration-<N>/`, and never fetched through the browser |
| **Authentication** | The project's own authentication path is reused first. Authentication state is never bypassed, faked, seeded or injected |
| **Escalation** | Every blocker goes back to the caller immediately with exact details. A trivially bypassable access gate is reported as a potential security vulnerability and never exploited |
| **No judging** | The skill never judges visual correctness and never modifies UI code, tests or design artifacts |

## How it works

0. **Define and create the artifact directory first:** `specifications/<task-id>/ui-verification/iteration-<N>/` (or `specifications/<page-slug>/…` when no task ID exists), with the shared `figma-expected.png` path beside it.
1. **Ensure the shared Figma reference** when a Figma URL was provided. Reuse a valid existing file, otherwise export it. An export failure stops the capture before the app page is opened.
2. **Open a named session** with `playwright-cli open -s <session-name>`.
3. **Resize** to the Figma frame width. The height only sizes the window.
4. **Navigate** to the full pinned URL, including query parameters.
5. **Stabilize the render** with reduced motion and a wait for network idle. Route mocks are added only when the task explicitly requires deterministic data.
6. **Screenshot** the full page and prove it is full-page.
7. **Take the accessibility snapshot** into `a11y-snapshot.yml`.
8. **Measure computed styles** into `computed-styles.json`, covering every major container and control under verification.
9. **Confirm the artifacts landed** in the iteration directory, with nothing left in `.playwright-cli/`.
10. **Clean up** by closing the session, unless the caller says the verification loop continues. Then the named session stays open and its name is reported, so the next iteration reuses the browser and its login.

Non-zero exit from `open` or `goto`, a login redirect, unexpected content or a missing target component are pre-verification blockers. The pass result is `VERIFICATION NOT RUN`, it consumes no iteration budget, and capture reruns once the blocker is resolved.

## Authenticated capture

The reference `authenticated-capture.md` is loaded the moment a login redirect appears. A genuine login through the application's real sign-in UI, with inputs the user explicitly provided, is allowed; bypassing the gate never is. The ladder, stopping at the first hit:

1. An auth recipe the project documents in `CLAUDE.md`, `.claude/rules/` or the plan's Technical Context.
2. An existing end-to-end auth setup, such as a Playwright `global.setup`, a committed storage-state path or an auth fixture.
3. Existing `.env` variables that plainly match the login form's fields, used as they are and never renamed.
4. A seed or fixture that creates a known development account.
5. Only when none exists, the derived `TSH_UI_LOGIN_*` contract: one variable name per form field, derived in the order `name`, `autocomplete`, `id`, visible label text. If the variables are missing, capture stops and returns the exact names to the caller, who asks the user to add them to the repo-root `.env`. The values are never pasted into chat and never printed.

After one real login the session can be saved with `state-save` to a path outside `specifications/**` and reused in later iterations. Non-standard auth such as an SSO chooser, MFA or captcha can use a caller-provided storage-state path or a manual login in the open session. The mechanism that authenticated the run is reported in the capture summary.

## Reference Loading

| Reference | Load when | Covers |
| :-- | :-- | :-- |
| `playwright-cli-commands.md` | Before running any playwright-cli command, or when exact syntax or a fallback is needed | Install and npx fallback, sessions, navigation, snapshots, `--raw`, eval, screenshots, run-code, route mocking, state save and load, and a worked computed-styles payload |
| `authenticated-capture.md` | The page redirects to login, auth inputs were provided, or an access gate blocks capture | The auth ladder, the `TSH_UI_LOGIN_*` contract, `.env` reload, storage-state reuse, non-standard auth fallbacks and secret handling |

## Related skills

- [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui): the judging standard these artifacts feed.
- [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui): orchestrates capture plus judgment as one pass.

Capture depends on the [Playwright CLI](/docs/integrations/playwright-cli) integration.

## Source

[`plugins/tsh-product-engineering/skills/capturing-ui-evidence/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/capturing-ui-evidence/SKILL.md)
