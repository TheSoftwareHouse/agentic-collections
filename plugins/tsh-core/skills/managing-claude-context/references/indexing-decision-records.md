# Indexing decision records

Use this reference when wiring architecture decision records into context, or when
a repository has decisions written down that Claude never finds. The problem is
almost never that the ADRs are missing. It is that nothing tells Claude they exist.

## 1. What this layer is for

`CLAUDE.md` holds conventions — what to do. ADRs hold decisions — what was chosen,
what was rejected, why, and whether it still stands. The two fail differently: a
convention that goes stale produces wrong code, while a decision that goes unread
produces re-litigation, where the model proposes the alternative the team rejected
eighteen months ago and nobody in the review remembers why it was rejected.

Decision records are far too long to load every session and far too valuable to
leave undiscoverable. That is exactly the shape progressive disclosure solves: a
thin index that is cheap to reach, and full records read only when the index says
one is relevant.

## 2. Layout

```text
docs/
└── decisions/
    ├── README.md                          # the index — the only file that must exist
    ├── 0001-use-postgresql.md
    ├── 0002-vertical-slice-modules.md
    └── 0003-replace-rest-with-graphql.md
```

`docs/decisions/` is this skill's **default**, not a requirement of Claude Code. A
repository already keeping ADRs in `docs/adr/`, `architecture/decisions/` or a wiki
keeps them there — point the index at the real location and change nothing else.
The wiring in section 4 is the part that is non-negotiable.

Number records with a zero-padded sequence and never renumber. The number is how
other records refer to this one.

## 3. The index

`docs/decisions/README.md` carries one row per decision, and four columns:

| Column | Holds |
| --- | --- |
| Path | Relative link to the record |
| Tags | Comma-separated topics, for matching a task to a decision |
| Description | One line: what was decided, not why |
| Status | `Proposed`, `Accepted`, `Superseded by NNNN`, or `Deprecated` |

```markdown
# Decision records

**Only records with status `Accepted` are binding.** Every other status is history:
read it to see what was already considered, never apply it as a current constraint.
A `Superseded` record is read together with its successor, never alone.

| Path | Tags | Description | Status |
| --- | --- | --- | --- |
| [0001](0001-use-postgresql.md) | database, persistence | PostgreSQL is the primary datastore | Accepted |
| [0002](0002-vertical-slice-modules.md) | architecture, modules | Features are vertical slices, not layers | Accepted |
| [0003](0003-rest-over-graphql.md) | api, graphql | REST stays; GraphQL was rejected | Superseded by 0007 |
| [0004](0004-event-sourcing.md) | architecture, events | Event-source the ledger | Proposed |
| [0005](0005-mongodb.md) | database | MongoDB as primary datastore | Rejected |
| [0007](0007-adopt-graphql.md) | api, graphql | GraphQL for the public API | Accepted |
```

Four properties matter more than the exact formatting:

- **The binding note goes at the top**, above the table. It is the one line that
  makes the status column mean something to a reader who arrives mid-task.
- **Tags carry the routing.** They are what lets Claude decide a database task means
  reading 0001. Tag with the words a task would use, not with a taxonomy.
- **Descriptions state the decision, not the deliberation.** "PostgreSQL is the
  primary datastore", never "evaluating datastore options".
- **Non-binding rows stay.** Deleting them destroys the record of what was tried.
  Row 0005 is what answers the next person who proposes MongoDB, and row 0003 is
  what stops a reader implementing REST-only after 0007 reversed it.

Keep the index a flat table. Grouping by topic looks tidier and makes the row you
need harder to find.

## 3a. Only `Accepted` binds

This is the rule the status column exists to support, and the reason the index is
worth building at all.

- **Constraints come from `Accepted` records and nowhere else.** When gathering the
  decisions that apply to a task, filter to `Accepted` before reading bodies.
- **Every other status is history.** `Proposed`, `Rejected`, `Superseded` and
  `Deprecated` may be read to answer "was this considered before?" — and must never
  be applied as a current constraint. Implementing a `Proposed` record means acting
  on a decision nobody made.
- **A `Superseded` record is never read alone.** Read its successor in the same
  pass. A reader who stops at 0003 above learns that GraphQL was rejected, which
  0007 reversed — the worst outcome this layer can produce.

History is not noise to filter away. A `Rejected` record is often the most valuable
file in the directory. The distinction is between *reading* it and *obeying* it.

## 4. The wiring, and the trap in it

Root `CLAUDE.md` names the index, in backticks:

```markdown
Architecture decisions are indexed in `docs/decisions/README.md`. Before changing
persistence, module boundaries or the API surface, read the index and follow only
records with status `Accepted`. Other statuses are history, not constraints.
```

**The backticks are load-bearing.** Written bare as `@docs/decisions/README.md`, the
path becomes an import: the whole index expands into context at launch, in full, and
follows its own imports up to four hops. That is the opposite of what this layer is
for. Import parsing skips Markdown code spans, so the backticked form stays literal
and is read on demand.

Pair the pointer with a condition, as above. A bare mention gets skimmed; a sentence
naming when to read the index gives the model something to act on.

**The filter sentence is not optional, and it belongs in both places** — this
pointer and the index header from section 3. The skill that writes these files runs
occasionally, at setup and audit; the generated sentences are what carry the rule
into every session afterwards. An index with a status column and no statement of
what status *means* leaves each reader to guess, and the common guess is that
everything written down applies.

## 5. Keeping the index true

The index is the only part of this layer that rots invisibly — a wrong status is
still a plausible-looking row.

Check during any audit:

- Every row's path resolves. A broken link here is a failure, not cosmetic.
- Every record in the directory has a row. An unindexed ADR is invisible.
- **Status and tags agree between the row and the record itself.** The record is the
  source of truth and the index mirrors it, so when they disagree the row is
  corrected — never the record. A row saying `Accepted` over a record saying
  `Superseded` is the most dangerous state this layer has, because the filter in
  section 3a reads the row and admits a reversed decision as binding.
- No row is still `Proposed` for a decision the code has clearly implemented. Report
  this rather than fixing it — promoting a status asserts an agreement.
- Every `Superseded by NNNN` names a record that exists, and that record names this
  one back.
- The binding note is present above the table, and the `CLAUDE.md` pointer still
  carries the filter sentence.

When a decision is reversed, add a new record and update the old row's status. Never
edit the original record's content — the historical record is the artifact.

## 6. What this skill does not do

This skill writes **index rows, the binding note, and the wiring**. It does not
write the body of a decision record, define the record format, or decide a status.
Three skills split the artifact, and the boundaries are worth knowing:

| Concern | Owner |
| --- | --- |
| Index schema, the binding note, the `CLAUDE.md` pointer | This skill |
| Record format, sections, numbering, status lifecycle, superseding | [`managing-decision-records`](../../managing-decision-records/SKILL.md) |
| The prose inside a record | [`writing-technical-documents`](../../writing-technical-documents/SKILL.md) |

- **Format and lifecycle** — what sections a record has, what the statuses mean, how
  to supersede one — belong to `managing-decision-records`. Read it before creating
  or restructuring a record rather than improvising a shape here.
- **Prose craft** — decision before deliberation, compressed alternatives, explicit
  consequences and reversibility — belongs to `writing-technical-documents`.
- **Status is a human call.** Marking a record `Accepted` or `Superseded` asserts
  something about what a team agreed. Infer a status from the code and you will
  eventually record agreement that never happened. When the status is unclear, add
  the row, leave the status as the author set it, and say which rows you could not
  determine.
