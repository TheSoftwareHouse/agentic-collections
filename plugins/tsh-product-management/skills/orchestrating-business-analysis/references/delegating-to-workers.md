# Delegating to the BA workers

Six read-only workers ship with this plugin. They keep their file reads, document
parsing and analysis traffic out of the main conversation and return structured
content you merge, validate and write.

| Work | Worker | Model |
| --- | --- | --- |
| Transcript cleanup and structuring | `transcript-cleaner` | haiku |
| Multi-source synthesis, baseline overlap, open questions | `discovery-analyst` | sonnet |
| Intent brief drafting, epic identification, story extraction | `backlog-extractor` | sonnet |
| Lite/Full review passes and structured findings | `backlog-quality-reviewer` | opus |
| Stable-ID reconciliation and the roadmap proposal | `roadmap-planner` | opus, never fanned out |
| Jira-ready formatting, verification diffs, baseline content | `jira-formatter` | haiku |

You may override a tier per call when the material justifies it — analysis on
`opus` for a five-document RFP bundle, extraction on `haiku` for one short
transcript. State the override and why.

Workers never write files, never speak to the user, and hold no Atlassian or design
tool access. You keep every user-facing interaction, every gate, every persistent
write, every Jira mutation, and every call to an external system — including
fetching designs.

## When to suggest parallelization

Do **not** auto-parallelize. Evaluate the volume, then *suggest* it and let the
user confirm. Conditions worth suggesting on:

- several independent input sources (transcript + Figma + codebase),
- 3+ substantial documents — multi-page PDFs, policy documents, requirement specs,
  not trivially short files,
- a transcript over ~3000 words or with 5+ distinct topics,
- 4+ epics with 15+ total stories, for quality review.

When you suggest it, say what will be parallelized, how many workers that means,
and the expected benefit.

**Issue every parallel `Agent` call in a single message.** Calls in separate
messages run sequentially and give up the entire benefit. This is the most common
mistake in this workflow.

## Scenario 1 — material processing (phase level)

*Case A, multi-source*: one worker per activity type — transcript, document
bundles, codebase reading. **Designs are the exception**: fetch them yourself with
whatever Figma tools the session exposes, then hand the extract to a worker to
interpret alongside the other material. A worker cannot reach a design tool.

*Case B, multi-document*: one worker per document. Group a subfolder into one
assignment when it holds 5 or fewer processable files; split larger ones into
batches of ~5, grouped by affinity. Each worker reads its own documents with `Read`
— PDFs included — and returns key requirements, decisions, constraints, business
rules and open questions.

The cases combine: 5 RFP documents + a codebase is up to 6 workers, with the Figma
link fetched by you and its extract folded into one of their prompts. Respect the
concurrency cap and batch, putting the long-running work — codebase, large PDFs —
in the first batch.

Then run a merge pass:

1. Collect every summary and verify completeness; report missing chunks to the user.
2. Cross-reference findings across documents for consistencies, conflicts and gaps.
   Think this through rather than skimming — cross-document contradictions are the
   highest-value output of this phase.
3. Raise contradictions with the user before proceeding (pricing in one document
   conflicting with scope in another).
4. Produce one unified material summary to feed extraction.

## Scenario 2 — task extraction (epic level)

Run material review and epic identification yourself, then fan out: one
`backlog-extractor` per epic, or 2–3 small epics per worker. Each gets the epic
definition, the paths to the source materials, and instructions to extract stories
for that epic only, following the story template. Each returns stories with
acceptance criteria, technical notes and priority for its epics.

Merge sequentially afterwards: consistent numbering, duplicates resolved,
cross-epic dependencies mapped. Then write `extracted-tasks.md` yourself.

## Scenario 3 — quality review (pass level)

Split the active passes into roughly equal batches across `backlog-quality-reviewer`
calls, each receiving the task list (or its path), its assigned passes, and the
suggestion format. Merge by deduplicating overlapping suggestions — keeping the
higher-confidence one or merging them — and assigning consistent IDs before
Gate 1.5.

## Roadmap planning is deliberately not a scenario

Reconciliation needs the entire epic set, the full prior roadmap and complete
dependency state in one context. Split across workers it produces conflicting
stable-ID allocations. Use exactly one `roadmap-planner`.

You may also skip the worker entirely. It is read-only, so you rewrite its whole
proposal to disk yourself — on a large epic set that pays for the content twice.
When the epic contracts are already in your context from extraction, or the backlog
is large enough that the rewrite dominates, apply `planning-delivery-roadmaps`
inline instead and say that you did and why. Delegation is the default, not a rule.

## Delegation rules

1. **Route to the owning worker.** Never send BA work to `general-purpose`,
   `Explore`, or any other agent — they carry no BA skills and no protected-status
   awareness.
2. **In-memory returns only.** Workers have no write tools; you assemble and write
   the output. This is what prevents concurrent file overwrites.
3. **1:1 assignment.** One chunk per worker, no overlapping material.
4. **Error handling.** A worker that fails or returns incomplete results is not
   automatically re-spawned — tell the user and ask whether to retry that chunk or
   proceed without it. A terminal error can also return *empty*: check for empty
   returns before merging rather than assuming content came back.
5. **Protected status.** Paste the policy into any prompt whose work touches
   existing tasks, even though the skills enforce it internally.
6. **Concurrency cap: 5 workers at once.** Batch beyond that.
7. **External systems stay with you.** Workers can query neither Jira nor a design
   tool; fetch what they need and pass it inline.

## The delegation prompt contract

A subagent starts with an empty context. The prompt is the only context it gets.
Every delegation prompt carries:

1. **Inputs** — repo-relative paths to `Read`. Never paste large material inline;
   pasting a 3000-word transcript into five prompts wastes context five times over.
2. **Scope** — the exact epic, document or passes assigned, and what is explicitly
   not theirs.
3. **External context** — any Jira payload and any design extract you fetched,
   inline. Workers reach neither system.
4. **Protected Status Policy** — verbatim, whenever existing tasks are in play.
5. **Output contract** — the exact section headings you expect back.
6. **Boundaries** — "Do not write files. Do not ask questions. Return the result as
   your final message."

```text
Extract user stories for Epic 2 (Payment reconciliation) only.

Inputs — read these files:
- specifications/billing-workshop/cleaned-transcript.md
- specifications/billing-workshop/intent-brief.md
- specifications/projects/acme/task-baseline.md

Scope: Epic 2 only. Epic boundary: everything from invoice import to ledger
match. Refunds are Epic 4 — do not extract them.

Jira context (you have no Atlassian access):
- ACME-441 "Import invoices" — status: Done  🔒 PROTECTED, do not restate
- ACME-462 "Match ledger entries" — status: In Progress

Return, as your final message and nothing else:
## Stories
(per story: ID, "As a… I want… So that…", GIVEN/WHEN/THEN criteria,
 source reference, priority)
## Cross-Epic Dependencies
## Open Questions

Do not write files. Do not ask questions.
```

## Merging and conflict resolution

1. **Deduplicate and check completeness.** Stories or suggestions can appear in two
   outputs at an epic boundary — keep the more detailed version, and verify every
   assigned chunk produced something.
2. **Renumber** to keep IDs sequential and consistent with the skill's scheme.
3. **Resolve cross-references** that span worker boundaries — dependencies, blockers.
4. **Escalate contradictions.** Two workers producing incompatible interpretations
   is a question for the user. If they ask you to resolve it yourself, reason it
   through and state which source you privileged and why.
