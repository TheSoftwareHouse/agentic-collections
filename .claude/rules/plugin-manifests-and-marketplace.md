---
paths:
  - ".claude-plugin/**"
  - "plugins/**/.claude-plugin/**"
  - "plugins/**/.mcp.json"
---

# Plugin manifests and the marketplace catalog

Rationale for hard rules 1 and 2 in the root `CLAUDE.md`, plus where a bundled MCP
server belongs. Every failure here is silent: nothing errors, nothing validates red,
the component simply never reaches anyone.

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

## Where an MCP server goes

A plugin bundles MCP servers from an `.mcp.json` at its **plugin root** — never under
`.claude-plugin/`, which holds `plugin.json` and nothing else. The same silent failure
applies: the plugin loads, the server simply isn't there.

Placement follows the routing predicate, with one substitution — count **disciplines**
instead of asking whose job it is:

| The server is driven by | It goes in |
| :-- | :-- |
| Three or more disciplines | `plugins/tsh-core/.mcp.json` — read `core-plugin-admission.md` first |
| One agent, one skill, one discipline | that plugin's own `.mcp.json` |

Atlassian is the first case: engineering, product management and testing all read
Jira. Playwright is the second: it exists to let `ui-engineer` look at a rendered
page, and it stays in `tsh-product-engineering`.

**Two facts that decide the boundary, both undocumented in the plugin docs:**

- **Plugin-provided servers deduplicate by *endpoint*, not by name.** Claude Code's
  precedence is Local → Project → User → plugin-provided → claude.ai connectors, and
  the three scopes match by name while plugins and connectors match by URL or command.
  So two plugins declaring the same Atlassian URL connect **once** — duplication does
  not double anyone's tool budget. It costs N files to keep in sync and N version
  bumps per change.
- **The surviving definition decides the tool namespace.** A plugin server's tools are
  called `mcp__plugin_<plugin-name>_<server-name>__<tool>`, and the winner tracks
  plugin **load order** — verified by swapping two `--plugin-dir` flags, which flips
  which plugin name survives. Nobody controls install order, so treat it as
  arbitrary. So **never name a shared
  server's tools in a `tools:` field, an `allowed-tools:` list, or a hook matcher** —
  the reference breaks silently depending on which plugins the teammate installed.
  One home per server is what makes those names safe to write down.

**Bundle a server that needs per-user OAuth; don't bundle one that needs a secret.**
A remote server the teammate authenticates once through `/mcp` is fine — that is the
Atlassian case, and the credential never touches the repo. A server needing a token in
`headers` is not: a static `headers.Authorization` also disables Claude Code's OAuth
fallback, so it fails outright for anyone who hasn't set the value. Leave those to the
consuming project, which is why Figma MCP is a `ui-engineer` prerequisite rather than
a bundled server.

An `.mcp.json` change is a `plugins/` change, so hard rule 3 applies in full: version
bump and `CHANGELOG.md` entry in the same commit.

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
