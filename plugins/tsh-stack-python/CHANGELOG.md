# Changelog

All notable changes to `tsh-stack-python` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.1.0] - 2026-08-19

Initial release, migrated from a pair of GitHub Copilot skills used in a Python
data-exploration project.

### Added

- `writing-modern-python`, adapted from the original Copilot skill of the same
  name. General Python 3.12+ practice: typing and PEP 695 generics, structural
  typing with `Protocol`, module layout, control-flow idioms, structured
  concurrency with `asyncio.TaskGroup`, exception handling, logging, and the
  `uv`/Ruff/`ty`/pytest workflow, with the full checklist in
  `references/review-checklist.md`.
- `writing-data-models`, adapted from the original Copilot skill of the same
  name. Pydantic v2, dataclass, SQLModel, and SQLAlchemy 2.0 data modeling:
  architectural boundaries, modern Pydantic syntax, validation/aliasing/adapters,
  serialization and file I/O, SQLModel/SQLAlchemy bridging, and
  immutability/performance constraints, with the full checklist in
  `references/checklist.md` and worked examples in `references/modeling-examples.md`
  and `references/persistence-examples.md`.
- Both skills ship in one plugin rather than two, because both are Python-stack
  guidance that would change together if the project switched language — the
  `tsh-stack-*` routing question in this repo's `CLAUDE.md` answers "yes" for
  both, and they already cross-reference each other (`writing-modern-python`
  delegates data-model decisions to `writing-data-models`).
