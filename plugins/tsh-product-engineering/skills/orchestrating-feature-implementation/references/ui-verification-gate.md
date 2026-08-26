# The UI verification gate

The per-item verify-fix loop that closes every Figma-backed UI task. It runs in the
main conversation after the implementer's report and before the final verification
phase — code review never starts while a UI item is open.

## Scope — what counts as a UI verification item

UI-verification involvement is broad: ANY change to rendered UI on a Figma-backed
screen — layout, spacing, sizing, width/height caps, flex/grid, alignment,
typography, colors, or component structure — is a UI verification item, even when the
plan carries no explicit verification task for it. Never reclassify a visual or
layout change as a "narrow code fix" to skip the gate. A UI task without a Figma
reference: stop and get the URL from the user, then record it in the plan — never
skip verification and never guess the design.

## Inputs pinned before the first iteration

- **Playwright CLI availability**, checked once, before the first UI delegation:
  run `playwright-cli --version`, falling back to `npx --no-install playwright-cli
  --version`. When neither responds, ask the user (AskUserQuestion) whether to
  install it now (`npm install -g @playwright/cli@latest`) or wait while they
  install it themselves — never start the gate with the CLI missing, and never let
  this blocker surface first inside a subagent, which cannot ask.
- **The exact full dev server URL**, confirmed by the user once and then forwarded
  unchanged through every capture and review delegation. Never inferred from config,
  running processes, or port scans; no delegate may switch it, swap ports, or start
  another server.
- **The Figma URL or node** for each item, from the plan (or the user when missing).
- **The shared verification root**, defined once per item before iteration 1:
  `specifications/<task-id>/ui-verification/`, with the reusable
  `figma-expected.png` inside it. Every iteration reuses that same shared root and
  reference while the Figma URL/node is unchanged — no per-iteration copies, and the
  root is never redefined mid-loop.

## The loop, per item — never batch items

```text
iteration = 0
while iteration < 5:
    iteration += 1
    fix ALL differences from the latest report (skip on the very first pass)
    run one verification pass exactly as reviewing-ui defines:
        fresh capture via ui-capture-worker  → iteration-<N>/ artifacts
        judgment via ui-reviewer             → verdict + report.md
    if PASS: item closed — exit the loop
    if FAIL: continue — do NOT stop, do NOT accept the current state
    if VERIFICATION NOT RUN: resolve the blocker with the user; this consumes
        NO iteration budget — rerun capture and review, same iteration count
after 5 completed FAIL iterations with remaining mismatches:
    open the structured escalation gate below
```

Each pass follows [`reviewing-ui`](../../reviewing-ui/SKILL.md) exactly: capture
first, hard ordering gate on the three ACTUAL artifacts, then the reviewer — both as
subagent delegations, never self-executed in this conversation.

The gate runs exclusively on the **Playwright CLI** (capture) and the **Figma MCP**
(EXPECTED) — no delegate substitutes another browser tool for either side. State in
every `ui-engineer` delegation under this gate that the gate runs after the task, so
the engineer implements and runs its Definition of Done commands but leaves all
rendered-result verification to the gate.

When the user has explicitly ruled on a difference mid-loop (a gate question about a
design-vs-ticket conflict, intentional data differences, and similar), forward that
ruling verbatim in every later reviewer delegation for the item. The reviewer may
exclude from its verdict only differences covered by a forwarded ruling — it never
invents waivers, and neither does this orchestrator.

Hard rules:

- A single FAIL is never terminal and never "good enough" — keep iterating.
- Never report an item complete while its latest result is FAIL.
- Every iteration regenerates fresh ACTUAL artifacts; the shared
  `figma-expected.png` is refreshed only if the Figma node changed. Never reuse
  pre-fix evidence — re-verification on stale artifacts is invalid.
- Type checks, builds, unit/integration tests, and code review are NOT UI
  verification; "it compiles" and "code review passed" never close a UI item.

## Routing fixes

On FAIL, delegate the fix to `ui-engineer` with the **complete** verification report
and the explicit instruction to fix **ALL** listed differences, not just the first.
Then fresh capture, then fresh review — never assume the fix worked.

Apply the report's confidence level:

- **HIGH** — fix exactly as reported.
- **MEDIUM** — fix the obvious issues; ask the user about the unclear ones.
- **LOW** — ask the user before any change; the tool data may be incomplete.

If the reviewer consistently returns LOW confidence or tool errors, do not loop
blindly: ask the user whether they can verify manually (Figma and app side by side),
record the issue in the plan's Changelog, and continue or escalate.

## Blockers (`VERIFICATION NOT RUN`)

A pre-verification blocker — missing or wrong URL, auth redirect, unreachable page,
wrong page state, incomplete artifacts, Figma MCP unavailable to the reviewer — never
counts as an iteration and never enters the escalation gate. Resolve it with the
user, rerun capture with the same pinned URL, and re-verify:

- **Auth redirect**: relay the capture worker's derived `TSH_UI_LOGIN_*` env var
  names using its exact `.env` message pattern; after the user confirms saving
  `.env`, rerun capture so the worker reloads the file. Never bypass the gate, and
  relay any "gate looks trivially bypassable" warning to the user as a potential
  security vulnerability.
- **Figma-side blocker**: ask the user to enable the Figma MCP or provide an
  exported reference image only after a delegated `ui-reviewer` pass itself reported
  the Figma side blocked — never from this conversation's own tool access.
- **Reviewer response empty or missing required fields**: rerun once with the same
  pinned URL, same fresh artifacts, and a stricter handoff; still invalid → keep the
  item at `VERIFICATION NOT RUN` and resolve with the user.
- An item may become `ESCALATED` from a blocker only when the user explicitly
  acknowledges it as unresolved.

## The structured escalation gate (after 5 FAIL iterations)

Pause and present a structured summary: component or section name, Figma URL,
remaining mismatches, what was attempted in each iteration, suspected root cause.
Then ask the user (use the AskUserQuestion tool) with exactly these options:

1. **Continue** — with an explicit additional iteration count chosen by the user.
2. **Stop and accept as `ESCALATED`** — the user explicitly acknowledges the
   remaining gaps.
3. **Custom instruction** — the user redirects the approach.

Record the decision and outcome in the plan's Changelog. If the extra budget is
exhausted with gaps remaining, run the same gate again. `ESCALATED` is narrow: a
genuine, user-acknowledged blocker — unresolved auth, ambiguous or intentional design
intent, or a capability limit after exhausted iterations. Missing capture,
fixed-but-not-reverified, and code-only review are incomplete verifications, never
valid escalations.

## Closing the gate

Every item ends **PASSED** or explicitly **ESCALATED** — individually, never
batched. Mark the verification result (PASS, iteration count, or escalation) in the
plan and todo list per item. Before the final verification phase, compile a **UI
Verification Summary**, reported separately from code review:

- components/sections verified, with per-item verdicts
- iterations per component
- design gaps discovered and how they were handled
- deviations from the design, with rationale and user decisions

Only when every item is PASSED or ESCALATED does the flow proceed to the plan's
final verification phase (code review + functional verification).
