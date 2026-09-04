# Changelog

All notable changes to `tsh-product-testing` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-03

### Changed

- **Live-page exploration moved from the bundled Playwright MCP server to the
  [Playwright CLI](https://www.npmjs.com/package/@playwright/cli)** — locator
  confirmation before a test is written, and page-state inspection inside the debug
  loop. The view is the same accessibility tree `getByRole` resolves against, so
  nothing about the standard changes; what improves is that the CLI executes a
  candidate locator string (`playwright-cli click "getByRole(…)"`) against the live
  page before it enters a test, its output stays out of MCP tool context, and both
  TSH plugins now drive the one browser tool — `tsh-product-engineering` made the
  same move in its 0.7.0. The mechanics live in a new `writing-playwright-e2e-tests`
  reference, `playwright-cli-exploration.md`, and the README now names the CLI as a
  prerequisite with the install command. The workflow checks availability
  (`playwright-cli --version`, `npx` fallback) before its first exploration — the
  same preflight `tsh-product-engineering` runs — and, when the CLI is missing,
  asks the user whether to install it for them or wait; a subagent, which cannot
  ask, reports the missing prerequisite. Neither guesses locators blind, and
  nothing installs without the user choosing it.
- **The language version under test is a pinned input.** A multilingual app renders
  different accessible names per locale, so `getByRole` locators written against the
  wrong language test nothing users get. The skill now requires pinning the language
  before any locator is read off a snapshot — from the plan, the Playwright config
  or existing tests, and by asking the user when nothing settles it — and
  exploration confirms the rendered language matches before any locator is
  confirmed. Imported from the wrong-language capture lesson in
  `tsh-product-engineering`'s benchmark rounds.
- **Locator confirmation is a MUST, not a procedure step, and the report proves
  it.** A pilot run showed the failure mode: with good sources at hand (translation
  files, component code) the model rationalized skipping live exploration entirely
  and derived locators from source — which happened to work, and would not have next
  time. Confirming locators against the running app now sits in the non-negotiable
  rules table (self-scoped: a test that drives no browser has no locators, so pure
  API scenarios are exempt), and the output contract carries two audit fields —
  `Locators confirmed against the running app` and `Language pinned by` — so a
  skipped confirmation is visible in the report instead of buried in a transcript.
  A second pilot closed three letter-of-the-rule dodges the first hardening left
  open: confirmation must use the CLI's own commands after loading the exploration
  reference (an improvised browser script skips the preflight and leaves scratch
  files in the repository), a silent language choice disclosed in the report does
  not count as asking, and the two audit fields are verbatim contract lines that
  prose cannot replace.

### Removed

- **The Playwright MCP server from `.mcp.json`** — with exploration on the CLI it has
  no consumer left; `context7` stays. No invocation handle breaks: plugin-MCP tool
  names were never safe to reference in `tools:` lists or hook matchers (the
  surviving namespace depends on plugin load order), so nothing configured can depend
  on them. A repository that used the bundled server for its own purposes should
  declare `@playwright/mcp` in its own project `.mcp.json`.

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
