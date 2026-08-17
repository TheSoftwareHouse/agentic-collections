# Authoring a subagent

Use this reference when writing or changing a custom subagent. A subagent is a worker
with its **own context window**, its own system prompt and its own tool access. It does
the work out of sight and returns only a result.

Reach for one when the intermediate reasoning is noise: broad searches, audits,
independent reviews, parallel investigations. If the conversation needs to see the
work, or the work needs what the conversation already knows, write a skill instead.

## 1. Where subagents live, and which one wins

A subagent is a Markdown file with YAML frontmatter. Priority, highest first:

| Location | Scope |
| --- | --- |
| Managed settings | Organization-wide |
| `--agents` CLI flag | This session |
| `.claude/agents/` | This project — commit it to share with the team |
| `~/.claude/agents/` | All your projects |
| `<plugin>/agents/` | Wherever the plugin is enabled |

Both `.claude/agents/` and `~/.claude/agents/` are scanned recursively. Subdirectories
organise files; they do not affect identity. **Only the `name` field identifies an
agent**, so names must be unique across the whole tree — two files with the same name
means one silently loses.

## 2. Frontmatter

Only `name` and `description` are required.

```yaml
---
name: a11y-auditor
description: Audits a page or component for WCAG 2.2 AA violations and reports findings by severity. Use after UI changes, or when asked to check accessibility.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are an accessibility auditor. …
```

| Field | Notes |
| --- | --- |
| `name` | Lowercase and hyphens. No `:` — that is reserved for plugin namespacing. Must match how you refer to the agent. |
| `description` | **When Claude should delegate to it.** This is the routing surface; the body is not consulted for the decision. |
| `tools` | Allow-list. Omit to inherit everything available, which is rarely what you want for a read-only worker. |
| `disallowedTools` | Subtracted from whatever was inherited or listed. |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit`. Defaults to `inherit`. |
| `skills` | Skills preloaded **in full** at startup — not on demand as in a normal session. |
| `memory` | `user`, `project` or `local` to give the agent persistent memory of its own. |
| `effort`, `maxTurns`, `background`, `isolation`, `color` | Execution controls; `isolation: worktree` runs it in a temporary git worktree. |
| `initialPrompt` | Auto-submitted as the first turn when the agent runs as the main session agent. |

The body of the file is the agent's **system prompt**. Write it as instructions to the
agent itself, not as documentation about it.

## 3. Restrict tools deliberately

`tools` is the difference between a reviewer and something that can rewrite the
repository. An agent that only needs to read should say so:

```yaml
tools: Read, Grep, Glob
```

Omitting `tools` inherits everything, including write and execute. That is a choice,
and it should be a deliberate one.

## 4. What the subagent actually starts with

A non-fork subagent gets a fresh context containing:

- its own system prompt — **not** the full Claude Code system prompt
- the delegation prompt the caller wrote
- every level of the `CLAUDE.md` hierarchy
- a git status snapshot from the parent session's start
- the full content of any skill named in `skills:`

It does **not** get the conversation history, the caller's invoked skills, or the main
conversation's auto memory. Two practical consequences:

- **State the task completely in the delegation prompt.** The agent cannot see what
  was discussed.
- **The result is all that comes back.** Say what shape the result should take, or you
  will get prose where you wanted a list.

The built-in `Explore` and `Plan` agents skip `CLAUDE.md` and git status to stay small.

## 5. Plugin-shipped agents cannot use three fields

**`hooks`, `mcpServers` and `permissionMode` are ignored in a plugin-shipped
subagent.** A plugin arrives from a marketplace, so an agent that could attach hooks or
spawn MCP servers would be arbitrary configuration delivered by an install.

If an agent genuinely needs one of them, it cannot ship in a plugin. Copy it to
`.claude/agents/` or `~/.claude/agents/`, where the fields work because the user wrote
them.

## 6. Subagent or agent team?

A subagent reports back to the caller and nothing else. **Agent teams** are independent
sessions that message each other, for work needing discussion between peers rather than
a single delegated result. They are experimental and off by default; start with a
subagent and escalate only when the workers genuinely need to talk to each other.

## 7. Verify

1. Run `/context` and confirm the agent appears under **Custom Agents**.
2. Invoke it explicitly and check the result's *shape*, not just its content.
3. Then describe a task matching its `description` **without naming it**, and confirm
   it gets delegated. If not, the `description` is wrong — it is the only thing routing
   sees.
