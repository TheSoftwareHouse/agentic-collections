# TSH Product Management

Workshop-to-backlog business analysis: Jira-ready epics and user stories, systematic quality review, and an outcome-based delivery roadmap, behind five human review gates.

Install at **user scope** — this plugin travels with you, not with a repository. It
carries TSH's business-analysis workflow: discovery material in, a reviewed backlog
and a client-facing roadmap out, with every irreversible step behind an approval the
workflow records in a file.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-product-management@tsh-agentic-collections
```

## Start here

```shell
/tsh-product-management:analyze-materials specifications/inputs/billing-workshop.md
```

```shell
/tsh-product-management:explore-materials specifications/inputs/rfp-bundle/
```

Both take a transcript path, a Figma or FigJam link, a PDF, a folder of documents —
or, for `analyze-materials`, Jira issue keys or a project key to import an existing
backlog instead.

## What's in it

| Component | Invoke | Covers |
| :-- | :-- | :-- |
| `analyze-materials` | `/tsh-product-management:analyze-materials` | Entry point for the full workflow: materials or an existing Jira backlog in, reviewed epics and stories out |
| `explore-materials` | `/tsh-product-management:explore-materials` | Entry point for Explore Mode: a business-context summary, deliberately stopping short of any backlog item |
| `domain-dictionary` | `/tsh-product-management:domain-dictionary` | Entry point for the per-product domain dictionary: canonical business terms, not domain-driven design |
| `orchestrating-business-analysis` | `/tsh-product-management:orchestrating-business-analysis` | Runs the workflow: the five gates, the delegation, the persistent writes, the Jira push |
| `managing-domain-dictionaries` | `/tsh-product-management:managing-domain-dictionaries` | Harvest, Reconcile and Interview modes for the dictionary, checked by eleven review passes and reconciled against a live codebase without editing it |
| `processing-workshop-transcripts` | `/tsh-product-management:processing-workshop-transcripts` | Raw transcript to a structured document — topics, decisions, action items, preserved quotes |
| `analyzing-discovery-context` | `/tsh-product-management:analyzing-discovery-context` | What is known, where it came from, and what is still missing — before committing to scope |
| `extracting-epics-and-stories` | `/tsh-product-management:extracting-epics-and-stories` | Intent brief, epics as demonstrable vertical slices with a delivery contract, stories with source traceability |
| `reviewing-backlog-quality` | `/tsh-product-management:reviewing-backlog-quality` | Twelve analysis passes over a domain model built from the tasks, as individually accept-or-reject suggestions |
| `planning-delivery-roadmaps` | `/tsh-product-management:planning-delivery-roadmaps` | Markdown-only roadmap: client-facing outcome waves and internal coordination, linked by stable epic IDs |
| `formatting-jira-issues` | `/tsh-product-management:formatting-jira-issues` | The benchmark template, the Gate 2 push, post-push verification, and Jira-to-local import |
| `transcript-cleaner` (agent) | `@tsh-product-management:transcript-cleaner` | Cleans a transcript and returns it — haiku |
| `discovery-analyst` (agent) | `@tsh-product-management:discovery-analyst` | Synthesizes materials and designs into a business summary — sonnet |
| `backlog-extractor` (agent) | `@tsh-product-management:backlog-extractor` | Extracts one epic's stories, so a large backlog fans out — sonnet |
| `backlog-quality-reviewer` (agent) | `@tsh-product-management:backlog-quality-reviewer` | Runs assigned review passes and returns structured findings — opus |
| `roadmap-planner` (agent) | `@tsh-product-management:roadmap-planner` | Reconciles stable epic identity and proposes the waves — opus, never fanned out |
| `jira-formatter` (agent) | `@tsh-product-management:jira-formatter` | Applies the benchmark template and prepares verification diffs — haiku |
| `terminology-extractor` (agent) | `@tsh-product-management:terminology-extractor` | Extracts term candidates from material and sweeps codebase identifiers for Reconcile mode — sonnet |

The three entry points — `analyze-materials`, `explore-materials` and
`domain-dictionary` — are `disable-model-invocation: true` — commands, not routing
surfaces, so they cost nothing until you type them. Everything else is
model-invocable and routes on how people describe the work.

Release notes live in [`CHANGELOG.md`](CHANGELOG.md).

## The five gates, and the hook behind the last one

| Gate | After | You decide |
| :-- | :-- | :-- |
| 0 | The intent brief | Is this the right scope? |
| 1 | Extraction | Is this the right breakdown? |
| 1.5 | Quality review | Which suggestions land? |
| 1.75 | The roadmap proposal | Are these the right waves? |
| 2 | Jira formatting | Push, to this project, now? |

Approvals are written to `specifications/<workshop-name>/.gates.md` **before** the
action they unlock, because a long session gets summarized and a remembered
approval does not survive that.

**Gate 2 is enforced, not merely stated.** The plugin ships a `PreToolUse` hook
(`hooks/hooks.json`) that denies Atlassian write calls while the Gate 2 row is
unapproved, and refuses to update an issue whose status is Done, Cancelled or PO
APPROVE. It is active for anyone who installs the plugin, whichever way the
workflow is entered — including a direct
`/tsh-product-management:formatting-jira-issues` that never touches the
orchestrator. An approval is scoped: the Gate 2 row names its target project key
and unlocks that project only, and archived sessions are invisible to the guard,
so one workshop's approval never carries into the next.

What keeps it out of everyone else's way is the script, not the registration: it
stands down entirely in a repository with no BA artifacts on disk, so ordinary
Jira work elsewhere is unaffected. Confirm it is live with `/hooks`.

## Prerequisites

**Jira needs the Atlassian MCP server, and `tsh-core` bundles it.** Install
`tsh-core` alongside this plugin and run `/mcp` once to authenticate; every call
then runs under your own Atlassian account. This plugin deliberately does not ship
a second copy — plugin MCP servers deduplicate by endpoint, and one home per server
is what keeps its tool names predictable.

Tool names still vary by Atlassian server version, so the workflow discovers what
is available before the first push rather than assuming. For the same reason
nothing here pins an `mcp__atlassian__*` name in a tool allowlist: Jira writes go
through the normal permission prompt, with the hook behind it.

**Figma needs the Figma MCP server, and `tsh-core` bundles it too.** Same deal as
Jira: install `tsh-core`, run `/mcp` once, pick `figma`. Until that sign-in happens,
design analysis is reported as blocked rather than silently skipped. As with
Atlassian, nothing here pins a Figma tool name — the workflow uses whatever the
session exposes.

**PDFs need nothing.** They are read with the standard `Read` tool.

## Where the output goes

Session artifacts live in `specifications/<workshop-name>/` — the gate ledger, the
cleaned transcript, the intent brief, the extracted tasks, the quality review, the
roadmap draft and the Jira-ready tasks. Four artifacts outlive the session in
`specifications/projects/<project-name>/`: the approved `roadmap.md`, the
`task-baseline.md` that gives the next workshop its continuity context, and
`domain-dictionary.md`, which keeps its own gate ledger, `.dictionary-gates.md`, at
that same project scope.

## Not covered here

Implementation and code review are `tsh-product-engineering`; E2E and manual QA are
`tsh-product-testing`; design work is `tsh-product-design`. Those plugins may not be
installed, so this one names the gap rather than linking into them.

## Contributing

Add an agent as `agents/<agent-name>.md`, a skill as `skills/<skill-name>/SKILL.md`.
Start from [`templates/agent.md`](../../templates/agent.md) or
[`templates/SKILL.md`](../../templates/SKILL.md), and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Once installed, components from this plugin are invoked as
`@tsh-product-management:<agent>` and `/tsh-product-management:<skill>`.
