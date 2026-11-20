# Concurrency in app code

How app code uses Swift concurrency under Swift 6 language mode. The build settings
that decide the defaults — language mode, default actor isolation, Approachable
Concurrency — belong to `configuring-xcode-for-ios`; this file assumes the TSH
defaults it sets and says what changes when a project differs.

## 1. Know the target's defaults first

Check before writing async code:

| Setting | TSH default for an app target | Effect on the code you write |
| --- | --- | --- |
| Swift language mode | 6 | Data-race safety is checked at compile time; violations are errors |
| Default actor isolation | `MainActor` | Every declaration without an explicit isolation is `@MainActor`. Views, screen models and most app code need no annotation |
| Approachable Concurrency | On | `nonisolated async` functions run on the **caller's** actor (SE-0461); use `@concurrent` to leave it. Conformances can be main-actor isolated (SE-0470) |

A package or target with `nonisolated` default isolation (typical for networking or
model packages) needs explicit `@MainActor` on anything UI-facing. A target still in
Swift 5 mode compiles unsafe code with warnings at most — write the code as if it were
in Swift 6 anyway, so the migration is free.

## 2. Where code runs

- **UI state, views, screen models: the main actor.** Under the default above that is
  automatic; otherwise annotate the type `@MainActor`.
- **Awaiting is not blocking.** `try await apiClient.send(request)` on the main actor
  suspends; `URLSession` does its I/O elsewhere. Network calls do not need to be moved
  off the main actor.
- **CPU-heavy work leaves the main actor explicitly** — decoding a large payload,
  image processing, parsing a file:

  ```swift
  @concurrent
  func decodeCatalog(_ data: Data) async throws -> Catalog {
      try JSONDecoder().decode(Catalog.self, from: data)
  }
  ```

  `@concurrent` runs the function on the global concurrent executor. Its parameters
  and result must be `Sendable`.
- **Types used off the main actor opt out of the default.** In a `MainActor`-default
  target, `struct Catalog: Decodable` is main-actor isolated, and with isolated
  conformances on, so is its `Decodable` conformance — decoding it in a `@concurrent`
  function then fails to compile. Declare such types `nonisolated struct Catalog:
  Decodable, Sendable`, or keep DTOs in a package whose default isolation is
  `nonisolated`.
- **Shared mutable state that is not UI state** lives in an `actor` — a cache, a token
  refresher that must not run twice:

  ```swift
  nonisolated struct Token: Sendable {
      let value: String
      let expiresAt: Date
      var isExpired: Bool { expiresAt <= .now }
  }

  actor TokenStore {
      private var token: Token?
      private var refreshTask: Task<Token, Error>?
      private let refresh: @Sendable () async throws -> Token

      init(refresh: @escaping @Sendable () async throws -> Token) {
          self.refresh = refresh
      }

      /// The stored token, refreshed once when it has expired; concurrent callers
      /// join the refresh already in flight instead of starting another.
      func current() async throws -> Token {
          if let token, !token.isExpired { return token }
          if let refreshTask { return try await refreshTask.value }
          let task = Task { try await refresh() }
          refreshTask = task
          defer { refreshTask = nil }
          let fresh = try await task.value
          token = fresh
          return fresh
      }
  }
  ```

  `Token` is `nonisolated` because under main-actor default isolation its
  `isExpired` would otherwise be main-actor isolated and unusable from the actor.

  Remember actor **reentrancy**: state can change across every `await` inside an actor
  method. Re-check assumptions after each suspension.
- **SwiftData off the main actor** uses a `@ModelActor`, never a `ModelContext` passed
  between actors (see `networking-and-persistence.md`).

## 3. Task lifetime

| Situation | Use |
| --- | --- |
| Load when a view appears | `.task { }` — cancelled when the view goes |
| Reload when an input changes | `.task(id: query) { }` — cancelled and restarted on change |
| A user action (button) | `Task { await model.save() }` in the action |
| Several independent calls at once | `async let`, or `withThrowingTaskGroup` for a dynamic count |
| Work that must outlive the screen (upload, sync) | A service owns the `Task` and its cancellation; not the view |
| Debounced search | `.task(id: query) { do { try await Task.sleep(for: .milliseconds(300)) } catch { return }; … }` — never `try?` on the sleep: it swallows the cancellation and the stale search still runs |

- **Unstructured `Task { }` is a last resort**; it is not cancelled with anything.
  When a type stores one, it cancels it in the right place.
- **`Task.detached` almost never.** It drops priority and task-locals. Use
  `@concurrent` for off-main work.
- **Honour cancellation.** Long loops check `try Task.checkCancellation()`; catch
  `CancellationError` separately and never present it as a failure.
- **No `DispatchQueue`, `DispatchGroup`, semaphores or completion handlers in new
  code.** Wrap a callback API once with `withCheckedThrowingContinuation`, resuming
  exactly once on every path.

## 4. Sendable

- Value types made of `Sendable` parts are `Sendable` implicitly within a module; mark
  `public` ones explicitly.
- Models crossing actors are `struct`s. A class that must cross is `final`, has only
  immutable `Sendable` stored properties, or is an `actor`.
- Closures passed to other isolation domains are `@Sendable` and capture only
  `Sendable` values.
- **Escape hatches need a proof, in a comment, at the site:**

  | Escape hatch | Acceptable when |
  | --- | --- |
  | `@unchecked Sendable` | The type guards all mutable state with a lock (`Mutex` from `Synchronization`, iOS 18+, or `OSAllocatedUnfairLock`) |
  | `nonisolated(unsafe)` | A global or static that is written once before any concurrent access |
  | `@preconcurrency import` | A third-party module not yet annotated — revisit on each update of it |
  | `MainActor.assumeIsolated` | A callback documented to arrive on the main thread from an API that cannot say so in its types |

  Never use one to make a diagnostic go away without understanding it. The usual real
  fix is moving the state onto the right actor or making the type a value type.

## 5. Common diagnostics and their real fixes

| Diagnostic (paraphrased) | Usual fix |
| --- | --- |
| Main actor-isolated property can't be referenced from a nonisolated context | The caller belongs on the main actor too, or the value is passed in as a parameter |
| Sending a non-Sendable value risks data races | Make the type a `Sendable` struct, or keep the work on one actor |
| Capture of non-Sendable type in a `@Sendable` closure | Capture a `Sendable` copy of what you need, not `self` |
| Conformance of a main-actor type to a protocol crosses into nonisolated code | With SE-0470 on, declare the conformance isolated: `extension Model: @MainActor SomeProtocol` |
| Static property is not concurrency-safe | Make it `let` of a `Sendable` type, or isolate it to an actor |

## Sources

Swift documentation and evolution proposals, verified 2026-11-19:

- [The Swift Programming Language — Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [Swift 6 migration guide](https://www.swift.org/migration/documentation/migrationguide/)
- [SE-0461: Run nonisolated async functions on the caller's actor by default](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md)
- [SE-0466: Control default actor isolation inference](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md)
- [SE-0470: Global-actor isolated conformances](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0470-isolated-conformances.md)
- [ModelActor](https://developer.apple.com/documentation/swiftdata/modelactor)
