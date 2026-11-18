# Roles, props and platform differences

Detail behind the rules in `SKILL.md`: which prop to set, which platform honours it,
and how to check it. Every table is drawn from the linked official page; when the
installed React Native major is newer than 0.88, re-check the page before relying on
a platform note.

## 1. Roles

`role` and `accessibilityRole` do the same job; `role` has
[precedence](https://reactnative.dev/docs/view#role) when both are set. New code uses
`role`. The two vocabularies differ in a few names
([role](https://reactnative.dev/docs/accessibility#role),
[accessibilityRole](https://reactnative.dev/docs/accessibility#accessibilityrole)):

| Intent | `role` | `accessibilityRole` |
| --- | --- | --- |
| Action, in-app navigation | `button` | `button` |
| Opens an external URL in a browser | `link` | `link` |
| Section title, navigation-bar title | `heading` | `header` |
| Meaningful image | `img` | `image` |
| Slider or other adjustable value | `slider` | `adjustable` |
| Search field | `searchbox` | `search` |
| List and its items | `list`, `listitem` | — |
| No role | `none` or `presentation` | `none` |
| Static text | — | `text` |
| Toggle button | — | `togglebutton` (with checked state) |
| Shared by both | `alert`, `checkbox`, `combobox`, `grid`, `menu`, `menubar`, `menuitem`, `progressbar`, `radio`, `radiogroup`, `scrollbar`, `spinbutton`, `summary`, `switch`, `tab`, `tablist`, `timer`, `toolbar` | same |

`link` is for opening an external URL; a pressable that navigates inside the app or
performs an action is a `button`
([role](https://reactnative.dev/docs/accessibility#role)). `grid` applies to
`ScrollView`, `FlatList`, `SectionList` and `VirtualizedList`.

## 2. State and value

Each state has an `aria-*` prop and a field of the older `accessibilityState` /
`accessibilityValue` object ([accessibility](https://reactnative.dev/docs/accessibility)).
New code uses the `aria-*` props.

| State | Prop | Values |
| --- | --- | --- |
| Checked | `aria-checked` | `true`, `false`, `'mixed'` |
| Selected | `aria-selected` | boolean |
| Expanded | `aria-expanded` | boolean |
| Disabled | `aria-disabled` | boolean |
| Busy (being updated) | `aria-busy` | boolean |
| Range value | `aria-valuemin`, `aria-valuemax`, `aria-valuenow` | numbers |
| Value as text | `aria-valuetext` | string |

In `accessibilityValue`, `min` and `max` are required when `now` is set, and `text`
overrides all three ([accessibility](https://reactnative.dev/docs/accessibility)).

## 3. Names, hints and labelling

| Prop | Platform | Behaviour |
| --- | --- | --- |
| `aria-label` / `accessibilityLabel` | both | The string the screen reader speaks. Without it the name is all `Text` children joined with spaces ([text](https://reactnative.dev/docs/text), [accessibilityLabel](https://reactnative.dev/docs/accessibility#accessibilitylabel)). |
| `accessibilityHint` | both | Spoken after the label. VoiceOver reads it only if the user has hints enabled; TalkBack hints cannot be turned off ([accessibility](https://reactnative.dev/docs/accessibility)). |
| `aria-labelledby` / `accessibilityLabelledBy` | Android | Points at the `nativeID` of the labelling element ([view](https://reactnative.dev/docs/view)). iOS ignores it, so keep `aria-label` on the input too. |
| `accessibilityLanguage` | iOS | BCP 47 tag for text in another language than the app's ([accessibility](https://reactnative.dev/docs/accessibility)). |

Writing names:

- Describe purpose and result, not appearance; do not repeat the role ("Submit", not
  "Submit button"); make repeated items unique — each list row names what is unique
  to it ([Android](https://developer.android.com/guide/topics/ui/accessibility/apps)).
- Localise names and hints with the rest of the UI strings.

## 4. Grouping, hiding and modality

`accessible={true}` makes a view one element for VoiceOver and TalkBack: on iOS it
maps to `isAccessibilityElement`, on Android to `focusable`. Touchable elements are
accessible by default; `Text` is accessible by default
([accessibility](https://reactnative.dev/docs/accessibility),
[text](https://reactnative.dev/docs/text)).

| Need | iOS | Android | Both |
| --- | --- | --- | --- |
| Hide one view and its children | `accessibilityElementsHidden` | `importantForAccessibility="no-hide-descendants"` | `aria-hidden` |
| The view is not important, descendants unaffected | — | `importantForAccessibility="no"` | — |
| Ignore siblings of an open custom modal | `aria-modal` (wins over `accessibilityViewIsModal`) | hide the background with `no-hide-descendants` | — |
| Announce changes to a region | — | `aria-live` / `accessibilityLiveRegion` (`polite`, `assertive`) | `announceForAccessibility` |

Sources: [view](https://reactnative.dev/docs/view),
[accessibility](https://reactnative.dev/docs/accessibility).

## 5. Focus and announcements — `AccessibilityInfo`

From [accessibilityinfo](https://reactnative.dev/docs/accessibilityinfo):

| Call | Platform | Use |
| --- | --- | --- |
| `sendAccessibilityEvent(ref, 'focus')` | both | Move screen-reader focus; `ref` is the host component's ref (`ref.current`). The target needs `accessible={true}`. To return focus when a modal or sheet closes, call it on the trigger's ref. `'click'`, `'viewHoverEnter'` and `'windowStateChange'` are Android only. |
| `setAccessibilityFocus(reactTag)` | — | Deprecated; use `sendAccessibilityEvent` with `'focus'`. |
| `announceForAccessibility(text)` | both | Speak a message. Interrupts current speech by default. |
| `announceForAccessibilityWithOptions(text, { queue, priority })` | iOS options | `queue: true` waits behind current speech; `priority` is `'low'`, `'default'` or `'high'`. |
| `getRecommendedTimeoutMillis(ms)` | Android | The user's "Time to take action" setting — use it for toasts and auto-dismissed UI. |

The React Native docs give no timing guidance for `sendAccessibilityEvent`: a focus event sent
in the same commit that mounts the view can be dropped, and `role="alert"` together with a focus
move can be announced twice. Check every focus move with VoiceOver and TalkBack on a device;
if focus does not land, send the event after the next frame.

## 6. System preferences

Query once, then subscribe; `addEventListener` returns a subscription to `remove()`
on unmount ([accessibilityinfo](https://reactnative.dev/docs/accessibilityinfo)).

| Setting | Query | Event | Platform |
| --- | --- | --- | --- |
| Screen reader on | `isScreenReaderEnabled()` | `screenReaderChanged` | both |
| Reduce Motion | `isReduceMotionEnabled()` | `reduceMotionChanged` | both (Android: also true when Developer options set Transition Animation Scale to off) |
| Prefer cross-fade transitions | `prefersCrossFadeTransitions()` | — | iOS |
| Bold text | `isBoldTextEnabled()` | `boldTextChanged` | iOS |
| Reduce transparency | `isReduceTransparencyEnabled()` | `reduceTransparencyChanged` | iOS |
| Invert colours | `isInvertColorsEnabled()` | `invertColorsChanged` | iOS |
| Grayscale | `isGrayscaleEnabled()` | `grayscaleChanged` | iOS |
| High text contrast | `isHighTextContrastEnabled()` | — | Android |

With Invert Colors on, set `accessibilityIgnoresInvertColors` on photos so they are not
inverted ([accessibility](https://reactnative.dev/docs/accessibility)).

```tsx
import { useEffect, useState } from 'react';
import { AccessibilityInfo } from 'react-native';

export function useReduceMotion(): boolean {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
    const subscription = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduceMotion);
    return () => subscription.remove();
  }, []);

  return reduceMotion;
}
```

## 7. Accessibility actions

`accessibilityActions` lists `{ name, label? }` objects and `onAccessibilityAction`
receives `event.nativeEvent.actionName`. Standard names
([accessibility](https://reactnative.dev/docs/accessibility)):

| Name | Platform |
| --- | --- |
| `activate`, `increment`, `decrement` | both |
| `magicTap`, `escape` | iOS |
| `longpress`, `expand`, `collapse` | Android |

A custom action (delete, archive, reply on a swipeable row) takes any `name` and a
localised `label`. Handle `increment` and `decrement` on a `slider` so it can be
operated without dragging. On iOS, handle `onAccessibilityEscape` (the two-finger Z
gesture) to close a custom modal.

## 8. Font scaling

From [text](https://reactnative.dev/docs/text):

| Prop | Default | Behaviour |
| --- | --- | --- |
| `allowFontScaling` | `true` | Text follows the system text-size setting. |
| `maxFontSizeMultiplier` | inherit | Largest scale; `0` means no cap, `>= 1` sets the cap. |
| `adjustsFontSizeToFit` + `minimumFontScale` | `false` | Shrinks text to fit — use sparingly, it works against the user's chosen size. |
| `numberOfLines` | `0` | Truncates with an ellipsis; give truncated text another way to be read in full. |
| `dynamicTypeRamp` | `'body'` | iOS: which Dynamic Type style the text scales with (`caption2` … `largeTitle`). |

Apple recommends that text can be enlarged to at least 200 percent
([HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)),
which is why any cap stays at 2 or above.

## 9. Contrast and target spacing

| Platform | Contrast | Source |
| --- | --- | --- |
| iOS | Up to 17 pt: 4.5:1. 18 pt and above, or bold at any size: 3:1. Check light and dark. | [HIG accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) |
| Android | Under 18 sp, or bold under 14 sp: 4.5:1. All other text: 3:1. | [Android accessibility](https://developer.android.com/guide/topics/ui/accessibility/apps) |

Apple also recommends about 12 pt of padding around bezelled controls and about
24 pt around borderless ones, so neighbouring targets are not hit by mistake
([HIG accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)).
The touch-target minimum itself is a rule of `implementing-react-native`.

## 10. Testing

**VoiceOver (iOS).** Settings → Accessibility → VoiceOver, or the Accessibility
Shortcut. The simulator has no VoiceOver; Xcode's Accessibility Inspector helps, but
test on a device ([accessibility](https://reactnative.dev/docs/accessibility)).

**TalkBack (Android).** Settings → Accessibility → TalkBack → Use service; holding
both volume keys for three seconds toggles it. Emulators need TalkBack installed from
the Google Play Store ([accessibility](https://reactnative.dev/docs/accessibility)).
Google's Accessibility Scanner app checks contrast on a running screen
([Android](https://developer.android.com/guide/topics/ui/accessibility/apps)).

**Walkthrough.** Swipe through the whole screen: every element announced once, in
reading order, with role, name and state; decoration silent; every control
operable; focus lands where the rules say; the screen still works at the largest
text size.

**Component tests (React Native Testing Library).** `*ByRole` matches only elements a
screen reader can focus — `Text`, `TextInput` and `Switch` by default, `Pressable`
and touchables, and `View` only with `accessible` — and skips hidden ones
([queries](https://github.com/callstack/react-native-testing-library/blob/main/docs/api/queries.md)).
Query priority: `getByRole` first, then the text-input queries (`getByPlaceholderText`,
`getByDisplayValue`), then the other accessible queries (`getByText`,
`getByLabelText`, `getByHintText`), and `getByTestId` last
([how to query](https://github.com/callstack/react-native-testing-library/blob/main/docs/guides/how-to-query.md)).

| Assert | Query or matcher |
| --- | --- |
| Role and name | `getByRole('button', { name: 'Save' })` |
| State in the query | `getByRole('checkbox', { checked: true })`; also `disabled`, `selected`, `busy`, `expanded`, `value` |
| Spoken name | `toHaveAccessibleName('Save')` |
| Checked | `toBeChecked()` — `Switch` and `checkbox`, `radio`, `switch` roles; `toBePartiallyChecked()` for `checkbox` |
| Selected | `toBeSelected()` |
| Range value | `toHaveAccessibilityValue({ now: 3, max: 5 })` |

Matchers: [jest-matchers](https://github.com/callstack/react-native-testing-library/blob/main/docs/api/jest-matchers.md).
A test is no substitute for the walkthrough: it proves the props are set, not that
the spoken result makes sense.
