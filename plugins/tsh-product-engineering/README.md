# TSH Product Engineering

Feature implementation, code review, refactoring, debugging and TDD workflows.

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
| `orchestrating-feature-implementation` | `/tsh-product-engineering:orchestrating-feature-implementation` | Drives implementation end to end: plan readiness, delegation to the agents below (parallel where the plan allows), per-task verification, final review |
| `creating-implementation-plans` | `/tsh-product-engineering:creating-implementation-plans` | Authors `*.plan.md` files from a menu of building blocks — verifiable tasks, persisted technical context, parallel groups |
| `reviewing-code` | `/tsh-product-engineering:reviewing-code` | TSH's structured review: plan comparison, executed test suites, anti-patterns, security, scalability |
| `discovering-technical-context` | `/tsh-product-engineering:discovering-technical-context` | Project conventions in priority order: plan context → instructions → codebase patterns → external docs |
| `software-engineer` (agent) | `@tsh-product-engineering:software-engineer` | Implements delegated plan tasks — code, tests, config — and verifies with the plan's commands |
| `ui-engineer` (agent) | `@tsh-product-engineering:ui-engineer` | Implements UI from a Figma reference and verifies the rendered result in a browser |
| `code-reviewer` (agent) | `@tsh-product-engineering:code-reviewer` | Read-only reviewer: runs the checks itself and returns a structured findings report |

All skills are model-invocable: describe the work ("plan this feature", "implement
the plan", "review this change") and the right one loads without naming it.

Release notes live in [`CHANGELOG.md`](CHANGELOG.md).

### Prerequisites for `ui-engineer`

The agent fetches designs through the **Figma MCP server**, which plugins cannot
bundle — connect it in the consuming project (and optionally a browser tool such as
the Playwright MCP for rendered verification). Without it, the agent stops and
reports what is missing rather than guessing at a design.

## Not covered yet

E2E test suites (`tsh-product-testing`), infrastructure and CI (`tsh-platform-engineering`),
and discovery/BA work (`tsh-product-management`) are other plugins' ground. Deeper
analysis skills (codebase analysis, gap analysis) are candidates for a later wave.

Git worktree lifecycle lives in `tsh-core`, not here — it doesn't change with your
discipline. Install that alongside this one.

## Contributing

Add an agent as `agents/<agent-name>.md`, a skill as `skills/<skill-name>/SKILL.md`.
Start from [`templates/agent.md`](../../templates/agent.md) or
[`templates/SKILL.md`](../../templates/SKILL.md), and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Once installed, components from this plugin are invoked as
`@tsh-product-engineering:<agent>` and `/tsh-product-engineering:<skill>`.
