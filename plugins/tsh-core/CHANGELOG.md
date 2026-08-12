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
