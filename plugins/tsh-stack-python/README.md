# TSH Stack: Python

TSH conventions for modern Python 3.12+ — general implementation and review
practices, and data modeling with Pydantic v2, dataclasses, SQLModel, and
SQLAlchemy 2.0.

This is a **stack** plugin, not a discipline plugin. Install it into the
projects that run on Python, at `project` scope, so it travels with the repo —
the repo already knows what it runs on. Your discipline plugin
(`tsh-product-engineering` and friends) travels with **you**, at `user` scope,
and so does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-python@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `writing-modern-python` | `/tsh-stack-python:writing-modern-python` | General Python 3.12+ practice: typing and PEP 695 generics, structural typing, module layout, control-flow idioms, structured concurrency with `asyncio.TaskGroup`, exception handling, logging, and the `uv`/Ruff/`ty`/pytest workflow |
| `writing-data-models` | `/tsh-stack-python:writing-data-models` | Pydantic v2, dataclass, SQLModel, and SQLAlchemy 2.0 data modeling: architectural boundaries, modern Pydantic syntax, validation/aliasing/adapters, serialization and file I/O, SQLModel/SQLAlchemy bridging, and immutability/performance constraints |

Both skills are model-invocable — Claude loads them when the work matches
their description, so you don't have to remember to type the command.

The two are designed to work together: `writing-modern-python` explicitly
delegates dataclass, Pydantic, ORM, and serialization decisions to
`writing-data-models`, and links to it directly. Because they ship in the
same plugin, that link always resolves.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates
arrive with `/plugin update`.

## Not covered yet

Deliberate gaps, so they read as scope rather than oversight:

- **Pandas** — DataFrame manipulation, dtypes, and vectorized workflows have
  no skill of their own yet.
- **Pandera** — DataFrame schema validation has no skill of their own yet.
- **Web framework guidance** — FastAPI, Django, and Flask have no skill of
  their own; `writing-data-models` covers the Pydantic/SQLModel layer
  underneath them.

## Scope

The routing question for this plugin is *would this guidance change if the
project switched language or framework?* If yes, it belongs here. If it would
change when the **reader** switched job, it belongs in a discipline plugin
instead.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change
never reaches them.

Two rules that bite hardest here:

- **Skill names carry no framework version.** The name is the invocation
  command, so pinning a version forces a rename on every upgrade.
- **Reference only files inside this plugin**, by relative path. A skill
  cannot reliably read another plugin's files, because that plugin may not be
  installed — and the failure is a silent dead link, not an error.
