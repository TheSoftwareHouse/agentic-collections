# React Navigation

Load this reference only when the project's `package.json` depends on `@react-navigation/native`.
An Expo Router project navigates through `expo.md` and does not need it unless it also installs React
Navigation directly. It targets React Navigation 7: the static API (`createStaticNavigation`) is
preferred, and the dynamic API (`NavigationContainer`) is supported where a project already uses it.
Check the installed major version first; for v8 or later read the current docs through context7.

## Navigators are created once

| Severity | Rule |
| --- | --- |
| MUST | Create navigators at module scope (`createNativeStackNavigator(...)`, `createStaticNavigation(...)`), outside any component. |
| NEVER | Create a navigator, or call `createStaticNavigation`, inside a component's render. A navigator built during render is a new component type on every render, so the whole tree below it unmounts and remounts and loses its state. |
| NEVER | Define a screen component inside another component, or pass an inline render function to `component` (`component={() => <Home />}`). Pass the component reference. React Navigation warns about the inline case only. |
| MUST | Pass data to a screen through route params, a context or a hook, not by wrapping the screen in a closure. |
| MUST | Keep one root navigator and one `NavigationContainer` (or one `createStaticNavigation` result) per app. |

Source: [troubleshooting](https://reactnavigation.org/docs/troubleshooting/).

## Static API first

| Severity | Rule |
| --- | --- |
| PREFER | The static API for new navigation: a navigator is a plain object of `screens`, and the app renders `createStaticNavigation(RootStack)`. It gives automatic typing, deep link paths and less glue. |
| MUST | In an existing dynamic-API project, keep the dynamic API and follow its conventions. Do not migrate it as a side effect of another change; migration is its own task. |
| MUST | Group related screens into nested navigators (tabs inside a stack) rather than one flat list of every screen. |
| PREFER | The navigator's `createXScreen` helper (for example `createNativeStackScreen`) when a screen's `options` or `listeners` need inferred param types. |

```tsx
import { createStaticNavigation } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { HomeScreen } from './screens/HomeScreen';
import { ProfileScreen } from './screens/ProfileScreen';

const RootStack = createNativeStackNavigator({
  screens: {
    Home: HomeScreen,
    Profile: ProfileScreen,
  },
});

const Navigation = createStaticNavigation(RootStack);

export function App() {
  return <Navigation />;
}
```

Sources: [static vs dynamic](https://reactnavigation.org/docs/static-vs-dynamic/),
[static configuration](https://reactnavigation.org/docs/static-configuration/).

## Typed params

| Severity | Rule |
| --- | --- |
| MUST | Static API: type each screen's props with `StaticScreenProps<{ ... }>` from `@react-navigation/native`. |
| MUST | Static API: declare the module augmentation once, next to the root navigator, so `useNavigation`, `Link` and `navigate` are type-checked. |
| MUST | Dynamic API: define one `RootStackParamList` type per navigator and type screens with the navigator's `NativeStackScreenProps<RootStackParamList, 'Name'>` (or the matching `StackScreenProps`, `BottomTabScreenProps`). Keep these types in a separate `types.ts`. |
| NEVER | Type params as `any` or cast `route.params`. A screen without params is `undefined`; an optional-params screen is `{ ... } | undefined`. |
| MUST | Pass serializable values only in params (ids, strings, numbers). Fetch the object on the destination screen from the shared data layer. |

```tsx
import type { StaticScreenProps } from '@react-navigation/native';

type ProfileScreenProps = StaticScreenProps<{ userId: string }>;

export function ProfileScreen({ route }: ProfileScreenProps) {
  // route.params.userId is a string
}
```

```ts
type RootStackType = typeof RootStack;

declare module '@react-navigation/native' {
  interface RootNavigator extends RootStackType {}
}
```

Sources: [TypeScript](https://reactnavigation.org/docs/typescript/),
[static vs dynamic](https://reactnavigation.org/docs/static-vs-dynamic/).

## Deep linking

| Severity | Rule |
| --- | --- |
| MUST | Enable deep links by passing a `linking` object with `prefixes` (your `https://` domain and custom scheme) to the navigation component. The native projects must also register the scheme or domain. |
| MUST | Static API: declare each screen's path in its own `linking` property. The `linking` prop on the component accepts `prefixes`, `enabled` and root-level options only, not a full `config`. |
| PREFER | `enabled: 'auto'` to generate paths for leaf screens, once you have checked the generated URLs are the ones you want to publish. `enabled: true` uses only paths declared explicitly. |
| MUST | A dynamic navigator nested inside a static one needs a `screens` map on the parent screen's `linking`, because the nested navigator cannot generate paths. |
| MUST | Treat deep link params as untrusted input and validate them in the screen, as for any external request. Never act on a link (delete, pay, sign out) without the user's confirmation. |

```tsx
const linking = {
  enabled: 'auto' as const,
  prefixes: ['https://example.com', 'example://'],
};

export function App() {
  return <Navigation linking={linking} />;
}
```

Sources: [static configuration](https://reactnavigation.org/docs/static-configuration/),
[combining static with dynamic](https://reactnavigation.org/docs/combine-static-with-dynamic/).

## Screen conventions

| Severity | Rule |
| --- | --- |
| MUST | Each screen handles its three UI states (loading, error, empty) itself; a navigator does not provide them. |
| MUST | Screen components are named exports, like every other component. |
| PREFER | `useNavigation()` in a deeply nested component over threading the `navigation` prop down. |
| MUST | Header colors, tab bar styling and transition options come from design tokens, not literals. |
| MUST | Respect the safe area under custom headers and tab bars (core rule on safe area and keyboard). |

## Checklist for a navigation change

1. Navigators and screen components are defined at module scope.
2. No inline render function in `component`.
3. Params typed with `StaticScreenProps` plus the `RootNavigator` augmentation, or with a param list.
4. Params are serializable and validated when they come from a link.
5. New deep link has a path, a prefix and native registration.
6. Each new screen has loading, error and empty states.
