---
title: UI Capture Worker
sidebar_label: ui-capture-worker
sidebar_position: 4
description: Collects UI verification evidence from a running app with Playwright CLI into the iteration artifact directory and exports the shared Figma reference image when given a Figma URL.
sources:
  - plugins/tsh-product-engineering/agents/ui-capture-worker.md
sources_hash: "307e20664038ab24fd2ad9ee9a046c3b89c2d8f301a75e0329ecfff187c6229d"
---

# UI Capture Worker

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Mention:** `@tsh-product-engineering:ui-capture-worker`  
**Model:** `haiku` (frontmatter also sets `effort: low`)  
**Tools:** no `tools` list in the frontmatter; `disallowedTools: Write, Edit`  
**Skills preloaded:** [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence)

A mechanical capture worker for the UI verification loop. It collects a full-page screenshot, computed styles and an accessibility snapshot from a running app, and prepares the shared Figma reference. It never judges whether the UI matches the design, never interprets visual correctness and never substitutes code reasoning for captured evidence. The preloaded `capturing-ui-evidence` skill is its capture contract. Use it during UI verification, always before [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) judges design fidelity.

## Inputs it requires

The delegation must name:

- the user-confirmed **exact full URL** for this pass. Without it the worker returns a blocker immediately,
- the pinned **locale, language and text direction**, with how to select them when the app supports more than one,
- the **iteration artifact directory** `specifications/<task-id>/ui-verification/iteration-<N>/`,
- the **shared verification root** with the `figma-expected.png` path.

It may also carry a Figma URL or node link, and prepared auth inputs: a repo-root `.env` contract or an already-authenticated storage-state path.

## Responsibilities and boundaries

- Never infers, normalizes or replaces the caller-provided URL, never inspects project config to pick another URL or port, and never launches or switches to another local app or server.
- When a Figma URL and shared root are provided, exports or ensures the shared `figma-expected.png` through the Figma MCP before browser capture begins, so auth or page blockers cannot prevent EXPECTED preparation. If the Figma MCP is unavailable it reports a blocker. It never opens figma.com in the browser and never saves a browser screenshot as the reference.
- Writes every artifact into the caller-provided iteration directory with explicit paths, never leaving artifacts in `.playwright-cli/` or the working directory. It never modifies UI code, tests or design artifacts.
- Never bypasses, fakes, seeds or injects authentication, even for a trivially circumventable gate, which it flags as a potential security vulnerability in its escalation notes. A genuine login through the app's real sign-in UI is allowed only with the delegated `.env` contract or storage-state path. On a standard login redirect without prepared variables it derives the exact `TSH_UI_LOGIN_*` names from the live form and returns them, and on a rerun it reloads `.env` before the auth attempt. Credential values are never printed.
- Escalates every blocker to the caller immediately (missing URL, unreachable page, login redirect, unexpected content, missing target component, failed command). It never stops silently and never asks the user directly.
- Never runs `git clean`, `git reset`, `git stash`, `git restore` or `git checkout -- <path>`.

## What it returns

A structured capture summary containing:

- the exact full URL used,
- the locale, language and text direction actually captured, and how it was selected,
- the authentication mechanism used, when the page required one (documented recipe, existing E2E setup, existing `.env` variables, seeded account, or the derived `TSH_UI_LOGIN_*` fallback),
- the elements `computed-styles.json` measured, named, so the caller can confirm they cover what is under verification,
- the iteration artifact directory path,
- the shared Figma reference path and status (reused, exported now, or blocked),
- the files written, with confirmation that each exists at its explicit path,
- the named session used,
- relevant exit codes for open, goto, screenshot, snapshot, eval and cleanup,
- blocker or escalation notes, including any security-vulnerability flag,
- the exact derived `TSH_UI_LOGIN_*` variable names, in form order, when auth blocks capture on a standard credential screen.

## Used by

- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) delegates capture to it per gate iteration, and also a background export of `figma-expected.png` while implementation is still running.
- [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) delegates the capture half of each verification pass to it.

## Source

[`plugins/tsh-product-engineering/agents/ui-capture-worker.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/agents/ui-capture-worker.md)
