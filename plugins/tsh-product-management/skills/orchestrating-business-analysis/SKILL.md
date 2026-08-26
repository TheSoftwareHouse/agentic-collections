---
name: orchestrating-business-analysis
description: "Runs the business-analysis workflow end to end from the main conversation: turns discovery workshop material — transcripts, Figma, PDFs, codebase context — into Jira-ready epics and user stories and a delivery roadmap, behind five human review gates, delegating the heavy reading to read-only worker subagents. Also imports an existing Jira backlog for local iteration and controlled push-back."
when_to_use: "Trigger on: 'turn this workshop into tickets', workshop-to-backlog work, discovery material that needs epics and stories, pushing or updating a backlog in Jira, importing a Jira project or epic keys to iterate on, or planning delivery waves for a project."
allowed-tools: Read, Write, Edit, Grep, Glob, TodoWrite, AskUserQuestion, Agent
---

# Orchestrating Business Analysis

In this workflow the main conversation is the orchestrator. It owns the materials,
the gates, the files and the Jira mutations; the reading and drafting run in
read-only worker subagents so their document parsing stays out of this context.
Output is **business-oriented** throughout: epics and stories a stakeholder
understands without technical knowledge, with technical notes only where the
workshop raised them.

## When to Use

- Discovery workshop material needs to become a backlog.
- An existing Jira backlog needs local iteration, review and push-back.
- The user asks to explore materials before committing to any backlog
  (**Explore Mode** — context summary only, no epics or stories).

## Applicability and Precedence

The user's own materials and any approved artifact outrank inference: an approved
`intent-brief.md` bounds extraction, an existing roadmap holds prior identities,
and Jira remains the source of truth for status and ownership. A project's own Jira
conventions outrank this workflow's defaults.

## Explicit Exclusions

No technical specifications or architecture decisions. No implementation, test or
deployment plans. No story point estimates — sizing guidance only, for the team to
estimate at refinement. Where the work needs one of those, name the gap to the user
rather than improvising it here.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Record every gate approval in `specifications/<workshop-name>/.gates.md` **before** taking the action it unlocks. The ledger is the source of truth, not the conversation. |
| MUST | Keep the Jira gate's ledger row numbered `2` — the `PreToolUse` hook matches it by number. Roadmap Review is `1.75` for that reason. |
| MUST | Treat Done, Cancelled and PO APPROVE as immutable, everywhere in the workflow. |
| MUST | Keep every user-facing question, persistent write and Jira mutation in this conversation. Workers write nothing and speak to nobody. |
| MUST | Issue parallel `Agent` calls in a single message, or they run sequentially and the parallelism is lost. |
| MUST | Ask for confirmation before spawning workers — evaluate the volume and suggest parallelization rather than auto-parallelizing. |
| NEVER | Push to Jira before Gate 2 is recorded. If a write is blocked, verify the ledger — never work around the hook. |
| NEVER | Fan out roadmap planning. Reconciliation needs the whole epic set in one context. |
| NEVER | Guess where you could ask. Exhaust the materials first, then ask. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Review gates and the ledger](./references/review-gates-and-ledger.md) | Before the first gate, and before recording any approval | The five gates, the `.gates.md` format, the hook interlock, how to ask well |
| [Protected Status Policy](./references/protected-status-policy.md) | Any time existing tasks are in play, and before every delegation that touches them | The protected statuses, the seven rules, the paste-ready block |
| [Delegating to workers](./references/delegating-to-workers.md) | Before spawning any worker | Worker routing, when to parallelize, the prompt contract, merge rules |
| [Working with Jira](./references/working-with-jira.md) | Any Jira read, push, or iteration-mode session | Tool discovery, the safe push sequence, import entry point |
| [Reading workshop materials](./references/reading-workshop-materials.md) | Processing PDFs, designs, or mixed material bundles | `Read` on PDFs, Figma scope and blockers, unsupported formats |

## Session Artifacts

