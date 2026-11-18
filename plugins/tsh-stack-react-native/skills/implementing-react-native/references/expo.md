# Expo

Load this reference only when the project's `package.json` depends on `expo`; a bare React Native
project never needs it. It targets Expo SDK 58 (React Native 0.88, React 19.3) and Expo Router.
Check the pinned SDK in `package.json` first; for a newer SDK read the current docs through
context7 before applying a row.

## Routes and the `app` directory

Older or migrated projects keep routes in a root `app/` instead of `src/app/`
([src directory](https://docs.expo.dev/router/reference/src-directory/)); use the directory the
project has and adjust the `src/app/**` globs here and in `react-native-patterns.md` to match.

| Severity | Rule |
| --- | --- |
| MUST | Keep `src/app/` for routes and layouts only. Every file in it becomes a screen (and a web page), so a component, hook or util placed there turns into a route. Put them in `src/components/`, `src/hooks/`, `src/utils/`. |
| MUST | Keep route files thin: read params, compose components, return. Screen logic lives in components and hooks outside `app/`. |
| MUST | Export a route file's component as `export default`. This is the one exception to `NEVER export default`, and it applies only to files inside `app/` (including `_layout.tsx`). |
| NEVER | Use `export default` anywhere else, and never widen the ESLint `no-restricted-exports` override beyond the `app/` glob. |
| MUST | Name route files by their URL: `index.tsx` for the directory root, `[id].tsx` for a dynamic segment, `_layout.tsx` for shared UI such as headers and tab bars. |
| PREFER | A named `ErrorBoundary` export from a route file over a hand-rolled boundary around the screen. It receives `error` and `retry` (`ErrorBoundaryProps` from `expo-router`); without one, the error goes to the nearest parent route's boundary. This is the "framework error boundary mechanism" for the third UI state. |

```tsx
import { type ErrorBoundaryProps } from 'expo-router';

export function ErrorBoundary({ error, retry }: ErrorBoundaryProps) {
  // render the error state with the project's tokens; call retry() to re-render the route
}

export default function OrderScreen() {
  // ...
}
```

The ESLint override that allows route default exports:

```js
{
  files: ['src/app/**'],
  rules: { 'no-restricted-exports': 'off' },
}
```

Sources: [core concepts](https://docs.expo.dev/router/basics/core-concepts/),
[add navigation](https://docs.expo.dev/tutorial/add-navigation/),
[error handling](https://docs.expo.dev/router/error-handling/).

## Typed routes and deep links

| Severity | Rule |
| --- | --- |
| PREFER | Turn on typed routes: `"experiments": { "typedRoutes": true }` in `app.json`, then `npx expo customize tsconfig.json` to add the required `include` entries, then `npx expo start` to generate the types. `href` on `<Link>` is then type-checked. The docs still label the feature beta, so say so when you enable it. |
| MUST | Set a `scheme` in the app config before using deep links, and list the `expo-router` config plugin in `plugins`. |
| MUST | Treat every route param as untrusted input from outside the app: validate it before use, as you would a request parameter. |

Sources: [typed routes](https://docs.expo.dev/router/reference/typed-routes/),
[installation](https://docs.expo.dev/router/installation/).

## Dependency versions

| Severity | Rule |
| --- | --- |
| MUST | Add packages with `npx expo install <package>`, not `npm install`. It picks the version compatible with the installed SDK. |
| MUST | Run `npx expo install --check` in CI. In a CI environment it exits non-zero when an installed package does not match the SDK, which makes the check a gate. |
| PREFER | `npx expo install --fix` to repair a local mismatch. It fixes unconditionally, so run it only on purpose and review the diff. |
| NEVER | Pin the React Native or React version by hand. The SDK fixes both (SDK 58 ships React Native 0.88 and React 19.3); upgrade by moving the SDK. |

Source: [Expo CLI](https://docs.expo.dev/more/expo-cli/).

## Native projects (CNG)

| Severity | Rule |
| --- | --- |
| MUST | When the project uses Continuous Native Generation (`npx expo prebuild`) and `ios/` and `android/` are generated, make native changes through config plugins or app config. Direct edits are lost on the next `npx expo prebuild --clean`. |
| MUST | Check whether `ios/` and `android/` are committed before editing them. If they are, the project has left CNG and prebuild would overwrite them; say so and stop rather than regenerate. |
| PREFER | A config plugin for any change to `Info.plist`, `AndroidManifest.xml` or a native target, so the change survives regeneration. |

Sources: [Continuous Native Generation](https://docs.expo.dev/workflow/continuous-native-generation/),
[config plugins](https://docs.expo.dev/config-plugins/introduction/).

## Environment variables and secrets

| Severity | Rule |
| --- | --- |
| MUST | Treat every `EXPO_PUBLIC_*` variable as public. Its value is inlined into the JavaScript bundle and readable from the shipped app. |
| NEVER | Put a secret, an API key with write access or an encryption key in `EXPO_PUBLIC_*` or in an `.env` file the bundle reads. |
| MUST | Store tokens and credentials with `expo-secure-store` (Keychain on iOS, Keystore on Android), per the core security rule. |
| PREFER | Reference variables as `process.env.EXPO_PUBLIC_NAME` literally; Expo inlines only the dot-notation form; `process.env['EXPO_PUBLIC_NAME']` and destructuring are not inlined. |

Sources: [environment variables](https://docs.expo.dev/guides/environment-variables/),
[authentication](https://docs.expo.dev/router/advanced/authentication/).

## Checklist for an Expo change

1. New file under `src/app/` is a route; anything else is outside it.
2. Default export only in `app/`; named exports elsewhere.
3. Packages added with `npx expo install`; `npx expo install --check` is clean.
4. No native directory edited by hand under CNG.
5. No secret in `EXPO_PUBLIC_*`.
6. Route has its loading, error (`ErrorBoundary`) and empty states.
