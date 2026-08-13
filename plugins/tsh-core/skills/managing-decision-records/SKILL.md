---
name: managing-decision-records
description: "Owns the shape and lifecycle of architecture decision records — the four-section format, the status vocabulary, numbering, superseding, and keeping `docs/decisions/README.md` in step. Use when adding a decision record, changing one's status, superseding an old decision, or deciding whether something warrants a record at all."
when_to_use: "Trigger on: writing a new ADR, recording an architecture or technology choice, marking a decision accepted or superseded, reversing an earlier decision, numbering or naming a record, a decision record missing from the index, an index status disagreeing with the record, or asking whether a choice deserves a record or belongs in `CLAUDE.md`."
---

# Managing Decision Records

Owns what a decision record **is** — its sections, its status, its number, and its
row in the index. It does not own the words inside it: prose craft belongs to
[`writing-technical-documents`](../writing-technical-documents/SKILL.md), which
covers decision-first ordering, compressed alternatives, concrete consequences and
reversibility.

**A decision record earns its keep only when someone later asks "why is it like
this?" and gets an answer.** A record with no rationale, or one the index does not
list, has cost effort and bought nothing.

## When to Use

- Recording an architecture, technology or approach decision the team has made
- Reversing or replacing an earlier decision
- Changing a record's status, or reconciling a status that disagrees with the index
- Numbering, naming or placing a new record
- Deciding whether something is a decision at all, or just a convention

## Applicability and Precedence

The repository's existing ADR convention outranks this format. Where records already
follow a shape — Nygard, MADR, a house template — match it exactly and apply only
the lifecycle rules in [`status-lifecycle.md`](./references/status-lifecycle.md).
Read two neighbouring records before writing a new one.

`docs/decisions/` is the default location. A repository already keeping records
elsewhere keeps them there.

**The record is the source of truth for status and tags. The index mirrors it.**
When the two disagree, the record wins and the index is corrected.

## Explicit Exclusions

This skill does not:

- make the decision, or choose between the options under discussion
- set or change a record's status on its own — that asserts what a team agreed, and
  is a human call recorded after the fact
- edit the body of an accepted record, ever; a decision that changes gets a new
  record and a forward link
- govern prose craft — that is
  [`writing-technical-documents`](../writing-technical-documents/SKILL.md)
- define the index schema or wire it into `CLAUDE.md` — that is
  [`managing-claude-context`](../managing-claude-context/SKILL.md)
- invent a rationale, a rejected alternative, or a consequence to fill a section

When the reasoning behind a decision cannot be recovered, write the record with the
gap named explicitly. A plausible invented rationale is worse than an admitted one,
because it will be cited later as if it were true.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Include all four sections — Decision, Context, Alternatives, Consequences, in that order — plus the metadata block. Decision comes first: the conclusion belongs in the first sentence. A record missing Alternatives cannot stop re-litigation, which is the reason the artifact exists. |
| MUST | State the decision in the present tense as settled fact, in the first sentence of the Decision section. |
| NEVER | Edit the body of a record whose status is `Accepted` or later. Write a new record and link the two. |
| MUST | Add the index row in the same change as the record. An unindexed record is invisible and will not be read. |
| MUST | Keep status and tags identical in the record and the index. The record is authoritative. |
| NEVER | Set or change a status yourself. Propose it, name who decides, and leave it. |
| MUST | Number records with a zero-padded sequence, never reused and never renumbered. |
| MUST | When superseding, update both records and both index rows — the old one points forward, the new one points back. |
| NEVER | Delete a record or its index row, including for rejected and superseded decisions. The rejected option is the most valuable thing in the archive. |
| MUST | Name the gap explicitly when a rationale cannot be recovered, rather than reconstructing one. |
| MUST | Treat only `Accepted` records as binding when reading decisions to inform other work. Other statuses are history. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Record format](./references/record-format.md) | Writing or restructuring any record | The metadata block and four sections one by one, why Decision precedes Context, numbering and file naming, a worked example, what bloats each section |
| [Status lifecycle](./references/status-lifecycle.md) | Setting a status, superseding, or reconciling index and record | The status vocabulary, legal transitions, the supersede procedure, which status binds, the index-sync obligation |
| [When to write one](./references/when-to-write-one.md) | Unsure whether something warrants a record | The threshold, ADR vs. a convention in `CLAUDE.md` vs. nothing, why most choices are not decisions |

## Procedure

**Step 1 — Confirm it is a decision.** Read
[`when-to-write-one.md`](./references/when-to-write-one.md) **before creating a
file**. Most things people want to record are conventions, and a convention belongs
in `CLAUDE.md` or a path-scoped rule where it is loaded automatically. A record
written for a non-decision dilutes the index for every real one.

**Step 2 — Read the neighbours.** Open the index and two existing records. Match
their shape. Check whether an existing record already covers this ground — if one
does, this is a supersede, not a new decision, and Step 5 applies.

**Step 3 — Gather what is actually known.** The constraint that forced the decision,
the options considered, the reason each lost, and the consequences. Ask when the
rationale is not recoverable. Do not fill a section by inference.

**Step 4 — Write the record.** Read
[`record-format.md`](./references/record-format.md) **before writing the first
section** — the ordering and what each section excludes are not reconstructible from
the rules table. Take the next free number. Apply
[`writing-technical-documents`](../writing-technical-documents/SKILL.md) to the prose
within the sections.

**Step 5 — Handle superseding, if this replaces something.** Read
[`status-lifecycle.md`](./references/status-lifecycle.md). The old record keeps its
body unchanged and gains a forward pointer; the new one points back. Both index rows
change in this same step.

**Step 6 — Update the index and stop at status.** Add or update the row so path,
tags, description and status match the record exactly. Then state the status you
believe is correct and who should confirm it — do not set it yourself.

## Self-check Before Handoff

```text
- [ ] This is a decision, not a convention that belongs in CLAUDE.md
- [ ] All four sections are present, Decision is first, and Alternatives says why each option lost
- [ ] The Decision section's first sentence states the choice as settled fact
- [ ] No accepted record's body was edited
- [ ] The index row was added or updated in this same change
- [ ] Status and tags are identical in the record and the index
- [ ] No status was set or changed without a human deciding it
- [ ] Superseding updated both records and both rows, in both directions
- [ ] Nothing was invented to fill a section; gaps are named as gaps
```
