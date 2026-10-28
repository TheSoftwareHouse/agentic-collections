# NestJS 11 Configuration, Security, and Observability

Use this reference when configuration, authentication, authorization, security controls, health, logging, tracing, or correlation is in scope for a NestJS 11 API.

## Table of Contents

- [Startup Configuration](#startup-configuration)
- [Secrets Boundary](#secrets-boundary)
- [Authentication and Authorization Seams](#authentication-and-authorization-seams)
- [Express-Edge Defenses](#express-edge-defenses)
- [Correlation Propagation](#correlation-propagation)
- [Structured Logging and Redaction](#structured-logging-and-redaction)
- [Health and Readiness](#health-and-readiness)
- [Composition-Boundary Observability](#composition-boundary-observability)
- [Decision Points](#decision-points)
- [Verification Sources](#verification-sources)

## Startup Configuration

Configuration is an input to application composition, not a global lookup available to every slice.

- Define a typed configuration contract for each concern, such as HTTP, database, messaging, and security settings.
- Validate and normalize configuration before the application starts accepting traffic. Invalid or missing required values MUST fail startup rather than produce a partially configured process.
- Load environment and deployment inputs at one configuration boundary, using the repository's established Nest configuration mechanism or an equivalent composition-root provider.
- Inject the typed configuration contract into modules and providers that need it. A feature, handler, entity, repository, guard, or logger adapter MUST NOT read `process.env` ad hoc deep in a slice.
- Keep defaults explicit and safe. A default is appropriate only when the setting is genuinely optional; do not silently default a security-sensitive or connectivity-critical value.
- Keep configuration validation errors actionable for operators but free of raw values and secret material. Failures may name a missing key or invalid shape, but never print its value.
- Make the startup boundary testable: configuration validation, provider construction, and refusal to listen on invalid input should each have a focused verification.

A configuration object may be mapped from environment variables at the boundary, but the rest of the application should depend on the typed object or injected provider. This keeps configuration access consistent and makes configuration changes visible in module composition.

## Secrets Boundary

Secrets are deployment inputs with a narrow lifetime and ownership boundary.

- NEVER put a secret in source code, a committed configuration file, a fixture, a documentation example, or a test snapshot.
- NEVER write a secret to a log line, metric label, trace attribute, exception message, or HTTP error response.
- Use the target deployment's approved secret injection mechanism and keep retrieval at the configuration or infrastructure boundary.
- Pass only the minimum required secret-derived value to the provider that needs it. Do not place all configuration, credentials, or raw environment values into a globally available object.
- Redact sensitive headers and payload fields before serialization. Do not rely on a downstream log sink to remove data that the application already emitted.
- Use synthetic placeholders in examples and tests. Examples must not contain credential-shaped values.
- Treat connection strings, signing material, session values, API keys, and private certificates as secrets even when their variable names appear harmless.

A secret may be present in process memory when a dependency requires it, but it must not cross into domain objects, commands, events, response DTOs, or general-purpose logging context.

## Authentication and Authorization Seams

Keep authentication and authorization replaceable by expressing them through Nest integration points rather than a product-specific provider or scheme.

| Seam | Responsibility | Boundary rule |
| --- | --- | --- |
| Authentication guard | Establish the caller principal or reject an unauthenticated request. | Keep provider-specific verification inside the guard or its injected adapter. Do not make handlers parse transport credentials. |
| Route/controller decorator | Declare required metadata such as public access or a capability policy. | Decorators describe policy inputs; they do not perform database work or business orchestration. |
| Authorization guard or policy service | Evaluate route-level and resource/application-level access. | Use injected application capabilities when a decision needs domain state; keep the decision outside repositories. |
| Application handler | Re-check authorization for a command or query when access depends on resource state or a non-HTTP entry point. | The handler receives a principal or authorization context, not an Express request or response. |
| Repository | Load and persist data according to an authorized application request. | Authorization decisions NEVER belong in a repository. Do not hide policy in query methods or entity mappings. |

Authentication is normally established at the HTTP boundary, while application handlers must remain safe for messages, jobs, and other non-HTTP entry points. Authorization belongs at the HTTP boundary or in the application layer: guards handle route and principal checks, and application services or handlers handle resource and business-policy checks. Repositories remain persistence adapters and never decide whether an action is allowed.

Do not couple feature code to a named identity product. Define a small principal and authorization-context contract, inject policy capabilities where needed, and preserve the target repository's established scheme. Do not put provider claims, raw headers, or transport objects into domain entities or persistence ports.

## Express-Edge Defenses

Apply resource-exhaustion defenses at the Express edge, before feature handlers and repositories run.

- Enforce a request-body payload-size limit appropriate to each endpoint class. Reject oversized bodies before parsing or business processing where the adapter allows it.
- Apply rate limiting at the edge with a policy that distinguishes public, authenticated, expensive, and mutation routes where the target deployment can support those distinctions.
- Keep edge limits explicit for JSON, URL-encoded, multipart, and any raw or streaming body paths; one default must not accidentally leave an alternate parser unbounded.
- Return a stable, safe client error for rejected size or rate limits. Do not disclose infrastructure details or log the rejected body.
- Include the correlation identifier in the rejection response and structured event, without copying sensitive request content.
- Combine rate and payload limits with upstream protections where available; application-level checks are not a substitute for network or gateway capacity controls.

These controls belong in Express middleware, adapter configuration, or a composition-boundary integration. They do not belong in repositories or in each feature's business handlers.

## Correlation Propagation

Create or accept a correlation identifier at the request edge according to the target repository's trust policy. Do not blindly trust a caller-supplied value when it can be used to spoof operational records; validate its shape and replace it when required.

Propagate the identifier through every synchronous and asynchronous seam:

1. Store it in the request execution context used by middleware, guards, interceptors, filters, and loggers.
2. Attach it to command and query metadata without putting transport request objects in the messages.
3. Preserve it while handlers call application ports and external adapters.
4. Include it in domain-event and integration-event metadata, and in an outbox record when delivery crosses a transaction or process boundary.
5. Copy it into outgoing message or HTTP metadata using the target integration's supported header/envelope mechanism.
6. Restore it at a consumer boundary before handling the message, then emit it in logs, traces, and safe error responses.

Correlation metadata is operational context, not business data. Keep it bounded, do not use it as an authorization credential, and never place personal or credential fields into it. If a message is retried, preserve the original correlation value and add a separate attempt identifier when the platform supports one.

## Structured Logging and Redaction

Use structured events with stable field names rather than interpolated text. Log at the composition boundary through the selected logger and tracing integration, and keep feature logs focused on meaningful application transitions.

The redaction policy MUST be explicit and tested:

- Start from an allowlist of fields useful for diagnosis, such as event name, operation, outcome, duration, route template, status, correlation ID, and trace ID.
- Redact personal fields, including names, contact details, addresses, free-text user content, and identifiers that the target privacy policy classifies as personal.
- Redact credential fields, including authorization material, session values, signing material, private keys, connection credentials, and provider assertions.
- Do not log complete request or response bodies, arbitrary headers, ORM entities, database rows, or exception objects without controlled serialization.
- Scrub nested objects, arrays, error causes, and metadata recursively; a top-level field filter is not enough.
- Keep redaction before the logger, exporter, or trace serializer. Add regression tests for representative nested payloads and failure paths.
- Keep personal data out of metric labels and trace attributes unless an explicit privacy review permits a bounded, non-identifying value.

The general logging, metrics and tracing standard is outside this reference. This reference adds the Nest-specific composition seams and the security boundary; it does not select a logging vendor or duplicate a general observability standard.

## Health and Readiness

Compose health checks at the application/platform boundary, not inside individual feature controllers.

- A liveness check should answer whether the process is running and able to serve its health mechanism. It should not require every downstream dependency.
- A readiness check may depend on critical dependencies required to serve traffic, such as the primary database or a required message transport, according to the deployment contract.
- Optional integrations, reporting systems, and best-effort dependencies MUST NOT make the process unready unless the service contract explicitly requires them for every request.
- Health checks must use bounded timeouts and safe failure handling. Do not let a hung dependency consume the health endpoint indefinitely.
- Expose only the minimum status and component information needed by the caller. Keep connection details, topology, raw exception text, and configuration values out of public responses.
- Separate internal diagnostic detail from the external health response and protect detailed health exposure according to the target deployment policy.
- Ensure startup configuration validation happens before readiness can become healthy; a process with invalid required configuration is not ready.

Health endpoints are transport-facing infrastructure endpoints. Their composition should be explicit in the root module or platform module, with dependency checks injected as small indicators or adapters rather than coupled to feature internals.

## Composition-Boundary Observability

Install observability once at stable composition boundaries:

- request middleware establishes correlation context and safe request metadata;
- global guards, interceptors, and filters cover authentication outcomes, timing, tracing, and safe failure mapping;
- the application bootstrap composes logger, tracer, metrics, health, and external-adapter instrumentation; and
- message consumers restore correlation context before dispatching commands or events.

A feature may emit a domain-specific event, metric, or structured outcome when it owns that semantic fact, but it must not reimplement request logging, redaction, tracing setup, or health registration. Prefer one composition-boundary wrapper over copy-pasted instrumentation in every controller and handler. Keep instrumentation independent of the TypeORM entity and repository APIs so persistence changes do not silently change operational contracts.

Review observability at both boundaries: confirm that an HTTP request and a message/event produce a connected trace or correlation record, and confirm that the same path remains safe when validation, authorization, dependency, or persistence failure occurs.

## Decision Points

Resolve these choices from the target repository's instructions, deployment model, threat model, and established conventions. Do not turn one project's selection into a TSH-wide provider or vendor standard.

| Decision | Acceptable approaches | Selection consequence |
| --- | --- | --- |
| Authentication scheme | The repository's existing session, token, certificate, or equivalent approved scheme; a deliberately public route where appropriate | Keep verification and principal construction behind guards/adapters, document trust boundaries, and test authenticated and unauthenticated entry points. |
| Authorization model | Capability/policy checks, role or scope metadata, resource ownership rules, or a repository-established combination | Keep route checks in guards and resource/business checks in the application layer; define behavior for non-HTTP entry points and deny by default when policy data is absent. |
| Logger and tracing stack | The repository's existing structured logger/tracer, an approved OpenTelemetry-compatible stack, or another established instrumentation path | Preserve stable event fields, redaction, correlation propagation, exporter configuration, and sampling policy across HTTP and message boundaries. |
| Rate-limit policy | A global baseline, route-class limits, identity-aware limits, or an upstream-enforced policy with application edge protection | Document keys, windows, burst behavior, trusted proxy assumptions, failure response, and exemptions; keep payload limits aligned with every parser path. |
| Health endpoint exposure | Internal-only probes, authenticated operational endpoints, or a minimal public liveness/readiness surface | Separate liveness from readiness, restrict detailed diagnostics, define which dependencies are critical, and align status semantics with deployment orchestration. |

Record the selected options in the target repository's architecture or configuration documentation before implementing a new integration. If the repository has no established choice, surface the decision rather than selecting a provider or vendor implicitly.

## Verification Sources

Verify release-sensitive registration and pipeline details against the selected NestJS and Express versions:

- [NestJS configuration](https://docs.nestjs.com/techniques/configuration)
- [NestJS guards](https://docs.nestjs.com/guards)
- [NestJS middleware](https://docs.nestjs.com/middleware)
- [NestJS request lifecycle](https://docs.nestjs.com/faq/request-lifecycle)
- [NestJS health checks](https://docs.nestjs.com/recipes/terminus)
- [NestJS CQRS recipe](https://docs.nestjs.com/recipes/cqrs)
- [Express API](https://expressjs.com/en/4x/api.html)
