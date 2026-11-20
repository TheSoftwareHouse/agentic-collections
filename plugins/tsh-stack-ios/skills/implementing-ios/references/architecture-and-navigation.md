# Architecture and navigation

How a feature is laid out, when a screen earns a model, how dependencies reach it, and
how screens are reached. An existing app's architecture wins over everything here.

## 1. Layers

```text
View  ──reads/calls──▶  Screen model (@Observable, main actor)  ──calls──▶  Service  ──▶  API client / store
```

- **Views** render state and forward user intent. Nothing else.
- **Screen models** hold one screen's state and turn intent into service calls.
- **Services** hold the app's behaviour and own no UI state: `OrdersService`,
  `AuthService`. They talk to the API client, SwiftData, the Keychain.
- **Models** are plain value types (`struct Order: Identifiable, Hashable, Sendable`)
  or SwiftData `@Model` classes for persisted data.

### When a screen needs a model

| The screen… | Do this |
| --- | --- |
| Only displays values it is given and forwards taps | No model. Properties and closures. |
| Has local UI state only (a toggle, a sheet flag, a draft) | `@State` in the view. No model. |
| Loads data, validates input, or coordinates more than one service | A screen model. |
| Shares state with sibling screens | That state lives in a service or session in the environment, not in any one screen's model. |

A model for a screen that does nothing is ceremony; a 200-line `body` full of
`Task { }` and `try await` is the opposite failure.

## 2. Feature layout

```text
App/
├── MyApp.swift            # @main, builds the dependencies, injects them
├── AppDependencies.swift  # the composition root
└── Features/
    ├── Orders/
    │   ├── OrdersScreen.swift
    │   ├── OrdersModel.swift
    │   ├── OrderRow.swift
    │   └── OrderDetailScreen.swift
    └── Profile/
Core/
├── Networking/            # APIClient, endpoints, DTOs
├── Persistence/           # SwiftData container, KeychainStore
└── DesignSystem/          # tokens, styles, shared components
```

- **Group by feature, not by kind.** No top-level `Views/`, `ViewModels/`, `Models/`
  folders.
- File name = the main type's name. One main type per file; small private helpers
  may share it.
- When the app grows past a handful of features, or build times hurt, move features
  and `Core` into **local Swift packages** — one per feature plus shared ones. Package
  boundaries make dependencies explicit and let a feature build and test alone.
  How to set the packages up is `configuring-xcode-for-ios`.
- Access control: types are `internal` by default; a package exposes only what other
  modules use as `public`. Never `public` "just in case".

## 3. Dependency injection

```swift
@main
struct MyApp: App {
    @State private var dependencies = AppDependencies.live()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(dependencies.session)
                .environment(\.ordersService, dependencies.orders)
        }
    }
}

extension EnvironmentValues {
    @Entry var ordersService: any OrdersService = UnimplementedOrdersService()
}
```

- **One composition root** builds the live services once (`AppDependencies.live()`)
  and hands them down. Previews and tests build their own.
- **Initializer injection** for a screen model: `OrdersModel(service:)`. The screen
  reads the service from the environment and passes it in.
- **`@Environment`** for what many screens need: an `@Observable` session with
  `.environment(session)`, or a service through an `@Entry` key. The default value of
  an `@Entry` key should fail loudly in debug (an "unimplemented" stub), so a missing
  injection is found in the first run, not in production.
- **Services are `Sendable`** — stateless structs, actors, or main-actor classes — so
  they can sit in the environment and cross into background work. Declare a service
  protocol as `protocol OrdersService: Sendable`.
- **A protocol only when there is a second implementation** — a fake in tests or
  previews counts. A protocol per type by reflex doubles the code for nothing.
- No third-party DI container by default.

## 4. Navigation

```swift
enum Route: Hashable {
    case order(Order.ID)
    case settings
}

@Observable
final class Router {
    var path: [Route] = []
    func show(_ route: Route) { path.append(route) }
    func popToRoot() { path.removeAll() }
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeScreen()
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .order(let id): OrderDetailScreen(orderID: id)
                    case .settings: SettingsScreen()
                    }
                }
        }
        .environment(router)
    }
}
```

- **Value-based navigation.** `NavigationStack(path:)` with a `Hashable` route enum and
  one `navigationDestination(for:)` per stack. Never the deprecated `NavigationView`,
  and never `NavigationLink(destination:)` for programmatic flows.
- **Routes carry identifiers, not models** — `case order(Order.ID)`. The destination
  loads what it needs; a route stays valid when restored from a deep link.
- **One router per navigation stack**, in the environment of that stack. A tab app has
  one per tab.
- **Sheets and full-screen covers** are driven by an optional `Identifiable` item
  (`.sheet(item:)`), owned by the screen that presents them, or by the router when
  other screens must open them.
- **Deep links** (`.onOpenURL`, universal links) parse the URL into routes and set
  `router.path`. Parsing lives in a testable function, not in the view.

## 5. Errors

- Services throw typed domain errors (`enum OrdersError: Error`) or rethrow; they
  never show UI.
- Screen models turn errors into a user-facing message and a recovery action, and log
  the underlying error with `Logger` (`os`), never `print`.
- `CancellationError` is not a failure: never show an alert for it.

## 6. Testing screen models and services

Testing is not this skill's focus, but the architecture above exists so these tests
are cheap:

```swift
import Testing
@testable import Orders

@MainActor
struct OrdersModelTests {
    @Test func failedLoadShowsMessageAndStopsLoading() async {
        let model = OrdersModel(service: FakeOrdersService(result: .failure(URLError(.timedOut))))
        await model.load()
        #expect(model.errorMessage != nil)
        #expect(model.isLoading == false)
        #expect(model.orders.isEmpty)
    }
}
```

- New unit tests use **Swift Testing** (`@Test`, `#expect`, `#require`); UI tests
  stay on XCTest's `XCUIApplication`. Keep existing XCTest suites; don't convert them
  unasked.
- Test screen models and services with fakes; don't unit-test SwiftUI layout.
- Assert every state property a case touches, not only the data — a spinner left
  running is a bug the data alone does not show.

## Sources

Apple and Swift documentation, verified 2026-11-19:

- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Migrating to new navigation types](https://developer.apple.com/documentation/swiftui/migrating-to-new-navigation-types)
- [Entry() macro](https://developer.apple.com/documentation/swiftui/entry())
- [Environment](https://developer.apple.com/documentation/swiftui/environment)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Logger](https://developer.apple.com/documentation/os/logger)
