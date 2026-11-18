# Lists and performance

Long lists, measuring speed, and the two threads every React Native app runs on. Load it when
you render a list of unknown or large length, or when someone reports slowness or dropped frames.

## Choosing a list

Docs: [Optimizing FlatList](https://reactnative.dev/docs/optimizing-flatlist-configuration),
[FlashList](https://shopify.github.io/flash-list/).

| Severity | Rule |
| --- | --- |
| NEVER | Render a list of unknown or large length with `ScrollView` plus `.map()`. It mounts every row at once. |
| MUST | Use a virtualised list: `FlatList` by default, FlashList when the project already depends on `@shopify/flash-list` or the list is large enough to need recycling. |
| PREFER | `ScrollView` only for short, fixed content such as a settings screen. |
| MUST | Cover the three UI states on a list: loading, error, and empty through `ListEmptyComponent`. |
| MUST | Check `package.json` before using FlashList. v2 requires the New Architecture; do not add it to a project that has not enabled it. |

## Keys and layout

Docs: [FlatList `keyExtractor`](https://reactnative.dev/docs/flatlist),
[FlashList v2 migration](https://github.com/shopify/flash-list/blob/main/documentation/docs/v2-migration.md),
[FlashList performant components](https://github.com/shopify/flash-list/blob/main/documentation/docs/fundamentals/performant-components.md).

| Severity | Rule |
| --- | --- |
| MUST | Pass a `keyExtractor` returning a stable unique id. The default checks `item.key`, then `item.id`, then falls back to the index. |
| NEVER | Use the array index as the key for a list that can reorder, insert or delete. |
| PREFER | `getItemLayout` on a `FlatList` whose rows have a fixed height that does not depend on text size (system font scaling changes the height of text rows); it removes the need to measure. Skip it when heights vary. |
| NEVER | Put a `key` prop on a FlashList item or on components nested inside it. It breaks view recycling and forces React to rebuild the item. For a `.map()` inside an item, use `key={getMappingKey(id, index)}` from `useMappingHelper()`. |
| NEVER | Pass `estimatedItemSize`, `estimatedListSize` or `estimatedFirstItemOffset` to FlashList v2. They no longer exist; models trained on v1 still suggest them. |
| PREFER | `getItemType` on a FlashList that mixes row shapes (header, ad, row) so recycling reuses a matching view. Keep it fast; it runs very often. |

```tsx
<FlashList
  data={orders}
  keyExtractor={(order) => order.id}
  renderItem={({ item }) => <OrderRow order={item} />}
  ListEmptyComponent={<EmptyOrders />}
/>
```

`OrderRow` renders its root without a `key`.

## Measuring

Docs: [Performance](https://reactnative.dev/docs/performance).

| Severity | Rule |
| --- | --- |
| NEVER | Judge speed, or report a regression, from a development build. JavaScript runs much slower in dev mode. |
| MUST | Measure on a release build, on a real device where possible. |
| NEVER | Leave `console.*` calls in code that ships. In a bundled app they can bottleneck the JavaScript thread, including calls made by logging libraries. |
| PREFER | Strip them at build time with `babel-plugin-transform-remove-console` for production, and keep `no-console` as an ESLint error. |

## JS thread and UI thread

Docs: [Animations](https://reactnative.dev/docs/animations),
[Animated](https://reactnative.dev/docs/animated),
[Reanimated — getting started](https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/getting-started/).

| Severity | Rule |
| --- | --- |
| MUST | Keep heavy work (large parsing, sorting thousands of rows, synchronous loops) off the render path. The JavaScript thread is the one that runs your component code; a blocked one stalls every animation that is not on the native driver. |
| MUST | Set `useNativeDriver` explicitly on every `Animated` animation, and set it to `true` when animating non-layout properties (`transform`, `opacity`): the animation then runs on the UI thread, so a busy JavaScript thread does not stall it. Layout properties (Flexbox, position, `width`, `height`) cannot use the native driver ([Animations — caveats](https://reactnative.dev/docs/animations#caveats)); animate a `transform` instead, or accept the JavaScript driver. Omitting the option defaults to `false` and logs a warning. |
| NEVER | Mix drivers on one animated value; every animation on that value must use the native driver. |
| MUST | When `package.json` has `react-native-reanimated`, animate with it, not `Animated`. Reanimated 4's Babel plugin is `react-native-worklets/plugin`, listed last in `babel.config.js` (Expo adds it automatically). |
