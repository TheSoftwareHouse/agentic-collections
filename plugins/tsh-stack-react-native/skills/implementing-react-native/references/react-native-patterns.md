# React Native implementation patterns

React Native implementations of the generic patterns in `implementing-react-native`.
Load this reference before writing or reviewing React Native code. Device concerns —
text, safe area, keyboard, storage — are in `platform-and-device.md`; lists and
performance are in `lists-and-performance.md`.

## Imports

The rule is in `SKILL.md`; this is how to apply and enforce it. It applies unchanged:
the React Native Babel preset compiles JSX with the automatic runtime
(`runtime: 'automatic'` in `@react-native/babel-preset` 0.88.1), and the official 0.88
template imports names, never `React`.

| Severity | Rule |
| --- | --- |
| MUST | Mark type-only imports with `type`, inline or as `import type`. |
| MUST | Import from `react` by name: `import { useState } from 'react'`. |
| PREFER | Import from `react-native` by name too (`import { Pressable, Text } from 'react-native'`); there is no default export worth importing. |
| PREFER | Propose the ESLint rule below when the project does not enforce the import style yet; add it only once the team agrees. A project on a shared ESLint config gets it there, not in its own file. |

```tsx
import { memo, useState, type ReactNode } from 'react';
```

The `TSQualifiedName` selector needs the `typescript-eslint` parser and matches only
in TypeScript files; the other three also work in `.js` and `.jsx`, so the glob covers
both. Merge the entries into the project's existing `no-restricted-syntax` — a second
declaration of the rule replaces the first instead of adding to it.

```js
// eslint.config.js
{
  files: ['**/*.{js,jsx,ts,tsx}'],
  rules: {
    'no-restricted-syntax': ['error',
      { selector: "ImportDeclaration[source.value='react'] > ImportNamespaceSpecifier", message: "Import from 'react' by name: import { useState } from 'react'." },
      { selector: "ImportDeclaration[source.value='react'] > ImportDefaultSpecifier", message: "Import from 'react' by name: import { useState } from 'react'." },
      { selector: "MemberExpression[object.name='React']", message: 'Use the named import instead of React.x.' },
      { selector: "TSQualifiedName[left.name='React']", message: "Import the type by name: import { type ReactNode } from 'react'." },
    ],
  },
},
```

## Exports

