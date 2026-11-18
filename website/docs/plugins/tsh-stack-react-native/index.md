---
title: TSH Stack React Native
sidebar_label: Overview
sidebar_position: 1
description: TSH conventions for React Native 0.88 with React 19 on iOS and Android, covering the shared frontend standard plus the rules a device adds.
sources:
  - plugins/tsh-stack-react-native/.claude-plugin/plugin.json
  - plugins/tsh-stack-react-native/README.md
sources_hash: "1767a9cdc4434197dff4e1e08eb91606cef57fb5b03219722450e5150e1109be"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack React Native

TSH conventions for React Native 0.88 with React 19, on iOS and Android: the same standard `tsh-stack-frontend` applies to browser code, plus the rules a device adds.

## Who installs it and where

`tsh-stack-react-native` is a **stack** plugin, not a discipline plugin. Install it into the projects that use React Native, at **project** scope, so it travels with the repo. Your discipline plugin (`tsh-product-engineering` and friends) travels with you at **user** scope, and so does [`tsh-core`](/docs/plugins/tsh-core/). The install commands and the scope prompt are on the [installation page](/docs/getting-started/installation), which renders the repository README. The marketplace entry is `tsh-stack-react-native@tsh-agentic-collections`. If you added the marketplace before this plugin existed, refresh it first with `/plugin marketplace update tsh-agentic-collections`.

## What it ships

<PluginComponents plugin="tsh-stack-react-native" />

The plugin ships two skills. Both are model-invocable: Claude loads them when the work matches their descriptions.

`implementing-react-native` covers any change to React Native application code: Figma-first work, design tokens, the three UI states, named exports and `react` imports, and module boundaries. The device rules on top are text inside `<Text>`, virtualized lists with stable keys, safe areas and keyboard, touch targets (44 pt on iOS, 48 dp on Android), platform-specific code checked on both platforms, and tokens and secrets only in Keychain or Keystore. See [`implementing-react-native`](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native).

[`ensuring-react-native-accessibility`](/docs/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility) covers accessibility while building screens: `role`, label and state props that VoiceOver and TalkBack announce, moving screen-reader focus and announcing changes, text that follows the system font size, reduced motion, and a walk with the screen reader on a device.

## References

Five references are always available to `implementing-react-native`: `component-guidelines.md`, `react-native-patterns.md`, `platform-and-device.md`, `lists-and-performance.md` and `typescript-for-react-native.md`.

Three more load only when the project uses the library. The core rules assume bare React Native; these add what each library changes.

| Reference | Loads when `package.json` depends on |
| :-- | :-- |
| `expo.md` | `expo` |
| `nativewind.md` | `nativewind` |
| `react-navigation.md` | `@react-navigation/native` |

## Not covered yet

The README lists these as outside the plugin:

- **UI verification on a simulator or device**, including Maestro flows.
- **Auditing an existing React Native app for accessibility violations.** `ensuring-react-native-accessibility` covers building; `auditing-accessibility` in `tsh-product-testing` is a web audit.
- **Native module authoring** in Swift, Kotlin or C++.
- **Build and release**: EAS, Fastlane, store submission. Pipelines belong to `tsh-platform-engineering`.

## Scope

The routing question for this plugin is whether the guidance would change if the project switched from React Native to a browser app. If yes, it belongs here. Rules that hold for both are duplicated on purpose (`.claude/rules/stack-plugin-conventions.md`); change both copies in the same PR.

## Changelog

Release notes are on the [changelog page](/docs/changelog/tsh-stack-react-native). Updates arrive with `/plugin update`.
