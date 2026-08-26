# Component guidelines

Framework-agnostic decision tables for the `implementing-frontend` process.

## State decision framework

| State type | When to use | Example |
| --- | --- | --- |
| Local state | UI-only, single component | Modal open/close, input value |
| Lifted state | Shared between 2–3 siblings | Filter applied to a sibling list |
| Context / DI | Deeply nested consumption | Theme, locale, auth status |
| Global store | Complex cross-cutting state | Multi-step form wizard, shopping cart |
| Server cache | Remote data with caching | API responses, paginated lists |

## Barrel file guidelines

| Rule | Description |
| --- | --- |
| Create barrel when | Folder exports are consumed by OTHER modules (public API boundary) |
| Avoid barrel when | Internal utils serve a single parent component — import directly |
| Re-export style | Named re-exports only: `export { Button } from './Button'` |
| Never wildcard | Avoid `export * from` — breaks tree shaking, hides the API surface |
| Keep flat | One level deep — no barrel importing another barrel |
| Test with build | Verify the barrel doesn't pull unused code into the bundle |

## Anti-patterns

| Anti-pattern | Instead do |
| --- | --- |
| Hardcoded colors/spacing (`#3B82F6`, `16px`) | Use design tokens (`var(--color-primary-500)`, `theme.spacing(2)`) |
| Monolithic component (300+ lines) | Split into composed sub-components |
| Props drilling through 4+ levels | Use context or a composition pattern |
| Duplicating an existing component | Extend the existing one with variants |
| Inline styles for theming | Use the design system's styling approach |
| `export default` | Named exports for consistency and refactoring |
| `any` type for props | Explicit type definitions |
| Barrel file for internal utils | Direct imports for single-consumer folders |
