---
title: Integrations overview
sidebar_label: Overview
sidebar_position: 1
description: The MCP servers and the CLI the TSH plugins rely on, which plugin bundles each, how they connect and what needs a sign-in.
sources:
  - plugins/tsh-core/README.md
  - plugins/tsh-core/.mcp.json
  - plugins/tsh-stack-aws/.mcp.json
  - plugins/tsh-stack-aws/README.md
  - plugins/tsh-stack-gcp/.mcp.json
  - plugins/tsh-stack-gcp/README.md
  - plugins/tsh-platform-engineering/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-testing/README.md
sources_hash: "450171976643218fc5b2364e5c2ff59c3c9249957ff58a08f74be003e6e97a67"
---

# Integrations overview

Plugins connect Claude to external tools through MCP servers bundled in a plugin's
`.mcp.json`, and through one command-line tool. An MCP server adds nothing to the
skill listing, and Claude Code defers its tool schemas until a tool is used, so a
session that never touches a server pays only for its tool names.

## What ships where

| Integration | Bundled by | Transport | Sign-in or prerequisite |
| :-- | :-- | :-- | :-- |
| [Atlassian](/docs/integrations/atlassian) | `tsh-core` | http | OAuth via `/mcp` |
| [Figma](/docs/integrations/figma) | `tsh-core` | http | OAuth via `/mcp` |
| [Context7](/docs/integrations/context7) | `tsh-core` | http | None |
| [AWS Documentation](/docs/integrations/aws-documentation) | `tsh-stack-aws` | stdio (`uvx`) | `uv` installed |
| [GCP](/docs/integrations/gcp): `gcp-gcloud`, `gcp-observability`, `gcp-storage` | `tsh-stack-gcp` | stdio (`npx`) | See the page |
| [Playwright CLI](/docs/integrations/playwright-cli) | Not bundled; a CLI you install | Command line, not MCP | `npm install -g @playwright/cli@latest` |

`tsh-stack-azure`, `tsh-platform-engineering` and `tsh-product-testing` bundle no
server of their own.

## One home per server

A server lives in exactly one plugin. Plugin-provided servers are deduplicated by
endpoint, but the surviving definition decides the tool namespace, and the winner
tracks plugin load order, which nobody controls. That is why `tsh-product-management`,
`tsh-product-engineering` and the other plugins that read Jira or Figma depend on
`tsh-core` for the servers instead of shipping a second copy.

Cloud servers ship with the cloud's own plugin: a GCP repository never starts an AWS
server, and no cloud server appears in a repository with no cloud plugin installed.

## Signing in

Run `/mcp` once per machine and sign in to `atlassian` and `figma`. Step by step:
[Connecting tools](/docs/getting-started/connecting-tools).

## Do not pin tool names

Tool names depend on which server entry wins. A teammate's own user-scope `figma`
entry takes precedence over the bundled one, and the namespace becomes `mcp__figma__*`
rather than `mcp__plugin_tsh-core_figma__*`. The plugins therefore never name a
server's tools in an agent's `tools:`, a skill's `allowed-tools:` or a hook matcher,
and discover what the session exposes at runtime instead.
