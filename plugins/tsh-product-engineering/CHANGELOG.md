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

## [0.7.0] - 2026-08-24

One theme: a delegated run now costs what the work costs. Checks run once, at the
tier that owns them; gates and discovery sweeps execute on the cheapest model that
can run them; delegations carry only the plan sections a delegate needs; and plans
prove their commands, artifacts and parallelism before execution starts. The rules were
calibrated against two full orchestrated runs of this plugin — a seven-phase and a
three-phase feature, each across three packages.

### Added

- **A `gate-runner` agent — no gate output in the orchestrator's context.** A small
  read-only agent on the cheapest model tier that executes delegated verification
  commands exactly once and returns verbatim pass/fail evidence with failure
  excerpts. It runs every phase checkpoint (the phase's `Verification:` line,
  commands verbatim) and the final verification phase's full gate set — typecheck,
  lint, format check, build, unit and integration suites — so neither the
  orchestrating conversation nor the review's expensive context spends anything on
  watching suites scroll by. In the final phase it launches alongside
  `feature-verifier` and its report is handed to `code-reviewer`; when both sides
  can rebuild the same artifact (a package `dist/`), the orchestrator names the
  collision in both delegations and authorizes exactly one re-run on that failure
  signature.
- **A `context-scout` agent — planning discovery leaves the expensive context.** A
  read-only agent on the cheapest model tier that answers locate, enumerate, and
  excerpt questions with file:line locations and bounded verbatim excerpts — never
  conclusions — and reports empty searches as evidence, so the planner can judge
  coverage. The planner launches scouts in parallel for discovery,
  current-implementation analysis, and the inventory sweep, reads directly only the
  design-critical files, and writes Technical Context itself from the returned
  evidence. Gathering is delegated; interpretation never is — a confidently wrong
  convention in Technical Context would poison every delegate that consumes it
  as-is. The orchestrating workflow routes discovery the same way: its task-routing
  table names the scout instead of declaring discovery out of scope, a rule covers
  the pre-planning window where exploration actually starts, and the skills spell
  out that a file dumped inline through a shell command is an inline read all the
  same — in an observed run the sweep was skipped in favor of shell reads that
  pulled whole source files into the orchestrator's context.
- **Phases can be independent, and the orchestrator executes the plan as a
  dependency graph.** A phase that consumes nothing from a predecessor — no shared
  files, no contract crossing the boundary, typically a different package — is
  marked `Independent of Phase N`, and at every gate the orchestrator launches
  everything whose dependencies have passed. A failure stops only its own line. The
  final verification phase is never independent — it gates on everything.
- **Light dependency chains batch into one delegation.** Two or three consecutive
  same-package tasks (around ten combined files, no integration-stack, E2E or
  browser work, never across a phase checkpoint) share one delegate instead of each
  paying a context read and a report-and-gate cycle. A batch that fails mid-way
  reports per-task state and the remainder goes to a fresh delegate.
- **Contract changes own their blast radius.** A `software-engineer` that changes a
  shared contract's shape searches the workspace for every constructor, literal and
  exhaustive assertion of it — test directories, e2e specs, fixtures, untyped
  scripts — and fixes the mechanical breakage beyond its `**Files:**` list instead
  of leaving it for a later gate. The planner produces such a task's `**Files:**`
  list from the same search. Seven of the ten defects that escaped task gates in
  the observed runs were this one pattern.
- **An inventory sweep at planning time** (`references/inventory-sweep.md`, plus a
  MUST and a procedure step in `creating-implementation-plans`). When a task changes
  a contract, the planner searches by inventory pattern — `information_schema`,
  migration ledgers, `toEqual([`, allowlists, fake-server fixtures — across every
  test tier: an enumerating inventory names every existing member and never the new
  one, so no search for the contract's name can find it, and one living in an e2e
  suite is invisible to every checkpoint before the final phase. Every hit closes
  into a task's `**Files:**` list or a checked-unaffected note.
