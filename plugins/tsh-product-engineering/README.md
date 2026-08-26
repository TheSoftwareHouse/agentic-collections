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
| `reviewing-ui` | `/tsh-product-engineering:reviewing-ui` | One UI verification pass: fresh Playwright-CLI capture judged against the Figma design — PASS, FAIL, or VERIFICATION NOT RUN with a complete difference table |
| `verifying-ui` | model-invoked only | The judging standard behind UI verification: categories, strict tolerances, PASS gate, report format — preloaded by `ui-reviewer` |
| `capturing-ui-evidence` | model-invoked only | The Playwright-CLI capture contract: artifact directory rules, stabilization, the `TSH_UI_LOGIN_*` `.env` auth contract — preloaded by `ui-capture-worker` |
| `discovering-technical-context` | `/tsh-product-engineering:discovering-technical-context` | Project conventions in priority order: plan context → instructions → codebase patterns → external docs |
| `software-engineer` (agent) | `@tsh-product-engineering:software-engineer` | Implements delegated plan tasks — code, tests, config — and verifies with the plan's commands |
| `ui-engineer` (agent) | `@tsh-product-engineering:ui-engineer` | Implements UI from a Figma reference; under the UI verification gate it implements and fixes, while capture and judgment run in the two agents below |
| `ui-capture-worker` (agent) | `@tsh-product-engineering:ui-capture-worker` | Mechanical evidence collector: Playwright-CLI screenshot, computed styles, and a11y snapshot into the iteration directory, plus the shared Figma reference export |
| `ui-reviewer` (agent) | `@tsh-product-engineering:ui-reviewer` | Read-only design judge: compares capture artifacts against the Figma design and returns PASS / FAIL / VERIFICATION NOT RUN with recommended fixes |
| `code-reviewer` (agent) | `@tsh-product-engineering:code-reviewer` | Read-only reviewer: runs the checks itself and returns a structured findings report |
| `feature-verifier` (agent) | `@tsh-product-engineering:feature-verifier` | Executes a plan's verification document against the running app — E2E suites, browser walkthroughs with examined screenshots, API/DB/log checks — with per-scenario evidence |

All skills are model-invocable, and their descriptions are written to route on the
work you describe rather than on the skill's name — "implement this ticket", "plan
this feature", "is this ready to merge", "does this page match the design". Each one
also names the sibling that owns the adjacent job, so they do not compete for the
same request. `verifying-ui` and `capturing-ui-evidence` stay out of the `/` menu:
they are contracts the two UI agents preload, not commands worth typing.

Release notes live in [`CHANGELOG.md`](CHANGELOG.md).

### Prerequisites: Playwright CLI and Figma MCP

**All browser evidence in this plugin runs on the
[Playwright CLI](https://www.npmjs.com/package/@playwright/cli)** — the UI
verification gate's capture (`ui-capture-worker`), `ui-engineer`'s standalone
screenshot checks, and `feature-verifier`'s browser walkthroughs. Its evidence is
files on disk — `actual.png`, `computed-styles.json`, `a11y-snapshot.yml` under
`specifications/<task-id>/ui-verification/`, per-step screenshots for functional
scenarios — and only paths and measured values enter model context, which is why it
replaced the Playwright MCP server this plugin bundled through 0.6.0. Have
`playwright-cli` on the machine: `npm install -g @playwright/cli@latest`, or a
project-local install reached via `npx playwright-cli` (Node.js required either
way). You do not have to remember this: before the first capture, the workflow runs
`playwright-cli --version` (with an `npx` fallback) and, when neither answers, asks
whether to install it for you or wait while you do it yourself.

**Design fetching needs the Figma MCP server**, which needs per-user
authentication, so we deliberately leave it to the consuming project — connect it
there. Without it, agents stop and report what is missing rather than guessing at a
design; the `ui-reviewer` reports `VERIFICATION NOT RUN`.

Have the target app already running and know the exact dev server URL: the
workflow asks you to confirm it once and pins it for the whole loop.

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
