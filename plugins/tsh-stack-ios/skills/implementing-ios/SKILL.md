---
name: implementing-ios
description: "TSH conventions for any change to native iOS app code in Swift, SwiftUI-first: views and state with Observation (@State, @Observable, @Environment), screen models, the loading, error and empty states, navigation with NavigationStack, dependency injection, Swift concurrency in app code, networking with URLSession and Codable, persistence with SwiftData and the Keychain, and UIKit interop. Use when writing, refactoring or reviewing Swift code in an iOS app — a SwiftUI view, screen, model, service, API client or feature module."
when_to_use: "Trigger on: building a screen or feature in an iPhone or iPad app, writing or changing a SwiftUI view, deciding where state lives (@State, @Observable, @Bindable, @Environment), adding a view model, wiring navigation or deep links, calling a REST API from an iOS app, moving work off the main actor, storing data with SwiftData, UserDefaults or the Keychain, embedding a UIKit view in SwiftUI or SwiftUI in a UIKit app, starting a new iOS app, or reviewing a Swift change in an iOS project."
---

# Implementing iOS

TSH conventions for native iOS application code in Swift: how SwiftUI views and their
state are built, how a screen is structured, and how app code talks to the network,
storage and the rest of the system.

## Applicability and Precedence

This skill covers **every** change to Swift code in an iOS app target or its feature
packages: a new screen, a view, a screen model, a service, an API client, a refactor.
It does not cover the Xcode project, build settings, Swift Package Manager or linting
— that is [`configuring-xcode-for-ios`](../configuring-xcode-for-ios/SKILL.md).

**Local conventions outrank this skill.** An existing app keeps its architecture —
TCA, VIPER, MVVM with Combine, UIKit with coordinators — and its UI framework: a
UIKit app gets UIKit code unless it already hosts SwiftUI screens or the user asks to
start. Apply these defaults where the project is silent; name a deliberate deviation
instead of mixing two styles in one feature.

## Version Baseline

Written against **Swift 6.4, Xcode 27 and the iOS 27 SDK**, with **iOS 17** as the
lowest deployment target the patterns below assume (Observation and SwiftData need
it). Before writing code, read the project's `IPHONEOS_DEPLOYMENT_TARGET`, Swift
language version and default actor isolation (build settings or `.xcconfig`, and
`Package.swift` for packages), and state them in one line with the UI framework.

- **Deployment target below 17** → no `@Observable`, `@Bindable` or SwiftData: use
  `ObservableObject`, `@Published`, `@StateObject`/`@ObservedObject` and Core Data,
  and say so. Every other rule holds.
- **No project yet — a greenfield app** → the deployment target is a business
  decision (it decides which devices can run the app): **ask**. Recommend the current
  major minus one.
  Then set the project up with `configuring-xcode-for-ios` first.
- **Xcode or iOS newer than 27** → check what changed in the current Apple
  documentation — through `context7`, which `tsh-core` bundles, or
  developer.apple.com — before applying this skill; where they disagree, the
  documentation wins.

