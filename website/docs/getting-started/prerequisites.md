---
title: Prerequisites
sidebar_label: Prerequisites
sidebar_position: 1
description: What you need before installing TSH Agentic Collections — Claude Code v2.1 or newer, plus the optional accounts and tools some plugins rely on.
sources:
  - README.md
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-stack-aws/README.md
  - plugins/tsh-stack-gcp/.mcp.json
sources_hash: "f768c5b41594dd2ff68288ab157094618629a4823142bbcc471de3dd5d7bbd00"
---

# Prerequisites

The collection is a Claude Code plugin marketplace, so the one hard requirement is
Claude Code itself. Everything else on this page is optional and depends on which
plugins you install.

## Claude Code v2.1 or newer

Check your version:

```shell
claude --version
```

To update, run `npm install -g @anthropic-ai/claude-code@latest`, or
`brew upgrade claude-code` if you installed it with Homebrew.

The marketplace repository is public, so adding it needs no GitHub authentication.

## Accounts for the bundled servers

`tsh-core` bundles three MCP servers. Two need an interactive sign-in, once per
machine. Both are optional; see [Connecting tools](/docs/getting-started/connecting-tools).

| Server | You need | Notes |
| :-- | :-- | :-- |
| [Atlassian](/docs/integrations/atlassian) | An Atlassian Cloud account | Atlassian Cloud only |
| [Figma](/docs/integrations/figma) | A Figma account | Works on all seats and plans |
| [Context7](/docs/integrations/context7) | Nothing | No sign-in |

## Tools some plugins launch

Plugins that launch a local tool need it on your machine. If it is missing, only the
feature that uses it fails.

| Tool | Needed for | What the source says |
| :-- | :-- | :-- |
| `playwright-cli` (Node.js required) | UI evidence in `tsh-product-engineering`, locator exploration in `tsh-product-testing` | Workflows check for it before first use and ask whether to install it for you. See [Playwright CLI](/docs/integrations/playwright-cli). |
| `uv` | The `aws-documentation` server in `tsh-stack-aws` | Without it that one server fails to start and everything else works. See [AWS Documentation](/docs/integrations/aws-documentation). |
| Node.js 20+ (`npx`) and the gcloud CLI, signed in | The three Google Cloud servers in `tsh-stack-gcp` | `npx` is declared in the plugin's `.mcp.json`; the servers' own READMEs add Node.js 20+ and a signed-in gcloud CLI. See [GCP](/docs/integrations/gcp). |

## Next

[Install the plugins](/docs/getting-started/installation).
