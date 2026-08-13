# Status lifecycle

Use this reference when setting a status, superseding a record, or reconciling a
record that disagrees with the index. Status is the single most consequential field
in a decision record, because it is what decides whether the record binds.

## 1. The vocabulary

| Status | Means | Binds? |
| --- | --- | --- |
| `Proposed` | Written, not yet agreed. The decision has not been made. | No |
| `Accepted` | Agreed and in force. | **Yes** |
| `Superseded` | Was in force; replaced by a later record. | No |
| `Rejected` | Considered and not adopted. | No |
| `Deprecated` | Was in force; no longer applies, with no replacement. | No |

Five values, and no others. A status invented for one record — `Partially adopted`,
`Under review`, `Legacy` — is unreadable to anyone applying the binding rule, and it
will be treated as non-binding by anything that does not recognise it.

## 2. Only `Accepted` binds

This is the rule the whole layer exists to support, and it holds for anyone reading
records — this skill, another skill, or an agent doing unrelated work:

- **Constraints come from `Accepted` records and nowhere else.** When gathering the
  rules that apply to a task, filter to `Accepted` first.
- **Every other status is history.** It may be read to answer "was this considered
  before?", and must never be applied as a current constraint.
- **A `Superseded` record is never read alone.** Read its successor in the same
  pass. A reader who stops at the superseded record learns the reversed decision and
  believes it current — the worst outcome this format can produce.

The history is not noise to be filtered away and forgotten. A `Rejected` record is
often the most valuable file in the directory: it is what answers someone proposing
the same option again. The distinction is between *reading* it and *obeying* it.

## 3. Legal transitions

```text
Proposed ──accepted──▶ Accepted ──replaced──▶ Superseded
    │                      │
    │                      └──retired, no replacement──▶ Deprecated
    └──not adopted──▶ Rejected
```

Everything else is illegal, and two cases matter:

- **`Superseded` → `Accepted` is never a transition.** Reviving a decision means
  writing a new record that supersedes the one that superseded it. The chain is the
  historical record; editing it backwards destroys the reason the format exists.
- **`Rejected` → `Accepted` is never a transition either.** Same reason. Write a new
  record; its Alternatives table cites the earlier rejection and says what changed.

A record's body is frozen once it reaches `Accepted`. After that only the status
line and the `Superseded by` field may change.

## 4. Never set a status yourself

Marking a record `Accepted` asserts that a team agreed something. Inferring that
from the code eventually records an agreement that never happened, and it is
unfalsifiable afterwards — the record becomes the evidence.

The correct move when writing a record is:

1. Write it with status `Proposed`.
2. State in the handoff which status you believe is correct and why.
3. Name who should confirm it.

The same applies to an existing record whose status looks wrong: report the
mismatch, do not fix it. "The code has used Postgres for two years but 0001 is still
`Proposed`" is a useful finding. Silently promoting it to `Accepted` is not.

## 5. Superseding, in full

Replacing a decision touches four things, and missing any one leaves the archive
inconsistent:

1. **Write the new record.** Its `Supersedes` field names the old number. Its
   Context explains what changed since — a new constraint, a limit reached, an
   assumption disproved. "We changed our minds" is not a context.
2. **Update the old record's metadata only.** Status becomes `Superseded`, and
   `Superseded by` names the new number. **The body is not touched**, including
   parts now known to be wrong. It is a historical document.
3. **Update both index rows.** The old row's status changes; the new row is added.
4. **Verify both directions resolve.** Old points forward, new points back. A
   one-directional link is how a chain becomes unreadable.

Deprecating is the same procedure without a successor: status becomes `Deprecated`,
`Superseded by` stays `—`, and the record says in one line why it no longer applies.

## 6. Keeping the index in step

The record is the source of truth for status and tags. The index mirrors it. When
they disagree, **the record wins and the index is corrected** — never the reverse,
because the index is a summary and summaries are what drift.

The index row must be written in the same change as the record. An unindexed record
is invisible: nothing routes to it, and the filter in section 2 never sees it.

Check during any audit:

- Every record has a row, and every row resolves to a file
- Status matches between record and row, in both directions
- Tags match between record and row
- Every `Superseded` record names a successor that exists
- Every successor names the record it supersedes
- No row is still `Proposed` for a decision the code has visibly implemented — this
  is a finding to report, not a fix to apply

## 7. Statuses in a repository that already has ADRs

An existing archive may use a different vocabulary — `Draft`, `Active`,
`Obsolete`, or MADR's `proposed | rejected | accepted | deprecated | superseded by`.
Match the existing vocabulary; do not migrate an archive as a side effect of writing
one record.

What still applies regardless of vocabulary: exactly one status means "in force",
and only that one binds. Identify which value that is before applying the filter in
section 2, and say which mapping you used.
