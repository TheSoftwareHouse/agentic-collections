---
name: formatting-jira-issues
description: "Transforms an approved epic and story list into Jira-ready issues against a benchmark template — field mapping, Jira markdown, completeness validation, the formatting review and the Gate 2 push approval — and imports an existing Jira backlog into the same local format for iteration. Use before creating or updating any Jira issue from a workshop backlog."
when_to_use: "Trigger on: 'get these ready for Jira', pushing a backlog to Jira, importing an existing Jira project or epic keys for local iteration, verifying issues after a push, or refreshing the project baseline after a sync."
---

# Formatting Jira Issues

Applies one consistent template to every task, preserves source traceability,
validates completeness, and manages the review gate that stands between a local
markdown file and real Jira issues.

## Applicability and Precedence

The project's own Jira conventions — naming, labels, priority scheme, issue types —
outrank this skill's defaults. Where the board already has a convention, match it
and say so; apply the benchmark template where the board is silent.

## Explicit Exclusions

This skill does not extract or invent scope, does not estimate (sizing guidance is
a suggestion for refinement, not an estimate), and does not decide roadmap waves.
No roadmap content reaches Jira.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Preserve a protected task (Done, Cancelled, PO APPROVE) exactly as imported, mark it `🔒` in its `###` heading, and skip every formatting, validation and update step for it. |
| MUST | Give every epic and story a `Jira Key` field — the real key, or `—` when it has never been pushed. |
| MUST | Record Gate 2 approval in `.gates.md` **before** the first Jira write call. A `PreToolUse` hook enforces this. |
| MUST | Present the sync summary — create / update / skipped, with counts — and get approval before pushing. |
| MUST | Write each returned Jira key back into `jira-tasks.md` immediately after that issue is created, not in a batch at the end. |
| MUST | Review formatted output from the file with one disposition question, never a popup per task. |
| MUST | Use the project's canonical terms in issue titles and descriptions when a domain dictionary exists — the `UI label` column is not the identifier and must never replace it in a title. |
| NEVER | Reformat, reword or update a protected task, locally or in Jira. |
| NEVER | Recreate a task that already has a Jira key — update it. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Benchmark template](./references/benchmark-template.md) | Before formatting anything — always | Required fields, description formats, priority mapping, labels, the `Jira Key` and `Status` fields |
| [Worked example](./references/jira-tasks-example.md) | While formatting the first epic and its stories | A fully populated epic with three stories at the expected depth and tone |
| [Pushing to Jira](./references/pushing-to-jira.md) | Steps 8–11, and any single-task change the user asks to push | Gate 2, sync summary, create/update order, verification, archive and baseline refresh, per-change flow |
| [Import mode](./references/import-mode.md) | The user supplies Jira keys, a project key or a JQL query instead of workshop materials | Fetching, field mapping, protected-status handling on import, file-first review |
| [Task baseline example](./references/task-baseline-example.md) | Refreshing the project baseline after a verified push | Baseline entry shape and identity rules |

## Execution Context

Jira mutation and file writing belong to the orchestrator in the main
conversation. Running as the `jira-formatter` subagent: you have no `Write`, no
`Edit` and no Atlassian tools — produce the formatted content, the completeness
table, the sync summary or the verification diff as your final message. Steps 8–11
are orchestrator-only.

## Procedure

1. **Load the inputs** — [`benchmark-template.md`](./references/benchmark-template.md)
   for the expected structure, `extracted-tasks.md` for the content, and the
   project's domain dictionary, if one exists, for canonical terms.
2. **Format each epic**: summary per the template's naming convention; a description
   carrying business overview, business value and success criteria; acceptance
   criteria transferred from the extraction; suggested labels drawn from the epic's
   domain, never hardcoded project values; and a priority mapped
   Critical → Highest, High → High, Medium → Medium, Low → Low.
3. **Format each story**: summary per the convention; a description with a context
   paragraph linking to the parent epic, a Source Context section preserving
   traceability, the "As a… I want… So that…" statement, numbered requirements, and
   technical notes only where the extraction carried them; acceptance criteria as a
   Jira-compatible checklist, keeping `GIVEN / WHEN / THEN` scenarios readable; a
   sizing suggestion (Small / Medium / Large) marked as guidance, not an estimate;
   labels consistent with the parent epic; the parent epic reference; and the mapped
   priority.
4. **Validate completeness** against the template — required fields populated,
   descriptions structured, criteria verifiable, language business-oriented,
   priorities and labels consistent — and produce a completeness table.
5. **Flag uncertain fields and ask.** Batch **up to 4 independent field questions**
   per `AskUserQuestion` call, each about a different task, never two about the
   same one. `header` is a chip of max 12 characters (`Story 2.1`, `Priority`); the
   question text names the task and what is missing; 2–4 options with 1–5 word
   labels and the reasoning in `description`. Resolve every flag before the review
   gate.
6. **Formatting review.** Write `jira-tasks.md` first (step 7), then review from the
   file: summarize in chat what was reworded, which priorities were adjusted, which
   fields were inferred, and which protected tasks were skipped with `🔒`. Ask one
   `AskUserQuestion` (`header: "Formatting"`): `Approve as-is` /
   `I'll edit the file` / `Walk me through the changes` / `Rework — I'll explain`.
   Walk through in batches of up to 4 when asked. Update and re-present on changes.
7. **Save** `specifications/<workshop-name>/jira-tasks.md`, with a `Jira Key` on
   every task — `—` for anything not yet pushed, the real key otherwise.
8. **Push, verify and refresh** — follow
   [`pushing-to-jira.md`](./references/pushing-to-jira.md) for Gate 2, the sync
   summary, creation and update order, post-push verification, and the archive and
   baseline refresh.

## Jira Markdown Compatibility

Applies to content destined for Jira itself. The local markdown file stays standard
markdown.

| Use | Not |
| --- | --- |
| `h2.`, `h3.` | `##`, `###` |
| `*bold*` | `**bold**` |
| `_italic_` | `*italic*` |
| `* item` (space after the asterisk) | `- item` |
| `# item` for numbered lists | `1. item` |
| `{noformat}` / `{code}` | fenced code blocks |
| `(/) criterion` for checklist items, including `(/) GIVEN … WHEN … THEN …` | `- [ ] criterion` |

## Related Skills

- [`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md) — supplies
  the task list this skill formats.
- [`reviewing-backlog-quality`](../reviewing-backlog-quality/SKILL.md) — runs before
  formatting, and applies equally to an imported backlog.
