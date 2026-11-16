---
title: UI verification
sidebar_label: UI verification
sidebar_position: 3
description: How implemented UI is judged against its Figma design — fresh Playwright-CLI capture, a read-only design judge, a verdict of PASS, FAIL or VERIFICATION NOT RUN, and a per-item verify-fix loop with an iteration budget and an escalation gate.
sources:
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/
  - plugins/tsh-product-engineering/skills/verifying-ui/
  - plugins/tsh-product-engineering/skills/capturing-ui-evidence/
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/references/ui-verification-gate.md
  - plugins/tsh-product-engineering/agents/ui-capture-worker.md
  - plugins/tsh-product-engineering/agents/ui-reviewer.md
  - plugins/tsh-product-engineering/agents/ui-engineer.md
sources_hash: "1836ea34987cdfc1ae8d6d37e2ec14e68d9f0da5c9ccd12f9d2f196ba54fcaf1"
---

# UI verification

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/) · **Start with:** `/tsh-product-engineering:reviewing-ui` for one standalone pass ("does this page match the design?"), or let [feature implementation](./feature-implementation) run it as the UI verification gate for every Figma-backed UI task.

UI verification compares the running application against its Figma design. The Figma design is the source of truth for every comparison: when in doubt, the design wins. Type checks, builds, unit tests and code review are never UI verification — "it compiles" and "code review passed" never close a UI item.

## At a glance

<!-- PHASE2(visual): the loop is a plain-text block because @docusaurus/theme-mermaid is not installed — the old site drew this flow as a diagram — decide in Phase 2 whether to add the Mermaid theme or a diagram component -->

```text
pin inputs once: Playwright CLI · dev server URL · Figma URL · locale · auth
   │
   ├─▶ (background) ui-capture-worker exports figma-expected.png
   │
   └─▶ per UI item, iteration N = 1…5
         ui-capture-worker ─▶ iteration-N/ actual.png · computed-styles.json · a11y-snapshot.yml
         main conversation checks the three files and what was measured
         ui-reviewer       ─▶ PASS | FAIL | VERIFICATION NOT RUN
         main conversation saves iteration-N/report.md
           PASS                 → item closed
           FAIL                 → ui-engineer fixes ALL differences → next iteration
           VERIFICATION NOT RUN → resolve the blocker with the user, no iteration used
         after 5 FAIL iterations → escalation question to the user
```

## Who does what

| Part | Runs in | Component |
| :-- | :-- | :-- |
| One verification pass: pin inputs, delegate capture, check artifacts, delegate judgment, save the report | Main conversation | [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) — delegate-only and read-only |
| The verify-fix loop, iteration budget and escalation | Main conversation | The UI verification gate of [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) |
| Capture ACTUAL evidence; export the shared Figma reference | Subagent (`haiku`, no `Write` or `Edit` tool; writes only the capture artifacts, through the Playwright CLI and shell redirection) | [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker), preloading [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence) |
| Judge ACTUAL against Figma EXPECTED | Subagent (`sonnet`, read-only) | [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer), preloading [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui) |
| Fix the reported differences | Subagent (`sonnet`) | [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer), in fix-application mode |

`verifying-ui` is the judging standard, not a command: it is neither user- nor model-invocable, so "does this page match the design?" routes to `reviewing-ui`, the pass that applies it. `capturing-ui-evidence` stays out of the `/` menu too; both are contracts the two UI agents preload.

## Before the first iteration

The gate pins its inputs once, before any UI delegation, and forwards them unchanged:

- **The Playwright CLI.** `playwright-cli --version`, falling back to `npx --no-install playwright cli --version`. When neither answers, the user is asked whether to install it now (`npm install -g @playwright/cli@latest`) or wait while they do it — never left to surface inside a subagent, which cannot ask.
- **The exact full dev server URL**, confirmed by the user and never inferred from config, running processes or port scans. No delegate may switch it, swap ports or start another server.
- **The Figma URL or node** for each item, from the plan or the user.
- **The locale, language and text direction** the design represents, when the app can render more than one.
- **Authentication**, when the page sits behind a login — resolved now, not discovered by the first capture.
- **Design-versus-ticket conflicts** visible from reading the Figma node against the ticket text.

URL, locale, auth and any visible conflict go to the user in one question round. The shared verification root, `specifications/<task-id>/ui-verification/`, is fixed once per item. While implementation is still running, a background `ui-capture-worker` run with only the Figma URL and that root exports `figma-expected.png`, taking the export off the first capture's critical path.

## One verification pass

Each pass follows [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) exactly, and both halves are subagent delegations — never done in the main conversation:

