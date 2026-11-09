---
title: Atlassian
sidebar_label: Atlassian
sidebar_position: 2
description: The Atlassian Rovo MCP server bundled with tsh-core — Jira and Confluence access under your own account, who uses it, and why Bitbucket is not bundled.
sources:
  - plugins/tsh-core/.mcp.json
  - plugins/tsh-core/README.md
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/skills/analyzing-discovery-context/SKILL.md
  - plugins/tsh-product-management/skills/formatting-jira-issues/references/pushing-to-jira.md
  - plugins/tsh-product-management/skills/analyze-materials/SKILL.md
  - plugins/tsh-product-management/skills/domain-dictionary/SKILL.md
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/references/handoff-and-portability.md
  - plugins/tsh-product-management/skills/reviewing-backlog-quality/SKILL.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/working-with-jira.md
  - plugins/tsh-product-testing/agents/e2e-engineer.md
  - plugins/tsh-product-engineering/README.md
sources_hash: "1d81544211827f0f09edc381c1e3f3f0472c136ccae502b24bd9736c0f9a01c5"
---

# Atlassian

Atlassian's official
[Rovo MCP server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/),
so Claude reads and updates Jira work items and Confluence pages directly instead of
waiting for someone to paste a ticket into the conversation.

| | |
| :-- | :-- |
| Server name | `atlassian` |
| Bundled by | [`tsh-core`](/docs/plugins/tsh-core/) |
| Transport | `http` |
| URL | `https://mcp.atlassian.com/v1/mcp/authv2` |
| Sign-in | OAuth in the browser, once per machine |
| Scope | Atlassian Cloud only |

It sits in `tsh-core` rather than a discipline plugin because Jira is not one job's
tool: engineering, product management and testing all read from it, and none of that
changes with the language a repo is written in.

## Sign in

Run `/mcp`, pick `atlassian` and finish the browser login. Every call then runs as
you, so the server grants nothing you could not already open in Jira yourself. It
appears in `/mcp` as plugin-provided, and you can disable it per project from the same
panel. See [Connecting tools](/docs/getting-started/connecting-tools).

## What uses it

| Component | What it does with Atlassian |
| :-- | :-- |
| [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) | All Jira access in the business-analysis workflow runs through this server; the orchestrator owns the Jira mutations |
| [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) | Pushes formatted epics and stories to Jira, and reads issues in import mode |
| [`analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) | Needs the server for anything Jira |
| [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context) | Fetches the details of a Jira or task ID; reads Jira and Confluence |
| [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) | Gathers Jira board context, only when the tools are available |
| [`domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary) and [`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) | Publish a dictionary to Confluence, only when the server is connected |
| [`e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) | Given only a Jira issue key, fetches the issue and takes the acceptance criteria from it |

The worker agents of `tsh-product-management` deliberately have no Atlassian access.
Any Jira context they need reaches them inline in the delegation. `tsh-product-management`
also ships a `PreToolUse` hook that denies Atlassian write calls until the Gate 2
approval is recorded, and refuses to update an issue whose status is Done, Cancelled
or PO APPROVE. Confluence tools are never gated.

Tool names vary by Atlassian server version, so the workflow discovers what is
available before the first push, and nothing pins an `mcp__atlassian__*` name in a
tool allowlist. Jira writes go through the normal permission prompt, with the hook
behind it.

## Bitbucket is not bundled

The same server exposes Bitbucket Cloud and Jira Service Management, but only under
API-token authentication, never OAuth. That needs an Atlassian org admin to enable
API-token authentication under **Admin Hub → Rovo → Rovo MCP server**, the Bitbucket
workspace linked to the organisation, and a scoped token per person, so bundling it
would ship a server that fails for most installs. The opt-in command is in
[the `tsh-core` README](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/README.md#the-atlassian-connector).
That variant covers Jira as well, so disable the bundled `atlassian` entry in `/mcp`
if you add it, or both sets of tools sit in the session.
