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

| Path | Tags | Description | Status |
| --- | --- | --- | --- |
| [0001](0001-use-postgresql.md) | database, persistence | PostgreSQL is the primary datastore | Accepted |
| [0002](0002-vertical-slice-modules.md) | architecture, modules | Features are vertical slices, not layers | Accepted |
| [0003](0003-replace-rest-with-graphql.md) | api, graphql | REST stays; GraphQL was rejected | Superseded by 0007 |
```

Three properties matter more than the exact formatting:

- **Tags carry the routing.** They are what lets Claude decide a database task means
  reading 0001. Tag with the words a task would use, not with a taxonomy.
- **Descriptions state the decision, not the deliberation.** "PostgreSQL is the
  primary datastore", never "evaluating datastore options".
- **Superseded rows stay.** Deleting them destroys the record of what was tried. A
  superseded row naming its successor is how the model avoids re-proposing it.

Keep the index a flat table. Grouping by topic looks tidier and makes the row you
need harder to find.

## 4. The wiring, and the trap in it

Root `CLAUDE.md` names the index, in backticks:

```markdown
Architecture decisions are indexed in `docs/decisions/README.md`. Read the index
before proposing a change to persistence, module boundaries, or the API surface.
```

**The backticks are load-bearing.** Written bare as `@docs/decisions/README.md`, the
path becomes an import: the whole index expands into context at launch, in full, and
follows its own imports up to four hops. That is the opposite of what this layer is
for. Import parsing skips Markdown code spans, so the backticked form stays literal
and is read on demand.

Pair the pointer with a condition, as above. A bare mention gets skimmed; a sentence
naming when to read the index gives the model something to act on.

## 5. Keeping the index true

The index is the only part of this layer that rots invisibly — a wrong status is
still a plausible-looking row.

Check during any audit:

- Every row's path resolves. A broken link here is a failure, not cosmetic.
- Every record in the directory has a row. An unindexed ADR is invisible.
- No row is still `Proposed` for a decision the code has clearly implemented.
- Every `Superseded by NNNN` names a record that exists.

When a decision is reversed, add a new record and update the old row's status. Never
edit the original record's content — the historical record is the artifact.

## 6. What this skill does not do

This skill writes **index rows and the wiring**. It does not write the body of a
decision record, and it does not decide a record's status.

- **Prose inside a record** is written with
  [`writing-technical-documents`](../../writing-technical-documents/SKILL.md), which
  owns decision-record craft: decision before deliberation, compressed alternatives,
  explicit consequences and reversibility.
- **Status is a human call.** Marking a record `Accepted` or `Superseded` asserts
  something about what a team agreed. Infer a status from the code and you will
  eventually record agreement that never happened. When the status is unclear, add
  the row, leave the status as the author set it, and say which rows you could not
  determine.