Never raise the deployment target, the Swift language mode or a dependency unasked.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | State the deployment target, Swift language mode and UI framework before writing code. When there is no project yet, ask for the deployment target. |
| NEVER | Call an API newer than the deployment target without an `if #available` / `@available` guard and a working fallback. |
| MUST | Keep views a function of state. Business logic, networking and persistence never live in `body` or in a view's helpers — they live in a screen model or a service. No `@Query` or `ModelContext` in a view, even for a simple list. |
| MUST | Give each piece of state one owner: `@State` for view-private values, an `@Observable` model created and held with `@State` by the view that owns it and passed down as a plain property or `@Bindable`, app-wide services through `@Environment`. NEVER `ObservableObject`, `@Published` or `@StateObject` in new code on iOS 17+. |
| MUST | Render every state of a loading screen — loading, failed (message plus retry), empty, loaded — from the screen model's `isLoading`, error and data properties. A screen that only renders the happy path is unfinished. |
| MUST | Inject dependencies through initializers, or through `@Environment` for app-wide services, with a protocol only where a test or a second implementation needs one. NEVER reach for a project singleton (`.shared`) from a view or a screen model in new code. |
| MUST | Start a view's async work in `.task` or `.task(id:)`, so it is cancelled with the view. NEVER `Task { }` in `onAppear` for loading, and NEVER `DispatchQueue` or completion handlers in new code. |
| MUST | Keep UI state and screen models on the main actor; move heavy work into an `@concurrent` function or an actor. NEVER `@unchecked Sendable`, `nonisolated(unsafe)` or `@preconcurrency` to silence the compiler without a comment proving why it is safe. |
| NEVER | Force-unwrap, `try!` or `as!` outside tests and compile-time certainties — handle the failure. |
| MUST | Keep secrets and tokens in the Keychain. NEVER in `UserDefaults`, `@AppStorage`, a plist or source code. |
| MUST | Take every user-facing string from a String Catalog and every colour and image from the asset catalog or the design system; support Dynamic Type and give icon-only controls an accessibility label. |
| MUST | Give every new view a `#Preview` that shows its states. NEVER `PreviewProvider` — Xcode 27 deprecates it. |
| MUST | Build and run the tests before reporting done (the project's own script, or `xcodebuild … build test`). A change that only compiles in your head is not done. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [SwiftUI views and state](./references/swiftui-views-and-state.md) | Before writing or reviewing any SwiftUI view, or deciding where state lives | Property wrappers and Observation, view composition, the screen model and its states, previews, strings, assets and Dynamic Type |
| [Architecture and navigation](./references/architecture-and-navigation.md) | Adding a screen or feature, a screen model, a service, navigation, a deep link, or a module | Feature layout, when a screen model is worth it, dependency injection, NavigationStack routing, modules, testing screen models |
| [Concurrency in app code](./references/concurrency-in-app-code.md) | The code uses `async`, `Task`, an actor or `Sendable`, or a concurrency diagnostic appears | Main-actor default, `@concurrent`, actors, task lifetime and cancellation, `Sendable` without escape hatches |
| [Networking and persistence](./references/networking-and-persistence.md) | Calling an API, decoding JSON, storing data locally, or handling a credential | The API client shape, errors, SwiftData, `UserDefaults`, the Keychain |
| [UIKit interop](./references/uikit-interop.md) | The project is UIKit-based, or one framework must host the other | Representables, hosting controllers, `UIHostingConfiguration`, working in a UIKit codebase |

## Procedure

1. **Read the ground truth.** Deployment target, Swift language mode, default actor
   isolation, UI framework, and how the neighbouring features are built — their
   folders, screen models, services, navigation and tests. Read the project's
   `CLAUDE.md` and `.claude/rules/` if present.
2. **Greenfield?** Ask for the deployment target, then set up the project with
   [`configuring-xcode-for-ios`](../configuring-xcode-for-ios/SKILL.md) before any
   app code.
3. **Plan the change.** Decide where each piece of state lives, whether the screen
   needs a screen model, which services it uses and how they are injected, how it is
   reached (route, sheet, deep link), and which module it belongs to. Search for an
   existing view, service or model to extend before writing a new one. Read
   [`architecture-and-navigation.md`](./references/architecture-and-navigation.md)
   before adding a screen.
4. **Implement inside out.** Model types, then services, then the screen model, then
   views, then previews. Read
   [`swiftui-views-and-state.md`](./references/swiftui-views-and-state.md) before
   writing any view, and
   [`concurrency-in-app-code.md`](./references/concurrency-in-app-code.md) before
   writing async code.
5. **Verify.** Build, run the tests (new unit tests use Swift Testing), run the
   formatter's lint, and for a UI change look at the previews or run the app in the
   Simulator and walk each state. Report what you ran and what you could not.

## Review Checklist

Also the checklist for reviewing an iOS change, together with the rules above.

```text
- [ ] Deployment target respected — every newer API is guarded
- [ ] One owner per piece of state; no ObservableObject in new iOS 17+ code
- [ ] No logic, networking or persistence in views
- [ ] Loading, failed, empty and loaded states all rendered
- [ ] Dependencies injected; no new singletons
- [ ] Async work tied to .task; no DispatchQueue; no unproven @unchecked Sendable
- [ ] No force unwraps, try! or as! outside tests
- [ ] Secrets in the Keychain only
- [ ] Strings localised, colours from assets, Dynamic Type works, icons labelled
- [ ] #Preview for each new view; build and tests pass
```

## Related Skills

- [`configuring-xcode-for-ios`](../configuring-xcode-for-ios/SKILL.md) — the
  project, build settings, packages and tooling underneath this code.
- Planning, orchestration and code review live in `tsh-product-engineering`, which
  may not be installed; this skill stands alone.
