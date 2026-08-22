# Semantics and structure

Start from the correct element. Every ARIA attribute added later is compensating for a
choice made here.

## Element selection

**Interactive**

- `<button>` — actions: submit, toggle, open a menu
- `<a href>` — navigation to another page or location
- `<input>`, `<select>`, `<textarea>` — form data entry

The button-versus-link distinction is not cosmetic: a link is expected to navigate and
responds to Enter, a button acts and responds to Enter and Space. Getting it wrong
breaks keyboard expectations and screen-reader announcement together.

**Landmarks**

- `<header>` — page or section header
- `<nav>` — navigation region
- `<main>` — primary content, exactly one per page
- `<aside>` — tangentially related content
- `<footer>` — page or section footer

Landmarks are how screen-reader users skip past navigation instead of tabbing through
it. A page with no `<main>` has no "skip to content" target.

**Structure**

- `<article>` — self-contained composition
- `<section>` — thematic grouping, and it **must** have a heading; a `<section>` with no
  accessible name is just a `<div>`
- `<details>` / `<summary>` — native expand and collapse, with keyboard behaviour free

**Lists**

- `<ul>` / `<ol>` for collections — the count is announced, which orients the user
- `<dl>` for key-value pairs

## Heading hierarchy

- One `<h1>` per page
- Nest logically: `h2` → `h3` → `h4`
- Never skip a level (`h2` → `h4`)

Headings are the primary navigation mechanism for screen-reader users — many jump by
heading before reading anything. A page whose headings were chosen for font size rather
than structure is unnavigable, and this is one of the most common real findings.

Check the order as a flat list, not visually. A correct-looking page frequently has a
broken sequence once styling is ignored.

## Audit the rendered output

Where a component library wraps native elements, **inspect the rendered HTML**, not the
source. `<Button>` rendering `<div onClick>` produces an element that is not focusable,
not announced as a button, and does not respond to Space — and nothing in the JSX
suggests it.

Open devtools, or use the accessibility tree. Roles come from what shipped.

## Common findings

| Finding | Correction |
| :-- | :-- |
| `<div onClick>` as a button | `<button>`; if it must stay a div, `role="button"` plus `tabindex="0"` plus Enter and Space handlers |
| Heading levels chosen for size | Correct level, sized with CSS |
| No `<main>` | Wrap primary content |
| `<section>` with no heading | Add a heading, or use `<div>` |
| List markup faked with divs | `<ul>`/`<li>`, so the count is announced |
| Placeholder used as the only label | A visible `<label>`; placeholders vanish on input and are not reliably announced |
| Icon-only button with no name | `aria-label`, or visually hidden text |
| Decorative image with descriptive alt | `alt=""` so it is skipped |
