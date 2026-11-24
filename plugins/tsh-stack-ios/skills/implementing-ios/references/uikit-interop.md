# UIKit interop

When one framework has to host the other, and how to work in an app that is UIKit at
its core. SwiftUI is the default for new screens in new apps; an existing UIKit app
keeps UIKit unless it already hosts SwiftUI or the user asks to start.

## 1. Working in a UIKit app

Read how the app already does it, then follow it:

- **Screen structure** — MVC, MVVM with Combine or closures, VIPER, coordinators.
  Add the new screen the same way; don't introduce a second pattern in one feature.
- **Layout** — Auto Layout in code, storyboards or XIBs. Match the feature you are in.
  New code in an all-code app never adds a storyboard.
- **Navigation** — coordinators or the view controllers themselves. Extend what is
  there.
- **Still apply** the rules that are framework-free: no logic in the view layer,
  dependencies injected through initializers, async/await over completion handlers in
  new code, Keychain for secrets, localised strings, Dynamic Type
  (`UIFont.preferredFont(forTextStyle:)` with `adjustsFontForContentSizeCategory`),
  accessibility labels, no force unwraps outside `@IBOutlet`s.
- **Main-thread UI work** is guaranteed by `@MainActor` on view controllers and views;
  don't add `DispatchQueue.main.async` around UI updates in async code.

## 2. SwiftUI inside UIKit

```swift
let screen = OrdersScreen(orders: dependencies.orders)
let controller = UIHostingController(rootView: screen)
navigationController?.pushViewController(controller, animated: true)
```

- **`UIHostingController`** hosts a SwiftUI screen in a UIKit navigation stack, tab,
  or modal. The UIKit side keeps owning navigation; the SwiftUI screen reports intent
  through closures (`onFinish`, `onSelect`) rather than reaching for the navigation
  controller.
- **`UIHostingConfiguration`** (iOS 16) renders SwiftUI content inside a
  `UICollectionViewCell` or `UITableViewCell`:

  ```swift
  cell.contentConfiguration = UIHostingConfiguration {
      OrderRow(order: order)
  }
  ```

- Inject dependencies into the hosted view through its initializer or `.environment`
  on the root view — the hosting controller has no other way to give them.
- When the app adopts SwiftUI screen by screen, new screens are SwiftUI and are
  presented by the existing UIKit navigation. Rewriting navigation is a separate,
  deliberate change.

## 3. UIKit inside SwiftUI

```swift
struct MapPreview: UIViewRepresentable {
    let coordinate: CLLocationCoordinate2D

    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView()
        map.isUserInteractionEnabled = false
        return map
    }

    func updateUIView(_ map: MKMapView, context: Context) {
        map.setCenter(coordinate, animated: false)
    }
}
```

- **Check for a SwiftUI equivalent first.** Many former reasons to wrap UIKit (maps,
  web content, text views, photo picking, sharing) have SwiftUI APIs on recent iOS
  versions; wrap only when the deployment target or a missing feature requires it.
- **`makeUIView`** creates and configures once; **`updateUIView`** pushes SwiftUI
  state into the view and must be cheap and idempotent — it runs on every relevant
  state change.
- **Delegates and callbacks** go through a `Coordinator` (`makeCoordinator()`), which
  forwards events into SwiftUI through a `Binding` or a closure.
- **`UIViewControllerRepresentable`** for controllers (document pickers, mail
  composer, a legacy screen). Dismissal is driven by SwiftUI state, not by the
  controller dismissing itself.
- Keep representables thin: no business logic, no network calls — they are adapters.

## 4. Observation in UIKit

- `@Observable` models work in UIKit too. On iOS 26 and later, UIKit records which
  `@Observable` properties these methods read and calls them again when one changes:

  | Class | Tracked methods |
  | --- | --- |
  | `UIViewController` | `updateProperties()`, `viewWillLayoutSubviews()`, `viewDidLayoutSubviews()`, `updateViewConstraints()`, `updateContentUnavailableConfiguration(using:)` |
  | `UIView` | `updateProperties()`, `layoutSubviews()`, `updateConstraints()`, `draw(_:)` |
  | `UIButton` | `updateConfiguration()`, `configurationUpdateHandler` |
  | Collection and table view cells, table headers and footers | `updateConfiguration(using:)`, `configurationUpdateHandler` |
  | `UIPresentationController` | `containerViewWillLayoutSubviews()`, `containerViewDidLayoutSubviews()` |

  Put model-to-view updates in `updateProperties()`; it runs before layout.
- **iOS 18:** the same tracking works once `Info.plist` sets
  `UIObservationTrackingEnabled` to `YES`. `updateProperties()` does not exist there;
  use `viewWillLayoutSubviews()` / `layoutSubviews()`.
- **iOS 17:** no automatic tracking. Wrap the reads in `withObservationTracking`
  and re-register from its `onChange` handler, hopping to the main actor.
- Don't introduce Combine in new code just to bind a model to a UIKit view.

## Sources

Apple documentation, verified 2026-11-19:

- [UIHostingController](https://developer.apple.com/documentation/swiftui/uihostingcontroller)
- [UIHostingConfiguration](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Automatic observation tracking](https://developer.apple.com/documentation/uikit/automatic-observation-tracking)
- [Updating views automatically with observation tracking in UIKit](https://developer.apple.com/documentation/uikit/updating-views-automatically-with-observation-tracking-in-uikit)
- [UIObservationTrackingEnabled](https://developer.apple.com/documentation/bundleresources/information-property-list/uiobservationtrackingenabled)
