# Changelog

All notable changes to `tsh-product-engineering` are documented here. The format
follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the
versions are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.2.0] - 2026-08-18

### Added

- `creating-implementation-plans`, `orchestrating-feature-implementation`,
  `reviewing-code`, and `discovering-technical-context` skills — the product
  engineering workflow migrated from `copilot-collections` and redesigned for Claude
  Code. Plans are still committable markdown files that survive across sessions, but
  the structure is now a menu of building blocks the model assembles per task instead
  of a fixed template, and the Copilot-era Human Approval protocol (approval tables,
  revision predicates, two-gate separation) is gone — the user approves by reading
  the plan and saying so.
- `software-engineer`, `ui-engineer`, and `code-reviewer` agents — the first agents
  in this marketplace. The main conversation orchestrates; these subagents implement
  and review, keeping file churn and MCP traffic out of your context. Plans now mark
  independent tasks as parallel groups, and the orchestration skill launches one
  implementer per task in the group concurrently.
- Not migrated, on purpose: the engineering-manager agent (the main conversation is
  the orchestrator in Claude Code), the plan-reviewer agent and approval gates (they
  slowed delivery), and the architect model bands (Claude Code picks a model per
  invocation). `ui-engineer` requires the Figma MCP server to be connected in the
  consuming project — it stops and says so when it is not.
