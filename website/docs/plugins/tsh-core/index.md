---
title: TSH Core
sidebar_label: Overview
sidebar_position: 0
description: Tool mechanics every TSH engineer needs regardless of discipline or stack, plus the Atlassian, Figma and Context7 MCP servers the other plugins rely on.
sources:
  - plugins/tsh-core/.claude-plugin/plugin.json
  - plugins/tsh-core/README.md
  - plugins/tsh-core/.mcp.json
sources_hash: "9509ae9b138a0a869e150606a96a06b4736b4132a0cb595430d9433db1a6983b"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Core

`tsh-core` holds what is neither a discipline's practice nor a stack's convention: Git worktree lifecycle, the house standard for writing technical documents, authoring Claude Code extensions, the project-context files Claude Code loads, the decision-record format and lifecycle, and a one-command project setup that wires them together. It also bundles three MCP servers: Atlassian for Jira and Confluence, Figma for design context, and Context7 for library documentation.

It is the only plugin in the marketplace defined by a negation (neither a discipline nor a stack), so it is deliberately small and has the highest admission bar in the repository.

## Who installs it and where

Install it at `user` scope, like a discipline plugin: nothing in it depends on your role or on the language a repository is written in, so it should follow you everywhere. Stack plugins go at `project` scope instead, because the repository decides those. See [Installation](/docs/getting-started/installation) for the commands.

`tsh-core` is installed by people who have no other plugin at all, so its skills reference only files inside the plugin itself.

## What it ships

<PluginComponents plugin="tsh-core" />

The plugin ships no agents and no hooks. Every skill except `init` is model-invocable: Claude loads it when the work matches its description. `init` is the one deliberate exception (`disable-model-invocation: true`): it is a command you type, so its description is never preloaded.

### How the skills divide the work

- **Build something versus fix the memory files.** [authoring-claude-extensions](/docs/plugins/tsh-core/skills/authoring-claude-extensions) owns skills, subagents, hooks and plugins; [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context) owns `CLAUDE.md`, `.claude/rules/` and the decision index. Each hands off to the other rather than overlapping.
- **Setup versus upkeep.** [init](/docs/plugins/tsh-core/skills/init) is the command you type once per repository. It works by running `managing-claude-context` and its neighbours in order and wiring maintenance pointers into `CLAUDE.md`; every rule about the artifacts stays with the owning skill.
- **Decision records are split three ways.** The index schema, the binding note and the `CLAUDE.md` pointer belong to `managing-claude-context`; record format, numbering, status lifecycle and superseding belong to [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records); the prose inside a record belongs to [writing-technical-documents](/docs/plugins/tsh-core/skills/writing-technical-documents). None of them sets a record's status: marking something `Accepted` stays a human call.
- **Prose craft, never structure.** `writing-technical-documents` governs the words inside a document, not which sections an artifact needs.

## Bundled MCP servers

The plugin ships an `.mcp.json` with three remote HTTP servers. They appear in `/mcp` as plugin-provided and can be disabled per project from the same panel. Adding a server to `tsh-core` needs three disciplines that use it in a normal month; an MCP server adds nothing to the skill listing, and Claude Code defers tool schemas until a tool is used.

| Server | Endpoint | Sign-in | What it gives Claude |
| :-- | :-- | :-- | :-- |
| `atlassian` | `https://mcp.atlassian.com/v1/mcp/authv2` | Run `/mcp`, pick `atlassian`, finish the browser login (OAuth) | Read and update Jira work items and Confluence pages directly. Atlassian Cloud only |
| `figma` | `https://mcp.figma.com/mcp` | Run `/mcp`, pick `figma`, finish the browser login (OAuth) | Read a design directly: layout, variables, components and a rendered export |
| `context7` | `https://mcp.context7.com/mcp` | None | Current, version-specific library and framework documentation, read-only |

- **Per-user access.** Atlassian and Figma are OAuth-authenticated, so every call runs as you and grants nothing you could not already open yourself. Without the Figma login the server shows as needing authentication, and agents that need a design report what is missing rather than guessing at one.
- **Context7 rate limit.** Without an API key it works under Context7's anonymous rate limit; a teammate who hits it can add their own key in a user-scope `context7` entry, which outranks the bundled one.
- **Bitbucket and the Figma desktop server are not bundled.** The same Atlassian server exposes Bitbucket Cloud only under API-token authentication, and the Figma desktop server is a separate local endpoint that needs the desktop app. The plugin README shows how to add each yourself.
- **Do not pin tool names.** A teammate's own user-scope entry wins on precedence and changes the tool namespace, so tool names are discovered at runtime and never written into an agent's `tools:`, a skill's `allowed-tools:` or a hook matcher.

For sign-in steps and server details see [Connecting tools](/docs/getting-started/connecting-tools), [Atlassian](/docs/integrations/atlassian), [Figma](/docs/integrations/figma) and [Context7](/docs/integrations/context7).

## Why these servers live here

Each server is here because several disciplines use it and none of that changes with the language a repository is written in. According to the plugin README:

- **Atlassian:** engineering, product management and testing all read from Jira.
- **Figma:** product engineering judges implemented UI against it, and product management reads flows and annotations out of it during discovery.
- **Context7:** testing looks up the Playwright API, platform engineering reads Terraform provider, Kubernetes and CI documentation, and product engineering checks framework APIs while implementing.

## What belongs in tsh-core

A contribution reaches `tsh-core` only by elimination: it would not change if the repository switched language or framework, and it would not change if the reader switched job. Core skills are tool mechanics, where the procedure is dictated by the tool's own semantics (`git`, the shell, Claude Code's memory subsystem), not by a TSH opinion. The README names two closed exceptions that wrap no tool, `writing-technical-documents` and `managing-decision-records`, and a pull request must name three of the five disciplines that would use an addition in a normal month and report the plugin's routing footprint (the combined `name`, `description` and `when_to_use` characters across its skills) before and after. A bundled MCP server adds no routing footprint, so for a server the three-discipline test decides. Ties go to a discipline plugin.

## Changelog

Release history is in the [tsh-core changelog](/docs/changelog/tsh-core).
