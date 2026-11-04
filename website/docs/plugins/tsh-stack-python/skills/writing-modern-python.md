---
title: Writing Modern Python
sidebar_label: writing-modern-python
sidebar_position: 1
description: Guides implementation and review of general modern Python 3.12+ code, covering typing and PEP 695 generics, module layout, asyncio and TaskGroup, exception handling, logging, and the uv, Ruff, ty and pytest workflow.
sources:
  - plugins/tsh-stack-python/skills/writing-modern-python/
sources_hash: "c7021530aa54242510a9f5b192c374d5856c0b1718186b463cd562e8df5268e0"
---

# Writing Modern Python

**Plugin:** [`tsh-stack-python`](/docs/plugins/tsh-stack-python/)  
**Invoke:** `/tsh-stack-python:writing-modern-python`, and Claude also loads it when the work matches its description  
**Used by:** no agent loads it. [`writing-data-models`](/docs/plugins/tsh-stack-python/skills/writing-data-models) links to it as the owner of the cross-cutting concerns outside data modelling. The `reviewing-code` skill in `tsh-product-engineering` loads whichever stack skill is available in the session and names a Python stack skill among its examples, but names no plugin.

Implements or reviews general modern Python 3.12+ code outside the dedicated data-modelling skill in this plugin. The skill owns the cross-cutting concerns: typing, control flow, concurrency, exceptions, logging and tooling. Dataclass, Pydantic, ORM, serialization and persistence-boundary contract decisions are delegated to [`writing-data-models`](/docs/plugins/tsh-stack-python/skills/writing-data-models).

Use it when choosing between `list`, `dict`, `set` and `tuple`, using PEP 695 generics or type aliases, choosing `typing.Protocol` over inheritance, structuring concurrency with `asyncio.TaskGroup`, finding blocking I/O inside a coroutine, chaining exceptions with `raise ... from`, setting up logging in a library, or answering `uv`, Ruff, `ty` and pytest workflow questions.

The repository's own conventions come first: project conventions override the generic guidance where they are more specific.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Module layout** | "Newspaper style": docstring, imports, constants and the public API at the top, with `_`-prefixed private helpers at the bottom |
| **Typing** | Built-in generics (`list[str]`, `A \| None`) and PEP 695 syntax (`def f[T](...)`, `type Alias = ...`), `typing.override` for inherited methods, `typing.Protocol` for duck-typed boundaries, `Self` where a method returns the current class, and no `from __future__ import annotations` |
| **Data structures** | Choosing collections deliberately, `defaultdict` for grouping, `Counter` for tallying, and `collections.abc` abstractions in parameter types |
| **Idioms** | Python 3.12 f-string capabilities, comprehensions and the walrus operator, reverting to an explicit loop when nesting hurts readability, `match` for control flow and not for validation, and no mutable defaults |
| **Concurrency** | `asyncio.TaskGroup` for related tasks with `except*`, `asyncio.gather` only when its fail-fast or collect-all semantics are intended, and blocking or CPU-bound work offloaded with `asyncio.to_thread` |
| **Resources** | `pathlib.Path` and context managers own acquisition and cleanup |
| **Exceptions** | Translate only at meaningful boundaries, preserve causes with `raise ... from e`, bare `raise` to propagate, `raise ... from None` only to suppress an internal cause on purpose, and no `assert` for production validation |
| **Logging** | The project's logging facade, no global logging configuration from inside a library, and no secrets in logs, including in `add_note()` |
| **Tooling** | `uv` for environments and dependencies, Ruff for linting and formatting, `ty` for type checking, and pytest for tests, running focused checks for touched code before broadening |

## How it works

1. **Confirm the boundary.** Identify the owning contract, invariants and any repository-specific instructions before changing code, and enforce the newspaper layout.
2. **Typing**, using the built-in and PEP 695 syntax above.
3. **Data structures**, chosen deliberately.
4. **Idioms**: 3.12 f-strings, comprehensions and the walrus operator, with an explicit `for` loop when nesting hurts.
5. **Delegate data models** to `writing-data-models`.
6. **Concurrency and resources**: structured concurrency, explicit thread offload, and `pathlib` with context managers.
7. **Exceptions and logging**: translate at meaningful boundaries, preserve causes, and log through the project's facade.
8. **Tooling**: run the focused `uv`, Ruff, `ty` and pytest checks for the touched code, then broaden only when the change warrants it.
9. Before finishing a review, work through the review checklist in full.

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | Structure modules newspaper style, with private helpers at the bottom |
| MUST | Use built-in generic syntax and PEP 695 syntax |
| NEVER | Use `from __future__ import annotations` |
| MUST | Favor `typing.Protocol` over deep inheritance for structural, duck-typed boundaries |
| MUST | Use `asyncio.TaskGroup` for related tasks and handle its exceptions with `except*` |
| NEVER | Run blocking I/O or CPU-bound work directly inside a coroutine |
| MUST | Preserve exception causes with `raise ... from e` when translating exceptions at a boundary |
| NEVER | Configure logging globally from inside a library, or use `assert` for production validation |
| MUST | Use `uv`, Ruff, `ty` and pytest |

## References

| Reference | Load when |
| :-- | :-- |
| Review checklist | Reviewing a change, or before finishing an implementation |

## Related skills

- [`writing-data-models`](/docs/plugins/tsh-stack-python/skills/writing-data-models) ships in the same plugin and owns Pydantic, dataclass domain modeling, serialization and persistence-boundary contracts.
- Pandas and Pandera guidance is not covered by this plugin yet. The skill is scoped to general Python 3.12+ practice, not DataFrame manipulation or DataFrame validation.

## Source

[`plugins/tsh-stack-python/skills/writing-modern-python/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-python/skills/writing-modern-python/SKILL.md)
