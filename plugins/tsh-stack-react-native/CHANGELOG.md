# Changelog

All notable changes to `tsh-stack-react-native` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

## [0.1.0] - 2026-11-18

Initial release: TSH conventions for React Native 0.88 with React 19, on iOS and Android.

### Added

- **`implementing-react-native`.** Applies the same standard as `tsh-stack-frontend`'s
  `implementing-frontend` to React Native code — Figma read before markup, design
  tokens, the three UI states, named exports and named `react` imports, module
  boundaries — and adds the rules a device requires: text only inside `<Text>`,
  virtualized lists with stable keys, safe areas and keyboard handling, touch targets
  of 44 pt on iOS and 48 dp on Android, platform-specific code checked on both
  platforms, and tokens and secrets kept only in Keychain or Keystore. References
  cover component guidelines, React Native patterns, platform and device behaviour,
  lists and performance, and TypeScript for React Native. Three more load only when
  the project uses them: Expo, NativeWind and React Navigation.
- **`ensuring-react-native-accessibility`.** Accessibility applied while building React
  Native screens on iOS and Android: `role`, label and state props that VoiceOver and
  TalkBack announce, moving screen-reader focus and announcing changes, text that
  follows the system font size, reduced motion, and a walk with the screen reader on.
  One reference holds the role, state and platform-difference tables.