- **`feature-verifier` attributes failures only as far as it proved them.** Before
  blaming the environment it checks the failing expectation against current source,
  reads deep-equality diffs in both directions, names the assertions a failure
  masked, and labels each attribution proven or hypothesis. It runs suites in the
  foreground, captures full output to a file on the first run, and saves
  screenshots and logs outside the repository so evidence never pollutes the change
  set the parallel reviewer is judging.
- **Execution starts from known state.** The orchestrator snapshots `git status`
  first — pre-existing working-tree modifications are declared outside the work's
  scope up front and never staged with the feature — and collects the working
  branch as a pinned input, asking before the first file is edited when on the
  default branch.

### Changed

- **Tasks are sized by what stays green, not by what fits in a file.** A task is the
  smallest change that leaves the project's static gate green on its own: a
  contract change ships with the call sites it breaks, splits go by behavior rather
  than by layer, and two to five tasks is a phase. A Definition of Done item that
  cannot pass until a later task lands means the two are one task — the
  orchestrator merges them in the plan instead of recording the caveat.
- **Every check belongs to exactly one tier.** File-scoped tests over what a task
  wrote go in its Definition of Done; one integration check plus the package-wide
  typecheck or build close each phase — using the package-scoped test run where
  typecheck and build exclude spec files; full suites, E2E and functional scenarios
  run once, in the final verification phase. Nothing re-runs for confidence or to
  recover lost output — output is captured to a file on the first run — and a
  failed phase checkpoint runs again only after its scoped fix lands.
- **Running a formatter is not a check.** It runs before a task's checks, as part
  of doing the work, and never justifies re-running one that already passed;
  `code-reviewer` runs it in check mode only and records drift as a finding.
- **Parallelism is designed, then proven — and an unjustified chain is not
  actionable.** Every phase states its parallel groups or names the data or
  contract dependency behind each sequential edge; an edge justified only by
  layering is a mis-slicing to re-cut by behavior, with fork–join for shared
  registration hotspots. When independence is uncertain the planner checks — diffs
  the `**Files:**` lists, greps outputs against inputs — instead of sequencing by
  default. The orchestrator routes a multi-behavior plan arriving as an unjustified
  chain back to planning, existing plans included.
- **Delegations carry section headings; delegates read only those sections.** Every
  delegation names the exact headings a delegate needs — Goal, Technical Context,
  its tasks, anything a task references — and agents locate them by heading, never
  by line number: the plan mutates during execution, so ranges rot.
- **Plans prove their commands, artifacts and save path before handover.** Every
  Definition of Done and phase command must name a script that exists in the
  project's manifest; each distinct file-scoped runner shape is executed once per
  package to prove it actually scopes, by its reported file count — a runner that
  silently swallows its path arguments goes green on the whole suite; every
  endpoint, table, fixture or env var a check names and the plan does not create is
  traced to source; and `git check-ignore` warns when the plan path would never
  travel in a commit.
- **The review grounds in gate evidence.** `code-reviewer` works diff-first,
  consumes the `gate-runner` report embedded in its delegation and runs only what
  it missed, keeps suite output out of its context, fails fast on a broken build,
  runs each gate once, and never writes to the working tree. The trust rule is
  restated to what it was always for: never accept results from the party that
  wrote the code; a dedicated runner's verbatim output is evidence.
- **Checkbox bookkeeping is split, not duplicated.** Implementers tick their own
  task and Definition of Done boxes; the orchestrator's gate confirms the ticks
  match the report and fixes a miss. An unsatisfied item stays unchecked and
  explained in the report, and a deviation that changes a pinned contract updates
  the plan's pinned-contract block in the same edit.
- **Discovery is scoped to the change.** `discovering-technical-context`'s
  categories are now a menu keyed to what the task touches — one nearest exemplar
  per open question, decision records opened from their index by title — and
  discovery ends when the open questions have answers, never when the repository is
  fully understood.
- **Verification documents name their preconditions honestly.** Every endpoint,
  table and fixture a scenario names is traceable to source — the verifier stops on
  a failed precondition, so one invented artifact deadlocks the phase. Documents
  state a clean-baseline path, preferring a scratch database on the same instance
  over volume resets (which stay reserved for what the user authorized), and say
  which database writes scenarios *may* make, not only which are forbidden.

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
