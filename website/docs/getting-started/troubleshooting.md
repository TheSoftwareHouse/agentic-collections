---
title: Troubleshooting
sidebar_label: Troubleshooting
sidebar_position: 5
description: Fixes for the common install problems — unrecognized /plugin, disabled plugins, a missing plugin in Discover, skills that do not appear — and for missing sign-ins and tools.
sources:
  - README.md
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/references/ui-verification-gate.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md
  - plugins/tsh-stack-aws/README.md
sources_hash: "a7c87183bc4c94efd9cf3682416ab2cb05df35049569501057c39f6f647fcf0d"
---

# Troubleshooting

## Install and catalog problems

**`/plugin` is not recognized.** Your Claude Code is too old. Update it, restart your
terminal and try again. The collection needs v2.1 or newer; see
[Prerequisites](/docs/getting-started/prerequisites).

**A plugin shows as `✘ disabled` in `claude plugin list`.** Check where you ran it.
`plugin list` reports every plugin you have installed, anywhere, but `Status`
reflects the current directory. A `project` or `local` scoped plugin is correctly
disabled outside its project. Run the command again from that project's root and it
should read `✔ enabled`.

**A plugin listed in the README is not in the Discover tab.** Your cached copy of the
catalog predates it. `/plugin` never re-fetches on its own and auto-update is off by
default, so refresh the marketplace; the README's
[Staying current](https://github.com/TheSoftwareHouse/agentic-collections#staying-current)
section has the commands. `/plugin update` will not help: it updates plugins you
already have, not the list of what exists.

**Skills or agents do not appear after installing.** Delete the marketplace's cached
clone, restart Claude Code, then add the marketplace again (Step 1) and reinstall
(Step 2) from the [installation steps](/docs/getting-started/installation):

```shell
rm -rf ~/.claude/plugins/marketplaces/tsh-agentic-collections
```

`~/.claude/plugins/known_marketplaces.json` is the index that tracks the clone and
where it lives. Older documentation points at `~/.claude/plugins/cache`; that path no
longer exists, so removing it does nothing.

**The reload summary says `0 skills`.** That is normal. It counts
only `commands/` directories, so `0 skills` does not mean anything failed.

**An empty component list for `tsh-product-design`.** Expected. That plugin is still
an empty scaffold and contributes no components yet.

**Anything else.** Run `/plugin` and open the **Errors** tab. Load failures are
reported there with the reason.

## Tools and sign-ins

**A server shows as needing authentication.** You have not signed in to it yet. Run
`/mcp`, pick the server and finish the browser login; see
[Connecting tools](/docs/getting-started/connecting-tools). Nothing else breaks while
you skip it.

**UI verification reports `VERIFICATION NOT RUN`.** That is a blocker state, not a
verdict, and it consumes no iteration of the verification loop. The blockers the
workflow names are a missing or wrong dev server URL, a login redirect, an
unreachable page, unexpected page content or state, incomplete capture artifacts, a
missing Figma reference, and the Figma MCP being unavailable to the reviewer. The
report says which one applies. Resolve it, rerun capture with the same pinned URL,
and verify again. For a Figma blocker, sign in to `figma` through `/mcp`. For a login
redirect, the capture worker names the `TSH_UI_LOGIN_*` variables to add to `.env`;
a login is never bypassed.

**`playwright-cli` is missing.** The UI verification and E2E workflows check for it
before first use and ask whether to install it for you or wait while you do. If an
agent cannot ask, it reports the missing prerequisite instead. See
[Playwright CLI](/docs/integrations/playwright-cli).

**The `aws-documentation` server fails to start.** It is launched with `uvx`, so
`uv` must be installed. Without it only that server fails; everything else keeps
working. See [AWS Documentation](/docs/integrations/aws-documentation).
