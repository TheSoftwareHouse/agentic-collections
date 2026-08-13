# When to write one

Use this reference before creating a record. Most things people want to record are
not decisions, and a directory full of non-decisions is worse than a small one: the
index gets longer, the tags get noisier, and the records that matter get harder to
find.

## 1. The test

A decision record is warranted when **all four** hold:

1. **A choice was made between real alternatives.** If there was only one viable
   option, there was no decision — there was a constraint.
2. **It is expensive to reverse.** Cheap-to-reverse choices get revisited on their
   merits when the time comes; they do not need an archive entry.
3. **Someone will ask "why is it like this?"** and the answer is not visible in the
   code.
4. **The rationale is recoverable now.** A record written after everyone who made
   the decision has left is a guess dressed as history.

Any one missing, and the answer is one of the alternatives in section 3.

## 2. What passes

- Choosing a datastore, a message broker, a cloud provider
- Adopting or dropping a framework, or a major version with a migration cost
- A module boundary or architectural pattern the codebase now assumes
- An authentication or authorisation model
- Deliberately accepting a limitation — "we do not support offline mode"
- Rejecting something people keep proposing. A `Rejected` record is one of the
  highest-value entries in an archive, because it is what answers the next proposal.

## 3. What does not, and where it goes instead

| Not a decision record | Belongs in |
| --- | --- |
| A convention — naming, layout, formatting, error shape | `CLAUDE.md`, or a path-scoped rule in `.claude/rules/` |
| A procedure — how to release, how to run migrations | A skill |
| Anything a linter or type-checker enforces | Nowhere; the tool is the record |
| A one-off implementation choice inside one module | The code, and a comment if it is surprising |
| A plan for work not yet done | A ticket |
| A decision nobody can explain any more | Nowhere. Say so instead of inventing one. |

The most common mistake by far is the first row. "We use camelCase for API fields"
feels like a decision and is a convention: it applies constantly, so it belongs
where it loads automatically, not behind an index that is consulted occasionally.
The distinction is not importance — it is **frequency of application**. A convention
applies on every file you touch. A decision applies when you are about to contradict
it.

## 4. Conventions and decisions can both exist

A decision often produces conventions. "PostgreSQL is the primary datastore" is a
decision; "migrations live in `db/migrations/` and are never edited after merge" is
a convention that follows from it.

Record both, in their own layers, and do not duplicate:

- The record explains *why* Postgres, and what it forecloses
- `CLAUDE.md` or a rule states *what to do* — where migrations live, how they run
- The convention does not restate the rationale; the record does not list the
  conventions

When someone asks "should this go in the ADR or in `CLAUDE.md`?", the answer is
usually **both, split that way**.

## 5. Writing one after the fact

Recording a decision made months ago is legitimate and common — most archives start
this way. Two rules keep it honest:

- **Date it when the decision was made**, not when the file was written. A record
  dated today for a 2024 decision misleads anyone reconstructing a timeline.
- **Name the gaps.** If the alternatives considered are not recoverable, write
  "Alternatives considered at the time are not recorded" rather than reconstructing
  a plausible list. An invented Alternatives table is actively harmful: it will be
  cited in a future discussion as evidence that an option was weighed when it never
  was.

Ask the people who were there before writing, when they are still reachable. That is
usually a five-minute conversation, and it is the difference between a record and a
reconstruction.

## 6. When the answer is "not yet"

A decision under active discussion gets a record with status `Proposed`, or no
record at all. Prefer no record while the discussion is genuinely open — a
`Proposed` record that sits for a year is indistinguishable from an abandoned one,
and it clutters the index without binding anything.

Write the `Proposed` record when it is about to be decided and the write-up is what
the decision will be made from. That is the point where the format earns its keep:
Alternatives and Consequences filled in properly is exactly the material a reviewer
needs.
