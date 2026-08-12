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