In `specifications/<workshop-name>/`: `.gates.md` (ledger), `cleaned-transcript.md`,
`workshop-context-summary.md` (Explore Mode only), `intent-brief.md`,
`extracted-tasks.md`, `quality-review.md`, `.roadmap-proposal.md` (draft),
`jira-tasks.md`. Outliving the session, in
`specifications/projects/<project-name>/`: `roadmap.md` and `task-baseline.md`.

## Procedure

Pick the entry point first. **Jira keys or a project key instead of materials** →
skip to import (`formatting-jira-issues` Import Mode), then join at step 6.
**Explore Mode** → produce `workshop-context-summary.md` and stop; do not create
epics or stories unless the user asks to continue.

1. **Create the gate ledger** at `specifications/<workshop-name>/.gates.md`.
2. **Process the transcript** with
   [`processing-workshop-transcripts`](../processing-workshop-transcripts/SKILL.md) when
   raw discussion material is supplied. Skip it for structured notes or direct
   requirements.
3. **Analyze the remaining materials and the baseline** —
   [`analyzing-discovery-context`](../analyzing-discovery-context/SKILL.md) over
   designs, PDFs and other documents, plus
   `specifications/projects/<project-name>/task-baseline.md` if it exists. This is
   the phase that most often justifies parallel workers; suggest it and get
   confirmation.
4. **Draft the intent brief** with
   [`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md), then run
   **Gate 0** and record it.
5. **Extract epics and stories** from the approved brief and all materials, then run
   **Gate 1** and record it.
6. **Run the quality review** with
   [`reviewing-backlog-quality`](../reviewing-backlog-quality/SKILL.md) — automatically
   after Gate 1, without asking whether to run it. Present the suggestions
   file-first at **Gate 1.5**, apply what the user accepts, and record it.
7. **Confirm the updated tasks.** Summarize what changed in `extracted-tasks.md`,
   offer the full list, and proceed only on confirmation.
8. **Propose the roadmap.** Route the confirmed tasks, accepted findings, baseline
   and any existing roadmap to a single `roadmap-planner`, which applies
   [`planning-delivery-roadmaps`](../planning-delivery-roadmaps/SKILL.md) and returns an
   in-memory proposal. Write it to `.roadmap-proposal.md`.
9. **Roadmap Review.** Validate the proposal from the file, ask one gate question,
   and record the approval in the `1.75` row. Only then create or update
   `specifications/projects/<project-name>/roadmap.md`, preserving prior identities
   and delivery history. The roadmap is Markdown-only: no Jira releases, custom
   fields, synchronization or status mutation.
10. **Format for Jira** with
    [`formatting-jira-issues`](../formatting-jira-issues/SKILL.md), preserving source
    traceability, and save `jira-tasks.md`.
11. **Gate 2.** Confirm the target project and the scope of the push, and record the
    approval **before** any write call.
12. **Push, verify, archive.** Create epics then linked stories (or update existing
    keys), read the issues back to verify, then archive the session artifacts and
    refresh the project baseline.

## Closing Handoff

End with exactly one suggested next step and the command to run — do not run it
yourself:

> Backlog is in Jira (ACME-501 … ACME-517), the roadmap is at
> `specifications/projects/acme/roadmap.md` (3 waves, 11 epics), and the baseline
> is refreshed.

Name the roadmap and its wave count when one was approved — it is what the client
sees, and with the baseline it is the only output that outlives the session. If the
session ended before Gate 2, say which gate you stopped at, which file holds the
current state, and how to resume.

Implementation, testing and platform work live in other plugins that may not be
installed. Name the gap; never path into them.

## Related Skills

All ship in this plugin, so if this skill loaded they are available — and each is
linked from the procedure step that uses it:
[`processing-workshop-transcripts`](../processing-workshop-transcripts/SKILL.md),
[`analyzing-discovery-context`](../analyzing-discovery-context/SKILL.md),
[`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md),
[`reviewing-backlog-quality`](../reviewing-backlog-quality/SKILL.md),
[`planning-delivery-roadmaps`](../planning-delivery-roadmaps/SKILL.md) and
[`formatting-jira-issues`](../formatting-jira-issues/SKILL.md).
