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

## [0.5.0] - 2026-08-20

### Changed

- **All four skills have new `description` and `when_to_use` text.** Claude Code routes
  on that text alone and never reads a skill's body to decide, so this is the only
  surface that determines whether a skill loads when nobody names it. The old text
  described mechanism ("delegates its tasks to implementer subagents"); the new text
  claims the words people actually use, and each pair now ends by naming the sibling
  that owns the adjacent job, so the four stop competing with each other.
- **`discovering-technical-context` no longer advertises itself for implementation.**
  It previously said "Use before implementing in an unfamiliar codebase" and listed
  "starting implementation or test-writing" as a trigger — competing with
  `orchestrating-feature-implementation` for exactly the requests that skill exists to
  handle, while being the cheapest of the four to load. It is now scoped to conventions
  questions. The three agents that preload it via `skills:` are unaffected; only
  main-conversation routing changes. **This is the behaviour most likely to be
  noticeable**: implementation requests should now reach the orchestrator instead.
- **`creating-implementation-plans` states why a committed plan beats a scratch one.**
  Its description now names the literal `specifications/<task-id>/<task-name>.plan.md`
  path and the three consequences of planning outside the repository — cannot be
  committed, reviewed in a PR, or read by an implementer subagent. Built-in plan mode
  writes to `~/.claude/plans/`, and the old description gave Claude no reason to prefer
  ours.
- **`reviewing-code` distinguishes itself from a diff-only review.** It now says what
  it does that a plain correctness pass does not: reads the plan first, and actually
  executes the project's suites rather than reading the diff. Near-identical
  descriptions are a coin flip, and the loser is silently never invoked.
- **The "Optional and may not be installed" hedge is gone from all four skills.** It
  was copy-pasted boilerplate meant for cross-plugin references, but every Related
  Skills link in this plugin is to a sibling that ships in the same plugin at the same
  version. In `orchestrating-feature-implementation` it directly contradicted the
  plan rule three sections above it — telling Claude that
  `creating-implementation-plans` was "never a prerequisite" while a MUST required it —
  which handed the model explicit permission to skip the plan. The genuine cross-plugin
  caveat is kept and now names the plugins it applies to.
- **`plugin.json` and the marketplace entry describe what actually ships.** Both
  advertised "refactoring, debugging and TDD workflows" with matching keywords; no
  component covers any of the three. A teammate who installed on that basis, asked for
  a TDD loop and got nothing had reason to conclude the plugin's skills do not fire.
- **Cost of the above:** the plugin's routing footprint — the combined `name`,
  `description` and `when_to_use` characters Claude Code preloads to route on — grows
  from 2,289 to 2,986 characters (+30%). No pair comes near the 1,536-character
  per-skill cap, but the increase is paid by every session that installs this plugin,
  including sessions that never implement anything. Always-on cost was ~989 tokens at
  0.4.1.
- **What this does not change.** Routing decides which skill loads; it does not survive
  the moment Claude has already judged a request to be a one-liner. Expect requests
  shaped like "implement this ticket" to reach `orchestrating-feature-implementation`
  and requests shaped like "just add a null check" to keep bypassing it. That case needs
  a hook, not more description text, and none ships here.

## [0.4.1] - 2026-08-18

### Changed

- `ui-engineer` must now verify each component by taking a browser screenshot at
  the design's breakpoint and examining the image — including design-defined
  states (hover, focus, error, empty). Previously "verify in a real browser"
  could be satisfied by accessibility snapshots and click-throughs, which are
  text-only and let visual defects (spacing, colors, typography) pass unnoticed;
  those now count as navigation, not verification.

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
