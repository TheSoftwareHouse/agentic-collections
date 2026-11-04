---
title: Auditing Accessibility
sidebar_label: auditing-accessibility
sidebar_position: 1
description: Audits UI against WCAG 2.1 AA and reports each violation with its success criterion, the element, reproduction steps and a fix.
sources:
  - plugins/tsh-product-testing/skills/auditing-accessibility/SKILL.md
  - plugins/tsh-product-testing/skills/auditing-accessibility/references/
sources_hash: "20027c8e56c9486743f477cb464ea2f3863d6f51e345f30ae1c938551e63e569"
---

# Auditing Accessibility

**Plugin:** [`tsh-product-testing`](/docs/plugins/tsh-product-testing/)  
**Invoke:** `/tsh-product-testing:auditing-accessibility` (Claude also loads it when the work matches its description)  
**Used by:** no agent preloads it and no skill delegates to it. [`writing-playwright-e2e-tests`](/docs/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests) and [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) point to it as a related skill.

Audits a page, component or flow against WCAG 2.1 AA and reports findings a developer can fix without further research: the success criterion, the exact element, how to reproduce it, and the concrete correction. WCAG 2.1 AA is the assumed baseline; if the project commits to AAA or a specific regulation, that one applies and the report says which.

## Audit or build

The repository splits accessibility work by outcome. This skill audits what exists. Implementing accessible components, such as a modal, menu, tabs, combobox or form, belongs to [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) in `tsh-stack-frontend`. The skill itself notes that the same criteria apply when building a component: audit late and every finding is a rework.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Applicability** | The repository's own accessibility conventions and any stated conformance target outrank the skill's defaults. Where a component library wraps native elements, the audit reads the rendered HTML, not the JSX |
| **Semantics and structure** | Element choice (`<button>` for actions, `<a href>` for navigation), landmarks with exactly one `<main>`, one `<h1>` and no skipped heading levels, lists, a `<section>` that needs a heading |
| **Keyboard and focus** | Reachability, tab order following DOM order, per-widget key behaviour, focus visibility, programmatic focus on dialog open and close and on route change, focus traps |
| **ARIA correctness** | Only the patterns that need ARIA, the HTML-to-ARIA fallback table, and what never to do, such as `aria-hidden="true"` on anything focusable |
| **Contrast and colour** | 4.5:1 for normal text, 3:1 for large text, component boundaries and informative non-text content, focus indicators at 3:1, both light and dark themes, never colour alone |
| **Zoom and reflow** | 200% text resize (SC 1.4.4) and 400% zoom at 320px width without horizontal scrolling (SC 1.4.10); data tables are the stated exception |
| **RTL** | Logical CSS properties, `dir="rtl"` on the root, flipping directional icons by meaning, testing both directions |
| **Automated scan** | `npx @axe-core/cli <URL>`, violations grouped by impact. The skill states that automated scanning catches roughly a third of what matters and a clean run is never a passing grade |

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Name the WCAG success criterion for every finding |
| MUST | Locate every finding in the source or reproduce it in a browser |
| MUST | Treat any keyboard-inoperable interactive element as a blocker |
| MUST | Prefer native HTML semantics over ARIA in every recommendation |
| MUST | Check both light and dark themes where supported, and both LTR and RTL where the app is localized |
| NEVER | Report information conveyed by colour alone as acceptable, whatever the contrast ratio |
| NEVER | Pad a clean audit with speculation |

## How it works

1. Identify the scope: a component, a page or a whole flow. Ask if unclear.
2. Check semantic structure: elements, landmarks, heading order.
3. Walk through the page with the keyboard.
4. Check focus management.
5. Check ARIA for correctness, conflicts and duplicated native semantics.
6. Check contrast and colour.
7. Check zoom and reflow.
8. Run the automated scan (ask for the URL if there is none), group violations by impact and re-run after fixes.
9. Report, ordered by severity. A repeated violation becomes one finding with a list of affected elements.

The report also states what could not be checked, so silence is not read as a pass. When the audit is written for people outside the team, such as a client report or a conformance statement, the skill applies [`writing-technical-documents`](/docs/plugins/tsh-core/skills/writing-technical-documents) from `tsh-core`.

## References

The skill loads these on demand:

| Reference | Loaded when |
| :-- | :-- |
| Semantics and structure | Auditing markup, or choosing elements for a new component |
| Keyboard and focus | The target has any interactive control, dialog or custom widget. The skill says to read it before auditing any interactive control |
| ARIA patterns | Considering an ARIA attribute, or auditing existing ARIA |
| Contrast, reflow and RTL | The change is visual, or the app is localized |

## Related skills

- [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility): the implementation-side counterpart in `tsh-stack-frontend`.
- [`writing-playwright-e2e-tests`](/docs/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests): `getByRole` resolves against the same accessibility tree an audit examines, so a locator that cannot find an element is itself a signal.

## Source

[`plugins/tsh-product-testing/skills/auditing-accessibility/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-testing/skills/auditing-accessibility/SKILL.md)
