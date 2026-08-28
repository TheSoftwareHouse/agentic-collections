---
name: reviewing-backlog-quality
description: "Systematically reviews an approved epic and story list for gaps, missing edge cases and delivery-readiness problems, then produces individually accept-or-reject suggestions that refine the backlog before Jira formatting. Runs Lite or Full analysis passes over a domain model built from the tasks themselves, optionally enriched with Jira board context."
when_to_use: "Trigger on: 'review these stories', quality-checking a backlog before pushing it to Jira, finding missing edge cases or lifecycle gaps in a task list, or auditing an imported Jira backlog for completeness."
---

# Reviewing Backlog Quality

Runs a structured gap analysis over a Gate 1-approved task list and turns each
finding into a suggestion the user accepts or rejects individually. The audit trail
is `quality-review.md`; accepted suggestions are applied to `extracted-tasks.md`.

## Applicability and Precedence

The approved task list is the subject, not the source of truth about scope — where
a finding would add scope the workshop never implied, it needs the user's explicit
acceptance. Jira board context, when available, outranks local guesses about
naming, labels and priorities.

## Explicit Exclusions

No technical architecture decisions. No effort estimates or priority changes. No
scope that is not implied by the source materials or a universal pattern. No
invented domain requirements without a cited source. No Jira writes — read-only
access, for enrichment only.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Filter out every task with a protected status (Done, Cancelled, PO APPROVE) before running passes, and drop any suggestion that targets one before presenting. |
| MUST | Run Pass R on every non-protected epic in both modes. |
| MUST | Write every suggestion to `quality-review.md` before asking anything, then ask one disposition question — a 40-suggestion review is never 40 popups. |
| MUST | Record a disposition for every suggestion, including rejected ones. The file is the audit trail. |
| MUST | Re-check the target's status immediately before applying an accepted suggestion, and log it as skipped if it became protected. |
| NEVER | Modify the task list without an explicit accept from the user. |
| NEVER | Mark a finding sourced from external research as High confidence. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Analysis passes](./references/analysis-passes.md) | Before step 4 — always; it defines every pass, its findings and its defaults | Passes A–J and R, example patterns, confidence and action defaults |
| [Quality review example](./references/quality-review-example.md) | Before writing `quality-review.md` in steps 7 and 9 | Report shape, suggestion format, disposition records |

## Execution Context

Running in the main conversation: ask with `AskUserQuestion`, apply accepted
changes and write the files yourself. Running as the `backlog-quality-reviewer`
subagent: you have no interactive tool, no write tool and no Atlassian access — run
only the passes your prompt assigns, over the task list it supplies, and return the
structured suggestions as your final message.

## Review Modes

| Mode | Use when | Active passes |
| --- | --- | --- |
| Lite | Default for small, low-risk workshops — roughly ≤3 epics and ≤12 stories, unless the user asks for Full | A, B, E, H, I, K, then R |
| Full | Larger workshops, regulated domains, high-risk scope, or on request | A–J, K, then R |

Pass K runs in both modes only when a project dictionary exists; with none, skip it
and record the skip in the review output.

## Procedure

1. **Load inputs and select the mode.** `extracted-tasks.md` is mandatory — it is the
   Gate 1-approved list. Cross-reference `cleaned-transcript.md`, `intent-brief.md`,
   `workshop-context-summary.md`, designs and any other source material for detail
   lost during extraction. Record the chosen mode in the review output before
   running anything.
2. **Gather Jira board context (optional).** Only if Atlassian tools are available
   and the user has named a project: list the accessible resources, ask which one if
   several exist, fetch the existing epics and stories, and note naming conventions,
   label usage, priority patterns and related work. The review works identically
   without it — never block on Jira.
3. **Build the domain model** from the task list alone: **actors** (role, epics
   involved, key capabilities), **entities** (where each is created, read, updated,
   deactivated), and the **relationships** between them. This is a business map of
   what the system manages, not a technical data model, and it is what makes the
   gap detection systematic. Where a project dictionary exists, seed the model from
   it; where one does not, offer the model built here to
   `/tsh-product-management:domain-dictionary` as a starting point.
4. **Run the active passes**, following
   [`analysis-passes.md`](./references/analysis-passes.md). Apply the protected-status
   filter first.
5. **Enrich with domain research** where `WebSearch`/`WebFetch` are available:
   identify the primary domain, research its common features and compliance
   expectations, and fold what you find into the Pass J results.
6. **Classify each finding into a suggestion**: a confidence level (**High** for
   universal patterns, **Medium** for context-dependent ones, **Low** for research
   or speculation); an action type — `ADD_ACCEPTANCE_CRITERION`, `MODIFY_STORY`,
   `ADD_TECHNICAL_NOTE`, `NEW_STORY`, `NEW_EPIC`, `MODIFY_EPIC`; and the exact
   proposed text, written in the format `extracted-tasks.md` already uses. Merge
   overlapping findings from different passes into one suggestion that names all
   contributing passes. Where Jira context exists, note duplicates
   ("already tracked as PROJ-123 — consider linking"). Keep the full evidence chain
   for every Pass R finding.
7. **Run Gate 1.5 file-first.** Order suggestions by epic, then confidence within
   the epic, with new-epic proposals last. Write them all to `quality-review.md` as
   checkbox items with stable IDs, then ask **one** `AskUserQuestion`
   (`header: "Review"`): `Accept all High` / `I'll tick the file` /
   `Walk me through them` / `Skip review`. Walk through in batches of **4 per call**
   when asked — `header` max 12 characters, full context in the question text,
   options `Accept` / `Reject` / `Accept, modified`. Honour free-text dispositions
   ("QR-01, QR-04–QR-09", "accept all high") without re-asking per item. Record each
   decision back into the file.
8. **Apply accepted suggestions** to `extracted-tasks.md`, re-checking protected
   status first: add criteria to the named story; update scope for `MODIFY_STORY`;
   append notes for `ADD_TECHNICAL_NOTE`; add a new story under its epic following
   the existing numbering; add a `NEW_EPIC` at the end with a complete Epic Delivery
   Contract, its stories, the overview table and any dependencies; change only the
   named field for `MODIFY_EPIC`. Update the Workshop Summary counts afterwards.
9. **Save the report** to `specifications/<workshop-name>/quality-review.md`
   following [`quality-review-example.md`](./references/quality-review-example.md):
   the domain model, every suggestion generated, each disposition, and a summary of
   what was applied.

## Related Skills

- [`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md) — supplies
  the task list and defines the Epic Delivery Contract that Pass R checks.
- [`planning-delivery-roadmaps`](../planning-delivery-roadmaps/SKILL.md) — consumes the
  accepted findings and owns every wave, track and allocation decision Pass R
  deliberately leaves alone.
