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

## [0.4.0] - 2026-09-18

### Added

- **A one-command scaffold for a project's context repository**, the new
  user-invoked skill `/tsh-product-management:initializing-project-context`. Run in
  the folder where a project should live, it asks four fixed questions — project name,
  owner (from git config, or "assign later"), where the catalog goes, and which extra
  delivery layers the project needs — then creates a project catalog `<slug>/` holding
  `<slug>-context/`.
- **The generated knowledge base** carries five project workspaces (baseline,
  architecture, product, delivery, quality) and three layer workspaces every project
  has (backend, frontend, design), with `mobile` and `platform` available on request.
  Each has a `README.md` index and a `CLAUDE.md` naming exactly one owner, mirrored in
  the area map. **All decision records live in one folder**, `docs/decisions/`, with a
  `Scope` column instead of a folder per layer: one number sequence, one place to look,
  and the same location and five-status vocabulary as
  `/tsh-core:managing-decision-records`, so that skill works against it unconfigured.
- **A quality gate that runs without git.** `check_links.py` fails on a relative link
  that does not resolve or a filename that is not kebab-case; `check_tables.py` fails
  on a markdown table that would render wrongly — a ragged row, a blank line splitting
  a table, a trailer glued onto one. Both read the git index when there is one and walk
  the tree when there is not.
- **The generated marketplace ships one plugin, `<slug>-shared`, with four skills**,
  each carrying the project slug so two installed projects never present two
  identically named skills: `<slug>-context` reads the knowledge base,
  `<slug>-knowledge` adds or updates a document in the owning workspace with its index
  entry and reviewer, `<slug>-links` repairs references, and `<slug>-space` creates a
  workspace with its owner and area-map row. All four resolve the knowledge base
  through one shared file, so they work from the context repository, from the catalog,
  and from any code repository beside it. Decision records are deliberately left to
  `tsh-core` rather than duplicated.
- **The plugin is live the moment the skill finishes.** The context repository, the
  catalog folder and every selected code repository are registered through the
  `claude plugin` CLI and given a committed settings entry with a portable relative
  marketplace path, so no install command and no trust dialog stand between the setup
  and the first use. The closing report says explicitly that the current session cannot
  see the new plugin and a new one is needed.
- **A `GUIDE.md` in two halves**, one for readers who never open a terminal and one for
  engineers, rendered to `GUIDE.pdf` when pandoc or Chrome is available.

The skill never runs git and never overwrites a file; a second run reports what already
existed. It ships as a 149-line `SKILL.md`, one reference
(`installation-mechanics.md`), four scripts (`probe.py`, `scaffold.py`,
`wire_repos.py`, `render_guide_pdf.py`) and the template tree under `templates/`.

## [0.3.2] - 2026-10-02

### Fixed

- **The Gate 2 hook no longer blocks Confluence.** `hooks.json` matches `confluence`
  so the Atlassian server's mixed tool set reaches the script, and the script then
  applied the Jira Gate 2 policy to every non-read call — so `createConfluencePage`
  in a repository with a pending ledger was denied with "Gate 2 not approved",
  which broke the domain dictionary's own Confluence handoff. Both policies are
  about Jira issues; a tool whose name carries `confluence` and not `jira` now goes
  to the normal permission prompt.
- The hook matcher was case-sensitive while the script was not, so a server keyed
  `Atlassian` bypassed the hook entirely. The matcher now accepts either case.
- Community Atlassian servers name every tool `jira_get_issue`-style; the product
  prefix defeated the verb classification and held every read at the gate, contrary
  to the "reads are never gated" promise. The prefix is stripped before classifying.
- Consistency: `delegating-to-workers.md` said six workers ship (seven do); Import
  Mode saved to `specifications/<project-or-topic>/` where every other path uses
  `<workshop-name>`; the ledger's 1.75 row named `roadmap.md` although the artifact
  reviewed at that gate is `.roadmap-proposal.md`.
- `plugin.json`'s description now names the domain dictionary and the hook, matching
  what the plugin ships.

## [0.3.1] - 2026-09-21

### Changed

- **The Figma MCP server is now bundled by `tsh-core` 0.10.0, so it is no longer
  yours to connect.** The README called it "a prerequisite, not a bundled server"
  because it needed per-user authentication — which is exactly the property that
  makes a server bundleable, as Atlassian already showed. Figma's official remote
  server authenticates through `/mcp`, so it sits in `tsh-core` alongside Atlassian.
  Install `tsh-core`, sign in once per machine, and both work.
- Nothing in the workflow changed. `reading-workshop-materials.md` still says to
  check what the session actually exposes and never to assume a tool name, which
  stays right whether the server comes from `tsh-core` or from a teammate's own
  `claude mcp add`. Design analysis still reports a blocker rather than skipping
  silently when no Figma server answers.

## [0.3.0] - 2026-08-27

### Added

- **A per-product domain dictionary**, produced and maintained end to end by the new
  `managing-domain-dictionaries` skill and its entry point,
  `/tsh-product-management:domain-dictionary`. This is not domain-driven design —
  the dictionary records the client's own vocabulary: canonical terms, their
  source-language surface forms, and where a UI label differs from the identifier —
  through Harvest, Reconcile and Interview modes, checked by eleven review passes
  and reconciled against a live codebase without ever editing it. The skill ships
  as a 103-line `SKILL.md` plus five references: `dictionary-format.md`,
  `elicitation-protocol.md`, `review-passes.md`, `reconciling-with-code.md` and
  `handoff-and-portability.md`.
- **A new read-only agent, `terminology-extractor`** (`Read`, `Grep`, `Glob`). It
  runs the harvest reading pass over supplied material and the identifier sweep
  Reconcile mode diffs against the term table. It writes nothing and asks nobody —
  every dictionary write and every question to the client stays with the skill.
- **A new quality-review pass, Pass K — Terminology Consistency**, added to
  `reviewing-backlog-quality` and its `analysis-passes.md`. It flags a story using a
  banned term, a synonym where a canonical term exists, a term used with two
  meanings and no disambiguating context, or a status value outside the entity's
  state set. It runs in both Lite and Full mode, but only when a dictionary exists
  for the project — with no dictionary, it is skipped and the skip is recorded.
- **The rest of the workflow now knows the dictionary exists.**
  `orchestrating-business-analysis` suggests or consumes a project's dictionary and
  tracks it as a project artifact — no new gate; the five BA gates are unchanged.
  `extracting-epics-and-stories` uses canonical terms and keeps an
  unresolved-terms inbox. `formatting-jira-issues` uses canonical terms in issue
  titles and descriptions. `processing-workshop-transcripts`,
  `analyzing-discovery-context` and the `transcript-cleaner` and
  `discovery-analyst` agents harvest term candidates as they read.

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
