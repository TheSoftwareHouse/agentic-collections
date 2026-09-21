# Bundler and ORM: One Paired Choice

Use this reference when choosing or switching the bundler behind packaging, when
deciding which ORM or query layer a service uses, or when a TypeORM-shaped
entity builds cleanly and then fails at runtime with a missing or wrongly
guessed column type.

## Table of Contents

- [Why the Bundler and the ORM Are One Decision](#why-the-bundler-and-the-orm-are-one-decision)
- [Wiring the bundler into packaging](#wiring-the-bundler-into-packaging)
- [The Three Pairings](#the-three-pairings)
- [If a Column's Type Ever Feels Like a Guess](#if-a-columns-type-ever-feels-like-a-guess)

This is the **canonical explanation** of the pairing. `configuring-serverless-service`
links here with `${CLAUDE_PLUGIN_ROOT}` rather than restating it — if you find
yourself copying this table elsewhere in the plugin, link instead.

## Why the Bundler and the ORM Are One Decision

The bundler and the persistence layer look independent — one packages code, the
other maps tables — but choosing them separately produces a combination that
fails silently, so they have to be decided together.

**`emitDecoratorMetadata` needs TypeScript's type system.** Decorator-based ORMs
(TypeORM is the common example) can infer a column's database type from the
TypeScript type of the decorated property, but only when something emits
`design:type` metadata for that property — and that emission is done by
TypeScript's own compiler, using its full type checker, as part of
`emitDecoratorMetadata`.

**esbuild does not implement `emitDecoratorMetadata`, and cannot**: esbuild is
a transpiler, not a type checker. It converts syntax to syntax; it never builds
the type graph that `design:type` metadata is derived from. There is no flag
that turns this on — the feature requires information esbuild deliberately does
not compute.

**The failure mode is what makes this dangerous.** A TypeORM entity with a bare
decorator and no explicit column type compiles under esbuild with **no build
error at all**. Decorators are valid syntax; esbuild transpiles them and moves
on. The metadata is simply never emitted — dropped silently, not rejected. The
entity builds, the service packages, the deploy succeeds. The bug appears only
at runtime, the first time that entity is mapped: TypeORM falls back to metadata
that was never produced, and the column gets **a missing or wrongly-guessed
type**. Nothing in the build output says so, because nothing in the build failed.

Bundler and ORM are therefore offered as one paired choice at bootstrap, never
as two independent questions — asking them separately lets someone assemble
esbuild with a decorator-based ORM without ever being told what that
combination does.

## Wiring the bundler into packaging

Neither bundler is invoked directly: the framework plugin that owns packaging
calls it. `serverless-esbuild` for esbuild, `serverless-webpack` for webpack —
declared in `plugins` and configured under `custom`. Name the one that matches
the chosen pairing when generating or reviewing a service; a bundler chosen in
`package.json` with no plugin wiring it in packages nothing.

This plugin carries esbuild's configuration in
[`compiler-options-for-serverless.md`](./compiler-options-for-serverless.md)
and the module-format consequences in
[`runtime-and-module-format.md`](./runtime-and-module-format.md). It does
**not** carry a webpack configuration: for the webpack pairing it gives the
compiler settings and the shared-output-directory trap, and the webpack config
itself is the team's to write.

## The Three Pairings

Neither pairing is presented as correct. The coupling — that the two decisions
constrain each other — is what must not be missable; which pairing fits a given
service is a judgment call the table below informs, not a house default.

| Pairing | When it is right | Cost |
| --- | --- | --- |
| **esbuild + Drizzle ORM** | The natural fit for a greenfield service with no existing ORM investment. Drizzle is TypeScript-native: schema is declared as plain objects with no decorators and no `reflect-metadata`, so there is no metadata emission for esbuild to fail to produce. It also carries no query-engine binary into the bundle. Kysely is the equivalent choice when the service wants a query builder rather than a full ORM. | A different mental model from decorator-based ORMs — schema-as-objects instead of schema-as-classes. The team spends time learning it. |
| **webpack + `ts-loader` + TypeORM** | A team already invested in TypeORM, or porting an existing TypeORM-based service. `ts-loader` runs the real TypeScript compiler as part of packaging, so `emitDecoratorMetadata` is emitted correctly and column types are inferred the way TypeORM expects. | Packaging is roughly an order of magnitude slower than esbuild. That cost is paid on every package, not once. |
| **esbuild + TypeORM through a `tsc` or SWC pass** | Only when TypeORM is non-negotiable *and* packaging speed still matters enough to justify the extra moving part. Needs a plugin or a preceding compiler pass — for example `esbuild-plugin-tsc`, an SWC-based decorator transform, or an equivalent tool that runs a real type checker ahead of esbuild — to produce the metadata esbuild itself cannot. | Reintroduces a per-file compiler pass ahead of the bundler, eroding much of the speed advantage that motivated choosing esbuild in the first place. Present this pairing as the compromise it is, not as a free win — it exists for the case where the other two genuinely do not fit. |

**Prisma is deliberately not offered as the esbuild pairing.** Prisma's query
engine ships as a separate native binary that has to reach the Lambda alongside
the JavaScript bundle — a packaging problem distinct from the decorator-metadata
one, and one that Drizzle and Kysely, being pure TypeScript with no engine
binary, do not have.

## If a Column's Type Ever Feels Like a Guess

Any bare decorator on a TypeORM column, in any pairing, is a place where the
mapping depends on inferred metadata rather than a stated fact:

```ts
@Column()
email!: string;
```

Give every column an explicit `type` regardless of which pairing is in use:

```ts
@Column({ type: "varchar", length: 320 })
email!: string;
```

An explicit type is not enforced by the compiler in any pairing — it is a
convention. Treat it as load-bearing rather than cosmetic: it is what keeps a
column's mapping deterministic independent of whether metadata emission
happened to work for that build.

| Severity | Rule |
| --- | --- |
| MUST | Decide the bundler and the ORM together, as one question, before either is adopted independently. |
| MUST | Give every TypeORM column an explicit `type`, in every pairing — it is the one convention that survives a future bundler change. |
| NEVER | Pair esbuild with a decorator-based ORM without one of the two mitigations above (switch the ORM, or add a compiler pass ahead of esbuild). Treat a bare decorator column under esbuild as a defect, not a style nit — it compiles clean and fails in production. |

## Sources

Verified 2026-09-18:

- [esbuild — TypeScript caveats](https://esbuild.github.io/content-types/#typescript-caveats) — `emitDecoratorMetadata` is unsupported because it needs type information esbuild does not compute
- [esbuild issue #257 — Support emitting TypeScript decorator metadata](https://github.com/evanw/esbuild/issues/257)
- [Drizzle ORM — Serverless](https://orm.drizzle.team/docs/perf-serverless)

The limitation is architectural, not a missing flag. If esbuild ever ships a type
checker, revisit the pairing table — not the rule that the two decisions are made
together.
