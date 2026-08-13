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
