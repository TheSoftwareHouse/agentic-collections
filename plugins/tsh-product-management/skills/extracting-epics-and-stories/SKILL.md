---
name: extracting-epics-and-stories
description: "Turns processed workshop materials into a business-oriented backlog: an approved intent brief first, then epics as independently demonstrable vertical slices with a delivery contract, and user stories with source traceability and GIVEN/WHEN/THEN acceptance criteria. Use after transcripts and materials are processed, before any Jira formatting."
when_to_use: "Trigger on: 'turn this into epics and stories', drafting an intent brief, breaking a workshop into a backlog, writing user stories from discovery material, or defining epic scope boundaries and dependencies."
---

# Extracting Epics and Stories

Identifies discrete pieces of work from discovery material and structures them for
stakeholder review and eventual Jira creation. The output is a backlog, not a
technical specification.

## Applicability and Precedence

An approved `intent-brief.md` outranks the raw materials: once the user has agreed
the scope at Gate 0, do not quietly extract beyond it. A project baseline at
`specifications/projects/<project-name>/task-baseline.md` outranks fresh
interpretation where the two overlap.

## Explicit Exclusions

No technical architecture or implementation detail, no QA-perspective test design,
no story point estimates, no sprint or release planning. Where the workshop
discussed a technical constraint explicitly, record it as a short note — never
invent one.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Get the intent brief approved at Gate 0 before extracting a single story. |
| MUST | Give every epic a complete Epic Delivery Contract (below). Downstream delivery-readiness review and roadmap planning both read these fields. |
| MUST | Give every story a `Source` field pointing back to the material it came from. |
| MUST | Write acceptance criteria primarily as concise `GIVEN / WHEN / THEN` scenarios. |
| MUST | Present a 15-story breakdown as a file plus one disposition question — never one popup per story. |
| NEVER | Use implementation jargon. A stakeholder must understand what will be delivered without technical knowledge. |
| NEVER | Treat a story as the primary delivery unit. Stories are implementation detail beneath a contracted epic. |
| NEVER | Mint a canonical term here. A term the project's domain dictionary does not contain goes to its unresolved-terms inbox, not into the backlog as a new canonical form. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Intent brief example](./references/intent-brief-example.md) | Before drafting the brief in step 2 | Section order and the scope fields the brief carries |
| [Extracted tasks example](./references/extracted-tasks-example.md) | Before writing `extracted-tasks.md` in step 9 | Epic and story shape, numbering, dependency and assumption sections |

## Execution Context

Running in the main conversation: ask with `AskUserQuestion`, run the gates, and
write the files yourself. Running as the `backlog-extractor` subagent: you have no
interactive and no write tool — stay inside the epic boundary your prompt assigns,
return the extracted content as your final message, and collect everything you
would have asked under `## Open Questions`.

## Procedure

1. **Review every input**: `workshop-context-summary.md` if Explore Mode ran, the
   cleaned transcript as primary source, Figma/FigJam flows and annotations, PDFs
   (via `Read`, with an explicit `pages` range beyond 10 pages), any other supplied
   documents, and the project baseline if one exists. If
   `specifications/projects/<project-name>/domain-dictionary.md` exists, consume it
   as canonical terms; otherwise point the user at
   `/tsh-product-management:domain-dictionary` later rather than inventing terms now.
   Build the full picture before extracting anything.
2. **Draft the intent brief** — goal, in scope, out of scope, key stakeholders and
   actors, likely epic candidates, baseline overlap, open questions. Scope
   decisions only, no backlog detail.
3. **Gate 0.** Present the brief, confirm scope, exclusions and candidate epics, and
   iterate until the user approves. Do not extract before that approval.
4. **Identify epics as end-to-end vertical slices.** Each is a cohesive business
   capability one developer can complete holistically and demonstrate to the
   client. Set granularity by demonstrable customer outcome, not by a target count:
   split or combine until each epic has an independently demoable boundary. Record
   the **Epic Delivery Contract** for each:
   - **Customer Outcome** — the customer-visible result the epic delivers.
   - **End-to-End Boundary** — the complete vertical-slice scope needed to achieve
     and demonstrate it.
   - **Explicit Exclusions** — work intentionally outside the boundary.
   - **Demonstrable Scenario or Criteria** — what proves the outcome to a client.
   - **Known Dependency or Required Shared Contract** — named, or "None".
   - **Collaboration/Concurrency Classification** — exactly one of
     `Independent parallel work`, `Blocked work`, or
     `Shared contract explicitly resolved`. This records evidence about the epic;
     it does not decide waves or tracks — that is roadmap planning's call.

   Also draft a business-oriented title, a 2–3 sentence value description, and
   high-level success criteria.
5. **Break each contracted epic into stories** — one deliverable piece of
   user-facing functionality each, small enough for a single sprint as a guideline.
   Look in feature descriptions, user workflows, business rules, data requirements
   and integration points. Include non-functional stories only where explicitly
   discussed.
6. **Write each story** with: title (short, action-oriented), "As a [role], I want
   [capability] so that [benefit]", `Source`, acceptance criteria as
   `GIVEN / WHEN / THEN` scenarios, high-level technical notes only where the
   workshop raised them, a priority suggestion (Critical / High / Medium / Low),
   and optional additional acceptance checks where scenario form is not enough.
7. **Map dependencies** — blocked-by, related-to, and epic-level ordering, in plain
   notation ("Story 1.2 is blocked by Story 1.1").
8. **Record assumptions and out-of-scope items.** Label every interpretation you
   made where intent was not fully clear, so stakeholders can correct it, and state
   what was explicitly excluded.
9. **Run Gate 1 file-first.** Write the draft `extracted-tasks.md`, present a compact
   summary in chat (epics with story counts, plus any story you are less than
   confident about, flagged), then ask **one** `AskUserQuestion`:
   `Approve as-is` / `I'll edit the file` / `Walk me through the flagged stories` /
   `Rework — I'll explain`. Walk through flagged stories in batches of up to 4 per
   call — keep / split / merge / modify / remove — and close with "did I miss
   anything?". Iterate until the user approves; the orchestrator records the
   approval in `.gates.md`.

   When you ask anything here: `header` is a chip of **max 12 characters**
   (`Story 1.2`, `Epic 2`, `Scope`); the `question` text opens with the parent epic
   and story title and carries the full context; option labels are 1–5 words with
   the reasoning in `description`; order by impact, highest first.
10. **Save the outputs** — `intent-brief.md` and `extracted-tasks.md` in
    `specifications/<workshop-name>/`, following the two reference examples, with
    source traceability and business-friendly scenario criteria intact.

## Related Skills

- [`processing-workshop-transcripts`](../processing-workshop-transcripts/SKILL.md) —
  supplies the cleaned transcript.
- [`analyzing-discovery-context`](../analyzing-discovery-context/SKILL.md) — supplies
  business context and baseline comparison before extraction.
- [`reviewing-backlog-quality`](../reviewing-backlog-quality/SKILL.md) — reviews what
  this skill produces, and checks the Epic Delivery Contract in Pass R.
