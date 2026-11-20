---
title: 'TSH Stack: iOS'
sidebar_label: Overview
sidebar_position: 0
description: Conventions for native iOS apps in Swift, SwiftUI-first implementation and the Xcode project, build settings and Swift Package Manager underneath it.
sources:
  - plugins/tsh-stack-ios/.claude-plugin/plugin.json
  - plugins/tsh-stack-ios/README.md
sources_hash: "5918d1bccf652312f11eb2ff6ca89352e86fab80068ccea7ba28e3b191934696"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: iOS

`tsh-stack-ios` carries conventions for native iOS apps in Swift: SwiftUI-first implementation of views, state, screens, navigation, concurrency, networking and persistence, and the Xcode project, build settings and Swift Package Manager setup underneath them.

## Who installs it and where

Install it at **project scope**, into the projects that ship an iOS app, so it travels with the repository. Your discipline plugin (for example [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)) and [`tsh-core`](/docs/plugins/tsh-core/) travel with you at user scope. The install commands live on the [installation page](/docs/getting-started/installation), which renders the repository README, so they are not repeated here. If you added the marketplace before this plugin existed, refresh it first with `/plugin marketplace update tsh-agentic-collections`.

Once installed, skills are invoked as `/tsh-stack-ios:<skill>`. Release notes are on the [changelog page](/docs/changelog/tsh-stack-ios).

## What it ships

<PluginComponents plugin="tsh-stack-ios" />

Both skills are model-invocable: Claude loads them when the work matches their description. The rule the plugin exists to enforce is that **the deployment target is a business decision**: it decides which devices can run the app, so both skills ask for it instead of picking one, and never raise it unasked.

## Version support

| | Written against | Lowest supported |
| :-- | :-- | :-- |
| Xcode | 27.2 | 26, which App Store Connect has required for uploads since 28 April 2026 |
| Swift | 6.4, Swift 6 language mode | Swift 5 mode, migrated module by module |
| iOS deployment target | Asked per project; the greenfield recommendation is the current major minus one | 17 for the default patterns (Observation, SwiftData); older targets get the `ObservableObject` and Core Data equivalents |

On a newer Xcode or iOS, the skills check the current Apple documentation, through `context7` (bundled by `tsh-core`) or developer.apple.com, before applying a version-specific rule.

## Works with

Planning, orchestration and pre-merge review live in [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/), installed at user scope. Its workflows are framework-neutral; these skills supply the iOS conventions they review against. Each side works without the other.

## MCP servers, hooks and agents

This plugin ships no agents, no `.mcp.json` and no hooks.

## Not covered

The plugin README lists these gaps as deliberate scope:

- **Testing** beyond the unit-test shape that screen models and services make possible (Swift Testing). UI tests, snapshot tests and test plans are not covered.
- **Accessibility beyond the basics**: Dynamic Type and labels are rules; a full VoiceOver and audit workflow is not.
- **Release**: signing at scale, TestFlight, App Store submission, fastlane.
- **Other Apple platforms**: macOS, watchOS, tvOS and visionOS.
- **Cross-platform frameworks**: React Native and Flutter.
- **A code reviewer agent**: reviews go through `tsh-product-engineering`.

## Source

- [`plugins/tsh-stack-ios/README.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-ios/README.md)
- [`plugins/tsh-stack-ios/.claude-plugin/plugin.json`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-ios/.claude-plugin/plugin.json)
