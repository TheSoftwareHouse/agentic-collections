# Component guidelines

Framework-agnostic decision tables for the `implementing-react-native` process. A
deliberate copy of the web counterpart: only the styling examples differ.

## State decision framework

| State type | When to use | Example |
| --- | --- | --- |
| Local state | UI-only, single component | Modal open/close, input value |
| Lifted state | Shared between 2–3 siblings | Filter applied to a sibling list |
| Context / DI | Deeply nested consumption | Theme, locale, auth status |
| Global store | Complex cross-cutting state | Multi-step form wizard, shopping cart |
| Server cache | Remote data with caching | API responses, paginated lists |

## Barrel file guidelines

The two blocking rules — barrels only at a public API boundary, and no pass-through
file after a move — sit in the skill's Non-negotiable Rules. The detail:

| Rule | Description |
| --- | --- |
| Create barrel when | Folder exports are consumed by OTHER modules (public API boundary) |
| Avoid barrel when | Internal utils serve a single parent component — import directly |
| After a move | Rewrite every importer to the new path and delete the old file; a file that only re-exports the new location is a shim, not a barrel |
| Re-export style | Named re-exports only: `export { Button } from './Button'` |
| Never wildcard | Avoid `export * from` — it hides the API surface |
| Keep flat | One level deep — no barrel importing another barrel |

## Anti-patterns

| Anti-pattern | Instead do |
| --- | --- |
| Hardcoded colors/spacing (`'#3B82F6'`, `padding: 16`) | Use design tokens (`theme.colors.primary`, `theme.spacing.md`) |
| Monolithic component (300+ lines) | Split into composed sub-components |
| Props drilling through 4+ levels | Use context or a composition pattern |
| Duplicating an existing component | Extend the existing one with variants |
| Inline styles for theming | Use the project's styling approach (theme object, `StyleSheet`, or NativeWind) |
| `export default` | Named exports for consistency and refactoring; the only exceptions are named in the skill's rules |
| `any` type for props | Explicit type definitions |
| Barrel file for internal utils | Direct imports for single-consumer folders |
| Re-export shim left at a module's old path "for compatibility" | Update the importers and delete the old file — inside one app there is no consumer to stay compatible with |
| `import * as React` / `React.useState` | Named imports: `import { useState } from 'react'` |
