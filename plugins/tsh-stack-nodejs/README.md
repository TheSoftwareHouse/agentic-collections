# TSH Stack: Node.js

TSH conventions for TypeScript on Node.js — compiler configuration for a Node
runtime, and NestJS API implementation and review.

This is a **stack** plugin, not a discipline plugin. Install it into the projects
that run on Node, at `project` scope, so it travels with the repo — the repo already
knows what it runs on. Your discipline plugin (`tsh-product-engineering` and
friends) travels with **you**, at `user` scope, and so does `tsh-core`.

A stack here is a **runtime target**, not a language. Browser-targeted TypeScript
lives in `tsh-stack-frontend`, because a bundled app and a Node service need
genuinely different compiler configuration — and because most projects have a
frontend whatever their backend is written in. A fullstack TypeScript repo installs
both.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-nodejs@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `configuring-typescript-for-nodejs` | `/tsh-stack-nodejs:configuring-typescript-for-nodejs` | Which TypeScript version to pin, the `tsconfig.json` baseline for a Node runtime, `module`/`moduleResolution` for a deployed Node major, the decorator-metadata and class-field settings NestJS and TypeORM require, upgrades, and staged adoption in an existing repo |
| `implementing-nestjs-api` | `/tsh-stack-nodejs:implementing-nestjs-api` | NestJS 11 REST APIs: vertical feature slices, CQRS handlers and module boundaries, TypeORM 0.3 persistence, DTO/validation/error contracts, testing layers, configuration and security, WebSocket gateways, and a review checklist |

Both skills are model-invocable — Claude loads them when the work matches their
description, so you don't have to remember to type the command.

The two are designed to work together: `implementing-nestjs-api` assumes the
compiler baseline the configuration skill establishes, and links to it directly.
Because they ship in the same plugin, that link always resolves.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates arrive
with `/plugin update`.

## Not covered yet

Deliberate gaps, so they read as scope rather than oversight:

- **Build toolchain choice** — `tsc` vs SWC vs esbuild vs `tsx`. The type-gate rule
  is covered; picking the transpiler is not.
- **Monorepo project references** beyond a short note.
- **Non-Nest frameworks** — Express, Fastify, and Hono have no skill of their own.
- **Type modelling** — unions, branded types, `unknown` over `any`. This left with
  the old `typescript-conventions` skill and will return as its own skill rather than
  being duplicated per target.

## Scope

The routing question for this plugin is *would this guidance change if the project
switched runtime target or framework?* If yes, it belongs here. If it would change
when the **reader** switched job, it belongs in a discipline plugin instead.

Framework skills live inside their runtime's plugin: `implementing-nestjs-api`
belongs here, not in a `tsh-stack-nestjs` of its own. The install unit is the
plugin, and nobody wants "NestJS guidance but explicitly not the TypeScript settings
it depends on."

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change never
reaches them.

Three rules that bite hardest here:

- **Skill names carry no framework version.** `implementing-nestjs-api`, not
  `implementing-nestjs-11-api`. The name is the invocation command, so pinning a
  major forces a rename on every upgrade. Put the version in the `description` and in
  a **Version Baseline** block in `SKILL.md`.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed —
  and the failure is a silent dead link, not an error.
- **`configuring-typescript-for-nodejs` has a near-twin** in `tsh-stack-frontend`.
  Version policy, the strictness ladder, and the upgrade procedure exist in both, on
  purpose, because they cannot be linked across plugins. When you change one, check
  the other in the same PR — and let the target-specific parts stay different.
