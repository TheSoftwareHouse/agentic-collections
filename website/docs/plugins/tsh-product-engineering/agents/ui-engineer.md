---
title: UI Engineer
sidebar_label: ui-engineer
sidebar_position: 5
description: Implements UI components and screens from a design reference, fetching the Figma design before writing code and verifying the rendered result against it, in a browser for a web app or in the iOS Simulator for a native iOS app.
sources:
  - plugins/tsh-product-engineering/agents/ui-engineer.md
sources_hash: "8449fa884dd28057fc3d07259cf2273cd5485c8f559436786a1618d3a401daa2"
---

# UI Engineer

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Mention:** `@tsh-product-engineering:ui-engineer`  
**Model:** `sonnet`  
**Tools:** no `tools` list or `disallowedTools` in the frontmatter  
**Skills preloaded:** [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context)

A UI-specialized implementer. It delivers UI changes that match the design reference in spacing, typography, colors, component structure and interaction states, not merely code that compiles. Use it for plan tasks that change rendered UI, especially Figma-backed screens and components, in a web app or a native iOS app.

## Inputs it requires

The delegation must name the plan file path and task IDs, the design reference (Figma URL or node) and where to see the result: the dev server URL for a web app, or the Xcode scheme and Simulator device for a native iOS app. If an input is missing it stops and reports exactly which one. It does not guess a URL, a scheme or a device, or infer a design from existing code.

## The design-first gate

Before writing or editing any markup, layout or styling for a Figma-backed task, the agent fetches and studies the design through the Figma MCP tools available in the session. If no Figma MCP is connected, it stops and reports that the session needs the Figma MCP server enabled, or an exported reference image supplied. It never opens figma.com in a browser to scrape a design and never substitutes a guess for the reference. It studies the design through the MCP response and does not save its own copy into `specifications/**`. The only design file that belongs there is the verification gate's shared `ui-verification/figma-expected.png`, written by the capture worker.

## Responsibilities

1. Reads the plan's Goal, its tasks and the Technical Context, and uses the persisted context as-is.
2. Fetches the design and extracts what the implementation must honor: layout, spacing, typography, design tokens, states and behavior.
3. Implements following the project's existing component patterns, loading the installed stack plugin's skills for the target by name: [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) and [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) from `tsh-stack-frontend` for a web app, [`implementing-ios`](/docs/plugins/tsh-stack-ios/skills/implementing-ios) from `tsh-stack-ios` for a native iOS app. When the matching plugin is not installed, the project's own conventions from the plan's Technical Context govern alone.
4. Verifies the rendered result against the design, per component. A native iOS app follows the Simulator check below. A web app is verified in a real browser with the Playwright CLI: opens a named session, resizes the viewport to the design's breakpoint, goes to the pinned dev server URL, saves a screenshot to an explicit path, reads the image and compares spacing, typography, colors and structure against the design. Every state the design defines (hover, focus, error, empty) gets the same screenshot treatment. Accessibility snapshots, DOM assertions and click-throughs are for navigation only, and a component whose screenshot has not been examined is unverified. It also runs the task's Definition of Done commands verbatim, as scoped. When neither `playwright-cli` nor `npx playwright cli` is available it stops and reports that the machine needs `npm install -g @playwright/cli@latest`.
5. Fixes and re-verifies, up to 5 iterations per component. If differences remain after 5, it stops and reports each remaining gap with what it tried.
6. Updates the plan's checkboxes for its delegated scope only, and never edits Definition of Done or acceptance-criteria text.

The delegated dev server URL is pinned: the agent never switches ports, starts a different server or "corrects" it. Type checks, builds and passing tests are not UI verification.

### Verifying a native iOS screen

A native app has no dev server and no DOM, so the orchestrator's browser gate never runs for it: the agent's own comparison is the task's UI verification. With the delegated scheme and device, unchanged, it resolves the device's UDID and addresses the Simulator by it, never by `booted`. It builds with `xcodebuild` against the project or workspace the plan names, reads the application target's `.app` and bundle id from `-showBuildSettings -json`, boots the device with `xcrun simctl bootstatus -b`, installs the app and launches it with `--terminate-running-process`, and saves a screenshot with `xcrun simctl io <udid> screenshot`, which it reads and compares against the design. It captures the default state first, then every state the design defines, reached through launch arguments (relaunching for each), deep links or debug routes the project already has. It sets dark mode or a text size with `xcrun simctl ui` and resets both straight after capturing that variant. A state it cannot reach without adding code is reported as unverified, never as matched. It then runs the Definition of Done commands and fixes and re-verifies up to 5 iterations per screen.

### Working under the UI verification gate

This applies to a web app only. When the delegation states that the orchestrator's UI verification gate runs after the task, the agent skips browser verification and iteration entirely. It implements from the fetched design, runs the Definition of Done commands, updates its plan checkboxes and hands back, stating in its report that verification is deferred to the gate. Its own browser comparison is not run there.

When the delegation carries a UI verification report with differences, the agent is in fix-application mode. It fixes all listed differences in one pass using the report's exact expected values, never a subset and never re-litigating the verdict. It applies the report's confidence guidance: HIGH means fix exactly as reported, MEDIUM means fix the obvious and flag the unclear, LOW means flag everything back before changing code. It reports the files changed and hands back for a fresh capture and review, and never claims the mismatch is resolved without that pass.

### Authentication and version-control safety

It never bypasses, fakes, seeds or injects authentication state. Logging in through the real sign-in flow with credentials the user provided is allowed, and credentials stay out of plans, reports and committed files. If it lacks credentials it stops and reports which login the page presents. It never runs `git clean`, `git reset`, `git stash`, `git restore` or `git checkout -- <path>`, and reports a blocker instead of discarding pre-existing changes.

## What it returns

A report with the task IDs completed, the files changed, the verification performed (Definition of Done command results plus the screenshot-versus-design comparison outcome per component, saying whether it ran in a browser or the iOS Simulator: matched, unverified states, or each remaining difference), and any blockers with exactly what is needed to clear them, such as a missing MCP, credentials or ambiguous design intent.

## Used by

- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) routes UI tasks backed by a design to it, and sends UI findings and UI verification reports back to it as fixes. Its UI verification gate reference states that the gate runs after the task, so the agent defers rendered-result verification; for a native iOS app the orchestrator closes the item on the agent's own Simulator comparison.

## Source

[`plugins/tsh-product-engineering/agents/ui-engineer.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/agents/ui-engineer.md)
