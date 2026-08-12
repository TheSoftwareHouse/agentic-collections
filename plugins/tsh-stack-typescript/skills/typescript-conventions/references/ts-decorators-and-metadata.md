# Decorators, Metadata, and Class Fields

Use this reference whenever decorators, dependency injection, or runtime type
reflection are involved — NestJS, Angular, TypeORM, `class-validator`,
`class-transformer`, `type-graphql`. The interactions here are the most common
way a *type-level* configuration change breaks a *running* application.

## Contents

- [Two Different Decorator Features](#two-different-decorator-features)
- [`emitDecoratorMetadata`](#emitdecoratormetadata)
- [`useDefineForClassFields`](#usedefineforclassfields)
- [`verbatimModuleSyntax` and Elided Imports](#verbatimmodulesyntax-and-elided-imports)
- [`erasableSyntaxOnly` and Parameter Properties](#erasablesyntaxonly-and-parameter-properties)
- [Framework Baselines](#framework-baselines)
- [Diagnosing](#diagnosing)

## Two Different Decorator Features

TypeScript has shipped decorators twice, and they are not compatible.

| | Legacy decorators | Standard decorators |
| --- | --- | --- |
| Enabled by | `experimentalDecorators: true` | on by default from TS 5.0 |
| Based on | a pre-standard proposal | the Stage 3 ECMAScript proposal |
| Parameter decorators | supported | **not supported** |
| `emitDecoratorMetadata` | supported | **not supported** |
| Used by | NestJS, Angular, TypeORM, `class-validator` | newer libraries, and framework majors that have migrated |

| Severity | Rule |
| --- | --- |
| MUST | Determine which of the two the project's frameworks require **before** changing any decorator-related flag. |
| NEVER | Assume "standard is newer, so use standard." For a NestJS or TypeORM codebase, legacy decorators are the correct and required choice, not technical debt. |
| NEVER | Mix the two in one compilation unit. `experimentalDecorators` is per-project; there is no per-file opt-out. |

The decisive constraint is usually parameter decorators. NestJS's
`@Inject()`, `@Body()`, `@Param()`, and `@Query()` are all parameter decorators,
so a NestJS project cannot use standard decorators until Nest itself migrates.

## `emitDecoratorMetadata`

With `experimentalDecorators` and `emitDecoratorMetadata` both on, the compiler
emits `design:type`, `design:paramtypes`, and `design:returntype` metadata for
decorated declarations, via `Reflect.metadata`. This requires the `reflect-metadata`
polyfill to be imported once, before anything decorated is loaded.

This metadata is what makes constructor injection work without naming the token:

```ts
@Injectable()
export class OrderService {
  constructor(private readonly repo: OrderRepository) {}
  //                                ^ recovered at runtime from design:paramtypes
}
```

The emit has hard limits worth knowing before relying on it:

- **Only types with a runtime value are preserved.** An interface or type alias
  emits as `Object`, which is why DI on an interface requires an explicit token.
- **Union and generic type arguments are erased.** `string | number` becomes
  `Object`; `Repository<Order>` becomes `Repository`.
- **Circular imports break it.** A type used only in metadata position can
  resolve to `undefined` when the module graph has a cycle.

| Severity | Rule |
| --- | --- |
| MUST | Import `reflect-metadata` exactly once, at the true entry point, before any decorated module is imported. |
| MUST | Use an explicit injection token for any interface or abstract dependency. Metadata cannot carry it. |
| AVOID | Depending on metadata for anything beyond DI and ORM mapping. It is a narrow, lossy channel. |

## `useDefineForClassFields`

This flag defaults to **`true`** when `target` is `ES2022` or higher, and it
changes what a class field declaration *does*.

```ts
class Example {
  declared!: string;        // no initializer
}
```

- **`false` (legacy):** the declaration emits nothing. The field exists only once
  something assigns it.
- **`true` (standard):** the declaration emits `Object.defineProperty(this, "declared", { value: undefined })`
  in the constructor — **overwriting** whatever a decorator, base constructor, or
  DI container had already set.

That difference is the cause of a whole family of bugs that appear after a
`target` bump and no other change:

- Injected properties becoming `undefined`.
- TypeORM entity columns losing values assigned by the driver.
- `class-transformer` output missing fields.
- Angular `@Input()` bindings resetting.

| Severity | Rule |
| --- | --- |
| MUST | Set `useDefineForClassFields` **explicitly** in any project using decorators. Do not let it be implied by `target`. |
| MUST | Set it to `false` for NestJS, Angular, and TypeORM codebases unless the framework documents otherwise. |
| MUST | Run the application, not just `tsc --noEmit`, after changing it or after changing `target`. The type-check cannot see this class of failure. |
| PREFER | `true` for framework-free code, where it is the standards-correct behavior. |

`declare` on a field (`declare foo: string`) opts a single field out of the emit,
which is the escape hatch when most of the project wants `true`.

## `verbatimModuleSyntax` and Elided Imports

`verbatimModuleSyntax` (TS 5.0+) emits import statements exactly as written and
drops anything marked `import type`. It is a good default — it makes emit
predictable and removes the old `importsNotUsedAsValues` guesswork.

The conflict: `emitDecoratorMetadata` needs some *type* positions to survive to
runtime, because it reads the imported class as a value when building
`design:paramtypes`.

```ts
import type { OrderRepository } from './order.repository';  // elided at emit

@Injectable()
export class OrderService {
  constructor(private readonly repo: OrderRepository) {}
  // design:paramtypes now references an identifier that isn't imported
}
```

| Severity | Rule |
| --- | --- |
| NEVER | Use `import type` for a class that appears in a decorated constructor parameter, a decorated property, or any position feeding `emitDecoratorMetadata`. Use a value import. |
| MUST | Verify at runtime before enabling `verbatimModuleSyntax` in a decorator-heavy project. The failure is a runtime `undefined`, not a compile error. |
| PREFER | Enabling it in projects without `emitDecoratorMetadata`, where it is unambiguously correct. |

The same caution applies to an auto-import or lint rule that "helpfully" converts
value imports to type imports — `@typescript-eslint/consistent-type-imports` will
introduce this bug at scale if configured without an exception for decorated code.

## `erasableSyntaxOnly` and Parameter Properties

TypeScript 5.8's `erasableSyntaxOnly` restricts the language to syntax a runtime
can strip without transforming — the requirement for executing TypeScript
directly under Node's native type stripping.

It bans:

- `enum` (use a `const` object plus a union type)
- `namespace` with runtime members
- constructor **parameter properties** (`constructor(private readonly x: T) {}`)

The third one is a direct conflict: parameter properties are the idiomatic NestJS
and Angular DI style, and the codebase is built on them.

| Severity | Rule |
| --- | --- |
| NEVER | Enable `erasableSyntaxOnly` in a NestJS or Angular project without first converting every parameter property to an explicit field assignment. |
| MUST | Treat "run TypeScript directly on Node" and "use decorator-based DI" as mutually exclusive today. Decorators still require a compile step. |
| PREFER | A `const` object with a derived union over `enum` in new code regardless — it erases cleanly and produces a narrower type. |

## Framework Baselines

Verify against the framework's own docs and `peerDependencies` before relying on
this table; it records the shape of the constraint, not a live pin.

| Framework | Decorators | `emitDecoratorMetadata` | `useDefineForClassFields` | Notes |
| --- | --- | --- | --- | --- |
| NestJS 11 | legacy (`experimentalDecorators`) | required | `false` | Parameter decorators throughout; `reflect-metadata` at entry point |
| TypeORM 0.3 | legacy | required for implicit column types | `false` | Explicit column types reduce metadata reliance |
| `class-validator` / `class-transformer` | legacy | required | `false` | Property decorators read `design:type` |
| Angular | legacy | not required (compiler handles it) | `false` | The Angular compiler supplies its own metadata |

## Diagnosing

When something decorated is `undefined` at runtime:

1. **Check `useDefineForClassFields`** and the `target` that implies it. This is
   the most common cause and the easiest to miss, because nothing in the source
   changed.
2. **Check for `import type`** on the class that came back `undefined`.
3. **Check `reflect-metadata`** is imported once, first, at the real entry point
   — including in the test setup, which often has a different entry.
4. **Check for a circular import** between the two modules. Metadata resolves to
   `undefined` in a cycle even when the runtime import eventually succeeds.
5. **Inspect the emit**, which settles it definitively:

   ```shell
   npx tsc --noEmit false --outDir /tmp/emit-check src/the-file.ts
   ```

   Read the generated constructor. If you see `Object.defineProperty` for a field
   you expected to be left alone, it is cause 1.
