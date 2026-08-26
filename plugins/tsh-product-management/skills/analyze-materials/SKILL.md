---
name: analyze-materials
description: "Entry point for the full business-analysis workflow: processes discovery workshop materials into Jira-ready epics and user stories, or imports an existing Jira backlog to iterate on. Run /tsh-product-management:analyze-materials with a transcript path, Figma link, PDF path, folder, Jira issue keys, or a project key."
disable-model-invocation: true
---

# Analyze materials

Materials or target: **$ARGUMENTS**

If nothing was supplied, ask what to process before doing anything else — a
transcript path, a Figma or FigJam link, a PDF or a folder of documents, Jira issue
keys, or a Jira project key.

## What this runs

**Invoke `/tsh-product-management:orchestrating-business-analysis`** and follow it end
to end. It owns the procedure, the five review gates, the delegation to worker
subagents, and the Jira push.

Invoke the skill — do not simply `Read` its `SKILL.md`. Reading the file gets you the
text; invoking it is what puts the skill's own configuration into effect for the
session.

## Which entry point applies

| What the user supplied | Where the workflow starts |
| --- | --- |
| A transcript, designs, PDFs, notes | The standard workflow, from transcript processing |
| Jira issue keys or a project key | Import Mode in `formatting-jira-issues`, then quality review |
| Materials too ambiguous to commit to a backlog | Say so, and offer `/tsh-product-management:explore-materials` first |

## What you should end up with

In `specifications/<workshop-name>/`, named after the workshop topic in kebab-case
(for example `specifications/user-onboarding/`):

- `.gates.md` — the gate ledger, created first and updated as each gate is approved
- `cleaned-transcript.md` — when a raw transcript was supplied
- `intent-brief.md` — approved at Gate 0 before extraction begins
- `extracted-tasks.md` — the epic and story breakdown, updated after quality review
- `quality-review.md` — every suggestion and its disposition
- `.roadmap-proposal.md` — the draft reviewed at the Roadmap Review gate
- `jira-tasks.md` — the Jira-ready tasks

And at project level, surviving the session:

- `specifications/projects/<project-name>/roadmap.md` — written only after Roadmap
  Review approval
- `specifications/projects/<project-name>/task-baseline.md` — refreshed after a
  verified push

## Before you start

The workflow needs the Atlassian MCP server for anything Jira, and Figma MCP for
design links. Check what this session actually has and say so up front, rather than
discovering it at the push.
