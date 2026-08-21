# <Workshop Topic> — Quality Review Report

## Review Context

| Field | Value |
|---|---|
| Review Date | <date> |
| Source Task List | `extracted-tasks.md` (Gate 1 approved) |
| Additional Sources | <cleaned-transcript.md, Figma designs, Jira board PROJ, etc. — or "None"> |
| Review Mode | <Lite / Full> |
| Passes Run | <A, B, E, H, I or A-J> |
| Epics Reviewed | <number> |
| Stories Reviewed | <number> |
| Total Suggestions | <number> |
| Accepted | <number> |
| Rejected | <number> |

---

## Domain Model

### Actors

| Actor | Epics Involved | Key Capabilities |
|---|---|---|
| <role-name> | <epic numbers, e.g. 1, 2, 4> | <what this actor can do> |
| <role-name> | <epic numbers> | <capabilities> |

### Entities

| Entity | Created In | Read In | Updated In | Deactivated/Deleted In |
|---|---|---|---|---|
| <entity-name> | <story ref or "—"> | <story ref or "—"> | <story ref or "—"> | <story ref or "—"> |

### Key Relationships

- <Entity A> belongs to <Entity B> — managed in <story ref>
- <Entity C> depends on <Entity D> being in <state> — validated in <story ref or "not covered">

---

## Suggestions

### Pre-Roadmap Delivery-Readiness Findings (Pass R)

Extraction-evidenced delivery-readiness findings, recorded before a roadmap proposal exists. Each one is an individually accepted or rejected suggestion at Gate 1.5, exactly like every other suggestion below.

#### QR-00 · High · MODIFY_EPIC

**Target Epic**: Epic 1 — <Epic Title>

**Finding** (Pass R: <vertical-slice boundary / customer outcome and demo criteria / exclusions / dependencies / shared-contract state / parallel-proposal eligibility>):
<1-2 sentence explanation of the approved-extraction delivery-readiness gap.>

**Approved-Extraction Evidence**:
<Relevant text, or the absent field, from the Gate 1-approved epic in extracted-tasks.md.>

**Proposed Correction**:
<Exact epic-contract text to add or revise in extracted-tasks.md.>

**Decision**: <✅ Accepted / ❌ Rejected / ⏭️ Skipped — task has protected status>

> An epic with an unresolved required shared contract is ineligible to be proposed for parallel execution, even when it is otherwise merely dependent on another epic. These findings do not validate same-wave execution, tracks, allocation, or wave client outcomes — `planning-delivery-roadmaps` and the Roadmap Review gate own those proposal-level decisions.

---

### Epic 1: <Epic Title>

#### QR-01 · High · ADD_ACCEPTANCE_CRITERION

**Target**: Story 1.3 — <Story Title>

**Finding** (Pass <X>: <Category Name>):
<1–2 sentence explanation of the gap and why it matters.>

**Proposed Change**:
Add to Story 1.3 acceptance criteria:
- [ ] <new verifiable condition>

**Decision**: ✅ Accepted

---

#### QR-02 · Medium · NEW_STORY

**Target**: Epic 1 (new story)

**Finding** (Pass <X>: <Category Name>):
<1–2 sentence explanation of the gap.>

**Proposed Change**:
Add new story under Epic 1:

### Story 1.N: <Story Title>

**User Story**: As a <role>, I want <capability> so that <benefit>.

**Source**: <workshop reference / baseline note>

**Acceptance Criteria**:
- [ ] GIVEN <business condition> WHEN <trigger> THEN <expected outcome>
- [ ] GIVEN <business condition> WHEN <trigger> THEN <expected outcome>

**Additional Acceptance Checks**:
- <optional non-scenario check>

**High-Level Technical Notes**: None

**Priority**: <priority>

**Decision**: ❌ Rejected — <user's stated reason, if any>

---

### Epic 2: <Epic Title>

#### QR-03 · High · MODIFY_STORY

**Target**: Story 2.1 — <Story Title>

**Finding** (Pass <X>: <Category Name>):
<explanation>

**Proposed Change**:
Update Story 2.1 description to include: <proposed text change>

**Source**: <workshop reference / baseline note>

**Decision**: ✅ Accepted

---

### New Epics

#### QR-04 · Medium · NEW_EPIC

**Finding** (Pass G: Platform Operations Perspective):
<explanation of why a new epic is warranted>

**Proposed Change**:
Add new epic:

## Epic N: <Epic Title>

### Epic Delivery Contract

**Customer Outcome**: <customer-visible result this epic delivers>

**End-to-End Boundary**: <complete vertical-slice scope needed to achieve and demonstrate the outcome>

**Explicit Exclusions**: <work intentionally outside this epic's boundary>

**Demonstrable Scenario or Criteria**: <client-demonstrable scenario or business criteria that proves the outcome>

**Known Dependency or Required Shared Contract**: <named dependency, required shared contract, or "None">

**Collaboration/Concurrency Classification**: <Independent parallel work / Blocked work / Shared contract explicitly resolved>

**Business Description**: <description>

**Success Criteria**:
- <criterion>

### Story N.1: <Story Title>

**User Story**: As a <role>, I want <capability> so that <benefit>.

**Acceptance Criteria**:
- [ ] <verifiable condition>

**High-Level Technical Notes**: None

**Priority**: <priority>

**Decision**: ✅ Accepted

---

## Applied Changes Summary

| # | Suggestion | Action | Target |
|---|---|---|---|
| QR-01 | <brief summary> | ADD_ACCEPTANCE_CRITERION | Story 1.3 |
| QR-03 | <brief summary> | MODIFY_STORY | Story 2.1 |
| QR-04 | <brief summary> | NEW_EPIC | Epic N (new) |

**Updated Totals**: <X> epics (+<N> new), <Y> stories (+<M> new, <K> modified)

## Rejected Suggestions

| # | Suggestion | Confidence | Reason |
|---|---|---|---|
| QR-02 | <brief summary> | Medium | <user's stated reason> |
