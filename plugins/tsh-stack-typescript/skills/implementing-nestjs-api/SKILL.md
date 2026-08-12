---
name: implementing-nestjs-api
description: "Guides implementation and review of NestJS 11 REST APIs with TypeScript, @nestjs/cqrs, TypeORM 0.3, and @nestjs/platform-express. Use when bootstrapping a service, organizing vertical feature slices, adding CQRS behavior, or implementing and reviewing REST API changes."
---

# Implementing NestJS API

This skill provides NestJS-specific implementation and review guidance for REST
APIs built with TypeScript, CQRS, TypeORM, and Express: framework-specific
boundaries, composition rules, and reference-led workflows.

## When to Use

- Bootstrapping a NestJS service with the Express adapter
- Adding or restructuring a vertical feature slice
- Adding commands, queries, handlers, or domain events with `@nestjs/cqrs`
- Designing cross-feature workflows and module boundaries
- Implementing TypeORM persistence, repositories, or migrations
- Defining DTO, validation, serialization, and error contracts
- Reviewing a NestJS REST API change for architectural, security, or testability risks

## Version Baseline

This skill targets **NestJS 11.x** with `@nestjs/cqrs`, **TypeORM 0.3** (the
`DataSource` era), and `@nestjs/platform-express`.

Read the target repository's `package.json` before applying anything here. If it
is on NestJS ≤10 or TypeORM 0.2, **stop and say so** — the module composition,
`DataSource`, and repository guidance below does not transfer. When a newer major
lands, add its deltas as a reference rather than renaming this skill.

For TypeScript language and compiler-level constraints that this guidance depends
on — decorator metadata, `useDefineForClassFields`, `verbatimModuleSyntax` — see
the sibling [`typescript-conventions`](../typescript-conventions/SKILL.md) skill
in this plugin.

## Applicability and Precedence

Discover the target repository's instructions, architecture, dependencies, and
established conventions first. Those local rules outrank this skill's defaults;
apply this skill where they are silent, and record any deliberate deviation rather
than silently mixing conventions.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Use vertical feature slices as the default unit of ownership; never organize the application around global `controllers/`, `services/`, or `entities/` folders. |
| NEVER | Use `forwardRef()` as a solution between feature modules. Remove the bidirectional ownership by changing the dependency direction. |
| MUST | Keep module imports and provider dependencies acyclic; place cross-feature workflows in a dedicated process or orchestration slice above the participating features. |
| MUST | Export narrow application ports and runtime tokens from a feature; never export TypeORM repositories or entities as its cross-feature API. |
| NEVER | Let Express `Request` or `Response` types cross the transport boundary into commands, queries, handlers, domain objects, or repositories. |
| MUST | Use TypeORM 0.3 `DataSource`-era APIs only; do not introduce TypeORM 0.2 connection or custom-repository patterns. |
| MUST | Keep controllers responsible for HTTP mapping and dispatch through `CommandBus` or `QueryBus`; controllers never contain business orchestration. |
| MUST | Apply CQRS proportionally: separating responsibilities does not by itself require event sourcing, a distributed broker, microservices, a generic repository abstraction, DDD aggregates for simple CRUD, or a separate denormalized read model. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Foundation and vertical slices](./references/nestjs-foundation-and-vertical-slices.md) | Starting a service or defining feature ownership | NestJS baseline, composition root, slice layout, and shared-kernel boundaries |
| [REST API layer](./references/nestjs-rest-api-layer.md) | Adding controllers, DTOs, or HTTP contracts | HTTP mapping, bus dispatch, REST semantics, pipelines, and OpenAPI decisions |
| [CQRS and module boundaries](./references/nestjs-cqrs-and-module-boundaries.md) | Adding handlers or cross-feature interactions | Ports, tokens, events, transactions, acyclic module design, and dependency graphs |
| [TypeORM persistence](./references/nestjs-typeorm-persistence.md) | Implementing persistence or migrations | TypeORM 0.3 `DataSource`, repositories, entities, transactions, and schema changes |
| [Validation, errors, and serialization](./references/nestjs-validation-errors-and-serialization.md) | Defining input or output contracts | Validation pipes, error envelopes, exception filters, and response shaping |
| [Zod validation with `nestjs-zod`](./references/nestjs-validation-with-zod.md) | Adopting or extending Zod/`nestjs-zod` DTO validation | Greenfield/brownfield adoption policy, canonical `createZodDto`/`.parse()` idioms, coercion/strictness rules, and version verification |
| [Testing](./references/nestjs-testing.md) | Adding or reviewing tests | Handler, wiring, HTTP, persistence, event, and outbox test layers |
| [Configuration, security, and observability](./references/nestjs-configuration-security-and-observability.md) | Configuring runtime cross-cutting concerns | Typed config, secrets, authorization seams, correlation, redaction, and health |
| [WebSocket gateways](./references/nestjs-websockets-gateways.md) | Adding a real-time channel | Gateway boundaries, adapter selection, message contracts, and scaling decisions |
| [Review checklist](./references/nestjs-review-checklist.md) | Reviewing an existing NestJS change | Severity-tagged checks for modules, slices, boundaries, persistence, APIs, tests, and security |

## Implementation Procedure

Copy and track this checklist while implementing a change:

```text
Implementation progress:
- [ ] Step 1: Discover local requirements and conventions
- [ ] Step 2: Load the references relevant to the change
- [ ] Step 3: Define the slice, ports, tokens, and dependency direction
- [ ] Step 4: Implement the transport, application, domain, and persistence seams
- [ ] Step 5: Add validation, security, observability, and layered tests
- [ ] Step 6: Verify both dependency graphs and review the resulting change
```

**Step 1 — Discover local requirements.** Read repository instructions, package versions, existing module structure, and the target feature's acceptance criteria before choosing a pattern.

**Step 2 — Load relevant references.** Use the loading table to select only the concern-specific guidance needed for the task; keep detailed implementation patterns in those references. Read them before writing code, not after — for example, read [`nestjs-rest-api-layer.md`](./references/nestjs-rest-api-layer.md) before writing any controller.

**Step 3 — Define boundaries.** Assign ownership to a vertical slice, expose narrow ports and runtime tokens, and place orchestration above features so both the TypeScript and Nest dependency graphs remain acyclic.

**Step 4 — Implement seams.** Keep controllers and gateways at the transport edge, dispatch through CQRS buses, keep domain and application code transport-neutral, and bind TypeORM adapters behind feature-owned ports.

**Step 5 — Add safeguards.** Apply the repository's chosen validation, error, authorization, configuration, and observability conventions, then test handlers, module wiring, HTTP behavior, and persistence at the appropriate layers.

**Step 6 — Verify and review.** Check the compile-time value graph and Nest runtime module/DI graph independently, then use the [review checklist](./references/nestjs-review-checklist.md) to report concrete findings.

## Review Procedure

For review, load [the NestJS review checklist](./references/nestjs-review-checklist.md), apply only checks relevant to the changed artifacts, and report findings grouped by severity and artifact. Trace each finding to the reference that owns the violated rule.

## Related Skills

Optional and may not be installed — treat each as a bonus, never a prerequisite,
and do not block on a missing one:

- [`typescript-conventions`](../typescript-conventions/SKILL.md) — ships in this
  same plugin, so it is always available alongside this skill. Covers the
  compiler and language baseline the guidance above assumes.
- `tsh-product-engineering` — TSH's discipline-level implementation, review, and
  TDD workflows, independent of framework.
- `tsh-product-testing` — E2E and exploratory testing practice beyond the unit
  and integration layers described in [Testing](./references/nestjs-testing.md).
