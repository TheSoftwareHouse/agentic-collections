# Changelog

All notable changes to `tsh-product-management` are documented here. The format
follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the
versions are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.2.0] - 2026-08-21

### Added

- **The plugin ships the business-analysis workflow.** It was a scaffold before
  this release; there is now a complete path from discovery workshop material —
  transcripts, Figma and FigJam, PDFs, an existing backlog — to Jira-ready epics
  and user stories and a per-project delivery roadmap. Start it with
  `/tsh-product-management:analyze-materials <materials>`, or
  `/tsh-product-management:explore-materials <materials>` when the material is too
  ambiguous to commit to a backlog yet.
- **Five human review gates, recorded in a file rather than in the conversation.**
  The intent brief (Gate 0), the extracted breakdown (Gate 1), the quality-review
  dispositions (Gate 1.5), the roadmap proposal (Roadmap Review, 1.75) and the Jira
  push (Gate 2) each need explicit approval, written into
  `specifications/<workshop-name>/.gates.md` **before** the action it unlocks. A
  long session can be summarized; the ledger survives that, and a memory of
  approval does not.
- **A `PreToolUse` hook that denies Jira writes until Gate 2 is approved**, and
  refuses to update an issue whose status is Done, Cancelled or PO APPROVE. It
  ships as `hooks/hooks.json`, so it is active however the workflow is entered —
  including a direct `formatting-jira-issues` invocation that never reaches the
  orchestrator. It costs nothing in sessions that never do BA work because the
  script stands down when no BA artifact is on disk, leaving ordinary Jira use
  elsewhere untouched. Reads are never gated — classification is an anchored read
  allowlist, so listing transitions or reading comments runs unprompted — and a
  tool it cannot classify is held with `ask` rather than waved through.
  The approval is **scoped and expires with the session**: the Gate 2 row names
  its target project key and unlocks writes to that project only, and anything
  archived under `sessions/` is invisible to the guard — a previous workshop's
  approved ledger or stale `🔒` marker cannot hold the gate open, or an issue
  hostage, for the next one. Protected tasks are recognized by parsing
  `jira-tasks.md` task blocks — a `🔒` in the task's `###` heading, or a
  protected `Status` value — rather than requiring the key and the marker to
  share a line, and the worked example now demonstrates the format.
- **Nine skills**: `analyze-materials` and `explore-materials` as user-invoked entry
  points, `orchestrating-business-analysis` running the workflow, and
  `processing-workshop-transcripts`, `analyzing-discovery-context`,
  `extracting-epics-and-stories`, `reviewing-backlog-quality`,
  `planning-delivery-roadmaps` and `formatting-jira-issues` doing the work.
- **Six read-only worker subagents** — `transcript-cleaner`, `discovery-analyst`,
  `backlog-extractor`, `backlog-quality-reviewer`, `roadmap-planner` and
  `jira-formatter` — so document parsing and analysis traffic stay out of the main
  conversation. They hold no write tools and no Atlassian access by construction:
  every file write, every user question and every Jira mutation stays with the
  orchestrator.
- **A systematic quality review** (`reviewing-backlog-quality`) that builds a domain
  model from the task list and runs eleven analysis passes over it — entity
  lifecycle, cross-feature state, bulk idempotency, dashboards, precondition
  guards, third-party boundaries, platform operations, error states, notifications,
  domain research, and a mandatory pre-roadmap delivery-readiness pass — then puts
  each finding through an individual accept/reject at Gate 1.5.
- **A Markdown-only delivery roadmap** (`planning-delivery-roadmaps`) with
  project-scoped stable epic IDs shared by a client-facing outcome-wave view and an
  internal coordination view. It creates no Jira releases or custom fields and
  mutates no status.

### Notes for installers

- **Jira needs the Atlassian MCP server**, which `tsh-core` bundles — install it and
  run `/mcp` once to authenticate. This plugin deliberately does not bundle a second
  copy.
- **Figma is a prerequisite, not a bundled server.** Design analysis is skipped, with
  a report, when no Figma MCP is connected.
- Migrated from the standalone `tsh-claude-collections` repository, restructured to
  this marketplace's conventions: no `tsh-` prefixes on component names, commands
  converted to user-invoked skills, and every skill split into a `SKILL.md` under
  ~150 lines plus `references/`.
