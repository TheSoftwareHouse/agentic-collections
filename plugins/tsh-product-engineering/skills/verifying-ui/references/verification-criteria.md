# Verification criteria

Compare in this fixed order and **complete every category regardless of findings** —
the goal is one complete difference list so the engineer fixes everything in a single
iteration. A visually similar screen can still be structurally wrong, which is why
Structure comes first.

1. **Structure** (CRITICAL)
2. **Layout** (CRITICAL)
3. **Dimensions** (CRITICAL)
4. **Visual** (CRITICAL)
5. **Components**

## Structure (CRITICAL)

| Check | Description |
| --- | --- |
| Container hierarchy | Does DOM structure match Figma's layer hierarchy? |
| Nesting depth | Are elements nested at the same level as in Figma? |
| Grouping | Are related elements grouped together as in design? |
| Element order | Is the visual order of elements the same? |
| Wrapper elements | Are there extra/missing wrapper divs that change layout? |
| Sections present | Are ALL sections from Figma present in the implementation? |

## Layout (CRITICAL)

| Check | Description |
| --- | --- |
| Flex/Grid direction | row vs column, wrap behavior |
| Alignment | justify-content, align-items values |
| Distribution | How space is distributed between elements |
| Positioning | relative, absolute, fixed — matches design intent? |
| Centering | Is content centered as in design? |

## Dimensions (CRITICAL)

| Check | Description |
| --- | --- |
| Container width | max-width, fixed width constraints |
| Card/panel boundaries | Does the card have the same width as in Figma? |
| Content area vs viewport | Ratio of content width to available space |
| Width/Height | Fixed, percentage, auto, min/max constraints |
| Spacing | Padding, margin, gap between elements |
| Gaps | Space between flex/grid children |

> **WARNING**: The accessibility tree does NOT contain CSS dimensions. A full-width
> container and a narrow centered one look identical in it. Measure actual computed
> styles from `computed-styles.json` to detect width and sizing differences.

## Visual

| Check | Description |
| --- | --- |
| Typography | font-family, size, weight, line-height, letter-spacing |
| Colors | Text, background, border colors |
| Radii | border-radius values |
| Shadows | box-shadow, drop-shadow |
| Backgrounds | Solid, gradient, image |

## Components

| Check | Description |
| --- | --- |
| Correct variants | Is the right variant of a component used? |
| Design tokens | Are correct tokens used (not hardcoded values)? |
| States | hover, focus, active, disabled states |

## Tolerances

| Category | Tolerance | Notes |
| --- | --- | --- |
| Structure | **None** | Any structural difference = FAIL |
| Layout direction | **None** | row vs column must match exactly |
| Alignment | **None** | Centering, justify, align must match |
| Dimensions | **1–2px** | Only for browser rendering variance |
| Colors | **Exact match** | Must use correct design tokens |
| Typography | **Exact match** | Font properties must match |
| Spacing | **1–2px** | Only for browser rendering variance |

## Severity definitions

| Severity | Description | Action |
| --- | --- | --- |
| **Critical** | Structure/layout differences, wrong component used | Must fix immediately |
| **Major** | Dimensions off by >2px, wrong colors/typography | Must fix before merge |
| **Minor** | 1–2px browser rendering variance | Acceptable, document if recurring |

## Content/data clarification gate

Use only when structure, layout, dimensions, visual styling, and component usage are
otherwise acceptable, and the remaining differences are limited to content or data
that may plausibly vary by environment, seed data, locale, or user state:

1. Summarize the remaining content/data differences clearly.
2. Ask whether those values are intentionally environment-specific or whether the UI
   should match Figma exactly — as a subagent, put the question in the report's
   `Clarification Needed` section for the caller to raise with the user.
3. Keep the overall result `FAIL` and list the items under `Clarification Needed`,
   not as automatic fixes, until the user confirms.
4. Convert them into actionable fixes only after the user confirms they should change.

If a content/data mismatch also changes structure, layout, or visual fidelity in a
real way, report that underlying defect normally.

## Checklist before reporting PASS

```text
- [ ] Verified the ENTIRE page (scrolled from top to bottom)
- [ ] All sections from Figma are present in the implementation
- [ ] Container hierarchy matches Figma layers
- [ ] Flex/grid direction is correct
- [ ] Alignment (justify/align) matches the design
- [ ] Element order matches the design
- [ ] No extra/missing wrapper elements that change layout
- [ ] Actual computed container widths measured (not inferred from the a11y tree)
- [ ] Full-page screenshot taken and visually compared against Figma
```

## Confidence levels

- **HIGH** — Both Figma and implementation data complete; the comparison is reliable.
  Fixes may be applied exactly as reported.
- **MEDIUM** — Some values could not be extracted; fix the obvious issues, flag the
  unclear ones for the user.
- **LOW** — Tool errors occurred or measurements are missing; the caller should get
  user confirmation before making any changes.
