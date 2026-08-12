# NestJS Validation with Zod

Use this reference when adopting or extending Zod/`nestjs-zod` DTO validation in a NestJS 11 API.

## Table of Contents

- [Applicability: Greenfield vs Brownfield](#applicability-greenfield-vs-brownfield)
- [Brownfield Bounded-Adoption Rules](#brownfield-bounded-adoption-rules)
- [Slice Boundary Rule (No Mixed Idioms)](#slice-boundary-rule-no-mixed-idioms)
- [Canonical Zod Idioms](#canonical-zod-idioms)
- [Version Baseline (Live Verification Required)](#version-baseline-live-verification-required)
- [OpenAPI / Swagger Integration](#openapi--swagger-integration)
- [WebSocket Gateway Validation with Zod](#websocket-gateway-validation-with-zod)
- [Security Considerations](#security-considerations)
- [Decision Points](#decision-points)
- [Official documentation](#official-documentation)

## Applicability: Greenfield vs Brownfield

| Repository state | Default stack | Exception |
| --- | --- | --- |
| Greenfield NestJS 11 project with no established DTO validation stack | Zod + `nestjs-zod` | Only an ADR-justified class-based requirement, such as a required decorated-class stack layer |
| Brownfield project with an established `class-validator`/`class-transformer` convention | Bounded adoption only; see the rules below | No unbounded default or wholesale migration |

The greenfield default operates within the repository-first convention rule in [`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md): it fixes the default only when no convention exists and never overrides an established convention.

## Brownfield Bounded-Adoption Rules

- Zod MAY be adopted for new vertical slices with no existing DTOs.
- Zod MAY be adopted for new WebSocket gateways.
- Zod MAY be adopted for modules with zero existing DTOs.
- Zod MUST NOT be adopted as a wholesale or global migration of an established `class-validator` codebase in one initiative.
- Rewriting a working, passing `class-validator` DTO solely for stack preference is NEVER permitted.
- A slice's DTOs MAY migrate to Zod only for a named, tracked defect that the existing implementation cannot fix without the rewrite, or for an unrelated, already-approved rewrite of that slice.

## Slice Boundary Rule (No Mixed Idioms)

- The boundary for one idiom per boundary is the vertical feature slice, not a file or a single DTO.
- Every DTO in one slice's `api/` folder, including WebSocket gateway DTOs, MUST use the same validation idiom.
- A slice MUST NOT contain both `class-validator` DTOs and Zod DTOs; a different slice MAY use a different idiom.

This is a stricter superset of, not a contradiction of, the per-contract mixing prohibition in [`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md) and [`nestjs-review-checklist.md`](./nestjs-review-checklist.md); one idiom per slice automatically satisfies one idiom per contract.

## Canonical Zod Idioms

- Controller and gateway DTOs MUST use `createZodDto(schema)` from `nestjs-zod`, once per schema and one class per schema. The API spelling used by the Phase 1 compatibility fixture is `nestjs-zod` `5.5.0` (resolved snapshot `2026-08-11T10:24:08Z`); the exact current factory signature is [unverified]; reverify it against the package repository before use.
- Parse at the transport boundary with `.parse()` or `ZodValidationPipe`; pass the resulting plain parsed object into command/query constructors. NEVER pass a raw schema, raw schema type, or DTO/class instance into those constructors. The exact integration behavior beyond the tested fixture is [unverified]; reverify it against the package repository before use.
- Coercion MUST be per-field: `z.coerce.number()` and `z.coerce.date()` require an explicit contract decision. Global implicit conversion MUST NOT be enabled. The exact coercion API is [unverified]; reverify it against the official Zod documentation.
- `z.coerce.boolean()` MUST NOT coerce arbitrary input strings: `Boolean("false") === true`, so the literal string `"false"` becomes `true`. Use a literal mapping such as `z.enum(['true', 'false']).transform((v) => v === 'true')`. This boolean-coercion behavior is [unverified]; cite and reverify against the official Zod documentation and repository, plus the `nestjs-zod` repository.
- Every schema MUST use `.strict()` by default for unknown-key rejection. `.passthrough()` or `.strip()` requires an explicit, recorded contract decision; the exact Zod v4 object policy API is [unverified]; reverify it against the official Zod documentation.
- Schemas MUST be colocated in the owning slice's `api/` folder and composed from a base schema with `.pick()`, `.extend()`, or `.omit()` instead of duplicating fields. The exact Zod v4 composition API is [unverified]; reverify it against the official Zod documentation.

## Version Baseline (Live Verification Required)

| Phase 1 item | Resolved value and provenance |
| --- | --- |
| `nestjs-zod` package and peers | `nestjs-zod` `5.5.0`; `@nestjs/common` peer `^10.0.0 \|\| ^11.0.0`; Zod peer `^3.25.0 \|\| ^4.0.0`; observed `@nestjs/swagger` peer `^7.4.2 \|\| ^8.0.0 \|\| ^11.0.0`. Registry metadata source: [nestjs-zod latest registry](https://registry.npmjs.org/nestjs-zod/latest), retrieved `2026-08-11T10:19:45Z`; resolved fixture snapshot `2026-08-11T10:24:08Z`. |
| Zod latest | Zod `4.4.3`, major `4`. Source: [Zod latest registry](https://registry.npmjs.org/zod/latest), retrieved `2026-08-11T10:19:45Z`. |
| Swagger fixture | `@nestjs/swagger` `11.4.6`; components `WidgetInput` and `WidgetOutput_Output`; refs `#/components/schemas/WidgetInput` and `#/components/schemas/WidgetOutput_Output`; no collision or manual disambiguation was required in this tested setup. Fixture source/provenance: local `2026-08-11` fixture run; the raw evidence file is not shipped with this skill. |
| WebSocket fixture | `ZodValidationException`; Socket.IO's filter changed the visible error frame but was not required to preserve the connection in the tested setup. `WsAdapter` emitted no explicit error frame with or without the filter. Fixture source/provenance: local `2026-08-11` fixture run; the raw evidence file is not shipped with this skill. |
| SWC fixture | With metadata disabled and no Swagger decorators, explicit `new ZodValidationPipe(Dto)` rejected the invalid payload, while implicit global metatype-driven validation accepted it. Metadata is therefore not universally removed: the tested explicit pipe path worked, but implicit/global behavior still required metadata. Fixture source/provenance: local `2026-08-11` fixture run; the raw evidence file is not shipped with this skill. |

Agents MUST reverify registry information live when scaffolding or changing a project. These results are [unverified — not a permanent pin] for future dependency resolution, even though the listed Phase 1 fixture observations are resolved evidence.

## OpenAPI / Swagger Integration

- The Phase 1 Swagger fixture used `nestjs-zod` `5.5.0`, Zod `4.4.3`, and `@nestjs/swagger` `11.4.6`.
- It produced component keys `WidgetInput` and `WidgetOutput_Output`, with refs `#/components/schemas/WidgetInput` and `#/components/schemas/WidgetOutput_Output`.
- Input/output IDs did not collide, and manual disambiguation was not required in that tested setup. Do not generalize this fixture result to every schema or toolchain without verification [unverified].
- Keep OpenAPI generation aligned with the DTO/schema contract and reverify the selected package set against the current registry before release.

## WebSocket Gateway Validation with Zod

- Gateway DTOs use the same `createZodDto` plus boundary parsing idiom as HTTP DTOs, consistent with [`nestjs-websockets-gateways.md`](./nestjs-websockets-gateways.md)'s rule that gateway payloads are validated like HTTP DTOs.
- The Phase 1 fixture observed `ZodValidationException` for invalid payloads.
- In the tested Socket.IO path, a filter altered the visible error frame but was not required to preserve the connection; the next valid payload succeeded.
- In the tested `WsAdapter` path, the connection remained open and the next valid payload succeeded, but no explicit error frame was observed with or without the filter. Do not make a stronger general claim [unverified]; verify each adapter-specific fixture.

## Security Considerations

- `.strict()` is the default mass-assignment posture. `.passthrough()` and `.strip()` require an explicit, recorded decision.
- `ZodError` MUST map through [`nestjs-validation-errors-and-serialization.md`](./nestjs-validation-errors-and-serialization.md); NEVER serialize raw issue trees or schema internals.
- The Zod schema object and its internal `_def` MUST NEVER be serialized into a response or error.
- Every schema's strictness and coercion choice MUST be explicit and reviewable, not accidental.
- `z.coerce.boolean()` MUST NOT be used for arbitrary strings: `Boolean("false") === true`; use a literal-mapping transform instead. This security interpretation is [unverified]; reverify against the official Zod coercion documentation.

## Decision Points

| Decision | Required choice |
| --- | --- |
| Adopt `nestjs-zod` | Apply the greenfield/brownfield and named-exception rules above; do not perform a wholesale brownfield migration. |
| Slice boundary | Select exactly one idiom for every DTO in a slice's `api/` folder, including gateway DTOs. |
| Unknown keys | Use `.strict()` unless an explicit, recorded contract decision selects `.passthrough()` or `.strip()`. |
| Dependency baseline | Reverify live registry metadata; do not treat the Phase 1 versions as permanently pinned [unverified]. |

## Official documentation

| Source | Retrieval date |
| --- | --- |
| [nestjs-zod GitHub](https://github.com/BenLorantfy/nestjs-zod) | 2026-08-11 |
| [nestjs-zod npm package](https://www.npmjs.com/package/nestjs-zod) | 2026-08-11 |
| [nestjs-zod latest registry](https://registry.npmjs.org/nestjs-zod/latest) | 2026-08-11T10:19:45Z |
| [Zod GitHub releases](https://github.com/colinhacks/zod/releases) | 2026-08-11 |
| [Zod latest registry](https://registry.npmjs.org/zod/latest) | 2026-08-11T10:19:45Z |
| [Nest validation](https://docs.nestjs.com/techniques/validation) | 2026-08-11 |
| [Nest OpenAPI introduction](https://docs.nestjs.com/openapi/introduction) | 2026-08-11 |
| [Nest WebSocket gateways](https://docs.nestjs.com/websockets/gateways) | 2026-08-11 |
| [Nest WebSocket exception filters](https://docs.nestjs.com/websockets/exception-filters) | 2026-08-11 |
| [Nest SWC recipe](https://docs.nestjs.com/recipes/swc) | 2026-08-11 |
