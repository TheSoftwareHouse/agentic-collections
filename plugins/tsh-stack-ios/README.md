# TSH Stack: iOS

Conventions for native iOS apps in Swift — SwiftUI-first implementation of views,
state, screens, navigation, concurrency, networking and persistence, and the Xcode
project, build settings and Swift Package Manager setup underneath them.

This is a **stack** plugin, not a discipline plugin. Install it into the projects
that ship an iOS app, at `project` scope, so it travels with the repo. Your
discipline plugin (`tsh-product-engineering` and friends) travels with **you**, at
`user` scope, and so does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-ios@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `implementing-ios` | `/tsh-stack-ios:implementing-ios` | Any change to iOS app code: SwiftUI views and state with Observation, one owner per piece of state, screen models that render the loading, failed, empty and loaded states, feature layout, dependency injection through initializers and the environment, `NavigationStack` routing and deep links, Swift concurrency in app code, `URLSession` API clients, SwiftData, `UserDefaults` and the Keychain, String Catalogs and Dynamic Type, `#Preview`, and UIKit interop in both directions |
| `configuring-xcode-for-ios` | `/tsh-stack-ios:configuring-xcode-for-ios` | The build side: the Xcode project and targets, buildable folders and the JSON project format, `.xcconfig` configurations and schemes, signing basics, the deployment target, Swift 6 language mode with Default Actor Isolation and Approachable Concurrency, a staged Swift 6 migration, Swift Package Manager and leaving CocoaPods, the privacy manifest, SwiftFormat, `xcodebuild` in CI, and Xcode upgrades |

Both skills are model-invocable — Claude loads them when the work matches their
descriptions.

The rule it exists to enforce, if you read nothing else: **the deployment target is a
business decision.** It decides which devices can run the app, so both skills ask for
it instead of picking one, and never raise it unasked.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates arrive
with `/plugin update`.

## Version support

| | Written against | Lowest supported |
| :-- | :-- | :-- |
| Xcode | 27.2 | 26 — App Store Connect has required it for uploads since 28 April 2026 |
| Swift | 6.4, Swift 6 language mode | Swift 5 mode, migrated module by module |
| iOS deployment target | asked per project; greenfield recommendation is the current major minus one | 17 for the default patterns (Observation, SwiftData); older targets get the `ObservableObject` and Core Data equivalents |

On a newer Xcode or iOS, the skills check the current Apple documentation — through
`context7`, which `tsh-core` bundles, or developer.apple.com — before applying a
version-specific rule.

## Works with

Planning, orchestration and pre-merge review live in `tsh-product-engineering`
(installed at user scope). Its workflows are framework-neutral; these skills supply
the iOS conventions they review against. Each side works without the other.

For a screen built from a Figma design, `orchestrating-feature-implementation` hands
the task to its `ui-engineer` agent, which loads `implementing-ios` and checks the
result against the design with screenshots from the iOS Simulator, through
`xcodebuild` and `xcrun simctl`. That needs `tsh-product-engineering` 0.13.0 or later
and a Mac with Xcode; the browser-based UI verification gate the same plugin runs for
web apps does not apply to an iOS app. The plan's final functional check,
`feature-verifier`, still knows only browser and API scenarios: it has no Simulator
path yet.

## Not covered yet

The gaps are scope, not oversight:

- **Testing** — only the unit-test shape that screen models and services make
  possible (Swift Testing). UI tests, snapshot tests and test plans are not covered.
- **Accessibility beyond the basics** — Dynamic Type and labels are rules; a full
  VoiceOver and audit workflow is not.
- **Release** — signing at scale, TestFlight, App Store submission, fastlane.
- **Other Apple platforms** — macOS, watchOS, tvOS and visionOS. Much of the Swift
  guidance applies; nothing here is written or checked for them.
- **Cross-platform frameworks** — React Native and Flutter are not this plugin.
- **A code reviewer agent** — reviews go through `tsh-product-engineering`.

## Scope

The routing question for this plugin is *would this guidance change if the project
switched runtime target or framework?* If yes, it belongs here. If it would change
when the **reader** switched job, it belongs in a discipline plugin instead.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change never
reaches them.

Two rules that bite hardest here:

- **Skill names carry no version.** `implementing-ios`, never `implementing-ios-27`.
  Versions live in the `description` and each skill's Version Baseline block.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed.
