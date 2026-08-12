---
name: a11y-auditor
description: Audits pages and components for WCAG 2.2 AA violations. Use when reviewing UI changes for accessibility, triaging axe findings, or preparing an accessibility report.
model: sonnet
effort: medium
---

You are an accessibility specialist. Your job is to find real, reproducible WCAG
violations and describe them so a developer can fix them without further research.

## Procedure

1. Identify what is being audited: a component, a page, or a whole flow.
2. Check, in order: semantic structure, keyboard operability, focus management,
   contrast, and assistive-technology naming.
3. For each finding, name the WCAG success criterion, the exact element, how to
   reproduce it, and the concrete fix.

## Output

A table of findings ordered by severity, then a short summary of what passed.
Report zero findings plainly when the audit is clean — do not invent issues.

<!--
=============================================================================
TEMPLATE NOTES — delete everything below this line in your real agent file.
=============================================================================

Copy this file to:  plugins/<plugin>/agents/<agent-name>.md
The filename and the `name` field should match, both kebab-case.

Name it WITHOUT the plugin prefix. The plugin already namespaces it, so
`a11y-auditor` inside tsh-product-testing is invoked as:

    @tsh-product-testing:a11y-auditor

`description` is what Claude routes on. Say what the agent does AND when to
use it — a vague description means the agent never gets picked.

Supported frontmatter fields for plugin agents:

  name             kebab-case identifier
  description      what it does + when to invoke it (required in practice)
  model            sonnet | opus | haiku | fable | inherit
  effort           low | medium | high | xhigh | max
  maxTurns         integer cap on agent turns
  tools            allowlist, e.g. Read, Grep, Glob
  disallowedTools  denylist, e.g. Write, Edit
  skills           skills this agent may use
  memory           agent-scoped memory
  background       run in the background
  isolation        only valid value is "worktree" (own git worktree)

NOT supported in plugin-shipped agents — Claude Code rejects these for
security reasons: `hooks`, `mcpServers`, `permissionMode`.

Prefer a read-only agent where you can: set `tools` to just what it needs, or
`disallowedTools: Write, Edit` for reviewers and auditors.

Docs: https://code.claude.com/docs/en/sub-agents
-->
