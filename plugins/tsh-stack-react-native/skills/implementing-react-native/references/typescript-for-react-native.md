# TypeScript for React Native

Use this reference when editing `tsconfig.json`, adding a path alias, choosing or
raising the TypeScript version, or finding that a build passes with type errors in it.

In React Native the compiler configuration is owned by a preset, so this is much
shorter than the browser setup: one `extends`, a real type-check step, and a version
policy. Local conventions outrank these defaults; in an existing repo propose the
smallest change that serves the task.

## Contents

- [Preset-owned configuration](#preset-owned-configuration)
- [The type gate](#the-type-gate)
- [Strictness and suppressions](#strictness-and-suppressions)
- [Path aliases](#path-aliases)
- [Version policy](#version-policy)

## Preset-owned configuration

| Project | Base config | Source |
| --- | --- | --- |
| Bare React Native | `"extends": "@react-native/typescript-config"` | [TypeScript](https://reactnative.dev/docs/typescript) |
| Expo | `"extends": "expo/tsconfig.base"`, plus `strict`; generate the file with `npx expo customize tsconfig.json` | [Expo TypeScript](https://docs.expo.dev/guides/typescript/) |

`@react-native/typescript-config` sets `strict`, `noEmit`, `moduleResolution: bundler`
and `jsx: react-native`, so a React Native `tsconfig.json` needs no `lib: DOM`, no
second config for build-time files and none of the browser options.

| Severity | Rule |
| --- | --- |
| MUST | Extend the preset and add only project fields (`paths`, `include`). Never restate or override a field the preset owns — the preset moves with the React Native version, a copy does not. |
| NEVER | Add `outDir` or turn `noEmit` off. Metro produces the bundle; two tools emitting into one tree is a debugging trap. |
| MUST | In an Expo project, keep the `include` entries the generated file has (`.expo/types/**/*.ts`, `expo-env.d.ts`) — typed routes and Expo's ambient types come from them. |
| PREFER | In an existing repo whose `tsconfig.json` works and differs from the preset, leave it alone and record the gap; never rewrite a working config wholesale to match this page. |

## The type gate

Babel strips types without checking them, and `tsc` is used only to type-check
([TypeScript](https://reactnative.dev/docs/typescript)). A green Metro bundle or a
launched app therefore proves nothing about type correctness.

| Severity | Rule |
| --- | --- |
| MUST | Run `tsc --noEmit` (or the project's `typecheck` script) as its own CI step. It is separate from the bundle, the tests and the linter, and fails the pipeline on any error. |
| MUST | Check that this step exists before tuning any flag — strictness is worth nothing if nothing runs the compiler. |
| PREFER | Expose the check as a `package.json` script (`"typecheck": "tsc --noEmit"`) so local runs and CI execute the same command. |
| NEVER | Rename the `./index.js` entry point to TypeScript when adopting `tsc` — the React Native guide says to leave it as is to avoid production bundling issues. |

## Strictness and suppressions

| Severity | Rule |
| --- | --- |
| MUST | Keep `strict` on. A project that cannot enable it wholesale turns the individual flags on progressively and records the remaining gap — never ships `strict: false` as a permanent state. |
| MUST | Treat `@ts-expect-error` as debt: it carries a comment naming the cause and the condition for removal. Prefer it over `@ts-ignore`, which silently rots when the error disappears. |
| NEVER | Disable a strict sub-flag to make one file compile. Fix the file, or isolate it with a narrowly scoped `@ts-expect-error`. |
| PREFER | `unknown` over `any` at boundaries (API responses, deep-link params, storage reads), narrowed before use. |

```tsx
// @ts-expect-error — vendor typings lack `hitSlop` on this component; remove after upgrading the library
<ThirdPartyIcon hitSlop={8} />
```

## Path aliases

An alias needs two entries that agree: the type checker's `paths` and the resolver that
bundles the app. `tsc` rewrites nothing, so an unmirrored alias type-checks and then
fails at bundle or run time.

| Project | Setup | Source |
| --- | --- | --- |
| Bare React Native | `compilerOptions.paths` in `tsconfig.json`, relative to the project root and without `baseUrl` ([TypeScript 6.0](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html) deprecates it, 7.0 removes it), mirrored in `babel.config.js` with `babel-plugin-module-resolver` (`root`, `extensions`, `alias`) | [TypeScript](https://reactnative.dev/docs/typescript) |
| Expo | `paths` in `tsconfig.json` only (`"@/*": ["./src/*"]`); Expo CLI resolves them automatically | [Expo TypeScript](https://docs.expo.dev/guides/typescript/) |

| Severity | Rule |
| --- | --- |
| MUST | Mirror every `paths` alias in `babel.config.js` in a bare project (or generate both from one source), and list the platform extensions in the resolver. |
| MUST | In Expo, restart Expo CLI after editing `paths` — it picks the change up without clearing the Metro cache ([Expo TypeScript](https://docs.expo.dev/guides/typescript/)). |
| NEVER | Add `babel-plugin-module-resolver` to an Expo project to reproduce `@/*`. |
| PREFER | One alias root (`@/*` → `src/*`) over one alias per folder. |

The Expo guide notes that an existing bare React Native app needs extra setup for
`tsconfig.json` aliases; where the project already uses the Babel resolver, keep it.

## Version policy

Verified 2026-11-17: React Native 0.88 with `@react-native/typescript-config` 0.88.1
and TypeScript 7.0.2 as the latest stable line, while the React Native template ships
`^6.0.3` — one major behind, as the browser template is.

| Severity | Rule |
| --- | --- |
| MUST | Pin an exact TypeScript version in `devDependencies` (`"typescript": "6.0.3"`, never `"^6.0.3"`). TypeScript does not follow semver — a minor release adds errors to code that compiled before. |
| MUST | Read the project's `package.json` first: a pinned version is followed, not changed as a side effect of another task. |
| MUST | Raise the version deliberately, in its own commit or PR with the error triage that follows — never inside an unrelated dependency update, and never on a React Native upgrade alone. |
| PREFER | For a new project, the TypeScript line the React Native template ships, moving to the latest stable line once `typescript-eslint` and the project's other compiler-API tooling declare support — confirmed by running `tsc --noEmit`, not assumed. |
| AVOID | Letting a repo fall more than two minors behind the line it follows. |
| MUST | Use one TypeScript version for a whole monorepo, hoisted to the root; two compiler versions make the same type unassignable to itself. |
