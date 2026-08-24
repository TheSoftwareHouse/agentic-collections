# Changelog

All notable changes to `tsh-core` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.8.1] - 2026-08-24

### Fixed

- **`managing-git-worktrees` told Claude to hold the new worktree's path in a shell
  variable named `path`, which breaks every command that follows it on macOS.** In
  zsh — the default shell there — `path` is an array tied to the `PATH` environment
  variable, so `path='/some/dir'` replaces `PATH` with that single entry and the next
  step fails with `command not found: git`. The create flow now uses
  `worktree_path` throughout, and step 5's existing zsh warning gained a second
  bullet naming `path`, `cdpath`, `fpath` and `manpath` as reserved. This was hit for
  real: the failure presents as a broken environment or a denied sandbox rather than
  a variable-naming bug, so it cost a diagnostic detour before anyone suspected the
  reference. `references/removing-a-worktree.md` was checked and never held a path in
  a variable.

## [0.8.0] - 2026-08-20

### Added

- **The plugin now bundles one MCP server: Atlassian's official
  [Rovo MCP server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)**
  (`.mcp.json`), so Jira work items and Confluence pages are readable and writable
  from any session — no per-project MCP setup, and no pasting a ticket into the
  conversation to plan against it. **One step per machine:** run `/mcp`, pick
  `atlassian`, finish the browser OAuth login; every call then runs under that
  person's own Atlassian account and grants nothing they could not already open in
  Jira. Atlassian Cloud only. It shows in `/mcp` as plugin-provided and can be
  disabled there per project.
- **Why here and not in a discipline plugin.** It fails both routing questions —
  Jira does not change with the language a repo is written in, nor with the reader's
  job — and it wraps a named tool rather than a TSH opinion, which is the test this
  plugin's bar is built around. The three disciplines that invoke it in a normal
  month: **product engineering, product management, product testing**. Placing it in
  one discipline plugin would mean re-declaring the same endpoint in each of the
  others; plugin servers are deduplicated by endpoint, so that connects once but
  leaves the `mcp__plugin_<plugin>_atlassian__*` namespace decided by whichever
  definition wins — and that tracks plugin load order, which nobody controls.
- **Routing footprint: 4,076 characters, unchanged by this release** — 3,686 of them
  actually preloaded, since `init` sets `disable-model-invocation: true`. An MCP
  server puts nothing in the skill listing, so it spends no routing budget at all.
  Its cost is MCP tool names, and Claude Code defers tool schemas until a tool is
  used. The `Scope` section of the README now states that the admission bar covers
  every component class, not only skills.
- **Bitbucket is deliberately not included, and that is not a bug.** The same server
  exposes Bitbucket Cloud and Jira Service Management only under API-token
  authentication — never OAuth — which additionally requires an org admin to enable
  API-token auth in Admin Hub → Rovo → Rovo MCP server, the workspace linked to the
  organisation, and a scoped token per person. Bundling that would ship a server that
  fails for most installs, so the README carries the `claude mcp add` command for
  anyone who wants to opt in themselves.

## [0.7.1] - 2026-08-20

### Fixed

- **`authoring-claude-extensions` described skill-frontmatter hooks incorrectly.** The
  registration-scope table said hooks in "Skill or subagent frontmatter" apply "only
  while that skill or subagent is active." That is true of a subagent and wrong of a
  skill: Claude Code registers a skill's hooks when the skill is invoked and keeps
  running them for the rest of the session, later turns included. The two rows are now
  separate. The wrong line mattered because it removed frontmatter hooks from
  consideration for the case they fit best — enforcement that should start when a
  workflow is entered and hold until the session ends, at no cost to sessions that
  never enter it.

### Added

- `hooks` and `paths` documented in the skill frontmatter table in
  `references/authoring-a-skill.md`. Neither was listed, which is why nothing in this
  marketplace uses either. The `hooks` row also records the asymmetry with `CLAUDE.md`'s
  hard rule on agents: a plugin-shipped **agent** may not declare `hooks`, but a
  plugin-shipped **skill** may.
