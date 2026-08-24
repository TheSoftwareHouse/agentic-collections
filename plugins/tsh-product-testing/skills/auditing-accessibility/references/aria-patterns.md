# ARIA patterns

The first rule of ARIA is not to use it. Native HTML carries the semantics already, and
incorrect ARIA is worse than none — it actively lies to assistive technology, which
then reports something that is not there.

Reach for it only where HTML cannot express the pattern.

## Patterns that genuinely need it

- **Icon-only buttons** — `aria-label="Close"`. Without a name, the control announces as
  just "button".
- **Expandable triggers** — `aria-expanded="true|false"` on the *trigger*, not the panel.
  Must be kept in sync with actual state; a stale value is a lie.
- **Live updates** — `aria-live="polite"` for non-urgent changes (results refreshed,
  filter applied), `aria-live="assertive"` only for genuinely urgent ones (session
  expiring, critical error). Assertive interrupts whatever is being read, so overuse
  makes an interface hostile.
- **Dialogs** — `aria-modal="true"`, `aria-labelledby` pointing at the title,
  `aria-describedby` at the description.
- **Form errors** — `aria-invalid="true"` on the field, `aria-describedby` pointing at
  the message, and the error container as `role="alert"` (or `aria-live="assertive"`)
  so it announces on appearance.
- **Loading states** — container with `role="status"`. That role already implies
  `aria-live="polite"`; adding both is redundant.
- **Current page** — `aria-current="page"` on the active nav link.
- **Progress** — `role="progressbar"` with `aria-valuenow`, `aria-valuemin`,
  `aria-valuemax`. Prefer native `<progress>` where it fits.

## The live-region gotcha

**A live region must exist in the DOM before the content it announces arrives.** Adding
the container and its text in the same render announces nothing — the region has to be
present and empty, then populated.

This is the most common reason "the error message has `aria-live` and still does not
announce", and it is invisible in a code review that only checks the attribute is there.

## HTML first, ARIA as fallback

| Need | HTML | ARIA fallback |
| :-- | :-- | :-- |
| Button | `<button>` | `role="button"` + `tabindex="0"` + Enter/Space handlers |
| Link | `<a href>` | `role="link"` (rare) |
| Navigation region | `<nav>` | `role="navigation"` |
| Main content | `<main>` | `role="main"` |
| Dialog | `<dialog>` | `role="dialog"` + `aria-modal="true"` |
| Expand/collapse | `<details>`/`<summary>` | `aria-expanded` on trigger |
| Progress | `<progress>` | `role="progressbar"` + values |
| Live update | — | `aria-live` on a pre-existing container |
| Icon-only button name | — | `aria-label` |
| Form error | — | `aria-invalid` + `aria-describedby` |
| Current page | — | `aria-current="page"` |

The right column is a fallback, not an alternative. Choosing it when the left column is
available is a finding.

## Never

- **`role="button"` on a `<div>`** where a `<button>` would do. Even done fully — role,
  tabindex, both key handlers — it reimplements for free what the platform provides,
  and one forgotten piece breaks it.
- **ARIA duplicating native semantics** — `role="heading"` on an `<h2>`,
  `role="list"` on a `<ul>`. Noise at best; in some combinations it overrides correct
  semantics with worse ones.
- **`aria-label` on non-interactive, non-landmark elements.** It is widely ignored on a
  plain `<div>` or `<span>`, so the name silently does not exist.
- **`aria-hidden="true"` on anything focusable.** It creates a control that is reachable
  by keyboard but invisible to screen readers — the worst of both.
- **Attributes referencing an ID that does not exist.** `aria-describedby` pointing at a
  removed element fails silently, so check the target resolves.

## Auditing existing ARIA

1. Open the accessibility tree in devtools, not the source. Verify the computed role,
   name and state are what was intended.
2. Check every `aria-expanded`, `aria-checked`, `aria-selected` and `aria-current`
   actually tracks state, rather than being set once at render.
3. Check every ID reference resolves.
4. Look for ARIA that could be deleted by switching to the native element — that is
   usually the best available fix.
