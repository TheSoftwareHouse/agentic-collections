# TSH Product Engineering

Spec-driven feature implementation: committed plan files, delegated implementer subagents, and TSH's structured pre-merge code review.

Install at **user scope** — this plugin travels with you, not with a repository. It
carries TSH's spec-driven implementation workflow: a plan file the team can read and
commit, implementer subagents that keep file churn and MCP traffic out of your
conversation, and a delegated review gate at the end.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-product-engineering@tsh-agentic-collections
```

## What's in it

| Component | Invoke | Covers |
| :-- | :-- | :-- |
| `orchestrating-feature-implementation` | `/tsh-product-engineering:orchestrating-feature-implementation` | Drives implementation end to end: plan readiness, delegation to the agents below (parallel where the plan allows), and a verification pyramid — scoped task checks, one checkpoint per phase, one final full pass |
| `creating-implementation-plans` | `/tsh-product-engineering:creating-implementation-plans` | Authors `*.plan.md` files from a menu of building blocks — verifiable tasks, persisted technical context, parallel groups |
| `reviewing-code` | `/tsh-product-engineering:reviewing-code` | TSH's structured review: plan comparison, executed test suites, anti-patterns, security, scalability |
| `discovering-technical-context` | `/tsh-product-engineering:discovering-technical-context` | Project conventions in priority order: plan context → instructions → codebase patterns → external docs |
| `software-engineer` (agent) | `@tsh-product-engineering:software-engineer` | Implements delegated plan tasks — code, tests, config — and verifies with the plan's commands |
| `ui-engineer` (agent) | `@tsh-product-engineering:ui-engineer` | Implements UI from a Figma reference and verifies the rendered result in a browser |
| `code-reviewer` (agent) | `@tsh-product-engineering:code-reviewer` | Read-only reviewer: judges the change set from executed gate evidence and returns a structured findings report |
| `gate-runner` (agent) | `@tsh-product-engineering:gate-runner` | Executes phase checkpoints and the final phase's gates — typecheck, lint, build, unit and integration — once each, and hands the code reviewer verbatim pass/fail evidence |
| `context-scout` (agent) | `@tsh-product-engineering:context-scout` | Read-only planning scout: sweeps the repo for conventions, call sites and inventories, returning file:line locations and verbatim excerpts — never conclusions |
| `feature-verifier` (agent) | `@tsh-product-engineering:feature-verifier` | Executes a plan's verification document against the running app — E2E suites, browser walkthroughs with examined screenshots, API/DB/log checks — with per-scenario evidence |

All skills are model-invocable, and their descriptions are written to route on the
work you describe rather than on the skill's name — "implement this ticket", "plan
this feature", "is this ready to merge". Each one also names the sibling that owns the
adjacent job, so the four do not compete for the same request.

Release notes live in [`CHANGELOG.md`](CHANGELOG.md).

### Prerequisites for `ui-engineer` and `feature-verifier`

**Browser verification ships with the plugin.** The plugin bundles the
[Playwright MCP server](https://github.com/microsoft/playwright-mcp) (`.mcp.json`),
so rendered-result verification and functional browser walkthroughs work out of the
box. It starts automatically with
each session and appears in `/mcp` as plugin-provided; disable it per project from
the same `/mcp` panel if a repository never renders UI. It needs Node.js on the
machine — `npx` fetches the server, and Playwright downloads its browser on first
use. Context cost stays low: Claude Code defers MCP tool schemas by default (tool
search), so sessions that never touch a browser pay only for the tool names.

**Design fetching does not.** The agent reads designs through the **Figma MCP
server**, which needs per-user authentication, so we deliberately leave it to the
consuming project — connect it there. Without it, the agent stops and reports what
is missing rather than guessing at a design.

## Not covered yet

E2E test suites (`tsh-product-testing`), infrastructure and CI (`tsh-platform-engineering`),
and discovery/BA work (`tsh-product-management`) are other plugins' ground. Deeper
analysis skills (codebase analysis, gap analysis) are candidates for a later wave.

Git worktree lifecycle lives in `tsh-core`, not here — it doesn't change with your
discipline. **Jira and Confluence access is there too:** `tsh-core` bundles the
Atlassian MCP server, because every discipline reads from Jira, not just this one.
Install it alongside this one and authenticate once with `/mcp`.

## Contributing

Add an agent as `agents/<agent-name>.md`, a skill as `skills/<skill-name>/SKILL.md`.
Start from [`templates/agent.md`](../../templates/agent.md) or
[`templates/SKILL.md`](../../templates/SKILL.md), and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Once installed, components from this plugin are invoked as
`@tsh-product-engineering:<agent>` and `/tsh-product-engineering:<skill>`.
