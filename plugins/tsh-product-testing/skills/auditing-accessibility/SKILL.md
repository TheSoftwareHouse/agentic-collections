---
name: auditing-accessibility
description: "Audits UI against WCAG 2.1 AA and reports violations with their success criterion: semantic structure and heading order, keyboard operability and focus management, ARIA correctness, colour contrast, text resize and reflow, and axe-core automated scanning. Use when auditing a page or component for accessibility or triaging axe output. Building accessible components is tsh-stack-frontend's ensuring-accessibility."
when_to_use: "Trigger on: auditing a page, component or flow for accessibility, an a11y or WCAG compliance check before release, interpreting or triaging axe-core output, keyboard navigation or focus-trap problems, whether an ARIA attribute is correct or needed, colour contrast ratios, screen-reader announcement of errors or dynamic content, text resize and 400% reflow, or RTL and bidirectional layout support of an existing page. Implementing an accessible modal, menu, tabs, combobox or form is tsh-stack-frontend's ensuring-accessibility."
---

# Auditing Accessibility

Report findings a developer can fix without further research: the success criterion, the
exact element, how to reproduce it, and the concrete correction. The same criteria apply
when building a component — audit late and every finding is a rework.

## Applicability and Precedence

The repository's own accessibility conventions and any stated conformance target
outrank this skill's defaults. **WCAG 2.1 AA is the baseline assumed here**; if the
project commits to AAA or to a specific regulation, apply that and say which.

Where a component library wraps native elements, audit the **rendered HTML**, not the
JSX. A `<Button>` that renders a `<div>` is a finding no source read will catch.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Name the WCAG success criterion for every finding — "SC 1.4.3 Contrast (Minimum)", not "poor contrast". Without it a finding cannot be prioritized or verified. |
| MUST | Locate every finding in the source or reproduce it in a browser. A violation you have not seen is a hypothesis. |
| MUST | Treat any keyboard-inoperable interactive element as a blocker, not a nit. It excludes users entirely rather than inconveniencing them. |
| MUST | Prefer native HTML semantics over ARIA in every recommendation. Reach for ARIA only where HTML cannot express the pattern. |
| MUST | Check both light and dark themes where the application supports them, and both LTR and RTL where it is localized. |
| NEVER | Report information conveyed by colour alone as acceptable, whatever the contrast ratio. |
| NEVER | Pad a clean audit with speculation. State plainly that nothing was found. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Semantics and structure](./references/semantics-and-structure.md) | Auditing markup, or choosing elements for a new component | Element selection, landmarks, heading hierarchy, lists, when a wrapper hides a problem |
| [Keyboard and focus](./references/keyboard-and-focus.md) | The target has any interactive control, dialog, or custom widget | Tab order, per-widget key behaviour, focus visibility, programmatic focus moves |
| [ARIA patterns](./references/aria-patterns.md) | Considering an ARIA attribute, or auditing existing ARIA | The patterns that genuinely need ARIA, the HTML-to-ARIA fallback table, and what never to do |
| [Contrast, reflow and RTL](./references/contrast-reflow-and-rtl.md) | The change is visual, or the app is localized | Contrast ratios by element type, zoom and reflow criteria, logical CSS properties |

Read [keyboard-and-focus.md](./references/keyboard-and-focus.md) before auditing any
interactive control — keyboard operability is where the blocking findings are.

## Principles

- **Semantic HTML first.** `<button>` for actions, `<a href>` for navigation, `<nav>`
  and `<main>` for regions. Native semantics are free, reliable, and need no ARIA.
- **Keyboard is mandatory.** Every mouse interaction must have a keyboard equivalent.
  Tab, Escape, Enter, Space and the arrow keys are the whole vocabulary.
- **Never colour alone.** Error states need an icon or text as well as red. Status
  indicators need a label, not just a coloured dot.

## Audit procedure

Copy this checklist and track progress:

```text
Accessibility audit:
- [ ] 1. Scope identified
- [ ] 2. Semantic structure
- [ ] 3. Keyboard walkthrough
- [ ] 4. Focus management
- [ ] 5. ARIA correctness
- [ ] 6. Contrast and colour
- [ ] 7. Zoom and reflow
- [ ] 8. Automated scan
- [ ] 9. Findings reported
```

1. **Identify the scope** — a component, a page, or a whole flow. Ask if it is unclear
   rather than auditing the wrong thing thoroughly.
2. **Semantic structure** — elements, landmarks, heading order. See
   [semantics-and-structure.md](./references/semantics-and-structure.md).
3. **Keyboard walkthrough** — Tab through everything. Is each interactive element
   reachable, is the order logical, is focus always visible, does Escape dismiss
   overlays, do arrows work where the pattern expects them?
4. **Focus management** — does focus move into a dialog on open and return to the
   trigger on close; does a route change move focus; is added content announced?
5. **ARIA** — correct, non-conflicting, and not duplicating native semantics.
6. **Contrast** — against [contrast-reflow-and-rtl.md](./references/contrast-reflow-and-rtl.md).
7. **Zoom and reflow** — 200% text resize (SC 1.4.4) and 400% zoom at 320px width
   without horizontal scrolling (SC 1.4.10).
8. **Automated scan** — `npx @axe-core/cli <URL>`. Ask for the URL if you do not have
   one. Group violations by impact (critical, serious, moderate, minor) and report rule
   ID, impact, affected elements and fix. Re-run after fixes.
9. **Report**, ordered by severity.

Automated scanning catches roughly a third of what matters and nothing about focus
order, announcement quality, or whether a label makes sense. A clean axe run is a
starting point, never a passing grade — say so when reporting one.

## Checklist

```text
- [ ] Semantic elements used (button, nav, main, …)
- [ ] One h1 per page, no skipped heading levels
- [ ] Every interactive element keyboard-reachable
- [ ] Focus visible everywhere, 3:1 against adjacent colours
- [ ] Tab order matches visual order
- [ ] Dialogs trap focus and restore it on close
- [ ] Icon-only buttons have an accessible name
- [ ] Form fields have visible labels, not placeholder-only
- [ ] Form errors announced (role="alert" or aria-live)
- [ ] Error states use icon or text as well as colour
- [ ] Contrast 4.5:1 normal text, 3:1 large text and UI boundaries
- [ ] Landmarks present (header, main, nav, footer)
- [ ] Text resizable to 200% without loss (SC 1.4.4)
- [ ] Reflows at 400% / 320px without horizontal scroll (SC 1.4.10)
```

## Reporting

Order findings by severity. For each: the success criterion, the element, reproduction
steps, and the fix. Consolidate a repeated violation into one finding with the list of
affected elements rather than one finding per instance.

State clearly what you could not check — a screen-reader announcement you could not
verify, a theme you could not reach — so nobody reads silence as a pass.

When the audit is written up for people outside the team — a client report, a
conformance statement — apply `/tsh-core:writing-technical-documents` to it. An audit
that leads with methodology instead of findings does not get read.

## Related skills in this plugin

- [Writing Playwright E2E tests](../writing-playwright-e2e-tests/SKILL.md) —
  `getByRole` resolves against the same accessibility tree an audit examines, so a
  locator that cannot find an element is itself a signal
