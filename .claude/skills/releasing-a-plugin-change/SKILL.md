---
name: releasing-a-plugin-change
description: Ship a change to a plugin in this marketplace — choose the version bump, write the CHANGELOG entry, and announce it. Use when releasing, shipping or publishing a plugin change, bumping a plugin version, adding a changelog entry, or when asked how teammates get an update to a tsh-* plugin.
---

# Releasing a plugin change

**There is no release step to separate from merging.** The marketplace serves
whatever is on `main`, so merging *is* releasing. Every step below lands in the
**same commit** as the change it describes.

The failure this skill prevents is a change nobody receives: push without bumping
`version` and `/plugin update` reports "already at the latest version", with no error
to explain why nothing arrived.

## When it does not apply

Changes outside `plugins/` — this file, `README.md`, `.claude/rules/`,
`.claude-plugin/marketplace.json` on its own, `templates/`, `website/`, `spec/` and
`specifications/` — ship nothing to anyone and need no bump and no
changelog entry. A `README.md`, `CLAUDE.md`, `LICENSE` or `marketplace.json` edit can
still stale a website page that lists it: run `npm run docs:check` from `website/`.

## Procedure

### 1. Identify which plugins changed

One bump per plugin touched. A commit that edits two plugins bumps both, each with
its own changelog entry. Never bump a plugin you did not change.

### 2. Choose the bump level

| Bump | When |
| :-- | :-- |
| `patch` | Wording, clarifications, a fix — no change to what the plugin can do |
| `minor` | A new skill or agent, or an existing one gains a capability |
| `major` | A skill or agent is renamed or removed, or a non-negotiable rule reverses in a way an existing workflow could depend on |

**Renames are `major`.** There is no deprecation mechanism: the name is the
invocation command, so a rename breaks docs, muscle memory and `enabledPlugins`
entries at once.

When a change is arguably `patch` or `minor`, ask what an installer would notice. If
they could invoke something they could not invoke before, it is `minor`.

### 3. Bump `version` in `plugin.json` — that file only

Edit `plugins/<name>/.claude-plugin/plugin.json`.

Claude Code resolves a plugin's version from `plugin.json` first, then the
marketplace entry, then the commit SHA. Because `plugin.json` always wins,
`.claude-plugin/marketplace.json` deliberately carries no `version` field — do not
add one back.

### 4. Add a `CHANGELOG.md` entry to that plugin

`plugins/<name>/CHANGELOG.md`, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), newest version first:

```markdown
## [0.6.0] - YYYY-MM-DD

### Added

- What an installer can now do that they could not before.

### Changed

- What behaves differently, and why the old behaviour was wrong.
```

Two conventions this repo holds:

- **No `[Unreleased]` section**, for the same reason there is no release step —
  nothing sits unreleased. An entry parked under `[Unreleased]` is false the moment
  it is pushed.
- **Create a plugin's `CHANGELOG.md` at its first version bump.** Do not scaffold
  empty ones.

`plugins/tsh-core/CHANGELOG.md` is the worked example. Write the entry for the person
deciding whether to update, not as a diff summary — read
`/tsh-core:writing-technical-documents` if the entry is doing real explaining.

### 5. Link the changelog from the plugin's `README.md`

Nothing in Claude Code surfaces release notes. If that plugin's `README.md` does not
already link `CHANGELOG.md`, add the link now.

### 6. Bring the website pages up to date

Pages in `website/docs` hash the plugin files they describe — `plugin.json` included,
so run this after the bump. From `website/`, once `npm ci` has run:

```shell
node scripts/sync-catalog.mjs --check
```

For every page it lists — stale, missing or orphaned — update the page to match its
sources, then stamp it with `npm run docs:stamp -- <page>`. Stamp only a page you
updated: the hash records that someone re-read it. Rerun until the check passes. CI
runs the same check in the `website` job. Page rules: `.claude/rules/website.md`.

### 7. Announce with the right command

Which command teammates need depends on what changed:

| What shipped | What teammates run |
| :-- | :-- |
| A change to an **existing** plugin | `/plugin update` |
| A **brand-new** plugin | `/plugin marketplace update tsh-agentic-collections` first, then install |

A new plugin has no installed version to compare against, so `/plugin update` never
reaches it, and it stays absent from **Discover** until the marketplace cache
refreshes. Attach the changelog link to the announcement.

## Before committing

```text
- [ ] Every plugin touched has a `version` bump in its own `.claude-plugin/plugin.json`
- [ ] No plugin was bumped that this change did not touch
- [ ] Each bumped plugin has a matching `CHANGELOG.md` entry, newest first, no `[Unreleased]`
- [ ] The changelog version string equals the new `version` in `plugin.json`
- [ ] `marketplace.json` gained no `version` field
- [ ] A new plugin also has a `marketplace.json` entry, with matching directory name and `name`
- [ ] `claude plugin validate ./plugins/<name>` passes for each one
- [ ] `node scripts/sync-catalog.mjs --check` passes from `website/`
- [ ] The bump, the changelog entry, the updated website pages and the change are all in the same commit
- [ ] The announcement names the right command — `/plugin update`, or the marketplace update for a new plugin
```
