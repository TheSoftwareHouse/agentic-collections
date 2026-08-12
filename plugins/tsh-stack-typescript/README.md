# TSH Stack: TypeScript

TSH conventions for TypeScript: language and version guidelines, and NestJS API
implementation and review.

This is a **stack** plugin, not a discipline plugin. Install it into the projects
that are written in TypeScript, at `project` scope, so it travels with the repo.
Your discipline plugin (`tsh-product-engineering` and friends) travels with you,
at `user` scope.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-typescript@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `typescript-conventions` | `/tsh-stack-typescript:typescript-conventions` | Version policy, `tsconfig` baselines, decorators and class fields, type modelling, migration between majors |
| `implementing-nestjs-api` | `/tsh-stack-typescript:implementing-nestjs-api` | NestJS 11 REST APIs: vertical slices, CQRS, TypeORM 0.3 persistence, validation, testing, review checklist |

Both skills are model-invocable — Claude loads them when the work matches their
description, so you don't have to remember to type the command.

Each skill keeps a short `SKILL.md` and pushes detail into `references/`, loaded
only when the task needs it. The **"Load when"** column in each skill's Reference
Loading table is what routes the model to the right file; keep it filled in when
adding references.

## Scope

This plugin owns TypeScript **as a language** plus the frameworks TSH builds on
it. Framework-agnostic engineering practice (how we review, how we do TDD) belongs
in `tsh-product-engineering` instead.

The rule: *would this guidance change if the team switched language or framework?*
If yes, it belongs here. If it holds regardless of stack, it belongs in a
discipline plugin.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Two rules that bite hardest here:

- **Skill names carry no framework version.** `implementing-nestjs-api`, not
  `implementing-nestjs-11-api` — the name is the invocation command, and renaming
  breaks every reference to it. Put the version in the `description` and in a
  Version Baseline block inside `SKILL.md`.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed.

This plugin will be split when it outgrows one install decision — roughly when it
passes ~8 skills, or when more than half of them are irrelevant to a typical
installer. At that point frontend and Node skills move to their own
`tsh-stack-*` plugins and the language-level core stays here.
