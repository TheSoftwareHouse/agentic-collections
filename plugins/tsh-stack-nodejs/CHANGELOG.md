# Changelog

All notable changes to `tsh-stack-nodejs` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.1.1] - 2026-10-02

### Fixed

- **Four NestJS references delegated to skills that do not exist here** —
  `tsh-implementing-backend`, `tsh-e2e-testing` (twice) and
  `tsh-implementing-observability`, names carried over from the Copilot collection.
  Each sentence now states the scope boundary without naming a skill.
- **TypeScript 6.0 facts.** Two references said 6.0 "removed" `moduleResolution:
  node`/`node10`, `target: es5`, `downlevelIteration`, `outFile` and the legacy
  module kinds. 6.0 deprecates them behind `ignoreDeprecations: "6.0"`; the removals
  land in 7.0. Corrected in both, in step with the same fix in `tsh-stack-frontend`
  0.2.2.

## [0.1.0] - 2026-08-12

Initial release. This plugin is one half of the split of `tsh-stack-typescript`,
which has been removed: a stack is now a **runtime target**, not a language, so
Node-side guidance lives here and browser-side guidance lives in
`tsh-stack-frontend`.

### Added

- `implementing-nestjs-api`, moved here unchanged from `tsh-stack-typescript`.
  NestJS 11 REST APIs with `@nestjs/cqrs`, TypeORM 0.3, and Express: vertical
  feature slices, module boundaries, persistence, validation and error contracts,
  testing layers, configuration and security, WebSocket gateways, and a review
  checklist.
- `configuring-typescript-for-nodejs`, replacing the Node-relevant half of the old
  `typescript-conventions` skill. Covers the `tsconfig.json` baseline for a Node
  runtime, `module`/`moduleResolution` for a deployed Node major, explicit ambient
  `types`, output layout, the decorator-metadata and class-field settings NestJS and
  TypeORM require, version policy and upgrades, and staged adoption in an existing
  repo.
- A brownfield posture stated as a non-negotiable rule in both skills: the baseline
  is a recommendation for new projects, and an existing `tsconfig.json` that differs
  from it is not a defect. Config changes are proposed as the smallest staged step,
  never as a wholesale rewrite.

### Changed

- TypeScript version guidance now reflects **TypeScript 6.0 and 7.0**, which shipped
  after the original material was written. The inherited text treated the Go-native
  compiler as forward-looking; 7.0 is the current stable line. The reference records
  6.0's changed defaults (`strict: true`, `module: esnext`, `types: []`, a floating
  `target`, `rootDir`), its removals (`moduleResolution: node`, `outFile`,
  `target: es5`), and the fact that 6.0 is a required stepping stone to 7.0.
- The Node baseline recommends `module`/`moduleResolution: nodenext` rather than
  `node16`, and writes `strict`, `types`, `rootDir`, and `target` out explicitly so a
  6.0 upgrade cannot change behavior silently.
- The decorators reference drops its Angular material, which belongs to a frontend
  target rather than this one.

### Removed

- The old skill's **type modelling** material (`unknown` over `any`, discriminated
  unions, branded types, `satisfies`) is not carried over. It is conventions rather
  than configuration, and identical for both runtime targets, so duplicating it into
  two plugins would have been pure duplication. It is expected to return as its own
  skill.