1. **Capture.** [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) ensures `figma-expected.png` through the Figma MCP before opening the browser, then drives the Playwright CLI in a named session: resize to the Figma frame width, go to the pinned URL, stabilise the render, and write three files into `iteration-<N>/` — a full-page `actual.png` (its height checked against the page's `scrollHeight`), `a11y-snapshot.yml`, and `computed-styles.json` measuring every container and control under verification. It returns a capture summary naming the elements it measured. It never judges what it captured.
2. **Gate on the artifacts.** The main conversation confirms the three ACTUAL files and the shared reference exist, and reads `computed-styles.json`: an entry that is `null` or carries an `error`, or thin coverage of the elements under verification, sends the capture back before any reviewer runs.
3. **Judge.** [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) takes EXPECTED only from the Figma MCP and the shared `figma-expected.png`, and ACTUAL only from this iteration's artifacts. It compares all five categories in one pass — Structure, Layout, Dimensions, Visual, Components — measures dimensions from `computed-styles.json`, and reports every difference with exact expected and actual values.
4. **Save the report.** The reviewer is read-only, so the main conversation writes its report verbatim to `iteration-<N>/report.md`. A report missing the `## Verification Result: <verdict>` heading or a required section is rerun once with a stricter handoff, then treated as `VERIFICATION NOT RUN`.

Run standalone, `reviewing-ui` ends here: it relays the verdict, the complete difference table and the recommended fixes, and never fixes code itself.

### The verdict

| Verdict | Means |
| :-- | :-- |
| **PASS** | The evidence proves a match: zero Structure, Layout or Dimension differences beyond 1–2px rendering tolerance, each backed by a measured value or a structural fact from this iteration, and the full-page screenshot compared side by side with the design |
| **FAIL** | There is something concrete to fix. A FAIL always carries recommended fixes; a FAIL with nothing to fix is treated as `VERIFICATION NOT RUN` |
| **VERIFICATION NOT RUN** | The evidence cannot be trusted or is missing — a blocker, not a verdict. It consumes no iteration |

There are no other verdicts and no invented waivers. A difference is excluded only when an explicit user ruling covering it was forwarded to the reviewer and is cited verbatim. Content or data differences that may vary by environment keep the item FAIL under `Clarification Needed` until the user says whether they should match Figma.

## The verify-fix loop

Inside feature implementation, the gate repeats the pass per item — never batching two items into one review — for up to five iterations:

- **FAIL** → the complete report goes to [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) with the instruction to fix **all** listed differences, using the report's exact values. Then fresh capture and fresh review; the fix is never assumed to have worked. The report's confidence decides how far the fix goes: HIGH — fix exactly as reported; MEDIUM — fix the obvious, ask about the unclear; LOW — ask the user before any change.
- **VERIFICATION NOT RUN** → the blocker is resolved with the user and capture reruns with the same pinned URL. A blocker iteration still gets its own `iteration-<N>/` directory, so directory numbers may run ahead of the iteration count.
- **PASS** → the item is closed.

The named browser session and its login survive the loop until the item ends. For the next iteration the capture worker is preferably resumed with the same recipe; the reviewer is fresh every pass, so no memory of an earlier verdict leaks into the next.

### The escalation gate

After five FAIL iterations, the orchestrator presents the component, the Figma URL, the remaining mismatches, what each iteration tried and the suspected root cause, and asks the user to choose:

1. **Continue** — with an additional iteration count the user picks.
2. **Stop and accept as `ESCALATED`** — the user explicitly acknowledges the remaining gaps.
3. **Custom instruction** — the user redirects the approach.

The decision is recorded in the plan's Changelog. `ESCALATED` is narrow: unresolved auth, ambiguous or intentional design intent, or a capability limit after exhausted iterations. Missing capture, fixed-but-not-reverified and code-only review are never valid escalations.

### Closing the gate

Every item ends PASSED or ESCALATED, individually. Before the final verification phase, the orchestrator compiles a **UI Verification Summary**, reported separately from code review: per-item verdicts, iterations per component, design gaps found and how they were handled, and deviations from the design with the user's decisions.

## Logins

Capture never bypasses, fakes or injects authentication state. It reuses what the project already has, in this order: a documented auth recipe, an existing E2E auth setup (`global.setup`, storage state, an auth fixture), existing `.env` variables that plainly match the login form, a seeded development account. Only when none exists does it derive `TSH_UI_LOGIN_*` variable names from the live form; the user adds them to the repository-root `.env` and capture reruns. Credentials never go through the chat, and a gate that looks trivially bypassable is reported as a potential security vulnerability.

## Where people decide

| Point | What the user decides |
| :-- | :-- |
| Pinned inputs | Confirms the dev server URL, the locale, the auth path, and any design-versus-ticket conflict — in one question round |
| Missing Playwright CLI | Install it now, or wait while they install it |
| Blockers | Resolves each `VERIFICATION NOT RUN` blocker — saving `.env` values, enabling the Figma MCP, supplying a missing URL |
| Clarification Needed | Whether environment-dependent content should match Figma |
| MEDIUM or LOW confidence | Which unclear differences to fix |
| Escalation | Continue, accept as ESCALATED, or redirect |

## What it leaves behind

```text
specifications/<task-id>/ui-verification/     (specifications/<page-slug>/… without a task id)
  figma-expected.png          shared reference, exported once per item
  iteration-<N>/
    actual.png                full-page screenshot of the running app
    computed-styles.json      measured widths, heights, paddings, margins, gaps
    a11y-snapshot.yml         accessibility snapshot: hierarchy, order, grouping
    report.md                 the reviewer's report, saved by the main conversation
  <label>/                    another locale or text direction, judged as its own item
```

## What it needs

- **`tsh-core`**, for the Figma MCP server it bundles — run `/mcp` once to sign in. Until then the reviewer reports `VERIFICATION NOT RUN`. Capture itself needs no design reference. See [Figma](/docs/integrations/figma).
- **The Playwright CLI** on the machine: `npm install -g @playwright/cli@latest`, or a project-local install reached through `npx playwright cli`. See [Playwright CLI](/docs/integrations/playwright-cli).
- **The app already running**, and the exact dev server URL.
