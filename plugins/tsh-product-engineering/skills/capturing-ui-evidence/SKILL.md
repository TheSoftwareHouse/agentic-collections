---
name: capturing-ui-evidence
description: "The mechanical capture contract for UI verification: drives the playwright-cli against the pinned dev server URL to collect actual.png, computed-styles.json and a11y-snapshot.yml into the iteration artifact directory, and exports the shared figma-expected.png via the Figma MCP. Evidence collection only — judging the result is verifying-ui."
when_to_use: "Trigger on: collecting ACTUAL evidence from a running app for UI verification, running playwright-cli capture commands, exporting the shared Figma reference image, or resolving a capture blocker such as a login redirect. Judging the artifacts is verifying-ui; running a full pass is reviewing-ui."
user-invocable: false
---

# Capturing UI Evidence

The capture side of UI verification: mechanical evidence collection with the
Playwright CLI, plus preparing the shared Figma reference. Capture never judges
whether the UI matches the design — that is [`verifying-ui`](../verifying-ui/SKILL.md).

## Applicability and Precedence

Local repository rules outrank this skill. If `playwright-cli` is not on PATH, use
`npx playwright-cli`; if neither works, that is a blocker to escalate (the fix is
`npm install -g @playwright/cli@latest`), never a reason to improvise another
capture method.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Use only the caller-provided, user-confirmed full URL for the current pass, unchanged. A delegation without that URL is an immediate blocker. |
| NEVER | Discover, infer, normalize, or replace the URL: no port swaps, no config inspection to pick another URL, no launching or switching to another local app or server. |
| MUST | Write every artifact into the caller-provided iteration directory with an explicit path. `playwright-cli` defaults to `.playwright-cli/` — that location is WRONG for these artifacts; never rely on default output locations. |
| MUST | Collect all three ACTUAL artifacts — `actual.png`, `computed-styles.json`, `a11y-snapshot.yml` — and confirm they exist in the iteration directory. Even one missing artifact makes the verification invalid. |
| MUST | When the caller provides a Figma URL and shared verification root, export or ensure the shared `figma-expected.png` via the Figma MCP BEFORE browser capture begins, so auth or page blockers cannot prevent EXPECTED preparation. |
| NEVER | Fetch a design through the browser: no figma.com navigation, no saving a browser, login, or error screenshot as `figma-expected.png`. Figma MCP unavailable → escalate the blocker. |
| NEVER | Bypass, fake, seed, or inject authentication state (cookies, tokens, localStorage, sessionStorage) or assume an identity to get past a login or access gate — even when the gate looks trivially circumventable. A genuine login through the app's real sign-in UI, with user-provided inputs, is allowed; bypass never is. Read `./references/authenticated-capture.md` the moment a login redirect appears. |
| MUST | Escalate every blocker (missing URL, unreachable page, login redirect, unexpected content, missing target component, failed command) back to the caller immediately with exact details. Never stop silently, and never ask the user directly from a subagent. |
| MUST | Report a trivially bypassable access gate as a potential security vulnerability in the escalation notes — flag it, never exploit it. |
| NEVER | Judge visual correctness, modify UI code, tests, or design artifacts. |

## Capture Procedure

0. **Define and create the artifact directory FIRST:**

   ```bash
   UI_VERIFICATION_DIR="specifications/<task-id>/ui-verification"   # or specifications/<page-slug>/... when no task id exists
   ARTIFACT_DIR="$UI_VERIFICATION_DIR/iteration-<N>"
   FIGMA_EXPECTED="$UI_VERIFICATION_DIR/figma-expected.png"
   mkdir -p "$ARTIFACT_DIR"
   ```

   Keep any `state-save` file outside `specifications/**`, in a git-ignored temp path.

1. **Ensure the shared Figma reference** when the caller provided a Figma URL:
   reuse a valid existing `$FIGMA_EXPECTED` (Figma URL/node unchanged), otherwise
   export it now via the Figma MCP node-image export. Export failure → stop and
   escalate before opening the app page.
2. **Open a named session** — `playwright-cli open -s <session-name>`.
3. **Resize to the Figma frame width** — `playwright-cli resize <figma-width> 1080 -s <session-name>`.
4. **Navigate to the full pinned URL** including query params —
   `playwright-cli goto <full-url> -s <session-name>`.
5. **Stabilize the render** —
   `playwright-cli run-code -s <session-name> "async page => { await page.emulateMedia({ reducedMotion: 'reduce' }); await page.waitForLoadState('networkidle'); }"`.
   Add route mocks only when the task explicitly requires deterministic data; mask
   known dynamic regions (timestamps, avatars, ads) when unavoidable.
6. **Screenshot** — `playwright-cli screenshot --filename="$ARTIFACT_DIR/actual.png" -s <session-name>`
   (full page when supported); fallback:
   `playwright-cli run-code -s <session-name> "async page => { await page.screenshot({ path: '$ARTIFACT_DIR/actual.png', fullPage: true }); }"`.
7. **Accessibility snapshot** — `playwright-cli --raw snapshot -s <session-name> > "$ARTIFACT_DIR/a11y-snapshot.yml"`.
8. **Computed styles** — `playwright-cli --raw eval -s <session-name> "JSON.stringify(...)" > "$ARTIFACT_DIR/computed-styles.json"`.
   The payload covers every major container and control under verification: bounding
   boxes, computed width/height, max-width, min-height, padding, margin, gap,
   alignment-relevant properties, and targeted style values needed to explain
   differences. Measure the VISIBLE rendered box — the element that paints the
   border and background — never only an inner input or text node. For
   component-library wrappers (MUI, Ant Design, …) capture both the wrapper and the
   inner control, labeled so the reviewer knows which is which; the design is
   compared against the wrapper.
9. **Confirm artifacts landed** — `ls -la "$ARTIFACT_DIR"`: all three files present
   there, and `$FIGMA_EXPECTED` present at the shared root. Anything in
   `.playwright-cli/` or the working directory → move it or re-run with the explicit
   path. Missing `figma-expected.png` → go back to step 1 and export it.
10. **Clean up** — `playwright-cli close -s <session-name>`, also after aborts.

## Exit codes and escalation

- `open` or `goto` non-zero → escalate immediately; never continue silently.
- Redirect to login or auth wall → follow `./references/authenticated-capture.md`;
  without prepared inputs, return the exact derived env var names to the caller.
- Unexpected content (error page, blank page, different route) or missing target
  component at the confirmed URL → escalate immediately with a description.
- Session cleanup failures → note them, then attempt explicit cleanup.

These are pre-verification blockers: the pass result is `VERIFICATION NOT RUN`, it
consumes no iteration budget, and capture reruns after the blocker is resolved.

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [playwright-cli commands](./references/playwright-cli-commands.md) | Before running any playwright-cli command, or when a command's exact syntax or fallback is needed | Install and npx fallback, sessions, navigation, snapshots, `--raw`, eval, screenshots, run-code, route mocking, state save/load |
| [Authenticated capture](./references/authenticated-capture.md) | The page redirects to login, auth inputs were provided, or an access gate blocks capture | The `TSH_UI_LOGIN_*` env contract, field-key derivation, `.env` reload, storage-state reuse, non-standard auth fallbacks, secret handling |

## Related Skills

- [`verifying-ui`](../verifying-ui/SKILL.md) — the judging standard these artifacts feed.
- [`reviewing-ui`](../reviewing-ui/SKILL.md) — orchestrates capture plus judgment as one pass.
