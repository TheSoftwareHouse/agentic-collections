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

## [0.7.0] - 2026-08-26

### Added

- **The frontend flow, migrated from `copilot-collections`: a UI verification gate
  with evidence-based Figma comparison.** Previously `ui-engineer` verified its own
  work by looking at screenshots inside its own context — implementer and judge were
  the same agent. Now every Figma-backed UI task closes through a per-item
  verify-fix loop owned by the orchestrator: a `ui-capture-worker` agent (Haiku,
  read-only) collects ACTUAL evidence with the **Playwright CLI** — `actual.png`,
  `computed-styles.json`, `a11y-snapshot.yml` under
  `specifications/<task-id>/ui-verification/iteration-<N>/` — and a `ui-reviewer`
  agent (Sonnet, read-only) judges it against EXPECTED taken **only from the Figma
  MCP** (a shared `figma-expected.png`, exported once per item and reused across
  iterations), returning PASS, FAIL, or VERIFICATION NOT RUN with a complete
  difference table. FAIL routes the full report back to `ui-engineer`, then fresh
  capture and fresh review — up to 5 iterations, then a structured user gate
  (continue with N more / accept as ESCALATED / custom instruction). Blockers
  (auth, wrong URL, missing artifacts) are VERIFICATION NOT RUN: they consume no
  iteration budget and never count as a pass. Code review starts only after every
  UI item is PASSED or user-acknowledged ESCALATED, and the UI Verification Summary
  is reported separately from code review.
- **Three skills behind the gate**: `reviewing-ui` (user-invocable — one
  capture-plus-comparison pass, the `/tsh-review-ui` equivalent), `verifying-ui`
  (the judging standard: categories, strict tolerances, PASS gate, report format;
  preloaded by `ui-reviewer`), and `capturing-ui-evidence` (the Playwright-CLI
  capture contract and the `TSH_UI_LOGIN_*` repo-root `.env` authentication
  contract; preloaded by `ui-capture-worker`).
- **Not migrated, on purpose**: the Copilot Human-Approval record machinery
  (approval tables, revision predicates, discussion boundaries) — this plugin's
  existing plan contract ("a plan file the user has read", material deviations stop
  the flow) already gates execution; and the engineering-manager agent — the main
  conversation orchestrates in Claude Code.

### Changed

- **`ui-engineer` under the gate implements only** — it skips its own in-browser
  comparison entirely (the gate owns all rendered-result verification, on the
  Playwright CLI and Figma MCP exclusively) and gains an explicit fix-application
  mode: fix ALL differences from a verification report in one pass, then hand back
  for fresh capture and review. Standalone delegations (no gate announced) keep the
  existing self-verifying behavior — examined screenshots per component and state —
  now driven by the Playwright CLI instead of the MCP server.
- **`feature-verifier` walks browser scenarios with the Playwright CLI** — named
  session, `snapshot` for element refs, `click`/`fill`/`press` for steps, per-step
  screenshots saved to explicit files and examined via Read, `console` and
  `requests` for log and network checks. The evidence rules themselves (examined
  screenshot per step, real API calls, verbatim queries and suite commands) are
  unchanged.
- **`orchestrating-feature-implementation`** routes UI verification capture to
  `ui-capture-worker` and verdicts to `ui-reviewer`, requires the exact full dev
  server URL to be user-confirmed (never inferred from config or port scans), and
  gains a Reference Loading table pointing at the new
  `references/ui-verification-gate.md`.
