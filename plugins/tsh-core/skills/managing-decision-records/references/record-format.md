# Record format

Use this reference before writing the first section of a record. The format is
deliberately small: a metadata block and four prose sections. Every section earns
its place by answering a question a future reader actually asks.

**Decision comes first, before Context.** This is the one place the format departs
from the classic Nygard ordering, and it follows the house rule in
[`writing-technical-documents`](../../writing-technical-documents/SKILL.md): the
conclusion goes in the first sentence. A reader who stops after the first line
should still leave knowing what was decided.

## 1. File naming and numbering

`NNNN-kebab-case-title.md`, zero-padded to four digits, in `docs/decisions/`:

```text
docs/decisions/
├── README.md
├── 0001-use-postgresql.md
├── 0002-vertical-slice-modules.md
└── 0003-adopt-graphql-for-public-api.md
```

Take the next free number. Numbers are never reused and never renumbered — other
records, commit messages and code comments refer to them, and renumbering breaks
every reference at once. A gap in the sequence is harmless; a shifted number is not.

The filename states the decision, not the topic. `0001-use-postgresql.md`, not
`0001-database.md`. Someone scanning `ls` should learn what was decided.

## 2. The skeleton

```markdown
# 0001. Use PostgreSQL as the primary datastore

- **Status:** Accepted
- **Date:** 2026-08-13
- **Tags:** persistence, database, infrastructure
- **Supersedes:** —
- **Superseded by:** —

## Decision

PostgreSQL is the primary datastore for all transactional application data.
Managed instances in every environment; no self-hosted deployments.

## Context

We need a datastore for transactional application data. The team has operational
experience with Postgres and none with the alternatives. Our data is relational
and our consistency requirements rule out eventual consistency at the primary.

## Alternatives

| Option | Why not |
| --- | --- |
| MySQL | No operational experience on the team; no feature we need that Postgres lacks |
| DynamoDB | Our access patterns are relational and not known up front |
| MongoDB | Consistency model does not fit the transactional requirement |

## Consequences

Schema changes need migrations, so the release process gains a step that must run
before deploy. Analytical queries will contend with transactional load until a read
replica exists. Full-text search is available without adding a component.

Reversing this is expensive: a datastore migration touches every persistence-layer
module and requires a data migration with downtime.
```

## 3. The metadata block

| Field | Rule |
| --- | --- |
| `Status` | One of the values in [`status-lifecycle.md`](./status-lifecycle.md). Set by a human, never inferred. |
| `Date` | When the decision was made, not when the file was written. `YYYY-MM-DD`. |
| `Tags` | The words someone would search for before they know this record exists. Match the index row exactly. |
| `Supersedes` | The record this replaces, or `—`. |
| `Superseded by` | Filled in when this record is replaced. Never removed afterwards. |

Tags carry the routing. Tag with the vocabulary of the *task* that should find this
record — `persistence`, `database` — not with a taxonomy you invented for the
archive. A record nobody's tags match is a record nobody reads.

## 4. Decision — settled fact, present tense, first

The first sentence states what was chosen. Not "we decided to", not "we will", not
"we are leaning towards" — the present tense, as a fact about how things are.

Add the scope: what the decision covers and what it explicitly does not. A decision
without a boundary gets applied where it was never meant to.

If the decision is not settled, the record's status is `Proposed` and the section
says plainly what would settle it — the experiment, the number, the person.

## 5. Context — the constraint, not the history

State what forced a decision: the requirement, the limit, the deadline, the thing
that broke. One paragraph is usually enough.

This section is the largest source of bloat in practice. It attracts the story of
how the team got there — who raised it, what was discussed, which meeting settled
it. None of that helps the reader, who wants to know whether the constraint that
produced this decision still holds.

> After several discussions in the platform sync, and following the incident in
> March, the team spent some time evaluating our options for storage…

> Our data is relational and our consistency requirements rule out eventual
> consistency at the primary.

## 6. Alternatives — one line each

Every option considered gets a row: what it was, and the single reason it lost.

This section is **not optional**, and it is the one most often dropped. Without it
the record cannot do its main job: when someone proposes MongoDB in eighteen months,
this table is what answers them. A record with no alternatives reads as though no
alternatives existed, which is almost never true.

One line, not a fair hearing. Multi-paragraph write-ups of rejected options are
written for the author's comfort and are the second-largest source of bloat. If a
reader wants to reopen an option, the line tells them which constraint to attack.

## 7. Consequences — including the ones you dislike

Name what becomes easier, what becomes harder, and what this forecloses. Then state
reversibility plainly: cheap or expensive, and what reversing costs.

Vague consequences are the part a future reader most needs and least often gets.
"This improves maintainability" says nothing. "Schema changes need migrations, so
the release process gains a step that must run before deploy" is checkable.

A consequences section that lists only benefits is a sales document, not a decision
record, and a reader will discount the whole file accordingly.

## 8. What this format deliberately omits

- **A scoring matrix.** Criteria and weights are usually reverse-engineered to
  justify the decision already made.
- **A deciders list.** Git history has it, and naming individuals discourages people
  from recording decisions at all.
- **A separate Rationale section.** The reason lives in Context and Alternatives; a
  third home guarantees the three drift.
- **Prose craft rules.** [`writing-technical-documents`](../../writing-technical-documents/SKILL.md)
  owns those, and duplicating them here would create a second source of truth.
