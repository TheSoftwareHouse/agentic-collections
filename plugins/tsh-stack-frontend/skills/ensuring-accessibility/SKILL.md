---
name: ensuring-accessibility
description: "WCAG 2.1 AA implementation patterns for building accessible frontend components: semantic HTML first, keyboard navigation and focus management, ARIA only where HTML falls short, contrast minimums, and an axe-core verification step. Use when implementing accessible components, adding keyboard or screen-reader support, or building inclusive forms and interactive widgets."
when_to_use: "Trigger on: implementing a component that must be accessible, keyboard navigation or focus management work, choosing between semantic HTML and ARIA, form error announcements, color-contrast decisions during implementation, or RTL support. Auditing an existing page for violations is tsh-product-testing's auditing-accessibility; component composition itself is implementing-frontend."
---

# Ensuring Accessibility

WCAG 2.1 AA compliance patterns for building inclusive frontend interfaces with
proper semantic markup, keyboard navigation, focus management, and screen reader
support — applied while implementing, not audited afterwards.

## Applicability and Precedence

Local repository rules outrank this skill: the project's component library and its
accessible primitives come first — verify their rendered HTML matches expectations
rather than re-implementing them.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Start with the correct HTML element: `<button>` for actions, `<a href>` for navigation, `<nav>`/`<main>`/`<header>`/`<footer>` landmarks, one `<h1>` per page with no skipped heading levels. Native semantics are free and reliable; reach for ARIA only when HTML cannot express the pattern. |
| MUST | Make every mouse interaction available to the keyboard: Tab order follows visual order, custom interactive elements get `tabindex="0"` and explicit key handlers, overlays close on Escape. Missing keyboard support is a blocker, not a nice-to-have. |
| NEVER | Remove the focus outline (`outline: none`) without a visible replacement of at least 3:1 contrast, or use a `tabindex` greater than 0. |
| NEVER | Convey information through color alone: error states need an icon or text besides the red border; status indicators need labels, not just colored dots. |
| MUST | Meet contrast minimums: 4.5:1 for normal text, 3:1 for large text, interactive component boundaries, and informative non-text content. |
| MUST | Move focus when context changes: into an opened modal, back to the trigger on close, to the heading or main content on route change; announce dynamic content via `aria-live`. |
| NEVER | Add ARIA that duplicates native semantics (`role="button"` on a `<div>` instead of `<button>`, `role="heading"` on an `<h2>`), or `aria-label` on non-interactive, non-landmark elements. |

## Implementation Process

1. **Choose semantic elements** — interactive (`button`, `a`, form controls),
   landmarks (`header`, `nav`, `main`, `aside`, `footer`), structure (`article`,
   `section` with a heading, `details`/`summary`), heading hierarchy, and `ul`/`ol`/
   `dl` for lists. When the component library wraps these, inspect the rendered HTML.
2. **Implement keyboard navigation** — per-widget key maps (menu: arrows + Escape +
   Enter; tabs: left/right arrows; dialog: focus trap + Escape; combobox: arrows +
   Enter + Escape), visible focus, programmatic focus management on context changes.
3. **Add ARIA where HTML falls short** — icon-only buttons (`aria-label`),
   expandables (`aria-expanded`), live updates (`aria-live="polite"`/`"assertive"`),
   dialogs (`aria-modal`, `aria-labelledby`), form errors (`aria-invalid` +
   `aria-describedby` + `role="alert"`), loading (`role="status"`), current nav page
   (`aria-current="page"`), progress (`role="progressbar"` + `aria-valuenow`).
   Full pattern tables in the reference below.
4. **Verify color and contrast** — the minimums above, focus indicators at 3:1,
   both themes when the app has light and dark, disabled states distinguishable
   (contrast-exempt under WCAG).
5. **Test with assistive technology** — keyboard walkthrough (everything reachable,
   logical order, visible focus, Escape dismisses), screen-reader announcements
   (headings, landmarks, labels, live regions, form errors), zoom (200% text resize,
   400% reflow without horizontal scroll), the browser accessibility tree, and
   automated axe-core: `npx @axe-core/cli <URL>` (ask for the URL if unknown),
   violations grouped by impact, re-run after fixes.

## Accessibility Checklist

```text
- [ ] Semantic HTML elements used (button, nav, main, …)
- [ ] One h1 per page, logical heading hierarchy (no skipped levels)
- [ ] All interactive elements keyboard-navigable, focus always visible
- [ ] Tab order follows visual/logical layout
- [ ] Modal/dialog traps focus and returns it on close
- [ ] Icon-only buttons have aria-label
- [ ] Form fields have visible labels (not placeholder-only)
- [ ] Form errors announced (role="alert" or aria-live)
- [ ] Error states use icon/text in addition to color
- [ ] Contrast: 4.5:1 normal text / 3:1 large text and boundaries
- [ ] ARIA landmarks present (header, main, nav, footer)
- [ ] Text resizable to 200%; content reflows at 400% zoom (SC 1.4.4, 1.4.10)
```

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [ARIA, contrast and RTL](./references/aria-contrast-and-rtl.md) | Picking an ARIA pattern, checking exact contrast ratios or keyboard maps, or supporting RTL | The ARIA quick-reference table, per-widget keyboard behavior, contrast tables, RTL/bidirectional rules |

## Related Skills

- [`implementing-frontend`](../implementing-frontend/SKILL.md) — the component
  composition these patterns apply to.
- Auditing an existing page for violations is `auditing-accessibility` in
  `tsh-product-testing`, which may not be installed — name the gap rather than
  improvising an audit here.
