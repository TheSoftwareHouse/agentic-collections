---
name: ensuring-react-native-accessibility
description: "Accessibility patterns for React Native screens on iOS and Android: role and accessibility props on View, Text and Pressable, labels and hints, grouping into one screen-reader stop, checked, selected and expanded state, focus moves and announcements through AccessibilityInfo, system font scaling, contrast, reduce motion, and testing with VoiceOver, TalkBack and getByRole queries. Use when making a mobile screen or control usable with a screen reader or large text."
when_to_use: "Trigger on: a React Native or Expo screen that must work with VoiceOver or TalkBack, choosing role versus accessibilityRole, accessibilityLabel or accessibilityHint wording, an icon-only Pressable with no spoken name, grouping a card into one screen-reader element, announcing a toast or validation error, moving screen-reader focus after a modal opens, Dynamic Type or Android font size breaking a layout, allowFontScaling or maxFontSizeMultiplier, honouring Reduce Motion, or asserting role and state in a React Native component test."
---

# Ensuring React Native Accessibility

Patterns for building React Native screens that work with VoiceOver, TalkBack, large
system text and reduced motion — applied while implementing, not audited afterwards.
React Native has no markup to lean on: every role, name and state a screen reader
announces comes from props you set on `View`, `Text`, `Pressable` and their wrappers.

## Applicability and Precedence

