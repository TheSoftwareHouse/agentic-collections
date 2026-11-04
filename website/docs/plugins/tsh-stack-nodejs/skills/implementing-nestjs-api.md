---
title: Implementing NestJS API
sidebar_label: implementing-nestjs-api
sidebar_position: 3
description: Guides implementation and review of NestJS 11 REST APIs with TypeScript, @nestjs/cqrs, TypeORM 0.3 and @nestjs/platform-express, covering vertical slices, CQRS boundaries, persistence, contracts and testing.
sources:
  - plugins/tsh-stack-nodejs/skills/implementing-nestjs-api/
sources_hash: "d0d90ead898d18b5fa7e738c77f7e8ef49cdd5393b5d0e4d7429e601292f0f65"
---

# Implementing NestJS API

**Plugin:** [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/)  
**Invoke:** `/tsh-stack-nodejs:implementing-nestjs-api`, and Claude also loads it when the work matches its description  
**Used by:** [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) and the [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) agent, both in `tsh-product-engineering`. When the change targets a stack whose skill is available in the session, they load that skill and apply its checklist alongside the discipline review. Their text names a NestJS stack skill as an example and names no plugin, so it stays silent when none is installed. [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) and [`modelling-types-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs) link to it as the framework layer above them.

NestJS-specific implementation and review guidance for REST APIs built with TypeScript, CQRS, TypeORM and Express: framework boundaries, composition rules and reference-led workflows.

Use it when bootstrapping a NestJS service with the Express adapter, adding or restructuring a vertical feature slice, adding commands, queries, handlers or domain events with `@nestjs/cqrs`, designing cross-feature workflows and module boundaries, implementing TypeORM persistence, repositories or migrations, defining DTO, validation, serialization and error contracts, or reviewing a NestJS REST API change for architectural, security or testability risks.

## Version baseline

The skill targets **NestJS 11.x** with `@nestjs/cqrs`, **TypeORM 0.3** (the `DataSource` era) and `@nestjs/platform-express`. It reads the repository's `package.json` first. If the project is on NestJS 10 or older, or on TypeORM 0.2, the skill stops and says so, because the module composition, `DataSource` and repository guidance does not transfer. The foundation reference sets the runtime baseline at Node.js 20 or above. For the compiler-level constraints this guidance depends on (decorator metadata, `useDefineForClassFields`, `verbatimModuleSyntax`), it points to [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs).

Local repository rules outrank the skill's defaults. It applies where they are silent and records a deliberate deviation instead of silently mixing conventions.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Foundation and vertical slices** | `NestFactory.create()` as the composition root, slice layout under `src/features/` (`api/`, `application/`, `domain/`, `infrastructure/`), dependency direction, and a small shared kernel. No catch-all `common` module and no `SharedModule` that imports every feature |
| **REST API layer** | Controllers map HTTP and dispatch through `CommandBus.execute()` or `QueryBus.execute()`. Request and response DTOs live in the owning feature's `api/` folder, `201 Created` with a `Location` header, idempotency of `PUT` and `DELETE`, which pipeline component owns which concern, and OpenAPI as a contract artifact |
| **CQRS and module boundaries** | `CqrsModule` registered once, handlers local to their feature, constructor-injected ports with runtime tokens, events versus a transactional outbox, sagas only for real asynchronous process management, and a cycle-resolution procedure |
| **TypeORM persistence** | `TypeOrmModule.forRootAsync()` at the composition boundary and `forFeature()` per owned entity, a CLI `DataSource`, repository adapters behind feature-owned ports, transaction ownership in the command handler, N+1, forward-only migrations with `synchronize: false`, locking strategies and parameterized queries |
| **Validation, errors and serialization** | One global validation boundary with `whitelist` and `forbidNonWhitelisted`, nested and array validation, one validation stack per boundary, a safe error contract (`code`, `message`, `correlationId`, optional `details`), one exception filter, and explicit response mapping |
| **Zod with `nestjs-zod`** | Greenfield default is Zod with `nestjs-zod`, while a brownfield `class-validator` codebase gets bounded adoption only. One idiom per vertical slice, per-field coercion, `.strict()` by default |
| **Testing** | Five runner-agnostic layers: handler unit, module wiring, controller and HTTP integration, repository and persistence against a real database, and event and outbox boundary |
| **Configuration, security and observability** | Typed configuration validated before startup, secrets boundary, authentication and authorization seams, Express-edge payload and rate limits, correlation propagation, structured logging with redaction, health and readiness |
| **WebSocket gateways** | Choosing between polling, SSE and a gateway, Socket.IO versus `@nestjs/platform-ws` with `ws`, adapter chosen once at the composition root, and gateways as transport boundaries |
| **Review checklist** | Severity-tagged checks (`[BLOCKER]`, `[HIGH]`, `[MEDIUM]`, `[LOW]`) for modules, both dependency graphs, controllers, handlers, ports, persistence, DTO and error contracts, tests, configuration and security, and gateways |

## How it works

1. **Discover local requirements.** Read repository instructions, package versions, the existing module structure and the feature's acceptance criteria before choosing a pattern.
2. **Load the relevant references** from the loading table, before writing code. For example, read the REST API layer reference before writing any controller.
3. **Define boundaries.** Assign ownership to a vertical slice, expose narrow ports and runtime tokens, and place orchestration above features so that both the TypeScript value graph and the Nest runtime module graph stay acyclic.
4. **Implement the seams.** Controllers and gateways stay at the transport edge and dispatch through the CQRS buses, domain and application code stay transport-neutral, and TypeORM adapters sit behind feature-owned ports.
5. **Add safeguards.** Apply the repository's validation, error, authorization, configuration and observability conventions, then test handlers, module wiring, HTTP behavior and persistence at the appropriate layers.
6. **Verify and review.** Check the compile-time value graph and the Nest runtime module and DI graph independently, then use the review checklist, grouped by severity and artifact.

For a review, the skill loads only the review checklist, applies the checks relevant to the changed artifacts, and traces each finding to the reference that owns the violated rule.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Use vertical feature slices as the default unit of ownership, never global `controllers/`, `services/` or `entities/` folders |
| NEVER | Use `forwardRef()` between feature modules. Remove the bidirectional ownership by changing the dependency direction |
| MUST | Keep module imports and provider dependencies acyclic, with cross-feature workflows in a dedicated process or orchestration slice above the participating features |
| MUST | Export narrow application ports and runtime tokens from a feature, never TypeORM repositories or entities |
| NEVER | Let Express `Request` or `Response` types cross the transport boundary into commands, queries, handlers, domain objects or repositories |
| MUST | Use TypeORM 0.3 `DataSource`-era APIs only, with no 0.2 connection or custom-repository patterns |
| MUST | Keep controllers to HTTP mapping and dispatch through `CommandBus` or `QueryBus` |
| MUST | Apply CQRS proportionally: it does not by itself require event sourcing, a distributed broker, microservices, a generic repository abstraction, DDD aggregates for simple CRUD, or a separate denormalized read model |

## Decisions left to the repository

Several references end in a decision-points table. They tell the model to resolve the choice from the target repository's instructions and conventions rather than turn one project's choice into a TSH-wide standard. These include the URL prefix and versioning strategy, OpenAPI exposure, the pagination envelope, the database vendor, migration command and naming strategy, the test runner and integration database policy, the authentication scheme and authorization model, the logger and tracing stack, rate-limit policy, and the WebSocket adapter. The validation reference adds the validation stack and the canonical error envelope.

## References

| Reference | Load when |
| :-- | :-- |
| Foundation and vertical slices | Starting a service or defining feature ownership |
| REST API layer | Adding controllers, DTOs or HTTP contracts |
| CQRS and module boundaries | Adding handlers or cross-feature interactions |
| TypeORM persistence | Implementing persistence or migrations |
| Validation, errors and serialization | Defining input or output contracts |
| Zod validation with `nestjs-zod` | Adopting or extending Zod DTO validation |
| Testing | Adding or reviewing tests |
| Configuration, security and observability | Configuring runtime cross-cutting concerns |
| WebSocket gateways | Adding a real-time channel |
| Review checklist | Reviewing an existing NestJS change |

## Related skills

- [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) ships in the same plugin and covers the compiler baseline the guidance assumes: the Node `tsconfig`, decorator metadata and class-field semantics.
- `tsh-product-engineering` supplies TSH's discipline-level implementation, review and TDD workflows, independent of framework. The skill treats it as optional.
- `tsh-product-testing` covers E2E and exploratory testing practice beyond the unit and integration layers in the testing reference. Full end-to-end coverage and Playwright organization are outside this skill.

## Source

[`plugins/tsh-stack-nodejs/skills/implementing-nestjs-api/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api/SKILL.md)
