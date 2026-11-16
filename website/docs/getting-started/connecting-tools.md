---
title: Connecting tools
sidebar_label: Connecting tools
sidebar_position: 3
description: Sign in to the Atlassian and Figma servers bundled with tsh-core with /mcp, once per machine, and what is deliberately left out.
sources:
  - README.md
  - plugins/tsh-core/README.md
  - plugins/tsh-core/.mcp.json
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-management/README.md
sources_hash: "35f63ecd103717f4c4974f890b1df693c805c9c3afeb8b5f80d0cbaca39b28c7"
---

# Connecting tools

`tsh-core` bundles three MCP servers. Two of them need one interactive sign-in each,
once per machine; the third needs nothing.

| Server | Gives Claude | Sign-in |
| :-- | :-- | :-- |
| [Atlassian](/docs/integrations/atlassian) | Jira work items and Confluence pages, read and updated directly | Browser login via `/mcp` |
| [Figma](/docs/integrations/figma) | Designs: layout, variables, components and a rendered export | Browser login via `/mcp` |
| [Context7](/docs/integrations/context7) | Current, version-specific library documentation | None |

## Sign in

Run `/mcp` inside a Claude Code session:

```shell
/mcp
```

Pick `atlassian`, finish the browser sign-in, then do the same for `figma`. You are
done on this machine, for every project.

Both servers are remote and OAuth-authenticated, so every call runs under your own
account and grants nothing you could not already open in Jira or Figma yourself.
Atlassian works with Atlassian Cloud only; Figma is available on all seats and plans.

Plugin-provided servers appear in `/mcp` as plugin-provided. You can disable one per
project from the same panel.

## If you skip a sign-in

Nothing else breaks. The server simply shows as needing authentication.

- **Figma:** agents that need a design report what is missing rather than guessing at one. The UI verification gate in `tsh-product-engineering` reports `VERIFICATION NOT RUN` instead of judging a design it cannot read.
- **Atlassian:** Jira and Confluence access is unavailable. For example, `e2e-engineer` reads acceptance criteria from a Jira issue key through this server, and without it you supply the criteria directly.

## What is deliberately left out

Two connections are not bundled, because each would fail for most people. Both are
documented, with an opt-in command, in the
[`tsh-core` README](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/README.md).

- **Bitbucket.** The Atlassian server exposes Bitbucket Cloud only under API-token authentication, never OAuth. That needs an Atlassian org admin to enable it first, the Bitbucket workspace linked to the organisation, and a scoped token per person. See [The Atlassian connector](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/README.md#the-atlassian-connector).
- **Figma's desktop server.** It is a separate local endpoint, served by the desktop app with Dev Mode enabled. It shows as a failed connection for anyone not running the desktop app, and it needs a Dev or Full seat on a paid plan, where the remote server needs neither. See [The Figma connector](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/README.md#the-figma-connector).

## Other servers and tools

Context7 is hosted, read-only and needs nothing on your machine. The servers shipped
by the cloud plugins and the Playwright CLI are not part of `tsh-core` and have their
own requirements, listed in the [integrations overview](/docs/integrations/overview).
