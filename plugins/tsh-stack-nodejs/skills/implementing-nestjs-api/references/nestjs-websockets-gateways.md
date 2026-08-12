# NestJS 11 WebSocket Gateways

Use this reference when a NestJS 11 feature needs a real-time channel and the team must choose between Socket.IO and the `ws` adapter.

## Table of Contents

- [Choose the transport](#choose-the-transport)
- [Package baseline](#package-baseline)
- [Adapter comparison](#adapter-comparison)
- [Composition-root selection](#composition-root-selection)
- [Gateway boundaries](#gateway-boundaries)
- [Decision Points](#decision-points)
- [Official references](#official-references)

## Choose the transport

Use a WebSocket gateway for bidirectional interaction or server-push updates where the client can send messages and receive unsolicited messages over a long-lived connection.

- Prefer polling when periodic freshness is sufficient, clients are intermittently connected, or the simplest request/response operational model matters.
- Prefer server-sent events (SSE) for one-way server-to-client notifications over HTTP when the client does not need to send messages on the same channel.
- Choose a gateway only when the connection lifecycle, bidirectional protocol, or real-time fan-out justifies its operational and client-compatibility cost. Do not introduce WebSockets for a one-way notification that SSE or polling serves clearly.

## Package baseline

`@nestjs/websockets` is required for both adapter routes.

| Route | Required packages | Client protocol |
| --- | --- | --- |
| Socket.IO | `@nestjs/websockets` and `@nestjs/platform-socket.io` | Socket.IO client protocol |
| Native WebSocket | `@nestjs/websockets`, `@nestjs/platform-ws`, and `ws`; add `@types/ws` when code types `ws` values directly | Native WebSocket protocol |

Keep the Nest packages on the same compatible NestJS 11 release line. Do not treat a Socket.IO client as interchangeable with a native browser `WebSocket` client; select the protocol and adapter together.

## Adapter comparison

| Concern | `@nestjs/platform-socket.io` | `@nestjs/platform-ws` with `ws` |
| --- | --- | --- |
| Required packages | `@nestjs/websockets` + `@nestjs/platform-socket.io` | `@nestjs/websockets` + `@nestjs/platform-ws` + `ws`; `@types/ws` for direct `ws` typing |
| Namespaces | Native Socket.IO namespaces | No native namespaces; approximate separation with servers mounted on different paths |
| Rooms and broadcasting | Built-in rooms and broadcast operations | No built-in rooms; implement membership and fan-out at the application or infrastructure boundary |
| Acknowledgements and reconnection | Built-in acknowledgements and client reconnection support | No built-in acknowledgements or reconnection; define them in the protocol and client |
| Client compatibility | Existing Socket.IO clients and their protocol | Native browser `WebSocket` clients and other clients speaking the WebSocket protocol |
| Message format | Socket.IO event names and payloads | Nest's `WsAdapter` expects `{ event, data }`; configure its `messageParser` when the wire format differs |
| Throughput and overhead | Feature-rich protocol with additional protocol overhead | Lower-overhead, efficient native WebSocket route, with fewer built-in features; no benchmark is implied |
| Horizontal scaling | Use a shared adapter, such as a Redis adapter, to broadcast across load-balanced instances | Solve cross-instance fan-out explicitly with an appropriate shared transport or broker; a local connection list is insufficient |

Default rule: prefer `@nestjs/platform-ws` for a native browser `WebSocket`, a simple JSON envelope, and a lower-overhead requirement; prefer `@nestjs/platform-socket.io` when rooms, namespaces, acknowledgements, automatic reconnection, transport fallback, or an existing Socket.IO client is genuinely required.

## Composition-root selection

Choose the adapter once at the composition root, not inside a feature slice. For the native route, the Nest composition root uses the documented switch:

```ts
app.useWebSocketAdapter(new WsAdapter(app));
```

Import `WsAdapter` from `@nestjs/platform-ws` and apply it before the application starts accepting WebSocket traffic. The `WsAdapter` message parser expects the `{ event, data }` envelope by default and accepts a `messageParser` option for an established alternate wire format. Keep that translation at the transport boundary.

Do not select different WebSocket adapters opportunistically in individual gateways. If a deployment needs multiple protocols, make each protocol and its path explicit at the composition boundary and document its scaling/fan-out design.

## Gateway boundaries

A gateway is a transport boundary, not an application-service replacement.

- A gateway validates message DTOs like HTTP DTOs, maps messages to `CommandBus` or `QueryBus` calls, and owns no business orchestration.
- Put the gateway and its message DTOs in the owning feature slice's `api/` folder. Keep handlers, domain rules, ports, and persistence below that boundary.
- A gateway never accepts an Express `Request` or `Response`, a TypeORM entity, or a peer feature's repository.
- Authenticate at the connection handshake and authorize again per message when the action or resource requires it. Do not assume an HTTP session automatically authorizes a WebSocket message.
- Treat reconnects, duplicate messages, ordering, and retry behavior as explicit protocol concerns. Commands must remain idempotent where retries can repeat a request.
- Keep rooms, subscriptions, and fan-out policy in a defined application or infrastructure boundary; do not hide cross-feature orchestration in the gateway.

The same vertical-slice, CQRS, DTO, and dependency-direction rules apply to gateways as to controllers.

## Decision Points

Resolve these choices from the target repository's clients, operational topology, and established conventions. Record the selection before implementing a new channel; do not make one adapter a TSH-wide standard.

| Decision | Selection guidance | Consequence to document |
| --- | --- | --- |
| Adapter | Socket.IO for its built-in protocol features; `ws` for native WebSocket compatibility and a simpler, lower-overhead route | Client protocol, fallback behavior, namespaces/rooms, and lifecycle semantics |
| Message envelope | Nest's `{ event, data }` shape or a repository-approved envelope parsed at the adapter boundary | Event naming, validation, versioning, errors, correlation, and compatibility rules |
| Scaling and fan-out | Socket.IO shared adapter, or an explicit shared transport/broker for `ws` | Membership state, delivery guarantees, ordering, reconnect behavior, backpressure, and failure recovery across instances |

## Official references

Verify release-sensitive APIs and adapter behavior against the official NestJS documentation:

- [NestJS WebSocket gateways](https://docs.nestjs.com/websockets/gateways) — gateway setup, package baseline, and protocol context.
- [NestJS WebSocket adapters](https://docs.nestjs.com/websockets/adapter) — `WsAdapter`, the composition-root switch, message parsing, and native WebSocket limitations.
- [NestJS WebSocket overview](https://docs.nestjs.com/websockets) — transport integration and adapter model.
