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

Sources: [core concepts](https://docs.expo.dev/router/basics/core-concepts/),
[add navigation](https://docs.expo.dev/tutorial/add-navigation/),
[error handling](https://docs.expo.dev/router/error-handling/).

## Typed routes and deep links

| Severity | Rule |
| --- | --- |
| PREFER | Turn on typed routes: `"experiments": { "typedRoutes": true }` in `app.json`, then `npx expo customize tsconfig.json` to add the required `include` entries, then `npx expo start` to generate the types. `href` on `<Link>` is then type-checked. The docs still label the feature beta, so say so when you enable it. |
| MUST | Set a `scheme` in the app config before using deep links, and list the `expo-router` config plugin in `plugins`. |
| MUST | Guard a screen with unsaved changes with `usePreventRemove` from `expo-router`, and continue the blocked action with the callback's `repeat()` after the user confirms ([router API](https://docs.expo.dev/versions/latest/sdk/router/)). Disabling the back gesture alone is not a guard. |
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
| MUST | In a monorepo, declare every native module in the `package.json` of each app that uses it, and keep exactly one copy installed. Only one version of a native module can be compiled into a build; duplicate JavaScript packages are often harmless, duplicate native modules are not ([monorepos](https://docs.expo.dev/guides/monorepos/)). |
| PREFER | Check for duplicates with `npx expo-modules-autolinking verify` after adding or bumping a native dependency ([autolinking](https://docs.expo.dev/modules/autolinking/)). From SDK 55 `experiments.autolinkingModuleResolution` is on for monorepo apps; it is a workaround for a duplicate you cannot remove, not a fix. |

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
| MUST | Keep development-only modules (a mock backend, debug panels) behind a literal `if (__DEV__)` or `process.env.NODE_ENV === 'development'` check at the place that imports them, so the production bundle drops them ([tree shaking](https://docs.expo.dev/guides/tree-shaking/)). A check hidden inside a called function is not removed. |
| MUST | Give a development fallback (a `localhost` API address, a skipped login, mock data) only under `__DEV__`. A release build with a required value missing fails with the variable's name; it never falls back to a development value. |
| PREFER | Validate the production profile in a dynamic `app.config.ts`: throw when its API or auth addresses are not `https`, point at a loopback, private or emulator (`10.0.2.2`) host, or when a development flag is on, so the build fails before a bundle exists. Key the check on a variable the build profile sets (`APP_ENV` in `eas.json` `env`), which EAS uses to evaluate the config ([eas.json](https://docs.expo.dev/build/eas-json/)). **TSH derivation from the two rules above.** |
| MUST | Store the refresh token with `keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY` (iOS), so a backup restored to another device does not carry it, and keep the `expo-secure-store` config plugin's `configureAndroidBackup` on — or, with your own Auto Backup rules, exclude the `SecureStore` shared preferences ([SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/)). |
| MUST | Know what `requireAuthentication` does before gating a token behind biometrics: on Android every operation, writes included, asks for authentication; on iOS only reading or updating an existing value does. Test it on a real device — simulators and emulators do not ask ([SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/)). |

Sources: [environment variables](https://docs.expo.dev/guides/environment-variables/),
[authentication](https://docs.expo.dev/router/advanced/authentication/).

## Checklist for an Expo change

1. New file under `src/app/` is a route; anything else is outside it.
2. Default export only in `app/`; named exports elsewhere.
3. Packages added with `npx expo install`; `npx expo install --check` is clean.
4. No native directory edited by hand under CNG.
5. No secret in `EXPO_PUBLIC_*`.
6. Route has its loading, error (`ErrorBoundary`) and empty states.
