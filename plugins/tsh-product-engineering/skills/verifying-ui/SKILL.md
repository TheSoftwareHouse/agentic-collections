---
name: verifying-ui
description: "The standard for judging implemented UI against its Figma design: EXPECTED comes only from the Figma MCP, ACTUAL only from live Playwright-CLI capture artifacts, compared across structure, layout, dimensions, visual and components under strict tolerances, ending in PASS, FAIL, or VERIFICATION NOT RUN. This is the judging standard the ui-reviewer agent applies — to actually run a verification pass, use reviewing-ui."
when_to_use: "Trigger on: judging whether a rendered page matches Figma, deciding PASS or FAIL for a UI verification item, interpreting capture artifacts (actual.png, computed-styles.json, a11y-snapshot.yml), or writing a UI verification report. Running a pass end to end is reviewing-ui; collecting the artifacts is capturing-ui-evidence."
user-invocable: false
---

# Verifying UI

The judging standard for comparing an implemented UI against its Figma design. The
Figma design is the **source of truth** for every comparison — when in doubt, the
design wins.

## Applicability and Precedence

Local repository rules outrank this skill. If the project defines its own visual
tolerances or design-QA process, apply those numbers inside this process.

**Default to raising, not guessing.** Every named blocker here is an example of one
rule: when you cannot run a real, complete verification on the full artifact base —
something missing, broken, ambiguous, or unexpected, listed here or not — stop.
As a subagent, return a `VERIFICATION NOT RUN` blocker report to the caller; in the
main conversation, ask the user. Never fabricate values or proceed on partial evidence.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Take EXPECTED only from the Figma MCP: resolve the node from the Figma URL, export the node image, and save it as the shared `figma-expected.png`. If the Figma MCP is unavailable or the node cannot be resolved, the result is `VERIFICATION NOT RUN` — never a guess. |
| NEVER | Open figma.com in a browser to fetch a design, or save a browser, login, or error screenshot as `figma-expected.png`. The browser is for the running app (ACTUAL) only. |
| MUST | Require all three ACTUAL artifacts for the current iteration — `actual.png`, `computed-styles.json`, `a11y-snapshot.yml` — before issuing any PASS or FAIL. Missing or partial artifacts → `VERIFICATION NOT RUN` with blocker guidance. |
| NEVER | Substitute code reading, type checks, builds, or test results for verification. They clarify context; the verdict comes only from Figma EXPECTED versus captured ACTUAL. |
| MUST | Complete ALL five categories in one pass — Structure, Layout, Dimensions, Visual, Components — and report every difference found, not just the first. A one-issue report when more exist wastes an iteration. |
| MUST | Measure dimensions from `computed-styles.json`. The accessibility tree carries no CSS: a full-width and a narrow centered container look identical in it. Unmeasured layout = invalid verification, confidence LOW. |
| NEVER | Report PASS while any structure, layout, or >2px dimension difference remains. Structure and layout mismatches are CRITICAL and cannot be waived as "close enough". |
| NEVER | Invent waiver states ("adjudicated", "accepted deviation", "out of scope for this task"). The only verdicts are PASS, FAIL, and VERIFICATION NOT RUN. A difference may be excluded from the verdict only when an explicit user ruling covering it was forwarded in the delegation — cite that ruling verbatim in the report. Everything else beyond tolerance keeps the item FAIL until the user closes it through the escalation gate. |
| MUST | Judge dimensions from values as recorded in `computed-styles.json`. If the captured element does not represent the visible rendered box (an inner input instead of its bordered wrapper), that is a capture defect: return `VERIFICATION NOT RUN` requesting re-capture of the right element — never reconstruct values arithmetically. |
| NEVER | Return FAIL when you recommend no code changes. FAIL means the engineer has something concrete to fix; a pass where nothing is actionable is PASS, and evidence you cannot trust is `VERIFICATION NOT RUN`. Check this before writing the verdict: an empty `Recommended Fixes` and a FAIL verdict together are a contradiction. |
| MUST | Read `computed-styles.json` as evidence about coverage as well as values: an entry that is `null`, carries an `error`, or is missing for an element under verification means that element was never measured. No PASS may rest on it — return `VERIFICATION NOT RUN` naming the unmeasured elements and asking for re-capture. |
| MUST | Treat a present-but-wrong measurement as untrustworthy evidence, not as a difference. When a measured entry describes a different element than its label claims — a page banner recorded as the card under verification, an inner input recorded as its bordered wrapper — the artifact is defective: return `VERIFICATION NOT RUN` naming the entry and the element it actually measured. Never convert a capture defect into a FAIL against the implementation. |
| NEVER | Treat `VERIFICATION NOT RUN` as a pass, a fail, or a consumed iteration. It is a pre-verification blocker state: resolve the blocker, recapture, rerun. |
| MUST | Re-verify after every fix on fresh artifacts from a new capture pass. Never reuse pre-fix evidence or assume a fix worked. |
| NEVER | Repeat a failing tool call more than once. After a second failure, stop and return a `VERIFICATION NOT RUN` blocker report describing the failure. |

