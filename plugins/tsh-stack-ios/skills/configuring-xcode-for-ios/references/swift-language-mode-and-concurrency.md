# Swift language mode and concurrency settings

The build settings that decide how strictly the compiler checks concurrency and
which actor code runs on by default. Writing concurrent code itself — actors,
`Task`, `Sendable` types — is [`implementing-ios`](../../implementing-ios/SKILL.md).

## 1. The baseline for a new app

| Setting | Xcode build setting | Value | Effect |
| --- | --- | --- | --- |
| Swift Language Version | `SWIFT_VERSION` | `6.0` (Swift 6 mode) | Complete data-race checking; violations are errors |
| Default Actor Isolation | `SWIFT_DEFAULT_ACTOR_ISOLATION` | `MainActor` | Unannotated code in the module is `@MainActor` |
| Approachable Concurrency | `SWIFT_APPROACHABLE_CONCURRENCY` | `YES` | Turns on upcoming features, below: two in Swift 6 mode, five in Swift 5 mode |

Put them in `Shared.xcconfig` so every configuration agrees:

```text
SWIFT_VERSION = 6.0
SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor
SWIFT_APPROACHABLE_CONCURRENCY = YES
```

Xcode 26's new-app template sets MainActor default isolation and Approachable
Concurrency but still creates the project in **Swift 5 mode**; existing projects
default to `nonisolated`. Set all three explicitly in the `.xcconfig` rather than
relying on whatever the template of the day writes.

### Why MainActor by default for an app target

An app module is mostly UI and the state behind it, which must run on the main
actor anyway. Making that the default removes most annotations and most Swift 6
diagnostics in UI code. Work that should leave the main thread is marked explicitly
(`@concurrent`, `nonisolated`, or a dedicated actor) — which makes off-main work
visible in review, where it belongs.

### What Approachable Concurrency turns on

| Upcoming feature | Proposal | Change |
| --- | --- | --- |
| `NonisolatedNonsendingByDefault` | SE-0461 | A `nonisolated async` function runs on the **caller's** actor instead of hopping to the global executor; `@concurrent` restores the old behaviour |
| `InferIsolatedConformances` | SE-0470 | A protocol conformance on a main-actor type is inferred as main-actor-isolated |

In **Swift 5 mode** the same setting also turns on three features that Swift 6 mode
already includes: `DisableOutwardActorInference`, `GlobalActorIsolatedTypesUsability`
and `InferSendableFromCaptures` (Xcode's `Swift.xcspec`). That matters during a
migration: a Swift 5-mode module with the setting on is already partly on Swift 6
semantics.

The two features in the table are off by default until a future language mode. `NonisolatedNonsendingByDefault`
**changes runtime behaviour**, not only diagnostics: async code that used to leave
the main actor implicitly now stays on it. That is why it is a default for new code
and a deliberate, tested step for existing code.

Two settings are independent: Approachable Concurrency does not imply MainActor
default isolation, and vice versa.

## 2. Swift packages

With `// swift-tools-version: 6.0` or later, packages compile in Swift 6 mode by
default — no `swiftLanguageModes` entry is needed. Default isolation in a package
needs tools version **6.2** or later.

```swift
// swift-tools-version: 6.2
import PackageDescription

let approachable: [SwiftSetting] = [
    .enableUpcomingFeature("NonisolatedNonsendingByDefault"),
    .enableUpcomingFeature("InferIsolatedConformances"),
]

let package = Package(
    name: "Features",
    platforms: [.iOS(.v26)],
    products: [.library(name: "Profile", targets: ["Profile"])],
    targets: [
        .target(
            name: "Profile",                        // UI feature: main actor by default
            swiftSettings: approachable + [.defaultIsolation(MainActor.self)]
        ),
        .target(
            name: "APIClient",                      // pure logic: stays nonisolated
            swiftSettings: approachable
        ),
    ]
)
```

- **UI and feature packages**: `.defaultIsolation(MainActor.self)`.
- **Model, networking and pure-logic packages**: keep the `nonisolated` default.
  Their types are mostly `Sendable` values used from many places; forcing them onto
  the main actor serialises work that does not need it.
- Package settings do **not** inherit the app target's build settings — each
  package target states its own.

The upcoming-feature list a toolchain supports, and which are already on by default:
`swift -print-supported-features`.

## 3. Migrating an existing Swift 5-mode project

Never flip a whole app to Swift 6 mode in one change. Go module by module, leaves
first (packages with no internal dependencies), then the app target last.

1. **Measure.** In the module, set `SWIFT_STRICT_CONCURRENCY = complete` while
   staying in Swift 5 mode. Data-race problems appear as **warnings**. Count them.
2. **Fix the warnings** in that module in their own change(s). Typical fixes are
   code changes — `Sendable` conformances, actor isolation, `@MainActor` on UI
   types — and belong to `implementing-ios`.
3. **Switch the module** to `SWIFT_VERSION = 6.0` (or drop the per-target
   `.swiftLanguageMode(.v5)` in a package) once it has no concurrency warnings.
4. **Repeat** for the next module. Record which modules are still in Swift 5 mode
   in the project README until none are.

Turning on MainActor default isolation or Approachable Concurrency in an existing
module is a **separate** step from the language-mode switch, each with a full test
run and a manual pass through the affected screens — both change where code runs.

`@preconcurrency import` is acceptable for a dependency that has not adopted
`Sendable` yet; leave a comment naming the dependency version that will let you drop
it.

## Sources

Verified 2026-11-19:

- Swift 6.4 release: https://www.swift.org/blog/swift-6.4-released/
- SE-0461 `nonisolated(nonsending)` by default:
  https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
- SE-0466 control default actor isolation inference:
  https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
- SE-0470 global-actor isolated conformances:
  https://github.com/swiftlang/swift-evolution/blob/main/proposals/0470-isolated-conformances.md
- Setting default actor isolation in Xcode 26:
  https://www.donnywals.com/setting-default-actor-isolation-in-xcode-26/
- Approachable concurrency in Swift packages:
  https://useyourloaf.com/blog/approachable-concurrency-in-swift-packages/
- Swift Forums, concurrency settings for a new project:
  https://forums.swift.org/t/what-should-the-concurrency-settings-be-for-a-brand-new-project/83109
- Swift 6 migration guide: https://www.swift.org/migration/documentation/migrationguide/
