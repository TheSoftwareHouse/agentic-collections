---
title: Implementing iOS
sidebar_label: implementing-ios
sidebar_position: 1
description: Conventions for any change to native iOS app code in Swift, SwiftUI-first, from where state lives to networking, persistence and UIKit interop.
sources:
  - plugins/tsh-stack-ios/skills/implementing-ios/
sources_hash: "411c64216acaaf327b58de10cd2325dba06f62151531fc26da701d56704b4825"
---

# Implementing iOS

**Plugin:** [`tsh-stack-ios`](/docs/plugins/tsh-stack-ios/)  
**Invoke:** `/tsh-stack-ios:implementing-ios`, and Claude also loads it when the work matches its description  
**Used by:** [`configuring-xcode-for-ios`](/docs/plugins/tsh-stack-ios/skills/configuring-xcode-for-ios) lists it as the sibling skill for app code

Conventions for native iOS application code in Swift: how SwiftUI views and their state are built, how a screen is structured, and how app code talks to the network, storage and the rest of the system. It covers every change to Swift code in an iOS app target or its feature packages: a new screen, a view, a screen model, a service, an API client or a refactor. The Xcode project, build settings, Swift Package Manager and linting belong to `configuring-xcode-for-ios`. The `ios/` project that React Native or Flutter generates is not covered: that code follows its framework's conventions. The skill is a companion to a workflow, not one itself: when `tsh-product-engineering` is installed, a feature request goes to `orchestrating-feature-implementation` first, and this skill supplies the iOS conventions while the code is written.

Local conventions outrank the skill: an existing app keeps its architecture (TCA, VIPER, MVVM with Combine, UIKit with coordinators) and its UI framework, so a UIKit app gets UIKit code unless it already hosts SwiftUI screens or the user asks to start.

## Key areas

| Area | Coverage |
| :-- | :-- |
| **Versions** | Written against Swift 6.4, Xcode 27 and the iOS 27 SDK, with iOS 17 as the lowest deployment target the patterns assume. Below 17 it falls back to `ObservableObject` and Core Data; with no project yet it asks for the deployment target |
| **State** | One owner per piece of state: `@State` for view-private values, an `@Observable` model held with `@State` by the view that owns it, `@Bindable` for bindings into it, `@Environment` for app-wide services, `@AppStorage` for small preferences only |
| **Screens** | A screen model with separate loading, error and data properties, and every loading screen renders loading, failed, empty and loaded; views stay a function of state, with no logic, networking or persistence |
| **Architecture** | Views, screen models and services, grouped by feature and moved into local Swift packages as the app grows; dependency injection through initializers and `@Entry` environment values, with no container |
| **Navigation** | Value-based `NavigationStack` routing with a `Hashable` route enum and a router per stack; routes carry identifiers, and deep links are parsed into routes |
| **Concurrency** | Main-actor default isolation, `@concurrent` for heavy work, actors for shared state, task lifetime tied to `.task`, no `DispatchQueue` or completion handlers in new code, and `Sendable` escape hatches only with a stated proof |
| **Networking and storage** | A `URLSession` API client with `nonisolated` DTOs and typed errors, which maps a cancelled request to `CancellationError` so no cancelled load shows as a failure; SwiftData behind a store service for structured data, `UserDefaults` for small preferences, the Keychain for every secret |
| **UI basics** | String Catalogs, asset catalog colours, Dynamic Type, VoiceOver labels on icon-only controls and grouped elements, and a `#Preview` per state |
| **UIKit interop** | `UIHostingController` and `UIHostingConfiguration` for SwiftUI inside UIKit, representables for UIKit inside SwiftUI, and working inside a UIKit app |

## How it works

1. **Read the ground truth:** deployment target, Swift language mode, default actor isolation, UI framework, and how neighbouring features are built.
2. **Greenfield:** ask for the deployment target, then set up the project with `configuring-xcode-for-ios` before any app code.
3. **Plan the change:** where each piece of state lives, whether the screen needs a model, which services it uses, how it is reached and which module it belongs to.
4. **Implement inside out:** model types, services, the screen model, views, previews.
5. **Verify:** run the calling workflow's verification commands when it defines them; otherwise build, run the tests (new unit tests use Swift Testing), run the formatter's lint, and for a UI change check the previews or the Simulator in every state.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | State the deployment target, Swift language mode and UI framework before writing code; ask for the deployment target when there is no project yet, or, as a subagent, report the blocker to the caller |
| MUST | For a screen backed by a Figma design, fetch and study the design through the Figma MCP before writing layout; never implement from assumptions |
| NEVER | Call an API newer than the deployment target without an availability guard and a working fallback |
| MUST | Keep views a function of state; logic, networking and persistence live in a screen model or a service, with no `@Query` in views |
| MUST | Give each piece of state one owner; no `ObservableObject`, `@Published` or `@StateObject` in new code on iOS 17+ |
| MUST | Render every state of a loading screen: loading, failed, empty and loaded |
| MUST | Inject dependencies through initializers or `@Environment`; no new project singletons from views or screen models |
| MUST | Start a view's async work in `.task`; no `Task { }` in `onAppear` for loading, no `DispatchQueue` or completion handlers in new code |
| MUST | Keep UI state on the main actor and move heavy work to `@concurrent` functions or actors; no unproven `@unchecked Sendable`, `nonisolated(unsafe)` or `@preconcurrency` |
| NEVER | Force-unwrap, `try!` or `as!` outside tests and compile-time certainties |
| MUST | Keep secrets and tokens in the Keychain only |
| MUST | Localise every user-facing string, take colours and images from assets, support Dynamic Type, label icon-only controls |
| MUST | Give every new view a `#Preview`; never `PreviewProvider` |
| MUST | Verify before reporting done: the calling workflow's verification commands when it defines them, otherwise a build and the tests |

## References

| Reference | Load when |
| :-- | :-- |
| SwiftUI views and state | Before writing or reviewing any SwiftUI view, or deciding where state lives |
| Architecture and navigation | Adding a screen, feature, screen model, service, navigation, deep link or module |
| Concurrency in app code | The code uses `async`, `Task`, an actor or `Sendable`, or a concurrency diagnostic appears |
| Networking and persistence | Calling an API, decoding JSON, storing data locally, or handling a credential |
| UIKit interop | The project is UIKit-based, or one framework must host the other |

## Related skills

- [`configuring-xcode-for-ios`](/docs/plugins/tsh-stack-ios/skills/configuring-xcode-for-ios): the project, build settings, packages and tooling underneath this code.

## Source

[`plugins/tsh-stack-ios/skills/implementing-ios/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-ios/skills/implementing-ios/SKILL.md)
