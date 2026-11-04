---
title: Verifying UI
sidebar_label: verifying-ui
sidebar_position: 8
description: The judging standard for comparing implemented UI against its Figma design across five categories under strict tolerances, ending in PASS, FAIL or VERIFICATION NOT RUN.
sources:
  - plugins/tsh-product-engineering/skills/verifying-ui/
sources_hash: "c97dfbfd0a5fe613f21075c96f2088ddd40066b3641bfa51ae82739de5451466"
---

# Verifying UI

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** no command (`user-invocable: false` and `disable-model-invocation: true`), so only agents that preload it use it. It is loaded only through the `skills:` preload of the [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) agent.  
**Used by:** the [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) agent. [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) reads it as a file when interpreting a verdict, and [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) names it as the judging standard behind the UI gate.

The judging standard for comparing an implemented UI against its Figma design. The Figma design is the source of truth for every comparison: when in doubt, the design wins. To actually run a verification pass, use [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui).

Today the Figma MCP is the only accepted source of EXPECTED. Everything else the standard defines (the five categories, the tolerances, the PASS gate and the report format) is independent of where EXPECTED came from. The reference source is a parameter of the standard, which is why the skill is named for the job rather than for today's single source. Adding a source means adding a rung to this skill, not a second copy of it. Local repository rules and project-defined visual tolerances outrank the skill.

The standard defaults to raising, not guessing. When a real, complete verification on the full artifact base cannot be run, the subagent returns a `VERIFICATION NOT RUN` blocker report to the caller, and in the main conversation the user is asked. Values are never fabricated and the verdict never rests on partial evidence.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **EXPECTED source** | Only the Figma MCP: the node is resolved from the Figma URL and the reference image is the shared `figma-expected.png` exported by the capture worker. A missing MCP, unresolvable node or missing image gives `VERIFICATION NOT RUN`. The judge never exports it itself and never opens figma.com in a browser |
| **ACTUAL source** | Only this iteration's `actual.png`, `computed-styles.json` and `a11y-snapshot.yml`. Missing or partial artifacts give `VERIFICATION NOT RUN` |
| **No substitutes** | Code reading, type checks, builds and test results never replace verification. The verdict comes only from Figma EXPECTED versus captured ACTUAL |
| **Five categories, one pass** | Structure, Layout, Dimensions, Visual and Components are all completed in one pass, and every difference is reported, not just the first |
| **Measured dimensions** | Dimensions come from `computed-styles.json`, because the accessibility tree carries no CSS. Unmeasured layout is an invalid verification with confidence LOW |
| **Strict PASS gate** | No PASS while any structure, layout or dimension difference above 2px remains. Structure and layout mismatches are CRITICAL and cannot be waived as "close enough" |
| **Three verdicts only** | PASS, FAIL and `VERIFICATION NOT RUN`. No invented waiver states. A difference is excluded only when an explicit user ruling was forwarded in the delegation and is cited verbatim |
| **FAIL needs a fix** | FAIL with an empty `Recommended Fixes` is a contradiction. If nothing is actionable, the verdict is PASS or `VERIFICATION NOT RUN` |
| **Coverage as evidence** | A `null` entry, an `error` entry or a missing entry for an element under verification means it was never measured, so no PASS may rest on it. A measurement of the wrong element is a capture defect, not a difference |
| **Fresh evidence** | Every fix is re-verified on fresh artifacts from a new capture pass. A failing tool call is never repeated more than once |

## Categories and tolerances

The reference `verification-criteria.md` is loaded before every comparison. Categories are compared in a fixed order, Structure first, because a visually similar screen can still be structurally wrong.

| Category | Severity class | Tolerance |
| :-- | :-- | :-- |
| Structure: container hierarchy, nesting depth, grouping, element order, wrapper elements, sections present | CRITICAL | None |
| Layout: flex or grid direction, alignment, distribution, positioning, centering | CRITICAL | None |
| Dimensions: container width, card and panel boundaries, content area versus viewport, width and height constraints, spacing, gaps | CRITICAL | 1 to 2px, only for browser rendering variance |
| Visual: typography, colors, radii, shadows, backgrounds | Listed as CRITICAL in the criteria list, but not one of the CRITICAL categories the PASS gate names (Structure, Layout, Dimensions). Wrong colors or typography are severity Major | Colors and typography: exact match |
| Components: correct variants, design tokens, states | not CRITICAL | not stated as a numeric tolerance |

Severity definitions are Critical (structure or layout differences, wrong component used), Major (dimensions off by more than 2px, wrong colors or typography) and Minor (1 to 2px rendering variance, acceptable). The reference also defines a content and data clarification gate: when everything else is acceptable and the remaining differences are content that may plausibly vary by environment, seed data, locale or user state, the result stays FAIL, the items go under `Clarification Needed`, and they become fixes only after the user confirms. It ends with a checklist to complete before reporting PASS and the confidence levels HIGH, MEDIUM and LOW.

## Artifact contract

```text
specifications/<task-id>/ui-verification/
  figma-expected.png          shared, exported once per item via the Figma MCP
  iteration-<N>/
    actual.png                full-page screenshot of the running app
    computed-styles.json      measured widths, heights, paddings, margins, gaps
    a11y-snapshot.yml         accessibility snapshot: hierarchy, order, grouping
    report.md                 this verification's report, saved by the caller
```

`figma-expected.png` is never duplicated into `iteration-<N>/` and never re-exported per iteration. A cropped reference for a region is a second shared file at the verification root, named `figma-expected-<region>.png`. Evidence for another locale, language or text direction goes in a labeled sibling directory such as `ui-verification/rtl-arabic/` and is judged as its own item. When no task ID exists, the root is `specifications/<page-slug>/ui-verification/`.

## Report format

The reference `report-format.md` defines the report skeleton. Every section is always present, even for `VERIFICATION NOT RUN`, with `UNKNOWN` for values that cannot be known: the literal `## Verification Result: [PASS | FAIL | VERIFICATION NOT RUN]` heading, Component with a confidence level, Sources, Artifact Directory, Artifact Status, Differences, Clarification Needed, Blocker Resolution and Recommended Fixes.

## How it works

1. **Validate inputs:** the Figma URL for the exact component, the pinned dev server URL, the component name and the iteration artifact directory.
2. **Ensure EXPECTED:** use the shared `figma-expected.png` when it is present and the node is unchanged, otherwise return `VERIFICATION NOT RUN`. Extract the design specs to compare from Figma.
3. **Confirm ACTUAL:** the three capture artifacts for this iteration only.
4. **Compare category by category** with the criteria reference.
5. **Report** in the exact skeleton, with expected and actual values for every difference.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| `verification-criteria.md` | About to compare EXPECTED versus ACTUAL, every pass |
| `report-format.md` | Writing any verdict or blocker report |

## Related skills

- [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence): how the ACTUAL artifacts this skill judges are collected.
- [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui): runs one verification pass end to end from the main conversation.

## Source

[`plugins/tsh-product-engineering/skills/verifying-ui/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/verifying-ui/SKILL.md)
