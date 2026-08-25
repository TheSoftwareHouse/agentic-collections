# Review gates and the gate ledger

Five gates stand between raw workshop material and a Jira backlog. No data reaches
Jira without explicit approval at all of them.

| Gate | After | The user is deciding |
| --- | --- | --- |
| **0** | The intent brief | Is this the right scope, with the right exclusions and candidate epics? |
| **1** | Task extraction | Is this the right epic and story breakdown? |
| **1.5** | Quality review | Which suggestions refine the list, and which are rejected? |
| **1.75** | The roadmap proposal | Are these waves, tracks and stable IDs right? |
| **2** | Jira formatting | Push this, to this project, now? |

## The ledger

A BA session is long and its context may be summarized, so gate state lives in a
file, never in the conversation. Create
`specifications/<workshop-name>/.gates.md` at the start of the session:

```markdown
# Gate Ledger — <workshop-name>

| Gate | Artifact | Status | Approved at |
|---|---|---|---|
| 0 | intent-brief.md | pending | — |
| 1 | extracted-tasks.md | pending | — |
| 1.5 | quality-review.md | pending | — |
| 1.75 | roadmap.md | pending | — |
| 2 | jira-tasks.md | pending | — |
```

Rules:

- **Read the ledger. Never treat a gate as approved because it felt approved
  earlier in the conversation.**
- Write the approval **before** taking the action it unlocks.
- Record the target project key for Gate 2, and whether the approval covered a
  batch push or a single task.
- Record Roadmap Review in the `1.75` row **before** writing
  `specifications/projects/<project-name>/roadmap.md`. The draft at
  `.roadmap-proposal.md` may be written and revised freely; the project roadmap may
  not.

## Never renumber the Jira gate

The `2` row is read by the `PreToolUse` hook this plugin ships, which denies
Atlassian write calls while it is unapproved. **The hook matches that row by
number.** A gate inserted at `2` would point the hook at the wrong row, and
approving something unrelated would silently unlock Jira writes. Roadmap Review is
numbered `1.75` for exactly this reason.

If a Jira write is blocked, do not look for a workaround. Check the ledger, and if
the gate genuinely has not been approved, go back and get approval.

## After Gate 1.5: confirm the tasks, then propose the roadmap

Once accepted suggestions are applied, summarize what changed in
`extracted-tasks.md` — stories added, criteria added, stories modified — and offer
the complete updated list if the user wants it. Proceed only after they confirm.

Then route the confirmed tasks, accepted findings, project baseline and any
existing roadmap to `roadmap-planner`, and run **Roadmap Review** as a distinct
gate. Write the proposal to `.roadmap-proposal.md` and review it from the file: a
proposal is four tables across every epic in the project, so it neither fits in a
gate question nor survives compaction. Validate:

- project-scoped stable epic IDs issued or reused correctly;
- an explicit `Match` decision with evidence, or `Review required`, wherever an
  incoming epic supplied no ID;
- historical entries and delivery history retained, with no prior ID reassigned;
- one wave allocation per active epic, or a documented exception;
- matching stable IDs across the client-facing and internal views;
- a demonstrable client outcome for every wave, and no enabler-only wave;
- tracks safe under the declared dependency and shared-contract state;
- blockers and required shared contracts visible;
- an updated Change Log.

## Asking well

**Gate approvals and destructive confirmations: exactly one question per call.**
Gate 0, Gate 1, the Gate 1.5 disposition, Roadmap Review, Gate 2, "which Jira
project", "push now?" — each gets the user's full attention.

**Item-level clarifications: batch up to 4 independent questions per call.** Never
batch two questions about the same story; a later answer would invalidate the
earlier one.

- `header` is a chip of **max 12 characters** — `Story 1.2`, `Epic 2`, `Jira push`,
  `Priority`.
- The `question` text carries the full context and opens with the parent epic and
  story title: *"[Epic: User Auth > Story 1.2: User can log in] The transcript
  mentions SSO but the Figma shows email/password only. Which scope is correct?"*
- 2–4 options, `label` 1–5 words, the reasoning in `description`. The user always
  gets a free-text "Other" — do not add one.
- **Order by impact**, so a user who stops answering after two has still answered
  the two that mattered.
- **Large review sets go to a file, not to popups.** Gate 1.5 with 20–40
  suggestions, Gate 1 with 15+ stories, an imported backlog of 50+ issues: write
  the full set to its markdown file and ask one disposition question against it.
- Exhaust the materials first. Never ask what the transcript, Figma, PDFs or
  codebase already answer.
