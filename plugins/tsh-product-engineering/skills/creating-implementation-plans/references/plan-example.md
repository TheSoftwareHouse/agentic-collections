# Worked example — a finished plan

Use this reference when unsure how a finished plan reads or how deep a mid-size task
should go. This is an illustration of the building blocks in use, **not a template to
fill** — this plan chose its sections for its task, and dropped Proposed Solution
diagrams, Security beyond one line, and Changelog because they added nothing here.
Its verification document lives beside it; the compact worked example in
[the verification-document reference](./verification-doc.md) is that file.

---

# Add CSV export to the reports list — Implementation Plan

## Task Details

| Field | Value |
| --- | --- |
| Ticket | PROJ-482 |
| Title | Users can export the filtered reports list as CSV |
| Related research | `specifications/PROJ-482/csv-export.research.md` |
| Verification doc | `specifications/PROJ-482/csv-export.verification.md` |

## Goal

**Goal**: A user viewing the reports list can download the currently filtered rows as
a CSV file.

**Success Measure**: `GET /reports/export?status=open` returns a
`text/csv` response whose rows match the filtered list, and the UI button downloads it.

**Do NOT touch / do NOT add**: no XLSX or PDF export, no change to the existing list
endpoint's response shape, no new pagination behavior, no background-job
infrastructure — the list is capped at 10k rows and streams synchronously.

## Current Implementation Analysis

### Already Implemented

- Filter parsing — `src/reports/report-filters.ts` — parses and validates the list
  query params; reuse unchanged for the export endpoint.
- Reports query — `src/reports/reports.repository.ts` — `findFiltered()` already
  accepts the parsed filters.

### To Be Modified

- `src/reports/reports.controller.ts` — add the `GET /reports/export` route.
- `src/pages/reports/ReportsToolbar.tsx` — add the Export button.

### To Be Created

- `src/reports/csv-serializer.ts` — turns report rows into RFC 4180 CSV, streaming.

## Technical Context

### Tech Stack

- Node 22, NestJS 11, TypeORM 0.3, pnpm. Frontend: React 18 + Vite.

### Conventions

- Controllers stay thin; serialization lives in a dedicated module
  (see `src/invoices/pdf-serializer.ts` for the established pattern).
- Streamed responses use `StreamableFile` (see `src/invoices/invoices.controller.ts:74`).

### Testing Patterns

- Unit: `pnpm vitest run <path>` — integration: `pnpm test:int -- <path>` —
  lint: `pnpm lint` — types: `pnpm tsc --noEmit` — frontend unit:
  `pnpm --filter web vitest run <path>`.

## Implementation Plan

### Phase 1: Export endpoint

**Goal**: The API serves filtered reports as CSV.

**Verification:** `pnpm test:int -- src/reports && pnpm tsc --noEmit`

Parallel group A: Tasks 1.1 and 1.2 — independent, disjoint files.

#### Task 1.1 - [CREATE] CSV serializer

**Description**: Create `csv-serializer.ts` exposing
`serializeReports(rows: AsyncIterable<Report>): Readable`. RFC 4180 quoting; header
row from the column list in the research file.

**Files:** `src/reports/csv-serializer.ts` (create),
`src/reports/csv-serializer.spec.ts` (create)

**Definition of Done**:

- [ ] Fields containing `,`, `"` or newlines are quoted and escaped per RFC 4180
- [ ] Run `pnpm vitest run src/reports/csv-serializer.spec.ts`

**Clues**: mirror the streaming shape of `src/invoices/pdf-serializer.ts`.

#### Task 1.2 - [MODIFY] Export button in the toolbar

**Description**: Add an Export button to `ReportsToolbar.tsx` that hits
`/reports/export` with the current filter query string and triggers a download.

**Files:** `src/pages/reports/ReportsToolbar.tsx` (modify),
`src/pages/reports/ReportsToolbar.test.tsx` (modify)

**Definition of Done**:

- [ ] Button builds the export URL from the active filters, not from component state copies
- [ ] Run `pnpm --filter web vitest run src/pages/reports/ReportsToolbar.test.tsx`

**Stop Rule:** if the toolbar no longer owns the filter state, stop and report —
do not lift state to make the task fit.

#### Task 1.3 - [MODIFY] Export route

**Description**: Add `GET /reports/export` to `reports.controller.ts`: parse filters
with the existing `report-filters.ts`, stream `findFiltered()` rows through the Task
1.1 serializer as a `StreamableFile` with `text/csv` and a dated filename.

**Files:** `src/reports/reports.controller.ts` (modify),
`src/reports/reports.controller.int-spec.ts` (modify),
`src/reports/csv-serializer.ts` (reuse — created in Task 1.1)

**Definition of Done**:

- [ ] Integration test covers filtered export and the empty-result case
- [ ] Run `pnpm test:int -- src/reports/reports.controller.int-spec.ts`

### Phase 2: Final verification

**Goal**: The whole change set is reviewed and the feature is verified working, once.

Parallel group B: Tasks 2.1 and 2.2 — reviewer is read-only, verifier exercises the
running app.

#### Task 2.1 - [REVIEW] Code review

**Description**: Delegate to `code-reviewer` with this plan and the full changed-file
list. The delegation states that functional and E2E verification runs in the parallel
verifier, so the reviewer runs static checks, unit and integration suites, and the
build — and excludes E2E.

**Definition of Done**:

- [ ] Review verdict returned; every blocker and major finding resolved and re-checked

#### Task 2.2 - [VERIFY] Functional verification

**Description**: Delegate to `feature-verifier` with
`specifications/PROJ-482/csv-export.verification.md` and the pinned dev server URL.

**Definition of Done**:

- [ ] Every scenario in the verification document passes, with evidence in the report

## Security Considerations

- CSV injection: fields starting with `=`, `+`, `-`, `@` are prefixed with `'` in the
  serializer (covered by a Task 1.1 test case).

## Acceptance Criteria

- [ ] Exported rows match the currently applied filters exactly
- [ ] The file opens correctly in Excel and Google Sheets (quoting, UTF-8 BOM)
- [ ] Export of an empty result returns a header-only CSV, not an error

## Improvements (Out of Scope)

- Async export with email delivery for lists above the 10k cap.
- Column selection UI.
