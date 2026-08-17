---
paths:
  - "plugins/**/agents/*.md"
  - "templates/agent.md"
---

# Agents in this marketplace

Repo-specific constraints for an agent that ships from here. **The general mechanics —
the frontmatter field set, `tools`, what loads at startup, skill-versus-subagent —
belong to `/tsh-core:authoring-claude-extensions`.** Invoke it rather than working from
memory; this file is only the local delta.

Creating an agent from scratch? Start with `/contributing-a-plugin-component`. This
rule fires when Claude *reads* an agent file, so it cannot reach you while you are
writing a new one.

## Forbidden frontmatter fields

**Plugin-shipped agents may not declare `hooks`, `mcpServers`, or `permissionMode`.**
Claude Code ignores those fields there, because a plugin installs from a marketplace
and those fields would let an install deliver arbitrary configuration.

If an agent genuinely needs one of them, it cannot ship in a plugin. Narrow its access
with `tools` instead, or leave the constraint to the installing repository.

## Naming

- Kebab-case, **without** a `tsh-` prefix. The plugin already namespaces it:
  `a11y-auditor` → `@tsh-product-testing:a11y-auditor`, never
  `@tsh-product-testing:tsh-a11y-auditor`.
- **The filename must match the frontmatter `name`.** `agents/a11y-auditor.md`
  declares `name: a11y-auditor`.
- Keep the name unique across every plugin here. Only the `name` field identifies an
  agent, so a collision means one of them silently loses.

## Renaming is a `major` bump

The name is the invocation handle and there is no deprecation mechanism. See
`/releasing-a-plugin-change`.
