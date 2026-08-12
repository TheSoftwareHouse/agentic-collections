# Type Modelling

Use this reference when deciding how to express a type, or when reviewing code
for types that lie. The organising principle: **a type is a claim, and the
compiler can only protect you from claims that are true.** Every `any`, every
unchecked assertion, and every over-wide signature converts a compile-time
guarantee into a runtime hope.

## Contents

- [`unknown` over `any`](#unknown-over-any)
- [Assertions](#assertions)
- [Making Illegal States Unrepresentable](#making-illegal-states-unrepresentable)
- [Branded Types](#branded-types)
- [Unions over Enums](#unions-over-enums)
- [`interface` vs `type`](#interface-vs-type)
- [Generic Discipline](#generic-discipline)
- [`satisfies`](#satisfies)
- [Boundaries](#boundaries)
- [Suppression](#suppression)

## `unknown` over `any`

`any` disables checking in every direction — it is assignable to anything and
accepts any operation. `unknown` is the honest version of the same idea: you
don't know the type, so you must narrow before use.

```ts
// Wrong — the error is silenced, not handled.
function handle(payload: any) {
  return payload.data.items.length;
}

// Right — the compiler forces the check the runtime needs anyway.
function handle(payload: unknown) {
  if (!isOrderPayload(payload)) throw new InvalidPayloadError();
  return payload.data.items.length;
}
```

| Severity | Rule |
| --- | --- |
| NEVER | Use `any` to make an error go away. |
| MUST | Use `unknown` at untyped boundaries, and narrow with a type guard or a schema parse. |
| MUST | Comment any surviving `any` with the reason and the condition for removing it. |
| PREFER | `unknown[]` over `any[]`, and `Record<string, unknown>` over `object` or `{}`. |

Enable `useUnknownInCatchVariables` (included in `strict`) so `catch (e)` gives
`unknown` rather than `any`.

## Assertions

A type assertion tells the compiler you know something it doesn't. That is
legitimate when true and a defect when it isn't.

| Severity | Rule |
| --- | --- |
| PREFER | A type guard or schema parse over an assertion. A guard is checked; an assertion is asserted. |
| NEVER | Use `as unknown as T` without a comment. The double assertion exists precisely to defeat the compiler's objection that the types don't overlap — that objection is usually correct. |
| NEVER | Use the non-null assertion `!` on a value the code cannot prove is present. It is a claim about runtime, not a formatting choice. |
| PREFER | `as const` freely — it narrows rather than widens, and is the one assertion that adds information instead of discarding it. |

Test fixtures are the common exception: a partial mock asserted to a full
interface is a reasonable trade, when it's confined to test code.

## Making Illegal States Unrepresentable

Prefer a shape where wrong combinations cannot be constructed, over a shape that
permits them and validates later.

```ts
// Permits { status: 'success', error: 'boom' } — a state that must never exist.
interface Result {
  status: 'success' | 'failure';
  data?: Order;
  error?: string;
}

// The union makes it impossible, and narrows automatically.
type Result =
  | { status: 'success'; data: Order }
  | { status: 'failure'; error: string };
```

| Severity | Rule |
| --- | --- |
| PREFER | A discriminated union over an interface with mutually exclusive optional fields. |
| MUST | Give the union a literal discriminant property, so narrowing works with a plain `switch` or `if`. |
| PREFER | Exhaustiveness checking on the discriminant, so adding a variant becomes a compile error rather than a silent fallthrough. |

```ts
function render(r: Result): string {
  switch (r.status) {
    case 'success': return r.data.id;
    case 'failure': return r.error;
    default: {
      const exhaustive: never = r;   // compile error when a variant is added
      throw new Error(`unhandled: ${String(exhaustive)}`);
    }
  }
}
```

## Branded Types

TypeScript is structural: every `string` is interchangeable with every other
`string`. When two values share a primitive but must never be swapped — a user id
and an order id, a raw password and a hash — brand them.

```ts
declare const brand: unique symbol;
type Brand<T, B> = T & { readonly [brand]: B };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

const asUserId = (raw: string): UserId => raw as UserId;   // one checked entry point

function loadUser(id: UserId): Promise<User> { /* … */ }

loadUser(someOrderId);   // compile error — structurally identical, nominally distinct
```

| Severity | Rule |
| --- | --- |
| PREFER | Branding identifiers that flow across module boundaries, and any value with a validity invariant (validated email, non-empty string, positive integer). |
| MUST | Funnel construction through a single validating function, so the brand means "checked" rather than "asserted somewhere." |
| AVOID | Branding everything. The cost is conversion noise; spend it where a mix-up is plausible and expensive. |

## Unions over Enums

A `const` object plus a derived union gives the same ergonomics as `enum` with
better behavior: it erases cleanly, it is a plain value at runtime, and the type
is a true literal union.

```ts
export const OrderStatus = {
  Pending: 'pending',
  Shipped: 'shipped',
  Cancelled: 'cancelled',
} as const;

export type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];
```

| Severity | Rule |
| --- | --- |
| PREFER | The `const` object pattern above over `enum` in new code. |
| NEVER | Use a numeric `enum` for a value that is persisted or serialized. Numeric enums accept any number, and the stored integers become an unversioned contract. |
| AVOID | `const enum`. It requires inlining, which breaks under `isolatedModules` and every transpile-only build. |

`enum` is not forbidden — an existing codebase that uses it consistently should
stay consistent. But it is banned outright by `erasableSyntaxOnly`, so new code
that might run under a type-stripping runtime should avoid it.

## `interface` vs `type`

Both work for object shapes. The distinction that matters:

| Use | For |
| --- | --- |
| `interface` | Object shapes meant to be implemented or extended, and public API surface. Supports declaration merging, which is required for augmenting third-party modules. |
| `type` | Unions, intersections, mapped and conditional types, tuples, function types, and anything with a computed shape. |

| Severity | Rule |
| --- | --- |
| PREFER | `interface` for a plain object contract, `type` when the definition needs anything `interface` cannot express. |
| MUST | Be consistent within a codebase. The choice matters far less than the churn of mixing both arbitrarily. |
| MUST | Use `interface` when augmenting a third-party module — declaration merging only works on interfaces. |

## Generic Discipline

A type parameter earns its place by relating two positions. If it appears exactly
once in a signature, it is not doing anything a plain type wouldn't.

```ts
// The parameter appears once — it means "any", with extra syntax.
function parse<T>(raw: string): T { return JSON.parse(raw); }

// Honest: the caller must narrow.
function parse(raw: string): unknown { return JSON.parse(raw); }
```

| Severity | Rule |
| --- | --- |
| NEVER | Add a type parameter that appears only in the return position. It is an unchecked assertion wearing generic syntax. |
| PREFER | Constraining parameters (`<T extends { id: string }>`) so the body can rely on structure. |
| PREFER | Overloads over a conditional return type when there are two or three concrete call shapes — the error messages are dramatically better. |
| AVOID | Deep conditional and recursive types in application code. They are slow to check and hostile to debug; they belong in libraries. |

Use `NoInfer<T>` (5.5+) to stop one argument's type from widening the inference
that another argument should drive.

## `satisfies`

`satisfies` checks a value against a type **without widening it**, which is what
you usually want for configuration objects and lookup tables.

```ts
// Annotated: checked, but `keys` is now just string[] — the literals are lost.
const routes: Record<string, Handler> = { list: h1, detail: h2 };

// satisfies: checked AND the literal keys survive.
const routes = { list: h1, detail: h2 } satisfies Record<string, Handler>;
type RouteName = keyof typeof routes;   // 'list' | 'detail'
```

| Severity | Rule |
| --- | --- |
| PREFER | `satisfies` over a type annotation whenever you want validation *and* the narrow inferred type. |
| MUST | Keep using an annotation when the wider type is the point — a variable that will later be reassigned to another member of the union. |

## Boundaries

Types describe compile time; the network does not. Every value entering the
process from outside is `unknown` until something checks it.

| Severity | Rule |
| --- | --- |
| MUST | Validate at the boundary — HTTP body, query string, env vars, message payloads, file contents, third-party responses. |
| NEVER | Cast an HTTP response body to its expected interface. `res.json() as Order` is a lie the compiler will believe and the runtime will not honor. |
| PREFER | A schema validator (Zod, Valibot) that produces both the runtime check and the static type from one declaration, so the two cannot drift. |
| MUST | Derive the static type from the schema (`z.infer`), never maintain a hand-written interface alongside it. |

Environment variables deserve explicit mention: `process.env.FOO` is
`string | undefined` and is frequently asserted away. Parse the whole environment
once at startup into a typed, frozen config object, and fail fast if it doesn't
validate.

## Suppression

| Severity | Rule |
| --- | --- |
| PREFER | `@ts-expect-error` over `@ts-ignore`. It fails when the error disappears, so it cleans itself up. |
| MUST | Put a comment on every suppression: what the error is, why it can't be fixed now, what would remove it. |
| NEVER | Use a file-level `// @ts-nocheck` in application code. |
| MUST | Treat a growing suppression count as a signal that a type is modelled wrongly, not that TypeScript is being difficult. |
