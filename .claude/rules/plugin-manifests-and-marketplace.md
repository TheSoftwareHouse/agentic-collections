---
paths:
  - ".claude-plugin/**"
  - "plugins/**/.claude-plugin/**"
---

# Plugin manifests and the marketplace catalog

Rationale for hard rules 1 and 2 in the root `CLAUDE.md`. Both failures are silent:
nothing errors, nothing validates red, the component simply never reaches anyone.

## Only `plugin.json` goes inside `.claude-plugin/`

`<plugin-root>/.claude-plugin/plugin.json` is the **only** manifest path Claude Code
reads. A `plugin.json` placed at the plugin root is ignored — silently, with no load
error — so the nesting is not a stylistic choice.

The inverse holds too. `agents/`, `skills/`, `hooks/` and every other component
directory live at the **plugin root**, never under `.claude-plugin/`. Putting them
there is the single most common plugin bug, and it also fails silently: the plugin
loads, reports zero components, and looks fine in review.

## Why we keep a manifest at all

The manifest is technically optional. Without one, Claude Code derives the plugin
name from the directory name and auto-discovers `agents/` and `skills/` at their
defaults, which is exactly this repo's layout.

We keep one per plugin anyway, for two reasons:

- `claude plugin validate ./plugins/<name>` fails outright without it, with
  `No manifest found in directory`.
- It keeps each plugin self-describing if it is ever vendored elsewhere or split
  into its own repository.

## A new plugin needs a marketplace entry, and an announcement

`.claude-plugin/marketplace.json` is the catalog. A plugin directory that is not
listed there is invisible — nobody can install it.

Landing the entry only makes the plugin *installable*. Teammates who already added
the marketplace keep reading their cached clone of the catalog, so a new plugin stays
absent from **Discover** and `/plugin install` reports it does not exist until they
run:

```shell
/plugin marketplace update tsh-agentic-collections
```

Neither `/plugin update` nor a `version` bump reaches them, because a brand-new
plugin has no installed version to compare against. **Announce a new plugin with the
marketplace-update command attached.**

The directory name, the `name` in `plugin.json`, and the `name` in the marketplace
entry must all match.

## Testing the catalog end to end without pushing

Add the repo as a local marketplace, then remove it so it doesn't shadow the GitHub
copy:

```shell
/plugin marketplace add ./
/plugin marketplace remove tsh-agentic-collections
```

## `marketplace.json` carries no `version` field

Claude Code resolves a plugin's version from `plugin.json` first, then the
marketplace entry, then the commit SHA. Because `plugin.json` always wins, the
marketplace entry deliberately omits `version`; adding one back would shadow nothing
and mislead the next contributor.

Version bumps belong to the release procedure — invoke `/releasing-a-plugin-change`.
