# SwiftUI views and state

How a SwiftUI view is built and where its state lives. Assumes a deployment target of
iOS 17 or later; below that, swap Observation for `ObservableObject` as the Version
Baseline in `SKILL.md` says.

## 1. Choosing the owner of a piece of state

| The state is… | Declare it as | Example |
| --- | --- | --- |
| Private to one view and a value type | `@State private var` | `isExpanded`, a text field's draft |
| Owned by this view, but it is a model with logic | `@State private var model = ScreenModel(...)` where `ScreenModel` is `@Observable` | a screen model |
| Owned by a parent, read here | a plain `let`/`var` property of the `@Observable` type | `let model: ScreenModel` |
| Owned by a parent, and this view needs a `Binding` into it | `@Bindable var model: ScreenModel` | `TextField("Name", text: $model.name)` |
| A value owned by a parent and written here | `@Binding var value: T` | a reusable toggle row |
| App-wide — a session, a service, the router | `@Environment(Session.self) private var session`, injected with `.environment(session)` | the signed-in user |
| A configuration value with a default | a custom `EnvironmentValues` entry declared with `@Entry` | a feature flag set, a date provider |
| A small user preference that must survive relaunch | `@AppStorage("key")` | a sort order — **never** a token |

Rules that follow:

- **One owner.** A value lives in exactly one place; everyone else gets it by
  property, `@Bindable`, `@Binding` or the environment. Copying model data into a
  view's `@State` creates a second source of truth that drifts.
- **`@State` is private.** Mark it `private`. A `@State` property set from outside
  through the initializer is read once; later changes from the parent are ignored.
- **`@State` re-runs its initial value expression whenever the parent re-creates the
  view struct**, even though SwiftUI keeps the first instance. Keep that initializer
  cheap: no network, no disk. Load in `.task`.
- **Observation tracks what `body` reads.** A view re-renders only when a property it
  actually read changes, so pass the model, not a dozen extracted values. Mark a
  stored property `@ObservationIgnored` when changing it must never re-render.
- **Outside SwiftUI**, observe an `@Observable` model with the `Observations` async
  sequence (iOS 26+) or `withObservationTracking` below that — not by polling and
  not with Combine. UIKit views: [`uikit-interop.md`](./uikit-interop.md).

## 2. The screen model

```swift
@Observable
final class OrdersModel {
    private(set) var orders: [Order] = []
    private(set) var isLoading = true // nothing loaded yet; see below
    private(set) var errorMessage: String?

    private let service: OrdersService

    init(service: OrdersService) {
        self.service = service
    }

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            orders = try await service.recent()
        } catch is CancellationError {
            // The view went away; keep what is on screen.
        } catch {
            errorMessage = String(localized: "Couldn't load your orders.")
        }
    }
}
```

- `final class`, `@Observable`, main-actor isolated (the default in a target set up by
  `configuring-xcode-for-ios`; otherwise annotate `@MainActor`).
- Each piece of screen state is its own property — the data, `isLoading` and
  `errorMessage` — and each is `private(set)`; the view changes them only through
  methods.
- **Start in the loading state.** The first frame renders before `.task` runs; with
  `isLoading = false` an unloaded screen looks like a loaded empty one and flashes
  "No orders yet".
- **`load()` keeps the properties consistent:** it clears the error when it starts
  and resets `isLoading` in a `defer`, so no exit path leaves a spinner running or a
  stale error showing.
- User-facing messages are localised here; the raw error is logged, not shown.

## 3. The view

```swift
struct OrdersScreen: View {
    @State private var model: OrdersModel

    init(orders: OrdersService) {
        _model = State(initialValue: OrdersModel(service: orders))
    }

    var body: some View {
        content
            .navigationTitle("Orders")
            .task { await model.load() }
            .refreshable { await model.load() }
    }

    @ViewBuilder
    private var content: some View {
        if model.orders.isEmpty {
            if model.isLoading {
                ProgressView()
            } else if let message = model.errorMessage {
                ContentUnavailableView {
                    Label(message, systemImage: "exclamationmark.triangle")
                } actions: {
                    Button("Try again") { Task { await model.load() } }
                }
            } else {
                ContentUnavailableView("No orders yet", systemImage: "bag")
            }
        } else {
            List(model.orders) { order in
                OrderRow(order: order)
            }
        }
    }
}
```

- **Render every state** — loading, failed, empty and loaded — and decide which one in
  a single place (`content`), so the order of the checks is visible. A screen that
  renders only the loaded list is unfinished.
- With data already on screen, a failed refresh keeps the data; show the error less
  intrusively (an alert or an inline banner) rather than replacing the list.

- Load in `.task`: SwiftUI cancels it when the view disappears. Use `.task(id:)` when
  the load depends on a value, so a change restarts it.
