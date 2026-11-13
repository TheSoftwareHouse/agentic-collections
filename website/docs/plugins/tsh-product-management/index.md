---
title: TSH Product Management
sidebar_label: Overview
sidebar_position: 1
description: The business-analysis workflow from workshop material to reviewed epics, stories and a delivery roadmap behind five review gates, plus the project knowledge base, with a hook that gates Jira writes.
sources:
  - plugins/tsh-product-management/.claude-plugin/plugin.json
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/hooks/
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/references/review-gates-and-ledger.md
  - plugins/tsh-product-management/skills/writing-project-knowledge/SKILL.md
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/skills/initializing-project-context/scripts/wire_repos.py
sources_hash: "469a7e52150dd844d1cefdf274b27aae32ab64dcd5a44fba38f729a64aac5a8c"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Product Management

`tsh-product-management` carries TSH's business-analysis workflow: discovery material goes in, and a reviewed backlog and a client-facing roadmap come out, with every irreversible step behind an approval the workflow records in a file. Materials can be transcripts, Figma, PDFs and codebase context. The output is Jira-ready epics and user stories, a per-product domain dictionary and an outcome-based delivery roadmap. It can also import an existing Jira backlog for local iteration and controlled push-back.

Read-only worker subagents keep the heavy reading out of the main conversation: transcript cleaning, discovery analysis, epic extraction, quality review, roadmap planning, Jira formatting and terminology extraction each have one.

The plugin has a second job. It sets up and reads a project's knowledge base: a `<project>-context` repository that every code repository and every role reads with cited sources, and that changes only through a branch and a pull request (a knowledge base with no remote yet is the one exception). That part is the project-context skills: [`initializing-project-context`](/docs/plugins/tsh-product-management/skills/initializing-project-context), [`navigating-project-context`](/docs/plugins/tsh-product-management/skills/navigating-project-context), [`writing-project-knowledge`](/docs/plugins/tsh-product-management/skills/writing-project-knowledge), [`adding-project-context-workspace`](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace) and [`repairing-project-context-links`](/docs/plugins/tsh-product-management/skills/repairing-project-context-links). They are the one part of this plugin that people outside product management use, so `initializing-project-context` enables the plugin in every repository it connects, and an engineer or tester gets them without installing anything, together with the rest of this plugin, including both hooks.

## Install and scope

Install at **user scope**: this plugin travels with you, not with a repository. The commands are in [Installation](/docs/getting-started/installation).

## Start here

Both entry points take a transcript path, a Figma or FigJam link, a PDF, or a folder of documents. `analyze-materials` also takes Jira issue keys or a project key, to import an existing backlog instead.

- [`/tsh-product-management:analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) runs the full workflow: materials or an existing Jira backlog in, reviewed epics and stories out.
- [`/tsh-product-management:explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) runs Explore Mode: a business-context summary that deliberately stops short of any backlog item.

`/tsh-product-management:domain-dictionary` starts the per-product domain dictionary workflow, and `initializing-project-context` starts the knowledge base. These commands, like the two above, are `disable-model-invocation: true`: commands, not routing surfaces, so they cost nothing until you type them. Every other skill is model-invocable and routes on how people describe the work.

## What it ships

<PluginComponents plugin="tsh-product-management" />

## The five gates

Human review gates stand between raw material and a Jira backlog. Approvals are written to `specifications/<workshop-name>/.gates.md` before the action they unlock, because a long session gets summarized and a remembered approval does not survive that.

| Gate | After | You decide |
| :-- | :-- | :-- |
| 0 | The intent brief | Is this the right scope? |
| 1 | Extraction | Is this the right breakdown? |
| 1.5 | Quality review | Which suggestions land? |
| 1.75 | The roadmap proposal | Are these the right waves? |
| 2 | Jira formatting | Push, to this project, now? |

The procedure behind them is [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis). The end-to-end flow is described in [Business analysis](/docs/workflows/business-analysis), and the knowledge base in [Project context](/docs/workflows/project-context).

## The Jira-write gate hook

Gate 2 is enforced, not merely stated. The plugin registers a `PreToolUse` hook in `hooks/hooks.json`. Its matcher is `mcp__.*([Aa]tlassian|[Jj]ira|[Rr]ovo|[Cc]onfluence).*`, and it runs `hooks/guard-jira-write.mjs` with Node. It is active for anyone who installs the plugin, whichever way the workflow is entered, including a direct `/tsh-product-management:formatting-jira-issues` that never touches the orchestrator. Confirm it is live with `/hooks`.

The hook reads the tool call and the files on disk and returns one of three outcomes: stay silent so normal permission rules apply, deny the call, or ask the user.

**What it checks, in order:**

