---
name: reviewing-ui
description: "Runs one UI verification pass against Figma: delegates fresh Playwright-CLI capture of the running app to ui-capture-worker, then the design comparison to ui-reviewer, and returns PASS, FAIL, or VERIFICATION NOT RUN with a complete difference table. Read-only — it never fixes code. Use when asked to verify implemented UI against a Figma design or check whether a page matches its design."
when_to_use: "Trigger on: 'verify this UI against Figma', 'does this page match the design', 'review the UI', re-verifying a component after a fix, or the per-iteration verification step of the UI verification gate. Judging code quality is reviewing-code; the full verify-fix loop lives in orchestrating-feature-implementation's UI verification gate."
---

# Reviewing UI

One verification pass comparing the current implementation against its Figma design,
run from the main conversation. This pass is **delegate-only and read-only**: capture
belongs to the `ui-capture-worker` subagent, judgment to the `ui-reviewer` subagent,
and no code changes happen here.

Inputs from `$ARGUMENTS`: the Figma URL (or pinned node link), the exact full dev
server URL, the component or section name, and optionally a task id or artifact
directory. Ask the user for whatever is missing — do not infer the dev server URL
from config files, running processes, or port scans.

## Applicability and Precedence

Local repository rules outrank this skill. During feature delivery, the
verify-fix loop in
[`orchestrating-feature-implementation`](../orchestrating-feature-implementation/references/ui-verification-gate.md)
owns iteration budgets and escalation; this skill is the single pass it repeats.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Treat the user-confirmed full dev server URL as a pinned session input: confirm it once, then forward it unchanged to every capture and review delegation. Never rediscover, normalize, or port-swap it. |
| MUST | Delegate capture to `ui-capture-worker` and judgment to `ui-reviewer`. Never perform either side in the main conversation, and never substitute code review, type checks, builds, or ad-hoc browser inspection for the delegated pass. |
| MUST | Enforce the hard ordering gate: `ui-reviewer` is invoked only after a completed `ui-capture-worker` pass for the current iteration AND `actual.png`, `computed-styles.json`, and `a11y-snapshot.yml` are confirmed present in the iteration directory. A reviewer invoked without them returns `VERIFICATION NOT RUN` — that is a process error, not a verdict. |
| NEVER | Claim capture is unavailable without an actual failed delegation, and never raise a Figma blocker from this conversation's own tool access — the `ui-reviewer` runtime determines whether the Figma MCP is available to it. |
| MUST | Require the reviewer's report to contain `Verification Result`, `Component`, `Artifact Directory`, per-artifact status, and blocker guidance. An empty or field-missing response is invalid: rerun once with the same pinned URL, the same artifact directory, and a stricter handoff; still invalid → treat as `VERIFICATION NOT RUN`. |
| MUST | Save the reviewer's returned report verbatim as `iteration-<N>/report.md` (the reviewer is read-only and cannot write it). |
| NEVER | Treat `VERIFICATION NOT RUN` as PASS or FAIL. It is a blocker state: resolve the blocker with the user, rerun capture, then rerun review on fresh artifacts. |
| NEVER | Bypass an authentication or access gate, ask the user to paste credentials into chat, or let a delegate do either. The default resolution is the repo-root `.env` contract the capture worker returns. |

## Procedure

1. **Pin the inputs.** Check the Playwright CLI once per session:
   `playwright-cli --version`, falling back to `npx --no-install playwright cli
   --version` (never `npx playwright-cli`, a deprecated npm package); when neither responds, ask the user whether to install it now
   (`npm install -g @playwright/cli@latest`) or wait while they install it. Then:
   Figma URL, exact full dev server URL (user-confirmed — ask
   once and pin it for the session), component name, task id when known. Derive the
   shared verification root `specifications/<task-id>/ui-verification/` (or
   `specifications/<page-slug>/…` without a task id) and the next
   `iteration-<N>/` directory.
2. **Delegate capture.** One self-contained `ui-capture-worker` delegation: the
   pinned full URL, the Figma URL, the shared root and `figma-expected.png` path,
   the iteration directory, and any prepared auth inputs (`.env` contract or
   storage-state path). Require its structured capture summary back.
3. **Gate on artifacts.** Confirm all three ACTUAL files exist in the iteration
   directory and the shared `figma-expected.png` exists. Capture blocked → step 5.
4. **Delegate judgment.** One `ui-reviewer` delegation: the Figma URL, the same
   pinned URL unchanged, the component name, and the exact artifact directory.
   Demand the full report contract. Save the report as `report.md` in the iteration
   directory and relay the verdict, the complete difference table, and recommended
   fixes to the caller or user.
5. **On blockers** (`VERIFICATION NOT RUN`): resolve with the user — missing or
   wrong URL, unexpected page content, missing Figma reference, or a login redirect
   (relay the capture worker's derived `TSH_UI_LOGIN_*` var names and its exact
   `.env` message; after the user confirms saving `.env`, rerun capture so it
   reloads the file). Blockers consume no iteration budget. Ask the user to enable
   the Figma MCP or supply an exported reference image only after a delegated
   `ui-reviewer` pass itself reports the Figma side blocked.

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [`verifying-ui`](../verifying-ui/SKILL.md) | Interpreting a verdict, tolerances, or the artifact contract | The judging standard the reviewer applies |
| [`capturing-ui-evidence`](../capturing-ui-evidence/SKILL.md) | A capture blocker needs diagnosing, or auth inputs must be prepared | The capture contract, playwright-cli commands, the `.env` auth contract |
| [UI verification gate](../orchestrating-feature-implementation/references/ui-verification-gate.md) | This pass runs inside feature delivery and returned FAIL | The verify-fix loop, 5-iteration budget, escalation gate |
