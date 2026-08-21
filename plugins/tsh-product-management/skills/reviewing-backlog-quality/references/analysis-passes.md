# Analysis passes

Each pass is independent and produces zero or more findings. A finding is a
potential gap or improvement that becomes a suggestion in step 6 of the skill.

Lite mode runs **A, B, E, H, I**. Full mode runs **A through J**. Both modes then
run the mandatory **Pass R**.

Before running any pass, filter out every task whose status is Done, Cancelled or
PO APPROVE. Those tasks may still be referenced as dependencies, but they generate
no findings.

## Pass A — Entity Lifecycle Completeness

For each entity in the domain model, verify the full lifecycle: **creation**,
**reading/listing**, **updating**, **deactivation/deletion**. A finding is
generated when an operation is missing for an entity that logically requires it.

*Example patterns*: a system manages "locations" but has no story for editing or
deleting one; a system creates "promotions" but no story shows promotion history.

## Pass B — Cross-Feature State Validation

When one feature consumes an entity managed by another, verify the consuming
feature validates that entity's readiness state — and defines what happens when it
is incomplete, deactivated, or in error.

*Example patterns*: a public page displays data from an entity that could be
deactivated, with no "inactive" case; a workflow depends on a verification step
without blocking or messaging when verification is incomplete.

## Pass C — Bulk Operation Idempotency

For any bulk or batch operation (imports, mass updates, batch processing): does it
handle items that already exist, partial failures, and reporting the outcome
(success count, failure count, error detail)?

*Example patterns*: a CSV import does not say what happens on a duplicate
identifier; a batch invitation does not clarify whether already-registered users
are skipped or re-invited.

## Pass D — Actor Dashboard Completeness

For every actor with a management interface, check three dimensions:
**metrics/statistics**, **configuration**, and **history/audit**. A finding is
generated when a dashboard exists but one dimension is missing.

*Example patterns*: an employer manages workers and locations but cannot see
tipping statistics; a worker sees recent transactions but no aggregate view.

## Pass E — Precondition Guards

When one feature unlocks another, verify the precondition is enforced, the user is
told what to do to satisfy it, and the dependent feature cannot operate in an
invalid state.

*Example patterns*: a QR code is generated for a worker who has not completed
identity verification; a feature requires a paid plan but no story covers the
free-plan experience.

## Pass F — Third-Party Boundary Clarity

For every story involving an external system: is the split between the external
system and in-house work clear, are the integration points documented (data in,
data back), and are failure modes covered (timeout, rejection, downtime)?

*Example patterns*: "verification is handled by the payment processor" with no
failure or timeout behaviour; an e-commerce integration that does not say whether
it is embedded, linked, or API-based.

## Pass G — Platform Operations Perspective

Does anything in the list serve the platform operators rather than end users —
system health and metrics, intervention (account status, dispute resolution), and
troubleshooting (transaction logs, audit trails)? A finding is generated when no
epic or story addresses the operator perspective. This is a common gap: workshops
focus on end-user features.

*Example patterns*: a marketplace has buyer and seller stories but none for the
marketplace operator; a subscription service has subscriber stories but nothing
for the billing team.

## Pass H — Error State and Edge Case Coverage

For each happy-path story: what happens on failure (network error, invalid input,
permission denied), on empty data (no records, no results), and at boundaries
(maximum limits, minimum values, expired items)?

*Example patterns*: "user can view transaction history" with no empty state;
"user can submit payment" with no insufficient-funds or expired-card path.

## Pass I — Notification and Communication Gaps

For each state change affecting an actor other than the one performing it: is that
actor notified, is the method specified (email, in-app, push), and are preferences
or opt-out addressed?

*Example patterns*: an employer deactivates a worker with no story notifying the
worker; a payout is processed without notifying the recipient.

## Pass J — Domain-Specific Research

Research common patterns, standards and regulatory expectations for the domain of
the project with `WebSearch` and `WebFetch`, and check them against the task list.

Findings from this pass are **Medium** or **Low** confidence — never High — and
must cite what was found so the user can judge the source. If neither research
tool is available, run the other nine passes and state that Pass J was skipped
rather than speculating.

*Example patterns*: a financial application with no audit logging; a healthcare
application with no data-retention policy; e-commerce with no cancellation or
refund flow.

## Pass R — Pre-Roadmap Delivery-Readiness (mandatory in both modes)

Run on every non-protected epic, after the selected Lite or Full passes and before
any roadmap proposal exists. It assesses only the Gate 1-approved epic content in
`extracted-tasks.md` — it does not use other material to infer delivery
requirements. Produce a finding when an epic is missing or unclear on:

1. **Independently demoable vertical-slice boundary** — an end-to-end boundary that
   can be completed and demonstrated on its own.
2. **Customer outcome and demonstrable scenario or criteria**.
3. **Explicit exclusions** — what lies outside the boundary.
4. **Known dependencies**.
5. **Explicit shared-contract state** — resolved, unresolved, or not applicable, per
   required contract.
6. **Parallel-proposal eligibility** — whether the approved evidence makes the epic
   eligible to be proposed for parallel execution. An epic depending on an
   unresolved required shared contract is ineligible, even when it is otherwise
   merely dependent on another epic.

Record the target epic, the approved-extraction evidence, the finding, and a
proposed correction, then put it through the normal accept/reject flow at Gate 1.5.
Never silently change the task list.

This pass does **not** validate same-wave execution, tracks, allocation, or wave
client outcomes — `planning-delivery-roadmaps` and the Roadmap Review gate own
those decisions.

The contract fields come from `extracting-epics-and-stories` step 4. For an epic
that predates the Epic Delivery Contract, report the missing fields as **one**
ordinary finding per epic — not six findings per legacy epic.

## Confidence and action defaults

| Pass | Category | Confidence default | Typical action |
| --- | --- | --- | --- |
| A | Entity Lifecycle Completeness | High | NEW_STORY or MODIFY_STORY |
| B | Cross-Feature State Validation | High | ADD_ACCEPTANCE_CRITERION or MODIFY_STORY |
| C | Bulk Operation Idempotency | High | ADD_ACCEPTANCE_CRITERION or MODIFY_STORY |
| D | Actor Dashboard Completeness | Medium | NEW_STORY |
| E | Precondition Guards | High | ADD_ACCEPTANCE_CRITERION or MODIFY_STORY |
| F | Third-Party Boundary Clarity | Medium | ADD_TECHNICAL_NOTE or MODIFY_STORY |
| G | Platform Operations Perspective | Medium | NEW_EPIC or NEW_STORY |
| H | Error State and Edge Case Coverage | High | ADD_ACCEPTANCE_CRITERION |
| I | Notification and Communication Gaps | High | NEW_STORY or ADD_ACCEPTANCE_CRITERION |
| J | Domain-Specific Research | Low–Medium | Varies |
| R | Pre-Roadmap Delivery-Readiness | High | MODIFY_EPIC |
