# Changelog

All notable changes to `tsh-stack-serverless` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

## [0.1.1] - 2026-10-02

### Fixed

- **One Node runtime.** `library-policy.md` settled on **Node 24 on `arm64`**
  while the Version Baseline of all three skills, the README and two references
  still said **Node.js 22+**. Node 24 is the right one — it is what the OSLS
  boilerplate deploys (`nodejs24.x`, `engines >=24 <25`) and `nodejs22.x` is
  deprecated on Lambda on 2027-04-30 — so every other mention now says 24, with
  22 kept in range for existing services only.
- "OSLS" was never expanded anywhere a newcomer would look. The README now says
  what the `osls` package is.

## [0.1.0] - 2026-09-18

Initial release: portable TSH conventions for AWS Lambda services built with
Serverless Framework or OSLS, covering the compiler, the handler, and the
deployable service as three independent skills.

### Added

- **`configuring-typescript-for-serverless`** — the Node runtime and TypeScript
  version to target, the ESM `tsconfig` baseline for bundler-emitted handler code,
  and how to choose between esbuild and webpack with `ts-loader`. States that the
  bundler is a transpiler, never a type checker, so `tsc --noEmit` runs as a
  separate, mandatory gate; and carries the full bundler-and-ORM pairing table with
  the three offered combinations, their costs, and why Prisma is not offered as the
  esbuild pairing.
- **`implementing-lambda-functions`** — the thin-handler and pure-service split,
  middy middleware chain ordering, event validation against one schema with the
  payload type inferred rather than hand-written, the `AppError` → `HttpError`
  hierarchy with every `name` a string literal, structured logging with the
  request id, and what belongs in the
  init phase versus the handler body, and the rule that every real repository has
  an integration test against the local database. Carries a severity-tagged review checklist
  for existing serverless function changes.
- **`configuring-serverless-service`** — the library policy (what TSH uses, what it
  avoids and why, and the two choices the team has deliberately left open), how a
  serverless project is structured, service and stage configuration, per-function
  definitions, least-privilege IAM with a named carve-out for the actions AWS defines
  no resource type for, per-function reserved concurrency, opt-in VPC attachment,
  secrets passed by identifier and resolved at runtime, assertions to run over the
  packaged CloudFormation template including executing it, API Gateway access logs and
  stage throttling, local development with `serverless-offline`, a `local` stage,
  `.env.dist` and a profile-gated database browser, the Step Functions task rules —
  `Retry` and `Catch` in the state machine, never in task code, `TimeoutSeconds` below
  the function timeout, error names as string literals, one directory per workflow and
  per step registered by a single `defineWorkflow()` call — the contract a deploy
  pipeline must fulfil, and X-Ray tracing on by default.

The plugin's most consequential technical claim is the bundler-and-ORM coupling:
esbuild does not implement `emitDecoratorMetadata` and cannot — the emit requires
TypeScript's type system, which esbuild deliberately does not have — and the failure is
silent, so a service on esbuild with a decorator-based ORM builds cleanly and fails at
runtime with a missing or wrongly-guessed column type. The two are therefore one
decision, whichever ORM the team eventually settles on.

**This plugin ships no bootstrap, no `init` and no example project.** It is a body of
practices, and the intended effect is indirect: with the practices in context, a model
building a serverless service already works the way TSH works, so what it produces is
boilerplate-shaped without anything generating a starter. An earlier draft carried a
four-question bootstrap that emitted a whole example service; it was removed, and the
project structure it pinned survives as a documented convention in
`project-structure.md`.

### Provenance

The conventions here were **derived from** TSH's serverless boilerplate
(`sls-boilerplate-osls`), read as a worked example of how a Serverless
Framework/OSLS service can be built — **no file was ported verbatim**. Its
scaffolding tool (`plop` and its templates), its npm script names (such as
`check-iam-template`), its coverage configuration (`.c8rc.json`), and its file
paths (`test/setup.ts` and the rest) deliberately did not travel: those are
one repository's tooling choices, not portable rules, and every reference in
this plugin was written from the constraint behind each one rather than from
the artifact itself.

What did travel, as the substantive portable content:

- The thin-handler and pure-service split, and the init-phase rule that expensive
  setup happens once at module scope rather than inside the handler.
- Middleware registration order — **corrected against middy's source**: in middy 7
  the CORS and security-header `onError` hooks skip a response that does not exist
  yet, so the error renderer is registered *after* them, not first. Registered
  first, every error response leaves without CORS headers; the source boilerplate's
  tests cover CORS on the 200 path only, which is how the inversion went unnoticed.
- Least-privilege IAM: no wildcard `Resource` or `Action`, with the narrow,
  explicitly named carve-out for actions AWS itself defines no resource type for.
- Per-function reserved concurrency, so one endpoint under load cannot starve
  every other function — or, for a database-backed function, exceed the
  connection-pool budget the account was sized for.
- Secrets resolved at runtime from an identifier, never stored as a literal value
  in a function's environment, where the CloudFormation template would keep it
  readable through `lambda:GetFunctionConfiguration`.
- Assertions over the packaged CloudFormation template — including how close it is
  to CloudFormation's 500-resource limit — *and* over the packaged artifact itself,
  run at package time —
  the last cheap moment to catch a wrong logical id or a wildcard statement
  before it fails minutes into a deploy.
