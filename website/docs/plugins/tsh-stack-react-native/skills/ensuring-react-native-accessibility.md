---
title: Ensuring React Native Accessibility
sidebar_label: ensuring-react-native-accessibility
sidebar_position: 2
description: Accessibility patterns applied while building React Native screens on iOS and Android, from VoiceOver and TalkBack roles and labels to focus, large text, contrast and reduced motion.
sources:
  - plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility/SKILL.md
  - plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility/references/
  - plugins/tsh-stack-react-native/agents/react-native-code-reviewer.md
sources_hash: "12c54c0cf33efc97e18277d0e598380e1086dcf1dc19795a58aca346c48fe409"
---

# Ensuring React Native Accessibility

**Plugin:** [`tsh-stack-react-native`](/docs/plugins/tsh-stack-react-native/)  
**Invoke:** `/tsh-stack-react-native:ensuring-react-native-accessibility` (Claude also loads it when the work matches its description)  
**Used by:** [`implementing-react-native`](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native) lists it as a related skill; the [`react-native-code-reviewer`](/docs/plugins/tsh-stack-react-native/agents/react-native-code-reviewer) preloads it for reviews

Accessibility patterns for React Native screens on iOS and Android: the roles, labels and state that VoiceOver and TalkBack announce, focus and announcements, text that follows the system font size, contrast and motion. They are applied while building, not audited afterwards. The project's component library and its accessible primitives come first; the skill says to check which `role`, label and state props they already set instead of re-implementing them, and to follow the React Native documentation for the version the project pins.

## Build or audit

This skill is for **building** accessible screens. **Auditing** an existing app for violations is [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility) in `tsh-product-testing`, a web skill that may not be installed. When it is not, the skill says to name the gap rather than improvise an audit. Component composition and the rest of the screen conventions are [`implementing-react-native`](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native). The web counterpart is [`ensuring-accessibility`](/docs/plugins/tsh-stack-frontend/skills/ensuring-accessibility) in `tsh-stack-frontend`.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Roles and names** | Every interactive element has a `role` (`button`, `checkbox`, `radio`, `switch`, `tab`, `heading`, `img`, …), which wins over `accessibilityRole`, and a spoken name from its `Text` children or, for an icon-only control, `aria-label`. `button` is for in-app navigation and actions; `link` only opens an external URL. A built-in control (`Switch`, `TextInput`) is preferred over a custom one |
| **Reachability** | One logical item is one screen-reader stop (`accessible` on its container), unless the group holds its own controls, which stay separate stops or are exposed as `accessibilityActions`. A swipe, long-press or drag-only action is also offered through `accessibilityActions` or a visible control |
| **State** | Checked, selected, expanded, disabled and busy go through `aria-checked`, `aria-selected`, `aria-expanded`, `aria-disabled` and `aria-busy`, and sliders and progress bars through the `aria-value*` props, never through colour alone |
| **Focus and announcements** | Focus moves into an opened custom modal or sheet (a native `<Modal>` opens its own window), back to the trigger when it closes and onto the first error after a failed submit, with `AccessibilityInfo.sendAccessibilityEvent(ref, 'focus')`, not the deprecated `setAccessibilityFocus`. Toasts and saved or error messages use `announceForAccessibility`, because `aria-live` is Android-only |
| **Names and noise** | Decorative images and duplicated text are hidden with `aria-hidden`, a label does not repeat the role ("Submit", not "Submit button"), and `accessibilityHint` is only for what the label cannot say |
| **Large text** | `allowFontScaling` stays on for body text, any `maxFontSizeMultiplier` is at least 2, and layouts grow with the text instead of using fixed heights |
| **Colour and contrast** | Information is never conveyed by colour alone. Contrast is 4.5:1 for normal text and 3:1 for large text (thresholds per platform in the reference), in both light and dark appearances |
| **Reduced motion** | `AccessibilityInfo.isReduceMotionEnabled()` is read and `reduceMotionChanged` subscribed to, and automatic and repetitive animation is replaced when the setting is on |
| **Touch targets** | The minimum size is a rule of [`implementing-react-native`](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native); this skill does not restate it |
| **Verification** | A walk with VoiceOver on a physical iPhone and TalkBack on an Android device or emulator, at the largest system text size. In tests, queries go `getByRole` first, then the text-input queries (placeholder, display value), then the other accessible queries (text, label, hint), with `testID` last |

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Give every interactive element a `role` and a spoken name |
| MUST | Make every touch action reachable with a screen reader: accessible grouping, and `accessibilityActions` or a visible control for gestures |
| MUST | Expose state through props, not only through its look |
| NEVER | Disable font scaling on body text or cap `maxFontSizeMultiplier` below 2 |
| NEVER | Convey information through colour alone |
| MUST | Meet the contrast minimums in both appearances |
| MUST | Move screen-reader focus when the context changes, including back to the trigger when a modal or sheet closes, and announce transient content |
| NEVER | Make the screen reader say things twice or say noise |
| MUST | Honour Reduce Motion |

## How it works

1. **Choose roles and components**: a built-in control where one exists, otherwise `role` on the pressable or container, noting the names that differ from `accessibilityRole`.
2. **Shape the focus order**: group each logical item into one stop, offer every gesture as an accessibility action or a visible control, hide decoration, and block content behind a custom modal.
3. **Add names, hints and state**: `aria-label` on icon-only controls, a short hint only when the result is not obvious, form labels tied to inputs, state props, and focus moves and announcements.
4. **Check text, colour and touch**: run the screen at the largest system text size on both platforms, check contrast in both appearances and confirm touch targets meet the minimum in `implementing-react-native`.
5. **Test with assistive technology**: in component tests, `getByRole` assertions come first and a failing one is an accessibility bug, not a test to rewrite with `testID`. Then the human check: swipe through every element with VoiceOver and TalkBack, or name the platform you could not test.

The skill ends with a thirteen-item accessibility checklist covering the same ground.

## References

| Reference | Loaded when |
| :-- | :-- |
| Roles, props and platform differences | Picking a role, choosing between an `aria-*` prop and its `accessibility*` twin, a prop that works on one platform only, announcements and focus, font scaling props, or writing accessibility assertions |

It holds the role and state tables, the label, grouping and custom-action props, a VoiceOver and TalkBack comparison, the font scaling and reduced-motion APIs with a code example, the contrast minimums, and the testing queries.

## Related skills

- [`implementing-react-native`](/docs/plugins/tsh-stack-react-native/skills/implementing-react-native): component composition, the touch-target rule and the rest of the screen conventions.
- [`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility): auditing an existing app, in `tsh-product-testing`.

## Source

[`plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-react-native/skills/ensuring-react-native-accessibility/SKILL.md)