1. **Not a Jira write.** A tool that is not an Atlassian, Jira, Rovo or Confluence tool is ignored. A Confluence tool whose name does not also carry `jira` is left to the normal permission prompt, because both policies are about Jira issues. Publishing a domain dictionary or a page is therefore not gated. The same goes for a Confluence or Bitbucket operation sent through the `executeWrite` or `executeDestructive` runner of Atlassian's v2 server: they are not Jira writes either, unless the operation's name also carries `jira`, so they are left to the normal permission prompt.
2. **Reads are never gated.** The bare tool name (the part after the last `__`) is classified by its leading verb. Names starting with `get`, `search`, `list`, `read`, `fetch`, `lookup`, `view`, `find`, `query`, `describe`, `count`, `export` or `download` are reads, as are a few exact names such as `atlassianUserInfo`. On Atlassian's v2 server, `discover` is a catalogue lookup that runs nothing and is never gated, and neither is a read operation sent through the `executeRead` runner: the hook reads the operation's name from the call's `name` argument and classifies that. A write-verb operation sent through `executeRead` is not trusted as a read; it is handled like one sent through `executeWrite`. This is why the status check the workflow requires before an update is never blocked.
3. **Stands down outside BA sessions.** It scans the working directory (depth 6, skipping `node_modules`, `.git`, `dist`, `build` and dot-directories other than `.claude`) for live BA artifacts: `.gates.md`, `jira-tasks.md` or `extracted-tasks.md`. If none exists, it allows the call, so ordinary Jira work in other repositories is unaffected. Anything under a `sessions` directory is archived history and is invisible to the guard.
4. **Protected Status Policy.** A task in a live `jira-tasks.md` is protected when its task heading (`##` to `####`, `###` in the template) carries `🔒` or the word `PROTECTED`, or its `Status` line names Done, Cancelled or PO APPROVE. A line that carries both the issue key and `🔒` also protects that key. A write that targets the issue key of a protected task is denied whether or not the gate is approved.
5. **Gate 2 approval.** There must be a live `.gates.md` with a row numbered `2` that says `approved`. The row must name the target project key, such as `project ACME`, and every project the write targets must be named by an approved row. Approval for one project does not unlock another. The hook reads the target project from the call's issue-key fields (`issueIdOrKey`, `issueKey`, `key`, `issues`, `issueKeys`, `inwardIssue`, `outwardIssue`) and its project fields (`projectKey`, `projectKeyOrId`, `projectIdOrKey`, `project`). For a runner call it reads them from the call's `inputs`, and from the rest of the call too, so a key placed beside `inputs` by mistake is still caught. A write whose payload names no project in those fields is allowed by any approved Gate 2 row in a live ledger. A missing ledger, or one with no approved Gate 2 row, is treated as not approved.

**Classification of writes.** A tool whose bare name starts with a recognised write verb (`create`, `edit`, `update`, `transition`, `delete`, `add`, `comment`, `link` and similar) that fails a policy is **denied**. A runner call is classified by its operation name instead of its tool name, after the read check in step 2. The name is matched as sent, Jira first: a name carrying `jira` is a write whatever its verb, because the runner's tier already says it writes, so a Jira operation sent through `executeWrite` or `executeDestructive` is **denied** when it fails a policy, like a primary tool. A name carrying `confluence` or `bitbucket` is exempt, as in step 1. A name that fits neither product (Compass, Jira Service Management, one nobody recognises) cannot be classified. Neither can a missing, empty or non-string operation name, on any runner, `executeRead` included: it is never an early allow. A tool the hook cannot classify as a read or a write is treated as a potential write: if it fails one of the policies above it is held with **ask** instead of being denied, and otherwise it is allowed, so an unfamiliar server version stops for a human rather than failing open or hard-blocking the session. If the hook cannot parse its payload, resolve the working directory, or hits an internal error, it also falls back to ask.

**Why the row number matters.** The hook matches the Gate 2 row by number. That is why Roadmap Review is numbered `1.75` and the Jira gate is never renumbered.

**Known residual.** Two live, unarchived workshops that push to the same project share gate state, because a tool call carries no signal of which workshop it serves. Archiving the session right after post-push verification, which the workflow already requires, takes its ledger out of play.

### The project-context hook

A second hook in the same `hooks.json` runs `hooks/guard-project-context-block.mjs` only for `Edit` and `Write` calls on a file named `CLAUDE.md` or `CLAUDE.local.md`. It denies an edit whose result would remove or change the `tsh:project-context` block, which tells every session in a code repository where the project's knowledge base is. Any internal error allows the call, so a broken guard cannot lock people out of their own `CLAUDE.md`. It does not cover a shell command that rewrites the file. `initializing-project-context` writes the block through its own script, never through `Edit` or `Write`, so it is never blocked by this hook.

## Prerequisites

- **Jira needs the Atlassian MCP server, and `tsh-core` bundles it.** Install `tsh-core` alongside this plugin and run `/mcp` once to authenticate; every call then runs under your own Atlassian account. This plugin ships no MCP server of its own. Tool names vary by Atlassian server version, so the workflow discovers what is available before the first push, and nothing here pins an `mcp__atlassian__*` name in a tool allowlist. See [Atlassian](/docs/integrations/atlassian).
- **Figma needs the Figma MCP server, and `tsh-core` bundles it too.** Run `/mcp` once and pick `figma`. Until that sign-in happens, design analysis is reported as blocked rather than silently skipped. See [Figma](/docs/integrations/figma).
- **PDFs need nothing.** They are read with the standard `Read` tool.

## Where the output goes

Session artifacts live in `specifications/<workshop-name>/`: the gate ledger, the cleaned transcript, the intent brief, the extracted tasks, the quality review, the roadmap draft and the Jira-ready tasks.

These artifacts outlive the session, in `specifications/projects/<project-name>/`: the approved `roadmap.md`, the `task-baseline.md` that gives the next workshop its continuity context, and `domain-dictionary.md`, which keeps its own gate ledger, `.dictionary-gates.md`, at that same project scope.

## Not covered here

Implementation and code review are `tsh-product-engineering`, and E2E and manual QA are `tsh-product-testing`. Those plugins may not be installed, so this one names the gap instead of linking into them.
