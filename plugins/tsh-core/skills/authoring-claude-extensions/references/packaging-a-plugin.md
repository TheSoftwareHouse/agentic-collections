# Packaging a plugin

Use this reference when bundling extensions for another repository or a marketplace. A
plugin is the **packaging layer**, not a fifth kind of extension: it wraps skills,
subagents and hooks into one installable, versioned unit — and, through an
`.mcp.json` at the plugin root, existing MCP servers, which this reference does not
cover beyond naming that file.

The trigger is distribution, never capability. Build the thing, use it in one place,
package it once it has survived contact with real work.

## 1. Layout, and the trap in it

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json        # the manifest — the ONLY file that goes in here
├── skills/
│   └── <skill-name>/SKILL.md
├── agents/
│   └── <agent-name>.md
├── hooks/
│   └── hooks.json
└── README.md
```

**`<plugin-root>/.claude-plugin/plugin.json` is the only manifest path Claude Code
reads.** A `plugin.json` at the plugin root is ignored — silently, with no load error.

The inverse is the more common bug and fails the same way: **`skills/`, `agents/` and
`hooks/` live at the plugin root, never inside `.claude-plugin/`.** Put them there and
the plugin loads, reports zero components, and looks entirely correct in review.

The manifest is technically optional — without one, Claude Code derives the name from
the directory and auto-discovers components at their defaults. Ship one anyway:
`claude plugin validate` fails without it, and it keeps the plugin self-describing if
it is ever vendored elsewhere.

## 2. Namespacing

Plugin components are namespaced by the plugin name, so they never collide with a
project's own:

- Skills: `/<plugin>:<skill-name>`
- Agents: `@<plugin>:<agent-name>`

**Do not repeat the plugin name inside a component name.** `a11y-auditor` in plugin
`acme-testing` becomes `@acme-testing:a11y-auditor`; naming the file
`acme-a11y-auditor` produces `@acme-testing:acme-a11y-auditor`.

## 3. Paths inside a plugin

| Variable | Resolves to |
| --- | --- |
| `${CLAUDE_PLUGIN_ROOT}` | The plugin's installed directory |
| `${CLAUDE_SKILL_DIR}` | The current skill's directory |
| `${CLAUDE_PLUGIN_DATA}` | The plugin's persistent data directory |
| `${CLAUDE_PROJECT_DIR}` | The project root |

Claude Code substitutes the first two in plugin skill markdown. Use relative
`./references/<topic>.md` within a skill, and `${CLAUDE_PLUGIN_ROOT}/…` for files
shared between skills of the same plugin.

**Never path from one plugin into another.** The other plugin may not be installed, and
the failure is a silent dead link rather than an error. Knowledge two plugins both need
has to be co-located — duplicate the file, and keep the copies deliberately divergent
so nobody mistakes them for one thing.

## 4. What a plugin cannot ship

Plugin-shipped **subagents** may not declare `hooks`, `mcpServers` or
`permissionMode`. Claude Code ignores those fields there, because a plugin arrives from
a marketplace and those fields would let an install deliver arbitrary configuration.

A `CLAUDE.md` inside a plugin is **not loaded**. To ship instructions that reach
Claude's context, write a skill. Per-plugin human documentation goes in `README.md`.

## 5. Marketplaces

A marketplace is a repository with `.claude-plugin/marketplace.json` listing its
plugins. Two mechanics decide whether a change reaches anyone:

- **A plugin absent from the catalog is invisible.** The directory alone installs
  nothing.
- **A brand-new plugin does not arrive with `/plugin update`.** Users hold a cached
  copy of the catalog, and a new plugin has no installed version to compare against.
  They need `/plugin marketplace update <marketplace-name>` first — so announce a new
  plugin with that command attached.

## 6. Versioning

Claude Code resolves a version from `plugin.json` first, then the marketplace entry,
then the commit SHA. Because `plugin.json` always wins, do not also put a `version` in
the marketplace entry — it would shadow nothing and mislead the next contributor.

**Users receive an update only when that string changes.** Push without bumping it and
`/plugin update` reports "already at the latest version", with no error to explain why
nothing arrived.

Renames are breaking. A skill or agent name *is* its invocation command, and there is
no deprecation mechanism, so a rename breaks documentation, muscle memory and any
`enabledPlugins` entry at once.

## 7. Verify

```shell
claude --plugin-dir ./my-plugin       # load from the working tree, no install
claude plugin validate ./my-plugin    # the manifest
claude plugin validate .              # the marketplace catalog
```

Expect `✔ Validation passed`; add `--strict` to treat warnings as errors. Then run
`/context` in a session and confirm the components actually appear — validation checks
the manifest, not whether your skills and agents were discovered.

Validation passing while `/context` shows nothing is the signature of §1's directory
trap.

## Sources

Claude Code documentation, verified 2026-08-17:

- [Plugins](https://code.claude.com/docs/en/plugins)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — the complete
  component schemas, manifest structure and CLI commands

Three things above ship on Claude Code's release cadence and will drift: the
**`${CLAUDE_*}` path variables** in §3, the **version-resolution order** in §6, and the
fields a plugin-shipped subagent may not declare in §4. The manifest path in §1 is the
most stable claim here and also the most costly to get wrong, since both failure modes
are silent. Where the documentation disagrees with this reference, **the documentation
is right** — treat a mismatch as a signal to update this file, not as a defect in the
tool.
