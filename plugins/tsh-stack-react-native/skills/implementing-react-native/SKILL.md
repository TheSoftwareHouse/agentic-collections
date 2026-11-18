---
name: implementing-react-native
description: "React Native rules for iOS and Android apps, Expo or bare: screens built from View, Text and Pressable, every string inside Text, virtualized lists with stable keys, safe area and keyboard handling, Keychain and Keystore for secrets, Platform.select and .ios/.android files, and a design read before layout when a mockup exists. Use when writing or refactoring app code that runs on a phone, simulator or emulator."
when_to_use: "Trigger on: building or changing a React Native or Expo screen, Pressable touch targets, FlatList or FlashList screens, notch and keyboard overlap, StyleSheet work, Platform.select or .ios and .android files, storing a token on the device, sign-in, sign-out or refresh-token handling, a development-only mock or fallback that must not ship, a pull-to-refresh list, an unsaved-changes prompt on leaving a screen, running on a simulator or emulator, mobile data wiring or refactors, or starting or upgrading a React Native app."
---

# Implementing React Native

TSH conventions for React Native application code: how components are composed,
where state and modules live, what the device demands on top of that, and — when
the task has a design — the Figma-to-code workflow that comes before any markup.

## Applicability and Precedence

This skill covers **every** change to React Native application code, with or without
a design: a new screen from Figma, a custom hook, a store or API client, a refactor
that moves modules, a data or logic change that renders nothing new. The rules scope
themselves: the Figma gate applies only when the task has a design reference, the
token and UI-state rules to code that renders, the device rules to code that
touches a screen, a list, storage or a platform API, and the import, export, typing
and module rules to all of it.

Local repository rules outrank this skill: the project's existing component
patterns, design system, and styling approach win over the defaults here. The core
assumes bare React Native; Expo, NativeWind and React Navigation are covered by
conditional references, loaded only when `package.json` depends on them.

## Version Baseline

The rules target **React Native 0.88 with React 19**. Read the project's
`package.json` before writing code:

- **React Native is pinned** → follow that version; every rule here holds for
  releases that use the New Architecture by default.
