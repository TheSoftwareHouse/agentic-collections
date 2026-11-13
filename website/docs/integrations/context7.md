---
title: Context7
sidebar_label: Context7
sidebar_position: 4
description: The hosted Context7 MCP server bundled with tsh-core — current, version-specific library documentation, with no sign-in — and the components that use it.
sources:
  - plugins/tsh-core/.mcp.json
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/agents/software-engineer.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-product-testing/agents/e2e-engineer.md
  - plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/SKILL.md
  - plugins/tsh-platform-engineering/README.md
  - plugins/tsh-platform-engineering/agents/devops-engineer.md
  - plugins/tsh-stack-frontend/README.md
  - plugins/tsh-stack-frontend/skills/implementing-frontend/SKILL.md
  - plugins/tsh-stack-aws/README.md
  - plugins/tsh-stack-azure/README.md
  - plugins/tsh-stack-gcp/README.md
sources_hash: "38bfca385360d05976082c7788d88ba3a8e0f520afc82111ae7be64ed0b43ad1"
---

# Context7

[Context7](https://github.com/upstash/context7) serves current, version-specific
library and framework documentation, so Claude checks an API against the version a
project pins instead of recalling it.

| | |
| :-- | :-- |
| Server name | `context7` |
| Bundled by | [`tsh-core`](/docs/plugins/tsh-core/) |
| Transport | `http` |
| URL | `https://mcp.context7.com/mcp` |
| Sign-in | None |
| Access | Read-only |

It sits in `tsh-core` because three disciplines drive it in a normal month: testing
looks up the Playwright API, platform engineering reads Terraform provider,
Kubernetes and CI documentation, and product engineering checks framework APIs while
implementing. Until `tsh-core` took it over, five plugins each bundled their own copy.

## No sign-in, no local process

This is Context7's hosted server, so it needs nothing on your machine. The copy the
five plugins used to bundle ran through `npx`, fetched the package from npm on every
session start and needed Node; this one does not.

Without an API key it works under Context7's anonymous rate limit. A teammate who hits
that limit can add their own key in a user-scope `context7` entry, which outranks the
bundled one.

## What uses it

| Plugin | Components |
| :-- | :-- |
| `tsh-product-engineering` | [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer) consults documentation for the version in the project manifest, through Context7 when it is available |
| `tsh-product-testing` | [`e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) and [`writing-playwright-e2e-tests`](/docs/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests) look up Playwright API detail |
| `tsh-platform-engineering` | [`devops-engineer`](/docs/plugins/tsh-platform-engineering/agents/devops-engineer), [`designing-multi-cloud-architecture`](/docs/plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture), [`implementing-ci-cd-pipelines`](/docs/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines), [`implementing-terraform-modules`](/docs/plugins/tsh-platform-engineering/skills/implementing-terraform-modules) and [`managing-secrets`](/docs/plugins/tsh-platform-engineering/skills/managing-secrets) check provider, platform and syntax documentation against pinned versions |
| `tsh-stack-frontend` | [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) looks up current React documentation for its version policy; without Context7 it falls back to react.dev |
| `tsh-stack-aws` | [`implementing-aws-terraform`](/docs/plugins/tsh-stack-aws/skills/implementing-aws-terraform) and [`auditing-aws-cost`](/docs/plugins/tsh-stack-aws/skills/auditing-aws-cost) use it for Terraform AWS provider documentation |
| `tsh-stack-azure` | [`implementing-azure-terraform`](/docs/plugins/tsh-stack-azure/skills/implementing-azure-terraform) and [`auditing-azure-cost`](/docs/plugins/tsh-stack-azure/skills/auditing-azure-cost) verify current VM sizes, AKS versions, pricing tiers and regional availability |
| `tsh-stack-gcp` | [`implementing-gcp-terraform`](/docs/plugins/tsh-stack-gcp/skills/implementing-gcp-terraform) and [`auditing-gcp-cost`](/docs/plugins/tsh-stack-gcp/skills/auditing-gcp-cost) verify machine types, GKE versions, pricing tiers and Terraform Google provider documentation |

## Playwright shortcut

For Playwright, `e2e-engineer` queries the library ID `/microsoft/playwright.dev`
directly rather than resolving it first, and puts the project's Playwright version in
the query.
