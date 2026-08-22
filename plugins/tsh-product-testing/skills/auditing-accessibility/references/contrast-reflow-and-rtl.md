# Contrast, reflow and RTL

## Contrast

| Element | Minimum ratio | Examples |
| :-- | :-- | :-- |
| Normal text, under 24px | 4.5:1 | Body text, labels, captions, small links |
| Large text — 24px+ / 18pt, or 19px+ / 14pt bold | 3:1 | Headings, large labels, prominent links |
| Interactive component boundaries | 3:1 | Button borders, input outlines, toggle tracks |
| Non-text content conveying information | 3:1 | Status icons, chart segments, badges |

Rules that go with the numbers:

- **Never colour alone** (SC 1.4.1). Error states need an icon or text as well as red;
  status needs a label, not just a coloured dot. This holds at any contrast ratio — it
  is a separate criterion, and the most frequently missed one.
- **Focus indicators need 3:1** against the background they sit on (SC 1.4.11), checked
  against every background the element appears over.
- **Both themes.** Where light and dark are supported, both are in scope; a palette
  passing in one commonly fails in the other.
- **Disabled controls are exempt** from contrast minimums, but must still be visually
  distinguishable from enabled ones.
- **Text over an image or gradient** needs the worst-case region measured, not an
  average — a scrim or solid backing is usually the fix.

Placeholder text is real text and must meet 4.5:1. Default browser placeholder styling
often does not, and it should not be the only label regardless.

## Zoom and reflow

Two distinct criteria, commonly conflated:

- **SC 1.4.4 Resize Text** — text scales to 200% with no loss of content or
  functionality. Breaks when a container has a fixed pixel height and clips its text.
- **SC 1.4.10 Reflow** — at 400% zoom, equivalent to a 320px viewport width, content
  reflows into a single column with **no horizontal scrolling**. Breaks on fixed-width
  containers, wide tables, and `min-width` on a layout wrapper.

Test by zooming a desktop browser, not by resizing to a mobile breakpoint — they trigger
different code paths, and a responsive layout can still fail reflow at 400%.

Data tables are the standard exception: they may scroll horizontally, since a table is
one of the content types the criterion exempts.

**Touch targets of 44×44 CSS pixels are a best practice, not a WCAG 2.1 AA
requirement.** Recommend it; do not report it as a conformance failure.

## RTL and bidirectional text

| Rule | Detail |
| :-- | :-- |
| Use logical CSS properties | `margin-inline-start` over `margin-left`, `padding-inline-end` over `padding-right`, `inset-inline-start` over `left` |
| Let the layout engine flip | Set `dir="rtl"` on the root; avoid manual transforms for standard layout |
| Flip directional icons | Arrows, chevrons, progress and back buttons need `transform: scaleX(-1)` or an RTL variant — a mirrored *logo* is a bug, so flip by meaning, not blanket |
| Do not flip everything | Media controls, clock faces and phone numbers stay LTR |
| Test both directions | Layout, alignment and text truncation all differ; truncation is where RTL bugs cluster |

Logical properties are the whole strategy. A stylesheet written with physical properties
needs a per-rule audit to support RTL at all, whereas one written logically works in
both directions with no extra rules.

Mixed-direction content — an English product name inside Arabic text — needs the
surrounding markup to declare its direction, or punctuation lands on the wrong side.
