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

## [0.4.0] - 2026-08-18

### Added

- The plugin now bundles the [Playwright MCP server](https://github.com/microsoft/playwright-mcp)
  (`.mcp.json`), so `ui-engineer`'s browser verification works out of the box —
  no per-project MCP setup. The server starts with each session, shows in `/mcp`
  as plugin-provided, and can be disabled there per project. It needs Node.js on
  the machine; context stays lean because Claude Code defers MCP tool schemas
  until a tool is used.

### Changed

- The `ui-engineer` prerequisites in the README no longer claim plugins cannot
  bundle MCP servers — only agent frontmatter is barred from `mcpServers`. Figma
  MCP remains a consuming-project prerequisite because it needs per-user
  authentication, not because bundling is impossible.

## [0.3.0] - 2026-08-18

### Changed

- The agents now pin their models instead of inheriting the session's:
  `software-engineer` and `ui-engineer` run on Sonnet, `code-reviewer` on Opus.
  Inheriting made delegation cost and quality depend on whatever model the session
  happened to use; now plan execution stays fast and cheap in parallel, and the
  pre-merge review always gets the stronger model. To override, set
  `CLAUDE_CODE_SUBAGENT_MODEL` or pass `model` when invoking an agent — both
  outrank the pinned value.

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
