# Changelog

All notable changes to `tsh-stack-serverless` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

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
- **`configuring-serverless-service`** — service and stage configuration,
  per-function definitions, least-privilege IAM with a named carve-out for the
  actions AWS defines no resource type for, per-function reserved concurrency,
  opt-in VPC attachment, secrets passed by identifier and resolved at runtime, and
  assertions to run over the packaged CloudFormation template before the first
  deploy, API Gateway access logs and stage throttling, local development
  with `serverless-offline`, a `local` stage, `.env.dist` and a profile-gated
  database browser, and the Step
  Functions task rules — `Retry` and `Catch` in the state machine, never in
  task code, `TimeoutSeconds` below the function timeout, error names as string
  literals, one directory per workflow and per step registered by a single
  `defineWorkflow()` call, and X-Ray tracing on by default. Carries the
  plugin's generative entry point: a four-question bootstrap procedure that
  opens with a single `AskUserQuestion` call and generates the complete starter
  — service definition and handler layer alike — on OSLS, never on the
  end-of-life Serverless Framework v3, with every dependency version resolved
  from the registry rather than written from memory. The starter ships a health
  endpoint, an integration test for every real repository, the TSH toolchain
  baseline and a `verify` gate that audits dependencies and executes the packaged
  artifact, states the contract a deploy pipeline must fulfil, requires every bootstrap option that switches off part of the plugin's guidance to name that gap in its own description — REST versus HTTP API, esbuild versus webpack, PostgreSQL versus anything else, and closes by
  seeding `CLAUDE.md` and the first decision records through `tsh-core`.

The plugin's most consequential design decision lives in this last skill's
bootstrap: the **bundler and the ORM are offered as one paired choice**, never as
two independent questions. esbuild does not implement `emitDecoratorMetadata` and
cannot — the emit requires TypeScript's type system, which esbuild deliberately
does not have — and the failure is silent: decorators compile without error and
the metadata is simply omitted, so an independently assembled esbuild + TypeORM
service builds cleanly and fails at runtime with a missing or wrongly-guessed
column type. Asking the two questions separately would let that combination be
assembled unwarned.

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
- Assertions over the packaged CloudFormation template, run at package time —
  the last cheap moment to catch a wrong logical id or a wildcard statement
  before it fails minutes into a deploy.