`restrictedNamedExports: ['default']` blocks only `export { x as default }`; it
deliberately does not block an `export default` declaration. Forbidding those takes
`restrictDefaultExports`
([`no-restricted-exports`](https://github.com/eslint/eslint/blob/main/docs/src/rules/no-restricted-exports.md)).

| Severity | Rule |
| --- | --- |
| MUST | Enforce the no-default-export rule with `restrictDefaultExports`, not `restrictedNamedExports` alone — the latter lets `export default` pass lint. |
| MUST | Scope the two exceptions in the config, not with inline disable comments: Storybook meta in `*.stories.tsx`, and Expo Router route files under `src/app/`. |
| NEVER | Widen an exception beyond those files. A default export anywhere else is a violation. |

```js
// eslint.config.js
{
  files: ['**/*.{js,jsx,ts,tsx}'],
  rules: {
    'no-restricted-exports': ['error', {
      restrictDefaultExports: {
        direct: true,      // export default function X() {}
        named: true,       // export { x as default }
        defaultFrom: true, // export { default } from './x'
        namedFrom: true,   // export { x as default } from './x'
        namespaceFrom: true, // export * as default from './x'
      },
    }],
  },
},
{
  // Storybook reads the meta from the default export; Expo Router
  // reads the screen component from a route file's default export.
  files: ['**/*.stories.{ts,tsx}', 'src/app/**'],
  rules: { 'no-restricted-exports': 'off' },
},
```

Drop the `src/app/**` glob in a project without Expo Router. Route files are specified
in `expo.md`.

## Component composition

| Generic pattern | React Native implementation |
| --- | --- |
| Content projection | `children` prop |
| Render delegation | Render props: `renderItem={({ item }) => <UserRow user={item} />}` on a list |
| Compound components | Shared context between parent and sub-components (`Tabs` + `Tabs.Tab`) |
| Slots | Named props accepting `ReactNode`: `header`, `footer`, `leading` |

Prefer `children` for single content projection. Use named `ReactNode` props (slots)
when multiple projection points are needed. Use compound components for tightly
coupled UI groups (tabs, segmented controls, accordions).

A list's `renderItem` returns a small component, not a large inline tree: the item is
the unit the list recycles, so keep it a named component with typed props.

## State patterns

| State type (from the skill) | React implementation | Hook |
| --- | --- | --- |
| Local state | Component-scoped | `useState`, `useReducer` |
| Lifted state | Prop drilling or callback props | Parent `useState` + pass down |
| Context / DI | React Context API | `createContext` + `useContext` |
| Server cache | Data fetching library | TanStack Query, SWR, or a framework-specific one |
| Device state | Platform hook for the value | `useColorScheme` ([docs](https://reactnative.dev/docs/usecolorscheme)), `AppState` |

Use `useReducer` over `useState` when state transitions are complex (multiple related
values, action-based updates). Read a device value through its hook so the screen
re-renders when it changes — never copy it into state once at mount.

## Declarative UI

| Severity | Rule |
| --- | --- |
| MUST | Drive the UI from state and props. Render the result; do not reach into rendered views to change them. |
| PREFER | Solve a performance problem with state structure, memoization or the native-driven animation APIs before direct manipulation. |
| NEVER | Call `setNativeProps` in ordinary screen code. It is imperative and keeps state in the native layer, outside React, which makes the code harder to reason about; the docs reserve it for continuous animations where re-rendering is a measured bottleneck ([Direct Manipulation](https://reactnative.dev/docs/legacy/direct-manipulation)). |

## Error handling

React Native uses the same **error boundaries** as React — class components with
`componentDidCatch` / `getDerivedStateFromError`:

- Wrap data-dependent sections with an `<ErrorBoundary>` component.
- Per-feature boundaries beat one global boundary.
- Error boundaries do NOT catch errors in event handlers or async code — handle those
  with try/catch and render the error state from component state.
- With Expo Router, the route file's named `ErrorBoundary` export is the mechanism;
  see `expo.md`.

The error UI is one of the three states every data-dependent screen handles; for a
list, `ListEmptyComponent` renders the empty state.

## Performance patterns

| Technique | React API | When to use |
| --- | --- | --- |
| Component memoization | `memo(Component)` | Prevent re-render when props unchanged |
| Expensive computation | `useMemo(() => compute(data), [data])` | Heavy calculations derived from state/props |
| Stable callbacks | `useCallback(fn, [deps])` | Callbacks passed to memoized children, including list `renderItem` |
| Stable style objects | `StyleSheet.create` or a module constant | Style objects passed to memoized children |

**Rule of thumb**: don't memoize by default. Measure first, and measure on a release
build — see `lists-and-performance.md`. `memo` only helps when re-renders are
measurably expensive and props don't change often.

## Lint rules for device code

`eslint-plugin-react-native` ships rules that enforce three of the skill's rules
mechanically. Propose them the same way as the import rule: when the project does not
enforce them yet, and added only once the team agrees. Register the plugin if the
project's shared config does not already. With ESLint 9, use
`@react-native/eslint-config/flat` as the base; `@react-native/eslint-config` and
`eslint-plugin-react-native` 5.0.0 support ESLint 8–9 only (npm, 2026-11-17).

| Rule | Enforces | Notes |
| --- | --- | --- |
| `react-native/no-raw-text` | Every string renders inside `<Text>` | `skip` option names project text components, merged with the built-in `Text`, `TSpan`, `StyledText`, `Animated.Text` |
| `react-native/no-inline-styles` | No literal values in a `style` object; values that are all variables (`style={{ paddingTop: insets.top }}`) pass | No options, no auto-fix |
| `react-native/no-color-literals` | No literal colors in styles | Flags `'#FFF'` or `'blue'`; a token or variable passes — the lint form of the design-token rule |

```js
// eslint.config.js — merge into the project's React Native block
rules: {
  'react-native/no-raw-text': 'error',
  'react-native/no-inline-styles': 'error',
  'react-native/no-color-literals': 'error',
},
```

Rule behaviour: [eslint-plugin-react-native](https://github.com/Intellicode/eslint-plugin-react-native).

## Anti-patterns

| Anti-pattern | Why | Fix |
| --- | --- | --- |
| Inline `{}` / `[]` as prop to a memo child | New reference every render defeats memo | Lift to a module constant or `useMemo` |
| Missing/wrong dependency array | Stale closures, infinite loops | Include all reactive values; lint with `exhaustive-deps` |
| `useEffect` for derived state | Unnecessary render cycle | Compute during render: `const x = fn(props.y)` |
| Index as list key | Without a `keyExtractor`, `FlatList` uses `item.key`, then `item.id`, then the index; breaks reconciliation on reorder/delete | Return a stable unique ID from `keyExtractor` |
| `onClick`, `div`-style thinking | There is no click or DOM | `Pressable` with `onPress` (see `platform-and-device.md`) |
| `setNativeProps` for ordinary updates | State lives outside React | Update state and re-render |
| Class component for new code (error boundaries excepted) | Inconsistent patterns, no hooks | Use functional components |
