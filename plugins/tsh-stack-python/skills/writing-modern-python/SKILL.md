---
name: writing-modern-python
description: "Guides implementation and review of general modern Python 3.12+ code. Activate for Python typing, PEP 695 generics, structural typing, module layout, control flow (comprehensions, walrus, 3.12 f-strings), asyncio and TaskGroup, exception handling, pathlib, logging, pytest, or uv/Ruff/ty workflows."
when_to_use: "Trigger on: choosing between list/dict/set/tuple, PEP 695 generics or type aliases, typing.Protocol vs inheritance, asyncio.TaskGroup or structured concurrency, blocking I/O inside a coroutine, exception chaining with raise ... from, logging setup in a library, or uv/Ruff/ty/pytest workflow questions."
---

# Writing modern Python

Implement or review general modern Python 3.12+ code outside the dedicated
data-modeling skill in this plugin.

## Applicability and Precedence

Read the repository's own conventions first — project conventions override
generic guidance where they are more specific.

Delegate dataclass, Pydantic, ORM, serialization, and persistence-boundary
contract decisions to
[`writing-data-models`](../writing-data-models/SKILL.md), which ships in this
same plugin. This skill owns cross-cutting concerns: typing, control flow,
concurrency, exceptions, logging, and tooling.

## Non-negotiable Rules

| Severity | Rule |
| :-- | :-- |
| MUST | Structure modules "newspaper style": docstring, imports, constants, and public API at the top; private helpers (`_`-prefixed) pushed to the bottom. |
| MUST | Use built-in generic syntax (`list[str]`, `dict[str, int]`, `A \| None`) and PEP 695 syntax (`def f[T](...)`, `type Alias = ...`). |
| NEVER | Use `from __future__ import annotations` — obsolete in modern Python. |
| MUST | Favor `typing.Protocol` over deep inheritance hierarchies for structural, duck-typed boundaries. |
| MUST | Use `asyncio.TaskGroup` for structured concurrency over related tasks, and handle its exceptions with `except*`. Use `asyncio.gather` only when its distinct fail-fast/collect-all semantics are actually intended. |
| NEVER | Run blocking I/O or CPU-bound work directly inside a coroutine. Offload it explicitly with `asyncio.to_thread` (or an equivalent thread boundary). |
| MUST | Preserve exception causes with `raise ... from e` when translating exceptions at a boundary; use bare `raise` for propagation. Use `raise ... from None` only to intentionally suppress an internal cause. |
| NEVER | Configure logging globally from inside a library. Use the project's logging facade and keep logs free of secrets, including in `add_note()`. |
| NEVER | Use `assert` for production validation — it is stripped under `-O` and is not a substitute for an explicit check. |
| MUST | Use `uv` for environment/dependency management, Ruff for linting/formatting, `ty` for type checking, and pytest for tests; run the focused checks for touched code before broadening. |

## Reference Loading

| Reference | Load when | Covers |
| :-- | :-- | :-- |
| [Review checklist](./references/review-checklist.md) | Reviewing a change, or before finishing an implementation | The full workflow and quick-review checks: typing, data structures, idioms, concurrency, resource management, exception handling, logging, and tooling |

## Procedure

1. **Confirm the boundary.** Identify the owning contract, invariants, and
   any repository-specific instructions before changing code. Enforce the
   newspaper layout for module structure.
2. **Typing.** Built-in generics and union syntax; PEP 695 generics and type
   aliases; `typing.override` for inherited methods; `typing.Protocol` for
   duck-typing boundaries.
3. **Data structures.** Choose collections deliberately — `list` for
   mutability, `tuple` for fixed/hashable records, `set` for uniqueness and
   fast lookup, `collections.defaultdict` for grouping,
   `collections.Counter` for tallying.
4. **Idioms.** Python 3.12 f-string capabilities (quote reuse, multi-line
   expressions in braces), comprehensions, and the walrus operator (`:=`) —
   but revert to an explicit `for` loop if nesting hurts readability.
5. **Delegate data models.** Dataclass, Pydantic, ORM, and serialization
   contract decisions belong to
   [`writing-data-models`](../writing-data-models/SKILL.md).
6. **Concurrency and resources.** Structured concurrency with
   `asyncio.TaskGroup`; explicit thread offload for blocking/CPU-bound work;
   `pathlib.Path` and context managers for resource lifetime.
7. **Exceptions and logging.** Translate exceptions only at meaningful
   boundaries, preserve causes, and log through the project's facade without
   leaking secrets.
8. **Tooling.** `uv`, Ruff, `ty`, and pytest — run the focused checks for the
   touched code, then broaden only when the change warrants it.
9. Before finishing a review, work through
   [`review-checklist.md`](./references/review-checklist.md) in full.

## Related Skills

- [`writing-data-models`](../writing-data-models/SKILL.md) — ships in this
  same plugin; owns Pydantic, dataclass domain modeling, serialization, and
  persistence-boundary contracts.
- Pandas and Pandera guidance is not covered by this plugin yet — this skill
  is scoped to general Python 3.12+ practice, not DataFrame manipulation or
  DataFrame validation.
