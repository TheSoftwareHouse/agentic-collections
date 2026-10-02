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
  run `playwright-cli --version`, falling back to `npx --no-install playwright cli
  --version` (never `npx playwright-cli`, a deprecated npm package). When neither responds, ask the user (AskUserQuestion) whether to
  install it now (`npm install -g @playwright/cli@latest`) or wait while they
  install it themselves — never start the gate with the CLI missing, and never let
  this blocker surface first inside a subagent, which cannot ask.
- **The exact full dev server URL**, confirmed by the user once and then forwarded
  unchanged through every capture and review delegation. Never inferred from config,
  running processes, or port scans; no delegate may switch it, swap ports, or start
  another server.
- **The Figma URL or node** for each item, from the plan (or the user when missing).
- **The locale, language and text direction the design represents**, when the app
  can render the screen in more than one. Ask the user once, pin it, and pass it in
  every capture delegation together with how to select it (URL parameter, app
  language switch, or a storage value the app itself sets). Capturing the wrong
  language against an English design wastes a full capture round. When another
  locale or direction also matters (an RTL variant, for example), capture it as an
  extra labeled sibling of the iteration directories — `ui-verification/<label>/` —
  never inside `iteration-<N>/`, and judge it as its own item.
- **Authentication, prepared before the first capture, not discovered by it.**
  When the pinned page sits behind a login, resolve the auth path now: check
  repo-root `.env` for existing `TSH_UI_LOGIN_*` vars, or ask the user for them in
  the same question round as the URL and locale. A first capture that exists only to
  discover the login screen burns four to five minutes and a delegation round that
  one upfront check replaces.
- **One question round, not four.** URL, locale, auth, and any design-vs-ticket
  conflict already visible go to the user together (AskUserQuestion takes up to four
  questions). Every separate round costs a full user round-trip — in practice the
  slowest step of the whole gate.
- **Read the design against the ticket before iteration 1.** A conflict visible by
  comparing the Figma node with the ticket text (a fixed-width card vs "full width")
  is a user question NOW — asked mid-loop it stalls the gate and can cost a whole
  FAIL iteration implementing the losing interpretation. Two patterns are candidate
  conflicts every time they appear: one control styled differently from its siblings
  (enabled-looking among disabled — intentional state or a design artifact?), and
  any dimension the ticket describes in words that the design contradicts in pixels.
  Scan for both while reading the node, and put what you find in the same upfront
  question round.
- **The shared verification root**, defined once per item before iteration 1:
  `specifications/<task-id>/ui-verification/`, with the reusable
  `figma-expected.png` inside it. Every iteration reuses that same shared root and
  reference while the Figma URL/node is unchanged — no per-iteration copies, and the
  root is never redefined mid-loop.
- **Prefetch the Figma reference while implementation is still running.** EXPECTED
  depends on the design, not on the code, so delegate the `figma-expected.png`
  export (a `ui-capture-worker` run with only the Figma URL and the shared root — no
  app URL, no browser) as a background task the moment the gate's inputs are pinned,
  in parallel with the `ui-engineer` delegations. This takes the export off the
  first capture's critical path and surfaces a Figma-side blocker minutes earlier,
  while the fix costs nothing instead of stalling the loop.

## The loop, per item — never batch items

Per-item means per-verdict, not single-file: with several UI items, stages of
different items may overlap — item B's capture can run while item A's review is in
flight — as long as every verdict is issued per item, on that item's own artifacts,
by its own fresh reviewer pass. What stays forbidden is batching two items into one
review or one report.

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

Two reuse rules keep later iterations fast without touching quality:

- **The browser session survives the loop.** The named playwright-cli session (and
  the login it holds) stays open across iterations of the same item and closes when
  the item ends PASS or ESCALATED — tell the capture delegation which session name
  to reuse. Re-opening a browser and re-authenticating every round costs minutes and
  adds nothing: freshness lives in the artifacts, which are regenerated every pass
  regardless.
- **Resume the capture worker; keep the reviewer fresh.** For iteration N+1, prefer
  resuming the previous capture worker (SendMessage) with "same recipe, write to
  iteration-<N+1>/" — it already knows the session, the root proof, and the
  measurement payload. The reviewer is the opposite case: fresh per pass, always,
  so no memory of a previous verdict leaks into the next one.

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

- **Gate on what capture measured, not only on file existence.** The capture
  summary must name the elements it measured; when `computed-styles.json` does not
  cover the containers and controls under verification, send capture back before
  invoking the reviewer. Three present-but-thin files still produce a wasted
  reviewer round. Read the file before delegating: an entry that is `null` or
  carries an `error`, or a companion measurements file bolted on beside it, means
  the capture is incomplete — re-capture, never review around the gap.
- **Save every reviewer report to disk yourself.** The reviewer is read-only, so
  after each verdict write its report verbatim to
  `iteration-<N>/report.md` before acting on it. A verdict that lives only in this
  conversation leaves no reviewable trace in the repository. You may add your own
  observations as a clearly marked `> **Orchestrator note.**` block above the
  report — never edited into its body.
- **Reject a report that breaks the contract before you act on it.** It must carry
  the literal `## Verification Result: <verdict>` heading plus the `Component`,
  `Artifact Directory`, `Artifact Status`, `Blocker Resolution` and
  `Recommended Fixes` sections. Missing any of them: rerun the reviewer once on the
  same artifacts with a stricter handoff naming the missing sections, then treat a
  second failure as `VERIFICATION NOT RUN`. Do not paraphrase a non-conforming
  report into shape yourself.
- **A FAIL with nothing to fix is not a FAIL.** When a report says FAIL but
  recommends no code change — or blames the evidence rather than the
  implementation — treat it as `VERIFICATION NOT RUN`: no iteration is consumed, and
  the next step is re-capture, not a fix delegation.
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
- **Every iteration directory ends with a report, or an explanation.** When a
  capture round is superseded before any reviewer saw it, write a one-line
  `iteration-<N>/report.md` saying so and why. A directory holding artifacts nobody
  judged, with nothing recording that, is indistinguishable later from a review that
  was skipped.
- **Directory numbers may outrun the iteration count, and that is fine.** A blocker
  pass still gets its own `iteration-<N>/` for its fresh artifacts, while the
  5-iteration budget counts only passes that actually judged the implementation.
  When they diverge, say so in the next report — "counted as the second real
  iteration; iteration 2 was an artifact blocker" — so the numbering stays
  auditable.

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
