# Changelog

All notable changes to `tsh-stack-ios` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.1.0] - 2026-11-20

Initial release: native iOS apps in Swift, SwiftUI-first, written against Xcode 27.2,
Swift 6.4 and the iOS 27.2 SDK.

### Added

- **`implementing-ios`.** Conventions for any change to native iOS app code (not the
  `ios/` project of a React Native or Flutter app): one owner per
  piece of state with `@State`, `@Observable`, `@Bindable` and `@Environment`; screen
  models whose loading, error and data properties render loading, failed, empty and
  loaded;
  feature folders, then local packages as the app grows; dependency injection through
  initializers and `@Entry` environment values, no container; value-based
  `NavigationStack` routing with a router per stack and deep links parsed into routes;
  Swift concurrency under main-actor default isolation, `@concurrent` for heavy work,
  task lifetime tied to `.task`, and `Sendable` escape hatches allowed only with a
  stated proof; a `URLSession` API client with `nonisolated` DTOs and typed errors that
  maps a cancelled request to `CancellationError`; SwiftData
  behind a store service, with no `@Query` in views; `UserDefaults` and the Keychain,
  each for what it is for; String Catalogs, asset
  catalog colours, Dynamic Type, VoiceOver labels and `#Preview`; a Figma design read
  before layout when a screen has one; UIKit interop in both directions and
  working in a UIKit app. The deployment target is asked for, never picked; below
  iOS 17 the skill falls back to `ObservableObject` and Core Data. It is a companion to
  an implementation workflow, not one itself.
- **`configuring-xcode-for-ios`.** The build side of a native project: the Xcode project with buildable
  folders and the Xcode 27.2 JSON project format; `.xcconfig` files per configuration
  and shared schemes; signing basics and no secrets in the bundle; the privacy
  manifest; Swift 6 language mode with `MainActor` default isolation and Approachable
  Concurrency for app targets, `nonisolated` for logic packages, and a staged
  module-by-module migration from Swift 5 mode; Swift Package Manager only, a
  committed `Package.resolved`, and leaving CocoaPods ahead of its trunk going
  read-only on 2 December 2026; SwiftFormat pinned through a build-tools package; `xcodebuild` build and
  test in CI on a pinned Xcode with warnings failing the build, switched on through
  the project's own `.xcconfig` so remote packages are not affected; and an Xcode upgrade
  procedure.
