---
paths:
  - "plugins/**/agents/*.md"
  - "templates/agent.md"
---

# Authoring an agent

An agent is delegated work in its own context, with its own system prompt and its own
tool restrictions. Use one when the work is a self-contained job whose intermediate
reasoning should stay out of the main conversation: audits, reviews, focused
investigations. Start from `templates/agent.md`.

Rule of thumb against a skill: **if it needs to hand back a report, make it an
agent. If it needs to change the way the current conversation proceeds, make it a
skill.**

## Forbidden frontmatter fields

**Plugin agents may not declare `hooks`, `mcpServers`, or `permissionMode`.** Claude
Code rejects those fields in plugin-shipped agents for security reasons. A plugin is
installed from a marketplace, so an agent that could attach hooks or spawn MCP
servers would be arbitrary code arriving with a `/plugin install`.

If an agent needs narrower tool access, use the `tools` field. If a constraint must
hold regardless of what the model decides, it cannot ship in a plugin agent — that is
a hook the installing repository configures itself.

## Naming

Kebab-case, **without** a `tsh-` prefix — the plugin already namespaces it.

- Correct: `a11y-auditor` → `@tsh-product-testing:a11y-auditor`
- Wrong: `tsh-a11y-auditor` → `@tsh-product-testing:tsh-a11y-auditor`

**The filename must match the frontmatter `name`.** `agents/a11y-auditor.md` declares
`name: a11y-auditor`.

## Renaming an agent is a `major` bump

There is no deprecation mechanism — the name is the invocation handle, so a rename
breaks docs, muscle memory and `enabledPlugins` entries at once. See
`/releasing-a-plugin-change`.
