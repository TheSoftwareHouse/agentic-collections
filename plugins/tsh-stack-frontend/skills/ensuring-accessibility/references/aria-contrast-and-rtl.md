# ARIA, contrast, and RTL reference

Detail tables for the `ensuring-accessibility` process.

## Keyboard behavior per widget

| Component | Keyboard behavior |
| --- | --- |
| Button | Enter + Space to activate |
| Menu | Arrow keys to navigate items, Escape to close, Enter to select |
| Tabs | Left/Right arrows to switch tabs, Tab to leave the tab group |
| Dialog / Modal | Tab trapped inside, Escape to close |
| Accordion | Enter/Space to expand/collapse, Arrow keys between headers |
| Combobox | Arrow keys to navigate options, Enter to select, Escape to close |

## ARIA usage quick reference

| Need | HTML solution | ARIA fallback (only if HTML insufficient) |
| --- | --- | --- |
| Button | `<button>` | `role="button"` + `tabindex="0"` + key handlers |
| Link | `<a href>` | `role="link"` (rare) |
| Navigation region | `<nav>` | `role="navigation"` |
| Main content | `<main>` | `role="main"` |
| Dialog | `<dialog>` | `role="dialog"` + `aria-modal="true"` |
| Live update | — | `aria-live="polite"` on the container |
| Expand/collapse | `<details>` / `<summary>` | `aria-expanded` on the trigger |
| Icon-only button | — | `aria-label` on the button |
| Form error | — | `aria-invalid` + `aria-describedby` |
| Current page | — | `aria-current="page"` on the nav link |
| Progress | `<progress>` | `role="progressbar"` + `aria-valuenow`/`-min`/`-max` |

Notes:

- `aria-live="polite"` for non-urgent updates (data refreshed, filter applied);
  `aria-live="assertive"` for urgent ones (session expiring, critical error).
- `role="status"` implicitly sets `aria-live="polite"` — don't add both.
- Form errors: `aria-invalid="true"` on the field, `aria-describedby` pointing at
  the error element, and the error container with `role="alert"` (or
  `aria-live="assertive"`) for immediate announcement.

## Contrast requirements

| Element | Minimum ratio | Examples |
| --- | --- | --- |
| Normal text (< 24px) | 4.5:1 | Body text, labels, captions, small links |
| Large text (≥ 24px / 18pt, or ≥ 19px / 14pt bold) | 3:1 | Headings, large labels, prominent links |
| Interactive component boundaries | 3:1 | Button borders, input outlines, toggle tracks |
| Non-text content conveying information | 3:1 | Status icons, chart segments, badges |

Additional rules:

- Focus indicators meet 3:1 against the background.
- Test both light and dark themes when the application supports them.
- Disabled states must be visually distinguishable but are exempt from contrast
  minimums under WCAG 2.1 AA.
- Touch targets of 44×44 CSS pixels are recommended best practice (not a 2.1 AA
  requirement).

## Zoom and reflow

- At 200% zoom, text resizes without loss of content or functionality (SC 1.4.4).
- At 400% zoom (320px viewport width), content reflows without horizontal
  scrolling (SC 1.4.10).

## RTL / bidirectional text support

| Rule | Description |
| --- | --- |
| Use logical CSS properties | `margin-inline-start` instead of `margin-left`; `padding-inline-end` instead of `padding-right` |
| Let the layout engine handle direction | Set `dir="rtl"` on the root; avoid manual transforms for standard layout |
| Icons may need flipping | Directional icons (arrows, progress bars) may need `transform: scaleX(-1)` in RTL |
| Test both directions | Verify layout, alignment, and text truncation in both LTR and RTL |
