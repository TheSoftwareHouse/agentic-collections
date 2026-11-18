# TSH Stack: React Native

TSH conventions for React Native 0.88 with React 19, on iOS and Android: the same
standard `tsh-stack-frontend` applies to browser code, plus the rules a device adds.

This is a **stack** plugin, not a discipline plugin. Install it into the projects
that use React Native, at `project` scope, so it travels with the repo. Your
discipline plugin (`tsh-product-engineering` and friends) travels with **you**, at
`user` scope, and so does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-react-native@tsh-agentic-collections
```

If you added the marketplace before this plugin existed, refresh it first with
`/plugin marketplace update tsh-agentic-collections`.

## What's in it

| Component | Invoke | Covers |
| :-- | :-- | :-- |
| `implementing-react-native` | `/tsh-stack-react-native:implementing-react-native` | Any change to React Native app code: Figma-first work, design tokens, the three UI states, named exports and `react` imports, module boundaries. Device rules: text inside `<Text>`, virtualized lists with stable keys, safe areas and keyboard, touch targets (44 pt iOS, 48 dp Android), platform-specific code checked on both platforms, tokens and secrets only in Keychain or Keystore |
| `ensuring-react-native-accessibility` | `/tsh-stack-react-native:ensuring-react-native-accessibility` | Accessibility while building React Native screens: `role`, label and state props that VoiceOver and TalkBack announce, moving screen-reader focus and announcing changes, text that follows the system font size, reduced motion, and a walk with the screen reader on a device |
| `react-native-code-reviewer` agent | `@tsh-stack-react-native:react-native-code-reviewer` | Read-only review of a React Native or Expo change against the installed versions and both skills — security and release hygiene, device rules, framework rules, lists and performance, accessibility, the component checklist — plus the project's type check, linter and tests, returned as a findings report that names what only a device run would settle |

Both skills are model-invocable — Claude loads them when the work matches their
descriptions. The reviewer agent preloads both.

### References

Always available to `implementing-react-native`:

- `component-guidelines.md`
- `react-native-patterns.md`
- `platform-and-device.md`
- `lists-and-performance.md`
- `typescript-for-react-native.md`

Loaded only when the project uses the library:

| Reference | Loads when `package.json` depends on |
| :-- | :-- |
| `expo.md` | `expo` |
| `nativewind.md` | `nativewind` |
| `react-navigation.md` | `@react-navigation/native` |

The core rules assume bare React Native; the conditional references add what Expo,
NativeWind or React Navigation change.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates
arrive with `/plugin update`.

## Not covered

- **UI verification on a simulator or device**, including Maestro flows.
- **Auditing an existing React Native app for accessibility violations.**
  `ensuring-react-native-accessibility` covers building; `auditing-accessibility`
  in `tsh-product-testing` is a web audit.
- **Native module authoring** in Swift, Kotlin or C++.
- **Build and release**: EAS, Fastlane, store submission. Pipelines belong to
  `tsh-platform-engineering`.

## Scope

The routing question for this plugin is *would this guidance change if the project
switched from React Native to a browser app?* If yes, it belongs here. Rules that hold
for both are duplicated on purpose (`.claude/rules/stack-plugin-conventions.md`);
change both copies in the same PR.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change
never reaches them.

- **Skill names carry no version.** Version differences go in the skill's Version
  Baseline and are marked where a rule depends on them.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed.
