# Modern Python Review Checklist

Use this checklist to implement or review general Python 3.12+ code, outside
data modeling, pandas, and Pandera concerns.

## Module Structure

- [ ] Module docstrings, imports, constants, and the public API sit at the top.
- [ ] Private helpers (`_`-prefixed) are pushed to the bottom, so the module reads high-level to low-level.
- [ ] Inverted structures (private functions at the top) are flagged.

## Typing

- [ ] Built-in generic syntax (`list[str]`, `dict[str, int]`) and union syntax (`A | None`) are used, not `typing.List`/`Dict`/`Optional`.
- [ ] `from __future__ import annotations` is absent — it is obsolete in modern Python.
- [ ] PEP 695 syntax is used where it applies: `def f[T](...)`, `type Alias = ...`.
- [ ] `typing.override` marks inherited methods that override a base implementation.
- [ ] `typing.Protocol` is used for duck-typing boundaries in place of deep inheritance hierarchies.
- [ ] `Self` is used for instance or class methods that return the current class; the concrete class annotation is used when the exact class (not a subclass) is returned.

## Data Structures

- [ ] Collections are chosen deliberately: `list` for mutability, `tuple` for fixed/hashable records, `set` for uniqueness and fast lookup.
- [ ] `collections.defaultdict` is used for grouping instead of manual `if key not in dict` checks.
- [ ] `collections.Counter` is used for tallying instead of a manually incremented dict.
- [ ] `collections.abc` abstractions (e.g. `Iterable`, `Mapping`) are accepted in parameter types; concrete containers are returned by default.

## Idioms

- [ ] Python 3.12 f-string capabilities are used where they help: quote reuse and multi-line expressions inside braces.
- [ ] Comprehensions and the walrus operator (`:=`) are used for concise filtering and assignment.
- [ ] Deeply nested comprehensions are rewritten as explicit `for` loops when nesting hurts readability.
- [ ] `match` clarifies control flow and pattern handling; it is not used as a substitute for validation.
- [ ] Mutable defaults (`def f(x: list = [])`) are absent.

## Concurrency

- [ ] `asyncio.TaskGroup` is used for structured concurrency over related tasks.
- [ ] `asyncio.gather` is used only when its distinct fail-fast/collect-all semantics are intentional, not as a default habit.
- [ ] Task groups handle exceptions with `except*`, not a bare `except`.
- [ ] Sibling tasks are not created with unstructured `asyncio.create_task` outside a `TaskGroup`.
- [ ] Blocking I/O or CPU-bound work is never run directly inside a coroutine; it is offloaded via `asyncio.to_thread` or an equivalent explicit thread boundary.

## Resources

- [ ] Resource lifetime is explicit: `pathlib.Path` and context managers own acquisition and cleanup.
- [ ] `Path` convenience methods (`read_text`, `write_text`) are acceptable when they keep ownership and cleanup clear.

## Exceptions

- [ ] Exceptions are translated only at meaningful boundaries, not defensively at every call site.
- [ ] Causes are preserved with `raise ... from e` when translating an exception.
- [ ] Bare `raise` is used for simple propagation.
- [ ] `raise ... from None` is used only to intentionally suppress an internal cause, not as a default.
- [ ] Production code does not use `assert` for validation — it is stripped under `-O`.

## Logging

- [ ] The project's logging facade (e.g. Loguru) is used; libraries do not configure logging globally.
- [ ] Logs are useful without exposing secrets, including in `add_note()` diagnostic context.

## Tooling

- [ ] `uv` manages environments and dependencies.
- [ ] Ruff handles linting and formatting.
- [ ] `ty` performs type checking.
- [ ] pytest is the test runner.
- [ ] Broad type-check or lint suppressions are flagged rather than accepted silently.
- [ ] Performance work is backed by a measurement, not undertaken speculatively.
- [ ] Focused pytest, Ruff, and `ty` checks run for the touched code; broader validation follows only when the change warrants it.
