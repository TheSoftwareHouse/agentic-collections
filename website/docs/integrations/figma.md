---
title: Figma
sidebar_label: Figma
sidebar_position: 3
description: Figma's remote MCP server bundled with tsh-core — how Claude reads a design, which agents and skills depend on it, and why the desktop server is not bundled.
sources:
  - plugins/tsh-core/.mcp.json
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/agents/ui-engineer.md
  - plugins/tsh-product-engineering/agents/ui-capture-worker.md
  - plugins/tsh-product-engineering/agents/ui-reviewer.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md
  - plugins/tsh-stack-frontend/skills/implementing-frontend/SKILL.md
  - plugins/tsh-product-testing/agents/e2e-engineer.md
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/reading-workshop-materials.md
sources_hash: "53a1293a38eb04cfcd3b85db87b13eb7acfc79969865db2be1a604f3f04a8a4a"
---

# Figma

Figma's official [remote MCP server](https://developers.figma.com/docs/figma-mcp-server/),
so Claude reads a design directly (the node's layout, variables, components and a
rendered export) instead of working from a description of it or a screenshot pasted
into the conversation.

| | |
| :-- | :-- |
| Server name | `figma` |
| Bundled by | [`tsh-core`](/docs/plugins/tsh-core/) |
| Transport | `http` |
| URL | `https://mcp.figma.com/mcp` |
| Sign-in | OAuth in the browser, once per machine |
| Availability | All seats and plans |

It sits in `tsh-core` because a Figma file is not one job's tool. Product engineering
judges implemented UI against it, and product management
reads flows and annotations out of it during discovery. It is deliberately not in
`tsh-stack-frontend`: stack plugins install at project scope, so a repository without
that plugin would leave the UI verification gate with no server.

## Sign in

Run `/mcp`, pick `figma` and finish the browser login. Every call runs as you, so the
server grants nothing you could not already open in Figma yourself. See
[Connecting tools](/docs/getting-started/connecting-tools).

Skip the login and the server shows as needing authentication. Agents that need a
design report what is missing rather than guessing at one, and the `ui-reviewer`
reports `VERIFICATION NOT RUN`.

## What uses it

| Component | What it does with Figma |
| :-- | :-- |
| [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) | Fetches and studies the design before writing any markup, layout or styling for a Figma-backed task; stops and reports if no Figma MCP is connected |
| [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) | Exports the shared reference image `figma-expected.png` when given a Figma URL, before browser capture begins |
| [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) | EXPECTED comes only from the Figma MCP; if it is unavailable or the node cannot be resolved, the result is `VERIFICATION NOT RUN` |
| [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) | One UI verification pass against a Figma URL, delegating capture and judgment to the two agents above |
| [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) | Closes every Figma-backed UI task through the UI verification gate |
| [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) | For a Figma-backed task, fetching the design through the Figma MCP is a hard gate before any markup or styling |
| [`e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) | Where a Figma MCP is connected and a design is referenced, reads the intended labels and flow, since accessible names inform locators. It does not judge visual styling |
| [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis) | Reads Figma and FigJam links in workshop materials, such as user flows and annotations. With no Figma MCP connected, design analysis is reported as blocked rather than silently skipped |

Capture and design access are separate: EXPECTED comes from Figma, while ACTUAL comes
from the running app through the [Playwright CLI](/docs/integrations/playwright-cli).
The UI agents never open figma.com in a browser to fetch a design.

The worker agents of `tsh-product-management` have no design-tool access. Figma
context reaches them inline in the delegation.

## The desktop server is not bundled

Figma also runs a local server at `http://127.0.0.1:3845/mcp`, served by the desktop
app with Dev Mode enabled. It is a separate endpoint, so bundling it would show as a
failed connection for everyone not running the desktop app. It also needs a Dev or
Full seat on a paid plan, where the remote server needs neither. The opt-in command
is in [the `tsh-core` README](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/README.md#the-figma-connector).
