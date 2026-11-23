# Networking and persistence

How an iOS app talks to an HTTP API and stores data on the device. Services own all
of it; views and screen models never touch `URLSession`, `ModelContext`,
`UserDefaults` or the Keychain directly.

## 1. The API client

`URLSession` with async/await and `Codable`. No networking library by default.

```swift
nonisolated struct Endpoint<Response: Decodable & Sendable>: Sendable {
    var method = "GET"
    var path: String
    var query: [URLQueryItem] = []
    var body: Data?
}

nonisolated struct APIClient: Sendable {
    let baseURL: URL
    let session: URLSession
    let tokens: TokenStore

    func send<Response>(_ endpoint: Endpoint<Response>) async throws -> Response {
        var components = URLComponents(url: baseURL.appending(path: endpoint.path),
                                       resolvingAgainstBaseURL: false)!
        if !endpoint.query.isEmpty { components.queryItems = endpoint.query }

        var request = URLRequest(url: components.url!)
        request.httpMethod = endpoint.method
        request.httpBody = endpoint.body
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let token = try await tokens.current()
        request.setValue("Bearer \(token.value)", forHTTPHeaderField: "Authorization")

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError where error.code == .cancelled {
            throw CancellationError() // a cancelled task, not a network failure
        }
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else {
            throw APIError.status(http.statusCode, data)
        }
        do {
            return try JSONDecoder.api.decode(Response.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }
}
```

(The two force unwraps build a URL from a valid base URL and path; they are the
compile-time-certain case the rule allows. Prefer a `throws` path if the path can
come from user input.)

- **One client, many endpoints.** Each service declares its endpoints; the client
  knows nothing about features.
- **DTOs are not models.** Decode into `Decodable` DTOs that mirror the API, then map
  to the app's models in the service. A backend rename then touches one file.
  Declare DTOs `nonisolated struct … : Decodable, Sendable`: under main-actor default
  isolation their `Decodable` conformance is otherwise main-actor isolated, and
  `send` rejects them.
- **One configured decoder/encoder** (`JSONDecoder.api`), with the API's key and date
  strategies set once — never configured ad hoc per call. Declare it `nonisolated`:
  in a target that defaults to the main actor, a plain `extension` makes `api`
  main-actor isolated, and the `nonisolated` client above cannot read it.

  ```swift
  nonisolated extension JSONDecoder {
      static let api: JSONDecoder = {
          let decoder = JSONDecoder()
          decoder.keyDecodingStrategy = .convertFromSnakeCase
          decoder.dateDecodingStrategy = .iso8601
          return decoder
      }()
  }
  ```
- **Errors are typed** (`enum APIError: Error`) and the service maps them to domain
  errors. A cancelled task makes `URLSession` throw `URLError(.cancelled)`, not
  `CancellationError`; the client maps it, so callers handle cancellation in one
  `catch is CancellationError`. Distinguish offline (`URLError.notConnectedToInternet`), unauthorised (401
  → refresh once, then sign out), and server errors.
- **Retries** only for idempotent requests, with a bound and backoff — never retry a
  `POST` blindly.
- **Base URLs per environment** come from build configuration (`configuring-xcode-for-ios`),
  never `#if DEBUG` string literals scattered in code.
- **App Transport Security stays on.** No `NSAllowsArbitraryLoads`. An exception for a
  local dev server goes in the Debug configuration only.
- **Images:** `AsyncImage` for simple cases; a caching image service only when lists
  of images need it.

## 2. Choosing storage

| Data | Store it in |
| --- | --- |
| Tokens, passwords, keys, anything a thief would want | **Keychain** |
| Small user preferences (sort order, onboarding seen) | `UserDefaults` / `@AppStorage` |
| Structured app data the user creates or that must work offline | **SwiftData** |
| A cache of server responses | `URLCache`, or files in the Caches directory |
| Large files (downloads, media) | Files in Application Support or Caches, with the path stored in SwiftData |

## 3. SwiftData

```swift
@Model
final class Draft {
    @Attribute(.unique) var id: UUID
    var title: String
    var updatedAt: Date

    init(id: UUID = UUID(), title: String, updatedAt: Date = .now) {
        self.id = id
        self.title = title
        self.updatedAt = updatedAt
    }
}
```

- **One `ModelContainer`**, created at the composition root and attached with
  `.modelContainer(container)`. Previews and tests use
  `ModelConfiguration(isStoredInMemoryOnly: true)`.
- **Every read and write goes through a store service** — a protocol plus a class
  wrapping `ModelContext`. No `@Query` and no `ModelContext` in views, including
  simple lists: the screen model calls the store and the view renders the screen
  model's properties.

  ```swift
  protocol DraftStore {
      func recent() throws -> [Draft]
      func save(_ draft: Draft) throws
  }

  final class SwiftDataDraftStore: DraftStore {
      private let context: ModelContext
      init(context: ModelContext) { self.context = context }

      func recent() throws -> [Draft] {
          try context.fetch(FetchDescriptor<Draft>(
              sortBy: [SortDescriptor(\.updatedAt, order: .reverse)]))
      }

      func save(_ draft: Draft) throws {
          context.insert(draft)
          try context.save()
      }
  }
  ```

- The store is created at the composition root from the container's `mainContext`
  and injected like any other service. Screen-model tests use a fake `DraftStore`;
  the store itself is tested against an in-memory container.
- Without `@Query` nothing refreshes on its own: the screen model reloads after its
  own writes, and a change made elsewhere (another screen, a background import) is
  announced by the store or picked up on the next `.task`.
- **Background work** uses a `@ModelActor` with its own context. `@Model` instances are
  not `Sendable`: pass `PersistentIdentifier`s between actors, never model objects.
- **Schema changes ship a migration plan** (`VersionedSchema` + `SchemaMigrationPlan`)
  once the app is released. A shipped schema changed without one loses user data.
- Save explicitly after a meaningful change; don't rely on autosave timing for data
  the user would miss.

## 4. Keychain

- Wrap the Security framework (`SecItemAdd`, `SecItemCopyMatching`,
  `SecItemUpdate`, `SecItemDelete`) once in a small `KeychainStore` service; nothing
  else calls `SecItem*`.
- Use `kSecClassGenericPassword` with a service and account per item, and
  `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`: readable by background work
  after the first unlock since boot, and kept on this device — it neither syncs
  through iCloud Keychain nor moves to a new device in a backup. Drop
  `ThisDeviceOnly` only when the user should keep the item on a new device. No
  non-deprecated class makes an item readable before the first unlock.
- Delete the user's items on sign-out. Keychain items survive app deletion; decide
  deliberately whether a reinstall should see them.

## 5. UserDefaults

- Keys are constants in one place, never string literals scattered across views.
- Only small, non-sensitive values. Never tokens, never personal data, never large
  blobs.

## 6. Privacy

- Every required-reason API the app or its dependencies use (`UserDefaults`, file
  timestamps, disk space, system boot time) is declared in the privacy manifest;
  how is `configuring-xcode-for-ios`.
- Ask for a permission (camera, location, notifications) at the moment the feature
  needs it, after explaining why, never at launch. Handle denial with a path to
  Settings.
- Never log tokens or personal data; use `Logger` with `privacy: .private` for values
  that may contain them.

## Sources

Apple documentation, verified 2026-11-19:

- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- [Restricting keychain item accessibility](https://developer.apple.com/documentation/security/restricting-keychain-item-accessibility)
- [Preventing insecure network connections](https://developer.apple.com/documentation/security/preventing-insecure-network-connections)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
