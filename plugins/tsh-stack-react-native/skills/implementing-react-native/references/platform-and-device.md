# Platform and device

What a phone changes compared with a browser: text, styles, touch, screen edges, keyboard,
platform differences, app lifecycle and secure storage. Load it when you write layout, a form,
anything that persists data, or code that must behave differently on iOS and Android.

## Text

Docs: [Text](https://reactnative.dev/docs/text).

| Severity | Rule |
| --- | --- |
| MUST | Put every string inside `<Text>` or the project's text component. A text node directly under `<View>` throws. |
| NEVER | Render with `{count && <Row />}` when `count` is a number. `0` is rendered as a bare text node and crashes. Use `{count > 0 ? <Row /> : null}`. |
| MUST | Route text through the project's text component (an `AppText`) where one exists; PREFER creating one in a new app. There is no style cascade: a font set on a `<View>` does not reach its text. |
| PREFER | Nested `<Text>` only for inline spans inside one paragraph. Styles inherit only inside a `<Text>` subtree. |
| PREFER | Enforce the first rule with the lint rule `react-native/no-raw-text` from `eslint-plugin-react-native`. |

```tsx
// Crashes when unreadCount is 0
{unreadCount && <Badge value={unreadCount} />}

// Safe
{unreadCount > 0 ? <Badge value={unreadCount} /> : null}
```

## Styles and layout

Docs: [Flexbox](https://reactnative.dev/docs/flexbox),
[Height and width](https://reactnative.dev/docs/height-and-width).

| Severity | Rule |
| --- | --- |
| MUST | Expect different flexbox defaults than CSS: `flexDirection` is `column`, `alignContent` is `flex-start`, `flexShrink` is `0`, and `flex` takes a single number. Do not port web layout unchanged. |
| MUST | Write dimensions as unitless numbers (density-independent points). No `px`, `rem` or `%`-of-font units. |
| MUST | Take colours, spacing and radii from the project's tokens, as everywhere else in this skill. A token is a TypeScript value, not a CSS variable. |
| PREFER | `StyleSheet.create` or the project's styling library over inline style objects; keep the lint rules `react-native/no-inline-styles` and `react-native/no-color-literals` on. |
| MUST | Where the app supports dark mode, read the light or dark scheme with `useColorScheme` and map it to a token set. Never hard-code a second palette in a component. See [useColorScheme](https://reactnative.dev/docs/usecolorscheme). |

## Touch

Docs: [Pressable](https://reactnative.dev/docs/pressable), [View `hitSlop`](https://reactnative.dev/docs/view),
[Android touch target size](https://support.google.com/accessibility/android/answer/7101858).

| Severity | Rule |
| --- | --- |
| MUST | Use `Pressable` for tappable elements. Do not write `onClick`, and do not use the older `Touchable*` components in new code. |
| MUST | Show the pressed state by passing a function to `style`: `style={({ pressed }) => [styles.button, pressed && styles.pressed]}`. There is no hover state to rely on. |
| MUST | Give every tappable element a touch area of at least 44 x 44 pt on iOS and 48 x 48 dp on Android. Apple: "a button needs a hit region of at least 44x44 pt" ([HIG — Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)); Android: 48 dp ([Touch target size](https://support.google.com/accessibility/android/answer/7101858)). The React Native docs' own 30–40 points is a lower bound we do not use. |
| MUST | Grow a small visual (an icon) with `hitSlop`, not by enlarging the icon. The touch area never extends beyond the parent's bounds, so leave room in the parent. |
| PREFER | On Android, add `android_ripple` for native feedback alongside the pressed style. |
| MUST | Set `disabled` on a `Pressable` that must not react, and reflect it visually. |

```tsx
<Pressable
  onPress={onClose}
  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
  style={({ pressed }) => [styles.closeButton, pressed && styles.closeButtonPressed]}
  role="button"
  aria-label={t('close')}
>
  <CloseIcon />
</Pressable>
```

## Safe area and keyboard

Docs: [Safe areas (Expo)](https://docs.expo.dev/develop/user-interface/safe-areas/),
[SafeAreaView](https://reactnative.dev/docs/safeareaview),
[React Native 0.81](https://reactnative.dev/blog/2025/08/12/react-native-0.81),
[KeyboardAvoidingView](https://reactnative.dev/docs/keyboardavoidingview),
[Keyboard handling (Expo)](https://docs.expo.dev/guides/keyboard-handling/).

| Severity | Rule |
| --- | --- |
| MUST | Keep content out of the notch, status bar and gesture bar with `react-native-safe-area-context`: `SafeAreaProvider` at the root, then its `SafeAreaView` or `useSafeAreaInsets()` applied as padding, with `edges` limited to the sides no header or tab bar already covers. Never the core `SafeAreaView`: it is deprecated, iOS-only and not edge-to-edge compatible. Android renders edge-to-edge from React Native 0.81 (target API 36). |
| PREFER | `SafeAreaView` for whole screens; `useSafeAreaInsets` when only one edge needs padding (it can perform worse than `SafeAreaView` while the device rotates). |
| MUST | Use the project's keyboard solution (e.g. `react-native-keyboard-controller`); with none, `KeyboardAvoidingView` with `behavior` set for both platforms. The focused input stays visible above the keyboard. |
| MUST | Test a form on both platforms with the keyboard open; `keyboardVerticalOffset` is often non-zero when a header sits above the view. |

## Platform differences

Docs: [Platform-specific code](https://reactnative.dev/docs/platform-specific-code).

| Severity | Rule |
| --- | --- |
| MUST | Branch on the platform with `Platform.select({ ios, android, default })` for a value, or with `Component.ios.tsx` / `Component.android.tsx` files when the whole implementation differs. |
| NEVER | Scatter `Platform.OS === 'ios'` checks through render logic. |
| MUST | Verify a platform-dependent change on both a simulator or emulator, or name the platform you did not test in the report. |
| PREFER | Keep the shared import path identical (`import { Sheet } from './Sheet'`); the bundler picks the platform file. |

## App lifecycle and links

Docs: [AppState](https://reactnative.dev/docs/appstate), [Linking](https://reactnative.dev/docs/linking).

| Severity | Rule |
| --- | --- |
| MUST | Refresh time-sensitive data when the app returns to the foreground: subscribe with `AppState.addEventListener('change', …)` and remove the subscription on cleanup. When the project uses TanStack Query, wire `AppState` to `focusManager.setFocused(status === 'active')` and NetInfo to `onlineManager` once at the app root instead of per screen — without it, refetch on focus and on reconnect does nothing in React Native ([TanStack Query: React Native](https://tanstack.com/query/latest/docs/framework/react/react-native)). |
| MUST | Handle a cold start from a link: `Linking.getInitialURL()` resolves to the launch URL or `null`; for links that arrive while the app is running, use the other `Linking` events. When a navigation library is in use, configure deep links there instead (see the conditional references). |
| NEVER | Trust data from a deep link. Validate and parse parameters as untrusted input. |

```tsx
useEffect(() => {
  const subscription = AppState.addEventListener('change', (state) => {
    if (state === 'active') refetch();
  });
  return () => subscription.remove();
}, [refetch]);
```

## Secure storage and secrets

Docs: [Security](https://reactnative.dev/docs/security),
[Expo authentication](https://docs.expo.dev/router/advanced/authentication/),
[Expo environment variables](https://docs.expo.dev/guides/environment-variables/),
[react-native-config](https://github.com/lugg/react-native-config),
[react-native-mmkv](https://github.com/margelo/react-native-mmkv/blob/main/README.md).

| Severity | Rule |
| --- | --- |
| NEVER | Store tokens, passwords or keys in AsyncStorage. It is unencrypted, and the docs list token storage and secrets under "don't". |
| MUST | Keep tokens, passwords and keys in the platform keychain: Keychain on iOS, Keystore on Android, through `react-native-keychain` or `expo-secure-store`. |
| PREFER | AsyncStorage or MMKV for non-sensitive data only: preferences, cached lists, onboarding flags. |
| NEVER | Put a secret or an encryption key in a bundled `.env` (`react-native-config`, `EXPO_PUBLIC_*`). Anything the JavaScript reads is inside the app and readable by the user; Expo states `EXPO_PUBLIC_*` values are plain text in the compiled app. |
| MUST | With `react-native-config`, treat every value as a string and parse it explicitly — `Config.MOCK_API === 'true'`, never `if (Config.MOCK_API)`, because `"false"` is truthy. The README: "All variables are strings". |
| MUST | After changing `.env` with `react-native-config`, rebuild the app: the values are baked in at build time, and restarting Metro does not rebuild native code (on iOS, re-run `pod install` if the build phase never ran). |
| PREFER | Type the keys in `react-native-config.d.ts` (`declare module 'react-native-config'` with an `export interface NativeConfig { … }`), so a misspelt key fails the type check. |
| MUST | Treat MMKV without an `encryptionKey` as plain text on disk, protected only by the OS sandbox (per the MMKV README). |
| MUST | If MMKV must hold sensitive data, generate the encryption key on the device at first launch and keep it in Keychain/Keystore. **This is TSH's derivation from the two sources above; the MMKV docs do not say where the key should come from.** |
| MUST | On iOS, store the refresh token with a `*_THIS_DEVICE_ONLY` accessibility (`WHEN_UNLOCKED_THIS_DEVICE_ONLY`, in `react-native-keychain`'s `ACCESSIBLE` or `expo-secure-store`'s `keychainAccessible`), so it is not migrated to a new device from a backup ([react-native-keychain](https://oblador.github.io/react-native-keychain/api/enumerations/ACCESSIBLE.html)). On Android, exclude secure storage from Auto Backup (Expo: see `expo.md`). |
| PREFER | Keep the access token in memory only and persist just the refresh token in secure storage. **TSH derivation: a short-lived token needs no persistence, and what is never written cannot leak from storage.** |
| MUST | On sign-out, clear the session on the device even when the network call fails: delete the tokens, clear the server cache (`queryClient.clear()` with TanStack Query clears queries and mutations — [QueryClient](https://tanstack.com/query/latest/docs/reference/QueryClient)), reset local stores, and remove user data from MMKV or AsyncStorage. |

