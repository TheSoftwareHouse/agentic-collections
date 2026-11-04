---
title: Ensuring Accessibility
sidebar_label: ensuring-accessibility
sidebar_position: 2
description: WCAG 2.1 AA implementation patterns applied while building frontend components, from semantic HTML and keyboard support to ARIA, contrast and axe-core.
sources:
  - plugins/tsh-stack-frontend/skills/ensuring-accessibility/SKILL.md
  - plugins/tsh-stack-frontend/skills/ensuring-accessibility/references/
sources_hash: "bfaf0f75fd6a40187a714aa24771f1e9f9632685944fadf668a1454d0ffc1f24"
---

# Ensuring Accessibility

**Plugin:** [`tsh-stack-frontend`](/docs/plugins/tsh-stack-frontend/)  
**Invoke:** `/tsh-stack-frontend:ensuring-accessibility` (Claude also loads it when the work matches its description)  
**Used by:** [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) in `tsh-product-engineering`, which loads it by name when `tsh-stack-frontend` is installed. [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) lists it as a related skill

WCAG 2.1 AA compliance patterns for building inclusive frontend interfaces with proper semantic markup, keyboard navigation, focus management and screen reader support, applied while implementing rather than audited afterwards. The project's own component library and its accessible primitives come first; the skill says to verify that their rendered HTML matches expectations rather than re-implementing them.

## Build or audit

The repository splits accessibility work by outcome. This skill is for **implementing** accessible components. **Auditing** an existing page for violations is [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility) in `tsh-product-testing`, which may not be installed. When it is not, the skill says to name the gap rather than improvise an audit. Component composition itself is [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend).

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Semantic HTML** | `<button>` for actions, `<a href>` for navigation, landmarks (`header`, `nav`, `main`, `aside`, `footer`), one `<h1>` per page with no skipped levels, `section` with a heading, `ul`/`ol`/`dl` for lists. Inspect the rendered HTML when a component library wraps these |
| **Keyboard** | Every mouse interaction has a keyboard equivalent, tab order follows visual order, custom interactive elements get `tabindex="0"` and explicit key handlers, overlays close on Escape. Per-widget key maps for button, menu, tabs, dialog, accordion and combobox |
| **Focus** | Never `outline: none` without a replacement of at least 3:1 contrast, never `tabindex` above 0. Focus moves into an opened modal, back to the trigger on close, and to the heading or main content on route change |
| **ARIA** | Only where HTML falls short: `aria-label` for icon-only buttons, `aria-expanded`, `aria-live`, `aria-modal` with `aria-labelledby`, `aria-invalid` with `aria-describedby` and `role="alert"` for form errors, `role="status"` for loading, `aria-current="page"`, `role="progressbar"` |
| **Contrast and colour** | 4.5:1 for normal text, 3:1 for large text, interactive component boundaries and informative non-text content, focus indicators at 3:1, both themes when the app has light and dark. Information is never conveyed by colour alone |
| **Zoom and reflow** | 200% text resize (SC 1.4.4) and reflow at 400% zoom, 320px width, without horizontal scrolling (SC 1.4.10) |
| **RTL** | Logical CSS properties, `dir="rtl"` on the root, flipping directional icons where needed, testing both directions |
| **Verification** | Keyboard walkthrough, screen-reader announcements, zoom, the browser accessibility tree and `npx @axe-core/cli <URL>` with violations grouped by impact |

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Start with the correct HTML element; reach for ARIA only when HTML cannot express the pattern |
| MUST | Make every mouse interaction available to the keyboard. Missing keyboard support is a blocker |
| NEVER | Remove the focus outline without a visible replacement of at least 3:1 contrast, or use a `tabindex` greater than 0 |
| NEVER | Convey information through colour alone |
| MUST | Meet the contrast minimums |
| MUST | Move focus when context changes and announce dynamic content via `aria-live` |
| NEVER | Add ARIA that duplicates native semantics, or `aria-label` on non-interactive, non-landmark elements |

## How it works

1. **Choose semantic elements**, and inspect the rendered HTML when a library wraps them.
2. **Implement keyboard navigation** with per-widget key maps, visible focus and programmatic focus management.
3. **Add ARIA where HTML falls short**, using the pattern tables in the reference.
4. **Verify colour and contrast**, including focus indicators and both themes. Disabled states must be distinguishable but are exempt from contrast minimums.
5. **Test with assistive technology**: keyboard walkthrough, screen-reader announcements, zoom, the accessibility tree, and axe-core, re-run after fixes. The skill asks for the URL if it is unknown.

The skill ends with a twelve-item accessibility checklist covering the same ground.

## References

| Reference | Loaded when |
| :-- | :-- |
| ARIA, contrast and RTL | Picking an ARIA pattern, checking exact contrast ratios or keyboard maps, or supporting RTL |

It holds the ARIA quick-reference table, per-widget keyboard behaviour, contrast tables, zoom and reflow, and the RTL rules. It also states that touch targets of 44×44 CSS pixels are recommended best practice and not a WCAG 2.1 AA requirement.

## Related skills

- [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend): the component composition these patterns apply to.
- [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility): auditing an existing page, in `tsh-product-testing`.

## Source

[`plugins/tsh-stack-frontend/skills/ensuring-accessibility/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-frontend/skills/ensuring-accessibility/SKILL.md)
