---
title: Installation
sidebar_label: Installation
sidebar_position: 2
description: Add the TSH marketplace to Claude Code, install the plugins you want at the right scope, activate them and sign in to Jira and Figma.
sources:
  - README.md
sources_hash: "8a09dd3f9ed05b5bf373ef613aed43978882a922b9d4886e3fc2c45e9f0beda5"
---

import Install from './_install.generated.md';

# Installation

Installation takes four steps: add the marketplace, install the plugins you want,
activate them, and sign in to Jira and Figma. The steps below are the install
section of the repository README, rendered here so the two never drift apart. Check
the [prerequisites](/docs/getting-started/prerequisites) first.

`tsh-product-design` is still an empty scaffold. Installing it works, but it
contributes no components yet, so an empty component list after installing it is
expected, not a broken install. Every other plugin ships real skills.

<Install />

## After installing

- Skills and agents are namespaced by plugin. See [First steps](/docs/getting-started/first-steps) for how to invoke them.
- Teams can declare the marketplace and a plugin set in a committed `.claude/settings.json`; the README section [Onboarding a whole project team at once](https://github.com/TheSoftwareHouse/agentic-collections#onboarding-a-whole-project-team-at-once) has the exact shape.
- To pick up new plugins and new versions, see [Staying current](https://github.com/TheSoftwareHouse/agentic-collections#staying-current); to remove plugins, see [Removing plugins](https://github.com/TheSoftwareHouse/agentic-collections#removing-plugins).
- If something does not show up, see [Troubleshooting](/docs/getting-started/troubleshooting).