- **New machine prerequisite: the [Playwright CLI](https://www.npmjs.com/package/@playwright/cli)**
  (`playwright-cli`, or `npx playwright-cli`). Every browser-driving component in
  this plugin now runs on it — the gate's capture, `ui-engineer`'s standalone
  checks, and `feature-verifier`'s walkthroughs. Two reasons: capture artifacts are
  files on disk, which MCP screenshots don't provide, and the CLI is materially
  cheaper — only paths and measured values enter model context, instead of full
  screenshots and tool schemas streaming through as MCP traffic. The Figma MCP
  remains a consuming-project prerequisite.

- **Hardening after the first live benchmark run (OSH-410).** Four gaps the run
  exposed, closed: (1) the reviewer can no longer invent waiver states
  ("adjudicated", "accepted deviation") — a difference is excluded from a verdict
  only under an explicit user ruling forwarded in the delegation and cited verbatim;
  everything else beyond tolerance stays FAIL until the user closes it through the
  escalation gate. (2) Capture must measure the visible rendered box — for
  component-library wrappers (MUI, AntD) both the wrapper and the inner control,
  labeled — and the reviewer returns VERIFICATION NOT RUN requesting re-capture
  instead of arithmetically reconstructing dimensions from a wrongly-captured
  element. (3) A PASS verdict must be backed by the current iteration's
  measurements only — an unmeasured critical item cannot be discounted against a
  prior pass. (4) DX: the orchestrator and `reviewing-ui` run a Playwright-CLI
  preflight (`playwright-cli --version`, `npx` fallback) before the first capture
  and, when missing, ask the user whether to install it or wait — the blocker never
  surfaces first inside a subagent, which cannot ask. Also: `feature-verifier`
  saves its evidence screenshots under
  `specifications/<task-id>/verification-evidence/`, and the final verification
  phase may launch its two delegates as immediately consecutive background
  delegations (still concurrent), not only in a single message.

### Removed

- **The bundled Playwright MCP server (`.mcp.json`).** With `ui-engineer` and
  `feature-verifier` switched to the Playwright CLI, the server had no consumer
  left. No invocation handle breaks: plugin-MCP tool names were never safe to
  reference in `tools:` lists or hook matchers (the surviving namespace depends on
  plugin load order), so nothing configured can depend on them. A repository that
  used the bundled server for its own purposes should declare `@playwright/mcp` in
  its own project `.mcp.json`.

## [0.6.0] - 2026-08-21

### Added

- **A `feature-verifier` agent.** It executes a plan's verification document against
  the running application — committed E2E suites, browser walkthroughs with examined
  screenshots, real API calls, database and log checks — and reports per-scenario
  evidence. It uses the Playwright MCP server the plugin already bundles.
- **A verification-document reference** in `creating-implementation-plans`. Every
  non-trivial plan now ships a `specifications/<task-id>/<task-name>.verification.md`
  drafted at planning time, with the user choosing which functional checks it
  includes before implementation starts.

### Changed

- **Verification now follows a pyramid, so nothing runs twice.** Previously the same
  suites could execute a dozen times per feature: per task by the implementer, again
  by the orchestrator's spot-check, again per phase, again in the plan's own review
  phase, and once more in the closing code review. Now each task runs only checks
  scoped to its own files and is trusted from its report; each phase closes with one
  integration checkpoint; and the plan's final verification phase is the single full
  pass — `code-reviewer` (static checks, unit, integration, build) in parallel with
  `feature-verifier` (E2E suite plus the functional scenarios). After that phase
  passes, nothing re-reviews: findings route back as scoped fixes with scoped
  re-checks.
- **`code-reviewer` and `reviewing-code` honor caller-set suite scope.** When a
  delegation assigns functional and E2E verification to a parallel verifier, the
  review excludes those suites and says so; a standalone "review this PR" still runs
  everything. Plans from before 0.6.0 still work — a plan without a final
  verification phase gets the old single full-scope review.

### Changed

- **The README now says where Jira access comes from.** `tsh-core` bundles the
  Atlassian MCP server, so a teammate reading only this plugin's README had no way to
  know Jira and Confluence were available at all. It sits in `tsh-core` rather than
  here for the same reason Git worktrees do: every discipline reads from Jira, so
  declaring the server in each discipline plugin would mean maintaining the same
  endpoint in five files. Playwright stays here — it exists for `ui-engineer` alone.

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