Local repository rules outrank this skill: the project's component library and its
accessible primitives come first — check what they set (`role`, label, state) with a
screen reader or a `getByRole` test rather than re-implementing them. The props here
are the ones documented for React Native 0.88; on a newer major, check the
[accessibility docs](https://reactnative.dev/docs/accessibility) first.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Give every interactive element a role and a spoken name: `role` (it [wins over `accessibilityRole`](https://reactnative.dev/docs/view#role)) and a name from its `Text` children or, for an icon-only control, `aria-label`. Use `button` for in-app navigation and actions; `link` only [opens an external URL](https://reactnative.dev/docs/accessibility#role). Prefer a built-in control (`Switch`, `TextInput`) over a custom one that has to rebuild its semantics. |
| MUST | Make every touch action reachable with a screen reader: one logical item is one focus stop (`accessible` on its container, unless the group holds its own controls — then leave them as separate stops, or group and expose them as `accessibilityActions`), and a swipe, long-press or drag-only action is also offered through `accessibilityActions` or a visible control. |
| MUST | Expose state, not only its look: `aria-checked`, `aria-selected`, `aria-expanded`, `aria-disabled`, `aria-busy`, and the `aria-value*` props on sliders and progress bars. A control that changes colour when toggled but announces nothing is a blocker. |
| NEVER | Disable font scaling on body text (`allowFontScaling={false}`), or cap `maxFontSizeMultiplier` below 2 — Apple recommends letting text [enlarge to at least 200 percent](https://developer.apple.com/design/human-interface-guidelines/accessibility). Layouts grow with the text; no fixed heights on text containers. |
| NEVER | Convey information through colour alone: error states need an icon or text besides the red border; status indicators need labels, not just coloured dots ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)). |
| MUST | Meet contrast minimums: 4.5:1 for normal text, 3:1 for large text (thresholds per platform in the reference) — the thresholds [Apple](https://developer.apple.com/design/human-interface-guidelines/accessibility) and [Android](https://developer.android.com/guide/topics/ui/accessibility/apps) publish — in both light and dark appearances. |
| MUST | Move screen-reader focus when context changes — into an opened custom modal or sheet (a native `<Modal>` opens its own window), back to the trigger when it closes, onto the first error after a failed submit — with `AccessibilityInfo.sendAccessibilityEvent(ref, 'focus')`, never the [deprecated `setAccessibilityFocus`](https://reactnative.dev/docs/accessibilityinfo); announce transient content (toasts, saved, errors) with `announceForAccessibility`, because `aria-live` is Android-only. |
| NEVER | Make the screen reader say things twice or say noise: decorative images and duplicated text are hidden (`aria-hidden`), a label does not repeat the role ("Submit", not "Submit button" — [Android](https://developer.android.com/guide/topics/ui/accessibility/apps)), and a hint is added only where the label cannot say what happens. |
| MUST | Honour Reduce Motion: read `AccessibilityInfo.isReduceMotionEnabled()`, subscribe to `reduceMotionChanged`, and replace automatic and repetitive animation when it is on ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)). |

The touch-target minimum is a rule of `implementing-react-native` in this plugin;
this skill does not restate it.

## Implementation Process

1. **Choose roles and components** — a built-in control where one exists; otherwise
   `role` on the pressable or container: `button`, `checkbox`, `radio` in a
   `radiogroup`, `switch`, `tab` in a `tablist`, `heading` for section titles,
   `img` for meaningful images, `progressbar`, `slider`, `alert`. Note the names
   that differ from `accessibilityRole` (`heading`/`header`, `img`/`image`,
   `slider`/`adjustable`) — table in the reference below.
2. **Shape the focus order** — set `accessible` on each container that is one item
   (a list row, a card, a label-and-value pair) so the screen reader reads it as one
   stop, and its `Text` children become its name. A group that contains its own controls
   stays separate stops, or is grouped with those controls exposed as
   `accessibilityActions` (reference §7). Offer every gesture as an
   accessibility action or a visible control. Hide decoration (`aria-hidden`); block
   content behind a custom modal with `aria-modal` (iOS) and
   `importantForAccessibility="no-hide-descendants"` on the background (Android).
3. **Add names, hints and state** — `aria-label` on icon-only controls, a short
   `accessibilityHint` only when the result is not obvious (VoiceOver users can turn
   hints off; TalkBack users cannot), form labels tied to inputs (`aria-labelledby`
   with `nativeID`, Android only — set `aria-label` on the input as well), state
   props from rule 3, `sendAccessibilityEvent` and `announceForAccessibility` for
   focus moves and transient messages. Full prop tables in the reference below.
4. **Check text, colour and touch** — run the screen at the largest system text
   size on both platforms: nothing clipped, overlapped or truncated without a way
   to read it; contrast at the minimums in both appearances; disabled states still
   distinguishable; touch targets meet the minimum set in `implementing-react-native`.
5. **Test with assistive technology** — in component tests, query with
   `getByRole(role, { name })` first and assert state with the accessibility
   matchers — the [RNTL queries](https://github.com/callstack/react-native-testing-library/blob/main/docs/api/queries.md)
   only find elements a screen reader can reach, so a failing `getByRole` is an
   accessibility bug, not a test to rewrite with `testID`. Then the human check:
   VoiceOver on a physical iPhone (the simulator has none; Xcode's Accessibility
   Inspector is a partial substitute) and TalkBack on an Android device or an emulator
   with TalkBack installed ([testing](https://reactnative.dev/docs/accessibility)) —
   swipe through every element, check each is announced with role, name and state,
   activate each control, confirm focus moves and announcements — or name the
   platform you could not test.

## Accessibility Checklist

```text
- [ ] Every interactive element has a role (role, not accessibilityRole, in new code)
- [ ] Every interactive element has a spoken name; icon-only controls have aria-label
- [ ] Labels do not repeat the role; hints only where the result is not obvious
- [ ] One logical item = one screen-reader stop (accessible on the container), unless it holds its own controls
- [ ] Every gesture also available as an accessibility action or a visible control
- [ ] Checked/selected/expanded/disabled/busy state exposed through props
- [ ] Decorative images and duplicated text hidden from the screen reader
- [ ] Focus moves into opened modals, back to the trigger on close, and onto the first error; toasts announced
- [ ] Body text scales with the system; any maxFontSizeMultiplier is >= 2
- [ ] Error states use icon/text in addition to colour
- [ ] Contrast: 4.5:1 normal text / 3:1 large text (thresholds per platform in the reference), light and dark
- [ ] Reduce Motion replaces automatic and repetitive animation
- [ ] Walked through with VoiceOver and TalkBack, or the untested platform named
```

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Roles, props and platform differences](./references/roles-props-and-platform-differences.md) | Picking a role, choosing between an `aria-*` prop and its `accessibility*` twin, a prop that works on one platform only, announcements and focus, font scaling props, or writing accessibility assertions | `role` versus `accessibilityRole` values, state and value props, labelling, hiding and modality, `AccessibilityInfo` methods and events, accessibility actions, font scaling, the contrast table, VoiceOver, TalkBack and RNTL testing |

## Related Skills

- [`implementing-react-native`](../implementing-react-native/SKILL.md) — the screen
  and component composition these patterns apply to, and the touch-target rule.
- Auditing an existing UI for violations is `auditing-accessibility` in
  `tsh-product-testing`, which may not be installed and audits rendered web pages
  rather than native screens — name the gap rather than improvising an audit here.