## Verification Process

1. **Validate inputs.** Figma URL for the exact component, the user-confirmed pinned
   dev server URL (used unchanged — never rediscovered, normalized, or port-swapped),
   the component name, and the iteration artifact directory.
2. **Ensure EXPECTED (ensure-or-fetch).** Check for a valid shared
   `figma-expected.png` at `specifications/<task-id>/ui-verification/`. Present and
   the Figma URL/node unchanged → reuse it. Missing or node changed → export it now
   via the Figma MCP. Only a genuine export failure justifies `VERIFICATION NOT RUN`.
   Also extract from Figma the specs to compare: layer hierarchy, layout direction,
   alignment, spacing, frame width, typography, colors, radii, shadows, variants,
   states.
3. **Confirm ACTUAL.** The three capture artifacts for THIS iteration, produced by
   `ui-capture-worker` per [`capturing-ui-evidence`](../capturing-ui-evidence/SKILL.md).
   Never artifacts from a prior iteration.
4. **Compare category by category** — read
   [`./references/verification-criteria.md`](./references/verification-criteria.md)
   before comparing. Multimodal comparison of `figma-expected.png` vs `actual.png`,
   `computed-styles.json` for every measured claim, `a11y-snapshot.yml` for structure
   and grouping. Record, per category, concrete differences or an evidence-backed
   "no differences".
5. **Report.** Follow [`./references/report-format.md`](./references/report-format.md)
   exactly — every section present even for `VERIFICATION NOT RUN`, with exact
   EXPECTED and ACTUAL values for every difference.

## Artifact Contract

```text
specifications/<task-id>/ui-verification/
  figma-expected.png          # shared, exported once per item via Figma MCP,
                              # reused across iterations while the node is unchanged
  iteration-<N>/
    actual.png                # full-page screenshot of the running app
    computed-styles.json      # measured widths, heights, paddings, margins, gaps
    a11y-snapshot.yml         # accessibility snapshot: hierarchy, order, grouping
    report.md                 # this verification's report, saved by the caller
```

`figma-expected.png` is never duplicated into `iteration-<N>/` and never re-exported
per iteration. When no task id exists, use `specifications/<page-slug>/ui-verification/`.

When the pinned Figma node covers more than the component under verification, a
cropped reference is allowed — but as a second shared file at the verification root,
named for the region (`figma-expected-<region>.png`), exported once and reused across
iterations. Never write a design image into `iteration-<N>/`: an iteration directory
holds this pass's ACTUAL evidence and its report, nothing else.

Evidence for another locale, language or text direction goes in a labeled sibling —
`ui-verification/<label>/` holding the same three artifacts, for example
`ui-verification/rtl-arabic/` — and is judged as its own item. Never mix a second
variant into `iteration-<N>/`, whose artifacts belong to one pass of one variant.

## PASS Gate (strict)

PASS is allowed only when the evidence proves it — never on "looks close", a partial
review, or to end a loop:

- Shared `figma-expected.png` exists, and this iteration's `actual.png`,
  `computed-styles.json`, and `a11y-snapshot.yml` all exist.
- Every CRITICAL category — Structure, Layout, Dimensions — has ZERO differences
  beyond 1–2px rendering tolerance, each conclusion backed by a cited measured value
  from `computed-styles.json` or a cited structural fact from `a11y-snapshot.yml`.
- The full-page `actual.png` was compared side by side against `figma-expected.png`.
- Every CRITICAL-category conclusion is backed by THIS iteration's artifacts. An
  item not measured in the current pass cannot be discounted by a prior iteration's
  finding — measure it now, or the verdict cannot be PASS.

Any structural difference, any layout difference, any dimension difference >2px, or
any unmeasured "looks roughly right" → FAIL (or `VERIFICATION NOT RUN` when evidence
is missing). The only differences excluded from a verdict are those covered by an
explicit, forwarded user ruling, cited verbatim — never a waiver the reviewer or the
caller invented.

When the only remaining differences are content/data that may plausibly vary by
environment, seed data, locale, or user state, keep the result FAIL, list them under
`Clarification Needed`, and ask whether they are intentional before converting them
to fixes — details in the criteria reference.

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Verification criteria](./references/verification-criteria.md) | About to compare EXPECTED vs ACTUAL, every pass | Category checklists, tolerances, severities, the pre-PASS checklist, confidence levels, the content/data clarification gate |
| [Report format](./references/report-format.md) | Writing any verdict or blocker report | The exact report skeleton, artifact-status table, blocker-resolution section, UNKNOWN rules |

## Related Skills

- [`capturing-ui-evidence`](../capturing-ui-evidence/SKILL.md) — how the ACTUAL
  artifacts this skill judges are collected.
- [`reviewing-ui`](../reviewing-ui/SKILL.md) — runs one verification pass end to end
  from the main conversation.
