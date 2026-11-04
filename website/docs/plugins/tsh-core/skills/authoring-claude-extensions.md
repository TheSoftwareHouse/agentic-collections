---
title: Authoring Claude Extensions
sidebar_label: authoring-claude-extensions
sidebar_position: 1
description: Decides which Claude Code extension a need calls for (skill, subagent, hook or plugin) and then writes it.
sources:
  - plugins/tsh-core/skills/authoring-claude-extensions/
sources_hash: "06f7dba65654fbeb4a02a9d2fc8cc8d25dee3fc8ed800006f8234ebb6568ecee"
---

# Authoring Claude Extensions

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:authoring-claude-extensions` (also loaded automatically when a request matches its description)  
**Used by:** [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context) (hands skill, subagent, hook and plugin work to it)

Two jobs, in order: decide which primitive the need calls for, then build that primitive correctly. The first job is where the expensive mistakes happen: a correctly written extension in the wrong primitive still fails, and it fails invisibly, because the file looks right in review.

The skill covers skills, subagents, hooks and plugins. If the answer is a memory file (`CLAUDE.md`, a `.claude/rules/` file or a decision record), it stops and hands off to [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context), which owns the memory layer. Writing an MCP server, agent teams, code intelligence and artifacts are not covered; bundling an existing MCP server in a plugin is a one-line `.mcp.json` at the plugin root.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Choosing the primitive** | Routes on what just happened to you rather than on the artifact you have in mind: guidance needed while creating a file is a skill, guidance for editing existing files is a path-scoped rule, a procedure pasted into chat for the third time is a skill, a side task that floods the conversation is a subagent, something that must happen every time is a hook, a second repository needing the setup is a plugin |
| **Timing over subject matter** | A path-scoped rule fires when Claude reads a matching file, not when it writes one, so creation-time guidance can never arrive through a rule. The symptom: the convention is honoured on edits and ignored on creation |
| **Skills** | Frontmatter, a `description` phrased the way a person would ask (the only thing routing sees), `disable-model-invocation` and `user-invocable`, progressive disclosure above about 150 lines, references of at most 300 lines each with a "Load when" column |
| **Subagents** | The frontmatter field set, restricting `tools` deliberately, what a subagent starts with (and what it does not get), and the rule that plugin-shipped subagents cannot declare `hooks`, `mcpServers` or `permissionMode` |
| **Hooks** | Events and which of them can block, matchers, handler types, exit codes, where hooks are registered, and failing safely. A hook is the right choice only when "usually followed" is not good enough |
| **Plugins** | Directory layout and the manifest trap, namespacing, path variables, what a plugin cannot ship, marketplaces and versioning |

## How It Works

1. **Read what exists.** List the skills, agents and hooks already present at project, user and plugin scope and run `/context`. An extension that duplicates one already installed makes both worse.
2. **Choose the primitive** by asking when the guidance is needed, whether it must be guaranteed, and whose context pays. If the answer is a memory file, hand off to `managing-claude-context`.
3. **Confirm the trigger exists.** Name the moment the extension will fire and check that moment is real.
4. **Write it,** reading the reference for that primitive first and writing the routing surface (`description`, `when_to_use`, matcher) before the body.
5. **Verify it loads and routes.** Run `/context`, then test routing with a request that does not name the extension.
6. **Report** which primitive was chosen and which was rejected, and why.

## Rules It Enforces

| Rule | Why |
| :-- | :-- |
| Decide the primitive before writing a line | The wrong primitive loads fine and fails invisibly |
| Use a hook, not an instruction, when something must hold regardless of what Claude decides | Instructions are context, not enforcement |
| Never ship two extensions whose descriptions overlap | Routing between near-identical descriptions is a coin flip, and the loser is silently never invoked |
| Never declare `hooks`, `mcpServers` or `permissionMode` in a plugin-shipped subagent | Claude Code ignores those fields there |
| Verify with `/context` and an un-named request | Loading and routing are different failures, and only one is visible |
| Never set a status, enable a hook or mark something enforced that the team has not agreed to | Enforcement is a team decision |

## What It Does Not Do

- Write product code, tests or infrastructure.
- Decide what a team's workflow should be; it packages workflows the team already has.
- Author `CLAUDE.md`, `.claude/rules/` or decision records.
- Configure MCP servers or permissions. A single hook wired into one repository's `settings.json` is Claude Code's own configuration, not an extension to author here; the skill picks the hook up once it ships inside a plugin or has to reach a second repository.

## Reference Files

| Reference | Load when |
| :-- | :-- |
| `choosing-the-primitive.md` | The routing table gives more than one plausible answer, every time |
| `authoring-a-skill.md` | Writing or restructuring any `SKILL.md` |
| `authoring-a-subagent.md` | Writing or changing a subagent |
| `authoring-a-hook.md` | Writing a hook, or deciding whether something needs enforcing |
| `packaging-a-plugin.md` | Bundling extensions for another repository or a marketplace |

## Related Skills

- [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context): owns `CLAUDE.md`, path-scoped rules and the decision index. The split: "I want to build something" goes to this skill, "I want this repo's memory files to be right" goes there.

## Source

- [`plugins/tsh-core/skills/authoring-claude-extensions/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/authoring-claude-extensions/SKILL.md)
- [`plugins/tsh-core/skills/authoring-claude-extensions/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-core/skills/authoring-claude-extensions/references)
