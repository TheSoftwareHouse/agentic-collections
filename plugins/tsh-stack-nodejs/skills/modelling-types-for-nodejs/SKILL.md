---
name: modelling-types-for-nodejs
description: "How to express a type in a Node.js/TypeScript backend so the compiler catches the bug instead of the runtime: discriminated unions that make illegal states unrepresentable, branded ids, const-object unions over enums, satisfies, unknown over any, and validating every boundary into a schema-derived type. Use when deciding how to model a DTO, entity, command or event payload, choosing union versus enum or interface versus type, or reviewing backend code for any, unsafe casts, or types that lie."
when_to_use: "Trigger on: deciding how to shape a type (union vs enum, interface vs type, optional fields vs a discriminated union), a review comment about `any`, `as`, non-null `!`, or an unchecked cast, branding ids that must not be swapped, typing an HTTP body/env/message boundary, choosing `satisfies` vs an annotation, or a generic that only appears in a return position. For *compiler configuration* — tsconfig, versions, decorators — use configuring-typescript-for-nodejs instead."
---

# Modelling Types for Node.js

How to model types in a Node/TypeScript backend so wrong states fail to compile
rather than reaching production. The organising principle: **a type is a claim, and
the compiler can only protect you from claims that are true.** Every `any`, every
unchecked assertion, and every over-wide signature trades a compile-time guarantee
for a runtime hope.

This is the type-*modelling* layer. The `tsconfig.json`, version policy, and
decorator settings it assumes belong to
[`configuring-typescript-for-nodejs`](../configuring-typescript-for-nodejs/SKILL.md),
and the NestJS/TypeORM feature patterns to
[`implementing-nestjs-api`](../implementing-nestjs-api/SKILL.md). All three ship in
this plugin, so those links always resolve.

## When to Use

- Deciding how to express a type: union vs enum, `interface` vs `type`, optional
  fields vs a discriminated union, a branded id vs a bare `string`.
- Modelling a DTO, entity, command or event payload so illegal combinations cannot
  be constructed.
- Typing a boundary — an HTTP body, query string, env var, or message payload —
  where data arrives untyped.
- Reviewing backend code for `any`, unsafe assertions, non-null `!`, or types that
  claim more than the code proves.

## Applicability and Precedence

Read the repository's own code and `tsconfig.json` before applying anything here.
**Local conventions outrank these defaults** — a codebase that uses `enum`
consistently stays consistent; apply this guidance where the repo is silent, and
record a deliberate deviation rather than silently mixing both.

Framework requirements also outrank this skill. NestJS, TypeORM, and the validation
library in use constrain how DTOs and entities are shaped; where a framework skill
and this one disagree, the framework skill wins for the files it owns.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| NEVER | Use `any` to silence an error. Use `unknown` at the boundary and narrow with a type guard or a schema parse; a surviving `any` carries a comment naming the reason and the condition for removal. |
| NEVER | Use a type assertion to overrule the compiler — `as unknown as T`, or a non-null `!` on a value the code cannot prove is present — without a comment justifying the claim. `as const` is the exception; it narrows rather than widens. |
| MUST | Validate every value entering the process (HTTP body, query string, env, messages, third-party responses) and derive its static type from the schema (`z.infer`), never cast a response body to a hand-written interface. |
| PREFER | A discriminated union with a literal discriminant over an interface with mutually exclusive optional fields, and add an exhaustiveness check so a new variant fails to compile until every consumer handles it. |
| PREFER | Branded types for ids and validated values that cross module boundaries, constructed through one validating function so the brand means "checked". |
| PREFER | A `const` object plus a derived union over `enum`; NEVER a numeric `enum` for a persisted or serialized value, whose stored integers become an unversioned contract. |
| PREFER | `satisfies` over an annotation when you want validation *and* the narrow inferred type (config objects, lookup tables). |
| NEVER | Add a type parameter that appears only in the return position — it is an unchecked assertion wearing generic syntax; have the caller narrow an `unknown` instead. |
| MUST | Comment every suppression and prefer `@ts-expect-error` over `@ts-ignore`; never a file-level `@ts-nocheck` in application code. A growing suppression count means a type is modelled wrongly. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Type modelling patterns](./references/type-modelling-patterns.md) | Applying any rule above to real code, or you need the worked example and the full rationale | Each pattern with backend code: `unknown` over `any`, assertions, making illegal states unrepresentable, branded types, unions over enums, `interface` vs `type`, generic discipline, `satisfies`, boundaries, suppression |

## Procedure

1. **Read the ground truth.** Look at the surrounding code and the repo's existing
   conventions — which of `enum`/union, `interface`/`type`, and validation library
   it already uses — before proposing a shape.
2. **Model the state, not the validation.** Prefer a type that makes the illegal
   combination impossible to construct over one that permits it and checks later.
3. **Check the boundaries.** Anything crossing into the process is `unknown` until a
   schema parses it; anything crossing a module boundary as a bare primitive id is a
   swap waiting to happen.
4. **Load the reference** for the worked example and the exact rule when applying any
   of the above to real code.
