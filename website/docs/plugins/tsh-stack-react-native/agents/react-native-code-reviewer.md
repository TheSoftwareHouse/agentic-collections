---
title: react-native-code-reviewer
sidebar_label: react-native-code-reviewer
sidebar_position: 1
description: Read-only reviewer for React Native and Expo changes that checks them against the installed versions and the plugin's device, performance and accessibility rules, and runs the project's own checks.
sources:
  - plugins/tsh-stack-react-native/agents/react-native-code-reviewer.md
sources_hash: "aeea6fd3e010c4f8b64808c2e6811dd088b7b85fb561b2543034f20527544372"
---

# react-native-code-reviewer

**Plugin:** [tsh-stack-react-native](/docs/plugins/tsh-stack-react-native/)  
**Mention:** `@tsh-stack-react-native:react-native-code-reviewer`  
**Model:** `opus`  
**Tools:** no `tools` allowlist; `disallowedTools: Write, Edit`  
**Preloaded skills:** [implementing-react-native](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native),
[ensuring-react-native-accessibility](/docs/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility)

Reviews React Native and Expo code changes against the project's React Native, Expo and library
versions and the plugin's device, performance and screen-reader rules. It runs the project's type
check, linter and tests and returns a structured findings report. It does not fix code: it reports,
and the caller decides what to change.

Use it after mobile app code is written or changed, before merge, or when asked to review a React
Native screen, hook or list.

## Responsibilities

| Area                 | What the agent does                                                                                                                                                                                                                  |
| :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scope**            | Expects the delegation to name the change set: a list of files, a branch, a diff or a commit range. If it cannot determine what changed, it says so and reviews nothing rather than guessing a scope.                                |
| **Versions**         | Reads `package.json` first (React Native, React, Expo SDK, NativeWind, React Navigation, FlashList, Reanimated, the secure-storage library) and loads the conditional references for the installed libraries. A version newer than the skill's baseline is checked in current documentation through `context7`; without it, the report says which findings rest on the baseline alone. |
| **Context**          | Opens the changed files and the components, hooks and modules they use and are used by, because a diff alone misses duplication, a reused component that already handles a state, and a list's item component.                      |
| **Lenses**           | Applies six lenses in order: security and release hygiene, device correctness, framework rules, lists and performance, accessibility, and the component and module rules of the skill's checklist.                                   |
| **Project checks**   | Runs the project's own checks in check-only mode: the type check, the linter, the tests for the changed area, and `npx expo install --check` in an Expo project. It never modifies files, installs packages, regenerates native projects or starts a build. |
| **Device limits**    | Cannot run the app or a screen reader, so it names every finding only a device run would settle as unverified on device, with the platform, instead of passing or failing it.                                                         |
| **Local rules**      | Judges against the project's documented convention where it differs from the skills, and says so. Reports only what it has located in the code; unclear intent becomes a question, not a defect.                                     |

## What it returns

1. **Target.** React Native, React, Expo SDK and the relevant library versions, and where each was
   read from.
2. **Verdict.** Approve, or changes needed, in one line.
3. **Findings**, ordered blocker, major, minor. Each has `file:line`, the rule broken and the skill or
   reference it comes from, the consequence on the device and the minimum correction. Repeats of the
   same rule are consolidated.
4. **Unverified on device.** What only a run on iOS, Android or with a screen reader would settle,
   per platform.
5. **Checks executed.** Every command run, verbatim, with pass or fail and the relevant failure
   output.
6. **What passed.** Brief. A clean review reports zero findings plainly; the agent never invents
   issues to seem thorough.

## Used by

No skill in `plugins/` delegates to this agent.

## Related

- [implementing-react-native](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native),
  the device rules and the component checklist the agent applies.
- [ensuring-react-native-accessibility](/docs/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility),
  the screen-reader, font-scaling and motion rules the agent applies.

## Source

[`plugins/tsh-stack-react-native/agents/react-native-code-reviewer.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-react-native/agents/react-native-code-reviewer.md)
