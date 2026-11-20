# Swift Package Manager

Dependencies and modules in a TSH iOS project go through Swift Package Manager
(SwiftPM). This covers adding and pinning remote packages, splitting the app into
local packages, and leaving CocoaPods.

## 1. One dependency manager: SwiftPM

New projects use **SwiftPM only**. No CocoaPods, no Carthage, no vendored binaries
copied into the repository.

CocoaPods trunk becomes **permanently read-only on 2 December 2026**: no new pods
and no new versions of existing pods can be published after that. Existing
`Podfile`s keep resolving, but every dependency is frozen at its last published
version — security fixes included. Several vendors (Firebase among them) have
already stopped publishing new versions to CocoaPods.

## 2. Adding a remote dependency

Before adding one, check that the platform does not already cover the need —
`URLSession`, `Codable`, SwiftData, `Observation` and Swift Testing replace several
packages projects used to pull in. Then:

| Requirement | Use for |
| --- | --- |
| `.upToNextMajor(from: "1.4.0")` | Default — Xcode's own default, and `from:` in `Package.swift`. `Package.resolved` already locks the exact version, so the requirement only bounds what a deliberate update may pull in |
| `.upToNextMinor(from: "1.4.0")` | A package that has broken its API in a minor release before |
| `exact: "1.4.2"` | A package under active investigation, or one that has broken a patch release |
| `branch:` / `revision:` | Never in a merged change; only to test an unreleased fix locally |

- **Commit `Package.resolved`** — for the app it lives in
  `<Project>.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved`
  (or the `.xcworkspace` equivalent). It is what makes every machine and CI build
  the same versions.
- Update dependencies deliberately (*File → Packages → Update to Latest Package
  Versions*, or `xcodebuild -resolvePackageDependencies` after editing a
  requirement), in a change of their own, with the `Package.resolved` diff reviewed.
- A package with a **binary target** (`.xcframework`) must come from the vendor's
  official repository and its checksum must be in the manifest. Check that the
  vendor ships a privacy manifest for it.
- Package plugins and macros run code at build time; Xcode asks to trust them. Read
  what a plugin does before trusting it, as you would a build script.

## 3. Local packages as modules

Split the app into **local Swift packages** rather than more app targets or
frameworks. A package gives each module its own access control (`internal` really
is internal), its own fast unit-test target that needs no simulator host for pure
logic, and its own concurrency settings.

```text
MyApp.xcodeproj
MyApp/                       # app target: @main, composition root, resources
Packages/
├── Core/                    # Package.swift: models, API client, persistence
└── Features/                # Package.swift: one library product per feature
```

- Add the package folder to the project (*File → Add Package Dependencies → Add
  Local…*), then link its library products to the app target.
- Start with one or two packages and split further only when a module boundary is
  real — a feature team, a shared extension, a build-time problem. A package per
  screen is overhead, not architecture.
- Dependency direction is one way: features depend on core, never the reverse, and
  features do not depend on each other.
- Set each package target's language mode and isolation as described in
  [`swift-language-mode-and-concurrency.md`](./swift-language-mode-and-concurrency.md);
  packages do not inherit the app's build settings.
- Declare `platforms: [.iOS(...)]` equal to the app's deployment target, and
  `defaultLocalization` when the package has user-facing strings.

## 4. Leaving CocoaPods

In an existing project, **do not migrate unasked.** When the task touches
dependencies, report the CocoaPods exposure and propose the migration as its own
change. When asked to migrate:

1. List every pod with its version and check whether the vendor publishes a SwiftPM
   package. A pod with no SwiftPM distribution needs a replacement or a decision
   before you start.
2. Move one pod at a time (or one small group): remove it from the `Podfile`, run
   `pod install`, add the SwiftPM package at the **same version**, build and test.
3. Watch for duplicate symbols when the same library arrives through both managers
   during the transition.
4. When the `Podfile` is empty, run `pod deintegrate`, delete `Podfile`,
   `Podfile.lock`, `Pods/` and the generated `.xcworkspace` if nothing else needs it,
   and update CI to build the `.xcodeproj` scheme.

## Sources

Verified 2026-11-19:

- CocoaPods trunk read-only plan: https://blog.cocoapods.org/CocoaPods-Specs-Repo/
- Swift Package Manager documentation: https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/
- Adding package dependencies to your app:
  https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app
- Organizing your code with local packages:
  https://developer.apple.com/documentation/xcode/organizing-your-code-with-local-packages
