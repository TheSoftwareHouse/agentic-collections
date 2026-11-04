---
title: Implementing Lambda Functions
sidebar_label: implementing-lambda-functions
sidebar_position: 2
description: Implements and reviews AWS Lambda handlers in TypeScript, covering the thin-handler and pure-service split, middy middleware ordering, schema validation at the event boundary, the error hierarchy, structured logging, and init-phase work.
sources:
  - plugins/tsh-stack-serverless/skills/implementing-lambda-functions/
sources_hash: "3c1b3944a83d671bd54ddb2cc8a6126d7a0f109c996bc4aadfe1bc1b3b885730"
---

# Implementing Lambda Functions

**Plugin:** [`tsh-stack-serverless`](/docs/plugins/tsh-stack-serverless/)  
**Invoke:** `/tsh-stack-serverless:implementing-lambda-functions`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) and [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) link to it as the owner of everything inside the handler, and the latter's project-structure, library-policy and Step Functions references defer to it for the middleware chain, the test layers and error names.

Implementation and review guidance for the handler layer of an AWS Lambda service: the split between the handler and the service it calls, the middy middleware chain, event validation, the error hierarchy, structured logging, and what a handler may safely assume has already run by the time it executes. It says nothing about how the function is deployed, which is [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service).

Use it when writing or restructuring a Lambda handler, adding an API Gateway endpoint, ordering middy middleware, validating an event with a schema, mapping a thrown error to an HTTP status, deciding what belongs in the init phase, logging from a Lambda, or reviewing a serverless function for testability and security.

## Version baseline

The skill targets AWS Lambda functions deployed with OSLS v4 or Serverless Framework v3, on Node.js 24 (`nodejs24.x`; `nodejs22.x` stays in range until its 2027-04-30 deprecation, but never for a new service), with middy as the middleware framework that the chain-ordering guidance assumes. It reads the repository's `package.json` first. If the project is on a materially different runtime or middleware framework, the skill stops and says so, because the middleware-order guidance does not transfer as-is.

Local conventions outrank the skill's defaults. It discovers the repository's existing handler shape, validation library and error types first, and records a deliberate deviation instead of silently mixing conventions.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Handler and service split** | A handler resolves dependencies, calls the service and shapes the response, with no business logic. The service is a plain function that takes every dependency as a parameter and never imports an infrastructure client at module scope |
| **Init phase** | Config parsing and client construction happen at module scope, once per execution environment. A memoised async accessor must clear its memo on rejection so one transient failure does not poison every warm invocation |
| **Middleware chain** | `before` runs in registration order, while `after` and `onError` run in reverse. The error-rendering middleware is registered after CORS and security headers, so its `onError` runs first and builds the response they decorate. For non-HTTP triggers the HTTP-specific middleware is dropped |
| **CORS** | Credentials are never enabled together with a wildcard origin, because the middleware reflects the request `Origin` and any site could read an authenticated response |
| **Validation** | The whole event is validated against one schema, with the payload type inferred from it (`zod`). Boundary validation checks shape, while business invariants stay in the service |
| **Error hierarchy** | `AppError`, then `HttpError`, then concrete subclasses. Every class sets `name` as a string literal, never `this.constructor.name`, because a bundler can rename classes. Only 4xx messages are rendered verbatim, and 5xx are masked |
| **Logging** | Structured JSON carrying the request id on every line, the deployment stage distinguished from `NODE_ENV`, the `Error` passed as its own argument, and no `console.*` in application code |
| **What is never logged** | Request bodies, authorization headers and cookies. middy 7 ships `omitPaths: []`, so the logging middleware redacts nothing by default, and the whole `headers` and `multiValueHeaders` objects are omitted rather than individual keys |
| **Testing** | Services are tested with fakes passed as parameters, the handler and middleware chain are tested when the chain itself changes, and every real repository has an integration test against the local database to prove the fake |
| **Review checklist** | Severity-tagged checks across handlers, services, middleware, validation and errors, logging, and tests |

## How it works

1. **Discover local conventions**: the validation library, error types and test runner. The test runner is deliberately not settled by the plugin, so the skill follows what the repository uses and asks rather than introducing one where there is none.
2. **Load the relevant references.** The handler and service split before writing any handler, and the middleware chain before touching the chain.
3. **Write inside-out.** The event schema first, then the pure service against that inferred type, then the handler that wires them together.
4. **Order the middleware** by the registration-order rule, dropping the HTTP-specific entries for a non-HTTP trigger.
5. **Add safeguards**: structured logging and tests per the references.
6. **Review** with the checklist and report findings by severity, with the reference that owns each violated rule.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Keep the handler thin, and give the service every dependency as a parameter |
| MUST | Register the error-rendering middleware after the CORS and security-header middleware, never first, and prove the order with a handler-level test asserting `Access-Control-Allow-Origin` on an error response |
| MUST | Validate the whole event against one schema at the boundary and infer the payload type from it |
| NEVER | Enable CORS credentials together with a wildcard origin |
| NEVER | Log request bodies, authorization headers or cookies, in application code or by weakening the logging middleware's redaction |
| MUST | Do expensive, reusable setup at module scope during the init phase and never repeat it inside the handler |

## References

| Reference | Load when |
| :-- | :-- |
| Handler and service split | Writing a handler, or splitting business logic out of one |
| Middleware chain | Ordering middy middleware, or adapting the chain for a non-HTTP trigger |
| Validation and errors | Validating an event, or mapping a thrown error to a response |
| Logging and observability | Adding or reviewing log statements |
| Testing Lambda code | Adding or reviewing tests for a handler or a service |
| Review checklist | Reviewing an existing serverless function change |

## Related skills

- [`configuring-typescript-for-serverless`](/docs/plugins/tsh-stack-serverless/skills/configuring-typescript-for-serverless) holds the compiler and bundler baseline this guidance assumes, including why the bundler alone cannot catch a type error.
- [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) covers how the function this skill implements gets deployed: IAM, concurrency, secrets and the packaged template. It also carries the library policy that settles zod and the logging shape.

## Source

[`plugins/tsh-stack-serverless/skills/implementing-lambda-functions/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-serverless/skills/implementing-lambda-functions/SKILL.md)
