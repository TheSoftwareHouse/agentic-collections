# Formatting, linting and CI

One formatter, configured by a committed file, and a CI build that runs the same
`xcodebuild` commands a developer can run locally. Which checks a given project's
pipeline runs beyond these is that project's decision.

## 1. Formatting: SwiftFormat

New projects use **SwiftFormat** ([nicklockwood/SwiftFormat](https://github.com/nicklockwood/SwiftFormat)),
the most widely used Swift formatter. Do not confuse it with Apple's **swift-format**,
a separate tool bundled with Xcode 16 and later, with a different configuration file.

### Pin it through a build-tools package

Install it as a Swift package, so its version is committed like any other
dependency and every machine and CI runner formats identically:

```text
BuildTools/
├── Package.swift       # SwiftFormat at an exact version
├── Package.resolved    # committed
└── Empty.swift         # an empty file; SwiftPM needs a source in the target
```

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "BuildTools",
    platforms: [.macOS(.v13)],
    dependencies: [
        .package(url: "https://github.com/nicklockwood/SwiftFormat", exact: "0.64.7"),
    ],
    targets: [.target(name: "BuildTools", path: "")]
)
```

- **`exact:`**, unlike app dependencies: a formatter's output changes between
  releases, so an update must be a deliberate change followed by a reformatting
  commit.
- Add `BuildTools/.build` and `BuildTools/.swiftpm` to `.gitignore`.

```shell
swift run -c release --package-path BuildTools swiftformat .          # format
swift run -c release --package-path BuildTools swiftformat --lint .   # check; exit 1 on findings
```

### Configuration

A committed `.swiftformat` at the repository root:

```text
--swift-version 6.4
--language-mode 6
--min-version 0.64.7
--exclude BuildTools,DerivedData,**/.build
```

- `--swift-version` enables the rules that depend on the Swift version; without it
  SwiftFormat silently skips them. Set it to the Swift of the pinned Xcode (6.4 for
  Xcode 27.2) and update it with every Xcode upgrade.
- `--language-mode 6` matches the Swift 6 language mode. Without it SwiftFormat
  assumes Swift 5 mode, whatever `--swift-version` says. A project still in Swift 5
  mode sets `5`.
- `--min-version` fails a run on an older SwiftFormat, so a developer with a stale
  copy cannot reformat the codebase backwards. Bump it with the package version.
- Keep the default rules. Each deviation (`--disable <rule>`, an option change) is a
  team decision, added to the file in its own commit, followed by one reformatting
  commit that touches nothing else — list that commit in `.git-blame-ignore-revs`.
- Run it from the command line, a pre-commit hook and CI, **not as an Xcode build
  phase**: a build phase needs User Script Sandboxing (`ENABLE_USER_SCRIPT_SANDBOXING`)
  turned off for the target, and slows every build.
- The *SwiftFormat for Xcode* editor extension does not pick up a project's
  `.swiftformat` automatically; prefer the command line so everyone uses the
  committed configuration.

### An existing project with another formatter or SwiftLint

**Keep what the project has.** A working `.swift-format`, `.swiftformat` or
`.swiftlint.yml` is a team decision, not a defect. Do not add SwiftFormat beside
another formatter: two tools rewriting the same whitespace produce endless diffs. If
SwiftLint is used only for lint rules (not formatting), it can sit beside SwiftFormat
with its formatting rules disabled — propose that as its own change, never as a side
effect.

## 2. The CI build

CI runs on a **pinned Xcode** ([`xcode-version-and-upgrades.md`](./xcode-version-and-upgrades.md)),
from a clean checkout, with the committed `Package.resolved`.

```shell
# Pick a simulator that exists on the runner image
xcrun simctl list devices available

xcodebuild \
  -project MyApp.xcodeproj \
  -scheme MyApp \
  -configuration Debug \
  -destination 'platform=iOS Simulator,name=<device from the list above>' \
  -onlyUsePackageVersionsFromResolvedFile \
  -resultBundlePath build/TestResults.xcresult \
  SWIFT_TREAT_WARNINGS_AS_ERRORS=YES \
  GCC_TREAT_WARNINGS_AS_ERRORS=YES \
  clean build test
```

| Flag | Why |
| --- | --- |
| `-scheme` | The **shared** scheme; a scheme only in `xcuserdata` does not exist on CI |
| `-destination` | Name a simulator the runner actually has; hard-coding a device that a new runner image dropped is the most common CI break after an Xcode upgrade |
| `-onlyUsePackageVersionsFromResolvedFile` | Fails instead of silently resolving newer versions than `Package.resolved` records |
| `-resultBundlePath` | Keeps the `.xcresult` (test results, coverage, logs) as a build artefact |
| `SWIFT_TREAT_WARNINGS_AS_ERRORS=YES` | Warnings fail CI. Passed on the command line, so local debug builds stay usable |
| `clean build test` | A clean build catches stale-derived-data passes |

- **Warnings fail CI only.** Treating warnings as errors locally blocks every
  experiment; never treating them as errors lets them pile up until nobody reads
  them. A specific warning that must stay can be downgraded in source with Swift
  6.4's `@diagnose` attribute (SE-0522), with a comment saying why.
- Package-only modules can also be tested with `swift test` from the package
  directory when they have no UI or app-host dependency — faster, no simulator.
- Cache SwiftPM checkouts between runs with `-clonedSourcePackagesDirPath <dir>`
  and the runner's cache keyed on `Package.resolved`.
- Run the formatter's lint as a separate step before the build, so a format failure
  reports quickly. On GitHub Actions, add `--reporter github-actions-log` to get
  findings as annotations on the pull request.

Signing for distribution, archives and TestFlight uploads are out of this skill's
scope; the build above needs no signing because it targets the Simulator.

## Sources

Verified 2026-11-19:

- SwiftFormat repository and README (installation, linting, Swift version,
  `--min-version`): https://github.com/nicklockwood/SwiftFormat
- SwiftFormat 0.64.7, latest release on 2026-11-14:
  https://github.com/nicklockwood/SwiftFormat/releases
- Swift 6.4 release (`@diagnose`, SE-0522): https://www.swift.org/blog/swift-6.4-released/
- xcodebuild man page: `man xcodebuild` on a machine with Xcode installed
- Building from the command line with Xcode FAQ:
  https://developer.apple.com/library/archive/technotes/tn2339/_index.html
