# Changelog

All notable changes to `tsh-product-testing` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-10-02

### Fixed

- **`auditing-accessibility` no longer competes with the frontend stack's
  `ensuring-accessibility`.** Its description and trigger list claimed "implementing
  an accessible widget, form or dialog" and "building an accessible modal, menu,
  tabs, combobox or form" — the exact triggers of the implementation skill in
  `tsh-stack-frontend`, which already pointed back here. Both now route one way:
  auditing an existing page is this plugin, building the component is the stack.
- `e2e-engineer` preloaded `auditing-accessibility` (about 130 lines on every E2E
  delegation) and never used it; the preload is gone. The locator rule that a
  missing accessible name is a finding stays in `writing-playwright-e2e-tests`.
- README claimed the bundled Playwright MCP "mirrors the Playwright server in
  `tsh-product-engineering`"; that plugin dropped its server in 0.7.0 for the
  Playwright CLI. The README now explains why the two plugins use different tools.

## [0.2.0] - 2026-08-22

First content release. Ports the QA collection from `copilot-collections`,
restructured for Claude Code.

### Added

- **`writing-playwright-e2e-tests`** — acceptance-criteria-to-scenario mapping, Page
  Object conventions, locator priority, anti-flake rules, the bounded debug loop with
  explicit iteration limits, and the CI-readiness gate. References cover locators, test
  data and mocking, plus debugging and flake diagnosis.
- **`auditing-accessibility`** — WCAG 2.1 AA audit procedure with four references:
  semantics and structure, keyboard and focus, ARIA patterns, and contrast, reflow and
  RTL.
- **`e2e-engineer` agent** — writes, debugs and de-flakes tests from a plan task or
  acceptance criteria; never modifies application code.
- **`.mcp.json`** with the Playwright MCP and `context7`.

### Changed from the copilot-collections originals

- **`internal-prompts/tsh-implement-e2e` is folded into the skill's procedure and
  output contract** rather than shipping as a separate routing entry.
- **`tsh-ensuring-accessibility` was reframed as an audit** and split into `SKILL.md`
  plus four references, per this marketplace's progressive-disclosure rule. It still
  carries the implementation patterns — the criteria are the same whether you are
  building or checking — and gained the live-region ordering trap, the DOM-order cause
  of broken tab order, the 1.4.4-versus-1.4.10 distinction, and the note that 44×44
  touch targets are best practice rather than an AA requirement.
- **E2E standards were moved from the agent body into the skill.** Locator priority,
  synchronization, test data isolation and naming were rules embedded in the agent
  definition; they belong where any caller can reach them.
- **The `playwright-cli` skill was not adopted.** This plugin uses the Playwright MCP,
  matching `tsh-product-engineering`. The CLI skill in `copilot-collections` exists to
  produce file artifacts for design verification, which is out of scope here.
- **The human-approval-record precondition was dropped**, as in
  `tsh-platform-engineering`: it validated a field set TSH's plan format here does not
  carry, so it could only fail closed. The narrower boundary replacing it is that the
  agent never modifies application code.
- **Cross-plugin file dependencies were severed.** `tsh-task-analysing` and
  `tsh-technical-context-discovering` references are replaced by an inline
  test-convention discovery section in the skill and the agent's own first step.
  Name-based references to `tsh-core`, which is assumed installed, replace the parts
  a core capability already covers: `e2e-engineer` fetches acceptance criteria from a
  Jira key using `tsh-core`'s Atlassian MCP tools, and an accessibility report written
  for people outside the team goes through `/tsh-core:writing-technical-documents`.
- **Handoffs to `tsh-software-engineer` and `tsh-ui-engineer` were dropped** — a plugin
  agent cannot rely on an agent from another plugin being installed. A discovered
  defect is reported to the caller, which routes the fix.
- **VS Code-specific frontmatter was translated**: `vscode/askQuestions` becomes
  `AskUserQuestion`, the model list becomes a single `model`, and the
  `sequential-thinking` MCP mandate is dropped in favour of extended thinking.
- **Explicit authentication-safety boundaries were added** to the agent, matching the
  rules `feature-verifier` already carries in `tsh-product-engineering`.

### Out of scope, deliberately

Design-implementation verification — `tsh-ui-verifying`, `tsh-ui-reviewer`,
`tsh-ui-capture-worker`, `/tsh-review-ui` — is a separate area whose outcome is design
fidelity rather than software quality. It belongs with product engineering and was not
migrated here. `tsh-reviewing-frontend` (frontend code review) and
`tsh-task-quality-reviewing` (ticket and acceptance-criteria quality) are likewise not
QA and route elsewhere.