- A `Task { }` inside a **button action** is fine — it is user-initiated, and the
  model still owns the work.
- `ContentUnavailableView` (iOS 17) is the system's empty and error state; use it
  unless the design system has its own.

## 4. Composition

- **Small views.** Extract a subview when a piece of `body` has a name, is reused, or
  makes `body` hard to read — not to save lines. A subview is a `struct`, not a
  computed property, when it has its own state or is reused elsewhere.
- **Pass the narrowest input.** A row takes the `Order`, not the screen model.
- **Actions as closures.** A reusable view takes `onSelect: (Order) -> Void`; it never
  reaches into a parent's model.
- **Custom modifiers** (`ViewModifier` plus a `View` extension) for styling repeated
  across screens; **custom styles** (`ButtonStyle`, `LabelStyle`) for controls.
- **No `AnyView`** to make branches type-check — use `@ViewBuilder` or `Group`.
- **Stable identity.** Collections use `Identifiable` models with a real ID, never
  `\.self` on a mutable value or array indices.
- **No `GeometryReader` for layout** a stack, `frame`, `containerRelativeFrame` or a
  custom `Layout` can express. It sizes to its proposal and breaks parent layout.

## 5. Strings, assets, accessibility

- **Strings.** Literals passed to `Text`, `Button`, `Label` and `navigationTitle` are
  already `LocalizedStringKey`s and land in the String Catalog (`.xcstrings`) on
  build. Strings built in models use `String(localized:)`. Never concatenate
  translated fragments; use interpolation so translators see the whole sentence.
- **Colours and images** come from the asset catalog or the design system's tokens,
  referenced through the generated symbols (`Color(.brandPrimary)`,
  `Image(.logo)`), never a hard-coded `Color(red:green:blue:)` or a string name.
- **Fonts** use text styles (`.font(.headline)`), or `.custom(_:size:relativeTo:)` for
  brand fonts, so Dynamic Type scales them. Avoid fixed frame heights around text.
- **Accessibility.** An icon-only `Button` gets a label (`Label("Delete",
  systemImage: "trash").labelStyle(.iconOnly)` or `.accessibilityLabel`); decorative
  images are `Image(decorative:)`; a custom control that combines elements uses
  `.accessibilityElement(children: .combine)`. Check the largest Dynamic Type size
  in a preview.

## 6. Previews

```swift
#Preview("Loaded") {
    NavigationStack {
        OrdersScreen(orders: PreviewOrdersService(result: .success(Order.samples)))
    }
}

#Preview("Failed") {
    NavigationStack {
        OrdersScreen(orders: PreviewOrdersService(result: .failure(URLError(.notConnectedToInternet))))
    }
}
```

- One `#Preview` per meaningful state; previews use fake services, never the network.
- Sample data lives next to the model under a `#if DEBUG` extension or in a
  preview-only file, not in production code paths.
- `PreviewProvider` and its preview modifiers (`previewDevice`, `previewLayout`,
  `previewDisplayName` and the rest) are deprecated in Xcode 27; convert one to
  `#Preview` when you touch its file. The compiler warns only once the deployment
  target is iOS 27, so older targets need the habit, not the warning.

## 7. Anti-patterns

| Anti-pattern | Instead |
| --- | --- |
| `URLSession`, `ModelContext` or `UserDefaults` calls inside a view | A service called by the screen model |
| `@StateObject` / `ObservableObject` in new iOS 17+ code | `@State` + `@Observable` |
| A screen that renders only the loaded data | Loading, failed, empty and loaded all rendered |
| `isLoading = false` set by hand on each exit path | `defer { isLoading = false }` |
| `onAppear { Task { await load() } }` | `.task { await load() }` |
| `@State var item: Item` set from the parent's initializer and expected to update | A plain property, or `@Binding` |
| `AnyView` to unify branches | `@ViewBuilder` |
| `ForEach(items.indices, id: \.self)` | `ForEach(items)` with `Identifiable` |
| Hard-coded colours, font sizes, user-facing strings | Asset catalog, text styles, String Catalog |

## Sources

Apple and Swift documentation, verified 2026-11-19:

- [Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [Migrating from the ObservableObject protocol to the Observable macro](https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro)
- [SE-0475: Transactional observation of values](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0475-observed.md)
- [ContentUnavailableView](https://developer.apple.com/documentation/swiftui/contentunavailableview)
- [Localizing and varying text with a String Catalog](https://developer.apple.com/documentation/xcode/localizing-and-varying-text-with-a-string-catalog)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes) — Previews, Deprecations: `PreviewProvider`
- [Deprecated preview APIs](https://developer.apple.com/documentation/swiftui/previews-deprecated)
