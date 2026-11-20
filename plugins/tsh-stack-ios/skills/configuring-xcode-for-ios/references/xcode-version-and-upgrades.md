# Xcode version, deployment target and upgrades

Which Xcode a project builds with, which iOS versions it supports, and how to move
either one forward.

## 1. Current toolchain (November 2026)

| | Version |
| --- | --- |
| Xcode (stable) | 27.2 |
| Swift | 6.4 (6.4.2 is the latest patch) |
| SDKs | iOS / iPadOS 27.2 |
| Xcode 27 host requirement | macOS Tahoe 26.6 or later, **Apple silicon only** |
| Oldest iOS deployment target Xcode 27 accepts | iOS 15 |
| App Store Connect upload requirement (since 28 April 2026) | Built with Xcode 26 or later, iOS 26 SDK or later |

These change on Apple's cadence — a major Xcode every autumn, point releases through
the year. Check the Xcode release notes before quoting any of them.

## 2. Pinning Xcode

- **One Xcode version per project**, the same on every developer machine and CI
  runner. Record it in a `.xcode-version` file at the repository root (for example
  `27.2`) and in the README. `xcodes install` / `xcodes select` with no argument,
  and fastlane's `xcodes`, `xcversion` and `ensure_xcode_version` actions, read the
  file on their own. GitHub's `maxim-lobanov/setup-xcode` action does not: read the
  file in an earlier step and pass the value to its `xcode-version` input.
- CI selects it explicitly (`sudo xcode-select -s /Applications/Xcode_27.2.app` or
  the runner's equivalent) and prints `xcodebuild -version` at the start of the log.
- Prefer the latest stable Xcode for new projects. Do not develop on a beta Xcode on
  the main branch; a beta-only API or project format then blocks everyone.

## 3. Deployment target

**The minimum iOS version is a business decision** — it sets which devices and users
the app reaches. When the project has none or the user has not stated it, **ask**,
and offer this recommendation:

- **Greenfield: the current major minus one** — iOS 26 today. Apple's adoption
  figures usually put the large majority of active devices on the latest two
  majors; quote the current figures from Apple's App Store support page rather than
  from memory.
- **Floor: iOS 17.** `@Observable` (Observation) and SwiftData — both defaults in
  `implementing-ios` — need it. Below 17 the code-level conventions change, so say
  so explicitly before agreeing to a lower target.
- An existing app keeps its target. Raising it is a product decision with its own
  change, because it drops users.

Set the target once — `IPHONEOS_DEPLOYMENT_TARGET` in `Shared.xcconfig` — and
mirror it in every local package's `platforms:` list. A package declaring a lower
version than the app is harmless; a higher one fails to link.

The **SDK** you build with is separate: always the one the pinned Xcode ships.
Building with the iOS 27 SDK and deploying to iOS 26 is normal; guard newer APIs
with `if #available(iOS 27, *)`.

## 4. What Xcode 27 changed that affects configuration

Read the full release notes before upgrading; these are the items most likely to
need a project change:

- **Apple silicon only** — an Intel Mac or Intel CI runner cannot run Xcode 27.
- **`ld64` removed**; `-ld_classic` is no longer supported. Remove either flag from
  `OTHER_LDFLAGS` before upgrading.
- **`PreviewProvider` deprecated**, with its preview modifiers — move previews to the
  `#Preview` macro. The warning appears once the deployment target is iOS 27.
- **Raised minimum deployment targets** for watchOS (9) and macOS (12); iOS stays at
  15. Debugging on a physical device needs iOS 17 or later on the device.
- **JSON project format** (Xcode 27.2) — the default for new projects, opt-in for
  existing ones; see
  [`xcode-project-and-build-settings.md`](./xcode-project-and-build-settings.md)
  before converting.
- **New-project settings** — don't trust a template's `SWIFT_VERSION` or isolation
  defaults; set them in the `.xcconfig` as
  [`swift-language-mode-and-concurrency.md`](./swift-language-mode-and-concurrency.md)
  describes.

## 5. Upgrade procedure

Upgrade Xcode as **its own change**, never mixed with feature work.

1. Read the release notes for every Xcode version between the pinned one and the
   target, and the Swift release notes for the matching compiler.
2. On a branch: install the new Xcode beside the old one, update `.xcode-version`,
   point CI at the new version.
3. Clean build (delete derived data). Triage new **errors** first, then new
   **warnings** — a new Swift version usually adds diagnostics. Fix them, or
   suppress a specific one in source with a reason; never turn off the CI
   warnings gate to get through an upgrade.
4. Run the full test suite and launch the app on the oldest supported iOS version
   in the Simulator, and on the newest.
5. Confirm every CI simulator destination still exists on the new runner image.
6. Merge, and tell the team to install the new Xcode the same day — a mixed team
   produces project-file churn.

A **Swift language mode** change (Swift 5 → 6) is a separate migration, not part of
an Xcode upgrade: see
[`swift-language-mode-and-concurrency.md`](./swift-language-mode-and-concurrency.md).

## Sources

Verified 2026-11-19:

- Xcode 27 release notes:
  https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes
- Xcode 27.2 release notes:
  https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes
- Xcode 27 release summary (requirements, deployment targets, removals):
  https://blakecrosley.com/blog/xcode-27-release
- xcodes (reads `.xcode-version`): https://github.com/XcodesOrg/xcodes
- Xcode release notes: https://developer.apple.com/documentation/xcode-release-notes/
- Xcode system requirements and compatibility: https://developer.apple.com/support/xcode/
- App Store Connect SDK minimum requirements:
  https://developer.apple.com/news/upcoming-requirements/
- Swift 6.4 release: https://www.swift.org/blog/swift-6.4-released/
- App Store adoption figures: https://developer.apple.com/support/app-store/
