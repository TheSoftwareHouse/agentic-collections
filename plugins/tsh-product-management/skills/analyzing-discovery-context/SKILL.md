---
name: analyzing-discovery-context
description: "Gathers and expands the business context around a task or workshop topic: pulls what is known from task trackers, knowledge bases, documents and designs, finds the gaps, resolves them with the user, and writes a research report. Use before committing to a backlog, when a request is ambiguous, or when comparing new material against an existing baseline."
when_to_use: "Trigger on: exploring workshop materials before extraction, 'what do we actually know about this', gap analysis on a thin task description, building context from a Jira ID or a PDF brief, or checking new material against an existing project baseline."
---

# Analyzing Discovery Context

Builds the picture the rest of the workflow depends on — what is already known,
where it came from, and what is still missing — without committing to any backlog
item.

## Applicability and Precedence

The user's own materials outrank anything inferred. Where a project baseline
exists at `specifications/projects/<project-name>/task-baseline.md`, treat it as
continuity context, not as a constraint on new scope.

## Explicit Exclusions

This skill does not create epics or stories, does not write technical
specifications or implementation plans, and does not estimate. It reports what is
known and what is missing.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Exhaust the supplied materials before asking the user anything — never ask what the transcript, PDF, design or tracker already answers. |
| MUST | Attribute every finding to its source, so a reader can tell evidence from inference. |
| NEVER | Guess at the contents of a document you could not read. Report the blocker instead. |
| NEVER | Fill a gap silently. An unresolved gap is an open question, not an assumption you make on the user's behalf. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Research report example](./references/research-report-example.md) | Before writing the report — always | Section order and the fields each section carries |

## Execution Context

Running in the main conversation: ask with `AskUserQuestion` and write the report
yourself. Running as the `discovery-analyst` subagent: you have no interactive and
no write tool — return the analysis as your final message with everything you
would have asked under `## Open Questions`, and let the orchestrator raise it at
the next gate.

## Procedure

1. **Determine the input source**, because it decides how much of steps 2–3 you
   need:
   - *Research or plan files* (`*.research.md`, `*.plan.md`) — the primary source of
     requirements, acceptance criteria, scope and definition of done.
   - *A Jira or task ID* — fetch the details through the Atlassian MCP tools
     available in this session.
   - *Context supplied inline* — treat the prompt as the single source of truth and
     ask for clarification when something critical is missing.
   - *PDFs* — read them with the `Read` tool; no separate PDF server. Pass an
     explicit `pages` range beyond 10 pages. A scanned PDF with no text layer
     returns empty content: say so and ask for a text-based version.
2. **Find the available sources.** Check which task and knowledge tools this session
   actually has — Jira and Confluence through Atlassian, plus whatever else is
   connected — and whether a project baseline already exists.
3. **Gather from every source.** Search by ID where one exists, and by domain and
   jobs-to-be-done where it does not. Follow the connected tasks, subtasks and
   parent epic, not just the one named. Open every external link, knowledge-base
   page and design that the material references. Read referenced PDFs in full.
4. **Identify gaps and resolve them.** List the ambiguities and missing information
   the materials leave open, and ask with `AskUserQuestion` — batching up to 4
   independent questions per call, never two about the same item. Do not proceed
   until they are answered or the user tells you to continue.
5. **Write the report.** Follow
   [`research-report-example.md`](./references/research-report-example.md) exactly:
   keep every section, and add one further section, **Term Candidates**, listing the
   terms and source-language forms found in the material — they feed
   `/tsh-product-management:domain-dictionary` next. Record all findings, all
   sources, and every question with the answer it received.

## Related Skills

- [`processing-workshop-transcripts`](../processing-workshop-transcripts/SKILL.md) —
  run first when the input includes a raw transcript.
- [`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md) — consumes
  this context to draft the intent brief.