- `once: true` explained in `references/authoring-a-hook.md` — it limits a handler to
  one run per session and is honoured only in skill frontmatter.

## [0.7.0] - 2026-08-17

### Added

- `init` — the one command that takes a repository from any starting state to a
  complete, wired set of context primitives. Run `/tsh-core:init` and it audits what
  already loads, creates or repairs root and nested `CLAUDE.md`, path-scoped rules
  and the decision-record archive with its index, and leaves a maintenance section
  in root `CLAUDE.md` telling every future session to invoke
  `managing-claude-context` when the project changes and to propose
  `managing-decision-records` when a decision is made. It is safe to re-run: the
  second pass converges to repair, never a rewrite.
- It is a **thin orchestrator**, not a third opinion. Every rule about the artifacts
  stays with the owning skill — `managing-claude-context` for the memory layer,
  `managing-decision-records` for record format and lifecycle — and init loads those
  skills rather than restating them, so there is exactly one copy of each rule to
  keep true. Its only original content is the sequence and one reference: the
  canonical maintenance block, phrased conditionally ("with the `tsh-core` plugin
  installed, invoke …; without it, do X by hand") because `tsh-core` installs at
  user scope and the generated `CLAUDE.md` is read by teammates who never installed
  it.
- `init` is the plugin's first **user-invoked-only** skill
  (`disable-model-invocation: true`). That is what makes the overlap with
  `managing-claude-context` safe: setup requests phrased in prose still route there,
  and init's description is never preloaded — the plugin's routing footprint is
  **unchanged at 3,647 characters** across the five model-invocable skills.
  Admission evidence: it wraps the same tool `managing-claude-context` does — Claude
  Code's memory subsystem — and every discipline initializes projects; product
  engineering, platform engineering and product testing would invoke it in a normal
  month.
- The naming rule gains one documented exception for user-invoked entry points: a
  skill that is a command rather than a routing surface may take a short imperative
  name (`init`). Kebab-case, no prefix, no version and rename-is-major all still
  apply, and a model-invocable skill never qualifies.

## [0.6.1] - 2026-08-17

### Changed

- **Every reference in `authoring-claude-extensions` and `managing-claude-context` now
  cites its upstream Claude Code documentation**, with a verification date and a note
  naming which of its own claims are version-sensitive. These are the only two skills
  here describing a tool that ships on its own release cadence — the 1,536-character
  description limit, the hook event table, the 1,000-pattern brace budget — so they are
  snapshots, and they now say so. Where the documentation disagrees, it wins.
- Both skills state in *Applicability and Precedence* that Claude Code's documentation
  outranks them. Neither `SKILL.md` carries a source list: a `SKILL.md` is paid on every
  invocation while a reference is paid only when read, and a link belongs next to the
  claim it supports.
- Corrected an attribution in `authoring-a-skill.md`, which listed the ~150-line split
  threshold among the figures sourced from Claude Code. It is a TSH convention and does
  not change when Claude Code does.

## [0.6.0] - 2026-08-17

### Added

- `authoring-claude-extensions`, which decides **which** Claude Code extension a need
  calls for — skill, subagent, hook or plugin — and then writes it. It covers those
  four and nothing else; MCP, agent teams, code intelligence and artifacts are out of
  scope.
- Five references: the primitive-choosing predicate, and one each for skills,
  subagents, hooks and plugin packaging.
- The routing table is keyed on **what just happened to you**, not on the artifact you
  already have in mind. Routing on the artifact is how you end up writing a perfectly
  correct rule for a job only a skill can do.

### Changed

- **`managing-claude-context` narrowed to the memory layer** — `CLAUDE.md` root and
  nested, `.claude/rules/`, and the decision index. Building a skill, subagent, hook or
  plugin now hands off to `authoring-claude-extensions`. Both skills state the boundary
  in their own `SKILL.md`, because two routers with adjacent descriptions is a coin
  flip and the loser is silently never invoked.
- **The layer predicate now asks *when* an instruction is needed, not only what it is
  about.** It previously asked only whether an instruction applied to files matching a
  pattern — a question about scope, which authoring guidance passes. So guidance on how
  to *write* a file routed to a path-scoped rule, and a rule fires when Claude **reads**
  a matching file. The result was guidance that could never load at the moment it was
  needed, with a symptom nobody traces back to the rule: the convention is honoured on
  edits and ignored on creation.
- The rules-versus-skills comparison gained **Trigger** and **Survives `/compact`**
  rows. Its old summary — "the dividing line is length and shape, not topic" — was
  incomplete: timing is the axis that decides, and a rule cannot reach creation time at
  any length.
- `choosing-the-layer.md` names the three peer primitives it routes to (skill, hook,
  subagent) instead of implying memory files are the whole space. Subagents previously
  appeared nowhere in the skill.
- `writing-path-scoped-rules.md` now requires expanding every `paths:` glob against the
  working tree before declaring a rule finished, and reads a zero-match result as a
  diagnosis rather than a typo: either the pattern is wrong, or the files do not exist
  yet because the guidance is creation-time and belongs in a skill.

## [0.5.0] - 2026-08-13

### Added

- `managing-decision-records`, which owns what a decision record *is*: a
  four-section format, the status vocabulary, numbering, superseding, and keeping
  the index in step. 0.4.0 mandated the index and the status column, then left the
  record body undefined — a gap that showed up immediately, because a status column
  nothing explains is a column every reader interprets differently.
- Three references: the format section by section with a worked example, the status
  lifecycle including the full supersede procedure, and the threshold test for
  whether something is a decision at all. That last one exists because the most
  common mistake is recording a *convention* — conventions apply on every file you
  touch and belong where they load automatically, while a decision applies when you
  are about to contradict it.
- `Alternatives` is a required section, not an optional one. It is the part that
  answers the person proposing the rejected option eighteen months later, which is
  the reason the artifact exists at all. A record without it reads as though no
  alternatives were considered, which is almost never true.

### Changed

- **Only `Accepted` records bind.** Every other status — `Proposed`, `Rejected`,
  `Superseded`, `Deprecated` — is history: readable to answer "was this considered
  before?", never applicable as a current constraint, and a `Superseded` record is
  never read without its successor. The alternative rule, "read only `Accepted`",
  was rejected because it would destroy what the rejected and superseded records
  exist for. The distinction is between reading a record and obeying it.
- `managing-claude-context` now **writes that rule into the artifacts it
  generates** — the `CLAUDE.md` pointer sentence and a note above the index table.
  This is the substance of the change rather than a detail of it: that skill runs at
  setup and audit, so a rule living only inside it would govern nothing else. The
  generated sentences are what carry the filter into sessions it never runs in.
- The index and the record can now disagree, so a precedence rule was needed: **the
  record is the source of truth for status and tags, and the index mirrors it.** An
  index row reading `Accepted` above a record reading `Superseded` is the most
  dangerous state this layer produces, because the filter reads the row and admits a
  reversed decision as binding. Audits check both directions and correct the row.
- The *name-the-tool* admission test now has **two** named exceptions rather than
  one, and the list is explicitly closed. `managing-decision-records` wraps no tool
  and is TSH opinion about document structure, which the rule otherwise routes to a
  discipline plugin. It is admitted because `managing-claude-context` — which passes
  the test outright — already mandates the index and the status vocabulary, and
  splitting one artifact system across two install units would leave a `tsh-core`
  installer told to keep an index with no guidance on what a record is. It is named
  as the **last** artifact-convention skill core admits; a third exception would
  make this a category, which is the failure the test was written to prevent. The
  amendment is recorded in `CLAUDE.md` and in this plugin's README rather than left
  implicit, because it reverses a rule those files previously stated.
- Decision records are now split three ways, and the verbs carry the routing:
  `managing-claude-context` owns the index and wiring, `managing-decision-records`
  owns format and lifecycle, `writing-technical-documents` owns the prose. Two
  skills under a `writing-` verb both claiming ADRs would have been a routing coin
  flip, which is why this one is `managing-`.
- Routing footprint: **2,245 to 2,937 characters** across four skills. The new entry
  is 692 of that, with `description` and `when_to_use` at 667 against the 1,536
  per-skill cap. It is the smallest entry in the plugin, because its description
  leads on format and lifecycle and deliberately avoids the words
  `writing-technical-documents` already claims.
- No skill sets or changes a record's status. Marking one `Accepted` asserts what a
  team agreed; inferring it from the code records an agreement that never happened,
  and the record then becomes the evidence for it.

## [0.4.0] - 2026-08-13

### Added

- `managing-claude-context`, which sets up and maintains the project-context files
  Claude Code loads: root and nested `CLAUDE.md`, path-scoped rules in
  `.claude/rules/`, and a decision-record index. It exists because the failure it
  prevents is expensive and invisible — a `CLAUDE.md` stating a build command that
  no longer works is worse than no file at all, since the model follows it
  confidently and the reader stops checking.
- A four-layer model the skill applies to the repositories it touches: orientation
  in a thin root `CLAUDE.md`, conventions in `.claude/rules/` scoped with `paths:`,
  locality in nested `CLAUDE.md` files owned by the directory's team, and decisions
  behind a `docs/decisions/README.md` index. Each layer stays thin and points
  downward, which is the same progressive-disclosure discipline this repo already
  applies to its own skills, turned outward.
- Explicit monorepo guidance, because the choice between a nested `CLAUDE.md` and a
  path-scoped rule is decided by **ownership** rather than file count: a rule
  maintained centrally belongs in `.claude/rules/` however many directories it
  touches, and a convention a package team owns belongs beside their code where
  their reviewers see it change. The split trigger is named too — a root file
  growing per-package sections has already outgrown its layer, well before it
  reaches 200 lines.
- Seven references loaded on demand: choosing the layer, writing `CLAUDE.md`,
  writing path-scoped rules, monorepos and scale, indexing decision records,
  bootstrapping a repository, and auditing for drift. The bootstrap and audit halves
  are separate references behind one branching first step, because "does context
  already exist here?" is a question the procedure answers, not a routing decision
  worth a second skill and a second near-identical description.
- Migration guidance from GitHub Copilot and Cursor, since the mapping is close to
  one-to-one — `copilot-instructions.md` to `CLAUDE.md`, and `*.instructions.md`
  with `applyTo:` to `.claude/rules/*.md` with `paths:`. The one asymmetry is called
  out: Copilot can apply an instruction file by semantic match on its description,
  which `paths` does not do, so such an instruction has to become a skill.

### Changed

- The *name-the-tool* admission test is **not** gaining a second exception. This
  skill wraps Claude Code's own memory subsystem, whose mechanics dictate the
  procedure rather than TSH preference: the documented precedence order, the
  200-line adherence target, the 1,536-character routing cap, the 1,000-pattern
  brace-expansion budget, and path-scoped rules that are not re-injected after
  `/compact`. `writing-technical-documents` remains the only named exception.
- One part of the skill is convention rather than mechanics, and is disclosed rather
  than blurred: `docs/decisions/` as a location, and the four index columns, are a
  TSH default a repository may override. The wiring is the non-negotiable part —
  the index must be referenced from `CLAUDE.md` in backticks, because written bare
  with a leading `@` it becomes an import and loads the whole index at launch, which
  is the opposite of what the layer is for.
- Routing footprint, disclosed per the admission bar: **1,492 to 2,245 characters**
  across three skills, measured as `name` plus `description` plus `when_to_use`. The
  new entry is 753 of that, with `description` and `when_to_use` at 730 against the
  1,536 per-skill cap. The three disciplines that would invoke it in a normal month
  are product engineering, platform engineering, and product testing.
- `writing-technical-documents` keeps sole ownership of decision-record prose. The
  new skill writes index rows and wiring only, and hands off the record body — the
  handoff its own Applicability section already anticipated for artifacts whose
  structure another skill defines. Record status stays a human call, because
  inferring `Accepted` from the code eventually records agreement that never
  happened.

## [0.3.0] - 2026-08-12

### Added

- `writing-technical-documents`, the house writing standard for any technical
  document a TSH project produces — README, CHANGELOG, `/docs` page, runbook, ADR,
  RFC, PR description, release note, migration guide, ticket, user story, bug
  report, test plan. It leads with the conclusion, verifies every path, command and
  version against the source, and cuts what does not change the reader's decision.
  The craft rules come from *Writing for Busy Readers* by Todd Rogers and Jessica
  Lasky-Fink, restated as checkable MUST/NEVER rules with a mandatory revision pass,
  because a model follows a predicate it can evaluate and skims a principle.
- Five references loaded on demand: the mechanical revision pass, plus one per
  artifact class — repository documentation, change records, decision records and
  work items. Each covers only how the craft rules land on that artifact: who reads
  it, what to front-load, what typically bloats it.

### Changed

- The skill governs prose craft and **never** an artifact's structure. It will not
  say what sections a user story or an ADR needs; that belongs to the discipline
  skill owning the artifact. Commit subject lines and PR titles are outside its
  scope entirely — the repository's commit convention owns those.
- `tsh-core`'s admission bar drops its six-skill hard cap. A count never measured
  the actual cost: Claude Code preloads every installed skill's name and
  description to route on, so three terse skills can cost less than one verbose
  one. A PR adding a skill here now reports the plugin's routing footprint before
  and after instead — a disclosure, not a ceiling.
- The *name-the-tool* admission test gains one named exception, for this skill
  only. It is named rather than generalised into an "output standards" category:
  an exception you can point at is auditable, a category is a hole.

## [0.2.0] - 2026-08-12

### Added

- `managing-git-worktrees` accepts a base branch, so a worktree no longer has to
  start from `main`. Any branch that exists on `origin` is a legal base, feature
  branches included — useful for spinning several experimental variants off one
  feature branch.
- Both create confirmations now name the base as `origin/<base_branch>` alongside
  the resolved commit, and disclose when the base was detected rather than named by
  the user. A bare commit SHA gave no way to notice the wrong trunk before the
  worktree existed.

### Changed

- Repositories whose trunk is `master`, `develop`, or anything other than `main`
  are supported instead of refused. When no base is named, origin's default branch
  is read from the remote with `git ls-remote --symref origin HEAD`.
- Base resolution never guesses. Local state is not consulted —
  `refs/remotes/origin/HEAD` can be stale and `init.defaultBranch` describes the
  machine, not the remote — and a base that cannot be resolved stops the workflow
  and asks rather than falling back to `main`.
- Tags, commit SHAs, local-only branches, and other remotes' branches are rejected
  as bases by the same `git ls-remote --exit-code --heads origin` check that
  validates the branch, and are listed as future extensions rather than silently
  accepted.

### Fixed

- The base fetch used a refspec-less `git fetch origin main`, which only guarantees
  `FETCH_HEAD`. Under a non-default fetch refspec or a single-branch clone, the
  following existence check could read a **stale** `refs/remotes/origin/main` while
  the skill reported the base as freshly fetched. The fetch now uses an explicit
  `+refs/heads/<base>:refs/remotes/origin/<base>` refspec.

## [0.1.0] - 2026-08-12

### Added

- Initial release: the `managing-git-worktrees` skill, covering worktree creation
  from a freshly fetched base, read-only listing, and removal of one precisely
  identified target — each with explicit confirmation and post-mutation
  verification.
