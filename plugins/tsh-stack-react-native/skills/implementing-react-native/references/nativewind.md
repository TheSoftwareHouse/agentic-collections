# NativeWind

Load this reference only when the project's `package.json` depends on `nativewind`; a project that
styles with `StyleSheet` or a theme object never needs it. It targets NativeWind 4.2 (stable, Tailwind
CSS 3, `tailwind.config.js`). NativeWind v5 (Tailwind CSS 4) is a release candidate and changes the
setup; do not apply a v4 row to a v5 project, and do not upgrade one to the other unasked.
NativeWind 4.2.7 documents Expo support up to SDK 57 ([installation](https://www.nativewind.dev/docs/getting-started/installation)); on a newer Expo SDK, check NativeWind's release notes before assuming the v4 setup still holds, and say so when you cannot confirm it.

## Detect the version first

| Severity | Rule |
| --- | --- |
| MUST | Read the installed `nativewind` and `tailwindcss` versions before writing a class or a config. NativeWind 4 requires Tailwind CSS 3; v5 targets Tailwind CSS 4. |
| MUST | Keep the existing setup. For v4 that is `nativewind/preset` in the Tailwind config, the `nativewind/babel` preset, `withNativeWind` in the Metro config and `global.css` imported once from the app entry. |
| NEVER | Replace a v4 configuration with the v5 one, or mix them. v5 is a release candidate; keep v4 unless the team decides to migrate. |
| MUST | When the version is v5, stop using this file for setup and read the current NativeWind docs through context7. In v5 the `cssInterop` and `remapProps` calls below are replaced by the `styled()` and `@map` mechanisms. |

Sources: [installation](https://www.nativewind.dev/docs/getting-started/installation),
[v4 repository README](https://github.com/nativewind/nativewind/blob/nativewind@4.2.7/README.md).

## Tokens live in the Tailwind theme

This is rule 3 of the core skill (every visual value comes from a token) applied to NativeWind.

| Severity | Rule |
| --- | --- |
| MUST | Define every design token (colors, spacing, radii, font sizes, shadows) in `theme.extend` of `tailwind.config.js`, named after the design system's token, and use it through a class: `bg-surface`, `text-primary`, `p-4`. |
| NEVER | Write a literal color, pixel size or radius in a class: no `bg-[#1f6feb]`, `p-[13px]`, `rounded-[7px]`. |
| MUST | When the design has no matching token, use the nearest theme value and report the difference, as the core rule says. Add a new token only when the design system defines it. |
| PREFER | Import a shared token file into the config (`const colors = require('./colors')` under `theme.extend`) when the values are also needed outside class names, for example a navigation theme or an icon color prop. One source, two consumers. |
| MUST | Keep `content` globs in the Tailwind config covering every file that contains classes, including shared packages in a monorepo. A class in an unscanned file produces no style and no error. |

Source: [themes](https://www.nativewind.dev/docs/guides/themes).

## Writing styles with `className`

| Severity | Rule |
| --- | --- |
| MUST | Style with `className`. `no-inline-styles` (`react-native/no-inline-styles`) still applies: no literal values in `style`; runtime values (insets, measured sizes, animated styles) may go through `style`. |
| MUST | Keep `react-native/no-color-literals` enabled. It catches the colors NativeWind does not. |
| MUST | Build class names from complete literal strings. Tailwind finds classes by scanning source text, so `` `bg-${tone}` `` generates nothing; map the variant to full class names instead. |
| PREFER | A variant map (`Record<Variant, string>`) over string concatenation with conditionals. |
| MUST | Accept an optional `className` prop on a reusable component only when callers need to override its look, and merge it with `tailwind-merge` 2.6.x (v3 supports Tailwind CSS 4 only). Register custom theme keys such as `touch` once with `extendTailwindMerge`, or an override of them is not merged. |
| NEVER | Concatenate two class strings that may set the same property (`'p-2 ' + className`). Both classes reach the style engine and the winner is not the one you intend. |
| MUST | Platform and state variants use the Tailwind prefixes (`ios:`, `android:`, `dark:`, `active:`), not `Platform.OS` branches around class strings. |
| MUST | Touch targets stay 44 pt (iOS) / 48 dp (Android) through a theme token (`minHeight: { touch: '48px' }`, `minWidth: { touch: '48px' }` in `theme.extend`, used as `min-h-touch min-w-touch`) or `hitSlop`. NativeWind's native rem is smaller than the web's 16 px (its own tests render `p-4` as about 14.3), so spacing-scale classes are not their web size: `min-h-12` comes out near 43, below both targets. |

Sources: [tailwind-merge](https://github.com/dcastil/tailwind-merge) for the merge behaviour and the
Tailwind version each major supports; [`extendTailwindMerge` in v2.6.0](https://github.com/dcastil/tailwind-merge/blob/v2.6.0/docs/configuration.md).

## TypeScript

| Severity | Rule |
| --- | --- |
| MUST | Keep the `nativewind-env.d.ts` file containing `/// <reference types="nativewind/types" />` and make sure `tsconfig.json` includes it. Without it `className` is a type error on core components. |
| NEVER | Name that file `nativewind.d.ts`, the name of a folder beside it, or the name of a folder in `node_modules` (such as `react.d.ts`); TypeScript then ignores it. |

Source: [installation](https://www.nativewind.dev/docs/getting-started/installation).

## Third-party components

A component from a library accepts `className` only after NativeWind is told which prop it maps to.
First check whether it already takes a `style` prop and whether wrapping it is simpler.

| Severity | Rule |
| --- | --- |
| PREFER | `remapProps(Component, { buttonClass: 'buttonStyle' })` when the component has plain style props and you want new `className`-like props that map one-to-one. |
| PREFER | `cssInterop(Component, { className: 'style' })` when the component needs its `style` resolved, or when a style value must be extracted into a non-style prop (`nativeStyleToProp`, for example `color` to `placeholderTextColor`). |
| MUST | Call `cssInterop` and `remapProps` once, at module scope, in a dedicated file (for example `src/components/ui/interop.ts`) imported by the app entry. Never call them inside a component. |
| MUST | Type any new prop you create by declaration merging, or the call site fails the type check. |
| NEVER | Fall back to `style={{ ... }}` with hand-copied token values to avoid the interop call. |

Sources: [cssInterop](https://www.nativewind.dev/docs/api/css-interop),
[remapProps](https://www.nativewind.dev/docs/api/remap-props).

## Checklist for a NativeWind change

1. Installed `nativewind` and `tailwindcss` versions match the setup being edited.
2. No literal color, size or radius in a class; tokens come from the theme.
3. No literal values in `style` (runtime values excepted); no class name built by string interpolation.
4. Overriding `className` goes through `tailwind-merge` 2.6.x, with custom theme keys registered.
5. Third-party components wrapped once at module scope.
6. Touch targets reach 44 pt / 48 dp.
