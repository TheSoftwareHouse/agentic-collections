---
title: Implementing React Native
sidebar_label: implementing-react-native
sidebar_position: 1
description: TSH conventions for any change to React Native application code, from named imports and module boundaries to the rules a device adds, such as text inside Text, virtualized lists and secrets in Keychain.
sources:
  - plugins/tsh-stack-react-native/skills/implementing-react-native/SKILL.md
  - plugins/tsh-stack-react-native/skills/implementing-react-native/references/
sources_hash: "a74250ec78568fb6bb5565e0bdb0c103cfc0898cdef0c30a37965eff73cbd72a"
---

# Implementing React Native

**Plugin:** [`tsh-stack-react-native`](/docs/plugins/tsh-stack-react-native/)  
**Invoke:** `/tsh-stack-react-native:implementing-react-native` (Claude also loads it when the work matches its description)  
**Used by:** [`ensuring-react-native-accessibility`](/docs/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility) points to it for component composition and touch-target code

TSH conventions for React Native application code: how components are composed, where state and modules live, what the device demands on top of that, and, when the task has a design, the Figma-to-code workflow that comes before any markup. It covers **every** change to React Native application code, with or without a design: a new screen from Figma, a custom hook, a store or API client, a refactor that moves modules, or a data or logic change that renders nothing new. Each rule scopes itself: the Figma gate applies only when the task has a design reference, the token and UI-state rules to code that renders, the device rules to code that touches a screen, a list, storage or a platform API, and the import, export, typing and module rules to all of it.

The project's existing component patterns, design system and styling approach outrank the skill's defaults. The core assumes bare React Native; Expo, NativeWind and React Navigation are covered by conditional references, loaded only when `package.json` depends on them.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Figma-first** | For a Figma-backed task, the design is fetched and studied through the Figma MCP before any markup, layout or styling is written. This pre-implementation read is a hard gate, distinct from any post-implementation verification loop |
| **No assumptions** | Missing or unclear design context, tokens or specs stop the work: a subagent reports the blocker to the caller, the main conversation asks the user |
| **Design tokens** | Every visual value comes from the project's tokens. No exact match means the closest token plus a documented deviation; a genuinely new value is flagged and asked about before a token is created |
| **Components** | Single responsibility, typed props, no `export default` (except a Storybook `meta` and Expo Router route files), no `any` props, no component with more than about 7 props where composition would do |
| **React imports** | Named imports from `react`, for example `import { useState, type ReactNode } from 'react'`. Never `import * as React`, `import React`, `React.useState`, `React.memo` or `React.FC` |
| **UI states** | Loading, error (a meaningful message plus a recovery action) and empty, in every data-dependent component |
| **Modules** | A barrel `index.ts` only at a public API boundary, with named re-exports. After a move or rename, every importer is updated and the old file is deleted |
| **Text** | Every string inside a `<Text>` component, enforced by the `react-native/no-raw-text` lint rule where the project lints with it, and proposed otherwise |
| **Lists** | Any list that can grow long goes through `FlatList` (or `FlashList` where the project uses it) with a stable key; never `ScrollView` plus `map` for unbounded data |
| **Screen edges** | Safe area and on-screen keyboard respected on every screen; touch targets of at least 44 pt on iOS and 48 dp on Android |
| **Secrets** | Tokens and secrets never in `AsyncStorage`, plain MMKV, source or the JS bundle; the platform Keychain and Keystore through a secure-storage library |
| **Platforms** | Platform-dependent code behind `Platform.select` or `.ios.tsx` / `.android.tsx` files, verified on both platforms or the unverified platform named |

## Version baseline

The rules target **React Native 0.88 with React 19**, and the skill reads the project's `package.json` first:

| Situation | What the skill does |
| :-- | :-- |
| React Native is pinned | Follows that version; every rule holds for releases that use the New Architecture by default |
| No `package.json` yet (greenfield) | Asks whether the app is Expo (the React Native docs recommend a framework) or bare before scaffolding, then installs the latest stable release, with the `react` version that release pins |
| Installed major is newer than 0.88 | Checks what changed in the current React Native documentation, through `context7` or reactnative.dev, before applying the skill; the documentation wins where they disagree |
| Project predates the New Architecture default | Says so before writing code; some library guidance and the lists reference assume it |

## How it works

Steps 1 and 2 apply when the task has a design reference. Without one, such as a hook, a refactor or a data or logic change, the process starts at step 3.

1. **Fetch and review the Figma design**: resolve the node, export the node image via the Figma MCP, and extract layout, spacing, typography, colours, dimensions, variants and states.
2. **Gather design context**: map every Figma value to an existing token and identify every state the design implies, including behaviour with a safe-area inset, the keyboard open, larger system font sizes, and on both platforms.
3. **Plan the structure**: reusable component, custom hook or screen-specific code; typed props and hook signatures; state placement; search for existing similar components and hooks to extend or compose. A module move lists every importer it will rewrite.
4. **Implement**: composition over prop sprawl, explicit prop types co-located in `ComponentName.types.ts`, named exports and `react` imports, the framework's error-boundary mechanism around data-dependent sections, the three UI states, tokens for every visual value, strings in `<Text>`.
5. **Organize modules**: barrels only at public boundaries, no importer left on an old path.
6. **Verify**: run the project's type check and linter. For a change that renders or is platform-dependent, also run it on an iOS simulator and an Android emulator, or name the platform that could not be run. For a design-backed task, if the calling workflow provides a verification loop, defer to it; otherwise compare the rendered screen against the design and walk through each interaction state.

The skill ends with a fifteen-item component checklist, which doubles as the React Native review checklist for the diff.

## References

| Reference | Loaded when |
| :-- | :-- |
| Component guidelines | Deciding where state lives, adding a barrel file, moving or splitting modules, or reviewing for anti-patterns |
| React Native patterns | Before writing or reviewing React Native code |
| Platform and device | Laying out a screen, handling forms or the keyboard, storing data on the device, or code that differs per platform |
| Lists and performance | Writing a list, or investigating jank or slow screens |
| TypeScript for React Native | Editing `tsconfig`, adding path aliases, typing navigation, or upgrading TypeScript |
| Expo | `package.json` depends on `expo` |
| NativeWind | `package.json` depends on `nativewind` |
| React Navigation | `package.json` depends on `@react-navigation/native` |

The framework rules in the Expo, NativeWind and React Navigation references, such as route files, class-based tokens and navigator structure, override the skill's defaults.

## Boundaries and dependencies

- **UI verification against Figma** (capture, tolerances, PASS gates) lives in `tsh-product-engineering`: `reviewing-ui` and its agents. That plugin may not be installed, and it drives a browser, so it does not cover React Native screens yet; the skill says to name the gap rather than improvise verification.
- **Accessibility**: screen-reader accessibility (roles, labels, state, focus, announcements, large text and reduced motion) is [`ensuring-react-native-accessibility`](/docs/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility), in this plugin.
- **Figma MCP and `context7`** come from [`tsh-core`](/docs/plugins/tsh-core/). See the [Figma](/docs/integrations/figma) and [Context7](/docs/integrations/context7) integration pages.

## Related skills

- [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend): the same standard for browser code in `tsh-stack-frontend`.
- [`ensuring-react-native-accessibility`](/docs/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility): VoiceOver and TalkBack accessibility while building screens.

## Source

[`plugins/tsh-stack-react-native/skills/implementing-react-native/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-react-native/skills/implementing-react-native/SKILL.md)
