---
title: Modelling Types for Node.js
sidebar_label: modelling-types-for-nodejs
sidebar_position: 2
description: How to express a type in a Node.js and TypeScript backend so the compiler catches the bug, using discriminated unions, branded ids, const-object unions, satisfies, unknown over any, and schema-derived boundary types.
sources:
  - plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs/
sources_hash: "33374f97960351fcf75af2dbe290e5ccb5bc7cb74525eccf4ce9111ba47d1842"
---

# Modelling Types for Node.js

**Plugin:** [`tsh-stack-nodejs`](/docs/plugins/tsh-stack-nodejs/)  
**Invoke:** `/tsh-stack-nodejs:modelling-types-for-nodejs`, and Claude also loads it when the work matches its description  
**Used by:** no agent or other skill loads it. The plugin README names it as the layer between the compiler baseline and the framework skill.

How to model types in a Node and TypeScript backend so wrong states fail to compile rather than reaching production. The organising principle is that a type is a claim, and the compiler can only protect you from claims that are true. Every `any`, every unchecked assertion and every over-wide signature trades a compile-time guarantee for a runtime hope.

This is the type-modelling layer. The `tsconfig.json`, version policy and decorator settings it assumes belong to [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs), and the NestJS and TypeORM feature patterns belong to [`implementing-nestjs-api`](/docs/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api).

Use it when deciding how to express a type (union versus enum, `interface` versus `type`, optional fields versus a discriminated union, a branded id versus a bare `string`), when modelling a DTO, entity, command or event payload, when typing an untyped boundary such as an HTTP body, query string, env var or message payload, and when reviewing backend code for `any`, unsafe assertions, non-null `!`, or types that claim more than the code proves.

Local conventions outrank the defaults: a codebase that uses `enum` consistently stays consistent, and a deliberate deviation is recorded instead of silently mixing both. Framework requirements outrank the skill as well, and where a framework skill and this one disagree, the framework skill wins for the files it owns.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **`unknown` over `any`** | Use `unknown` at untyped boundaries and narrow with a type guard or a schema parse. A surviving `any` carries a comment naming the reason and the condition for removal |
| **Assertions** | Prefer a guard or schema parse over an assertion. `as unknown as T` and a non-null `!` on an unproven value need a justifying comment. `as const` is the exception because it narrows rather than widens |
| **Illegal states unrepresentable** | A discriminated union with a literal discriminant over an interface with mutually exclusive optional fields, plus an exhaustiveness check so a new variant fails to compile until every consumer handles it |
| **Branded types** | Brand ids and validated values that cross module boundaries, constructed through a single function that validates before it asserts, so the brand means "checked" |
| **Unions over enums** | A `const` object with a derived union instead of `enum`. A numeric `enum` is never used for a persisted or serialized value, and `const enum` is avoided in new code |
| **`interface` versus `type`** | `interface` for plain object contracts and module augmentation, `type` for unions, intersections, mapped and conditional types. Stay consistent within a codebase |
| **Generic discipline** | A type parameter that appears only in the return position to hand back an unproven value (`parse<T>(raw): T`) is an unchecked assertion. A factory such as `createSet<T>()` asserts nothing and is fine |
| **`satisfies`** | Prefer it over an annotation when you want validation and the narrow inferred type, as for config objects and lookup tables |
| **Boundaries** | Validate every value entering the process (HTTP body, query string, env, messages, third-party responses) and derive the static type from the schema with `z.infer`. Parse the whole environment once at startup into a typed config object |
| **Suppression** | `@ts-expect-error` over `@ts-ignore`, a comment on every suppression, and no file-level `@ts-nocheck` in application code |

## How it works

1. **Read the ground truth.** Look at the surrounding code and the repository's conventions: which of `enum` and union, `interface` and `type`, and which validation library it already uses.
2. **Model the state, not the validation.** Prefer a type that makes the illegal combination impossible to construct over one that permits it and checks later.
3. **Check the boundaries.** Anything crossing into the process is `unknown` until a schema parses it, and a bare primitive id crossing a module boundary is a swap waiting to happen.
4. **Load the reference** for the worked example and the exact rule when applying any of the above to real code.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| NEVER | Use `any` to silence an error, or a type assertion to overrule the compiler without a justifying comment |
| MUST | Validate every value entering the process and derive its type from the schema, never casting a response body to a hand-written interface |
| PREFER | A discriminated union with an exhaustiveness check, branded types for ids, a `const` object union over `enum`, and `satisfies` over an annotation |
| NEVER | Use a numeric `enum` for a persisted or serialized value, or a return-only type parameter that fabricates an unproven value |
| MUST | Comment every suppression and prefer `@ts-expect-error` over `@ts-ignore` |

## References

| Reference | Load when |
| :-- | :-- |
| Type modelling patterns | Applying any rule above to real code, or when you need the worked example and the full rationale |

The patterns reference uses backend examples: entities, DTOs, command and event payloads, and HTTP and env boundaries.

## Related skills

- [`configuring-typescript-for-nodejs`](/docs/plugins/tsh-stack-nodejs/skills/configuring-typescript-for-nodejs) sets the compiler baseline this skill assumes. For compiler configuration, tsconfig, versions and decorators, use that skill instead.
- [`implementing-nestjs-api`](/docs/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api) owns the NestJS and TypeORM feature patterns, and its constraints on how DTOs and entities are shaped win over this skill.

## Source

[`plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-nodejs/skills/modelling-types-for-nodejs/SKILL.md)