- **No `package.json` yet — a greenfield app** → ask whether the app is Expo (the
  React Native docs [recommend a framework](https://reactnative.dev/docs/environment-setup))
  or bare before scaffolding; then install the latest stable release
  (`npm view react-native version`), with the `react` version that release pins.
- **The installed major is newer than 0.88** → check what changed in the current
  React Native documentation — through `context7`, which `tsh-core` bundles, or
  reactnative.dev — before applying this skill; where they disagree, the
  documentation wins.
- **Writing a library call or a config file** → the references state rules, not
  setup code; take the exact syntax for the installed version from its current
  documentation through `context7` rather than from memory.
- **The project predates the New Architecture default** → say so before writing
  code; some library guidance and the lists reference assume it.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | For a Figma-backed task, fetch and study the design through the Figma MCP before writing or editing any markup, layout, or styling. This pre-implementation design read is a hard gate, distinct from any post-implementation verification loop. |
| NEVER | Implement from assumptions. Design context, tokens, or specs missing or unclear → stop and raise it (as a subagent, report the blocker to the caller; in the main conversation, ask the user). Missing information produces wrong UI; asking produces correct UI. |
| MUST | Take every visual value (colors, spacing, typography, shadows, radii) from the project's design system tokens. No exact token match → use the closest existing token and document the deviation; a genuinely new value → flag it and ask before creating a token. |
| NEVER | Use `export default`, untyped or `any` props, or a component with more than ~7 props where composition (children, slots, compound components) would do. Exceptions: a Storybook `meta` default export and Expo Router route files, where the framework requires it. |
| MUST | Handle all three UI states in every data-dependent component: loading (progress indicator), error (meaningful message plus recovery action), empty (helpful message when no data). |
| MUST | Declare what the UI looks like from state; never imperatively manipulate the rendered views. Compose complex UIs from small, single-responsibility components. |
| MUST | Import what you use from `react` by name: `import { useState, type ReactNode } from 'react'`. NEVER `import * as React`, `import React`, `React.useState`, `React.memo` or `React.FC`. A project that already uses the namespace style consistently keeps it; one that already mixes the two writes new code with named imports and converts a file only when it changes it anyway. |
| MUST | Add a barrel `index.ts` only at a public API boundary — a folder other modules consume — with named re-exports. A folder serving one parent is imported directly. |
| NEVER | Leave a pass-through file after moving or renaming a module. A file that only re-exports the new location is not a barrel: update every importer to the new path and delete the old file in the same change. The exceptions are the public API of a package other code consumes — kept and marked `@deprecated` — and a re-export the plan explicitly stages as transitional. |
| MUST | Render every string inside a `<Text>` component, never as a bare child of a `View`; enforced by `react-native/no-raw-text` where the project lints with it; propose it otherwise. |
| MUST | Render any list that can grow long through a virtualized list (`FlatList`, or `FlashList` where the project uses it) with a stable `keyExtractor` or `key`; NEVER `ScrollView` + `map` for unbounded data. |
| MUST | Respect the safe area and the on-screen keyboard on every screen, and give each pressable a touch target of at least 44 pt on iOS and 48 dp on Android. |
| NEVER | Store tokens or secrets in `AsyncStorage`, plain MMKV, source or the JS bundle; use the platform Keychain and Keystore through a secure-storage library. |
| MUST | Isolate platform-dependent code behind `Platform.select` or `.ios.tsx` / `.android.tsx` files, and verify the change on both platforms — or name the platform you could not verify. |
| MUST | Read `package.json` before writing code, and read the matching reference first when it depends on `expo` ([expo.md](./references/expo.md)), `nativewind` ([nativewind.md](./references/nativewind.md)) or `@react-navigation/native` ([react-navigation.md](./references/react-navigation.md)). Their framework rules — route files, class-based tokens, navigator structure — override the defaults here. |

## Implementation Process

Steps 1–2 apply when the task has a design reference. Without one — a hook, a
refactor, a data or logic change — start at step 3.

1. **Fetch and review the Figma design** (the gate above). Resolve the node, export
   the node image via the Figma MCP, and extract layout, spacing, typography, colors,
   dimensions, variants, and states.
2. **Gather design context.** Map every Figma value to an existing design token:
   extract the raw value → search the codebase for a matching token → use it; no
   exact match → closest token plus a documented deviation; truly new → ask first.
   Identify every state the design implies (default, pressed, focused, disabled,
   loading, error, empty), and how the screen behaves with a safe-area inset, the
   keyboard open, larger system font sizes, and on both platforms.
3. **Plan the structure.** Decide reusable component, custom hook, or screen-specific
   code; define typed props and hook signatures with sensible defaults; place state
   using the state framework in the reference below; search for existing similar
   components and hooks and extend or compose rather than duplicate. A module move
   lists every importer it will rewrite.
4. **Implement.** Composition patterns (children/slots, render delegation, compound
   components) over prop sprawl; explicit prop types co-located in
   `ComponentName.types.ts`; named exports and named `react` imports; the
   framework's error-boundary mechanism around data-dependent sections; the three
   UI states; tokens for every visual value; strings in `<Text>`.
5. **Organize modules.** Barrels only at public API boundaries; after a move, no
   importer points at the old path and the old file is gone — rules in the
   reference below.
6. **Verify.** Run the project's type check and linter. For a change that renders or
   is platform-dependent, also run it on an iOS simulator and an Android emulator, or
   name the platform you could not run. For a design-backed task, if the calling
   workflow provides a verification loop (a UI verification gate run by the
   orchestrator), defer to it — do not duplicate verification here. Otherwise,
   compare the rendered screen against the Figma design yourself and walk through
   each interaction state, iterating until it matches within tolerance.

## Component Checklist

The same list is the React Native review checklist: when reviewing a change, check
the diff against it and the Non-negotiable Rules above.

```text
- [ ] Single responsibility — one clear purpose
- [ ] Typed props — explicit types, sensible defaults
- [ ] Named export — no default exports
- [ ] Named react imports — no React namespace, no React.FC
- [ ] Design tokens — no hardcoded visual values
- [ ] Error state — handles failure gracefully
- [ ] Loading state — shows progress indicator
- [ ] Empty state — meaningful message when no data
- [ ] Composition — uses children/slots, not prop sprawl
- [ ] Modules — barrels only at public boundaries, no pass-through files after a move
- [ ] Text — every string inside <Text>
- [ ] Lists — virtualized, stable keys
- [ ] Safe area and keyboard — handled; touch targets 44 pt / 48 dp
- [ ] Platforms — platform code isolated, checked on iOS and Android
- [ ] Secrets — tokens only in Keychain/Keystore; sign-out clears the session
- [ ] Release build — development-only code and fallbacks unreachable
```

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Component guidelines](./references/component-guidelines.md) | Deciding where state lives, adding a barrel file, moving or splitting modules, or reviewing for anti-patterns | The state decision framework, barrel-file details, the anti-pattern table |
| [React Native patterns](./references/react-native-patterns.md) | Before writing or reviewing React Native code | How React implements the composition, state, error-handling, and performance patterns above, plus the lint rules that enforce imports, exports and raw text |
| [Platform and device](./references/platform-and-device.md) | Laying out a screen, handling forms or the keyboard, storing data on the device, or code that differs per platform | Text and styles, flexbox defaults, Pressable, safe area, keyboard, platform files, AppState, deep links, secure storage, session and sign-out, environment variables |
| [Lists and performance](./references/lists-and-performance.md) | Writing a list, or investigating jank or slow screens | FlatList and FlashList, keys, pull-to-refresh state, release-build measurement, JS thread versus UI thread |
| [TypeScript for React Native](./references/typescript-for-react-native.md) | Editing `tsconfig`, adding path aliases, typing navigation, or upgrading TypeScript | The preset-owned config, `tsc` as a separate gate, aliases, version policy |
| [Expo](./references/expo.md) | `package.json` depends on `expo` | Expo-specific setup, config, routing, unsaved-changes guard, monorepo native modules, release-build guards and build conventions |
| [NativeWind](./references/nativewind.md) | `package.json` depends on `nativewind` | Tokens through Tailwind classes, setup and its limits |
| [React Navigation](./references/react-navigation.md) | `package.json` depends on `@react-navigation/native` | Navigator structure, typed routes, screen options, deep links, unsaved-changes guard |

## Related Skills

- UI verification against Figma (capture, tolerances, PASS gates) lives in the
  `tsh-product-engineering` plugin (`reviewing-ui` and its agents), which may not be
  installed and drives a browser, so it does not cover React Native screens yet — name
  the gap rather than improvising verification here.
- Screen-reader accessibility — roles, labels, state, focus, announcements, large text
  and reduced motion — is `ensuring-react-native-accessibility`, in this plugin
  ([`ensuring-react-native-accessibility`](../ensuring-react-native-accessibility/SKILL.md)).
