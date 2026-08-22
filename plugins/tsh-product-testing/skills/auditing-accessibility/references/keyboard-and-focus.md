# Keyboard and focus

Where the blocking findings are. A keyboard-inoperable control excludes people
outright, so it is never a minor issue.

## Reachability

Native interactive elements are focusable by default. A custom interactive element needs
`tabindex="0"`.

**Avoid `tabindex` above 0.** A positive value jumps to the front of the page's tab
order, ahead of everything native, producing a sequence nobody can predict — and one
positive value anywhere reorders the whole page.

Use `tabindex="-1"` for elements that should be focusable programmatically but not
tabbable — a dialog container, or a heading you move focus to after a route change.

## Tab order

Must follow visual and logical reading order. It derives from DOM order, so any CSS that
reorders visually — `flex-direction: row-reverse`, `order`, `grid-area`, absolute
positioning — desynchronizes the two. That is the usual cause of an order that looks
fine and tabs wrongly.

Fix by reordering the DOM, not by adding `tabindex`.

## Per-widget key behaviour

| Component | Expected keys |
| :-- | :-- |
| Button | Enter and Space activate |
| Link | Enter activates |
| Menu | Arrows move between items, Escape closes, Enter selects |
| Tabs | Left/Right switch tabs, Tab leaves the tab group |
| Dialog / modal | Tab trapped inside, Escape closes |
| Accordion | Enter/Space toggles, arrows move between headers |
| Combobox | Arrows navigate options, Enter selects, Escape closes |
| Slider | Arrows adjust, Home/End for min and max |

The pattern that matters: **inside a composite widget, arrows move and Tab leaves.**
A tab group where Tab cycles through every tab, or a menu with no arrow support, is a
finding even though every item is technically reachable.

## Focus visibility

**Never remove the focus outline without a visible replacement.** `outline: none` with
nothing in its place is among the most damaging one-line accessibility regressions —
sighted keyboard users lose all sense of position.

A custom focus style needs at least 3:1 contrast against adjacent colours (SC 1.4.11).
Prefer `:focus-visible` so pointer users do not see rings while keyboard users do.

Check focus visibility against every background the element appears on — a white ring is
invisible on a light card.

## Programmatic focus

Move focus when context changes:

- **Dialog opens** → focus the first focusable element inside, or the dialog container
- **Dialog closes** → return focus to the element that opened it. Skipping this drops
  the user back at the document start, losing their place entirely
- **Route change** in a single-page app → focus the new page's heading or main content.
  Without this, navigation is silent to a screen reader and focus stays on a link that
  no longer exists
- **Content added dynamically** → focus it, or announce it via `aria-live`

## Focus traps

A dialog must trap Tab inside itself while open — Tab from the last element returns to
the first, and Shift+Tab from the first goes to the last. Everything behind it should be
inert so it cannot receive focus at all.

Native `<dialog>` with `showModal()` gives you the trap, the inertness, and Escape for
free. Prefer it, or the `inert` attribute, over hand-written key handling.

## The walkthrough

1. Tab from the top. Is every interactive element reachable?
2. Is the order logical?
3. Is focus visible at every stop, on every background?
4. Does Escape dismiss overlays?
5. Do arrows work inside composite widgets?
6. Does opening and closing a dialog move focus in and back?
7. Does a route change move focus?
8. Can you complete the primary task without touching the mouse?

Step 8 is the real test. Everything else is diagnosis.
